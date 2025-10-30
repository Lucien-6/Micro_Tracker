"""
Phase 2: 多帧SAM2提示处理脚本

实现分段处理策略，在每个标注帧添加SAM2提示

Author: Lucien (lucien-6@qq.com)
Date: 2025-10-30
"""

import numpy as np
import torch
import cv2
from pathlib import Path
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 延迟导入SAM2（避免测试时import错误）
# from sam2.build_sam import build_sam2_video_predictor
from utils.utils import determine_model_cfg


def analyze_frame_segments(annotated_frames, total_frames):
    """
    分析标注帧，计算处理段
    
    Args:
        annotated_frames (list): 排序后的标注帧列表，例如 [0, 50, 120]
        total_frames (int): 视频总帧数
    
    Returns:
        list: 处理段列表 [(start, end), ...]
              例如 [(0, 49), (50, 119), (120, 199)]
    
    Notes:
        - 每个段从一个标注帧开始，到下一个标注帧的前一帧结束
        - 最后一段从最后一个标注帧到视频末尾
    
    Examples:
        >>> analyze_frame_segments([0, 50, 120], 200)
        [(0, 49), (50, 119), (120, 199)]
        
        >>> analyze_frame_segments([0], 100)
        [(0, 99)]
    """
    if not annotated_frames:
        return []
    
    segments = []
    for i, frame_idx in enumerate(annotated_frames):
        start = frame_idx
        
        # 结束帧：下一个标注帧的前一帧，或视频末尾
        if i < len(annotated_frames) - 1:
            end = annotated_frames[i + 1] - 1
        else:
            end = total_frames - 1
        
        segments.append((start, end))
    
    return segments


def process_segment(predictor, inference_state, segment_start, segment_end, 
                   frame_annotations, progress_callback=None):
    """
    处理单个帧段
    
    Args:
        predictor: SAM2 video predictor实例
        inference_state: SAM2 inference state
        segment_start (int): 段起始帧索引
        segment_end (int): 段结束帧索引
        frame_annotations (list): 该起始帧的标注 [[x1,y1,x2,y2,obj_id], ...]
        progress_callback (callable, optional): 进度回调函数
    
    Returns:
        dict: 该段的所有帧masks，格式 {frame_idx: {obj_id: mask_array}}
    
    Raises:
        Exception: SAM2处理失败时抛出
    
    Notes:
        - 在segment_start帧添加所有边界框提示
        - 使用propagate_in_video前向传播到segment_end
        - clear_old_points=False，累积所有标注
    """
    if progress_callback:
        progress_callback(f"  → 处理段 [{segment_start}-{segment_end}]帧")
    
    # 1. 在起始帧添加所有边界框提示
    for bbox in frame_annotations:
        x1, y1, x2, y2, obj_id = bbox
        
        try:
            _, out_obj_ids, out_mask_logits = predictor.add_new_points_or_box(
                inference_state=inference_state,
                frame_idx=segment_start,
                obj_id=obj_id,
                box=np.array([x1, y1, x2, y2], dtype=np.float32),
                clear_old_points=True  # Phase 2修正: 必须清除旧点以添加box
            )
            
            if progress_callback:
                progress_callback(f"    ✓ 第 {segment_start} 帧添加对象 {obj_id} 的提示")
        
        except Exception as e:
            if progress_callback:
                progress_callback(f"    ✗ 警告: 添加对象 {obj_id} 提示失败: {e}")
            continue
    
    # 2. 前向传播
    segment_masks = {}
    
    try:
        for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(
            inference_state,
            start_frame_idx=segment_start,
            max_frame_num_to_track=segment_end - segment_start + 1,
            reverse=False
        ):
            # 存储该帧的所有对象masks
            frame_masks = {}
            for i, obj_id in enumerate(out_obj_ids):
                # 转换为二值mask
                mask = (out_mask_logits[i] > 0.0).cpu().numpy().squeeze()
                frame_masks[obj_id] = mask
            
            segment_masks[out_frame_idx] = frame_masks
            
            # 进度回调（每10帧报告一次）
            if progress_callback and (out_frame_idx - segment_start) % 10 == 0:
                progress = int((out_frame_idx - segment_start) / (segment_end - segment_start + 1) * 100)
                progress_callback(f"    传播进度: {progress}% ({out_frame_idx}/{segment_end}帧)")
    
    except Exception as e:
        if progress_callback:
            progress_callback(f"    ✗ 错误: 传播失败: {e}")
        raise
    
    if progress_callback:
        progress_callback(f"  ✓ 段处理完成，获得 {len(segment_masks)} 帧结果")
    
    return segment_masks


def save_results(all_masks, video_path, output_path, mask_dir, save_to_video, progress_callback=None):
    """
    保存处理结果（视频和掩码）
    
    Args:
        all_masks (dict): 所有帧的masks，{frame_idx: {obj_id: mask_array}}
        video_path (str): 输入视频路径
        output_path (str): 输出视频路径
        mask_dir (str): 掩码保存目录
        save_to_video (bool): 是否保存视频
        progress_callback (callable, optional): 进度回调
    
    Notes:
        - 视频：将masks叠加到原始帧上
        - 掩码：保存为8位灰度图，像素值=obj_id+1，背景=0
    """
    if progress_callback:
        progress_callback("\n==== 保存结果 ====")
    
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 视频写入器
    video_writer = None
    if save_to_video:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if progress_callback:
            progress_callback(f"创建输出视频: {output_path}")
    
    # 掩码目录
    if mask_dir:
        Path(mask_dir).mkdir(parents=True, exist_ok=True)
        if progress_callback:
            progress_callback(f"创建掩码目录: {mask_dir}")
    
    # 颜色映射（用于可视化）
    color_map = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255),
        (192, 192, 192), (128, 128, 0)
    ]
    
    # 逐帧保存
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 叠加masks
        if frame_idx in all_masks:
            for obj_id, mask in all_masks[frame_idx].items():
                # 调整mask尺寸
                if mask.shape != (height, width):
                    mask_resized = cv2.resize(mask.astype(np.uint8), (width, height), 
                                             interpolation=cv2.INTER_NEAREST)
                else:
                    mask_resized = mask.astype(np.uint8)
                
                # 选择颜色
                color = np.array(color_map[obj_id % len(color_map)])
                
                # 半透明叠加
                frame[mask_resized > 0] = (frame[mask_resized > 0] * 0.5 + color * 0.5).astype(np.uint8)
        
        # 保存视频帧
        if video_writer:
            video_writer.write(frame)
        
        # 保存掩码
        if mask_dir and frame_idx in all_masks:
            mask_image = np.zeros((height, width), dtype=np.uint8)
            for obj_id, mask in all_masks[frame_idx].items():
                if mask.shape != (height, width):
                    mask_resized = cv2.resize(mask.astype(np.uint8), (width, height),
                                             interpolation=cv2.INTER_NEAREST)
                else:
                    mask_resized = mask.astype(np.uint8)
                
                # 像素值 = obj_id + 1（背景为0）
                mask_image[mask_resized > 0] = obj_id + 1
            
            mask_path = Path(mask_dir) / f"frame_{frame_idx:05d}.png"
            cv2.imwrite(str(mask_path), mask_image)
        
        frame_idx += 1
        
        # 进度报告
        if progress_callback and frame_idx % 50 == 0:
            progress = int(frame_idx / total_frames * 100)
            progress_callback(f"保存进度: {progress}% ({frame_idx}/{total_frames}帧)")
    
    cap.release()
    if video_writer:
        video_writer.release()
    
    if progress_callback:
        progress_callback(f"✓ 保存完成!")
        if save_to_video:
            progress_callback(f"  视频: {output_path}")
        if mask_dir:
            progress_callback(f"  掩码: {mask_dir} ({frame_idx}张)")


def process_video_multiframe(args, multi_frame_annotations):
    """
    多帧SAM2提示处理主函数
    
    Args:
        args: 参数对象，包含以下属性:
            - video_path (str): 视频路径
            - model_path (str): SAM2模型路径
            - device (str): 设备 (cuda/cpu)
            - video_output_path (str): 输出视频路径
            - mask_dir (str, optional): 掩码保存目录
            - save_to_video (bool): 是否保存视频
            - progress_callback (callable, optional): 进度回调函数
        multi_frame_annotations (dict): 多帧标注数据
            格式: {frame_idx: [[x1,y1,x2,y2,obj_id], ...]}
    
    Workflow:
        1. 初始化SAM2模型和inference state
        2. 分析标注帧，计算处理段
        3. 逐段处理：在每个段的起始帧添加提示，然后前向传播
        4. 保存结果（视频和掩码）
    
    Examples:
        >>> args = Args()
        >>> args.video_path = "video.mp4"
        >>> annotations = {0: [[10,20,100,100,0]], 50: [[15,25,105,105,0]]}
        >>> process_video_multiframe(args, annotations)
    """
    progress_callback = getattr(args, 'progress_callback', None)
    
    # 1. 初始化SAM2
    if progress_callback:
        progress_callback("==== Phase 2: 多帧SAM2提示处理 ====")
        progress_callback("正在初始化SAM2模型...")
    
    try:
        # 延迟导入SAM2
        from sam2.build_sam import build_sam2_video_predictor
        
        model_cfg = determine_model_cfg(args.model_path)
        predictor = build_sam2_video_predictor(model_cfg, args.model_path, device=args.device)
        
        if progress_callback:
            progress_callback(f"✓ 模型加载成功: {Path(args.model_path).name}")
    except Exception as e:
        if progress_callback:
            progress_callback(f"✗ 模型加载失败: {e}")
        raise
    
    # 2. 初始化inference state
    if progress_callback:
        progress_callback("正在加载视频...")
    
    try:
        inference_state = predictor.init_state(video_path=args.video_path)
        
        if progress_callback:
            progress_callback(f"✓ 视频加载成功: {Path(args.video_path).name}")
    except Exception as e:
        if progress_callback:
            progress_callback(f"✗ 视频加载失败: {e}")
        raise
    
    # 3. 获取视频信息
    cap = cv2.VideoCapture(args.video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    if progress_callback:
        progress_callback(f"视频信息: {total_frames}帧, {fps:.2f} FPS")
    
    # 4. 分析标注帧和处理段
    annotated_frames = sorted(multi_frame_annotations.keys())
    segments = analyze_frame_segments(annotated_frames, total_frames)
    
    if progress_callback:
        progress_callback(f"\n==== 标注分析 ====")
        progress_callback(f"标注帧数: {len(annotated_frames)}")
        progress_callback(f"标注帧: {annotated_frames}")
        progress_callback(f"处理段数: {len(segments)}")
        for i, (start, end) in enumerate(segments):
            progress_callback(f"  段{i+1}: 第{start}-{end}帧 ({end-start+1}帧)")
    
    # 5. 逐段处理
    all_masks = {}
    
    if progress_callback:
        progress_callback(f"\n==== 开始分段处理 ====")
    
    for seg_idx, (seg_start, seg_end) in enumerate(segments):
        if progress_callback:
            progress_callback(f"\n--- 段 {seg_idx+1}/{len(segments)} ---")
        
        # === Phase 2修正: 每个段重新初始化inference_state ===
        # 这是必需的，因为SAM2的inference_state在每个段之间不兼容
        if seg_idx > 0:
            if progress_callback:
                progress_callback(f"  重新初始化inference_state（段间隔离）")
            
            try:
                inference_state = predictor.init_state(video_path=args.video_path)
            except Exception as e:
                if progress_callback:
                    progress_callback(f"  ✗ inference_state初始化失败: {e}")
                raise
        
        # 获取该段起始帧的标注
        frame_annotations = multi_frame_annotations[seg_start]
        
        if progress_callback:
            obj_ids = [bbox[4] for bbox in frame_annotations]
            progress_callback(f"  起始帧: 第{seg_start}帧")
            progress_callback(f"  对象数: {len(frame_annotations)}")
            progress_callback(f"  对象ID: {obj_ids}")
        
        # 处理该段
        try:
            segment_masks = process_segment(
                predictor, 
                inference_state,
                seg_start, 
                seg_end,
                frame_annotations,
                progress_callback
            )
            
            # 合并到总结果
            all_masks.update(segment_masks)
            
            if progress_callback:
                progress_callback(f"  ✓ 段 {seg_idx+1} 完成")
        
        except Exception as e:
            if progress_callback:
                progress_callback(f"  ✗ 段 {seg_idx+1} 处理失败: {e}")
            raise
    
    # 6. 保存结果
    try:
        save_results(
            all_masks,
            args.video_path,
            args.video_output_path,
            getattr(args, 'mask_dir', None),
            getattr(args, 'save_to_video', True),
            progress_callback
        )
    except Exception as e:
        if progress_callback:
            progress_callback(f"✗ 保存结果失败: {e}")
        raise
    
    if progress_callback:
        progress_callback("\n==== Phase 2 多帧处理完成！ ====")


# 向后兼容的入口函数
def main(args, bbox_list):
    """
    兼容旧接口的入口函数
    
    Args:
        args: 参数对象
        bbox_list: 边界框数据，可以是：
            - dict: {frame_idx: [[x1,y1,x2,y2,id], ...]}  # 多帧
            - list: [[x1,y1,x2,y2,id], ...]                # 单帧（转换为{0: bbox_list}）
    
    Notes:
        如果是字典且帧数>1，使用多帧处理
        否则退化为单帧处理（兼容Phase 1）
    """
    if isinstance(bbox_list, dict):
        # 字典格式
        if len(bbox_list) > 1:
            # 多帧模式
            process_video_multiframe(args, bbox_list)
        else:
            # 单帧（转换后处理）
            process_video_multiframe(args, bbox_list)
    else:
        # 列表格式：转换为单帧字典
        single_frame_annotations = {0: bbox_list}
        process_video_multiframe(args, single_frame_annotations)


if __name__ == "__main__":
    print("Phase 2: 多帧SAM2提示处理脚本")
    print("请通过Micro_Tracker GUI或processing_thread调用此脚本")

