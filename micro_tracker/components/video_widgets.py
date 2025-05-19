import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem, QSizePolicy, QMainWindow
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QRectF

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
        self.bboxes = []  # 边界框列表 [[x1, y1, x2, y2, id], ...]
        self.selected_bbox = -1  # 选中的边界框索引
        self.colors = COLOR # Use the imported or default COLOR
        self.tracks = {}  # 轨迹点 {obj_id: [points], ...}
        self.object_features = {}  # 对象特征(长短轴、角度等)
        self.id_labels = []  # ID标签位置和内容
        self.frame_size = (640, 480)  # 帧大小
        self.drawing = False  # 是否正在绘制
        self.current_bbox = [0, 0, 0, 0, -1]  # 当前正在绘制的边界框
        self.setAcceptHoverEvents(True)
    
    def boundingRect(self):
        return QRectF(0, 0, self.frame_size[0], self.frame_size[1])
    
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self._draw_bboxes(painter)
        self._draw_tracks(painter)
        self._draw_object_features(painter)
        self._draw_id_labels(painter)
        if self.drawing:
            self._draw_current_bbox(painter)
    
    def _draw_bboxes(self, painter):
        for i, bbox in enumerate(self.bboxes):
            color = self.colors[i % len(self.colors)]
            qcolor = QColor(color[0], color[1], color[2])
            pen = QPen(qcolor)
            pen.setWidth(2)
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
    
    def _draw_current_bbox(self, painter):
        if not self.drawing:
            return
        pen = QPen(QColor(255, 255, 0))
        pen.setWidth(2)
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
            color_idx = obj_id % len(self.colors) if obj_id >= 0 else 0
            color = self.colors[color_idx]
            qcolor = QColor(color[0], color[1], color[2])
            pen = QPen(qcolor)
            pen.setWidth(2)
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
            color_idx = obj_id % len(self.colors) if obj_id >= 0 else 0
            color = self.colors[color_idx]
            is_selected = (i == self.selected_bbox)
            text = f"obj_{obj_id}"
            if is_selected:
                text = f"* {text} *"
            text_x = int(bbox[0])
            text_y = int(bbox[1] - 5)
            painter.setPen(QColor(color[0], color[1], color[2]))
            painter.drawText(text_x, text_y, text)
    
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
    
    def start_drawing(self, x, y, next_id):
        self.drawing = True
        self.current_bbox = [x, y, x, y, next_id]
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
        if self.selected_bbox == -1:
            return -1
        deleted_id = self.bboxes[self.selected_bbox][4]
        del self.bboxes[self.selected_bbox]
        if deleted_id in self.tracks:
            del self.tracks[deleted_id]
        if deleted_id in self.object_features:
            del self.object_features[deleted_id]
        self.selected_bbox = -1
        self.update()
        return deleted_id
    
    def clear_bboxes(self):
        count = len(self.bboxes)
        self.bboxes = []
        self.selected_bbox = -1
        self.tracks = {}
        self.object_features = {}
        self.update()
        return count
    
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
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.scale_factor = 1.0
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
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.scale_factor = 1.0
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.frame is not None:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def mousePressEvent(self, event):
        if self.frame is None:
            return
        self.setFocus()
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        selected_bbox = self.overlay_layer.select_bbox(x, y)
        if selected_bbox >= 0:
            self.bbox_selected.emit(selected_bbox)
            return
        next_id = len(self.overlay_layer.bboxes)
        self.overlay_layer.start_drawing(x, y, next_id)
    
    def mouseMoveEvent(self, event):
        if self.frame is None:
            return
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        self.overlay_layer.update_drawing(x, y)
    
    def mouseReleaseEvent(self, event):
        if self.frame is None:
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
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            deleted_id = self.overlay_layer.delete_selected_bbox()
            if deleted_id >= 0:
                self.bbox_deleted.emit(deleted_id)
                event.accept()
                return
        elif event.key() in (Qt.Key_Space, Qt.Key_F, Qt.Key_D):
            if self.window() and isinstance(self.window(), QMainWindow): # Check if self.window() is valid
                self.window().keyPressEvent(event)
                event.accept()
                return
        super().keyPressEvent(event)
        
    def get_bbox_list(self):
        return [[bbox[0], bbox[1], bbox[2], bbox[3]] for bbox in self.overlay_layer.bboxes]
        
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