from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
                             QLineEdit, QGroupBox)
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp

class FilterConditionsGroup:
    """筛选条件组组件类"""
    
    def __init__(self, main_window):
        """
        初始化筛选条件组
        
        Args:
            main_window: 主窗口引用
        """
        self.main_window = main_window
        
    def create_group(self):
        """创建筛选条件组组件"""
        filter_conditions_group = QGroupBox("筛选条件")
        filter_conditions_layout = QVBoxLayout()
        filter_conditions_layout.setContentsMargins(15, 20, 15, 15)
        filter_conditions_layout.setSpacing(15)
        
        # 3.1 面积区间
        area_filter_layout = self.create_area_filter_layout()
        filter_conditions_layout.addLayout(area_filter_layout)
        
        # 3.2 面积变化率阈值
        area_change_filter_layout = self.create_area_change_filter_layout()
        filter_conditions_layout.addLayout(area_change_filter_layout)
        
        # 3.3 瞬时速度区间
        velocity_filter_layout = self.create_velocity_filter_layout()
        filter_conditions_layout.addLayout(velocity_filter_layout)
        
        # 3.4 总位移区间
        displacement_filter_layout = self.create_displacement_filter_layout()
        filter_conditions_layout.addLayout(displacement_filter_layout)
        
        # 3.5 边界截断排除
        boundary_filter_layout = self.create_boundary_filter_layout()
        filter_conditions_layout.addLayout(boundary_filter_layout)
        
        # 3.6 相互最短距离阈值
        min_distance_filter_layout = self.create_min_distance_filter_layout()
        filter_conditions_layout.addLayout(min_distance_filter_layout)
        
        filter_conditions_group.setLayout(filter_conditions_layout)
        return filter_conditions_group
    
    def create_area_filter_layout(self):
        """创建面积区间筛选布局"""
        area_filter_layout = QHBoxLayout()
        area_filter_layout.setSpacing(10)
        
        area_filter_layout.addWidget(QLabel("面积区间:"))
        
        self.main_window.area_filter_check = QCheckBox("启用")
        self.main_window.area_filter_check.setMinimumHeight(24)
        
        area_range_layout = QHBoxLayout()
        area_range_layout.setSpacing(5)
        self.main_window.area_min_input = QLineEdit("0")
        self.main_window.area_min_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.main_window.area_min_input.setMinimumHeight(24)
        self.main_window.area_min_input.setFixedWidth(80)
        
        area_range_label = QLabel("至")
        
        self.main_window.area_max_input = QLineEdit("999999")
        self.main_window.area_max_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.main_window.area_max_input.setMinimumHeight(24)
        self.main_window.area_max_input.setFixedWidth(80)
        
        area_unit_label = self.main_window.create_unit_label("μm²")
        
        area_range_layout.addWidget(self.main_window.area_min_input)
        area_range_layout.addWidget(area_range_label)
        area_range_layout.addWidget(self.main_window.area_max_input)
        area_range_layout.addWidget(area_unit_label)
        
        area_filter_layout.addWidget(self.main_window.area_filter_check)
        area_filter_layout.addLayout(area_range_layout)
        area_filter_layout.addStretch(1)
        
        return area_filter_layout
    
    def create_area_change_filter_layout(self):
        """创建面积变化率阈值筛选布局"""
        area_change_filter_layout = QHBoxLayout()
        area_change_filter_layout.setSpacing(10)
        
        area_change_filter_layout.addWidget(QLabel("面积变化率阈值:"))
        
        self.main_window.area_change_check = QCheckBox("启用")
        self.main_window.area_change_check.setMinimumHeight(24)
        
        area_change_threshold_layout = QHBoxLayout()
        area_change_threshold_layout.setSpacing(5)
        self.main_window.area_change_input = QLineEdit("0.5")
        self.main_window.area_change_input.setValidator(QRegExpValidator(QRegExp(r'0(\.[0-9]{0,2})?|1(\.0{0,2})?')))
        self.main_window.area_change_input.setMinimumHeight(24)
        self.main_window.area_change_input.setFixedWidth(80)
        
        area_change_unit_label = self.main_window.create_unit_label("比例值(0~1)")
        
        area_change_threshold_layout.addWidget(self.main_window.area_change_input)
        area_change_threshold_layout.addWidget(area_change_unit_label)
        
        area_change_filter_layout.addWidget(self.main_window.area_change_check)
        area_change_filter_layout.addLayout(area_change_threshold_layout)
        area_change_filter_layout.addStretch(1)
        
        return area_change_filter_layout
    
    def create_velocity_filter_layout(self):
        """创建瞬时速度区间筛选布局"""
        velocity_filter_layout = QHBoxLayout()
        velocity_filter_layout.setSpacing(10)
        
        velocity_filter_layout.addWidget(QLabel("瞬时速度区间:"))
        
        self.main_window.velocity_check = QCheckBox("启用")
        self.main_window.velocity_check.setMinimumHeight(24)
        
        velocity_range_layout = QHBoxLayout()
        velocity_range_layout.setSpacing(5)
        self.main_window.velocity_min_input = QLineEdit("0")
        self.main_window.velocity_min_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.main_window.velocity_min_input.setMinimumHeight(24)
        self.main_window.velocity_min_input.setFixedWidth(80)
        
        velocity_range_label = QLabel("至")
        
        self.main_window.velocity_max_input = QLineEdit("999999")
        self.main_window.velocity_max_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.main_window.velocity_max_input.setMinimumHeight(24)
        self.main_window.velocity_max_input.setFixedWidth(80)
        
        velocity_unit_label = self.main_window.create_unit_label("μm/s")
        
        velocity_range_layout.addWidget(self.main_window.velocity_min_input)
        velocity_range_layout.addWidget(velocity_range_label)
        velocity_range_layout.addWidget(self.main_window.velocity_max_input)
        velocity_range_layout.addWidget(velocity_unit_label)
        
        velocity_filter_layout.addWidget(self.main_window.velocity_check)
        velocity_filter_layout.addLayout(velocity_range_layout)
        velocity_filter_layout.addStretch(1)
        
        return velocity_filter_layout
    
    def create_displacement_filter_layout(self):
        """创建总位移区间筛选布局"""
        displacement_filter_layout = QHBoxLayout()
        displacement_filter_layout.setSpacing(10)
        
        displacement_filter_layout.addWidget(QLabel("总位移区间:"))
        
        self.main_window.displacement_check = QCheckBox("启用")
        self.main_window.displacement_check.setMinimumHeight(24)
        
        displacement_range_layout = QHBoxLayout()
        displacement_range_layout.setSpacing(5)
        self.main_window.displacement_min_input = QLineEdit("0")
        self.main_window.displacement_min_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.main_window.displacement_min_input.setMinimumHeight(24)
        self.main_window.displacement_min_input.setFixedWidth(80)
        
        displacement_range_label = QLabel("至")
        
        self.main_window.displacement_max_input = QLineEdit("999999")
        self.main_window.displacement_max_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.main_window.displacement_max_input.setMinimumHeight(24)
        self.main_window.displacement_max_input.setFixedWidth(80)
        
        displacement_unit_label = self.main_window.create_unit_label("μm")
        
        displacement_range_layout.addWidget(self.main_window.displacement_min_input)
        displacement_range_layout.addWidget(displacement_range_label)
        displacement_range_layout.addWidget(self.main_window.displacement_max_input)
        displacement_range_layout.addWidget(displacement_unit_label)
        
        displacement_filter_layout.addWidget(self.main_window.displacement_check)
        displacement_filter_layout.addLayout(displacement_range_layout)
        displacement_filter_layout.addStretch(1)
        
        return displacement_filter_layout
    
    def create_boundary_filter_layout(self):
        """创建边界截断排除筛选布局"""
        boundary_filter_layout = QHBoxLayout()
        boundary_filter_layout.setSpacing(10)
        
        boundary_filter_layout.addWidget(QLabel("边界截断排除:"))
        
        self.main_window.boundary_check = QCheckBox("启用边界截断排除")
        self.main_window.boundary_check.setMinimumHeight(24)
        
        boundary_filter_layout.addWidget(self.main_window.boundary_check)
        boundary_filter_layout.addStretch(1)
        
        return boundary_filter_layout
    
    def create_min_distance_filter_layout(self):
        """创建相互最短距离阈值筛选布局"""
        min_distance_filter_layout = QHBoxLayout()
        min_distance_filter_layout.setSpacing(10)
        
        min_distance_filter_layout.addWidget(QLabel("相互最短距离阈值:"))
        
        self.main_window.min_distance_check = QCheckBox("启用")
        self.main_window.min_distance_check.setMinimumHeight(24)
        
        min_distance_threshold_layout = QHBoxLayout()
        min_distance_threshold_layout.setSpacing(5)
        self.main_window.min_distance_input = QLineEdit("10")
        self.main_window.min_distance_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.main_window.min_distance_input.setMinimumHeight(24)
        self.main_window.min_distance_input.setFixedWidth(80)
        
        min_distance_unit_label = self.main_window.create_unit_label("μm")
        
        min_distance_threshold_layout.addWidget(self.main_window.min_distance_input)
        min_distance_threshold_layout.addWidget(min_distance_unit_label)
        
        min_distance_filter_layout.addWidget(self.main_window.min_distance_check)
        min_distance_filter_layout.addLayout(min_distance_threshold_layout)
        min_distance_filter_layout.addStretch(1)
        
        return min_distance_filter_layout 