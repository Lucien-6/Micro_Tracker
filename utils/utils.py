import os
import tempfile

import cv2
import numpy as np
from PIL import Image


def bbox_process(bbox_list, labels=None):
    """
    处理边界框列表，转换为SAM2所需的prompts格式
    
    Args:
        bbox_list: 边界框列表，支持两种格式：
                   - [x1, y1, x2, y2] (4个值)
                   - [x1, y1, x2, y2, obj_id] (5个值，Phase 1 MVP格式)
        labels: 可选的标签列表
    
    Returns:
        prompts: {obj_id: ((x1, y1, x2, y2), label)}
    """
    prompts = {}
    for fid, bbox in enumerate(bbox_list):
        # Phase 1 MVP: 支持5个值的格式 [x1, y1, x2, y2, obj_id]
        if len(bbox) == 5:
            x1, y1, x2, y2, obj_id = bbox
            label = labels[fid] if labels else f"obj_{obj_id}"
        elif len(bbox) == 4:
            x1, y1, x2, y2 = bbox
            obj_id = fid
            label = labels[fid] if labels else f"obj_{fid}"
        else:
            raise ValueError(f"Invalid bbox format: expected 4 or 5 values, got {len(bbox)}")
        
        prompts[obj_id] = ((int(x1), int(y1), int(x2), int(y2)), label)
    return prompts

def determine_model_cfg(model_path):
    if "large" in model_path:
        return "configs/sam2.1/sam2.1_hiera_l.yaml"
    elif "base_plus" in model_path:
        return "configs/sam2.1/sam2.1_hiera_b+.yaml"
    elif "small" in model_path:
        return "configs/sam2.1/sam2.1_hiera_s.yaml"
    elif "tiny" in model_path:
        return "configs/sam2.1/sam2.1_hiera_t.yaml"
    else:
        raise ValueError("Unknown model size in path!")

def load_txt(gt_path):
    with open(gt_path, 'r') as f:
        gt = f.readlines()
    prompts = {}
    for fid, line in enumerate(gt):
        line = line.strip()
        if len(line) == 0:
            continue
        x, y, w, h = map(float, line.split(','))
        x, y, w, h = int(x), int(y), int(w), int(h)
        prompts[fid] = ((x, y, x + w, y + h), 0)
    return prompts

def prepare_frames_or_path(video_path):
    # 支持常见的视频格式
    video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".MP4", ".AVI", ".MOV", ".MKV"]
    is_video_file = any(video_path.endswith(ext) for ext in video_extensions)
    
    if is_video_file or os.path.isdir(video_path):
        return video_path
    else:
        raise ValueError("Invalid video_path format. Should be a video file (.mp4, .avi, .mov, .mkv) or a directory of jpg frames.")


def save_frames_to_temp_dir(frames: list[np.ndarray]) -> str:
    tmp_dir = tempfile.mkdtemp(prefix="chunk_frames_")
    for i, frame in enumerate(frames):
        path = os.path.join(tmp_dir, f"{i:04d}.jpg")
        # OpenCV uses BGR, PIL expects RGB
        Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(path)
    return tmp_dir


def extract_frames(
        video_path,
        output_dir,
        frame_ids=None,
        frame_range=None):

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames in video: {total_frames}")

    selected_frames = set()
    if frame_ids:
        selected_frames.update([i for i in frame_ids if 0 <= i < total_frames])
    if frame_range:
        start, end = frame_range
        selected_frames.update(range(max(0, start), min(end + 1, total_frames)))

    selected_frames = sorted(selected_frames)
    print(f"Extracting frames: {selected_frames}")

    current_frame = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if current_frame in selected_frames:
            filename = os.path.join(output_dir, f"frame_{current_frame:05d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Saved frame {current_frame} to {filename}")

        current_frame += 1
        if current_frame > max(selected_frames):
            break

    cap.release()
    print("Done.")

# extract_frames('assets/05_default_juggle.mp4',
#                'assets',
#                [0])