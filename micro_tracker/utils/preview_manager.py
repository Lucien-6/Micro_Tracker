"""
实时Mask预览管理器

提供SAM2单帧预测功能，用于标注界面的实时mask预览。

Author: Lucien (lucien-6@qq.com)
Date: 2025-10-31
"""

import numpy as np
import torch
import cv2
from PyQt5.QtCore import QThread, pyqtSignal


class PreviewThread(QThread):
    """
    异步预测线程，避免阻塞UI
    
    Signals:
        preview_ready: 预测完成信号，参数为(obj_id: int, mask: np.ndarray)
    """
    preview_ready = pyqtSignal(int, object)  # (obj_id, mask)
    
    def __init__(self, predictor, image, prompts):
        """
        初始化预测线程
        
        Args:
            predictor: SAM2ImagePredictor实例
            image: RGB格式的图像数组
            prompts: 提示数据字典 {"box": [...], "points": [...], "labels": [...], "obj_id": int}
        """
        super().__init__()
        self.predictor = predictor
        self.image = image
        self.prompts = prompts
    
    def run(self):
        """执行异步预测"""
        try:
            # 提取提示
            box = self.prompts.get("box")
            points = self.prompts.get("points")
            labels = self.prompts.get("labels")
            obj_id = self.prompts.get("obj_id", 0)
            
            # 调用预测
            masks, scores, logits = self.predictor.predict(
                point_coords=np.array(points) if points else None,
                point_labels=np.array(labels) if labels else None,
                box=np.array(box) if box else None,
                multimask_output=False
            )
            
            # 取第一个mask
            mask = masks[0] if len(masks) > 0 else None
            if mask is not None:
                self.preview_ready.emit(obj_id, mask)
        
        except Exception as e:
            print(f"预览预测失败: {e}")
            import traceback
            traceback.print_exc()


class MaskPreviewManager:
    """
    Mask预览管理器
    
    负责管理SAM2ImagePredictor实例，提供单帧mask预测功能。
    采用懒加载策略，首次使用时才初始化模型。
    """
    
    def __init__(self, main_window):
        """
        初始化预览管理器
        
        Args:
            main_window: 主窗口引用
        """
        self.main_window = main_window
        self.predictor = None  # SAM2ImagePredictor实例（懒加载）
        self.current_frame_cache = None  # 缓存当前帧RGB图像
        self.current_frame_idx = -1  # 当前帧索引
        self.preview_enabled = True  # 是否启用预览
        self.preview_thread = None  # 异步预测线程
        
    def initialize_predictor(self):
        """
        懒加载：首次使用时初始化预测器
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        if self.predictor is not None:
            return True
        
        try:
            from sam2.build_sam import build_sam2
            from sam2.sam2_image_predictor import SAM2ImagePredictor
            from utils.utils import determine_model_cfg
            
            model_path = self.main_window.model_path
            device = self.main_window.device_combo.currentData()
            
            self.main_window.log_message("正在加载预览模型...", "info")
            
            # 构建模型
            model_cfg = determine_model_cfg(model_path)
            sam2_model = build_sam2(model_cfg, model_path, device=device)
            self.predictor = SAM2ImagePredictor(sam2_model)
            
            self.main_window.log_message("✓ 预览模型初始化成功", "success")
            return True
        
        except Exception as e:
            self.main_window.log_message(f"✗ 预览模型初始化失败: {e}", "error")
            import traceback
            traceback.print_exc()
            return False
    
    def set_current_frame(self, frame_idx, frame_bgr):
        """
        设置当前帧（缓存图像特征）
        
        Args:
            frame_idx (int): 帧索引
            frame_bgr (np.ndarray): BGR格式的帧图像
        
        Notes:
            - 只有帧索引变化时才更新缓存
            - 自动转换BGR到RGB
            - 如果predictor已初始化，会提取图像特征
        """
        if frame_idx != self.current_frame_idx:
            # 转换为RGB
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            self.current_frame_cache = frame_rgb
            self.current_frame_idx = frame_idx
            
            # 如果预测器已初始化，设置图像特征
            if self.predictor is not None:
                try:
                    self.predictor.set_image(frame_rgb)
                except Exception as e:
                    print(f"设置图像特征失败: {e}")
                    import traceback
                    traceback.print_exc()
    
    def generate_preview(self, obj_id, prompts):
        """
        生成mask预览（同步方式）
        
        Args:
            obj_id (int): 对象ID
            prompts (dict): 提示数据 {"box": [x1,y1,x2,y2], "points": [(x,y)...], "labels": [0/1...]}
        
        Returns:
            np.ndarray | None: 二值mask数组，失败返回None
        
        Notes:
            - 如果predictor未初始化，会自动初始化
            - 至少需要box或points中的一个
            - 同步调用，可能阻塞UI（推荐使用异步版本）
        """
        if not self.preview_enabled:
            return None
        
        # 懒加载初始化
        if self.predictor is None:
            if not self.initialize_predictor():
                return None
        
        # 确保当前帧已设置
        if self.current_frame_cache is None:
            return None
        
        try:
            # 提取提示
            box = prompts.get("box")
            points = prompts.get("points")
            labels = prompts.get("labels")
            
            # 调用SAM2预测
            masks, scores, logits = self.predictor.predict(
                point_coords=np.array(points) if points else None,
                point_labels=np.array(labels) if labels else None,
                box=np.array(box) if box else None,
                multimask_output=False
            )
            
            return masks[0] if len(masks) > 0 else None
        
        except Exception as e:
            print(f"预览生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_preview_async(self, obj_id, prompts, callback):
        """
        异步生成预览（推荐用于生产）
        
        Args:
            obj_id (int): 对象ID
            prompts (dict): 提示数据
            callback: 回调函数，签名为 callback(obj_id: int, mask: np.ndarray)
        
        Notes:
            - 使用单独线程，不阻塞UI
            - 会自动取消之前未完成的预测
            - 通过回调函数返回结果
        """
        if not self.preview_enabled or self.predictor is None:
            return
        
        # 取消之前的预测
        if self.preview_thread is not None and self.preview_thread.isRunning():
            self.preview_thread.terminate()
            self.preview_thread.wait()
        
        # 创建新线程
        prompts_with_id = {**prompts, "obj_id": obj_id}
        self.preview_thread = PreviewThread(
            self.predictor, 
            self.current_frame_cache, 
            prompts_with_id
        )
        self.preview_thread.preview_ready.connect(callback)
        self.preview_thread.start()
    
    def clear(self):
        """
        清除缓存和状态
        
        Notes:
            - 清除帧缓存
            - 终止运行中的预测线程
            - 不释放predictor（避免重复加载模型）
        """
        self.current_frame_cache = None
        self.current_frame_idx = -1
        if self.preview_thread is not None and self.preview_thread.isRunning():
            self.preview_thread.terminate()
            self.preview_thread.wait()
    
    def toggle_preview(self, enabled):
        """
        开关预览功能
        
        Args:
            enabled (bool): True启用，False禁用
        """
        self.preview_enabled = enabled
        self.main_window.log_message(
            f"实时预览: {'启用' if enabled else '禁用'}", 
            "info"
        )

