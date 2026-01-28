from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QLineEdit, QSlider, QCheckBox, QComboBox, 
                             QGroupBox, QFormLayout, QProgressBar, QMessageBox, QSizePolicy, 
                             QTextEdit, QApplication, QRadioButton, QButtonGroup, QDoubleSpinBox)
from PyQt5.QtGui import QIcon, QTextCursor, QRegExpValidator
from PyQt5.QtCore import Qt, QTimer, QRegExp

import os
import torch
from pathlib import Path

from micro_tracker.ui.base_tab import BaseTab
from micro_tracker.components.video_widgets import VideoLabel
from micro_tracker.config.style import TEXTEDIT_LOG_STYLE
from micro_tracker.ui.annotation_manager import AnnotationManagerWidget

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
        
        # === 输入类型选择 ===
        input_type_layout = QHBoxLayout()
        input_type_layout.setSpacing(15)
        
        self.video_input_radio = QRadioButton("视频文件")
        self.video_input_radio.setChecked(True)
        self.video_input_radio.setToolTip("选择 .mp4, .avi, .mov, .mkv 等视频文件")
        
        self.image_seq_input_radio = QRadioButton("图像序列")
        self.image_seq_input_radio.setToolTip("选择包含图像序列的文件夹 (支持 jpg, png, tif, bmp)")
        
        self.input_type_group = QButtonGroup()
        self.input_type_group.addButton(self.video_input_radio)
        self.input_type_group.addButton(self.image_seq_input_radio)
        
        input_type_layout.addWidget(self.video_input_radio)
        input_type_layout.addWidget(self.image_seq_input_radio)
        input_type_layout.addStretch()
        
        file_layout.addRow("输入类型:", input_type_layout)
        
        # 连接信号（两个单选按钮都需要连接）
        self.video_input_radio.toggled.connect(self.on_input_type_changed)
        self.image_seq_input_radio.toggled.connect(self.on_input_type_changed)
        
        # === 输入源选择（视频文件或图像序列文件夹）===
        input_source_layout = QHBoxLayout()
        input_source_layout.setSpacing(8)
        self.main_window.video_path_edit = QLineEdit()
        self.main_window.video_path_edit.setReadOnly(True)
        self.main_window.video_path_edit.setPlaceholderText("选择输入视频文件...")
        self.main_window.video_path_edit.setMinimumHeight(24)
        self.input_browse_btn = QPushButton("浏览")
        self.input_browse_btn.setIcon(QIcon.fromTheme("document-open"))
        self.input_browse_btn.setMinimumWidth(60)
        self.input_browse_btn.setMaximumWidth(60)
        self.input_browse_btn.setMinimumHeight(24)
        self.input_browse_btn.clicked.connect(self.main_window.browse_input)
        input_source_layout.addWidget(self.main_window.video_path_edit)
        input_source_layout.addWidget(self.input_browse_btn)
        file_layout.addRow("输入源:", input_source_layout)
        
        # === 图像序列默认帧率（不显示UI，使用默认值10fps）===
        self.main_window.image_seq_fps = 10.0  # 默认10fps
        
        # 模型文件选择（下拉选择）
        model_layout = QHBoxLayout()
        model_layout.setSpacing(8)
        self.main_window.model_combo = QComboBox()
        self.main_window.model_combo.setMinimumHeight(24)
        self.main_window.model_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # 自动扫描并添加模型
        self.populate_model_list()
        
        # 连接信号
        self.main_window.model_combo.currentIndexChanged.connect(self.on_model_selected)
        
        # 设置下拉框样式
        self.main_window.model_combo.setStyleSheet("""
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
        
        model_browse_btn = QPushButton("浏览")
        model_browse_btn.setIcon(QIcon.fromTheme("document-open"))
        model_browse_btn.setMinimumWidth(60)
        model_browse_btn.setMaximumWidth(60)
        model_browse_btn.setMinimumHeight(24)
        model_browse_btn.setToolTip("选择自定义模型文件")
        model_browse_btn.clicked.connect(self.main_window.browse_model)
        
        model_layout.addWidget(self.main_window.model_combo)
        model_layout.addWidget(model_browse_btn)
        file_layout.addRow("SAM2 模型:", model_layout)
        
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
        file_layout.addRow("结果视频输出:", output_layout)
        
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
        file_layout.addRow("掩码保存目录:", mask_layout)
        
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
        param_layout.addRow("处理设备:", self.main_window.device_combo)
        
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
        
        # 不再单独应用样式，完全依赖全局样式中的QTextEdit[readOnly="true"]规则
        
        progress_layout.addWidget(self.main_window.log_text)
        
        self.main_window.progress_bar = QProgressBar()
        self.main_window.progress_bar.setRange(0, 100)
        self.main_window.progress_bar.setValue(0)
        self.main_window.progress_bar.setTextVisible(True)
        self.main_window.progress_bar.setFormat("%p%")  # 只显示百分比
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
        
        # 视频预览和提示绘制区域
        preview_group = QGroupBox("视频预览和提示绘制")
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
        
        self.main_window.frame_info_label = QLabel("0 / 0")
        self.main_window.frame_info_label.setMinimumWidth(50)
        self.main_window.frame_info_label.setStyleSheet("font-weight: bold; color: #455a64;")
        
        # 已标注帧数统计（移到滑块右侧）
        self.main_window.annotated_frames_label = QLabel("已标注: 0帧 / 0个对象")
        self.main_window.annotated_frames_label.setStyleSheet("""
            background-color: #E8F5E9;
            padding: 6px 12px;
            border-radius: 4px;
            border: 1px solid #81C784;
            color: #2E7D32;
            font-weight: bold;
            font-size: 9pt;
        """)
        
        control_layout.addWidget(self.main_window.play_pause_btn, 0)  # 不伸展
        control_layout.addWidget(self.main_window.frame_slider, 1)  # 可伸展
        control_layout.addWidget(self.main_window.frame_info_label, 0)  # 不伸展
        control_layout.addWidget(self.main_window.annotated_frames_label, 0)  # 不伸展
        
        preview_layout.addLayout(control_layout)
        
        # === 标注模式与提示类型的左右布局 ===
        mode_prompt_layout = QHBoxLayout()
        
        # 左侧：标注模式
        annotation_mode_group = QGroupBox("标注模式")
        annotation_mode_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 9pt;
                margin-top: 6px;
                padding-top: 12px;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        annotation_mode_layout = QVBoxLayout()
        annotation_mode_layout.setSpacing(5)
        annotation_mode_layout.setContentsMargins(8, 5, 8, 5)
        
        # 模式选择按钮（左右排列）
        mode_selection_layout = QHBoxLayout()
        
        self.new_object_radio = QRadioButton("新对象")
        self.new_object_radio.setChecked(True)
        self.new_object_radio.setToolTip("为新出现的对象添加标注")
        self.new_object_radio.setStyleSheet("""
            QRadioButton {
                font-size: 9pt;
                padding: 2px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
        """)
        
        self.refine_object_radio = QRadioButton("修正对象")
        self.refine_object_radio.setToolTip("为已存在的对象添加新帧标注")
        self.refine_object_radio.setStyleSheet("""
            QRadioButton {
                font-size: 9pt;
                padding: 2px;
            }
        """)
        
        self.mode_button_group = QButtonGroup()
        self.mode_button_group.addButton(self.new_object_radio)
        self.mode_button_group.addButton(self.refine_object_radio)
        
        mode_selection_layout.addWidget(self.new_object_radio)
        mode_selection_layout.addWidget(self.refine_object_radio)
        mode_selection_layout.addStretch()
        annotation_mode_layout.addLayout(mode_selection_layout)
        
        # 对象选择下拉框（水平排列）
        object_selector_layout = QHBoxLayout()
        object_selector_layout.setSpacing(8)
        
        object_selector_label = QLabel("选择对象:")
        object_selector_label.setStyleSheet("font-size: 9pt;")
        
        self.main_window.object_selector_combo = QComboBox()
        self.main_window.object_selector_combo.setEnabled(False)
        self.main_window.object_selector_combo.setMinimumWidth(240)
        self.main_window.object_selector_combo.setMaximumHeight(28)
        self.main_window.object_selector_combo.setStyleSheet("""
            QComboBox {
                font-size: 9pt;
                padding: 2px 4px;
            }
        """)
        
        object_selector_layout.addWidget(object_selector_label)
        object_selector_layout.addWidget(self.main_window.object_selector_combo)
        object_selector_layout.addStretch()
        annotation_mode_layout.addLayout(object_selector_layout)
        
        annotation_mode_group.setLayout(annotation_mode_layout)
        mode_prompt_layout.addWidget(annotation_mode_group)
        
        # 右侧：提示类型
        prompt_type_group = QGroupBox("提示类型")
        prompt_type_group.setStyleSheet("""  
            QGroupBox {
                font-weight: bold;
                font-size: 9pt;
                margin-top: 6px;
                padding-top: 12px;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        prompt_type_layout = QVBoxLayout()
        prompt_type_layout.setSpacing(4)
        prompt_type_layout.setContentsMargins(8, 5, 8, 5)
        
        # 主要提示类型（左右排列）
        prompt_mode_layout = QHBoxLayout()
        
        self.box_mode_radio = QRadioButton("边界框模式")
        self.box_mode_radio.setChecked(True)
        self.box_mode_radio.setToolTip("使用鼠标拖拽绘制边界框")
        self.box_mode_radio.setStyleSheet("""
            QRadioButton {
                font-size: 9pt;
                padding: 2px;
            }
        """)
        
        self.point_mode_radio = QRadioButton("点击模式")
        self.point_mode_radio.setToolTip("左键-添加区域（正向点击），右键-移除区域（负向点击）")
        self.point_mode_radio.setStyleSheet("""
            QRadioButton {
                font-size: 9pt;
                padding: 2px;
            }
        """)
        
        self.prompt_type_button_group = QButtonGroup()
        self.prompt_type_button_group.addButton(self.box_mode_radio)
        self.prompt_type_button_group.addButton(self.point_mode_radio)
        
        prompt_mode_layout.addWidget(self.box_mode_radio)
        prompt_mode_layout.addWidget(self.point_mode_radio)
        prompt_mode_layout.addStretch()
        prompt_type_layout.addLayout(prompt_mode_layout)
        
        # 说明文字
        hint_label = QLabel("点击模式: 左键添加区域，右键移除区域")
        hint_label.setStyleSheet("font-size: 8pt; color: #666; padding-left: 5px;")
        prompt_type_layout.addWidget(hint_label)
        
        prompt_type_group.setLayout(prompt_type_layout)
        mode_prompt_layout.addWidget(prompt_type_group)
        
        preview_layout.addLayout(mode_prompt_layout)
        
        # 连接信号
        self.new_object_radio.toggled.connect(self.on_annotation_mode_changed)
        self.refine_object_radio.toggled.connect(self.on_annotation_mode_changed)
        self.main_window.object_selector_combo.currentIndexChanged.connect(self.on_object_selected)
        
        # 连接提示类型信号
        self.box_mode_radio.toggled.connect(self.on_prompt_type_changed)
        self.point_mode_radio.toggled.connect(self.on_prompt_type_changed)
        
        # 标注管理器移到这里
        from micro_tracker.ui.annotation_manager import AnnotationManagerWidget
        self.main_window.annotation_manager = AnnotationManagerWidget(self.main_window)
        preview_layout.addWidget(self.main_window.annotation_manager)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        return right_panel
    
    # === Phase 2: 标注模式切换回调方法 ===
    def on_annotation_mode_changed(self, checked):
        """标注模式切换处理"""
        # 只处理按钮被选中的情况，忽略取消选中的信号
        if not checked:
            return
            
        if self.new_object_radio.isChecked():
            # 新对象模式
            self.main_window.object_selector_combo.setEnabled(False)
            self.main_window.video_label.overlay_layer.set_annotation_mode("new_object")
            self.main_window.log_message("标注模式: 新对象", "info")
            
            # 恢复box模式选项
            if hasattr(self, 'box_mode_radio'):
                self.box_mode_radio.setEnabled(True)
        else:
            # 修正模式
            self.main_window.object_selector_combo.setEnabled(True)
            self.update_object_selector()
            
            # === 符合SAM2官方规范：refinement时自动切换到点击模式 ===
            if hasattr(self, 'point_mode_radio') and hasattr(self, 'box_mode_radio'):
                # 自动切换到点击模式
                if not self.point_mode_radio.isChecked():
                    self.point_mode_radio.setChecked(True)
                
                # 禁用box模式（符合SAM2官方规范：refinement只用points）
                self.box_mode_radio.setEnabled(False)
            
            self.main_window.log_message(
                "标注模式: 修正对象 (已自动切换到点击模式，符合SAM2官方规范)", 
                "warning"
            )
    
    def update_object_selector(self):
        """更新对象选择下拉框"""
        combo = self.main_window.object_selector_combo
        
        # === 修复：阻塞信号，防止 clear() 和 addItem() 触发 currentIndexChanged ===
        # 这会避免在新对象模式下意外触发模式切换
        combo.blockSignals(True)
        
        combo.clear()
        
        # 获取对象注册表
        registry = self.main_window.video_label.overlay_layer.object_registry
        
        if not registry:
            combo.addItem("（无可用对象，请先添加对象）", None)
            combo.blockSignals(False)
            return
        
        # 按对象ID排序
        for obj_id in sorted(registry.keys()):
            info = registry[obj_id]
            first_frame = info["first_frame"]
            frame_count = len(info["frames"])
            
            # 显示对象信息
            text = f"对象 {obj_id} (首次: 第{first_frame}帧, {frame_count}个标注)"
            combo.addItem(text, obj_id)
        
        # 恢复信号
        combo.blockSignals(False)
        
        # === 只有在修正模式下才自动选中第一个对象 ===
        if combo.count() > 0 and self.refine_object_radio.isChecked():
            combo.setCurrentIndex(0)
            # 手动触发（因为信号已解除阻塞）
            self.on_object_selected(0)
    
    def on_object_selected(self, index):
        """用户选择了要修正的对象"""
        combo = self.main_window.object_selector_combo
        
        if index < 0 or combo.count() == 0:
            return
        
        obj_id = combo.currentData()
        
        if obj_id is not None:
            # === 修复：只有在修正模式下才设置修正模式 ===
            # 避免在新对象模式下被意外触发
            if not self.refine_object_radio.isChecked():
                return
            
            # 设置修正模式
            self.main_window.video_label.overlay_layer.set_annotation_mode("refine_object", obj_id)
            
            # 获取该对象的信息
            registry = self.main_window.video_label.overlay_layer.object_registry
            if obj_id in registry:
                info = registry[obj_id]
                frames_str = ", ".join(map(str, info["frames"]))
                self.main_window.log_message(
                    f"选中对象 {obj_id}，已在帧 [{frames_str}] 标注", 
                    "highlight"
                )
    
    def on_prompt_type_changed(self, checked):
        """提示类型切换处理"""
        # 只处理按钮被选中的情况，忽略取消选中的信号
        if not checked:
            return
            
        if not hasattr(self.main_window, 'video_label') or not self.main_window.video_label:
            return
            
        if self.box_mode_radio.isChecked():
            # 边界框模式
            self.main_window.video_label.overlay_layer.prompt_mode = "box"
            self.main_window.log_message("提示类型: 边界框模式", "info")
        else:
            # 点击模式（左键=正向，右键=负向）
            self.main_window.video_label.overlay_layer.prompt_mode = "point"
            self.main_window.log_message("提示类型: 点击模式（左键添加，右键移除）", "info")
    
    def toggle_prompt_type(self):
        """
        切换提示类型（Tab快捷键触发）
        
        Returns:
            bool: 切换是否成功
        
        Notes:
            - 修正模式下边界框被禁用，不允许切换
            - 循环顺序：边界框 → 点击 → 边界框
        """
        # 检查边界框模式是否可用
        if not self.box_mode_radio.isEnabled():
            self.main_window.log_message(
                "⚠️ 修正模式下只能使用点击模式（符合SAM2官方规范）", 
                "warning"
            )
            return False
        
        # 切换模式
        if self.box_mode_radio.isChecked():
            self.point_mode_radio.setChecked(True)
        else:
            self.box_mode_radio.setChecked(True)
        
        return True
    
    def on_input_type_changed(self, checked):
        """
        输入类型切换处理
        
        Args:
            checked (bool): 按钮是否被选中
        
        Notes:
            - 切换视频文件和图像序列输入模式
            - 更新UI元素的可见性和占位符文本
            - 清空当前选择
        """
        # 只处理按钮被选中的情况
        if not checked:
            return
        
        is_video_mode = self.video_input_radio.isChecked()
        
        # 更新占位符文本
        if is_video_mode:
            self.main_window.video_path_edit.setPlaceholderText("选择输入视频文件...")
            self.main_window.input_type = "video"
        else:
            self.main_window.video_path_edit.setPlaceholderText("选择图像序列文件夹...")
            self.main_window.input_type = "image_sequence"
        
        # 清空当前选择
        self.main_window.video_path_edit.clear()
        self.main_window.video_path_edit.setToolTip("")
        self.main_window.video_path = ""
        self.main_window.input_source = None
        
        # 禁用开始按钮
        self.start_btn.setEnabled(False)
        
        # 日志
        if is_video_mode:
            self.main_window.log_message("输入模式已切换为: 视频文件 (支持格式: mp4, avi, mov, mkv)", "info")
        else:
            self.main_window.log_message("输入模式已切换为: 图像序列", "info")
            self.main_window.log_message(
                "  支持格式: jpg, jpeg, png, tif, tiff, bmp", 
                "info"
            )
    
    def populate_model_list(self):
        """自动扫描并填充模型列表"""
        combo = self.main_window.model_combo
        combo.clear()
        
        # 定义模型目录
        model_dir = Path("models/sam2/checkpoints")
        
        # 检查目录是否存在
        if not model_dir.exists():
            combo.addItem("❌ 模型目录不存在", None)
            self.main_window.log_message(f"警告: 模型目录不存在: {model_dir}", "warning")
            return
        
        # 扫描.pt文件
        model_files = sorted(model_dir.glob("*.pt"))
        
        if not model_files:
            combo.addItem("❌ 未找到模型文件", None)
            self.main_window.log_message(f"警告: 在 {model_dir} 中未找到.pt模型文件", "warning")
            return
        
        # 添加找到的模型
        model_info = {
            "tiny": ("🟢 Tiny - 最快速度，适合实时预览", "sam2.1_hiera_tiny.pt"),
            "small": ("🟡 Small - 平衡速度与精度", "sam2.1_hiera_small.pt"),
            "base_plus": ("🟠 Base+ - 高精度（推荐）", "sam2.1_hiera_base_plus.pt"),
            "large": ("🔴 Large - 最高精度，较慢", "sam2.1_hiera_large.pt"),
        }
        
        default_index = 0
        for i, model_file in enumerate(model_files):
            file_name = model_file.name
            
            # 查找友好名称
            display_name = file_name
            for key, (friendly_name, pattern) in model_info.items():
                if pattern in file_name:
                    display_name = friendly_name
                    break
            
            # 添加到下拉框
            combo.addItem(display_name, str(model_file))
            
            # 设置默认选项（tiny）
            if "tiny" in file_name.lower():
                default_index = i
        
        # 设置默认选择
        combo.setCurrentIndex(default_index)
        
        self.main_window.log_message(f"✓ 发现 {len(model_files)} 个SAM2模型", "info")
    
    def on_model_selected(self, index):
        """模型选择变化处理"""
        combo = self.main_window.model_combo
        
        if index < 0 or combo.count() == 0:
            return
        
        model_path = combo.currentData()
        
        if model_path and model_path != "None":
            self.main_window.model_path = model_path
            self.main_window.log_message(f"选择模型: {Path(model_path).name}", "info")
            self.main_window.check_start_enabled()
        else:
            self.main_window.log_message("警告: 无效的模型路径", "warning")
    
    def reset_ui_state(self):
        """
        重置标注相关的UI状态（用于加载新视频/图像序列时）
        
        Notes:
            - 重置标注模式为"新对象"
            - 重置提示类型为"边界框模式"
            - 清空并禁用对象选择器
        """
        # 重置标注模式为"新对象"
        self.new_object_radio.setChecked(True)
        
        # 重置提示类型为"边界框模式"并启用
        self.box_mode_radio.setEnabled(True)
        self.box_mode_radio.setChecked(True)
        
        # 清空并禁用对象选择器
        self.main_window.object_selector_combo.clear()
        self.main_window.object_selector_combo.setEnabled(False) 