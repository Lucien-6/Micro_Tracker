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


def process_video_with_refinement(args, annotations_data):
    """
    新的统一处理函数，支持refinement
    
    Args:
        args: 处理参数对象，包含以下属性:
            - video_path (str): 视频路径
            - model_path (str): SAM2模型路径
            - device (str): 设备 (cuda/cpu)
            - video_output_path (str): 输出视频路径
            - mask_dir (str, optional): 掩码保存目录
            - save_to_video (bool): 是否保存视频
            - progress_callback (callable, optional): 进度回调函数
        annotations_data (dict): 统一格式的标注数据
            格式: {frame_idx: {obj_id: {"box": [x1,y1,x2,y2], "points": [(x,y)], "labels": [0/1], "mask": np.array}}}
    
    Workflow:
        1. 初始化SAM2模型和单一inference state
        2. 按帧顺序添加所有提示（box和points）
        3. 一次性传播整个视频
        4. 保存结果（视频和掩码）
    
    Notes:
        - 支持混合提示类型（box + points）
        - 使用单一inference_state保持temporal consistency
    
    Prompt Handling Strategy (符合SAM2官方规范):
        - Box和Points在同一次API调用中传入（如果都存在）
        - SAM2内部会自动将box转换为2个特殊点（标签2和3，代表左上角和右下角）
        - 然后与用户points拼接，形成统一的点集传入Transformer Encoder
        - 这确保了所有提示在模型中的完整语义关联，提升refinement质量
        - 始终使用clear_old_points=True（符合SAM2 API约定）
        
        参考：models/sam2/video_predictor_example.ipynb, Cell 46
                models/sam2/sam2/sam2_video_predictor.py, L294-318
    """
    progress_callback = getattr(args, 'progress_callback', None)
    
    # 记录每个对象的首次标注帧（用于后续过滤）
    obj_first_frame = {}
    for frame_idx, frame_data in annotations_data.items():
        for obj_id in frame_data.keys():
            if obj_id not in obj_first_frame:
                obj_first_frame[obj_id] = frame_idx
    
    # 1. 初始化SAM2
    if progress_callback:
        progress_callback("==== Refinement模式: SAM2处理 ====", 0)
        progress_callback("正在初始化SAM2模型...", 5)
    
    try:
        # 延迟导入SAM2
        from sam2.build_sam import build_sam2_video_predictor
        
        model_cfg = determine_model_cfg(args.model_path)
        predictor = build_sam2_video_predictor(model_cfg, args.model_path, device=args.device)
        
        if progress_callback:
            progress_callback(f"✓ 模型加载成功: {Path(args.model_path).name}", 10)
    except Exception as e:
        if progress_callback:
            progress_callback(f"✗ 模型加载失败: {e}")
        raise
    
    # 2. 初始化inference state（只做一次）
    if progress_callback:
        progress_callback("正在加载视频...", 15)
    
    try:
        inference_state = predictor.init_state(video_path=args.video_path)
        
        if progress_callback:
            progress_callback(f"✓ 视频加载成功: {Path(args.video_path).name}", 20)
    except Exception as e:
        if progress_callback:
            progress_callback(f"✗ 视频加载失败: {e}")
        raise
    
    # 3. 获取视频/图像序列信息
    input_type = getattr(args, 'input_type', 'video')
    
    if input_type == "image_sequence" and getattr(args, 'image_files', None):
        # 图像序列模式
        total_frames = len(args.image_files)
        fps = getattr(args, 'image_sequence_fps', 10.0)
        if progress_callback:
            progress_callback(f"图像序列信息: {total_frames}帧, {fps:.2f} FPS", 20)
    else:
        # 视频模式
        cap = cv2.VideoCapture(args.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        if progress_callback:
            progress_callback(f"视频信息: {total_frames}帧, {fps:.2f} FPS", 20)
    
    if progress_callback:
        progress_callback(f"\n==== 添加所有提示 ====", 25)
        progress_callback(f"标注帧数: {len(annotations_data)}", 25)
    
    # 4. 按帧顺序添加所有提示
    # 首先确保所有对象都已注册（避免初始化问题）
    all_obj_ids = set()
    for frame_data in annotations_data.values():
        all_obj_ids.update(frame_data.keys())
    
    # 先处理所有的box提示（必须在points之前）
    for frame_idx in sorted(annotations_data.keys()):
        frame_annotations = annotations_data[frame_idx]
        
        if progress_callback:
            progress_callback(f"\n处理第 {frame_idx} 帧的标注:")
        
        for obj_id, prompts in frame_annotations.items():
            try:
                # 准备参数
                box = None
                points = None
                labels = None
                
                # 处理box提示
                if "box" in prompts and prompts["box"]:
                    box = np.array(prompts["box"], dtype=np.float32)
                    if progress_callback:
                        progress_callback(f"  - 对象 {obj_id}: 添加边界框 {prompts['box']}")
                
                # 处理点击提示
                if "points" in prompts and prompts["points"]:
                    points = np.array(prompts["points"], dtype=np.float32)
                    labels = np.array(prompts["labels"], dtype=np.int32)
                    if progress_callback:
                        num_pos = sum(1 for l in labels if l == 1)
                        num_neg = sum(1 for l in labels if l == 0)
                        progress_callback(f"  - 对象 {obj_id}: 添加 {num_pos} 个正向点击, {num_neg} 个负向点击")
                
                # === 添加提示到SAM2（符合官方API规范）===
                # 策略：一次性调用添加所有提示（box和points会在SAM2内部自动合并）
                # 参考：models/sam2/video_predictor_example.ipynb, Cell 46
                
                # 构建提示参数字典
                prompt_kwargs = {
                    "inference_state": inference_state,
                    "frame_idx": frame_idx,
                    "obj_id": obj_id,
                    "clear_old_points": True  # 始终清除旧点（符合SAM2 API约定）
                }
                
                # 添加box（如果存在）
                if box is not None:
                    prompt_kwargs["box"] = box
                
                # 添加points和labels（如果存在）
                if points is not None and len(points) > 0:
                    prompt_kwargs["points"] = points
                    prompt_kwargs["labels"] = labels
                
                # 验证：至少有一个提示类型
                if "box" not in prompt_kwargs and "points" not in prompt_kwargs:
                    if progress_callback:
                        progress_callback(f"    ⚠️ 对象 {obj_id} 没有任何提示，跳过")
                    continue
                
                # 一次性调用SAM2 API（box和points会在内部自动合并）
                _, out_obj_ids, out_mask_logits = predictor.add_new_points_or_box(**prompt_kwargs)
                
                if progress_callback:
                    # 生成详细的提示信息
                    prompt_types = []
                    if "box" in prompt_kwargs:
                        prompt_types.append("box")
                    if "points" in prompt_kwargs:
                        num_pos = sum(1 for l in labels if l == 1)
                        num_neg = sum(1 for l in labels if l == 0)
                        prompt_types.append(f"{num_pos}正向点+{num_neg}负向点")
                    progress_callback(f"    ✓ 成功添加对象 {obj_id} 的提示 ({', '.join(prompt_types)})")
            
            except Exception as e:
                if progress_callback:
                    progress_callback(f"    ✗ 警告: 添加对象 {obj_id} 提示失败: {e}")
                continue
    
    # 5. 一次性传播整个视频
    if progress_callback:
        progress_callback(f"\n==== 传播到整个视频 ====", 30)
        progress_callback(f"对象首次标注帧: {obj_first_frame}", 30)
    
    all_masks = {}
    
    try:
        frame_count = 0
        for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(inference_state):
            # 存储该帧的所有对象masks（仅保存已到达首次标注帧的对象）
            frame_masks = {}
            for i, obj_id in enumerate(out_obj_ids):
                # 检查当前帧是否在对象的有效追踪范围内
                if out_frame_idx >= obj_first_frame.get(obj_id, 0):
                    # 转换为二值mask
                    mask = (out_mask_logits[i] > 0.0).cpu().numpy().squeeze()
                    frame_masks[obj_id] = mask
                # 否则跳过该对象（不保存在首次标注帧之前的mask）
            
            if frame_masks:  # 只有当帧中有有效对象时才保存
                all_masks[out_frame_idx] = frame_masks
            frame_count += 1
            
            # 进度回调（每20帧报告一次）
            if progress_callback and frame_count % 20 == 0:
                # 传播阶段占0-70%的进度
                progress = int(frame_count / total_frames * 70)
                progress_callback(f"  传播进度: {frame_count}/{total_frames}帧", progress)
    
    except Exception as e:
        if progress_callback:
            progress_callback(f"  ✗ 错误: 传播失败: {e}")
        raise
    
    if progress_callback:
        progress_callback(f"  ✓ 传播完成，获得 {len(all_masks)} 帧结果", 70)  # 传播完成算70%
        
        # 统计每个对象的实际追踪范围
        obj_tracking_stats = {}
        for frame_idx, frame_masks in all_masks.items():
            for obj_id in frame_masks.keys():
                if obj_id not in obj_tracking_stats:
                    obj_tracking_stats[obj_id] = {"first": frame_idx, "last": frame_idx, "count": 0}
                obj_tracking_stats[obj_id]["last"] = frame_idx
                obj_tracking_stats[obj_id]["count"] += 1
        
        progress_callback(f"\n对象追踪统计:")
        for obj_id, stats in sorted(obj_tracking_stats.items()):
            progress_callback(f"  对象 {obj_id}: 第{stats['first']}-{stats['last']}帧 (共{stats['count']}帧)")
    
    # 6. 保存结果
    try:
        save_results(
            all_masks,
            args.video_path,
            args.video_output_path,
            args.mask_dir,
            args.save_to_video,
            progress_callback,
            input_type=getattr(args, 'input_type', 'video'),
            image_files=getattr(args, 'image_files', None),
            image_sequence_fps=getattr(args, 'image_sequence_fps', 10.0)
        )
    except Exception as e:
        if progress_callback:
            progress_callback(f"\n✗ 保存失败: {e}")
        raise
    
    if progress_callback:
        progress_callback("\n✅ Refinement模式处理完成！")


def save_results(all_masks, video_path, output_path, mask_dir, save_to_video, 
                 progress_callback=None, input_type="video", image_files=None, 
                 image_sequence_fps=10.0):
    """
    保存处理结果（视频和掩码）
    
    Args:
        all_masks (dict): 所有帧的masks，{frame_idx: {obj_id: mask_array}}
        video_path (str): 输入视频路径或图像序列工作目录
        output_path (str): 输出视频路径
        mask_dir (str): 掩码保存目录
        save_to_video (bool): 是否保存视频
        progress_callback (callable, optional): 进度回调
        input_type (str): 输入类型 "video" 或 "image_sequence"
        image_files (list, optional): 图像文件列表（图像序列模式）
        image_sequence_fps (float): 图像序列帧率
    
    Notes:
        - 视频：将masks叠加到原始帧上
        - 掩码：保存为8位灰度图，像素值=obj_id+1，背景=0
    """
    if progress_callback:
        progress_callback("\n==== 保存结果 ====")
    
    # 根据输入类型初始化帧读取器
    if input_type == "image_sequence" and image_files:
        # 图像序列模式
        first_img = cv2.imread(image_files[0])
        if first_img is None:
            raise RuntimeError(f"无法读取图像: {image_files[0]}")
        height, width = first_img.shape[:2]
        fps = image_sequence_fps
        total_frames = len(image_files)
        cap = None  # 图像序列不使用VideoCapture
        
        if progress_callback:
            progress_callback(f"图像序列模式: {total_frames}帧, {fps:.1f}fps")
    else:
        # 视频模式
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 视频写入器
    video_writer = None
    if save_to_video:
        # 使用 mp4v 编解码器（Windows 兼容性最佳）
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # 验证视频写入器是否成功初始化
        if not video_writer.isOpened():
            raise RuntimeError(f"无法初始化视频写入器: {output_path}")
        
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
    
    # 根据输入类型决定帧读取方式
    if input_type == "image_sequence" and image_files:
        # 图像序列模式：遍历图像文件
        for img_path in image_files:
            frame = cv2.imread(img_path)
            if frame is None:
                frame_idx += 1
                continue
            
            # 叠加masks
            if frame_idx in all_masks:
                for obj_id, mask in all_masks[frame_idx].items():
                    if mask.shape != (height, width):
                        mask_resized = cv2.resize(mask.astype(np.uint8), (width, height), 
                                                 interpolation=cv2.INTER_NEAREST)
                    else:
                        mask_resized = mask.astype(np.uint8)
                    
                    color = np.array(color_map[int(obj_id) % len(color_map)])
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
                    mask_image[mask_resized > 0] = int(obj_id) + 1
                
                mask_path = Path(mask_dir) / f"frame_{frame_idx:05d}.png"
                cv2.imwrite(str(mask_path), mask_image)
            
            frame_idx += 1
            
            if progress_callback and frame_idx % 50 == 0:
                progress = 70 + int(frame_idx / total_frames * 30)
                progress_callback(f"保存进度: {frame_idx}/{total_frames}帧", progress)
    else:
        # 视频模式：使用VideoCapture
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
                    color = np.array(color_map[int(obj_id) % len(color_map)])
                    
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
                    mask_image[mask_resized > 0] = int(obj_id) + 1
                
                mask_path = Path(mask_dir) / f"frame_{frame_idx:05d}.png"
                cv2.imwrite(str(mask_path), mask_image)
            
            frame_idx += 1
            
            # 进度报告（保存阶段占70-100%的进度）
            if progress_callback and frame_idx % 50 == 0:
                progress = 70 + int(frame_idx / total_frames * 30)
                progress_callback(f"保存进度: {frame_idx}/{total_frames}帧", progress)
    
    # 释放资源
    if cap is not None:
        cap.release()
    if video_writer:
        video_writer.release()
    
    if progress_callback:
        progress_callback(f"✓ 保存完成!", 100)  # 保存完成算100%
        if save_to_video:
            progress_callback(f"  视频: {output_path}")
        if mask_dir:
            progress_callback(f"  掩码: {mask_dir} ({frame_idx}张)")


def convert_legacy_annotations_to_refinement_format(multi_frame_annotations):
    """
    将旧格式的标注数据转换为新的refinement格式
    
    Args:
        multi_frame_annotations (dict): 旧格式 {frame_idx: [[x1,y1,x2,y2,obj_id], ...]}
    
    Returns:
        dict: 新格式 {frame_idx: {obj_id: {"box": [x1,y1,x2,y2], "points": [], "labels": []}}}
    """
    refinement_annotations = {}
    
    for frame_idx, bbox_list in multi_frame_annotations.items():
        frame_data = {}
        for bbox in bbox_list:
            x1, y1, x2, y2, obj_id = bbox
            frame_data[obj_id] = {
                "box": [x1, y1, x2, y2],
                "points": [],  # 暂时没有点击
                "labels": []
            }
        refinement_annotations[frame_idx] = frame_data
    
    return refinement_annotations


def process_video_multiframe(args, multi_frame_annotations):
    """
    多帧SAM2提示处理主函数 - 现在使用refinement模式
    
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
            旧格式: {frame_idx: [[x1,y1,x2,y2,obj_id], ...]}
            新格式: {frame_idx: {obj_id: {"box": [...], "points": [...], "labels": [...]}}}
    
    Notes:
        - 现在使用refinement模式处理
        - 自动检测并转换旧格式数据
        - 支持混合提示类型
    """
    progress_callback = getattr(args, 'progress_callback', None)
    
    # 检测数据格式
    needs_conversion = False
    if multi_frame_annotations:
        # 检查第一个帧的数据格式
        first_frame = next(iter(multi_frame_annotations))
        first_data = multi_frame_annotations[first_frame]
        
        # 如果是list，说明是旧格式
        if isinstance(first_data, list):
            needs_conversion = True
    
    # 转换数据格式（如果需要）
    if needs_conversion:
        if progress_callback:
            progress_callback("检测到旧格式标注数据，正在转换...")
        annotations_data = convert_legacy_annotations_to_refinement_format(multi_frame_annotations)
    else:
        # 已经是新格式
        annotations_data = multi_frame_annotations
    
    # 调用新的refinement处理函数
    process_video_with_refinement(args, annotations_data)


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

