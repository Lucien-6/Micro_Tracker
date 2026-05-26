"""
Phase 2: 标注管理器组件

提供标注列表、跳转、删除、导入导出等功能

Author: Lucien (lucien-6@qq.com)
Date: 2026-01-28
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QLabel,
                             QMessageBox, QFileDialog, QDialog, QTextBrowser, 
                             QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from pathlib import Path
import json
import os
import webbrowser
from micro_tracker.components.custom_widgets import RippleButton


def validate_annotation_data(import_data, video_width=None, video_height=None):
    """
    验证导入的标注数据格式和内容
    
    Args:
        import_data (dict): 导入的JSON数据
        video_width (int, optional): 视频宽度，用于验证坐标范围
        video_height (int, optional): 视频高度，用于验证坐标范围
    
    Returns:
        tuple: (bool, str) - (是否有效, 错误信息)
    
    Raises:
        ValueError: 数据格式或内容不符合要求时抛出异常
    """
    # 1. 验证基本结构
    if not isinstance(import_data, dict):
        return False, "导入的数据必须是字典格式"
    
    if "annotations" not in import_data:
        return False, "缺少 'annotations' 字段"
    
    annotations = import_data["annotations"]
    if not isinstance(annotations, dict):
        return False, "'annotations' 必须是字典格式"
    
    # 2. 检查是否为空
    if len(annotations) == 0:
        return False, "标注数据为空"
    
    # 3. 验证格式类型
    format_type = import_data.get("format", "legacy")
    if format_type not in ["refinement", "legacy"]:
        return False, f"不支持的格式类型: {format_type}"
    
    is_refinement_format = format_type == "refinement" or "refinement" in import_data.get("version", "")
    obj_ids_with_bbox = set()
    all_refinement_obj_ids = set()
    
    # 4. 逐帧验证
    for frame_idx_str, frame_data in annotations.items():
        # 验证帧索引
        try:
            frame_idx = int(frame_idx_str)
            if frame_idx < 0:
                return False, f"无效的帧索引: {frame_idx}（必须为非负整数）"
        except (ValueError, TypeError):
            return False, f"无效的帧索引: {frame_idx_str}（必须为整数）"
        
        # 根据格式类型验证frame_data
        if is_refinement_format:
            # 新格式: {obj_id: {"box": [...], "points": [...], "labels": [...]}}
            if not isinstance(frame_data, dict):
                return False, f"第 {frame_idx} 帧的数据格式错误（必须为字典）"
            
            for obj_id_str, prompts in frame_data.items():
                # 验证对象ID
                try:
                    obj_id = int(obj_id_str)
                    if obj_id < 0:
                        return False, f"第 {frame_idx} 帧：无效的对象ID {obj_id}（必须为非负整数）"
                except (ValueError, TypeError):
                    return False, f"第 {frame_idx} 帧：无效的对象ID {obj_id_str}（必须为整数）"
                
                if not isinstance(prompts, dict):
                    return False, f"第 {frame_idx} 帧对象 {obj_id}：提示数据格式错误（必须为字典）"
                
                # 验证box（如果存在）
                if "box" in prompts and prompts["box"] is not None:
                    box = prompts["box"]
                    if not isinstance(box, (list, tuple)) or len(box) != 4:
                        return False, f"第 {frame_idx} 帧对象 {obj_id}：边界框格式错误（必须为4个元素的列表）"
                    
                    try:
                        x1, y1, x2, y2 = map(float, box)
                        
                        # 验证坐标顺序
                        if x1 >= x2 or y1 >= y2:
                            return False, f"第 {frame_idx} 帧对象 {obj_id}：边界框坐标顺序错误 (x1={x1}, y1={y1}, x2={x2}, y2={y2})"
                        
                        # 验证坐标范围（如果提供了视频尺寸）
                        if video_width is not None and video_height is not None:
                            if x1 < 0 or y1 < 0 or x2 > video_width or y2 > video_height:
                                return False, f"第 {frame_idx} 帧对象 {obj_id}：边界框超出视频范围 ({video_width}x{video_height})"
                    
                    except (ValueError, TypeError) as e:
                        return False, f"第 {frame_idx} 帧对象 {obj_id}：边界框坐标必须为数字"
                
                # 验证points和labels（如果存在）
                if "points" in prompts and prompts["points"]:
                    points = prompts["points"]
                    if not isinstance(points, list):
                        return False, f"第 {frame_idx} 帧对象 {obj_id}：点击坐标格式错误（必须为列表）"
                    
                    for i, point in enumerate(points):
                        if not isinstance(point, (list, tuple)) or len(point) != 2:
                            return False, f"第 {frame_idx} 帧对象 {obj_id}：第 {i+1} 个点击坐标格式错误（必须为2个元素）"
                        
                        try:
                            x, y = map(float, point)
                            if video_width is not None and video_height is not None:
                                if x < 0 or y < 0 or x > video_width or y > video_height:
                                    return False, f"第 {frame_idx} 帧对象 {obj_id}：点击坐标超出视频范围"
                        except (ValueError, TypeError):
                            return False, f"第 {frame_idx} 帧对象 {obj_id}：点击坐标必须为数字"
                    
                    # 验证labels
                    if "labels" in prompts and prompts["labels"]:
                        labels = prompts["labels"]
                        if not isinstance(labels, list):
                            return False, f"第 {frame_idx} 帧对象 {obj_id}：标签格式错误（必须为列表）"
                        
                        if len(labels) != len(points):
                            return False, f"第 {frame_idx} 帧对象 {obj_id}：标签数量与点击数量不匹配"
                        
                        for i, label in enumerate(labels):
                            if label not in [0, 1]:
                                return False, f"第 {frame_idx} 帧对象 {obj_id}：第 {i+1} 个标签值无效（必须为0或1）"
                
                all_refinement_obj_ids.add(obj_id)
                has_valid_box = (
                    "box" in prompts
                    and prompts["box"] is not None
                    and isinstance(prompts["box"], (list, tuple))
                    and len(prompts["box"]) == 4
                )
                has_points = bool(prompts.get("points"))
                if has_points:
                    if "labels" not in prompts or not prompts["labels"]:
                        return False, (
                            f"第 {frame_idx} 帧对象 {obj_id}：提供点提示时必须包含等长的 labels 列表（值为 0 或 1）"
                        )
                if not has_valid_box and not has_points:
                    return False, (
                        f"第 {frame_idx} 帧对象 {obj_id}：至少需提供边界框或点提示之一"
                    )
                if has_valid_box:
                    obj_ids_with_bbox.add(obj_id)
        
        else:
            # 旧格式: [[x1, y1, x2, y2, obj_id], ...]
            if not isinstance(frame_data, list):
                return False, f"第 {frame_idx} 帧的数据格式错误（必须为列表）"
            
            for i, bbox in enumerate(frame_data):
                if not isinstance(bbox, (list, tuple)) or len(bbox) != 5:
                    return False, f"第 {frame_idx} 帧第 {i+1} 个边界框格式错误（必须为5个元素的列表）"
                
                try:
                    x1, y1, x2, y2 = map(float, bbox[:4])
                    obj_id = int(bbox[4])
                    
                    if x1 >= x2 or y1 >= y2:
                        return False, f"第 {frame_idx} 帧第 {i+1} 个边界框坐标顺序错误"
                    
                    if obj_id < 0:
                        return False, f"第 {frame_idx} 帧第 {i+1} 个边界框的对象ID无效"
                    
                    if video_width is not None and video_height is not None:
                        if x1 < 0 or y1 < 0 or x2 > video_width or y2 > video_height:
                            return False, f"第 {frame_idx} 帧第 {i+1} 个边界框超出视频范围"
                
                except (ValueError, TypeError) as e:
                    return False, f"第 {frame_idx} 帧第 {i+1} 个边界框数据类型错误"
    
    # 4b. Refinement 格式：每个对象全局至少一处有效边界框
    if is_refinement_format:
        for obj_id in all_refinement_obj_ids:
            if obj_id not in obj_ids_with_bbox:
                return False, (
                    f"对象 {obj_id} 没有任何边界框提示，不符合项目要求"
                    f"（每个对象至少需在一帧上提供边界框）"
                )
    
    # 5. 验证object_registry（如果存在）
    if "object_registry" in import_data:
        registry = import_data["object_registry"]
        if not isinstance(registry, dict):
            return False, "'object_registry' 必须是字典格式"
        
        for obj_id_str, obj_info in registry.items():
            try:
                obj_id = int(obj_id_str)
                if obj_id < 0:
                    return False, f"对象注册表中的对象ID {obj_id} 无效"
            except (ValueError, TypeError):
                return False, f"对象注册表中的对象ID {obj_id_str} 必须为整数"
            
            if not isinstance(obj_info, dict):
                return False, f"对象 {obj_id} 的注册信息格式错误"
            
            # 验证必需字段
            required_fields = ["first_frame", "frames", "color"]
            for field in required_fields:
                if field not in obj_info:
                    return False, f"对象 {obj_id} 的注册信息缺少 '{field}' 字段"
        
        if is_refinement_format:
            for obj_id_str in registry.keys():
                obj_id = int(obj_id_str)
                if obj_id not in obj_ids_with_bbox:
                    return False, (
                        f"对象注册表中的对象 {obj_id} 在标注数据中没有任何边界框"
                    )
    
    return True, "验证通过"


def _rebuild_object_registry_from_bboxes(overlay):
    """Rebuild object_registry and next_available_id from bboxes_per_frame."""
    overlay.object_registry.clear()
    for frame_idx, bbox_list in overlay.bboxes_per_frame.items():
        for bbox in bbox_list:
            obj_id = bbox[4]
            overlay.register_object(obj_id, frame_idx)
    if overlay.object_registry:
        overlay.next_available_id = max(overlay.object_registry.keys()) + 1
    else:
        overlay.next_available_id = 0


def validate_runtime_refinement_annotations(refinement_data):
    """
    Validate in-memory refinement annotations before processing.
    
    Returns:
        tuple: (bool, str) - (是否有效, 错误信息)
    """
    if not refinement_data:
        return False, "没有标注数据"
    
    all_obj_ids = set()
    obj_ids_with_bbox = set()
    
    for frame_idx, frame_data in refinement_data.items():
        for obj_id, prompts in frame_data.items():
            all_obj_ids.add(obj_id)
            
            has_valid_box = (
                isinstance(prompts, dict)
                and prompts.get("box") is not None
                and isinstance(prompts.get("box"), (list, tuple))
                and len(prompts["box"]) == 4
            )
            if has_valid_box:
                obj_ids_with_bbox.add(obj_id)
            
            points = prompts.get("points") if isinstance(prompts, dict) else None
            if points:
                labels = prompts.get("labels")
                if not labels:
                    return False, (
                        f"第 {frame_idx} 帧对象 {obj_id}：提供点提示时必须包含等长的 labels 列表（值为 0 或 1）"
                    )
                if not isinstance(labels, list) or len(labels) != len(points):
                    return False, (
                        f"第 {frame_idx} 帧对象 {obj_id}：提供点提示时必须包含等长的 labels 列表（值为 0 或 1）"
                    )
                for i, label in enumerate(labels):
                    if label not in [0, 1]:
                        return False, (
                            f"第 {frame_idx} 帧对象 {obj_id}：第 {i+1} 个标签值无效（必须为0或1）"
                        )
    
    for obj_id in all_obj_ids:
        if obj_id not in obj_ids_with_bbox:
            return False, (
                f"对象 {obj_id} 没有任何边界框提示，无法开始处理"
                f"（每个对象至少需在一帧上提供边界框）"
            )
    
    return True, "验证通过"


def format_user_friendly_error(exception):
    """
    将Python异常转换为用户友好的错误消息
    
    Args:
        exception: Python异常对象
    
    Returns:
        str: 用户友好的错误消息
    """
    error_type = type(exception).__name__
    error_msg = str(exception)
    
    # 常见错误的友好化处理
    if isinstance(exception, FileNotFoundError):
        return f"文件未找到：{error_msg}\n\n请检查文件路径是否正确。"
    
    elif isinstance(exception, PermissionError):
        return f"没有权限访问文件：{error_msg}\n\n请检查文件是否被其他程序占用，或者您是否有足够的权限。"
    
    elif isinstance(exception, json.JSONDecodeError):
        return f"JSON文件格式错误：\n\n文件内容不是有效的JSON格式。\n\n详细信息：第 {exception.lineno} 行，第 {exception.colno} 列\n{exception.msg}"
    
    elif isinstance(exception, ValueError):
        if "invalid literal" in error_msg:
            return f"数据格式错误：\n\n文件中包含无法识别的数字格式。\n\n请检查坐标和ID是否为有效的数字。"
        elif "too many values to unpack" in error_msg or "not enough values to unpack" in error_msg:
            return f"数据结构错误：\n\n文件中的数据格式不符合要求。\n\n请确保边界框包含4个坐标和1个ID。"
        else:
            return f"数据验证失败：\n\n{error_msg}"
    
    elif isinstance(exception, KeyError):
        return f"缺少必要字段：\n\n文件中缺少 '{error_msg}' 字段。\n\n这可能不是有效的标注文件。"
    
    elif isinstance(exception, TypeError):
        return f"数据类型错误：\n\n文件中的数据类型不正确。\n\n{error_msg}"
    
    elif isinstance(exception, MemoryError):
        return f"内存不足：\n\n标注数据太大，超出可用内存。\n\n请尝试关闭其他程序或重启应用。"
    
    elif isinstance(exception, IOError):
        return f"文件读写错误：\n\n{error_msg}\n\n请检查磁盘空间是否充足，文件是否损坏。"
    
    else:
        # 通用错误处理
        return f"操作失败：\n\n错误类型：{error_type}\n\n{error_msg}\n\n如果问题持续存在，请联系技术支持。"


class AnnotationManagerWidget(QWidget):
    """标注管理器组件"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 主布局（水平布局：表格在左，按钮在右）
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["帧号", "对象数", "提示信息", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setColumnWidth(0, 60)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 9pt;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #E1F5FE;
                color: #000;
            }
        """)
        # 移除最大高度限制，让表格自由伸展
        self.table.setMinimumHeight(160)
        main_layout.addWidget(self.table)
        
        # 右侧按钮区（垂直布局）
        button_layout = QVBoxLayout()
        button_layout.setSpacing(30)
        
        # 导入标注按钮
        self.import_btn = RippleButton("导入标注", "从JSON文件导入标注数据")
        self.import_btn.setMinimumWidth(80)
        self.import_btn.setMinimumHeight(35)
        self.import_btn.setStyleSheet("QPushButton { margin-top: 15px; }")
        self.import_btn.clicked.connect(self.import_annotations)
        button_layout.addWidget(self.import_btn)
        
        # 清空所有按钮
        self.clear_all_btn = RippleButton("清空所有", "清空所有帧的标注（不可撤销）")
        self.clear_all_btn.setMinimumWidth(80)
        self.clear_all_btn.setMinimumHeight(35)
        self.clear_all_btn.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; }
            QPushButton:disabled { background-color: #cccccc; color: #888888; }
        """)
        self.clear_all_btn.clicked.connect(self.clear_all_annotations)
        button_layout.addWidget(self.clear_all_btn)
        
        # 使用指南按钮
        self.help_btn = RippleButton("使用指南", "打开完整的使用指南（浏览器）")
        self.help_btn.setMinimumWidth(80)
        self.help_btn.setMinimumHeight(35)
        self.help_btn.clicked.connect(self.open_user_guide)
        button_layout.addWidget(self.help_btn)
        
        # 添加弹簧，将按钮推到顶部
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def refresh_table(self):
        """刷新表格数据（支持纯点击标注显示）"""
        if not hasattr(self.main_window, 'video_label') or not self.main_window.video_label:
            return
        
        overlay = self.main_window.video_label.overlay_layer
        current_frame = overlay.current_frame_idx
        
        # 清空表格
        self.table.setRowCount(0)
        
        # === 改进：合并bbox标注和refinement标注 ===
        bbox_annotations = overlay.get_all_annotations()  # {frame_idx: [[x1,y1,x2,y2,id], ...]}
        refinement_data = overlay.get_refinement_annotations() if hasattr(overlay, 'get_refinement_annotations') else {}
        
        # 收集所有有标注的帧（包括纯点击标注）
        all_frames = set()
        if bbox_annotations:
            all_frames.update(bbox_annotations.keys())
        if refinement_data:
            all_frames.update(refinement_data.keys())
        
        if not all_frames:
            return
        
        # 填充数据
        for frame_idx in sorted(all_frames):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 帧号（当前帧高亮）
            frame_item = QTableWidgetItem(f"{frame_idx}")
            if frame_idx == current_frame:
                frame_item.setBackground(QColor(255, 235, 59, 100))  # 黄色高亮
            frame_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, frame_item)
            
            # === 统计对象数（合并bbox和refinement） ===
            obj_ids = set()
            
            # 从bbox收集对象ID
            if frame_idx in bbox_annotations:
                for bbox in bbox_annotations[frame_idx]:
                    obj_ids.add(bbox[4])
            
            # 从refinement收集对象ID
            if frame_idx in refinement_data:
                obj_ids.update(refinement_data[frame_idx].keys())
            
            count_item = QTableWidgetItem(f"{len(obj_ids)}")
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, count_item)
            
            # 提示信息（改进版，使用HTML格式支持颜色）
            prompt_info_html = []
            if frame_idx in refinement_data:
                for obj_id, prompts in refinement_data[frame_idx].items():
                    # 构建单个对象的提示描述
                    obj_prompt_parts = []
                    
                    # 检查边界框（使用空心方块符号）
                    has_box = prompts.get("box") is not None and prompts.get("box")
                    if has_box:
                        obj_prompt_parts.append('<span style="font-size: 12pt;">□</span>')
                    
                    # 检查点击（使用emoji符号，格式：🟢×3）
                    if prompts.get("points"):
                        num_pos = sum(1 for l in prompts.get("labels", []) if l == 1)
                        num_neg = sum(1 for l in prompts.get("labels", []) if l == 0)
                        
                        if num_pos > 0:
                            obj_prompt_parts.append(f'<span style="font-size: 11pt; font-weight: bold;">🟢×{num_pos}</span>')
                        if num_neg > 0:
                            obj_prompt_parts.append(f'<span style="font-size: 11pt; font-weight: bold;">🔴×{num_neg}</span>')
                    
                    # 如果该对象有任何提示，添加到列表
                    if obj_prompt_parts:
                        prompt_info_html.append(f"Obj_{obj_id}: {' + '.join(obj_prompt_parts)}")
                    else:
                        prompt_info_html.append(f"Obj_{obj_id}: ⚠️无提示")
            
            # 显示提示信息（使用QLabel支持HTML格式）
            if prompt_info_html:
                prompt_html = " | ".join(prompt_info_html)
            else:
                prompt_html = "⚠️无提示数据"
            
            # 创建QLabel作为cell widget以支持HTML富文本（启用自动换行）
            prompt_label = QLabel(prompt_html)
            prompt_label.setTextFormat(Qt.RichText)
            prompt_label.setWordWrap(True)  # 启用自动换行
            prompt_label.setStyleSheet("padding: 2px 5px;")
            self.table.setCellWidget(row, 2, prompt_label)
            
            # 操作按钮（上下布局）
            action_widget = QWidget()
            action_layout = QVBoxLayout()
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(3)
            
            jump_btn = RippleButton("跳转", f"快速跳转到第{frame_idx}帧")
            jump_btn.setMaximumWidth(50)
            jump_btn.setMinimumHeight(22)
            jump_btn.clicked.connect(lambda checked, f=frame_idx: self.jump_to_frame(f))
            
            delete_btn = RippleButton("删除", "删除该帧的所有标注；若含某对象最后一处边界框，将同步删除其全部点提示（不可撤销）")
            delete_btn.setMaximumWidth(50)
            delete_btn.setMinimumHeight(22)
            delete_btn.setStyleSheet("""
                QPushButton { background-color: #ff5252; color: white; }
                QPushButton:disabled { background-color: #cccccc; color: #888888; }
            """)
            delete_btn.clicked.connect(lambda checked, f=frame_idx: self.delete_frame_annotation(f))
            
            action_layout.addWidget(jump_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)
            
            self.table.setCellWidget(row, 3, action_widget)
        
        # 自动调整所有行的高度以适应多行内容
        for row in range(self.table.rowCount()):
            self.table.resizeRowToContents(row)
    
    def jump_to_frame(self, frame_idx):
        """跳转到指定帧"""
        self.main_window.set_frame_index(frame_idx)
        self.main_window.log_message(f"跳转到第 {frame_idx} 帧", "info")
        self.refresh_table()  # 刷新高亮
    
    def delete_frame_annotation(self, frame_idx):
        """删除指定帧的所有标注"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除第 {frame_idx} 帧的所有标注吗？\n"
            f"若该帧包含某对象的最后一处边界框，将同步删除该对象在所有帧的点提示。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            overlay = self.main_window.video_label.overlay_layer
            
            # Snapshot obj_ids on this frame before deletion
            obj_ids_on_frame = set()
            obj_ids_with_bbox_on_frame = set()
            if frame_idx in overlay.bboxes_per_frame:
                for bbox in overlay.bboxes_per_frame[frame_idx]:
                    obj_ids_on_frame.add(bbox[4])
                    obj_ids_with_bbox_on_frame.add(bbox[4])
            if frame_idx in overlay.annotations_per_frame:
                obj_ids_on_frame.update(overlay.annotations_per_frame[frame_idx].keys())
            
            # 删除该帧的边界框标注
            if frame_idx in overlay.bboxes_per_frame:
                # 更新对象注册表
                bboxes = overlay.bboxes_per_frame[frame_idx]
                for bbox in bboxes:
                    obj_id = bbox[4]
                    if obj_id in overlay.object_registry:
                        frames = overlay.object_registry[obj_id]["frames"]
                        if frame_idx in frames:
                            frames.remove(frame_idx)
                        if len(frames) == 0:
                            overlay.unregister_object(obj_id)
                
                # 删除帧的边界框标注
                del overlay.bboxes_per_frame[frame_idx]
            
            # 删除该帧的点击标注（修复：之前遗漏）
            if frame_idx in overlay.annotations_per_frame:
                del overlay.annotations_per_frame[frame_idx]
            
            # 若对象已无任意帧的边界框，级联删除其在所有帧的点提示
            obj_ids_cascaded = set()
            for obj_id in obj_ids_with_bbox_on_frame:
                has_bbox = any(
                    obj_id == bbox[4]
                    for bboxes_list in overlay.bboxes_per_frame.values()
                    for bbox in bboxes_list
                )
                if not has_bbox:
                    obj_ids_cascaded.add(obj_id)
                    for other_frame_idx in list(overlay.annotations_per_frame.keys()):
                        frame_data = overlay.annotations_per_frame[other_frame_idx]
                        if obj_id in frame_data:
                            del frame_data[obj_id]
                            if not frame_data:
                                del overlay.annotations_per_frame[other_frame_idx]
            
            # 级联移除的对象：清除临时点击
            if overlay.current_editing_obj_id in obj_ids_cascaded:
                overlay.temp_points = []
                overlay.temp_labels = []
                overlay.temp_points_frame_idx = None
                overlay.current_editing_obj_id = None
            
            # 如果是当前帧，清空显示并同步
            if frame_idx == overlay.current_frame_idx:
                overlay.bboxes = []
                # 清空当前帧的临时点击
                if overlay.temp_points_frame_idx == frame_idx:
                    overlay.temp_points = []
                    overlay.temp_labels = []
                    overlay.temp_points_frame_idx = None
                    overlay.current_editing_obj_id = None
            
            # 清除已无标注对象的轨迹、特征和预览 masks
            for obj_id in obj_ids_cascaded:
                if obj_id in overlay.tracks:
                    del overlay.tracks[obj_id]
                if obj_id in overlay.object_features:
                    del overlay.object_features[obj_id]
                if obj_id in overlay.preview_masks:
                    del overlay.preview_masks[obj_id]
            if frame_idx == overlay.current_frame_idx:
                for obj_id in obj_ids_on_frame:
                    if obj_id in overlay.preview_masks:
                        del overlay.preview_masks[obj_id]
            
            if frame_idx == overlay.current_frame_idx or obj_ids_cascaded:
                overlay.update()
            
            if obj_ids_cascaded:
                ids_str = ", ".join(str(i) for i in sorted(obj_ids_cascaded))
                self.main_window.log_message(
                    f"对象 {ids_str} 已无边界框，已同步删除其在所有帧的点提示",
                    "warning"
                )
                if hasattr(self.main_window, 'setup_tab') and self.main_window.setup_tab:
                    if hasattr(self.main_window.setup_tab, 'update_object_selector'):
                        self.main_window.setup_tab.update_object_selector()
            
            self.main_window.log_message(f"已删除第 {frame_idx} 帧的所有标注", "warning")
            self.refresh_table()
            self.main_window._update_annotation_status_display()
    
    def clear_all_annotations(self):
        """清空所有标注"""
        overlay = self.main_window.video_label.overlay_layer
        
        if hasattr(overlay, 'get_refinement_annotations'):
            annotations = overlay.get_refinement_annotations()
        else:
            annotations = overlay.get_all_annotations()
        
        if not annotations:
            QMessageBox.information(self, "提示", "没有标注需要清空")
            return
        
        reply = QMessageBox.question(
            self,
            "确认清空",
            f"确定要清空所有 {len(annotations)} 帧的标注吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 清空边界框数据
            overlay.bboxes_per_frame.clear()
            overlay.bboxes = []
            
            # 清空点击标注数据（修复：之前遗漏）
            overlay.annotations_per_frame.clear()
            overlay.temp_points = []
            overlay.temp_labels = []
            overlay.temp_points_frame_idx = None
            overlay.current_editing_obj_id = None
            
            # 清空对象注册和ID计数
            overlay.object_registry.clear()
            overlay.next_available_id = 0
            
            # === 清除所有预览masks ===
            overlay.preview_masks.clear()
            overlay.tracks.clear()
            overlay.object_features.clear()
            
            # 强制刷新当前帧显示（确保点击标注也被清除）
            current_frame = overlay.current_frame_idx
            overlay.set_current_frame(current_frame)
            
            self.main_window.log_message("已清空所有标注（包括边界框和点击标注）", "warning")
            self.refresh_table()
            self.main_window._update_annotation_status_display()
            
            if hasattr(self.main_window, 'setup_tab') and self.main_window.setup_tab:
                if hasattr(self.main_window.setup_tab, 'update_object_selector'):
                    self.main_window.setup_tab.update_object_selector()
    
    def auto_save_annotations(self, file_path):
        """
        自动保存标注到指定路径（用于开始处理前自动保存）
        
        Args:
            file_path (str): 保存路径
        
        Returns:
            tuple: (bool, str) - (是否成功, 消息)
        """
        overlay = self.main_window.video_label.overlay_layer
        
        # 获取refinement格式的数据（包含box和points）
        if hasattr(overlay, 'get_refinement_annotations'):
            refinement_data = overlay.get_refinement_annotations()
            use_refinement = True
        else:
            refinement_data = overlay.get_all_annotations()
            use_refinement = False
        
        if not refinement_data:
            return False, "没有标注数据"
        
        # 确定正确的视频路径
        if hasattr(self.main_window, 'input_source') and self.main_window.input_source:
            video_path_for_export = self.main_window.input_source.source_path
        else:
            video_path_for_export = self.main_window.video_path
        
        # 构建导出数据
        export_data = {
            "video_path": video_path_for_export,
            "annotations": refinement_data,
            "object_registry": overlay.object_registry,
            "format": "refinement" if use_refinement else "legacy",
            "version": "v2.0_refinement" if use_refinement else "phase2_v1.0"
        }
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True, f"标注已自动保存到: {file_path}"
        
        except Exception as e:
            return False, f"保存失败: {str(e)}"
    
    def import_annotations(self):
        """从JSON文件导入标注"""
        # 选择文件
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入标注",
            "",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # === 数据验证 ===
            # 获取视频尺寸用于坐标范围验证
            video_width = None
            video_height = None
            if hasattr(self.main_window, 'video_label') and self.main_window.video_label:
                video_width, video_height = self.main_window.video_label.overlay_layer.frame_size
            
            # 调用验证函数
            is_valid, error_msg = validate_annotation_data(import_data, video_width, video_height)
            if not is_valid:
                self.main_window.log_message(f"数据验证失败: {error_msg}", "error")
                QMessageBox.critical(self, "数据验证失败", f"导入的标注文件存在问题：\n\n{error_msg}\n\n请检查文件格式是否正确。")
                return
            else:
                self.main_window.log_message("✓ 数据验证通过", "success")
            
            # 确认导入
            reply = QMessageBox.question(
                self,
                "确认导入",
                f"即将导入 {len(import_data['annotations'])} 帧的标注\n"
                "这将覆盖当前所有标注，是否继续？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # 导入
            overlay = self.main_window.video_label.overlay_layer
            
            overlay.tracks.clear()
            overlay.object_features.clear()
            
            # 检测格式
            format_type = import_data.get("format", "legacy")
            version = import_data.get("version", "")
            
            if format_type == "refinement" or "refinement" in version:
                # 新格式：直接导入到annotations_per_frame（确保obj_id为整数）
                annotations = {}
                for frame_idx_str, frame_data in import_data["annotations"].items():
                    frame_idx = int(frame_idx_str)
                    annotations[frame_idx] = {}
                    for obj_id_str, prompts in frame_data.items():
                        obj_id = int(obj_id_str)  # 确保对象ID为整数
                        annotations[frame_idx][obj_id] = prompts
                overlay.annotations_per_frame = annotations
                
                # 从 refinement 数据提取 bbox 到旧格式（以保持兼容性）
                bbox_data = {}
                for frame_idx, frame_data in annotations.items():
                    bbox_list = []
                    for obj_id, prompts in frame_data.items():
                        if isinstance(prompts, dict) and prompts.get("box"):
                            box = prompts["box"]
                            bbox_list.append([box[0], box[1], box[2], box[3], obj_id])
                    if bbox_list:
                        bbox_data[frame_idx] = bbox_list
                overlay.bboxes_per_frame = bbox_data
            else:
                # 旧格式
                overlay.annotations_per_frame.clear()
                annotations = {int(k): v for k, v in import_data["annotations"].items()}
                overlay.bboxes_per_frame = annotations
            
            # 导入对象注册表
            if "object_registry" in import_data:
                registry = {int(k): v for k, v in import_data["object_registry"].items()}
                overlay.object_registry = registry
                
                # 更新next_available_id
                if registry:
                    overlay.next_available_id = max(registry.keys()) + 1
            else:
                _rebuild_object_registry_from_bboxes(overlay)
            
            # === 清空所有临时状态，避免与导入数据混淆 ===
            overlay.temp_points = []
            overlay.temp_labels = []
            overlay.temp_points_frame_idx = None
            overlay.current_editing_obj_id = None
            
            # === 清除所有预览masks（因为导入的是新数据）===
            overlay.preview_masks.clear()
            
            # 刷新显示
            overlay.set_current_frame(overlay.current_frame_idx)
            self.refresh_table()
            self.main_window._update_annotation_status_display()
            
            if hasattr(self.main_window, 'setup_tab') and self.main_window.setup_tab:
                if hasattr(self.main_window.setup_tab, 'update_object_selector'):
                    self.main_window.setup_tab.update_object_selector()
            
            # Restore preview masks for the current frame after import
            self.main_window._restore_preview_for_current_frame()
            
            format_msg = "（Refinement格式）" if format_type == "refinement" else "（旧格式）"
            self.main_window.log_message(f"标注已从 {file_path} 导入 {format_msg}", "success")
            QMessageBox.information(self, "成功", f"标注导入成功！\n格式: {format_type}")
        
        except Exception as e:
            friendly_msg = format_user_friendly_error(e)
            self.main_window.log_message(f"导入失败: {str(e)}", "error")
            QMessageBox.critical(self, "导入失败", friendly_msg)
    
    def open_user_guide(self):
        """打开使用指南HTML文件（在默认浏览器中）"""
        # 获取项目根目录路径
        project_root = Path(__file__).parent.parent.parent
        
        # 构建HTML文件的绝对路径
        html_path = project_root / "docs" / "user_guide.html"
        
        # 检查文件是否存在
        if html_path.exists():
            # 转换为绝对路径字符串并使用file://协议
            file_url = html_path.absolute().as_uri()
            
            # 在默认浏览器中打开
            try:
                webbrowser.open(file_url)
                self.main_window.log_message(f"已在浏览器中打开使用指南: {html_path}", "info")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "打开失败",
                    f"无法在浏览器中打开使用指南：\n\n{str(e)}"
                )
                self.main_window.log_message(f"打开使用指南失败: {str(e)}", "error")
        else:
            # 文件不存在，显示错误对话框
            QMessageBox.critical(
                self,
                "文件未找到",
                f"使用指南文件不存在：\n\n{html_path}\n\n请确保文件位于正确的位置。"
            )
            self.main_window.log_message(f"使用指南文件未找到: {html_path}", "error")

