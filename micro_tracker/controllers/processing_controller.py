import os
from pathlib import Path

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QMutex

class ProcessingController:
    """处理控制器，负责管理视频处理相关功能"""
    
    def __init__(self, main_window):
        """
        初始化处理控制器
        
        Args:
            main_window: 主窗口引用
        """
        self.main_window = main_window
    
    def start_processing(self):
        """启动视频处理"""
        # 获取边界框列表
        bbox_list = self.main_window.video_label.get_bbox_list()
        if not bbox_list:
            self.main_window.log_message("错误: 未标注任何边界框！", "error")
            QMessageBox.warning(self.main_window, "警告", "请至少绘制一个边界框！")
            return
        
        # 准备处理参数
        class Args:
            pass
        
        args = Args()
        args.video_path = self.main_window.video_path
        args.model_path = self.main_window.model_path
        args.video_output_path = self.main_window.output_path_edit.text() if os.path.isabs(self.main_window.output_path_edit.text()) else self.main_window.output_path
        args.save_to_video = self.main_window.save_video_check.isChecked()
        
        # 根据保存掩码选项决定是否使用掩码保存目录
        if self.main_window.save_mask_check.isChecked():
            # 确保掩码目录存在
            mask_dir = Path(self.main_window.mask_dir)
            if not mask_dir.exists():
                os.makedirs(self.main_window.mask_dir, exist_ok=True)
                self.main_window.log_message(f"创建掩码保存目录: {self.main_window.mask_dir}", "info")
            args.mask_dir = self.main_window.mask_dir
        else:
            args.mask_dir = None
            
        args.device = self.main_window.device_combo.currentData()
        
        # 显示进度条
        self.main_window.progress_bar.setVisible(True)
        
        # 清空日志
        self.main_window.log_text.clear()
        self.main_window.log_message("====== 开始处理视频 ======", "highlight")
        self.main_window.log_message("参数设置:", "highlight")
        self.main_window.log_message(f"输入视频: {args.video_path}", "info")
        self.main_window.log_message(f"使用模型: {args.model_path}", "info")
        self.main_window.log_message(f"输出路径: {args.video_output_path}", "info")
        self.main_window.log_message(f"处理设备: {args.device}", "info")
        if args.mask_dir:
            self.main_window.log_message(f"掩码保存目录: {args.mask_dir}", "info")
            self.main_window.log_message("掩码格式: 每帧一张8位灰度图像，像素值表示对象ID+1，背景为0", "info")
        else:
            self.main_window.log_message("不保存掩码", "warning")
        self.main_window.log_message(f"保存处理视频: {'是' if args.save_to_video else '否'}", "info")
        
        self.main_window.log_message("标注信息:", "highlight")
        self.main_window.log_message(f"边界框数量: {len(bbox_list)}", "info")
        for i, bbox in enumerate(bbox_list):
            self.main_window.log_message(f"边界框 {i}: ({int(bbox[0])},{int(bbox[1])},{int(bbox[2])},{int(bbox[3])})", "info")
        
        self.main_window.log_message("-" * 50, "info")
        self.main_window.log_message("正在准备处理环境...", "info")
        
        # 创建处理线程
        self.main_window.processing_thread = self.main_window.ProcessingThread(args, bbox_list)
        self.main_window.processing_thread.progress_update.connect(self.main_window.update_progress)
        self.main_window.processing_thread.progress_percent.connect(self.main_window.update_progress_bar)
        self.main_window.processing_thread.processing_finished.connect(self.main_window.processing_done)
        self.main_window.processing_thread.frame_processed.connect(self.main_window.update_result_frame)
        
        # 重置并显示进度条
        self.main_window.progress_bar.setValue(0)
        self.main_window.progress_bar.setVisible(True)
        
        # 禁用开始按钮
        self.main_window.setup_tab.start_btn.setEnabled(False)
        
        # 开始处理
        self.main_window.processing_thread.start()
    
    def load_result_video(self):
        """加载处理后的视频用于预览"""
        output_path = self.main_window.output_path_edit.text()
        if not os.path.exists(output_path):
            self.main_window.log_message(f"警告: 无法找到输出视频文件 {output_path}", "warning")
            return
            
        self.main_window.log_message(f"正在加载处理结果视频: {output_path}", "info")
        
        # 停止之前的结果视频线程
        if self.main_window.result_video_thread and self.main_window.result_video_thread.isRunning():
            self.main_window.result_video_thread.stop()
        
        # 创建新的视频线程用于结果预览
        self.main_window.result_video_thread = self.main_window.VideoThread(output_path)
        self.main_window.result_video_thread.frame_ready.connect(self.main_window.update_result_video_frame)
        self.main_window.result_video_thread.frame_index_changed.connect(self.main_window.update_result_frame_slider)
        
        # 启动视频线程 - 保持暂停状态
        self.main_window.result_video_thread.start()
        
        # 获取视频信息
        try:
            import cv2
            cap = cv2.VideoCapture(output_path)
            if cap.isOpened():
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                self.main_window.log_message(f"结果视频信息: {width}x{height}, {fps:.1f} FPS, {total_frames} 帧", "info")
        except Exception as e:
            self.main_window.log_message(f"获取结果视频信息时出错: {str(e)}", "warning")
        
        # 更新播放按钮状态
        self.main_window.result_play_pause_btn.setText("播放")
        self.main_window.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.main_window.result_play_pause_btn.setEnabled(True) 