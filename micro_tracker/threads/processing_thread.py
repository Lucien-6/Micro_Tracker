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
    
    def __init__(self, args, bbox_list):
        super().__init__()
        self.args = args
        self.bbox_list = bbox_list
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
            
            # 导入必要的库
            from scripts.process_video import main as process_video_main, process_video_in_chunks
            
            # 保存 bbox_list 到临时文件，用于兼容原始脚本
            bbox_file = Path("temp_bbox_list.json")
            with open(bbox_file, "w") as f:
                json.dump(self.bbox_list, f)
            
            # 获取视频信息
            cap = cv2.VideoCapture(self.args.video_path)
            if not cap.isOpened():
                raise Exception(f"无法打开视频: {self.args.video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            
            # 设置进度条最大值
            self.progress_percent.emit(0)
            
            # 根据视频帧数决定使用哪个处理函数
            use_chunks = False
            if total_frames > 1000:  # 如果视频超过1000帧，使用分块处理
                use_chunks = True
                self.progress_update.emit(f"视频较长 ({total_frames} 帧, {duration:.1f} 秒)，将使用分块处理...")
            
            # 设置进度回调函数
            last_progress_time = time.time()
            last_frame_count = 0
            
            def progress_callback(current_frame, total):
                nonlocal last_progress_time, last_frame_count
                if not self.is_running:
                    return False  # 返回False表示终止处理
                
                # 计算进度百分比
                percent = int((current_frame / total) * 100)
                self.progress_percent.emit(percent)
                
                # 限制更新频率，避免大量日志
                current_time = time.time()
                if current_time - last_progress_time > 1.0 or current_frame == total - 1:
                    # 计算处理速度
                    time_diff = current_time - last_progress_time
                    if time_diff > 0:
                        frame_diff = current_frame - last_frame_count
                        fps_val = frame_diff / time_diff
                        
                        # 计算预计剩余时间
                        remaining_frames = total - current_frame
                        eta = remaining_frames / fps_val if fps_val > 0 else 0
                        eta_min = int(eta // 60)
                        eta_sec = int(eta % 60)
                        
                        # 更新进度信息
                        self.progress_update.emit(
                            f"处理中: {current_frame}/{total} 帧 ({percent}%) - "
                            f"速度: {fps_val:.1f} FPS, 预计剩余时间: {eta_min}分{eta_sec}秒"
                        )
                    
                    # 更新上次进度时间和帧数
                    last_progress_time = current_time
                    last_frame_count = current_frame
                
                return True  # 返回True表示继续处理
            
            # 修改原始Args对象，添加进度回调
            self.args.progress_callback = progress_callback
            self.progress_update.emit(f"正在加载模型到{self.args.device}设备...")
            self.progress_update.emit("处理开始，这可能需要几分钟时间...")
            
            # 执行处理
            if use_chunks:
                # 使用500帧为一块进行处理，而不是基于时间
                chunk_frames = 500
                self.progress_update.emit(f"将视频分为{(total_frames + chunk_frames - 1) // chunk_frames}个块进行处理，每块最多{chunk_frames}帧")
                process_video_in_chunks(self.args, self.bbox_list, chunk_frames=chunk_frames)
            else:
                process_video_main(self.args, self.bbox_list)
            
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