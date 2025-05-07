import argparse
import os
import os.path as osp

import imageio
import numpy as np
import cv2
import torch
import gc
import sys

from utils.color import COLOR
from utils.utils import determine_model_cfg, bbox_process, prepare_frames_or_path, save_frames_to_temp_dir
from models.sam2.sam2.build_sam import build_sam2_video_predictor
from pathlib import Path
import imageio.v3 as iio

def process_video_in_chunks(args, initial_bbox_list: list[list[float]], chunk_seconds: int = 2, chunk_frames: int = None):
    """
    分块处理视频，支持基于时间（秒）或基于帧数的分块
    
    参数:
        args: 参数对象，包含视频路径等信息
        initial_bbox_list: 初始边界框列表
        chunk_seconds: 每块的秒数（当chunk_frames为None时使用）
        chunk_frames: 每块的帧数（优先使用此参数，若提供则忽略chunk_seconds）
    """
    cap = cv2.VideoCapture(args.video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    device = args.device

    model_cfg = determine_model_cfg(args.model_path)
    predictor = build_sam2_video_predictor(model_cfg, args.model_path, device=device)

    mask_dir = Path(args.mask_dir) if args.mask_dir else None
    if mask_dir:
        mask_dir.mkdir(exist_ok=True, parents=True)

    if args.save_to_video:
        writer = imageio.get_writer(args.video_output_path, fps=fps, format='FFMPEG')

    # 确定每块的大小（优先使用帧数，否则使用时间）
    if chunk_frames is not None:
        chunk_size = chunk_frames
    else:
        chunk_size = chunk_seconds * fps
        
    # 输出分块信息
    if hasattr(args, 'progress_callback') and args.progress_callback:
        total_chunks = (total_frames + chunk_size - 1) // chunk_size
        args.progress_callback(0, total_frames)  # 初始化进度
    
    current_frame_idx = 0
    bbox_list = initial_bbox_list

    while current_frame_idx < total_frames:
        # Step 1: 读取 chunk 的帧
        frames = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_idx)
        chunk_frame_count = min(chunk_size, total_frames - current_frame_idx)
        
        for frame_offset in range(chunk_frame_count):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            
            # 如果有进度回调，更新处理进度
            if hasattr(args, 'progress_callback') and args.progress_callback:
                if not args.progress_callback(current_frame_idx + frame_offset, total_frames):
                    # 用户取消处理
                    cap.release()
                    if args.save_to_video:
                        writer.close()
                    del predictor
                    return False
        
        if len(frames) == 0:
            break
            
        frames_folder = save_frames_to_temp_dir(frames)
        # Step 2: 准备和初始化 predictor
        with torch.inference_mode(), torch.autocast('cuda', dtype=torch.float16):
            state = predictor.init_state(frames_folder, offload_video_to_cpu=True, offload_state_to_cpu=True)
            prompts = bbox_process(bbox_list)
            for idx, (bbox, _) in enumerate(prompts.values()):
                _, _, masks = predictor.add_new_points_or_box(state, box=bbox, frame_idx=0, obj_id=idx)

            for i, object_ids, masks in predictor.propagate_in_video(state, disable_display=False):
                mask_to_vis = {}
                bbox_to_vis = {}
                
                # 创建一个8位灰度图像，用于存储所有对象的掩码
                if mask_dir:
                    combined_mask = np.zeros((height, width), dtype=np.uint8)
                
                for obj_id, mask in zip(object_ids, masks):
                    mask = mask[0].cpu().numpy()
                    binary_mask = mask > 0.0
                    non_zero_indices = np.argwhere(binary_mask)
                    if len(non_zero_indices) == 0:
                        bbox = [0, 0, 0, 0]
                    else:
                        y_min, x_min = non_zero_indices.min(axis=0).tolist()
                        y_max, x_max = non_zero_indices.max(axis=0).tolist()
                        bbox = [x_min, y_min, x_max - x_min, y_max - y_min]

                    mask_to_vis[obj_id] = binary_mask
                    bbox_to_vis[obj_id] = bbox

                    # 将每个对象的二值掩码添加到组合掩码中，使用对象ID+1作为灰度值
                    if mask_dir:
                        combined_mask[binary_mask] = obj_id + 1

                # 保存组合掩码作为单一灰度图像
                if mask_dir:
                    mask_path = mask_dir / f'frame_{current_frame_idx+i:04}.png'
                    iio.imwrite(mask_path, combined_mask)

                if args.save_to_video:
                    img = frames[i]
                    for obj_id, mask in mask_to_vis.items():
                        mask_img = np.zeros((height, width, 3), np.uint8)
                        mask_img[mask] = COLOR[obj_id % len(COLOR)]
                        img = cv2.addWeighted(img, 1, mask_img, 0.5, 0)

                    for obj_id, bbox in bbox_to_vis.items():
                        label = f"obj_{obj_id}"
                        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), COLOR[obj_id % len(COLOR)], 2)
                        cv2.putText(img, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR[obj_id % len(COLOR)], 2)

                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    writer.append_data(img)

            # Step 3: 更新 bbox_list（取最后一帧的检测框）
            bbox_list = list(bbox_to_vis.values())

            del state
            torch.clear_autocast_cache()
            torch.cuda.empty_cache()
            gc.collect()

        current_frame_idx += len(frames)

    cap.release()
    if args.save_to_video:
        writer.close()
    del predictor

def main(args, bbox_list:list[list[float]]):
    device = args.device
    model_cfg = determine_model_cfg(args.model_path)
    predictor = build_sam2_video_predictor(model_cfg, args.model_path, device=device,)
    frames_or_path = prepare_frames_or_path(args.video_path)
    prompts = bbox_process(bbox_list)

    if args.save_to_video:
        if osp.isdir(args.video_path):
            frames = sorted([osp.join(args.video_path, f) for f in os.listdir(args.video_path) if f.endswith(".jpg")])
            loaded_frames = [cv2.imread(frame_path) for frame_path in frames]
            height, width = loaded_frames[0].shape[:2]
        else:
            cap = cv2.VideoCapture(args.video_path)
            loaded_frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                loaded_frames.append(frame)
            cap.release()
            height, width = loaded_frames[0].shape[:2]

            if len(loaded_frames) == 0:
                raise ValueError("No frames were loaded from the video.")
                
    # 获取视频总帧数
    total_frames = len(loaded_frames)

    if args.save_to_video:
        writer = imageio.get_writer(args.video_output_path, fps=30, format='FFMPEG')

    mask_dir = args.mask_dir
    if args.mask_dir is not None:
        mask_dir = Path(mask_dir)
        mask_dir.mkdir(exist_ok=True, parents=True)
    with torch.inference_mode(), torch.autocast('cuda', dtype=torch.float16):
        state = predictor.init_state(frames_or_path, offload_video_to_cpu=True, offload_state_to_cpu=True, async_loading_frames=True)
        all_masks = []
        for idx, (bbox, track_label) in enumerate(prompts.values()):
            _, _, masks = predictor.add_new_points_or_box(state, box=bbox, frame_idx=0, obj_id=idx)
            all_masks.append(masks)

        for frame_idx, object_ids, masks in predictor.propagate_in_video(state, disable_display=False):
            # 更新进度
            if hasattr(args, 'progress_callback') and args.progress_callback:
                if not args.progress_callback(frame_idx, total_frames):
                    # 用户取消了处理
                    if args.save_to_video:
                        writer.close()
                    del predictor, state
                    return False
                    
            mask_to_vis = {}
            bbox_to_vis = {}
            
            # 创建一个8位灰度图像，用于存储所有对象的掩码
            if mask_dir is not None:
                combined_mask = np.zeros((height, width), dtype=np.uint8)

            for obj_id, mask in zip(object_ids, masks):
                mask = mask[0].cpu().numpy()
                mask = mask > 0.0
                non_zero_indices = np.argwhere(mask)
                if len(non_zero_indices) == 0:
                    bbox = [0, 0, 0, 0]
                else:
                    y_min, x_min = non_zero_indices.min(axis=0).tolist()
                    y_max, x_max = non_zero_indices.max(axis=0).tolist()
                    bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
                bbox_to_vis[obj_id] = bbox
                mask_to_vis[obj_id] = mask
                
                # 将每个对象的二值掩码添加到组合掩码中，使用对象ID+1作为灰度值
                if mask_dir is not None:
                    combined_mask[mask] = obj_id + 1
            
            # 保存组合掩码作为单一灰度图像
            if mask_dir is not None:
                mask_path = mask_dir / f'frame_{frame_idx:04}.png'
                iio.imwrite(mask_path, combined_mask)

            if args.save_to_video:
                img = loaded_frames[frame_idx]
                for obj_id, mask in mask_to_vis.items():
                    mask_img = np.zeros((height, width, 3), np.uint8)
                    mask_img[mask] = COLOR[obj_id % len(COLOR)]
                    img = cv2.addWeighted(img, 1, mask_img, 0.4, 0)

                for obj_id, bbox in bbox_to_vis.items():
                    label = f"obj_{obj_id}"
                    cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), COLOR[obj_id % len(COLOR)], 2)
                    cv2.putText(img, label, (bbox[0], bbox[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                COLOR[obj_id % len(COLOR)], 2)

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                writer.append_data(img)

        if args.save_to_video:
            writer.close()

    del predictor, state
    gc.collect()
    torch.clear_autocast_cache()
    torch.cuda.empty_cache()
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_path", default="assets/05_default_juggle.mp4")
    parser.add_argument("--model_path", default="models/sam2/checkpoints/sam2.1_hiera_tiny.pt", help="Path to the model checkpoint.")
    parser.add_argument("--video_output_path", default="processed_video.mp4", help="Path to save the output video.")
    parser.add_argument("--save_to_video", default=True, help="Save results to a video.")
    parser.add_argument("--mask_dir", help="If provided, save mask images to the given directory")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    main(args, bbox_list=[[607.75244140625, 126.3901596069336, 791.4397583007812, 356.09332275390625],
                          [612.8888549804688, 284.82171630859375, 692.8299560546875, 362.6283874511719],
                          [638.74560546875, 598.923095703125, 687.992431640625, 663.7514038085938],
                          [733.8016357421875, 612.997314453125, 782.0617065429688, 671.3180541992188],
                          [639.07861328125, 345.004638671875, 775.4666748046875, 615.2918701171875],
                          [797.278564453125, 261.87451171875, 818.1863403320312, 283.78070068359375]])
    # process_video_in_chunks(args, initial_bbox_list=[[364.53216552734375, 426.52178955078125, 437.9630126953125, 500.3838195800781],
    #                                                  [260.3464050292969, 0.1987624168395996, 445.94500732421875, 198.92283630371094],
    #                                                  [829.1287841796875, 292.64874267578125, 999.095703125, 544.427978515625],
    #                                                  [568.9965209960938, 291.2940673828125, 738.1513671875, 544.0554809570312]])