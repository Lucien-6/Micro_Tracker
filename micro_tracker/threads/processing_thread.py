import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
import time
import os
import json
from pathlib import Path
import traceback

class ProcessingThread(QThread):
    """视频处理线程"""
    progress_update = pyqtSignal(str)  # 进度更新信号
    progress_percent = pyqtSignal(int)  # 进度百分比信号
    processing_finished = pyqtSignal(bool, str)  # 处理完成信号，参数为(成功与否, 消息)
    frame_processed = pyqtSignal(np.ndarray, int, int)  # 帧处理信号，参数为(帧, 当前索引, 总帧数)
    
    def __init__(self, args, bbox_data):
        """
        Args:
            args: 处理参数对象
            bbox_data: 边界框数据，可以是字典（多帧）或列表（单帧兼容）
        """
        super().__init__()
        self.args = args
        self.bbox_list = bbox_data  # Phase 1 MVP: 支持字典和列表格式
        self.is_running = True
    
    def run(self):
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 发送初始化中的消息
            self.progress_update.emit("正在初始化SAM2模型...")
            
            # 获取系统信息
            import platform
            system_info = platform.platform()
            python_version = platform.python_version()
            self.progress_update.emit(f"系统信息: {system_info}")
            self.progress_update.emit(f"Python版本: {python_version}")
            
            # 检查设备
            if self.args.device.startswith("cuda"):
                import torch
                if torch.cuda.is_available():
                    device_id = 0
                    if ":" in self.args.device:
                        device_id = int(self.args.device.split(":")[-1])
                    gpu_name = torch.cuda.get_device_name(device_id)
                    self.progress_update.emit(f"GPU: {gpu_name}")
                    self.progress_update.emit(f"CUDA版本: {torch.version.cuda}")
                else:
                    self.progress_update.emit("警告: CUDA不可用，已回退到CPU")
                    self.args.device = "cpu"
            
            # === Phase 2: 统一使用多帧处理模式 ===
            # 确保数据格式统一为字典
            if isinstance(self.bbox_list, list):
                # 旧格式列表 → 转换为单帧字典
                self.bbox_list = {0: self.bbox_list}
                self.progress_update.emit("转换为标准多帧格式（单帧）")
            
            # 统计标注信息
            annotated_frames = len(self.bbox_list)
            total_annotations = sum(len(bboxes) for bboxes in self.bbox_list.values())
            
            self.progress_update.emit(f"📊 标注统计: {annotated_frames}帧, {total_annotations}个对象")
            
            # 导入多帧处理脚本（统一处理路径）
            from scripts.process_video_multiframe import process_video_multiframe
            
            # 获取视频信息
            cap = cv2.VideoCapture(self.args.video_path)
            if not cap.isOpened():
                raise Exception(f"无法打开视频: {self.args.video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            
            self.progress_update.emit(f"视频信息: {total_frames}帧, {fps:.1f}fps, {duration:.1f}秒")
            
            # 设置进度条最大值
            self.progress_percent.emit(0)
            
            # === Phase 2: 统一的进度回调（接受消息字符串）===
            def multiframe_progress_callback(message):
                """统一的多帧处理进度回调"""
                if not self.is_running:
                    return False
                self.progress_update.emit(message)
                return True
            
            # 设置进度回调
            self.args.progress_callback = multiframe_progress_callback
            
            # === 统一使用多帧SAM2提示处理 ===
            self.progress_update.emit("🚀 开始SAM2多帧提示处理...")
            process_video_multiframe(self.args, self.bbox_list)
            
            # 处理完成
            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            
            self.progress_update.emit(f"处理完成，总耗时: {minutes}分{seconds}秒")
            self.progress_update.emit(f"处理速度: {total_frames / elapsed_time:.1f} FPS")
            
            # 尝试加载处理后的视频进行预览
            try:
                if self.args.save_to_video:
                    self.progress_update.emit("正在加载预览...")
                    preview_cap = cv2.VideoCapture(self.args.video_output_path)
                    frame_count = int(preview_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
                    for i in range(frame_count):
                        ret, frame = preview_cap.read()
                        if ret:
                            self.frame_processed.emit(frame, i, frame_count)
                            # 放慢预览速度
                            self.msleep(30)
                        else:
                            break
                    
                    preview_cap.release()
            except Exception as e:
                self.progress_update.emit(f"加载处理后的视频预览时出错: {str(e)}")
            
            # 处理成功
            self.processing_finished.emit(True, "视频处理成功")
            
        except Exception as e:
            error_message = str(e)
            stack_trace = traceback.format_exc()
            
            self.progress_update.emit(f"错误: {error_message}")
            self.progress_update.emit(f"堆栈跟踪:\n{stack_trace}")
            self.processing_finished.emit(False, error_message)
        finally:
            # 清理临时文件
            if 'bbox_file' in locals() and bbox_file.exists():
                bbox_file.unlink()
    
    def stop(self):
        """停止处理线程"""
        self.is_running = False 