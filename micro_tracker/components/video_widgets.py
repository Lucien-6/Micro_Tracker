import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem, QSizePolicy, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QTimer, QPropertyAnimation, QEasingCurve

# Placeholder for 'from utils.color import COLOR' - this will be addressed later if utils.color is moved
# For now, define a default COLOR list if the import fails, as in the original code.
try:
    from utils.color import COLOR
except ImportError:
    COLOR = [
        (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
        (0, 0, 128), (128, 128, 0),
    ]

class OverlayLayer(QGraphicsItem):
    """高分辨率UI元素覆盖层"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 高分辨率比例因子，使覆盖层分辨率高于视频
        self.resolution_factor = 2.0
        
        # === Phase 1 MVP: 多帧模式支持 ===
        self.multi_frame_mode = True  # 启用多帧模式
        self.current_frame_idx = 0    # 当前显示的帧索引
        self.bboxes_per_frame = {}    # {frame_idx: [[x1,y1,x2,y2,id], ...]}
        
        # === Phase 2: 对象ID管理 ===
        self.object_registry = {}  # {obj_id: {"first_frame": int, "frames": [int], "color": tuple}}
        self.annotation_mode = "new_object"  # "new_object" 或 "refine_object"
        self.selected_object_id_for_refine = None  # 修正模式下选中的对象ID
        self.next_available_id = 0  # 下一个可用ID
        
        # === Refinement功能: 新的统一标注结构 ===
        self.annotations_per_frame = {}  # {frame_idx: {obj_id: {"box": [x1,y1,x2,y2], "points": [(x,y)], "labels": [0/1], "mask": np.array}}}
        self.prompt_mode = "box"  # "box", "positive_point", "negative_point"
        self.temp_points = []  # [(x, y)]临时点击存储
        self.temp_labels = []  # [0/1]点击标签
        self.temp_points_frame_idx = None  # 临时点击所属的帧索引
        self.current_editing_obj_id = None  # 当前编辑的对象ID
        
        # === 提示隐藏功能 ===
        self.prompts_hidden = False  # 是否隐藏已有提示标记
        
        # 固定颜色调色板（Phase 2）- 20色高饱和度方案
        self.color_palette = [
            (255, 0, 0),     # 鲜红色
            (255, 100, 0),   # 深橙色
            (255, 165, 0),   # 亮橙色
            (0, 255, 0),     # 鲜绿色
            (0, 255, 127),   # 春绿色
            (0, 255, 255),   # 青色
            (0, 150, 255),   # 天蓝色
            (0, 0, 255),     # 鲜蓝色
            (128, 0, 255),   # 紫色
            (255, 0, 255),   # 品红色
            (255, 0, 127),   # 深粉色
            (255, 50, 150),  # 玫瑰红
            (255, 127, 80),  # 珊瑚色
            (150, 255, 0),   # 黄绿色
            (0, 200, 150),   # 青绿色
            (0, 180, 200),   # 深青色
            (75, 0, 200),    # 靛蓝色
            (200, 0, 200),   # 紫红色
            (200, 0, 50),    # 深红色
            (50, 255, 50),   # lime色
        ]
        
        # === 保留：向后兼容 ===
        self.bboxes = []  # 边界框列表 [[x1, y1, x2, y2, id], ...]
        
        self.selected_bbox = -1  # 选中的边界框索引
        self.colors = COLOR # Use the imported or default COLOR
        self.tracks = {}  # 轨迹点 {obj_id: [points], ...}
        self.object_features = {}  # 对象特征(长短轴、角度等)
        self.id_labels = []  # ID标签位置和内容
        self.frame_size = (640, 480)  # 帧大小
        self.drawing = False  # 是否正在绘制
        self.current_bbox = [0, 0, 0, 0, -1]  # 当前正在绘制的边界框
        
        # === 实时预览支持 ===
        self.preview_masks = {}  # {obj_id: np.ndarray} 预览mask数据
        self.preview_enabled = True  # 默认启用预览功能
        
        self.setAcceptHoverEvents(True)
    
    def boundingRect(self):
        return QRectF(0, 0, self.frame_size[0], self.frame_size[1])
    
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # === 提示隐藏功能：隐藏状态下跳过绑制已有提示标记（不影响预览mask） ===
        if not self.prompts_hidden:
            self._draw_bboxes(painter)
            self._draw_tracks(painter)
            self._draw_object_features(painter)
            self._draw_id_labels(painter)
            self._draw_click_markers(painter)  # 绘制点击标记
        
        # 预览mask始终绘制（不受隐藏状态影响，仅在提示被删除时才清除）
        self._draw_preview_masks(painter)
        
        # 始终绘制正在绘制的边界框（允许用户在隐藏模式下绘制新提示）
        if self.drawing:
            self._draw_current_bbox(painter)
    
    def _draw_bboxes(self, painter):
        for i, bbox in enumerate(self.bboxes):
            # === Phase 2: 使用对象固定颜色 ===
            obj_id = bbox[4]
            color = self.get_object_color(obj_id)
            
            qcolor = QColor(color[0], color[1], color[2])
            pen = QPen(qcolor)
            pen.setWidth(2)
            pen.setCosmetic(True)
            if i == self.selected_bbox:
                pen.setStyle(Qt.DashLine)
                pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(
                int(bbox[0]), 
                int(bbox[1]), 
                int(bbox[2] - bbox[0]), 
                int(bbox[3] - bbox[1])
            )
        
        # === Phase 2: 修正模式时高亮正在修正的对象 ===
        if self.annotation_mode == "refine_object" and self.selected_object_id_for_refine is not None:
            for bbox in self.bboxes:
                if bbox[4] == self.selected_object_id_for_refine:
                    # 绘制闪烁金色边框
                    painter.setPen(QPen(QColor(255, 215, 0), 3, Qt.DashLine))
                    painter.drawRect(int(bbox[0]), int(bbox[1]), 
                                   int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1]))
    
    def _draw_current_bbox(self, painter):
        if not self.drawing:
            return
        pen = QPen(QColor(255, 255, 0))
        pen.setWidth(2)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(
            int(self.current_bbox[0]), 
            int(self.current_bbox[1]), 
            int(self.current_bbox[2] - self.current_bbox[0]), 
            int(self.current_bbox[3] - self.current_bbox[1])
        )
    
    def _draw_tracks(self, painter):
        for obj_id, points in self.tracks.items():
            if len(points) < 2:
                continue
            color_idx = int(obj_id) % len(self.colors) if int(obj_id) >= 0 else 0
            color = self.colors[color_idx]
            qcolor = QColor(color[0], color[1], color[2])
            pen = QPen(qcolor)
            pen.setWidth(2)
            pen.setCosmetic(True)
            painter.setPen(pen)
            for i in range(1, len(points)):
                painter.drawLine(
                    int(points[i-1][0]), int(points[i-1][1]),
                    int(points[i][0]), int(points[i][1])
                )
    
    def _draw_object_features(self, painter):
        for obj_id, features in self.object_features.items():
            if 'center' not in features:
                continue
            center = features['center']
            if 'major_axis' in features and 'minor_axis' in features and 'angle' in features:
                major_axis = features['major_axis']
                minor_axis = features['minor_axis']
                angle = features['angle']
                pen = QPen(QColor(255, 0, 0)) # Red for major axis
                pen.setWidth(2)
                pen.setCosmetic(True)
                painter.setPen(pen)
                angle_rad = np.deg2rad(angle)
                dx_major = major_axis * np.cos(angle_rad)
                dy_major = major_axis * np.sin(angle_rad)
                painter.drawLine(
                    int(center[0] - dx_major), int(center[1] - dy_major),
                    int(center[0] + dx_major), int(center[1] + dy_major)
                )
                pen = QPen(QColor(0, 0, 255)) # Blue for minor axis
                pen.setWidth(2)
                pen.setCosmetic(True)
                painter.setPen(pen)
                minor_angle_rad = angle_rad + np.pi/2
                dx_minor = minor_axis * np.cos(minor_angle_rad)
                dy_minor = minor_axis * np.sin(minor_angle_rad)
                painter.drawLine(
                    int(center[0] - dx_minor), int(center[1] - dy_minor),
                    int(center[0] + dx_minor), int(center[1] + dy_minor)
                )
    
    def _draw_id_labels(self, painter):
        font = QFont("Arial", 10)
        font.setBold(True)
        painter.setFont(font)
        for i, bbox in enumerate(self.bboxes):
            obj_id = bbox[4]
            
            # === Phase 2: 使用对象固定颜色 ===
            color = self.get_object_color(obj_id)
            
            is_selected = (i == self.selected_bbox)
            text = f"obj_{obj_id}"
            if is_selected:
                text = f"* {text} *"
            text_x = int(bbox[0])
            text_y = int(bbox[1] - 5)
            painter.setPen(QColor(color[0], color[1], color[2]))
            painter.drawText(text_x, text_y, text)
    
    def _draw_click_markers(self, painter):
        """绘制点击标记"""
        # 绘制已保存的点击
        if self.current_frame_idx in self.annotations_per_frame:
            frame_data = self.annotations_per_frame[self.current_frame_idx]
            for obj_id, prompts in frame_data.items():
                if "points" in prompts and prompts["points"]:
                    for i, (x, y) in enumerate(prompts["points"]):
                        label = prompts["labels"][i] if "labels" in prompts and i < len(prompts["labels"]) else 1
                        # 绘制不同颜色的点：绿色=正向，红色=负向
                        color = QColor(0, 255, 0) if label == 1 else QColor(255, 0, 0)
                        pen = QPen(color, 1)
                        pen.setCosmetic(True)
                        painter.setPen(pen)
                        painter.setBrush(Qt.NoBrush)
                        # 绘制圆形标记（修复：移除错误的resolution_factor缩放）
                        painter.drawEllipse(int(x - 4), int(y - 4), 8, 8)
                        # 绘制中心点
                        pen = QPen(color, 3)
                        pen.setCosmetic(True)
                        painter.setPen(pen)
                        painter.drawPoint(int(x), int(y))
        
        # 绘制临时点击（还未保存的）- 只在所属帧显示
        if self.temp_points and self.temp_points_frame_idx == self.current_frame_idx:
            for i, (x, y) in enumerate(self.temp_points):
                label = self.temp_labels[i] if i < len(self.temp_labels) else 1
                color = QColor(0, 255, 0, 150) if label == 1 else QColor(255, 0, 0, 150)
                painter.setPen(QPen(color, 1, Qt.SolidLine))
                painter.setBrush(Qt.NoBrush)
                # 修复：移除错误的resolution_factor缩放
                painter.drawEllipse(int(x - 4), int(y - 4), 8, 8)
    
    def _draw_preview_masks(self, painter):
        """
        绘制实时预览的masks（优化版本，使用numpy批量操作）
        
        Notes:
            - 只在preview_enabled=True时绘制
            - mask以半透明方式叠加在视频帧上
            - 使用对象固定颜色（来自color_palette）
            - 使用numpy批量操作提升绘制性能
        
        Performance:
            使用numpy批量操作代替逐像素循环，提升绘制速度
        """
        if not self.preview_enabled or not self.preview_masks:
            return
        
        for obj_id, mask in self.preview_masks.items():
            if mask is None:
                continue
            
            try:
                # 调整mask尺寸
                target_size = (self.frame_size[0], self.frame_size[1])
                if mask.shape[:2] != (self.frame_size[1], self.frame_size[0]):
                    mask_resized = cv2.resize(
                        mask.astype(np.uint8), 
                        target_size,
                        interpolation=cv2.INTER_NEAREST
                    )
                else:
                    mask_resized = mask.astype(np.uint8)
                
                # 创建彩色mask图像（使用numpy批量操作）
                color = self.get_object_color(obj_id)
                mask_colored = np.zeros((mask_resized.shape[0], mask_resized.shape[1], 4), dtype=np.uint8)
                
                # 只在mask区域填充颜色（80透明度）
                mask_indices = mask_resized > 0
                mask_colored[mask_indices] = [color[2], color[1], color[0], 80]  # BGRA格式
                
                # 转换为QImage
                from PyQt5.QtGui import QImage
                height, width = mask_colored.shape[:2]
                bytes_per_line = 4 * width
                q_image = QImage(
                    mask_colored.data, 
                    width, 
                    height, 
                    bytes_per_line, 
                    QImage.Format_ARGB32
                )
                
                # 绘制
                painter.drawImage(0, 0, q_image)
            
            except Exception as e:
                print(f"绘制预览mask失败 (obj_id={obj_id}): {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def update_frame_size(self, width, height):
        self.frame_size = (width, height)
        self.prepareGeometryChange()
    
    def clear_all(self):
        self.bboxes = []
        self.selected_bbox = -1
        self.tracks = {}
        self.object_features = {}
        self.id_labels = []
        self.drawing = False
        self.current_bbox = [0, 0, 0, 0, -1]
        self.update()
    
    # === Phase 1 MVP: 多帧管理方法 ===
    def set_current_frame_silent(self, frame_idx):
        """
        静默设置当前帧索引（用于视频播放期间）
        
        Args:
            frame_idx (int): 要切换到的帧索引（从0开始）
        
        Notes:
            - 不弹出对话框、不询问未保存的临时点击
            - 清除预览masks
            - 同步边界框显示
            - 用于视频播放时的帧切换，避免打断播放流程
        
        Version:
            Added to fix preview masks persisting during video playback
        """
        try:
            old_frame_idx = self.current_frame_idx
            self.current_frame_idx = frame_idx
            
            # 清除选择状态
            if old_frame_idx != frame_idx:
                self.selected_bbox = -1
                
                # 切换帧时自动取消隐藏提示
                self.prompts_hidden = False
                
                # 清除预览masks（关键：防止预览停留在视频上）
                self.preview_masks.clear()
            
            # 同步边界框显示
            self._sync_bboxes_from_current_frame()
            self.update()
        except Exception as e:
            print(f"Error in set_current_frame_silent: {e}")
            import traceback
            traceback.print_exc()
            self.bboxes = []
            self.update()
    
    def set_current_frame(self, frame_idx):
        """
        设置当前帧索引，触发边界框显示更新
        
        Args:
            frame_idx (int): 要切换到的帧索引（从0开始）
        
        Notes:
            - 切换帧时会清除当前选中的边界框
            - 会自动从 bboxes_per_frame 字典同步到 bboxes 列表
            - 会清空不属于当前帧的临时点击（修复点击标注跨帧显示问题）
            - 触发重绘更新UI显示
            - 即使切换到相同帧索引也会同步（用于强制刷新）
        
        Version:
            Added in Phase 1 MVP for multi-frame annotation support
        """
        try:
            # 总是执行同步和更新，即使帧索引相同
            # 这确保了数据一致性，特别是在外部修改bboxes_per_frame后
            old_frame_idx = self.current_frame_idx
            self.current_frame_idx = frame_idx
            
            # 只有在帧真正切换时才清除选择和临时点击
            if old_frame_idx != frame_idx:
                self.selected_bbox = -1
                
                # === 提示隐藏功能：切换帧时自动取消隐藏 ===
                self.prompts_hidden = False
                
                # === 改进：清空临时点击前先提示用户 ===
                if self.temp_points_frame_idx is not None and self.temp_points_frame_idx != frame_idx:
                    # 检查是否有临时点击需要保存
                    if len(self.temp_points) > 0:
                        # 尝试获取主窗口并显示提示
                        from PyQt5.QtWidgets import QApplication, QMessageBox
                        app = QApplication.instance()
                        should_clear = True  # 默认清除
                        
                        if app:
                            for widget in app.topLevelWidgets():
                                if hasattr(widget, 'log_message'):
                                    # 显示警告日志
                                    widget.log_message(
                                        f"⚠️ 检测到第 {self.temp_points_frame_idx} 帧有 {len(self.temp_points)} 个未保存的临时点击", 
                                        "warning"
                                    )
                                    
                                    # 弹出确认对话框
                                    reply = QMessageBox.question(
                                        widget,
                                        "未保存的临时点击",
                                        f"第 {self.temp_points_frame_idx} 帧有 {len(self.temp_points)} 个临时点击尚未保存。\n\n"
                                        f"切换到第 {frame_idx} 帧后，这些临时点击将被丢弃。\n\n"
                                        f"是否继续切换？\n\n"
                                        f"提示：您可以先返回第 {self.temp_points_frame_idx} 帧，按 A 键保存点击。",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No
                                    )
                                    
                                    if reply == QMessageBox.No:
                                        # 用户选择不切换，恢复到原来的帧
                                        self.current_frame_idx = old_frame_idx
                                        return
                                    else:
                                        # 用户确认丢弃
                                        widget.log_message(f"🗑️ 已丢弃第 {self.temp_points_frame_idx} 帧的临时点击", "warning")
                                    
                                    break
                    
                    # 清空临时点击
                    self.temp_points = []
                    self.temp_labels = []
                    self.temp_points_frame_idx = None
                    self.current_editing_obj_id = None
            
            self._sync_bboxes_from_current_frame()
            self.update()
        except Exception as e:
            print(f"Error in set_current_frame: {e}")
            import traceback
            traceback.print_exc()
            # 回退到安全状态
            self.bboxes = []
            self.update()
    
    def _sync_bboxes_from_current_frame(self):
        """
        从当前帧的字典同步到 bboxes 列表（用于绘制）
        
        Notes:
            - 只在多帧模式下执行
            - 总是执行同步以确保一致性
        """
        try:
            if not self.multi_frame_mode:
                return
            
            # 从字典获取当前帧的边界框
            current_bboxes = self.bboxes_per_frame.get(self.current_frame_idx, [])
            self.bboxes = current_bboxes.copy()
        except Exception as e:
            print(f"Error in _sync_bboxes_from_current_frame: {e}")
            self.bboxes = []
    
    def _sync_bboxes_to_current_frame(self):
        """
        从 bboxes 列表同步回当前帧的字典
        
        Notes:
            - 只在多帧模式下执行
            - 如果当前帧没有边界框，会从字典中删除该帧
        """
        try:
            if not self.multi_frame_mode:
                return
            
            if len(self.bboxes) > 0:
                self.bboxes_per_frame[self.current_frame_idx] = self.bboxes.copy()
            else:
                # 如果当前帧没有边界框，从字典中删除该帧
                self.bboxes_per_frame.pop(self.current_frame_idx, None)
        except Exception as e:
            print(f"Error in _sync_bboxes_to_current_frame: {e}")
    
    def get_annotated_frame_indices(self):
        """
        获取所有已标注的帧索引列表（包括边界框和点标注）
        
        Returns:
            list: 排序后的帧索引列表
        
        Notes:
            - 合并 bboxes_per_frame 和 annotations_per_frame 的所有帧
            - 确保纯点标注的帧也被统计
        """
        if self.multi_frame_mode:
            # 合并两个数据源的帧索引
            all_frames = set()
            
            # 添加有边界框标注的帧
            all_frames.update(self.bboxes_per_frame.keys())
            
            # 添加有refinement标注的帧（包括纯点标注）
            all_frames.update(self.annotations_per_frame.keys())
            
            return sorted(all_frames)
        else:
            return [0] if len(self.bboxes) > 0 else []
    
    def get_annotation_count(self):
        """
        获取当前帧的标注数量
        
        Returns:
            int: 当前帧的边界框数量
        """
        if self.multi_frame_mode:
            return len(self.bboxes_per_frame.get(self.current_frame_idx, []))
        else:
            return len(self.bboxes)
    
    def get_all_annotations(self):
        """
        获取所有帧的标注数据（用于处理）
        
        Returns:
            dict: {frame_idx: [[x1, y1, x2, y2, id], ...]}
        """
        if self.multi_frame_mode:
            return self.bboxes_per_frame.copy()
        else:
            # 向后兼容：单帧模式返回第0帧
            return {0: self.bboxes.copy()} if len(self.bboxes) > 0 else {}
    
    def get_refinement_annotations(self):
        """
        获取refinement格式的标注数据
        
        Returns:
            dict: {frame_idx: {obj_id: {"box": [x1,y1,x2,y2], "points": [(x,y)], "labels": [0/1]}}}
        """
        refinement_data = {}
        
        # 先合并bbox数据和点击数据
        # 1. 从旧格式的bbox数据开始
        bbox_annotations = self.get_all_annotations()
        
        for frame_idx, bbox_list in bbox_annotations.items():
            if frame_idx not in refinement_data:
                refinement_data[frame_idx] = {}
                
            for bbox in bbox_list:
                x1, y1, x2, y2, obj_id = bbox
                refinement_data[frame_idx][obj_id] = {
                    "box": [x1, y1, x2, y2],
                    "points": [],
                    "labels": []
                }
        
        # 2. 合并annotations_per_frame中的点击数据
        for frame_idx, frame_data in self.annotations_per_frame.items():
            if frame_idx not in refinement_data:
                refinement_data[frame_idx] = {}
                
            for obj_id, prompts in frame_data.items():
                if obj_id in refinement_data.get(frame_idx, {}):
                    # 更新已有对象的点击数据
                    if "points" in prompts:
                        refinement_data[frame_idx][obj_id]["points"] = prompts["points"]
                    if "labels" in prompts:
                        refinement_data[frame_idx][obj_id]["labels"] = prompts["labels"]
                else:
                    # 新对象（只有点击没有box）
                    refinement_data[frame_idx][obj_id] = prompts
        
        # 3. 添加临时点击（如果有）
        if self.temp_points and self.current_editing_obj_id is not None:
            frame_idx = self.current_frame_idx
            obj_id = self.current_editing_obj_id
            
            if frame_idx not in refinement_data:
                refinement_data[frame_idx] = {}
            if obj_id not in refinement_data[frame_idx]:
                refinement_data[frame_idx][obj_id] = {"box": None, "points": [], "labels": []}
                
            # 添加临时点击到已有点击列表
            existing_points = refinement_data[frame_idx][obj_id].get("points", [])
            existing_labels = refinement_data[frame_idx][obj_id].get("labels", [])
            
            refinement_data[frame_idx][obj_id]["points"] = existing_points + self.temp_points
            refinement_data[frame_idx][obj_id]["labels"] = existing_labels + self.temp_labels
        
        return refinement_data
    
    # === Phase 2: 对象ID管理方法 ===
    def register_object(self, obj_id, frame_idx):
        """
        注册对象或更新对象信息
        
        Args:
            obj_id (int): 对象ID
            frame_idx (int): 帧索引
        """
        if obj_id not in self.object_registry:
            # 新对象：分配颜色
            color_idx = int(obj_id) % len(self.color_palette)
            self.object_registry[obj_id] = {
                "first_frame": frame_idx,
                "frames": [frame_idx],
                "color": self.color_palette[color_idx]
            }
        else:
            # 已有对象：添加新帧
            if frame_idx not in self.object_registry[obj_id]["frames"]:
                self.object_registry[obj_id]["frames"].append(frame_idx)
                self.object_registry[obj_id]["frames"].sort()
    
    def unregister_object(self, obj_id):
        """移除对象注册"""
        if obj_id in self.object_registry:
            del self.object_registry[obj_id]
    
    def get_next_object_id(self):
        """获取下一个可用的对象ID"""
        while self.next_available_id in self.object_registry:
            self.next_available_id += 1
        return self.next_available_id
    
    def set_annotation_mode(self, mode, obj_id=None):
        """
        设置标注模式
        
        Args:
            mode (str): "new_object" 或 "refine_object"
            obj_id (int, optional): 修正模式下的对象ID
        """
        if mode not in ["new_object", "refine_object"]:
            raise ValueError(f"Invalid annotation mode: {mode}")
        
        self.annotation_mode = mode
        # 确保obj_id为整数类型
        self.selected_object_id_for_refine = int(obj_id) if obj_id is not None else None
        
        if mode == "refine_object" and obj_id is None:
            raise ValueError("修正模式下必须指定对象ID")
    
    def get_object_color(self, obj_id):
        """获取对象的固定颜色"""
        if obj_id in self.object_registry:
            return self.object_registry[obj_id]["color"]
        else:
            # 未注册对象：临时分配颜色
            color_idx = int(obj_id) % len(self.color_palette)
            return self.color_palette[color_idx]
    
    def save_temp_clicks(self):
        """保存临时点击到annotations_per_frame"""
        if not self.temp_points or self.current_editing_obj_id is None:
            return False
        
        # 验证临时点击属于当前帧
        if self.temp_points_frame_idx is not None and self.temp_points_frame_idx != self.current_frame_idx:
            error_msg = f"无法保存：临时点击属于第 {self.temp_points_frame_idx} 帧，但当前在第 {self.current_frame_idx} 帧"
            print(f"警告: {error_msg}")
            
            # === 新增：通过主窗口显示错误信息 ===
            # 尝试获取主窗口实例
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if hasattr(widget, 'log_message'):
                        widget.log_message(f"❌ {error_msg}", "error")
                        QMessageBox.warning(
                            widget, 
                            "保存失败", 
                            f"{error_msg}\n\n请先切换到第 {self.temp_points_frame_idx} 帧，再按 A 键保存点击。"
                        )
                        break
            
            return False
            
        frame_idx = self.current_frame_idx
        obj_id = self.current_editing_obj_id
        
        # 确保数据结构存在
        if frame_idx not in self.annotations_per_frame:
            self.annotations_per_frame[frame_idx] = {}
        if obj_id not in self.annotations_per_frame[frame_idx]:
            self.annotations_per_frame[frame_idx][obj_id] = {
                "box": None,
                "points": [],
                "labels": []
            }
        
        # 获取该对象在当前帧的bbox（如果有）
        for bbox in self.bboxes:
            if bbox[4] == obj_id:
                self.annotations_per_frame[frame_idx][obj_id]["box"] = [bbox[0], bbox[1], bbox[2], bbox[3]]
                break
        
        # 添加点击到现有列表
        existing_points = self.annotations_per_frame[frame_idx][obj_id].get("points", [])
        existing_labels = self.annotations_per_frame[frame_idx][obj_id].get("labels", [])
        
        self.annotations_per_frame[frame_idx][obj_id]["points"] = existing_points + self.temp_points
        self.annotations_per_frame[frame_idx][obj_id]["labels"] = existing_labels + self.temp_labels
        
        # 清空临时列表
        num_saved = len(self.temp_points)
        self.temp_points = []
        self.temp_labels = []
        self.temp_points_frame_idx = None
        self.current_editing_obj_id = None
        
        # 更新显示
        self.update()
        
        return num_saved
    
    def clear_temp_clicks(self):
        """清除临时点击"""
        self.temp_points = []
        self.temp_labels = []
        self.temp_points_frame_idx = None
        self.current_editing_obj_id = None
        self.update()
    
    def start_drawing(self, x, y, next_id=None):
        """开始绘制边界框"""
        self.drawing = True
        
        # === Phase 2: 根据标注模式决定对象ID ===
        if self.annotation_mode == "new_object":
            obj_id = self.get_next_object_id()
        elif self.annotation_mode == "refine_object":
            obj_id = self.selected_object_id_for_refine
            if obj_id is None:
                raise ValueError("修正模式下必须先选择对象")
        else:
            # 向后兼容
            obj_id = next_id if next_id is not None else self.get_next_object_id()
        
        self.current_bbox = [x, y, x, y, obj_id]
        self.update()
    
    def update_drawing(self, x, y):
        if not self.drawing:
            return
        self.current_bbox[2] = x
        self.current_bbox[3] = y
        self.update()
    
    def finish_drawing(self):
        if not self.drawing:
            return None
        self.drawing = False
        x1 = min(self.current_bbox[0], self.current_bbox[2])
        y1 = min(self.current_bbox[1], self.current_bbox[3])
        x2 = max(self.current_bbox[0], self.current_bbox[2])
        y2 = max(self.current_bbox[1], self.current_bbox[3])
        bbox_id = self.current_bbox[4]
        if (x2 - x1) > 10 and (y2 - y1) > 10:
            new_bbox_data = [x1, y1, x2, y2, bbox_id]
            self.bboxes.append(new_bbox_data)
            
            # === Phase 2: 注册对象 ===
            self.register_object(bbox_id, self.current_frame_idx)
            
            # Phase 1 MVP: 同步到多帧字典
            self._sync_bboxes_to_current_frame()
            
            self.tracks[bbox_id] = [(int((x1+x2)/2), int((y1+y2)/2))]
            self.object_features[bbox_id] = {'center': (x1, y1)}
            self.update()
            return new_bbox_data
        return None
    
    def select_bbox(self, x, y):
        old_selected = self.selected_bbox
        self.selected_bbox = -1
        for i, bbox in enumerate(self.bboxes):
            if (bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]):
                self.selected_bbox = i
                self.update()
                return i
        if old_selected != self.selected_bbox:
            self.update()
        return -1
    
    def delete_selected_bbox(self):
        """
        删除选中的对象在所有帧的标注
        
        Returns:
            int: 被删除的对象ID，如果没有选中则返回-1
        
        Notes:
            - 删除该对象在所有帧的边界框标注
            - 删除该对象在所有帧的点击标注
            - 完全移除对象注册信息
            - 清理轨迹、特征和预览数据
        """
        if self.selected_bbox == -1:
            return -1
        
        deleted_id = int(self.bboxes[self.selected_bbox][4])  # 确保为整数类型
        
        # === 1. 删除该对象在所有帧的边界框标注 ===
        frames_to_clean = []  # 记录需要清理的空帧
        for frame_idx in list(self.bboxes_per_frame.keys()):
            # 过滤掉该对象的边界框
            self.bboxes_per_frame[frame_idx] = [
                bbox for bbox in self.bboxes_per_frame[frame_idx] 
                if bbox[4] != deleted_id
            ]
            # 如果该帧没有任何边界框了，标记为待清理
            if len(self.bboxes_per_frame[frame_idx]) == 0:
                frames_to_clean.append(frame_idx)
        
        # 清理空帧
        for frame_idx in frames_to_clean:
            del self.bboxes_per_frame[frame_idx]
        
        # === 2. 删除该对象在所有帧的点击标注 ===
        frames_to_clean = []
        for frame_idx in list(self.annotations_per_frame.keys()):
            if deleted_id in self.annotations_per_frame[frame_idx]:
                del self.annotations_per_frame[frame_idx][deleted_id]
            # 如果该帧没有任何点击标注了，标记为待清理
            if len(self.annotations_per_frame[frame_idx]) == 0:
                frames_to_clean.append(frame_idx)
        
        # 清理空帧
        for frame_idx in frames_to_clean:
            del self.annotations_per_frame[frame_idx]
        
        # === 3. 清除临时点击（如果属于该对象）===
        if self.current_editing_obj_id == deleted_id:
            self.temp_points = []
            self.temp_labels = []
            self.temp_points_frame_idx = None
            self.current_editing_obj_id = None
        
        # === 4. 完全移除对象注册信息 ===
        self.unregister_object(deleted_id)
        
        # === 5. 清理轨迹和特征数据 ===
        if deleted_id in self.tracks:
            del self.tracks[deleted_id]
        if deleted_id in self.object_features:
            del self.object_features[deleted_id]
        
        # === 6. 清除该对象的预览mask ===
        if deleted_id in self.preview_masks:
            del self.preview_masks[deleted_id]
        
        # === 7. 同步当前帧的边界框显示 ===
        self._sync_bboxes_from_current_frame()
        
        self.selected_bbox = -1
        self.update()
        return deleted_id
    
    def clear_bboxes(self):
        count = len(self.bboxes)
        self.bboxes = []
        
        # === Phase 1 MVP: 同步到多帧字典 ===
        self._sync_bboxes_to_current_frame()
        
        # 清空当前帧的点击标注（修复：之前遗漏）
        if self.current_frame_idx in self.annotations_per_frame:
            del self.annotations_per_frame[self.current_frame_idx]
        
        # 清空当前帧的临时点击
        if self.temp_points_frame_idx == self.current_frame_idx:
            self.temp_points = []
            self.temp_labels = []
            self.temp_points_frame_idx = None
            self.current_editing_obj_id = None
        
        self.selected_bbox = -1
        self.tracks = {}
        self.object_features = {}
        
        # === 清除所有预览masks ===
        self.preview_masks.clear()
        
        self.update()
        return count
    
    def reset_all_state(self):
        """
        完全重置所有状态（用于加载新视频/图像序列时）
        
        Notes:
            - 清空所有帧的边界框和点击标注数据
            - 重置对象注册表和ID计数器
            - 重置标注模式和UI相关状态
            - 比clear_bboxes()更彻底，适用于加载新输入源时
        """
        # 清空所有帧的边界框数据
        self.bboxes_per_frame.clear()
        self.bboxes = []
        
        # 清空所有帧的点击标注数据
        self.annotations_per_frame.clear()
        
        # 清空临时点击状态
        self.temp_points = []
        self.temp_labels = []
        self.temp_points_frame_idx = None
        self.current_editing_obj_id = None
        
        # 重置对象注册表和ID计数器
        self.object_registry.clear()
        self.next_available_id = 0
        
        # 重置标注模式
        self.annotation_mode = "new_object"
        self.selected_object_id_for_refine = None
        
        # 重置选择和绘制状态
        self.selected_bbox = -1
        self.drawing = False
        self.current_bbox = [0, 0, 0, 0, -1]
        
        # 清空轨迹和特征数据
        self.tracks.clear()
        self.object_features.clear()
        
        # 清空预览masks
        self.preview_masks.clear()
        
        # 重置提示隐藏状态
        self.prompts_hidden = False
        
        # 重置当前帧索引
        self.current_frame_idx = 0
        
        # 刷新显示
        self.update()
    
    def update_object_feature(self, obj_id, feature_name, value):
        if obj_id not in self.object_features:
            self.object_features[obj_id] = {}
        self.object_features[obj_id][feature_name] = value
        self.update()
    
    def add_track_point(self, obj_id, point):
        if obj_id not in self.tracks:
            self.tracks[obj_id] = []
        self.tracks[obj_id].append(point)
        self.update()
    
    # === 实时预览控制方法 ===
    def set_preview_mask(self, obj_id, mask):
        """
        设置预览mask
        
        Args:
            obj_id (int): 对象ID
            mask (np.ndarray): 二值mask数组
        """
        self.preview_masks[obj_id] = mask
        self.update()
    
    def clear_preview_masks(self):
        """清除所有预览masks"""
        self.preview_masks.clear()
        self.update()
    
    def set_preview_enabled(self, enabled):
        """
        启用/禁用预览功能
        
        Args:
            enabled (bool): True启用，False禁用
        """
        self.preview_enabled = enabled
        if not enabled:
            self.clear_preview_masks()
        self.update()
    
    def toggle_prompts_visibility(self):
        """
        切换提示标记的可见性（Ctrl+H快捷键触发）
        
        Returns:
            tuple: (bool, str) - (切换是否成功, 状态消息)
        
        Notes:
            - 存在临时点击时不允许隐藏，需先保存或删除
            - 切换帧时会自动取消隐藏
        """
        # 检查是否有临时点击
        if self.temp_points and len(self.temp_points) > 0:
            return False, "存在未保存的临时点击，请先按 A 键保存或 Ctrl+C 删除"
        
        # 切换隐藏状态
        self.prompts_hidden = not self.prompts_hidden
        self.update()
        
        if self.prompts_hidden:
            return True, "已隐藏提示标记（按 Ctrl+H 或切换帧恢复显示）"
        else:
            return True, "已显示提示标记"


class MultiLayerVideoView(QGraphicsView):
    bbox_added = pyqtSignal(list)
    bbox_selected = pyqtSignal(int)
    bbox_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("border: 1px solid #c0c0c0; background-color: #f0f0f0;")
        self.setFocusPolicy(Qt.StrongFocus)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.frame_layer = QGraphicsPixmapItem()
        self.scene.addItem(self.frame_layer)
        self.overlay_layer = OverlayLayer()
        self.scene.addItem(self.overlay_layer)
        self.overlay_layer.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        # 禁用自动锚点，手动控制缩放中心
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)
        # 启用滚动条以支持拖拽功能
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scale_factor = 1.0
        self.manual_zoom_active = False
        self.is_panning = False
        self.last_pan_pos = None
        self.min_scale = 1.0
        self.max_scale = 10.0
        self.zoom_step = 1.15
        self.zoom_tip_timer = None
        self.zoom_tip_label = None
        self.frame = None
        self.original_pixmap = None
    
    def set_frame(self, frame):
        self.frame = frame
        if self.frame is not None:
            self._update_display()
    
    def _update_display(self):
        if self.frame is None:
            return
        h, w, c = self.frame.shape
        bytes_per_line = c * w
        q_img = QImage(self.frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
        self.original_pixmap = pixmap
        self.frame_layer.setPixmap(pixmap)
        self.overlay_layer.update_frame_size(w, h)
        if not self.manual_zoom_active:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.scale_factor = 1.0
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.frame is not None and not self.manual_zoom_active:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def wheelEvent(self, event):
        """鼠标滚轮事件处理：Ctrl+滚轮缩放"""
        if event.modifiers() == Qt.ControlModifier:
            if self.frame is None:
                event.ignore()
                return
            
            delta = event.angleDelta().y()
            if delta > 0:
                zoom_factor = self.zoom_step
            else:
                zoom_factor = 1.0 / self.zoom_step
            
            new_scale = self.scale_factor * zoom_factor
            
            if self.min_scale <= new_scale <= self.max_scale:
                # 手动实现以鼠标为中心的缩放
                # 1. 获取鼠标在视图中的位置（像素坐标）
                view_pos = event.pos()
                
                # 2. 获取鼠标对应的场景位置（缩放前）
                scene_pos = self.mapToScene(view_pos)
                
                # 3. 执行缩放
                self.scale(zoom_factor, zoom_factor)
                self.scale_factor = new_scale
                self.manual_zoom_active = True
                
                # 4. 缩放后，计算同一场景点在视图中的新位置
                new_view_pos = self.mapFromScene(scene_pos)
                
                # 5. 计算视图坐标的偏移（像素）
                # 这是场景点在视图中"漂移"的距离
                delta_x = new_view_pos.x() - view_pos.x()
                delta_y = new_view_pos.y() - view_pos.y()
                
                # 6. 调整滚动条补偿这个偏移，使场景点回到鼠标位置
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() + int(delta_x)
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() + int(delta_y)
                )
                
                self.show_zoom_tip()
                event.accept()
            else:
                self.show_zoom_boundary_feedback(new_scale)
                event.accept()
        else:
            super().wheelEvent(event)
    
    def mousePressEvent(self, event):
        if self.frame is None:
            return
        self.setFocus()
        
        # 优先级1：Ctrl+左键拖拽
        if event.modifiers() == Qt.ControlModifier and event.button() == Qt.LeftButton:
            self.is_panning = True
            self.last_pan_pos = event.pos()
            self.viewport().setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        
        # 优先级2：中键重置缩放
        if event.button() == Qt.MiddleButton:
            self.reset_zoom()
            event.accept()
            return
        
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        
        # 检查当前提示模式
        if self.overlay_layer.prompt_mode == "point":
            # 点击模式：根据鼠标键判断正负
            if event.button() == Qt.LeftButton:
                # 左键=正向点击
                self._handle_point_click(x, y, 1)
            elif event.button() == Qt.RightButton:
                # 右键=负向点击
                self._handle_point_click(x, y, 0)
            return
        
        # === Refinement模式下禁止绘制新的边界框（符合SAM2官方规范）===
        if self.overlay_layer.annotation_mode == "refine_object":
            # 修正模式下不允许绘制box，只能使用点击
            if self.window():
                self.window().log_message(
                    "⚠️ 修正模式下不能绘制新的边界框，请使用点击提示（符合SAM2官方规范）", 
                    "warning"
                )
            return
        
        # 边界框模式（原有逻辑 - 仅在新对象模式下可用）
        selected_bbox = self.overlay_layer.select_bbox(x, y)
        if selected_bbox >= 0:
            self.bbox_selected.emit(selected_bbox)
            return
        next_id = len(self.overlay_layer.bboxes)
        self.overlay_layer.start_drawing(x, y, next_id)
    
    def mouseMoveEvent(self, event):
        if self.frame is None:
            return
        
        # 处理拖拽平移
        if self.is_panning and self.last_pan_pos is not None:
            # 计算鼠标移动的距离（视图坐标）
            delta = event.pos() - self.last_pan_pos
            self.last_pan_pos = event.pos()
            
            # 更新滚动条（注意方向相反）
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        
        # 原有的标注更新逻辑
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        self.overlay_layer.update_drawing(x, y)
    
    def mouseReleaseEvent(self, event):
        if self.frame is None:
            return
        
        # 检查是否在拖拽状态
        if self.is_panning:
            self.is_panning = False
            self.last_pan_pos = None
            self.viewport().setCursor(Qt.ArrowCursor)
            event.accept()
            return
        
        # scene_pos = self.mapToScene(event.pos()) # x, y not used from here
        # x, y = scene_pos.x(), scene_pos.y()
        new_bbox = self.overlay_layer.finish_drawing()
        if new_bbox:
            # center_x = int((new_bbox[0] + new_bbox[2]) / 2) # Not used
            # center_y = int((new_bbox[1] + new_bbox[3]) / 2) # Not used
            obj_id = new_bbox[4]
            self.overlay_layer.update_object_feature(obj_id, 'center', (new_bbox[0], new_bbox[1]))
            self.bbox_added.emit(new_bbox)
            self.overlay_layer.update()
            self.scene.update()
    
    def _handle_point_click(self, x, y, label):
        """处理点击提示"""
        # 获取当前选中或最后一个对象的ID
        if self.overlay_layer.annotation_mode == "refine_object" and self.overlay_layer.selected_object_id_for_refine is not None:
            obj_id = self.overlay_layer.selected_object_id_for_refine
        elif len(self.overlay_layer.bboxes) > 0:
            # 如果有选中的bbox，使用它；否则使用最后一个bbox
            if self.overlay_layer.selected_bbox >= 0:
                obj_id = int(self.overlay_layer.bboxes[self.overlay_layer.selected_bbox][4])
            else:
                obj_id = int(self.overlay_layer.bboxes[-1][4])
        else:
            # 没有任何对象，无法添加点击
            if self.window():
                self.window().log_message("❗ 请先绘制一个边界框再添加点击提示", "warning")
            return
        
        # 确保obj_id为整数类型
        obj_id = int(obj_id)
        
        # 保存点击到临时列表
        self.overlay_layer.temp_points.append((x, y))
        self.overlay_layer.temp_labels.append(label)
        self.overlay_layer.temp_points_frame_idx = self.overlay_layer.current_frame_idx  # 记录帧索引
        self.overlay_layer.current_editing_obj_id = obj_id
        
        # 更新显示
        self.overlay_layer.update()
        
        # 日志
        if self.window():
            click_type = "正向" if label == 1 else "负向"
            icon = "➕" if label == 1 else "➖"
            self.window().log_message(f"{icon} 添加{click_type}点击: ({x:.2f}, {y:.2f}) 到对象 {obj_id}", "info")
        
        # === 触发实时预览 ===
        if self.overlay_layer.preview_enabled and self.window():
            self.window()._generate_preview_for_object(obj_id)
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Home:
            self.reset_zoom()
            event.accept()
            return
        elif event.key() == Qt.Key_Delete:
            deleted_id = self.overlay_layer.delete_selected_bbox()
            if deleted_id >= 0:
                self.bbox_deleted.emit(deleted_id)
                event.accept()
                return
        elif event.key() == Qt.Key_A:
            # 应用临时点击
            obj_id = self.overlay_layer.current_editing_obj_id  # 保存obj_id
            num_saved = self.overlay_layer.save_temp_clicks()
            if num_saved > 0:
                if self.window():
                    self.window().log_message(f"✅ 已保存 {num_saved} 个点击提示", "success")
                    # === 更新预览 ===
                    if self.overlay_layer.preview_enabled and obj_id is not None:
                        self.window()._generate_preview_for_object(obj_id)
                    # === 刷新标注管理器 ===
                    if hasattr(self.window(), 'annotation_manager') and self.window().annotation_manager:
                        self.window().annotation_manager.refresh_table()
            event.accept()
            return
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            # Ctrl+S: 保存临时点击并切换到下一帧
            if self.overlay_layer.temp_points:
                obj_id = self.overlay_layer.current_editing_obj_id
                num_saved = self.overlay_layer.save_temp_clicks()
                if num_saved > 0 and self.window():
                    self.window().log_message(f"✅ 已保存 {num_saved} 个点击提示", "success")
                    # 更新预览
                    if self.overlay_layer.preview_enabled and obj_id is not None:
                        self.window()._generate_preview_for_object(obj_id)
                    # === 刷新标注管理器 ===
                    if hasattr(self.window(), 'annotation_manager') and self.window().annotation_manager:
                        self.window().annotation_manager.refresh_table()
                    # 切换到下一帧
                    if hasattr(self.window(), 'set_frame_index'):
                        current_idx = self.overlay_layer.current_frame_idx
                        self.window().set_frame_index(current_idx + 1)
            event.accept()
            return
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            # Ctrl+C: 清除临时点击
            obj_id = self.overlay_layer.current_editing_obj_id  # 保存obj_id用于更新预览
            self.overlay_layer.clear_temp_clicks()
            if self.window():
                self.window().log_message("🗑️ 清除所有临时点击", "warning")
                # === 更新预览：清除临时点击后，重新生成基于已保存标注的预览 ===
                if self.overlay_layer.preview_enabled and obj_id is not None:
                    self.window()._generate_preview_for_object(obj_id)
            event.accept()
            return
        elif event.key() == Qt.Key_H and event.modifiers() == Qt.ControlModifier:
            # Ctrl+H: 切换提示标记可见性
            success, message = self.overlay_layer.toggle_prompts_visibility()
            if self.window():
                msg_type = "info" if success else "warning"
                self.window().log_message(f"{'👁️' if success else '⚠️'} {message}", msg_type)
            event.accept()
            return
        elif event.key() in (Qt.Key_Space, Qt.Key_F, Qt.Key_D):
            if self.window() and isinstance(self.window(), QMainWindow): # Check if self.window() is valid
                self.window().keyPressEvent(event)
                event.accept()
                return
        super().keyPressEvent(event)
    
    def reset_zoom(self):
        """重置缩放到自适应状态"""
        self.resetTransform()
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.scale_factor = 1.0
        self.manual_zoom_active = False
        self.show_zoom_tip()
    
    def show_zoom_tip(self):
        """显示缩放倍数悬浮提示"""
        if self.zoom_tip_label is None:
            self.zoom_tip_label = QLabel(self.viewport())
            self.zoom_tip_label.setStyleSheet("""
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14pt;
                font-weight: bold;
            """)
            self.zoom_tip_label.setAlignment(Qt.AlignCenter)
            self.zoom_tip_label.hide()
        
        if self.manual_zoom_active:
            text = f"{int(self.scale_factor * 100)}%"
        else:
            text = "自适应"
        
        self.zoom_tip_label.setText(text)
        self.zoom_tip_label.adjustSize()
        
        # 定位到右上角
        x = self.viewport().width() - self.zoom_tip_label.width() - 15
        y = 15
        self.zoom_tip_label.move(x, y)
        self.zoom_tip_label.raise_()
        self.zoom_tip_label.show()
        
        if self.zoom_tip_timer is None:
            self.zoom_tip_timer = QTimer()
            self.zoom_tip_timer.timeout.connect(self.hide_zoom_tip)
        
        self.zoom_tip_timer.stop()
        self.zoom_tip_timer.start(2000)
    
    def hide_zoom_tip(self):
        """隐藏缩放提示"""
        if self.zoom_tip_label is not None and self.zoom_tip_label.isVisible():
            self.zoom_tip_label.hide()
    
    def show_zoom_boundary_feedback(self, attempted_scale=None):
        """显示缩放边界反馈
        
        Args:
            attempted_scale: 尝试达到的缩放倍数，用于判断是最小还是最大边界
        """
        original_geometry = self.geometry()
        
        # 如果没有传入attempted_scale，使用当前scale_factor判断
        check_scale = attempted_scale if attempted_scale is not None else self.scale_factor
        
        if check_scale < self.min_scale:
            tip_text = "已达到最小缩放 (100%)"
        else:
            tip_text = "已达到最大缩放 (1000%)"
        
        # 创建抖动动画
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(100)
        animation.setStartValue(original_geometry)
        
        # 向上移动3像素
        shake_up = original_geometry.adjusted(0, -3, 0, -3)
        animation.setKeyValueAt(0.5, shake_up)
        animation.setEndValue(original_geometry)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        
        # 临时显示边界提示
        if self.zoom_tip_label is None:
            self.show_zoom_tip()
        
        original_text = self.zoom_tip_label.text() if self.zoom_tip_label else ""
        self.zoom_tip_label.setText(tip_text)
        self.zoom_tip_label.adjustSize()
        x = self.viewport().width() - self.zoom_tip_label.width() - 15
        y = 15
        self.zoom_tip_label.move(x, y)
        self.zoom_tip_label.show()
        
        # 动画结束后恢复原始文本
        def restore_text():
            if self.manual_zoom_active:
                self.zoom_tip_label.setText(f"{int(self.scale_factor * 100)}%")
            else:
                self.zoom_tip_label.setText("自适应")
            self.zoom_tip_label.adjustSize()
            x = self.viewport().width() - self.zoom_tip_label.width() - 15
            self.zoom_tip_label.move(x, 15)
        
        animation.finished.connect(restore_text)
        animation.start()
    
    def get_manual_zoom_state(self):
        """获取当前手动缩放状态"""
        center_point = self.mapToScene(self.viewport().rect().center())
        return {
            'manual_zoom_active': self.manual_zoom_active,
            'scale_factor': self.scale_factor,
            'center_point': center_point
        }
        
    def get_bbox_list(self):
        """获取边界框列表（保持原有接口）"""
        return [[bbox[0], bbox[1], bbox[2], bbox[3]] for bbox in self.overlay_layer.bboxes]
    
    # === Phase 1 MVP: 多帧API方法 ===
    def get_multi_frame_annotations(self):
        """
        获取多帧标注数据
        
        Returns:
            dict: {frame_idx: [[x1, y1, x2, y2, obj_id], ...]}
        """
        return self.overlay_layer.get_all_annotations()
    
    def get_refinement_annotations(self):
        """
        获取refinement格式的标注数据
        
        Returns:
            dict: {frame_idx: {obj_id: {"box": [x1,y1,x2,y2], "points": [(x,y)], "labels": [0/1]}}}
        """
        return self.overlay_layer.get_refinement_annotations()
    
    def set_current_frame_index(self, frame_idx):
        """
        设置当前帧索引，更新边界框显示
        
        Args:
            frame_idx (int): 帧索引
        """
        self.overlay_layer.set_current_frame(frame_idx)
    
    def get_annotated_frame_indices(self):
        """
        获取所有已标注的帧索引
        
        Returns:
            list: 帧索引列表
        """
        return self.overlay_layer.get_annotated_frame_indices()
    
    def get_current_frame_annotation_count(self):
        """
        获取当前帧的标注数量
        
        Returns:
            int: 标注数量
        """
        return self.overlay_layer.get_annotation_count()
        
    def clear_bboxes(self):
        return self.overlay_layer.clear_bboxes()
        
    def add_object_feature(self, obj_id, center=None, major_axis=None, minor_axis=None, angle=None):
        if center:
            self.overlay_layer.update_object_feature(obj_id, 'center', center)
        if major_axis is not None:
            self.overlay_layer.update_object_feature(obj_id, 'major_axis', major_axis)
        if minor_axis is not None:
            self.overlay_layer.update_object_feature(obj_id, 'minor_axis', minor_axis)
        if angle is not None:
            self.overlay_layer.update_object_feature(obj_id, 'angle', angle)
            
    def add_track_point(self, obj_id, point):
        self.overlay_layer.add_track_point(obj_id, point)
        
    def clear_ui_elements(self):
        self.overlay_layer.clear_all()
    
    def clear(self):
        """Clear all content including frame and overlay elements"""
        # Clear frame layer
        self.frame_layer.setPixmap(QPixmap())
        
        # Reset state variables
        self.frame = None
        self.original_pixmap = None
        
        # Clear overlay layer
        self.clear_ui_elements()

class VideoLabel(MultiLayerVideoView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid #c0c0c0; background-color: #f0f0f0;")

class ResultVideoLabel(MultiLayerVideoView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid #c0c0c0; background-color: #f0f0f0;")
    
    def setVideoFrame(self, frame):
        self.set_frame(frame)
        if hasattr(self, 'process_result_frame'): # This method is not defined, but kept for compatibility
            self.process_result_frame(frame) 