"""
Phase 2: 标注管理器组件

提供标注列表、跳转、删除、导入导出等功能

Author: Lucien (lucien-6@qq.com)
Date: 2025-10-30
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QLabel,
                             QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from pathlib import Path
import json


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
        
        # 标题
        title_label = QLabel("📋 标注关键帧")
        title_label.setStyleSheet("""
            font-size: 10pt;
            font-weight: bold;
            color: #2c3e50;
            padding: 5px;
        """)
        layout.addWidget(title_label)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["帧号", "对象数", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
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
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setToolTip("刷新标注列表")
        self.refresh_btn.clicked.connect(self.refresh_table)
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.setToolTip("导出标注为JSON文件")
        self.export_btn.clicked.connect(self.export_annotations)
        
        self.import_btn = QPushButton("📥 导入")
        self.import_btn.setToolTip("从JSON文件导入标注")
        self.import_btn.clicked.connect(self.import_annotations)
        
        self.clear_all_btn = QPushButton("🗑️ 清空")
        self.clear_all_btn.setToolTip("清空所有标注")
        self.clear_all_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.clear_all_btn.clicked.connect(self.clear_all_annotations)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_all_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def refresh_table(self):
        """刷新表格数据"""
        if not hasattr(self.main_window, 'video_label') or not self.main_window.video_label:
            return
        
        overlay = self.main_window.video_label.overlay_layer
        annotations = overlay.get_all_annotations()
        current_frame = overlay.current_frame_idx
        
        # 清空表格
        self.table.setRowCount(0)
        
        if not annotations:
            return
        
        # 填充数据
        for frame_idx in sorted(annotations.keys()):
            bboxes = annotations[frame_idx]
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 帧号（当前帧高亮）
            frame_item = QTableWidgetItem(f"{frame_idx}")
            if frame_idx == current_frame:
                frame_item.setBackground(QColor(255, 235, 59, 100))  # 黄色高亮
            frame_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, frame_item)
            
            # 对象数
            count_item = QTableWidgetItem(f"{len(bboxes)}")
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, count_item)
            
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
            
            self.table.setCellWidget(row, 2, action_widget)
    
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
            
            # 删除该帧的标注
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
                
                # 删除帧标注
                del overlay.bboxes_per_frame[frame_idx]
                
                # 如果是当前帧，清空显示
                if frame_idx == overlay.current_frame_idx:
                    overlay.bboxes = []
                    overlay.update()
                
                self.main_window.log_message(f"已删除第 {frame_idx} 帧的标注", "warning")
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
            overlay.bboxes_per_frame.clear()
            overlay.object_registry.clear()
            overlay.bboxes = []
            overlay.next_available_id = 0
            overlay.update()
            
            self.main_window.log_message("已清空所有标注", "warning")
            self.refresh_table()
            self.main_window._update_annotation_status_display()
    
    def export_annotations(self):
        """导出标注为JSON文件"""
        overlay = self.main_window.video_label.overlay_layer
        annotations = overlay.get_all_annotations()
        
        if not annotations:
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
            "annotations": annotations,
            "object_registry": overlay.object_registry,
            "version": "phase2_v1.0"
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.main_window.log_message(f"标注已导出到: {file_path}", "success")
            QMessageBox.information(self, "成功", f"标注已导出!\n{file_path}")
        
        except Exception as e:
            self.main_window.log_message(f"导出失败: {e}", "error")
            QMessageBox.critical(self, "错误", f"导出失败:\n{e}")
    
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
            
            # 验证格式
            if "annotations" not in import_data:
                raise ValueError("无效的标注文件格式")
            
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
            
            # 转换键为整数（JSON键都是字符串）
            annotations = {int(k): v for k, v in import_data["annotations"].items()}
            overlay.bboxes_per_frame = annotations
            
            # 导入对象注册表
            if "object_registry" in import_data:
                registry = {int(k): v for k, v in import_data["object_registry"].items()}
                overlay.object_registry = registry
                
                # 更新next_available_id
                if registry:
                    overlay.next_available_id = max(registry.keys()) + 1
            
            # 刷新显示
            overlay.set_current_frame(overlay.current_frame_idx)
            self.refresh_table()
            self.main_window._update_annotation_status_display()
            
            self.main_window.log_message(f"标注已从 {file_path} 导入", "success")
            QMessageBox.information(self, "成功", "标注导入成功！")
        
        except Exception as e:
            self.main_window.log_message(f"导入失败: {e}", "error")
            QMessageBox.critical(self, "错误", f"导入失败:\n{e}")

