"""
Phase 2: 标注管理器组件

提供标注列表、跳转、删除、导入导出等功能

Author: Lucien (lucien-6@qq.com)
Date: 2025-10-30
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QLabel,
                             QMessageBox, QFileDialog, QDialog, QTextBrowser, 
                             QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from pathlib import Path
import json


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
        if format_type == "refinement" or "refinement" in import_data.get("version", ""):
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
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
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
                background-color: #E3F2FD;
                color: #000;
            }
        """)
        self.table.setMaximumHeight(200)
        layout.addWidget(self.table)
        
        # 按钮区
        button_layout = QHBoxLayout()
        
        self.help_btn = QPushButton("操作说明")
        self.help_btn.setToolTip("查看详细的操作说明")
        self.help_btn.clicked.connect(self.show_help_dialog)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setToolTip("刷新标注列表")
        self.refresh_btn.clicked.connect(self.refresh_table)
        
        self.export_btn = QPushButton("导出")
        self.export_btn.setToolTip("导出标注为JSON文件")
        self.export_btn.clicked.connect(self.export_annotations)
        
        self.import_btn = QPushButton("导入")
        self.import_btn.setToolTip("从JSON文件导入标注")
        self.import_btn.clicked.connect(self.import_annotations)
        
        self.clear_all_btn = QPushButton("清空")
        self.clear_all_btn.setToolTip("清空所有标注")
        self.clear_all_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.clear_all_btn.clicked.connect(self.clear_all_annotations)
        
        button_layout.addWidget(self.help_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_all_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
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
                    
                    # 检查边界框（使用黑色方块符号）
                    has_box = prompts.get("box") is not None and prompts.get("box")
                    if has_box:
                        obj_prompt_parts.append('<span style="font-size: 12pt;">⬛️</span>')
                    
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
                        prompt_info_html.append(f"obj{obj_id}: {' + '.join(obj_prompt_parts)}")
                    else:
                        prompt_info_html.append(f"obj{obj_id}: ⚠️无提示")
            
            # 显示提示信息（使用QLabel支持HTML格式）
            if prompt_info_html:
                prompt_html = " | ".join(prompt_info_html)
            else:
                prompt_html = "⚠️无提示数据"
            
            # 创建QLabel作为cell widget以支持HTML富文本
            prompt_label = QLabel(prompt_html)
            prompt_label.setTextFormat(Qt.RichText)
            prompt_label.setStyleSheet("padding: 2px 5px;")
            self.table.setCellWidget(row, 2, prompt_label)
            
            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(4)
            
            jump_btn = QPushButton("跳转")
            jump_btn.setMaximumWidth(50)
            jump_btn.clicked.connect(lambda checked, f=frame_idx: self.jump_to_frame(f))
            
            delete_btn = QPushButton("删除")
            delete_btn.setMaximumWidth(50)
            delete_btn.setStyleSheet("background-color: #ff5252; color: white;")
            delete_btn.clicked.connect(lambda checked, f=frame_idx: self.delete_frame_annotation(f))
            
            action_layout.addWidget(jump_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)
            
            self.table.setCellWidget(row, 3, action_widget)
    
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
            f"确定要删除第 {frame_idx} 帧的所有标注吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            overlay = self.main_window.video_label.overlay_layer
            
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
            
            # 如果是当前帧，清空显示并同步
            if frame_idx == overlay.current_frame_idx:
                overlay.bboxes = []
                # 清空当前帧的临时点击
                if overlay.temp_points_frame_idx == frame_idx:
                    overlay.temp_points = []
                    overlay.temp_labels = []
                    overlay.temp_points_frame_idx = None
                    overlay.current_editing_obj_id = None
                
                # === 清除该帧所有对象的预览masks ===
                if frame_idx in overlay.bboxes_per_frame or bboxes:
                    for bbox in bboxes:
                        obj_id = bbox[4]
                        if obj_id in overlay.preview_masks:
                            del overlay.preview_masks[obj_id]
                
                overlay.update()
            
            self.main_window.log_message(f"已删除第 {frame_idx} 帧的所有标注", "warning")
            self.refresh_table()
            self.main_window._update_annotation_status_display()
    
    def clear_all_annotations(self):
        """清空所有标注"""
        overlay = self.main_window.video_label.overlay_layer
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
            
            # 强制刷新当前帧显示（确保点击标注也被清除）
            current_frame = overlay.current_frame_idx
            overlay.set_current_frame(current_frame)
            
            self.main_window.log_message("已清空所有标注（包括边界框和点击标注）", "warning")
            self.refresh_table()
            self.main_window._update_annotation_status_display()
    
    def export_annotations(self):
        """导出标注为JSON文件"""
        overlay = self.main_window.video_label.overlay_layer
        
        # 获取refinement格式的数据（包含box和points）
        if hasattr(overlay, 'get_refinement_annotations'):
            refinement_data = overlay.get_refinement_annotations()
            use_refinement = True
        else:
            refinement_data = overlay.get_all_annotations()
            use_refinement = False
        
        if not refinement_data:
            QMessageBox.information(self, "提示", "没有标注可以导出")
            return
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出标注",
            f"{Path(self.main_window.video_path).stem}_annotations.json" if self.main_window.video_path else "annotations.json",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        # 构建导出数据
        export_data = {
            "video_path": self.main_window.video_path,
            "annotations": refinement_data,
            "object_registry": overlay.object_registry,
            "format": "refinement" if use_refinement else "legacy",
            "version": "v2.0_refinement" if use_refinement else "phase2_v1.0"
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.main_window.log_message(f"标注已导出到: {file_path}", "success")
            QMessageBox.information(self, "成功", f"标注已导出!\n{file_path}")
        
        except Exception as e:
            friendly_msg = format_user_friendly_error(e)
            self.main_window.log_message(f"导出失败: {str(e)}", "error")
            QMessageBox.critical(self, "导出失败", friendly_msg)
    
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
            
            # 检测格式
            format_type = import_data.get("format", "legacy")
            version = import_data.get("version", "")
            
            if format_type == "refinement" or "refinement" in version:
                # 新格式：直接导入到annotations_per_frame
                annotations = {int(k): v for k, v in import_data["annotations"].items()}
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
                annotations = {int(k): v for k, v in import_data["annotations"].items()}
                overlay.bboxes_per_frame = annotations
            
            # 导入对象注册表
            if "object_registry" in import_data:
                registry = {int(k): v for k, v in import_data["object_registry"].items()}
                overlay.object_registry = registry
                
                # 更新next_available_id
                if registry:
                    overlay.next_available_id = max(registry.keys()) + 1
            
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
            
            format_msg = "（Refinement格式）" if format_type == "refinement" else "（旧格式）"
            self.main_window.log_message(f"标注已从 {file_path} 导入 {format_msg}", "success")
            QMessageBox.information(self, "成功", f"标注导入成功！\n格式: {format_type}")
        
        except Exception as e:
            friendly_msg = format_user_friendly_error(e)
            self.main_window.log_message(f"导入失败: {str(e)}", "error")
            QMessageBox.critical(self, "导入失败", friendly_msg)
    
    def show_help_dialog(self):
        """显示操作说明弹窗（带滚动条的增强版）"""
        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("📖 标注操作详细说明")
        dialog.setMinimumSize(700, 600)  # 设置合适的对话框大小
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建文本浏览器（支持滚动和富文本）
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(False)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
                font-size: 10pt;
            }
        """)
        
        # 帮助文本（使用HTML格式以获得更好的排版）
        help_html = """
        <style>
            h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; margin-top: 15px; }
            h3 { color: #4CAF50; margin-top: 12px; margin-bottom: 5px; }
            ul { margin-left: 20px; }
            li { margin-bottom: 4px; }
            .emoji { font-size: 14pt; }
            .note { background-color: #FFF9C4; padding: 8px; border-left: 4px solid #FFC107; margin: 8px 0; }
            .warning { background-color: #FFEBEE; padding: 8px; border-left: 4px solid #F44336; margin: 8px 0; }
            .success { background-color: #E8F5E9; padding: 8px; border-left: 4px solid #4CAF50; margin: 8px 0; }
            kbd { background-color: #f4f4f4; border: 1px solid #ccc; border-radius: 3px; padding: 2px 6px; font-family: monospace; }
        </style>
        
        <h2><span class="emoji">📌</span> 一、标注模式</h2>
        
        <h3><span class="emoji">🆕</span> 新对象模式（New Object）</h3>
        <ul>
            <li>用于首次标注一个新的对象</li>
            <li>系统自动分配唯一ID和固定颜色</li>
            <li>通常在第0帧标注对象首次出现的位置</li>
        </ul>
        
        <h3><span class="emoji">✏️</span> 修正对象模式（Refine Object）</h3>
        <ul>
            <li>用于在关键帧补充已有对象的标注</li>
            <li>需要先从下拉框选择要修正的对象ID</li>
            <li>正在修正的对象会以金色虚线高亮显示</li>
            <li><b>⚠️ 重要：</b>修正模式下<b style="color: #F44336;">只能使用点击提示</b>，不能绘制边界框
                <ul>
                    <li>符合SAM2官方最佳实践规范</li>
                    <li>切换到修正模式时会自动切换到点击模式</li>
                    <li>边界框选项会被禁用</li>
                </ul>
            </li>
            <li><b>适用场景：</b>
                <ul>
                    <li>对象形状显著变化</li>
                    <li>对象被遮挡前后</li>
                    <li>对象运动方向改变</li>
                </ul>
            </li>
        </ul>
        
        <h2><span class="emoji">🎯</span> 二、提示类型</h2>
        
        <h3><span class="emoji">▢</span> 边界框模式（Box）</h3>
        <ul>
            <li>按住鼠标左键拖动绘制矩形框</li>
            <li>框选对象的完整轮廓</li>
            <li>松开鼠标后自动生成实时预览</li>
        </ul>
        
        <h3><span class="emoji">👆</span> 点击模式（Point）</h3>
        <ul>
            <li>左键点击：添加正向区域（<span style="color: #4CAF50; font-weight: bold;">➕绿色标记</span>）</li>
            <li>右键点击：添加负向区域（<span style="color: #F44336; font-weight: bold;">➖红色标记</span>）</li>
            <li>可以添加多个点击来精细化分割</li>
            <li>点击后即时生成预览，可立即验证效果</li>
            <li>按 <kbd>A</kbd> 键保存临时点击</li>
            <li>按 <kbd>Ctrl+C</kbd> 清除临时点击</li>
        </ul>
        
        <h2><span class="emoji">🎬</span> 三、视频浏览</h2>
        <ul>
            <li><b>滑块：</b>拖动滑块快速跳转到任意帧</li>
            <li><b>快捷键：</b>
                <ul>
                    <li><kbd>空格</kbd> - 播放/暂停</li>
                    <li><kbd>F</kbd> - 下一帧</li>
                    <li><kbd>D</kbd> - 上一帧</li>
                </ul>
            </li>
        </ul>
        <div class="note">💡 提示：使用快捷键可以更精确地定位关键帧</div>
        
        <h2><span class="emoji">⌨️</span> 四、键盘快捷键</h2>
        
        <h3>基本操作</h3>
        <ul>
            <li><kbd>空格</kbd> - 播放/暂停</li>
            <li><kbd>F</kbd> - 下一帧</li>
            <li><kbd>D</kbd> - 上一帧</li>
        </ul>
        
        <h3>标注编辑</h3>
        <ul>
            <li><kbd>Del</kbd> - 删除选中的边界框</li>
            <li><kbd>A</kbd> - 应用并保存临时点击</li>
            <li><kbd>Ctrl+C</kbd> - 清除临时点击</li>
            <li><kbd>Ctrl+S</kbd> - 保存点击并切换到下一帧 <span style="color: #FF5722;">（新增）</span></li>
        </ul>
        
        <h3>标注管理</h3>
        <ul>
            <li>使用表格中的"跳转"按钮快速切换到标注帧</li>
            <li>使用"删除"按钮移除不需要的标注</li>
        </ul>
        
        <h2><span class="emoji">👁️</span> 五、实时预览功能</h2>
        <div class="success">
            <b>✨ 添加标注后自动生成mask预览</b>
            <ul>
                <li>可以立即验证标注质量</li>
                <li>半透明彩色蒙版显示分割结果</li>
                <li>预览使用对象的固定颜色</li>
                <li>如果预览效果不理想，可以添加更多点击来优化</li>
            </ul>
        </div>
        
        <h2><span class="emoji">📋</span> 六、标注管理</h2>
        
        <h3>查看与管理</h3>
        <ul>
            <li><b>刷新：</b>更新标注列表显示</li>
            <li><b>跳转：</b>快速切换到指定标注帧</li>
            <li><b>删除：</b>移除单帧的所有标注</li>
            <li><b>清空：</b>移除所有帧的标注（需确认）</li>
        </ul>
        
        <h3>💾 导入/导出</h3>
        <ul>
            <li><b>导出：</b>保存标注为JSON文件
                <ul>
                    <li>包含边界框、点击、对象注册等完整信息</li>
                    <li>可作为项目备份</li>
                </ul>
            </li>
            <li><b>导入：</b>从JSON文件恢复标注
                <ul>
                    <li>支持新旧格式自动识别</li>
                    <li>导入前会进行数据验证</li>
                </ul>
            </li>
        </ul>
        
        <h2><span class="emoji">✅</span> 七、标注最佳实践</h2>
        
        <h3>建议</h3>
        <ol>
            <li>在第0帧标注所有对象的初始位置</li>
            <li>每个对象标注5-10个关键帧即可，不宜过多</li>
            <li>在以下情况添加修正标注：
                <ul>
                    <li>对象形状显著变化</li>
                    <li>对象被遮挡前后</li>
                    <li>对象运动方向改变</li>
                    <li>SAM2追踪出现明显偏差</li>
                </ul>
            </li>
            <li>使用实时预览验证标注质量</li>
            <li>定期导出标注作为备份</li>
        </ol>
        
        <div class="warning">
            <b>⚠️ 注意事项</b>
            <ul>
                <li>切换帧前记得保存临时点击（按<kbd>A</kbd>键）</li>
                <li>未保存的临时点击切换帧后会丢失（有警告提示）</li>
                <li>导入标注会覆盖当前所有标注</li>
                <li>删除操作不可撤销，请谨慎操作</li>
            </ul>
        </div>
        
        <h2><span class="emoji">❓</span> 八、常见问题</h2>
        
        <p><b>Q: 临时点击无法保存？</b><br>
        A: 检查是否在正确的帧上（临时点击只能在添加它的帧上保存）</p>
        
        <p><b>Q: 预览效果不理想？</b><br>
        A: 尝试添加更多点击（正向或负向）来精细化分割</p>
        
        <p><b>Q: 如何修改已有标注？</b><br>
        A: 切换到对应帧，删除原标注，重新绘制</p>
        
        <p><b>Q: 导入失败？</b><br>
        A: 检查JSON文件格式是否正确，查看错误提示信息</p>
        
        <div class="note" style="margin-top: 20px;">
            <b>💡 小提示</b><br>
            将鼠标悬停在按钮上可查看功能说明
        </div>
        """
        
        text_browser.setHtml(help_html)
        layout.addWidget(text_browser)
        
        # 添加关闭按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        # 显示对话框
        dialog.exec_()

