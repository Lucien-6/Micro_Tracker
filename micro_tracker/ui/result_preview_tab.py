from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QSlider, QGroupBox, QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os
import subprocess
import sys

from micro_tracker.ui.base_tab import BaseTab
from micro_tracker.components.video_widgets import ResultVideoLabel

class ResultPreviewTab(BaseTab):
    """结果预览标签页类"""
    
    def __init__(self, main_window):
        """
        初始化结果预览标签页
        
        Args:
            main_window: 主窗口引用
        """
        super().__init__(main_window)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        # 整体布局
        process_layout = QVBoxLayout(self)
        process_layout.setContentsMargins(15, 15, 15, 15)  # 增加边距
        process_layout.setSpacing(12)  # 增加间距
        
        # 结果预览区域
        result_group = QGroupBox("处理结果视频预览")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(15, 20, 15, 15)  # 增加内边距
        result_layout.setSpacing(12)  # 增加间距
        
        self.main_window.result_label = ResultVideoLabel()
        self.main_window.result_label.setMinimumSize(800, 500)  # 增加最小尺寸
        self.main_window.result_label.setAlignment(Qt.AlignCenter)
        self.main_window.result_label.setStyleSheet("""
            border: 1px solid #e0e0e0; 
            background-color: #f8f8f8;
            border-radius: 4px;
        """)
        self.main_window.result_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        result_layout.addWidget(self.main_window.result_label)
        
        # 预览控制器
        result_control_layout = QHBoxLayout()
        result_control_layout.setContentsMargins(0, 12, 0, 0)  # 增加上边距
        result_control_layout.setSpacing(15)  # 增加组件间距
        
        # 添加播放/暂停按钮
        self.main_window.result_play_pause_btn = QPushButton("播放")
        self.main_window.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.main_window.result_play_pause_btn.setMinimumWidth(90)
        self.main_window.result_play_pause_btn.setMaximumWidth(110)
        self.main_window.result_play_pause_btn.setEnabled(False)
        self.main_window.result_play_pause_btn.setStyleSheet("font-weight: bold;")
        self.main_window.result_play_pause_btn.clicked.connect(self.main_window.toggle_result_play_pause)
        
        self.main_window.result_slider = QSlider(Qt.Horizontal)
        self.main_window.result_slider.setEnabled(False)
        self.main_window.result_slider.setMinimumHeight(30)  # 增加滑块高度
        self.main_window.result_slider.valueChanged.connect(self.main_window.set_result_frame_index)
        
        self.main_window.result_info_label = QLabel("处理结果: 0 / 0")
        self.main_window.result_info_label.setMinimumWidth(120)  # 增加标签宽度
        self.main_window.result_info_label.setStyleSheet("font-weight: bold; color: #455a64;")  # 添加粗体样式
        
        open_output_btn = QPushButton("打开输出文件夹")
        open_output_btn.setIcon(QIcon.fromTheme("folder-open"))  # 添加图标
        open_output_btn.clicked.connect(self.main_window.open_output_folder)
        open_output_btn.setMinimumWidth(120)
        open_output_btn.setMaximumWidth(130)
        open_output_btn.setMinimumHeight(36)  # 增加按钮高度
        open_output_btn.setStyleSheet("background-color: #03A9F4;")  # 使用蓝色突出此按钮
        
        result_control_layout.addWidget(self.main_window.result_play_pause_btn)
        result_control_layout.addWidget(self.main_window.result_slider)
        result_control_layout.addWidget(self.main_window.result_info_label)
        result_control_layout.addWidget(open_output_btn)
        
        result_layout.addLayout(result_control_layout)
        
        result_group.setLayout(result_layout)
        process_layout.addWidget(result_group)
        
        # 添加一个说明标签
        result_help_label = QLabel("处理完成后，您可以在此处查看处理结果视频。使用滑块浏览不同帧，点击\"打开输出文件夹\"可直接访问输出视频所在目录。键盘控制: 空格键-播放/暂停, F键-下一帧, D键-上一帧。")
        result_help_label.setAlignment(Qt.AlignCenter)
        result_help_label.setStyleSheet("color: #666666; background-color: #f5f5f5; padding: 10px; border-radius: 3px; border: 1px solid #e0e0e0;")
        result_help_label.setWordWrap(True)  # 启用自动换行
        result_help_label.setMinimumHeight(50)
        process_layout.addWidget(result_help_label) 