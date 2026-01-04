"""
Input Manager - 输入源管理器

统一管理视频文件和图像序列的输入源，提供统一接口。
支持格式转换（PNG/TIFF/BMP → JPEG）以兼容SAM2。

Author: Lucien (lucien-6@qq.com)
Date: 2025-01-04
"""

import os
import re
import cv2
import shutil
import tempfile
import numpy as np
from pathlib import Path
from abc import ABC, abstractmethod


class InputSource(ABC):
    """
    输入源抽象基类
    
    Attributes:
        source_type (str): 输入类型 "video" 或 "image_sequence"
        source_path (str): 原始输入路径
        working_path (str): 实际工作路径（可能是临时目录）
        total_frames (int): 总帧数
        frame_width (int): 帧宽度
        frame_height (int): 帧高度
        fps (float): 帧率
        needs_cleanup (bool): 是否需要清理临时文件
    """
    
    def __init__(self):
        self.source_type = ""
        self.source_path = ""
        self.working_path = ""
        self.total_frames = 0
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 10.0
        self.needs_cleanup = False
    
    @abstractmethod
    def get_frame(self, frame_idx: int) -> np.ndarray:
        """
        获取指定帧
        
        Args:
            frame_idx (int): 帧索引（从0开始）
        
        Returns:
            np.ndarray: BGR格式的帧图像，失败返回None
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理临时文件"""
        pass


class VideoInputSource(InputSource):
    """
    视频文件输入源
    
    从视频文件（.mp4, .avi, .mov, .mkv等）读取帧。
    """
    
    def __init__(self, video_path: str):
        """
        初始化视频输入源
        
        Args:
            video_path (str): 视频文件路径
        
        Raises:
            ValueError: 视频文件不存在或无法打开
        """
        super().__init__()
        
        if not os.path.exists(video_path):
            raise ValueError(f"视频文件不存在: {video_path}")
        
        self.source_type = "video"
        self.source_path = video_path
        self.working_path = video_path
        self.needs_cleanup = False
        
        # 获取视频信息
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        
        if self.fps <= 0:
            self.fps = 10.0
        
        cap.release()
    
    def get_frame(self, frame_idx: int) -> np.ndarray:
        """获取指定帧"""
        if frame_idx < 0 or frame_idx >= self.total_frames:
            return None
        
        cap = cv2.VideoCapture(self.source_path)
        if not cap.isOpened():
            return None
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        cap.release()
        
        return frame if ret else None
    
    def cleanup(self):
        """视频输入源无需清理"""
        pass


class ImageSequenceInputSource(InputSource):
    """
    图像序列输入源
    
    从图像文件夹读取帧序列。支持多种图像格式，
    自动转换非JPEG格式以兼容SAM2。
    """
    
    # 支持的图像格式
    SUPPORTED_FORMATS = [
        '.jpg', '.jpeg', '.JPG', '.JPEG',
        '.png', '.PNG',
        '.tif', '.tiff', '.TIF', '.TIFF',
        '.bmp', '.BMP'
    ]
    
    # SAM2兼容的JPEG格式
    SAM2_FORMATS = ['.jpg', '.jpeg', '.JPG', '.JPEG']
    
    def __init__(self, folder_path: str, fps: float = 10.0):
        """
        初始化图像序列输入源
        
        Args:
            folder_path (str): 图像文件夹路径
            fps (float): 播放帧率，默认10.0
        
        Raises:
            ValueError: 文件夹不存在或不包含有效图像
        """
        super().__init__()
        
        if not os.path.exists(folder_path):
            raise ValueError(f"文件夹不存在: {folder_path}")
        
        if not os.path.isdir(folder_path):
            raise ValueError(f"路径不是文件夹: {folder_path}")
        
        self.source_type = "image_sequence"
        self.source_path = folder_path
        self.fps = fps
        self.needs_cleanup = False
        self._temp_dir = None
        
        # 扫描图像文件
        self.image_files = self._scan_images(folder_path)
        
        if not self.image_files:
            raise ValueError(
                f"文件夹中未找到有效图像文件: {folder_path}\n"
                f"支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        self.total_frames = len(self.image_files)
        
        # 获取图像尺寸（从第一张图像）
        first_img = cv2.imread(self.image_files[0])
        if first_img is None:
            raise ValueError(f"无法读取图像: {self.image_files[0]}")
        
        self.frame_height, self.frame_width = first_img.shape[:2]
        
        # 检查是否需要转换
        if self._needs_conversion():
            self._create_converted_directory()
        else:
            self.working_path = folder_path
    
    def _scan_images(self, folder_path: str) -> list:
        """
        扫描并排序图像文件
        
        Args:
            folder_path (str): 文件夹路径
        
        Returns:
            list: 排序后的图像文件完整路径列表
        """
        image_files = []
        
        for filename in os.listdir(folder_path):
            ext = os.path.splitext(filename)[1]
            if ext in self.SUPPORTED_FORMATS:
                full_path = os.path.join(folder_path, filename)
                image_files.append(full_path)
        
        # 按帧编号排序
        image_files.sort(key=lambda p: self._extract_frame_number(os.path.basename(p)))
        
        return image_files
    
    def _extract_frame_number(self, filename: str) -> int:
        """
        从文件名提取帧编号
        
        支持多种命名格式：
        - 纯数字: 00001.jpg → 1
        - 前缀+数字: frame_00001.png → 1
        - 任意前缀: img_001.tif → 1
        
        Args:
            filename (str): 文件名（不含路径）
        
        Returns:
            int: 帧编号，无法提取时返回0
        """
        name = os.path.splitext(filename)[0]
        
        # 尝试纯数字
        if name.isdigit():
            return int(name)
        
        # 尝试提取末尾数字
        match = re.search(r'(\d+)$', name)
        if match:
            return int(match.group(1))
        
        # 尝试提取任意位置的数字
        match = re.search(r'(\d+)', name)
        if match:
            return int(match.group(1))
        
        return 0
    
    def _needs_conversion(self) -> bool:
        """
        检查是否需要格式转换
        
        Returns:
            bool: True表示需要转换
        """
        for img_path in self.image_files:
            ext = os.path.splitext(img_path)[1]
            filename = os.path.basename(img_path)
            name_without_ext = os.path.splitext(filename)[0]
            
            # 检查格式是否为JPEG
            if ext not in self.SAM2_FORMATS:
                return True
            
            # 检查文件名是否为纯数字（SAM2要求）
            if not name_without_ext.isdigit():
                return True
        
        return False
    
    def _create_converted_directory(self):
        """
        创建转换后的临时目录
        
        将所有图像转换为JPEG格式，命名为 00000.jpg, 00001.jpg, ...
        """
        # 创建临时目录
        self._temp_dir = tempfile.mkdtemp(prefix="micro_tracker_imgs_")
        self.working_path = self._temp_dir
        self.needs_cleanup = True
        
        # 转换每张图像
        for idx, src_path in enumerate(self.image_files):
            # 读取原图
            img = cv2.imread(src_path)
            if img is None:
                raise ValueError(f"无法读取图像: {src_path}")
            
            # 生成目标文件名（SAM2要求格式）
            dst_filename = f"{idx:05d}.jpg"
            dst_path = os.path.join(self._temp_dir, dst_filename)
            
            # 保存为JPEG（质量95，接近无损）
            cv2.imwrite(dst_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # 更新image_files为转换后的路径（用于get_frame仍从原图读取显示）
        # working_path用于SAM2处理
    
    def get_frame(self, frame_idx: int) -> np.ndarray:
        """
        获取指定帧
        
        注意：始终从原始图像文件读取，确保显示质量
        
        Args:
            frame_idx (int): 帧索引
        
        Returns:
            np.ndarray: BGR格式的帧图像
        """
        if frame_idx < 0 or frame_idx >= self.total_frames:
            return None
        
        # 从原始文件读取
        return cv2.imread(self.image_files[frame_idx])
    
    def cleanup(self):
        """清理临时目录"""
        if self.needs_cleanup and self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None
                self.needs_cleanup = False
            except Exception as e:
                print(f"清理临时目录失败: {e}")
    
    def __del__(self):
        """析构时尝试清理"""
        try:
            self.cleanup()
        except Exception:
            pass


def create_input_source(path: str, input_type: str = "auto", fps: float = 10.0) -> InputSource:
    """
    工厂函数：创建输入源
    
    Args:
        path (str): 文件或文件夹路径
        input_type (str): 输入类型 "video", "image_sequence", 或 "auto"（自动检测）
        fps (float): 图像序列的帧率
    
    Returns:
        InputSource: 输入源实例
    
    Raises:
        ValueError: 无法识别输入类型或路径无效
    """
    if input_type == "auto":
        if os.path.isdir(path):
            input_type = "image_sequence"
        elif os.path.isfile(path):
            input_type = "video"
        else:
            raise ValueError(f"无效的路径: {path}")
    
    if input_type == "video":
        return VideoInputSource(path)
    elif input_type == "image_sequence":
        return ImageSequenceInputSource(path, fps=fps)
    else:
        raise ValueError(f"未知的输入类型: {input_type}")
