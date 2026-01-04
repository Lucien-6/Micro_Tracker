import sys
import os
import cv2
import numpy as np
import torch
import warnings
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                            QFileDialog, QMessageBox, QApplication, QTabWidget)
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import Qt, QDateTime, QMutex

from micro_tracker.config.style import COMPLETE_STYLE
from micro_tracker.ui.setup_tab import SetupTab
from micro_tracker.ui.result_preview_tab import ResultPreviewTab
from micro_tracker.ui.filter_tab import FilterTab
from micro_tracker.ui.guide_tab import GuideTab
from micro_tracker.threads.video_processing_threads import VideoThread, ProcessingThread, FilterMaskThread, FilterVideoThread
from micro_tracker.controllers.processing_controller import ProcessingController
from micro_tracker.controllers.filter_controller import FilterController

class MainWindow(QMainWindow):
    """主窗口类，集成所有UI组件和功能"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Micro Tracker | 显微视频目标分割和追踪工具")
        self.setMinimumSize(1200, 900)  # 调整最小窗口大小
        self.setStyleSheet(COMPLETE_STYLE)  # 应用预组合的完整样式，避免运行时叠加导致的解析问题
        
        # 添加应用图标
        app_icon = QIcon("icons/icon.png") if os.path.exists("icons/icon.png") else QIcon.fromTheme("video-x-generic")
        self.setWindowIcon(app_icon)
        
        # 初始化共享变量
        self.video_path = ""
        self.model_path = "models/sam2/checkpoints/sam2.1_hiera_tiny.pt"  # 设置默认模型路径
        self.output_path = ""
        self.mask_dir = ""
        self.save_mask_enabled = True  # 默认启用掩码保存
        
        # === 输入源管理 ===
        self.input_type = "video"       # "video" 或 "image_sequence"
        self.input_source = None        # InputSource 实例
        self.image_sequence_fps = 10.0  # 图像序列默认帧率
        
        # === Phase 1 MVP: 多帧模式状态 ===
        self.multi_frame_mode = True  # 启用多帧模式
        self.current_frame_index = 0  # 当前帧索引
        
        # 线程类引用
        self.VideoThread = VideoThread
        self.ProcessingThread = ProcessingThread
        self.FilterMaskThread = FilterMaskThread
        self.FilterVideoThread = FilterVideoThread
        
        # 线程对象
        self.video_thread = None
        self.processing_thread = None
        self.result_video_thread = None
        
        # 记录当前聚焦的视频标签，用于键盘控制
        self.focused_video = None
        
        # 初始化控制器
        self.processing_controller = ProcessingController(self)
        self.filter_controller = FilterController(self)
        
        # === 实时预览管理器（懒加载）===
        self.preview_manager = None
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化主窗口界面"""
        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        # 创建标签页
        self.setup_tab = SetupTab(self)
        self.result_tab = ResultPreviewTab(self)
        self.filter_tab = FilterTab(self)
        self.guide_tab = GuideTab(self)
        
        # 添加标签页
        self.tab_widget.addTab(self.setup_tab, "参数设置与标注")
        self.tab_widget.addTab(self.result_tab, "结果预览")
        self.tab_widget.addTab(self.filter_tab, "筛选过滤")
        self.tab_widget.addTab(self.guide_tab, "使用指南")
    
    def get_preview_manager(self):
        """
        懒加载获取预览管理器
        
        Returns:
            MaskPreviewManager: 预览管理器实例
        """
        if self.preview_manager is None:
            from micro_tracker.utils.preview_manager import MaskPreviewManager
            self.preview_manager = MaskPreviewManager(self)
        return self.preview_manager
    
    # ==== 文件操作方法 ====
    
    def browse_input(self):
        """浏览选择输入源（视频文件或图像序列文件夹）"""
        if self.input_type == "video":
            self._browse_video_input()
        else:
            self._browse_image_sequence_input()
    
    def browse_video(self):
        """兼容旧接口，调用browse_input"""
        self.browse_input()
    
    def _browse_video_input(self):
        """浏览选择视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*)"
        )
        if file_path:
            self.video_path = file_path
            self.input_source = None  # 视频模式不使用InputSource
            self.video_path_edit.setText(os.path.basename(file_path))
            self.video_path_edit.setToolTip(file_path)
            
            # 获取原视频所在目录和文件名（不含扩展名）
            video_dir = os.path.dirname(file_path)
            video_filename = os.path.basename(file_path)
            video_name_without_ext = os.path.splitext(video_filename)[0]
            
            # 设置输出视频路径为原视频同级目录下的processed_{原视频文件名}
            self.output_path = os.path.join(video_dir, f"processed_{video_filename}")
            self.output_path_edit.setText(self.output_path)
            self.output_path_edit.setToolTip(self.output_path)
            
            # 设置掩码保存目录为原视频同级目录下的masks_{原视频文件名}文件夹
            self.mask_dir = os.path.join(video_dir, f"masks_{video_name_without_ext}")
            self.mask_dir_edit.setText(self.mask_dir)
            self.mask_dir_edit.setToolTip(self.mask_dir)
            
            # 将文件选择记录到日志
            self.log_message(f"选择视频文件: {file_path}", "info")
            self.log_message(f"输出视频将保存到: {self.output_path}", "info")
            self.log_message(f"掩码图片将保存到: {self.mask_dir}", "info")
            
            # 加载视频第一帧
            self.load_input_source()
            
            # 检查是否可以启用开始按钮
            self.check_start_enabled()
    
    def _browse_image_sequence_input(self):
        """浏览选择图像序列文件夹"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择图像序列文件夹", ""
        )
        if folder_path:
            try:
                from micro_tracker.utils.input_manager import ImageSequenceInputSource
                
                # 使用默认帧率10fps
                fps = getattr(self, 'image_seq_fps', 10.0)
                self.image_sequence_fps = fps
                
                # 创建输入源（会自动验证和转换）
                input_source = ImageSequenceInputSource(folder_path, fps=fps)
                
                self.video_path = input_source.working_path  # SAM2使用的路径
                self.input_source = input_source
                
                # 更新UI
                folder_name = os.path.basename(folder_path)
                self.video_path_edit.setText(f"{folder_name}/ ({input_source.total_frames}张图像)")
                self.video_path_edit.setToolTip(folder_path)
                
                # 设置输出路径
                self.output_path = os.path.join(folder_path, f"processed_{folder_name}.mp4")
                self.output_path_edit.setText(self.output_path)
                self.output_path_edit.setToolTip(self.output_path)
                
                # 设置掩码目录
                self.mask_dir = os.path.join(folder_path, f"masks_{folder_name}")
                self.mask_dir_edit.setText(self.mask_dir)
                self.mask_dir_edit.setToolTip(self.mask_dir)
                
                # 日志
                self.log_message(f"选择图像序列: {folder_path}", "info")
                self.log_message(f"  共 {input_source.total_frames} 张图像", "info")
                self.log_message(f"  分辨率: {input_source.frame_width}x{input_source.frame_height}", "info")
                self.log_message(f"  帧率: {fps} FPS", "info")
                self.log_message(f"输出视频将保存到: {self.output_path}", "info")
                self.log_message(f"掩码图片将保存到: {self.mask_dir}", "info")
                
                if input_source.needs_cleanup:
                    self.log_message(f"  ⚠️ 检测到非JPEG格式，已创建临时转换目录", "warning")
                
                # 加载预览
                self.load_input_source()
                self.check_start_enabled()
                
            except ValueError as e:
                self.log_message(f"错误: {str(e)}", "error")
                QMessageBox.warning(self, "图像序列加载失败", str(e))
    
    def browse_model(self):
        """浏览选择自定义模型文件"""
        # 从当前选择的模型路径获取目录
        current_dir = os.path.dirname(self.model_path) if self.model_path else "models/sam2/checkpoints"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择SAM2模型文件", current_dir, "模型文件 (*.pt *.pth);;所有文件 (*)"
        )
        if file_path:
            self.model_path = file_path
            
            # 检查是否在下拉列表中
            combo = self.model_combo
            found = False
            for i in range(combo.count()):
                if combo.itemData(i) == file_path:
                    combo.setCurrentIndex(i)
                    found = True
                    break
            
            # 如果不在列表中，添加为自定义选项
            if not found:
                display_name = f"📁 自定义: {os.path.basename(file_path)}"
                combo.addItem(display_name, file_path)
                combo.setCurrentIndex(combo.count() - 1)
            
            self.log_message(f"选择模型文件: {os.path.basename(file_path)}", "info")
            self.check_start_enabled()
    
    def browse_output(self):
        """设置输出视频文件路径"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "设置输出视频文件", self.output_path_edit.text(), "视频文件 (*.mp4 *.avi);;所有文件 (*)"
        )
        if file_path:
            self.output_path = file_path
            self.output_path_edit.setText(file_path)  # 显示完整路径
            self.output_path_edit.setToolTip(file_path)
            self.log_message(f"设置输出视频: {file_path}", "info")
    
    def browse_mask_dir(self):
        """设置掩码保存目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择掩码保存目录", ""
        )
        if dir_path:
            self.mask_dir = dir_path
            self.mask_dir_edit.setText(dir_path)  # 显示完整路径
            self.mask_dir_edit.setToolTip(dir_path)
            self.log_message(f"设置掩码保存目录: {dir_path}", "info")
    
    def browse_filter_mask_dir(self):
        """浏览掩膜图片文件夹"""
        # 先尝试使用已有的掩膜目录
        initial_dir = ""
        if hasattr(self, 'mask_dir') and self.mask_dir and os.path.exists(self.mask_dir):
            initial_dir = self.mask_dir
        
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择掩膜图片文件夹", initial_dir
        )
        
        if dir_path:
            self.filter_mask_dir_edit.setText(dir_path)
            self.filter_mask_dir_edit.setToolTip(dir_path)
            
            # 检查是否含有掩膜图片
            mask_files = [f for f in os.listdir(dir_path) if f.endswith('.png') and f.startswith('frame_')]
            
            if mask_files:
                self.log_message(f"找到 {len(mask_files)} 个掩膜图片", "info")
                self.apply_filter_btn.setEnabled(True)
            else:
                self.log_message(f"警告: 在所选文件夹中未找到掩膜图片", "warning")
                self.apply_filter_btn.setEnabled(False)
    
    def open_output_folder(self):
        """打开输出文件夹"""
        output_path = self.output_path
        if not output_path:
            return
        
        output_dir = os.path.dirname(os.path.abspath(output_path))
        if os.path.exists(output_dir):
            # 打开输出目录
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', output_dir])
            else:  # Linux
                subprocess.run(['xdg-open', output_dir])
    
    # ==== 视频处理方法 ====
    
    def load_input_source(self):
        """加载输入源（视频或图像序列）并显示第一帧"""
        if self.input_type == "image_sequence" and self.input_source:
            self._load_image_sequence()
        else:
            self._load_video()
    
    def load_video(self):
        """兼容旧接口，调用load_input_source"""
        self.load_input_source()
    
    def _load_video(self):
        """加载视频并显示第一帧"""
        if not self.video_path or not os.path.exists(self.video_path):
            return
        
        # 清空日志
        self.log_text.clear()
        self.log_message(f"加载视频: {self.video_path}", "highlight")
        
        # 停止之前的视频线程
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
        
        # 获取视频信息
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.log_message(f"错误: 无法打开视频文件 {self.video_path}", "error")
            return
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()
        
        self.log_message(f"视频分辨率: {width}x{height}", "info")
        self.log_message(f"帧率: {fps:.2f} FPS", "info")
        self.log_message(f"总帧数: {total_frames}", "info")
        self.log_message(f"时长: {duration:.2f} 秒", "info")
        
        # 设置滑块范围
        self.frame_slider.setRange(0, total_frames - 1)
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(True)
        self.frame_info_label.setText(f"当前帧: 0 / {total_frames-1}")
        
        # 启用播放/暂停按钮
        self.play_pause_btn.setEnabled(True)
        self.play_pause_btn.setText("播放")
        self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        
        # 清除之前的边界框
        count = self.video_label.clear_bboxes()
        if count > 0:
            self.log_message(f"清除了 {count} 个已有边界框", "warning")
        
        # 创建新的视频线程
        self.video_thread = VideoThread(self.video_path)
        self.video_thread.frame_ready.connect(self.update_video_frame)
        self.video_thread.frame_index_changed.connect(self.update_frame_slider)
        
        # 启动视频线程 - 线程默认已设置为暂停状态
        self.video_thread.start()
        self.log_message("视频加载完成，请在第一帧上标注目标边界框", "success")
        
        # === 自动初始化实时预览功能 ===
        self._init_preview_manager()
    
    def _load_image_sequence(self):
        """加载图像序列并显示第一帧"""
        from micro_tracker.threads.video_thread import ImageSequenceThread
        
        # 清空日志
        self.log_text.clear()
        self.log_message(f"加载图像序列: {self.input_source.source_path}", "highlight")
        
        # 停止之前的线程
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
        
        # 获取信息
        total_frames = self.input_source.total_frames
        fps = self.input_source.fps
        width = self.input_source.frame_width
        height = self.input_source.frame_height
        duration = total_frames / fps if fps > 0 else 0
        
        self.log_message(f"图像分辨率: {width}x{height}", "info")
        self.log_message(f"设定帧率: {fps:.2f} FPS", "info")
        self.log_message(f"总帧数: {total_frames}", "info")
        self.log_message(f"预计时长: {duration:.2f} 秒", "info")
        
        # 设置滑块
        self.frame_slider.setRange(0, total_frames - 1)
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(True)
        self.frame_info_label.setText(f"当前帧: 0 / {total_frames-1}")
        
        # 启用播放按钮
        self.play_pause_btn.setEnabled(True)
        self.play_pause_btn.setText("播放")
        self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        
        # 清除边界框
        count = self.video_label.clear_bboxes()
        if count > 0:
            self.log_message(f"清除了 {count} 个已有边界框", "warning")
        
        # 创建图像序列线程
        self.video_thread = ImageSequenceThread(
            self.input_source.image_files,
            fps=self.input_source.fps
        )
        self.video_thread.frame_ready.connect(self.update_video_frame)
        self.video_thread.frame_index_changed.connect(self.update_frame_slider)
        self.video_thread.start()
        
        self.log_message("图像序列加载完成，请在第一帧上标注目标边界框", "success")
        
        # === 自动初始化实时预览功能 ===
        self._init_preview_manager()
    
    def _init_preview_manager(self):
        """初始化实时预览管理器"""
        self.log_message("正在初始化实时预览功能...", "info")
        try:
            preview_mgr = self.get_preview_manager()
            success = preview_mgr.initialize_predictor()
            
            if success:
                self.log_message("✓ 实时预览已启用（添加标注后自动显示mask）", "success")
            else:
                self.log_message("⚠️ 实时预览初始化失败，将仅显示边界框标注", "warning")
        except Exception as e:
            self.log_message(f"⚠️ 实时预览初始化异常: {e}，将仅显示边界框标注", "warning")
    
    # 委托给ProcessingController的方法
    def start_processing(self):
        """启动视频处理"""
        self.processing_controller.start_processing()
    
    def update_progress(self, message):
        """更新处理进度"""
        # 根据消息内容确定类型
        msg_type = "info"
        if "错误" in message or "出错" in message:
            msg_type = "error"
        elif "警告" in message:
            msg_type = "warning"
        elif "完成" in message or "成功" in message:
            msg_type = "success"
        elif "初始化" in message or "开始" in message:
            msg_type = "highlight"
            
        self.log_message(message, msg_type)
    
    def update_progress_bar(self, percent):
        """更新进度条百分比"""
        self.progress_bar.setValue(percent)
    
    def processing_done(self, success, message):
        """处理完成后的回调"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 更新日志
        if success:
            self.log_message("====== 处理完成 ======", "highlight")
            self.log_message(f"处理成功！输出文件: {self.output_path_edit.text()}", "success")
            # 显示成功提示
            QMessageBox.information(self, "处理完成", f"视频处理成功！\n输出文件: {self.output_path_edit.text()}")
            # 自动切换到结果预览标签页
            self.tab_widget.setCurrentIndex(1)  # 第二个标签页是结果预览
            
            # 启用结果预览的播放/暂停按钮
            self.result_play_pause_btn.setEnabled(True)
            
            # 初始化结果视频线程
            self.processing_controller.load_result_video()
            
            # 如果掩膜目录存在，自动设置到筛选过滤标签页
            if self.mask_dir and os.path.exists(self.mask_dir):
                self.filter_mask_dir_edit.setText(self.mask_dir)
                self.filter_mask_dir_edit.setToolTip(self.mask_dir)
                
                # 检查掩膜目录中是否有图片
                mask_files = [f for f in os.listdir(self.mask_dir) if f.endswith('.png') and f.startswith('frame_')]
                if mask_files:
                    self.apply_filter_btn.setEnabled(True)
                    self.log_message(f"已自动加载掩膜目录: {self.mask_dir}", "info")
        else:
            self.log_message("====== 处理失败 ======", "highlight")
            self.log_message(f"处理失败: {message}", "error")
            # 显示错误提示
            QMessageBox.critical(self, "处理失败", f"视频处理失败！\n错误信息: {message}")
        
        # 重新启用开始按钮
        self.setup_tab.start_btn.setEnabled(True)
    
    # 委托给FilterController的方法
    def apply_mask_filter(self):
        """应用筛选"""
        self.filter_controller.apply_mask_filter()
    
    def save_filter_results(self):
        """保存筛选结果"""
        self.filter_controller.save_filter_results()
    
    def check_start_enabled(self):
        """检查是否可以启用开始按钮"""
        # 启用开始按钮的条件
        video_ok = bool(self.video_path and os.path.exists(self.video_path))
        model_ok = bool(self.model_path and os.path.exists(self.model_path))
        
        # 如果模型路径设置为默认值但文件不存在，检查是否创建了该目录结构
        if not model_ok and self.model_path == "models/sam2/checkpoints/sam2.1_hiera_tiny.pt":
            # 仅在用户有明确加载视频的意图时启用按钮
            model_ok = bool(self.video_path and os.path.exists(self.video_path))
        
        self.setup_tab.start_btn.setEnabled(video_ok and model_ok)
        
        # 如果条件满足，更改按钮样式为突出显示
        if video_ok and model_ok:
            self.setup_tab.start_btn.setStyleSheet("""
                font-weight: bold; 
                font-size: 14px; 
                padding: 12px;
                background-color: #4CAF50;
                border-radius: 6px;
            """)
        else:
            self.setup_tab.start_btn.setStyleSheet("""
                font-weight: bold; 
                font-size: 14px; 
                padding: 12px;
                background-color: #cccccc;
                color: #888888;
                border-radius: 6px;
            """)
    
    def update_video_frame(self, frame):
        """更新视频帧显示"""
        if frame is not None:
            self.video_label.set_frame(frame)
    
    def update_frame_slider(self, frame_index):
        """更新当前帧滑块位置，但不触发新的帧加载"""
        # 暂时断开滑块的valueChanged信号连接，避免循环触发
        self.frame_slider.blockSignals(True)
        self.frame_slider.setValue(frame_index)
        self.frame_slider.blockSignals(False)
        
        # === Bug Fix: 更新overlay层的帧索引（静默模式，不弹窗）===
        # 解决问题：视频播放时预览mask停留在视频上
        if hasattr(self, 'video_label') and self.video_label:
            self.video_label.overlay_layer.set_current_frame_silent(frame_index)
            self.current_frame_index = frame_index
        
        # 更新帧信息标签，将帧索引加1使其从1开始显示
        total_frames = self.video_thread.total_frames if self.video_thread else 0
        
        # === Phase 1 MVP: 显示标注状态（简化版：仅通过颜色指示）===
        if hasattr(self, 'video_label') and self.video_label:
            annotation_count = self.video_label.get_current_frame_annotation_count()
            self.frame_info_label.setText(f"当前帧: {frame_index} / {total_frames-1}")
            if annotation_count > 0:
                # 有标注时显示绿色
                self.frame_info_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
            else:
                # 无标注时显示默认颜色
                self.frame_info_label.setStyleSheet("font-weight: bold; color: #455a64;")
        else:
            self.frame_info_label.setText(f"当前帧: {frame_index} / {total_frames-1}")
            self.frame_info_label.setStyleSheet("font-weight: bold; color: #455a64;")
    
    def set_frame_index(self, index):
        """设置视频当前帧索引"""
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.set_frame_index(index)
            
            # === Phase 1 MVP: 更新边界框显示 ===
            self.current_frame_index = index
            if hasattr(self, 'video_label') and self.video_label:
                self.video_label.set_current_frame_index(index)
                self._update_annotation_status_display()
                
                # === 清除预览（切换帧时）===
                self.video_label.overlay_layer.clear_preview_masks()
                
                # === 自动恢复预览（如果新帧有标注）===
                self._restore_preview_for_current_frame()
    
    def toggle_play_pause(self):
        """切换视频播放/暂停状态"""
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.toggle_pause()
            
            # 获取当前状态以更新按钮
            mutex = QMutex()
            mutex.lock()
            is_paused = self.video_thread.paused
            mutex.unlock()
            
            # 更新按钮文本
            if is_paused:
                self.play_pause_btn.setText("播放")
                self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
                self.log_message("视频预览已暂停", "info")
            else:
                self.play_pause_btn.setText("暂停")
                self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
                self.log_message("视频预览开始播放", "info")
    
    def update_result_frame(self, frame, current_idx, total_frames):
        """更新结果预览帧"""
        if frame is None:
            return
        
        # 更新结果预览标签
        self.result_label.setVideoFrame(frame)
        
        # 更新结果预览滑块
        if self.result_slider.maximum() != total_frames - 1:
            self.result_slider.setRange(0, total_frames - 1)
        self.result_slider.setValue(current_idx)
        self.result_slider.setEnabled(True)
        
        # 更新结果信息标签
        self.result_info_label.setText(f"处理结果: {current_idx} / {total_frames-1}")
        
        # 定期更新日志（避免大量更新），每50帧或达到100%时更新一次
        if current_idx % 50 == 0 or current_idx == total_frames - 1:
            percent = int((current_idx + 1) / total_frames * 100)
            self.log_message(f"已处理: {current_idx+1}/{total_frames} 帧 ({percent}%)", "info")
    
    def update_result_frame_slider(self, frame_index):
        """更新结果预览帧滑块位置，但不触发新的帧加载"""
        # 暂时断开滑块的valueChanged信号连接，避免循环触发
        self.result_slider.blockSignals(True)
        self.result_slider.setValue(frame_index)
        self.result_slider.blockSignals(False)
        
        # 更新帧信息标签
        total_frames = self.result_video_thread.total_frames if self.result_video_thread else 0
        self.result_info_label.setText(f"处理结果: {frame_index} / {total_frames-1}")
    
    def update_result_video_frame(self, frame):
        """更新结果预览的视频帧"""
        if frame is not None:
            self.result_label.setVideoFrame(frame)
    
    def set_result_frame_index(self, index):
        """设置结果预览的帧索引"""
        if self.result_video_thread and self.result_video_thread.isRunning():
            self.result_video_thread.set_frame_index(index)
    
    def toggle_result_play_pause(self):
        """切换结果预览的播放/暂停状态"""
        if self.result_video_thread and self.result_video_thread.isRunning():
            self.result_video_thread.toggle_pause()
            
            # 获取当前状态以更新按钮
            mutex = QMutex()
            mutex.lock()
            is_paused = self.result_video_thread.paused
            mutex.unlock()
            
            # 更新按钮文本
            if is_paused:
                self.result_play_pause_btn.setText("播放")
                self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            else:
                self.result_play_pause_btn.setText("暂停")
                self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
    
    def set_filter_frame_index(self, index):
        """设置筛选预览的帧索引"""
        if hasattr(self, 'filter_video_thread') and self.filter_video_thread.isRunning():
            self.filter_video_thread.set_frame_index(index)
    
    def toggle_filter_play_pause(self):
        """切换筛选预览的播放/暂停状态"""
        if hasattr(self, 'filter_video_thread') and self.filter_video_thread.isRunning():
            self.filter_video_thread.toggle_pause()
            
            # 获取当前状态以更新按钮
            mutex = QMutex()
            mutex.lock()
            is_paused = self.filter_video_thread.paused
            mutex.unlock()
            
            # 更新按钮文本
            if is_paused:
                self.filter_play_pause_btn.setText("播放")
                self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            else:
                self.filter_play_pause_btn.setText("暂停")
                self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
    
    def keyPressEvent(self, event):
        """处理键盘按键事件"""
        # 根据当前激活的标签页来判断要控制哪个视频
        current_tab = self.tab_widget.currentIndex()
        
        # 第一个标签页（参数设置与标注）- 控制原始视频
        if current_tab == 0 and self.video_thread and self.video_thread.isRunning():
            # 空格键 - 播放/暂停
            if event.key() == Qt.Key_Space:
                self.toggle_play_pause()
                event.accept()
                return
            # F键 - 下一帧
            elif event.key() == Qt.Key_F:
                self.next_frame(self.video_thread, self.frame_slider)
                event.accept()
                return
            # D键 - 上一帧
            elif event.key() == Qt.Key_D:
                self.previous_frame(self.video_thread, self.frame_slider)
                event.accept()
                return
            # Ctrl+Q键 - 切换提示类型
            elif event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
                if hasattr(self, 'setup_tab') and self.setup_tab:
                    self.setup_tab.toggle_prompt_type()
                event.accept()
                return
        
        # 第二个标签页（结果预览）- 控制结果视频
        elif current_tab == 1 and self.result_video_thread and self.result_video_thread.isRunning():
            # 空格键 - 播放/暂停
            if event.key() == Qt.Key_Space:
                self.toggle_result_play_pause()
                event.accept()
                return
            # F键 - 下一帧
            elif event.key() == Qt.Key_F:
                self.next_frame(self.result_video_thread, self.result_slider)
                event.accept()
                return
            # D键 - 上一帧
            elif event.key() == Qt.Key_D:
                self.previous_frame(self.result_video_thread, self.result_slider)
                event.accept()
                return
        
        # 第三个标签页（筛选过滤）- 控制筛选视频
        elif current_tab == 2 and hasattr(self, 'filter_video_thread') and self.filter_video_thread.isRunning():
            # 空格键 - 播放/暂停
            if event.key() == Qt.Key_Space:
                self.toggle_filter_play_pause()
                event.accept()
                return
            # F键 - 下一帧
            elif event.key() == Qt.Key_F:
                self.next_frame(self.filter_video_thread, self.filter_slider)
                event.accept()
                return
            # D键 - 上一帧
            elif event.key() == Qt.Key_D:
                self.previous_frame(self.filter_video_thread, self.filter_slider)
                event.accept()
                return
        
        # 调用父类的keyPressEvent以确保其他按键事件正常处理
        super().keyPressEvent(event)
    
    def next_frame(self, video_thread, slider):
        """播放下一帧"""
        if not video_thread or not video_thread.isRunning():
            return
        
        # 确保视频是暂停状态
        mutex = QMutex()
        mutex.lock()
        is_paused = video_thread.paused
        mutex.unlock()
        
        if not is_paused:
            # 如果正在播放，先暂停
            video_thread.toggle_pause()
            # 更新对应按钮的状态（根据video_thread类型）
            if video_thread is self.video_thread:
                self.play_pause_btn.setText("播放")
                self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            elif video_thread is self.result_video_thread:
                self.result_play_pause_btn.setText("播放")
                self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            elif hasattr(self, 'filter_video_thread') and video_thread is self.filter_video_thread:
                self.filter_play_pause_btn.setText("播放")
                self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        
        # 计算下一帧的索引
        current_idx = slider.value()
        next_idx = min(current_idx + 1, slider.maximum())
        
        # 设置新的帧索引
        if next_idx != current_idx:
            slider.setValue(next_idx)  # 这会通过滑块的valueChanged信号间接调用set_frame_index
    
    def previous_frame(self, video_thread, slider):
        """播放上一帧"""
        if not video_thread or not video_thread.isRunning():
            return
        
        # 确保视频是暂停状态
        mutex = QMutex()
        mutex.lock()
        is_paused = video_thread.paused
        mutex.unlock()
        
        if not is_paused:
            # 如果正在播放，先暂停
            video_thread.toggle_pause()
            # 更新对应按钮的状态（根据video_thread类型）
            if video_thread is self.video_thread:
                self.play_pause_btn.setText("播放")
                self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            elif video_thread is self.result_video_thread:
                self.result_play_pause_btn.setText("播放")
                self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            elif hasattr(self, 'filter_video_thread') and video_thread is self.filter_video_thread:
                self.filter_play_pause_btn.setText("播放")
                self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        
        # 计算上一帧的索引
        current_idx = slider.value()
        prev_idx = max(current_idx - 1, 0)
        
        # 设置新的帧索引
        if prev_idx != current_idx:
            slider.setValue(prev_idx)  # 这会通过滑块的valueChanged信号间接调用set_frame_index
    
    # ==== 边界框相关事件处理 ====
    
    def on_bbox_added(self, bbox):
        """当添加新边界框时的处理"""
        frame_idx = self.current_frame_index
        obj_id = bbox[4]
        
        # === Phase 2: 根据标注模式显示不同消息 ===
        mode = self.video_label.overlay_layer.annotation_mode
        if mode == "new_object":
            self.log_message(
                f"在第 {frame_idx} 帧添加新对象 {obj_id}, "
                f"坐标=({int(bbox[0])},{int(bbox[1])},{int(bbox[2])},{int(bbox[3])})", 
                "success"
            )
        else:  # refine_object
            self.log_message(
                f"在第 {frame_idx} 帧为对象 {obj_id} 添加修正标注, "
                f"坐标=({int(bbox[0])},{int(bbox[1])},{int(bbox[2])},{int(bbox[3])})", 
                "highlight"
            )
        
        self._update_annotation_status_display()
        
        # === Phase 2: 刷新对象选择器和标注管理器 ===
        if hasattr(self, 'tabs'):
            setup_tab = self.tabs.widget(0)
            if hasattr(setup_tab, 'update_object_selector'):
                setup_tab.update_object_selector()
            if hasattr(setup_tab, 'annotation_manager'):
                setup_tab.annotation_manager.refresh_table()
        
        # === 触发实时预览 ===
        if hasattr(self, 'video_label') and self.video_label:
            if self.video_label.overlay_layer.preview_enabled:
                self._generate_preview_for_object(bbox[4])
    
    def _generate_preview_for_object(self, obj_id, silent=False):
        """
        为指定对象生成实时预览
        
        Args:
            obj_id (int): 对象ID
            silent (bool): 静默模式，不输出日志（用于批量恢复）
        
        Notes:
            - 收集该对象的所有提示（box + points）
            - 调用PreviewManager生成mask
            - 将mask设置到OverlayLayer显示
        """
        try:
            preview_mgr = self.get_preview_manager()
            overlay = self.video_label.overlay_layer
            
            # 获取当前帧图像（支持视频和图像序列两种模式）
            frame = None
            if self.input_type == "image_sequence" and self.input_source:
                # 图像序列模式：从InputSource读取
                frame = self.input_source.get_frame(self.current_frame_index)
            else:
                # 视频模式：使用cv2.VideoCapture
                cap = cv2.VideoCapture(self.video_path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_index)
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    frame = None
            
            if frame is None:
                if not silent:
                    self.log_message("⚠️ 无法读取当前帧，跳过预览", "warning")
                return
            
            # 设置当前帧到预览管理器
            preview_mgr.set_current_frame(self.current_frame_index, frame)
            
            # 收集该对象的所有提示
            prompts = {"box": None, "points": [], "labels": []}
            
            # 1. 从bbox获取边界框
            for bbox in overlay.bboxes:
                if bbox[4] == obj_id:
                    prompts["box"] = [bbox[0], bbox[1], bbox[2], bbox[3]]
                    break
            
            # 2. 从annotations_per_frame获取点击
            frame_idx = self.current_frame_index
            if frame_idx in overlay.annotations_per_frame:
                if obj_id in overlay.annotations_per_frame[frame_idx]:
                    ann = overlay.annotations_per_frame[frame_idx][obj_id]
                    prompts["points"] = ann.get("points", [])
                    prompts["labels"] = ann.get("labels", [])
            
            # 3. 包含临时点击（如果属于该对象）
            if (overlay.temp_points and 
                overlay.current_editing_obj_id == obj_id and
                overlay.temp_points_frame_idx == frame_idx):
                prompts["points"] = prompts["points"] + overlay.temp_points
                prompts["labels"] = prompts["labels"] + overlay.temp_labels
            
            # 4. 验证至少有一个提示
            if not prompts["box"] and not prompts["points"]:
                if not silent:
                    self.log_message(f"⚠️ 对象 {obj_id} 没有任何提示，无法生成预览", "warning")
                return
            
            # 5. 生成预览mask
            mask = preview_mgr.generate_preview(obj_id, prompts)
            
            if mask is not None:
                overlay.set_preview_mask(obj_id, mask)
                if not silent:
                    self.log_message(f"✓ 对象 {obj_id} 预览已更新", "success")
            else:
                if not silent:
                    self.log_message(f"✗ 对象 {obj_id} 预览生成失败", "error")
        
        except Exception as e:
            if not silent:
                import traceback
                self.log_message(f"✗ 预览生成异常: {e}", "error")
                traceback.print_exc()
    
    def _restore_preview_for_current_frame(self):
        """
        恢复当前帧的预览mask（切换帧后自动调用）
        
        Notes:
            - 检查当前帧是否有标注
            - 如果有，为每个对象自动生成预览
            - 静默失败，不影响用户体验
        """
        if not hasattr(self, 'video_label') or not self.video_label:
            return
        
        overlay = self.video_label.overlay_layer
        
        # 检查是否启用预览
        if not overlay.preview_enabled:
            return
        
        # 获取当前帧的所有对象
        current_frame = self.current_frame_index
        if current_frame not in overlay.bboxes_per_frame:
            return  # 当前帧没有标注
        
        # 获取当前帧的所有对象ID
        bboxes = overlay.bboxes_per_frame[current_frame]
        if not bboxes:
            return
        
        # 为每个对象生成预览（静默模式）
        for bbox in bboxes:
            obj_id = bbox[4]
            try:
                self._generate_preview_for_object(obj_id, silent=True)
            except Exception:
                # 静默失败，不影响用户体验
                pass
    
    def on_bbox_selected(self, index):
        """当选中边界框时的处理"""
        if index >= 0 and index < len(self.video_label.overlay_layer.bboxes):
            bbox = self.video_label.overlay_layer.bboxes[index]
            self.log_message(f"选中边界框: ID={bbox[4]}", "info")
    
    def on_bbox_deleted(self, bbox_id):
        """当删除边界框时的处理"""
        frame_idx = self.current_frame_index
        self.log_message(f"删除第 {frame_idx} 帧的边界框: ID={bbox_id}", "warning")
        self._update_annotation_status_display()
        
        # === Phase 2: 刷新对象选择器和标注管理器 ===
        if hasattr(self, 'tabs'):
            setup_tab = self.tabs.widget(0)
            if hasattr(setup_tab, 'update_object_selector'):
                setup_tab.update_object_selector()
            if hasattr(setup_tab, 'annotation_manager'):
                setup_tab.annotation_manager.refresh_table()
    
    def create_unit_label(self, unit_text):
        """创建统一样式的单位标签，特别处理带有微米符号的单位"""
        label = QLabel(unit_text)
        label.setStyleSheet("""
            font-family: "Times New Roman", Arial, sans-serif;
            font-size: 10pt;
        """)
        return label
    
    def on_tab_changed(self, index):
        """当切换标签页时让相应的视频控件获得焦点"""
        # 第一个标签页 - 视频标注
        if index == 0 and hasattr(self, 'video_label'):
            self.video_label.setFocus()
        # 第二个标签页 - 结果预览
        elif index == 1 and hasattr(self, 'result_label'):
            self.result_label.setFocus()
        # 第三个标签页 - 筛选过滤
        elif index == 2 and hasattr(self, 'filter_video_label'):
            self.filter_video_label.setFocus()
    
    # === Phase 1 MVP: 辅助方法 ===
    def _update_annotation_status_display(self):
        """
        更新标注状态显示
        
        Notes:
            - 更新已标注帧数标签
            - 使用定时器防抖优化性能
        """
        if not hasattr(self, 'video_label') or not self.video_label:
            return
        
        # 使用定时器防抖，避免频繁更新
        if not hasattr(self, '_status_update_timer'):
            from PyQt5.QtCore import QTimer
            self._status_update_timer = QTimer()
            self._status_update_timer.setSingleShot(True)
            self._status_update_timer.timeout.connect(self._do_update_annotation_status)
        
        # 100ms 内只更新一次
        self._status_update_timer.start(100)
    
    def _do_update_annotation_status(self):
        """实际执行状态更新"""
        if not hasattr(self, 'video_label') or not self.video_label:
            return
        
        # 更新已标注帧数标签（如果存在）
        if hasattr(self, 'annotated_frames_label'):
            annotated_frames = self.video_label.get_annotated_frame_indices()
            annotations_dict = self.video_label.get_multi_frame_annotations()
            
            # 统计唯一对象数量（而非标注总数）
            unique_obj_ids = set()
            for bboxes in annotations_dict.values():
                for bbox in bboxes:
                    if len(bbox) >= 5:  # 确保bbox包含obj_id
                        unique_obj_ids.add(bbox[4])
            total_objects = len(unique_obj_ids)
            
            self.annotated_frames_label.setText(
                f"已标注: {len(annotated_frames)}帧 / {total_objects}个对象"
            )
    
    def log_message(self, message, msg_type="info"):
        """记录信息到日志区域，使用不同颜色区分不同类型
        
        参数:
            message: 要显示的消息文本
            msg_type: 消息类型，可以是 "info"(默认), "warning", "error", "success", "highlight"
        """
        # 检查日志组件是否存在
        if not hasattr(self, 'log_text') or self.log_text is None:
            return
            
        # 根据消息类型设置颜色
        colors = {
            "info": "black",
            "warning": "#FF8C00",  # 深橙色
            "error": "#FF0000",    # 红色
            "success": "#008000",  # 绿色
            "highlight": "#0000FF" # 蓝色，用于高亮重要信息
        }
        
        color = colors.get(msg_type, "black")
        
        # 添加带颜色的文本
        self.log_text.append(f'<span style="color:{color};">{message}</span>')
        
        # 确保滚动到最新内容并强制更新滚动条
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()
        
        # 强制刷新滚动条
        QApplication.processEvents() 
    
    def closeEvent(self, event):
        """处理窗口关闭事件，弹出确认对话框"""
        # 创建自定义消息框以使用中文按钮
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认退出")
        msg_box.setText("您确定要关闭Micro Tracker吗？\n未保存的数据和结果将会丢失。")
        msg_box.setIcon(QMessageBox.Question)
        
        # 添加自定义按钮
        confirm_btn = msg_box.addButton("确认", QMessageBox.YesRole)
        cancel_btn = msg_box.addButton("取消", QMessageBox.NoRole)
        msg_box.setDefaultButton(cancel_btn)  # 默认选中取消按钮
        
        # 显示对话框并获取结果
        msg_box.exec_()
        clicked_button = msg_box.clickedButton()

        if clicked_button == confirm_btn:
            # 清理输入源临时文件
            if self.input_source and hasattr(self.input_source, 'cleanup'):
                try:
                    self.input_source.cleanup()
                except Exception as e:
                    print(f"清理临时文件失败: {e}")
            
            # 如果有正在运行的线程，关闭它们
            if hasattr(self, 'video_thread') and self.video_thread and self.video_thread.isRunning():
                self.video_thread.stop()
                
            if hasattr(self, 'processing_thread') and self.processing_thread and self.processing_thread.isRunning():
                self.processing_thread.stop()
                
            if hasattr(self, 'result_video_thread') and self.result_video_thread and self.result_video_thread.isRunning():
                self.result_video_thread.stop()
                
            if hasattr(self, 'filter_video_thread') and self.filter_video_thread and self.filter_video_thread.isRunning():
                self.filter_video_thread.stop()
                
            # 接受关闭事件，关闭窗口
            event.accept()
        else:
            # 拒绝关闭事件，窗口保持打开
            event.ignore() 