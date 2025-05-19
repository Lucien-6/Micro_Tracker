from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QSlider, QGroupBox, QSizePolicy, QFormLayout, QLineEdit, 
                             QCheckBox, QTextEdit, QApplication, QProgressBar)
from PyQt5.QtGui import QIcon, QTextCursor, QRegExpValidator
from PyQt5.QtCore import Qt, QTimer, QRegExp

from micro_tracker.ui.base_tab import BaseTab
from micro_tracker.ui.filter_conditions import FilterConditionsGroup
from micro_tracker.components.video_widgets import ResultVideoLabel

class FilterTab(BaseTab):
    """筛选过滤标签页类"""
    
    def __init__(self, main_window):
        """
        初始化筛选过滤标签页
        
        Args:
            main_window: 主窗口引用
        """
        super().__init__(main_window)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI界面"""
        # 整体布局
        filter_layout = QHBoxLayout(self)
        filter_layout.setContentsMargins(5, 10, 5, 5)
        filter_layout.setSpacing(12)  # 增加左右面板之间的间距
        
        # 创建左右面板
        filter_left_panel = self.create_left_panel()
        filter_right_panel = self.create_right_panel()
        
        # 添加左右面板到主布局
        filter_layout.addWidget(filter_left_panel, 2)  # 左侧占比2
        filter_layout.addWidget(filter_right_panel, 3)  # 右侧占比3
    
    def create_left_panel(self):
        """创建左侧控制面板"""
        filter_left_panel = QWidget()
        filter_left_panel.setMinimumWidth(400)  # 设置最小宽度
        filter_left_panel.setMaximumWidth(500)  # 设置最大宽度
        filter_left_layout = QVBoxLayout(filter_left_panel)
        filter_left_layout.setContentsMargins(0, 0, 0, 0)
        filter_left_layout.setSpacing(10)  # 增加组件间的垂直间距
        
        # 1. 掩膜图片序列选择组件
        mask_select_group = self.create_mask_selection_group()
        filter_left_layout.addWidget(mask_select_group)
        
        # 2. 参数设置组件
        param_setting_group = self.create_parameter_settings_group()
        filter_left_layout.addWidget(param_setting_group)
        
        # 3. 筛选条件组件（使用独立组件类）
        filter_conditions_component = FilterConditionsGroup(self.main_window)
        filter_conditions_group = filter_conditions_component.create_group()
        filter_left_layout.addWidget(filter_conditions_group)
        
        # 4. 排除指定对象组件
        exclude_group = self.create_exclude_objects_group()
        filter_left_layout.addWidget(exclude_group)
        
        # 5. 应用筛选按钮
        self.main_window.apply_filter_btn = QPushButton("应 用 筛 选")
        self.main_window.apply_filter_btn.setEnabled(False)
        self.main_window.apply_filter_btn.clicked.connect(self.main_window.apply_mask_filter)
        self.main_window.apply_filter_btn.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            padding: 5px;
            background-color: #4CAF50;
            border-radius: 6px;
        """)
        self.main_window.apply_filter_btn.setMinimumHeight(40)
        self.main_window.apply_filter_btn.setIcon(QIcon.fromTheme("view-filter"))
        filter_left_layout.addWidget(self.main_window.apply_filter_btn)
        
        # 6. 筛选处理进度区域
        filter_progress_group = self.create_filter_progress_group()
        filter_left_layout.addWidget(filter_progress_group, 1)  # 添加伸缩因子1
        
        return filter_left_panel
    
    def create_right_panel(self):
        """创建右侧预览面板"""
        filter_right_panel = QWidget()
        filter_right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        filter_right_layout = QVBoxLayout(filter_right_panel)
        filter_right_layout.setContentsMargins(5, 0, 0, 0)
        
        # 筛选结果视频预览
        filter_preview_group = QGroupBox("筛选结果预览")
        filter_preview_layout = QVBoxLayout()
        filter_preview_layout.setContentsMargins(10, 15, 10, 15)
        filter_preview_layout.setSpacing(10)
        
        # 结果视频显示标签
        self.main_window.filter_video_label = ResultVideoLabel()
        self.main_window.filter_video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_window.filter_video_label.setStyleSheet("""
            border: 1px solid #e0e0e0; 
            background-color: #f8f8f8;
            border-radius: 4px;
        """)
        filter_preview_layout.addWidget(self.main_window.filter_video_label)
        
        # 筛选结果控制
        filter_control_layout = QHBoxLayout()
        filter_control_layout.setContentsMargins(0, 12, 0, 0)
        filter_control_layout.setSpacing(15)
        
        # 播放/暂停按钮
        self.main_window.filter_play_pause_btn = QPushButton("播放")
        self.main_window.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.main_window.filter_play_pause_btn.setMinimumWidth(90)
        self.main_window.filter_play_pause_btn.setMaximumWidth(110)
        self.main_window.filter_play_pause_btn.setEnabled(False)
        self.main_window.filter_play_pause_btn.setStyleSheet("font-weight: bold;")
        self.main_window.filter_play_pause_btn.clicked.connect(self.main_window.toggle_filter_play_pause)
        
        self.main_window.filter_slider = QSlider(Qt.Horizontal)
        self.main_window.filter_slider.setEnabled(False)
        self.main_window.filter_slider.setMinimumHeight(28)
        self.main_window.filter_slider.valueChanged.connect(self.main_window.set_filter_frame_index)
        
        self.main_window.filter_info_label = QLabel("筛选结果: 0 / 0")
        self.main_window.filter_info_label.setMinimumWidth(100)
        self.main_window.filter_info_label.setStyleSheet("font-weight: bold; color: #455a64;")
        
        # 保存按钮
        self.main_window.save_filter_btn = QPushButton("输出保存")
        self.main_window.save_filter_btn.setIcon(QIcon.fromTheme("document-save"))
        self.main_window.save_filter_btn.setMinimumWidth(100)
        self.main_window.save_filter_btn.setMaximumWidth(110)
        self.main_window.save_filter_btn.setEnabled(False)
        self.main_window.save_filter_btn.setStyleSheet("background-color: #03A9F4;")
        self.main_window.save_filter_btn.clicked.connect(self.main_window.save_filter_results)
        
        filter_control_layout.addWidget(self.main_window.filter_play_pause_btn)
        filter_control_layout.addWidget(self.main_window.filter_slider)
        filter_control_layout.addWidget(self.main_window.filter_info_label)
        filter_control_layout.addWidget(self.main_window.save_filter_btn)
        
        filter_preview_layout.addLayout(filter_control_layout)
        
        # 统计信息面板
        filter_stats_layout = QHBoxLayout()
        filter_stats_layout.setSpacing(20)
        
        self.main_window.filter_stats_label = QLabel("对象数量: 0 | 通过筛选: 0")
        self.main_window.filter_stats_label.setStyleSheet("""
            background-color: #e8f5e9; 
            padding: 8px; 
            border-radius: 5px; 
            border: 1px solid #a5d6a7;
            color: #2e7d32;
            font-weight: bold;
        """)
        self.main_window.filter_stats_label.setAlignment(Qt.AlignCenter)
        
        filter_stats_layout.addWidget(self.main_window.filter_stats_label)
        filter_preview_layout.addLayout(filter_stats_layout)
        
        # 添加键盘控制说明
        filter_keyboard_help = QLabel("键盘控制: 空格键-播放/暂停, F键-下一帧, D键-上一帧")
        filter_keyboard_help.setStyleSheet("color: #666666; font-style: italic;")
        filter_keyboard_help.setAlignment(Qt.AlignCenter)
        filter_preview_layout.addWidget(filter_keyboard_help)
        
        filter_preview_group.setLayout(filter_preview_layout)
        filter_right_layout.addWidget(filter_preview_group)
        
        return filter_right_panel
    
    def create_mask_selection_group(self):
        """创建掩膜图片序列选择组件"""
        mask_select_group = QGroupBox("掩膜图片序列选择")
        mask_select_layout = QFormLayout()
        mask_select_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        mask_select_layout.setContentsMargins(15, 20, 15, 15)
        mask_select_layout.setSpacing(15)
        mask_select_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        mask_select_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 掩膜文件夹选择
        mask_folder_layout = QHBoxLayout()
        mask_folder_layout.setSpacing(8)
        self.main_window.filter_mask_dir_edit = QLineEdit()
        self.main_window.filter_mask_dir_edit.setReadOnly(True)
        self.main_window.filter_mask_dir_edit.setPlaceholderText("选择掩膜图片文件夹...")
        self.main_window.filter_mask_dir_edit.setMinimumHeight(24)
        mask_folder_browse_btn = QPushButton("浏览")
        mask_folder_browse_btn.setIcon(QIcon.fromTheme("folder"))
        mask_folder_browse_btn.setMinimumWidth(60)
        mask_folder_browse_btn.setMaximumWidth(60)
        mask_folder_browse_btn.setMinimumHeight(24)
        mask_folder_browse_btn.clicked.connect(self.main_window.browse_filter_mask_dir)
        mask_folder_layout.addWidget(self.main_window.filter_mask_dir_edit)
        mask_folder_layout.addWidget(mask_folder_browse_btn)
        mask_select_layout.addRow("<b>掩膜文件夹:</b>", mask_folder_layout)
        
        mask_select_group.setLayout(mask_select_layout)
        return mask_select_group
    
    def create_parameter_settings_group(self):
        """创建参数设置组件"""
        param_setting_group = QGroupBox("参数设置")
        param_setting_layout = QFormLayout()
        param_setting_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        param_setting_layout.setContentsMargins(15, 20, 15, 15)
        param_setting_layout.setSpacing(15)
        param_setting_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        param_setting_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 帧率设置
        self.main_window.fps_input = QLineEdit("1.00000")
        self.main_window.fps_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,5})?')))
        self.main_window.fps_input.setMinimumHeight(24)
        param_setting_layout.addRow("<b>帧率 (FPS):</b>", self.main_window.fps_input)
        
        # 像素比例系数
        self.main_window.um_per_pixel_input = QLineEdit("1.00000")
        self.main_window.um_per_pixel_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,5})?')))
        self.main_window.um_per_pixel_input.setMinimumHeight(24)
        param_setting_layout.addRow("<b>比例系数 (</b>" + "<span style='font-family: \"Times New Roman\", Arial, sans-serif;'>μm</span>" + "<b>/pixel):</b>", self.main_window.um_per_pixel_input)
        
        param_setting_group.setLayout(param_setting_layout)
        return param_setting_group
    
    def create_exclude_objects_group(self):
        """创建排除指定对象组件"""
        exclude_group = QGroupBox("排除指定对象")
        exclude_layout = QHBoxLayout()  # 水平布局
        exclude_layout.setContentsMargins(15, 20, 15, 15)
        exclude_layout.setSpacing(10)
        
        # 创建标签并添加到布局
        exclude_label = QLabel("<b>排除对象ID:</b>")
        exclude_label.setMinimumWidth(75)
        exclude_layout.addWidget(exclude_label)
        
        # 创建输入框并添加到布局
        self.main_window.exclude_ids_input = QLineEdit()
        self.main_window.exclude_ids_input.setPlaceholderText("输入要排除的对象ID，用逗号分隔，如: 1,2,3")
        self.main_window.exclude_ids_input.setMinimumHeight(24)
        exclude_layout.addWidget(self.main_window.exclude_ids_input)
        
        exclude_group.setLayout(exclude_layout)
        return exclude_group
    
    def create_filter_progress_group(self):
        """创建筛选处理进度组件"""
        filter_progress_group = QGroupBox("筛选处理进度")
        filter_progress_layout = QVBoxLayout()
        filter_progress_layout.setContentsMargins(10, 15, 10, 15)
        filter_progress_layout.setSpacing(10)
        
        # 筛选处理日志文本区域
        self.main_window.filter_log_text = QTextEdit()
        self.main_window.filter_log_text.setReadOnly(True)
        self.main_window.filter_log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.main_window.filter_log_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_window.filter_log_text.setStyleSheet("""
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
        # 移除最小/最大高度限制，让日志区域自由扩展
        filter_progress_layout.addWidget(self.main_window.filter_log_text, 1)  # 添加伸缩因子1
        
        # 筛选进度条（使用和主界面相同的进度条样式）
        self.main_window.filter_progress_bar = QProgressBar()
        self.main_window.filter_progress_bar.setRange(0, 100)
        self.main_window.filter_progress_bar.setValue(0)
        self.main_window.filter_progress_bar.setTextVisible(True)
        self.main_window.filter_progress_bar.setFormat("%p% (%v/%m)")
        self.main_window.filter_progress_bar.setStyleSheet("""
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
        self.main_window.filter_progress_bar.setVisible(False)  # 默认隐藏进度条
        filter_progress_layout.addWidget(self.main_window.filter_progress_bar)
        
        # 添加一个函数来确保滚动条正确显示
        def ensure_filter_scrollbars_visible():
            # 添加一些测试文本确保滚动条初始化正确
            for i in range(20):
                self.main_window.filter_log_text.append(f"初始化日志行 {i+1}")
            
            # 强制更新UI并滚动到顶部
            QApplication.processEvents()
            self.main_window.filter_log_text.clear()
            QApplication.processEvents()
        
        # 在UI初始化完成后调用此函数
        QTimer.singleShot(100, ensure_filter_scrollbars_visible)
        
        filter_progress_group.setLayout(filter_progress_layout)
        # 设置筛选处理进度区域为可扩展的
        filter_progress_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        return filter_progress_group 