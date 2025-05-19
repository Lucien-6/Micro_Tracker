from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QLineEdit, QSlider, QCheckBox, QComboBox, 
                             QGroupBox, QFormLayout, QProgressBar, QMessageBox, QSizePolicy, 
                             QTextEdit, QApplication)
from PyQt5.QtGui import QIcon, QTextCursor, QRegExpValidator
from PyQt5.QtCore import Qt, QTimer, QRegExp

import os
import torch

from micro_tracker.ui.base_tab import BaseTab
from micro_tracker.components.video_widgets import VideoLabel

class SetupTab(BaseTab):
    """参数设置与标注标签页类"""
    
    def __init__(self, main_window):
        """
        初始化设置标签页
        
        Args:
            main_window: 主窗口引用
        """
        super().__init__(main_window)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        # 设置整体布局
        setup_layout = QHBoxLayout(self)
        setup_layout.setContentsMargins(5, 10, 5, 5)
        setup_layout.setSpacing(12)  # 增加左右面板之间的间距
        
        # 创建左右面板
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        # 添加左右面板到布局中
        setup_layout.addWidget(left_panel, 2)  # 左侧面板占比2
        setup_layout.addWidget(right_panel, 3)  # 右侧面板占比3
    
    def create_left_panel(self):
        """创建左侧控制面板"""
        # 左侧控制面板
        left_panel = QWidget()
        left_panel.setMinimumWidth(400)  # 设置最小宽度
        left_panel.setMaximumWidth(500)  # 设置最大宽度
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)  # 增加组件间的垂直间距
        
        # 添加文件选择区域
        file_group = self.create_file_selection_group()
        left_layout.addWidget(file_group)
        
        # 添加参数设置区域
        param_group = self.create_parameter_settings_group()
        left_layout.addWidget(param_group)
        
        # 创建一个垂直布局的伸缩器，使后面的处理进度区域占据所有剩余空间
        left_bottom_container = QWidget()
        left_bottom_layout = QVBoxLayout(left_bottom_container)
        left_bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加处理进度区域
        progress_group = self.create_progress_group()
        left_bottom_layout.addWidget(progress_group, 1)  # 使用伸缩因子1
        
        # 添加开始处理按钮
        self.start_btn = QPushButton("开 始 处 理")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.main_window.start_processing)
        self.start_btn.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            padding: 5px;
            background-color: #4CAF50;
            border-radius: 6px;
        """)
        self.start_btn.setMinimumHeight(40)  # 增加按钮高度
        self.start_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        left_bottom_layout.addWidget(self.start_btn)
        
        # 添加左下角容器到左侧面板
        left_layout.addWidget(left_bottom_container, 1)  # 设置伸缩因子为1
        
        return left_panel
    
    def create_file_selection_group(self):
        """创建文件选择组件"""
        file_group = QGroupBox("文件选择")
        file_layout = QFormLayout()
        file_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        file_layout.setContentsMargins(15, 20, 15, 15)
        file_layout.setSpacing(15)  # 增加表单项之间的间距
        file_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        file_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 视频文件选择
        video_layout = QHBoxLayout()
        video_layout.setSpacing(8)
        self.main_window.video_path_edit = QLineEdit()
        self.main_window.video_path_edit.setReadOnly(True)
        self.main_window.video_path_edit.setPlaceholderText("选择输入视频文件...")
        self.main_window.video_path_edit.setMinimumHeight(24)  # 设置输入框高度
        video_browse_btn = QPushButton("浏览")
        video_browse_btn.setIcon(QIcon.fromTheme("document-open"))
        video_browse_btn.setMinimumWidth(60)
        video_browse_btn.setMaximumWidth(60)
        video_browse_btn.setMinimumHeight(24)  # 设置按钮高度与输入框一致
        video_browse_btn.clicked.connect(self.main_window.browse_video)
        video_layout.addWidget(self.main_window.video_path_edit)
        video_layout.addWidget(video_browse_btn)
        file_layout.addRow("<b>输入视频:</b>", video_layout)
        
        # 模型文件选择
        model_layout = QHBoxLayout()
        model_layout.setSpacing(8)
        self.main_window.model_path_edit = QLineEdit(self.main_window.model_path)
        self.main_window.model_path_edit.setReadOnly(True)
        self.main_window.model_path_edit.setMinimumHeight(24)  # 设置输入框高度
        model_browse_btn = QPushButton("浏览")
        model_browse_btn.setIcon(QIcon.fromTheme("document-open"))
        model_browse_btn.setMinimumWidth(60)
        model_browse_btn.setMaximumWidth(60)
        model_browse_btn.setMinimumHeight(24)  # 设置按钮高度与输入框一致
        model_browse_btn.clicked.connect(self.main_window.browse_model)
        model_layout.addWidget(self.main_window.model_path_edit)
        model_layout.addWidget(model_browse_btn)
        file_layout.addRow("<b>SAM2 模型:</b>", model_layout)
        
        # 输出视频路径
        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)
        self.main_window.output_path_edit = QLineEdit()
        self.main_window.output_path_edit.setReadOnly(True)
        self.main_window.output_path_edit.setPlaceholderText("(默认由系统自动设置)")
        self.main_window.output_path_edit.setMinimumHeight(24)  # 设置输入框高度
        output_browse_btn = QPushButton("浏览")
        output_browse_btn.setIcon(QIcon.fromTheme("document-save"))
        output_browse_btn.setMinimumWidth(60)
        output_browse_btn.setMaximumWidth(60)
        output_browse_btn.setMinimumHeight(24)  # 设置按钮高度与输入框一致
        output_browse_btn.clicked.connect(self.main_window.browse_output)
        output_layout.addWidget(self.main_window.output_path_edit)
        output_layout.addWidget(output_browse_btn)
        file_layout.addRow("<b>输出视频:</b>", output_layout)
        
        # 掩码保存目录
        mask_layout = QHBoxLayout()
        mask_layout.setSpacing(8)
        self.main_window.mask_dir_edit = QLineEdit()
        self.main_window.mask_dir_edit.setReadOnly(True)
        self.main_window.mask_dir_edit.setPlaceholderText("(默认由系统自动设置)")
        self.main_window.mask_dir_edit.setMinimumHeight(24)  # 设置输入框高度
        mask_browse_btn = QPushButton("浏览")
        mask_browse_btn.setIcon(QIcon.fromTheme("folder"))
        mask_browse_btn.setMinimumWidth(60)
        mask_browse_btn.setMaximumWidth(60)
        mask_browse_btn.setMinimumHeight(24)  # 设置按钮高度与输入框一致
        mask_browse_btn.clicked.connect(self.main_window.browse_mask_dir)
        mask_layout.addWidget(self.main_window.mask_dir_edit)
        mask_layout.addWidget(mask_browse_btn)
        file_layout.addRow("<b>掩码目录:</b>", mask_layout)
        
        file_group.setLayout(file_layout)
        return file_group
    
    def create_parameter_settings_group(self):
        """创建参数设置组件"""
        param_group = QGroupBox("参数设置")
        param_layout = QFormLayout()
        param_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        param_layout.setContentsMargins(10, 15, 10, 15)  # 增加底部边距
        param_layout.setSpacing(15)  # 增加设置项间距
        param_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        param_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 设备选择
        self.main_window.device_combo = QComboBox()
        self.main_window.device_combo.setMinimumHeight(24)  # 设置下拉框高度
        self.main_window.device_combo.addItem("CUDA:0 (默认)", "cuda:0")
        self.main_window.device_combo.addItem("CPU", "cpu")
        # 如果有多个 GPU，添加它们
        if torch.cuda.is_available():
            for i in range(1, torch.cuda.device_count()):
                self.main_window.device_combo.addItem(f"CUDA:{i}", f"cuda:{i}")
        # 确保下拉箭头显示
        self.main_window.device_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 2px 6px;
                padding-right: 20px;
                background-color: white;
                min-height: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: url(icons/dropdown.png);
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                selection-background-color: #bbdefb;
                selection-color: #000000;
                border-radius: 0 0 4px 4px;
            }
        """)
        param_layout.addRow("<b>处理设备:</b>", self.main_window.device_combo)
        
        # 保存视频选项
        save_options_layout = QHBoxLayout()
        save_options_layout.setSpacing(20)
        
        video_save_layout = QHBoxLayout()
        video_save_layout.setSpacing(5)
        self.main_window.save_video_check = QCheckBox()
        self.main_window.save_video_check.setChecked(True)
        self.main_window.save_video_check.setMinimumHeight(24)  # 设置复选框高度
        video_save_label = QLabel("保存处理视频")
        video_save_label.setStyleSheet("font-weight: normal;")
        video_save_layout.addWidget(self.main_window.save_video_check)
        video_save_layout.addWidget(video_save_label)
        video_save_layout.addStretch(1)
        
        mask_save_layout = QHBoxLayout()
        mask_save_layout.setSpacing(5)
        self.main_window.save_mask_check = QCheckBox()
        self.main_window.save_mask_check.setChecked(True)  # 默认选中
        self.main_window.save_mask_check.setMinimumHeight(24)  # 设置复选框高度
        mask_save_label = QLabel("保存分割掩码")
        mask_save_label.setStyleSheet("font-weight: normal;")
        mask_save_layout.addWidget(self.main_window.save_mask_check)
        mask_save_layout.addWidget(mask_save_label)
        mask_save_layout.addStretch(1)
        
        save_options_layout.addLayout(video_save_layout)
        save_options_layout.addLayout(mask_save_layout)
        
        param_layout.addRow("输出选项:", save_options_layout)
        
        param_group.setLayout(param_layout)
        param_group.setMinimumHeight(120)  # 降低最小高度，原为180
        return param_group
    
    def create_progress_group(self):
        """创建处理进度组件"""
        progress_group = QGroupBox("处理进度")
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(10, 15, 10, 15)
        progress_layout.setSpacing(10)
        
        self.main_window.log_text = QTextEdit()
        self.main_window.log_text.setReadOnly(True)
        # 确保日志文本区域总是显示滚动条
        self.main_window.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.main_window.log_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 设置更新的样式，确保滚动条可见
        self.main_window.log_text.setStyleSheet("""
            font-family: 'Consolas', 'Monaco', 'Source Code Pro', monospace; 
            font-size: 9.5pt;
            background-color: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 8px;
            color: #424242;
            
            /* Vertical scrollbar styles moved back here */
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 14px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #505050;  /* 黑灰色 */
                min-height: 30px;
                margin: 2px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #404040;  /* 更深的黑灰色 */
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #f0f0f0;
            }
        """)
        
        progress_layout.addWidget(self.main_window.log_text)
        
        self.main_window.progress_bar = QProgressBar()
        self.main_window.progress_bar.setRange(0, 100)
        self.main_window.progress_bar.setValue(0)
        self.main_window.progress_bar.setTextVisible(True)
        self.main_window.progress_bar.setFormat("%p% (%v/%m)")
        self.main_window.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                background-color: #f5f5f5;
                height: 24px;
                font-size: 10pt;
                font-weight: bold;
                color: #424242;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.main_window.progress_bar.setVisible(False)
        progress_layout.addWidget(self.main_window.progress_bar)
        
        # 添加一个函数来确保滚动条正确显示
        def ensure_scrollbars_visible():
            # 添加一些测试文本确保滚动条初始化正确
            for i in range(20):
                self.main_window.log_text.append(f"初始化日志行 {i+1}")
            
            # 强制更新UI并滚动到顶部
            QApplication.processEvents()
            self.main_window.log_text.clear()
            QApplication.processEvents()
        
        # 在UI初始化完成后调用此函数
        QTimer.singleShot(100, ensure_scrollbars_visible)
        
        progress_group.setLayout(progress_layout)
        # 设置处理进度区域为垂直方向可扩展
        progress_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        return progress_group
    
    def create_right_panel(self):
        """创建右侧预览面板"""
        right_panel = QWidget()
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 0, 0, 0)
        
        # 视频预览和边界框绘制区域
        preview_group = QGroupBox("视频预览和边界框绘制")
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(10, 15, 10, 15)
        preview_layout.setSpacing(10)
        
        # 视频显示标签
        self.main_window.video_label = VideoLabel()
        self.main_window.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        self.main_window.video_label.setStyleSheet("""
            border: 1px solid #e0e0e0; 
            background-color: #f8f8f8;
            border-radius: 4px;
        """)
        preview_layout.addWidget(self.main_window.video_label)
        
        # 连接边界框相关信号
        self.main_window.video_label.bbox_added.connect(self.main_window.on_bbox_added)
        self.main_window.video_label.bbox_selected.connect(self.main_window.on_bbox_selected)
        self.main_window.video_label.bbox_deleted.connect(self.main_window.on_bbox_deleted)
        
        # 视频预览控制
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 12, 0, 0)  # 增加顶部间距
        control_layout.setSpacing(15)
        
        # 添加播放/暂停按钮
        self.main_window.play_pause_btn = QPushButton("播放")
        self.main_window.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.main_window.play_pause_btn.setMinimumWidth(90)
        self.main_window.play_pause_btn.setMaximumWidth(110)
        self.main_window.play_pause_btn.setEnabled(False)
        self.main_window.play_pause_btn.setStyleSheet("font-weight: bold;")
        self.main_window.play_pause_btn.clicked.connect(self.main_window.toggle_play_pause)
        
        self.main_window.frame_slider = QSlider(Qt.Horizontal)
        self.main_window.frame_slider.setEnabled(False)
        self.main_window.frame_slider.setMinimumHeight(28)  # 增加滑块高度
        self.main_window.frame_slider.valueChanged.connect(self.main_window.set_frame_index)
        
        self.main_window.frame_info_label = QLabel("当前帧: 0 / 0")
        self.main_window.frame_info_label.setMinimumWidth(100)
        self.main_window.frame_info_label.setStyleSheet("font-weight: bold; color: #455a64;")
        
        clear_bbox_btn = QPushButton("清除边界框")
        clear_bbox_btn.setIcon(QIcon.fromTheme("edit-delete"))
        clear_bbox_btn.setMinimumWidth(80)
        clear_bbox_btn.setMaximumWidth(100)
        clear_bbox_btn.setStyleSheet("background-color: #f44336;")
        clear_bbox_btn.clicked.connect(self.main_window.video_label.clear_bboxes)
        
        control_layout.addWidget(self.main_window.play_pause_btn)
        control_layout.addWidget(self.main_window.frame_slider)
        control_layout.addWidget(self.main_window.frame_info_label)
        control_layout.addWidget(clear_bbox_btn)
        
        preview_layout.addLayout(control_layout)
        
        # 操作说明
        help_text = QLabel(
            "操作说明: \n"
            "1. 在视频画面上点击并拖动鼠标来绘制边界框\n"
            "2. 点击边界框可选中它，按 Delete 键删除选中的边界框\n"
            "3. 使用滑块浏览视频帧，在第一帧上绘制要追踪的目标边界框\n"
            "4. 键盘控制: 空格键-播放/暂停, F键-下一帧, D键-上一帧\n"
        )
        help_text.setAlignment(Qt.AlignCenter)
        help_text.setStyleSheet("""
            background-color: #e8f5e9; 
            padding: 10px; 
            border-radius: 5px; 
            border: 1px solid #a5d6a7;
            color: #2e7d32;
            font-weight: bold;
            font-size: 9.5pt;
        """)
        help_text.setMinimumHeight(90)  # 设置最小高度
        preview_layout.addWidget(help_text)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        return right_panel 