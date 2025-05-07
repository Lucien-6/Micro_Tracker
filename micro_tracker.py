import sys
import os
import cv2
import numpy as np
import torch
import warnings # Add import for warnings module
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QFileDialog, QLineEdit, QSlider, QCheckBox,
                           QComboBox, QGroupBox, QFormLayout, QProgressBar, QMessageBox, 
                           QTabWidget, QSplitter, QTextEdit, QSizePolicy, QGraphicsView, 
                           QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont, QIcon, QTextCursor, QRegExpValidator, QTransform
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRectF, QTimer, QSize, QMutex, QDateTime, QRegExp, QPointF
import subprocess
from pathlib import Path
import json
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time

# 定义全局样式
STYLE = """
QMainWindow {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QTabWidget::pane {
    border: 1px solid #e0e0e0;
    background-color: #ffffff;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #f0f2f5;
    border: 1px solid #e0e0e0;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 100px;
    font-size: 10.5pt;
    color: #666666;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-bottom-color: #ffffff;
    color: #2979ff;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #e6f0ff;
}

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    margin-top: 12px;
    font-weight: bold;
    font-size: 10pt;
    color: #444444;
    padding-top: 6px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background-color: #ffffff;
}

QPushButton {
    background-color: #2979ff;
    color: white;
    border: none;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 9.5pt;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #448aff;
}

QPushButton:pressed {
    background-color: #2962ff;
}

QPushButton:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
}

QLineEdit {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 3px 6px;
    min-height: 18px;
    background-color: white;
    selection-background-color: #bbdefb;
}

QLineEdit:focus {
    border: 1px solid #2979ff;
}

QTextEdit {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: white;
    selection-background-color: #bbdefb;
    padding: 4px;
}

QLabel {
    color: #424242;
    font-size: 9.5pt;
}

QCheckBox {
    spacing: 8px;
    color: #424242;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid #bdbdbd;
}

QCheckBox::indicator:checked {
    background-color: #2979ff;
    border: 1px solid #2979ff;
    image: url(icons/check.png);
}

QCheckBox::indicator:hover {
    border: 1px solid #2979ff;
}

QSlider::groove:horizontal {
    border: 1px solid #e0e0e0;
    height: 8px;
    background: #f5f5f5;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #2979ff;
    border: none;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #448aff;
}

QProgressBar {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    text-align: center;
    background-color: #f5f5f5;
    height: 20px;
    font-size: 9pt;
    color: #424242;
}

QProgressBar::chunk {
    background-color: #4caf50;
    border-radius: 3px;
}

QComboBox {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 2px 6px;
    padding-right: 25px;  /* 为下拉箭头留出空间 */
    background-color: white;
    min-height: 20px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: none;
    padding-right: 5px;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
    image: url(icons/dropdown.png);
    margin-right: 5px;
}

/* 默认箭头样式 */
QComboBox::down-arrow:default {
    width: 12px;
    height: 12px;
    image: url(icons/dropdown.png);
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    border: 1px solid #e0e0e0;
    selection-background-color: #bbdefb;
    border-radius: 0 0 4px 4px;
}

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

QScrollBar:horizontal {
    border: none;
    background: #f0f0f0;
    height: 14px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #505050;  /* 黑灰色 */
    min-width: 30px;
    margin: 2px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #404040;  /* 更深的黑灰色 */
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: #f0f0f0;
}

QSplitter::handle {
    background-color: #e0e0e0;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}
"""

# 自定义MatplotlibCanvas类
class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('y')
        self.axes.grid(True, linestyle='--', alpha=0.7)
        self.fig.tight_layout()

class VideoThread(QThread):
    """视频读取线程，用于显示视频第一帧和滑动浏览视频帧"""
    frame_ready = pyqtSignal(np.ndarray)
    frame_index_changed = pyqtSignal(int)  # 添加帧索引变化信号
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True
        self.paused = True  # 默认启动时处于暂停状态
        self.frame_index = 0
        self.total_frames = 0
        self.fps = 30  # 默认帧率，会在run()中更新为实际帧率
        self.frame_time_ms = 33  # 默认帧间隔(毫秒)，会在run()中更新
        self.cap = None
        self.mutex = QMutex()  # 添加互斥锁保护共享数据
        self.frame_changed = False  # 标记是否请求了新帧
        self.last_frame_time = 0  # 上一帧的时间戳
        
    def run(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print(f"Error: Could not open video file {self.video_path}")
            return
            
        # 获取视频信息
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0:
            self.fps = 30  # 如果无法获取帧率，使用默认值
        
        # 计算帧间隔时间(毫秒)
        self.frame_time_ms = int(1000 / self.fps)
        
        # 立即读取第一帧
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.cap.read()
        if ret:
            self.frame_ready.emit(frame)
            self.frame_index_changed.emit(0)  # 发送初始帧索引信号
        
        self.last_frame_time = QDateTime.currentMSecsSinceEpoch()
        
        while self.running:
            current_time = QDateTime.currentMSecsSinceEpoch()
            
            self.mutex.lock()
            paused = self.paused
            current_index = self.frame_index
            frame_changed = self.frame_changed
            self.frame_changed = False  # 重置标志
            self.mutex.unlock()
            
            if not paused or frame_changed:
                # 设置视频位置并读取帧
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_index)
                ret, frame = self.cap.read()
                
                if ret:
                    self.frame_ready.emit(frame)
                    self.frame_index_changed.emit(current_index)  # 发送帧索引变化信号
                    
                    # 更新时间戳
                    self.last_frame_time = current_time
                    
                    # 如果不是暂停状态且没有特定帧的请求，则自动前进到下一帧
                    if not paused and not frame_changed:
                        self.mutex.lock()
                        next_index = (current_index + 1) % self.total_frames
                        self.frame_index = next_index
                        self.mutex.unlock()
                    
                else:
                    # 读取失败，可能到达视频末尾，回到开始
                    self.mutex.lock()
                    self.frame_index = 0
                    if not paused:  # 如果是自动播放模式，则循环播放
                        self.frame_changed = True  # 标记需要重新加载第一帧
                    else:
                        self.paused = True  # 如果是手动模式，则暂停
                    self.mutex.unlock()
            
            # 计算下一帧应该等待的时间
            if not paused:
                # 基于上一帧的时间和帧率计算下一帧应显示的时间
                next_frame_time = self.last_frame_time + self.frame_time_ms
                current_time = QDateTime.currentMSecsSinceEpoch()
                
                # 计算需要等待的时间
                wait_time = next_frame_time - current_time
                
                # 如果需要等待，则等待合适的时间；否则立即处理下一帧
                if wait_time > 1:
                    self.msleep(int(wait_time))
                else:
                    # 如果处理时间已经超过了帧间隔，至少休眠1毫秒避免CPU占用过高
                    self.msleep(1)
            else:
                # 如果暂停，则较长时间休眠以减少CPU使用
                self.msleep(100)
        
        if self.cap:
            self.cap.release()
    
    def stop(self):
        self.running = False
        self.wait()
    
    def set_frame_index(self, index):
        """设置要显示的帧索引"""
        self.mutex.lock()
        self.frame_index = max(0, min(index, self.total_frames - 1))
        self.frame_changed = True  # 标记需要切换到新帧
        self.mutex.unlock()
        
    def toggle_pause(self):
        """切换暂停/播放状态"""
        self.mutex.lock()
        self.paused = not self.paused
        # 重置时间戳，保证从暂停恢复播放时帧率正确
        if not self.paused:
            self.last_frame_time = QDateTime.currentMSecsSinceEpoch()
        self.mutex.unlock()

class ProcessingThread(QThread):
    """视频处理线程"""
    progress_update = pyqtSignal(str)  # 进度更新信号
    progress_percent = pyqtSignal(int)  # 进度百分比信号
    processing_finished = pyqtSignal(bool, str)  # 处理完成信号，参数为(成功与否, 消息)
    frame_processed = pyqtSignal(np.ndarray, int, int)  # 帧处理信号，参数为(帧, 当前索引, 总帧数)
    
    def __init__(self, args, bbox_list):
        super().__init__()
        self.args = args
        self.bbox_list = bbox_list
        self.is_running = True
    
    def run(self):
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 发送初始化中的消息
            self.progress_update.emit("正在初始化SAM2模型...")
            
            # 获取系统信息
            import platform
            system_info = platform.platform()
            python_version = platform.python_version()
            self.progress_update.emit(f"系统信息: {system_info}")
            self.progress_update.emit(f"Python版本: {python_version}")
            
            # 检查设备
            if self.args.device.startswith("cuda"):
                import torch
                if torch.cuda.is_available():
                    device_id = 0
                    if ":" in self.args.device:
                        device_id = int(self.args.device.split(":")[-1])
                    gpu_name = torch.cuda.get_device_name(device_id)
                    self.progress_update.emit(f"GPU: {gpu_name}")
                    self.progress_update.emit(f"CUDA版本: {torch.version.cuda}")
                else:
                    self.progress_update.emit("警告: CUDA不可用，已回退到CPU")
                    self.args.device = "cpu"
            
            # 导入必要的库
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from scripts.process_video import main, process_video_in_chunks
            
            # 保存 bbox_list 到临时文件，用于兼容原始脚本
            bbox_file = Path("temp_bbox_list.json")
            with open(bbox_file, "w") as f:
                json.dump(self.bbox_list, f)
            
            # 获取视频信息
            cap = cv2.VideoCapture(self.args.video_path)
            if not cap.isOpened():
                raise Exception(f"无法打开视频: {self.args.video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            
            # 设置进度条最大值
            self.progress_percent.emit(0)
            
            # 根据视频帧数决定使用哪个处理函数
            use_chunks = False
            if total_frames > 1000:  # 如果视频超过1000帧，使用分块处理
                use_chunks = True
                self.progress_update.emit(f"视频较长 ({total_frames} 帧, {duration:.1f} 秒)，将使用分块处理...")
            
            # 设置进度回调函数
            last_progress_time = time.time()
            last_frame_count = 0
            
            def progress_callback(current_frame, total):
                nonlocal last_progress_time, last_frame_count
                if not self.is_running:
                    return False  # 返回False表示终止处理
                
                # 计算进度百分比
                percent = int((current_frame / total) * 100)
                self.progress_percent.emit(percent)
                
                # 限制更新频率，避免大量日志
                current_time = time.time()
                if current_time - last_progress_time > 1.0 or current_frame == total - 1:
                    # 计算处理速度
                    time_diff = current_time - last_progress_time
                    if time_diff > 0:
                        frame_diff = current_frame - last_frame_count
                        fps = frame_diff / time_diff
                        
                        # 计算预计剩余时间
                        remaining_frames = total - current_frame
                        eta = remaining_frames / fps if fps > 0 else 0
                        eta_min = int(eta // 60)
                        eta_sec = int(eta % 60)
                        
                        # 更新进度信息
                        self.progress_update.emit(
                            f"处理中: {current_frame}/{total} 帧 ({percent}%) - "
                            f"速度: {fps:.1f} FPS, 预计剩余时间: {eta_min}分{eta_sec}秒"
                        )
                    
                    # 更新上次进度时间和帧数
                    last_progress_time = current_time
                    last_frame_count = current_frame
                
                return True  # 返回True表示继续处理
            
            # 修改原始Args对象，添加进度回调
            self.args.progress_callback = progress_callback
            self.progress_update.emit(f"正在加载模型到{self.args.device}设备...")
            self.progress_update.emit("处理开始，这可能需要几分钟时间...")
            
            # 执行处理
            if use_chunks:
                # 使用500帧为一块进行处理，而不是基于时间
                chunk_frames = 500
                self.progress_update.emit(f"将视频分为{(total_frames + chunk_frames - 1) // chunk_frames}个块进行处理，每块最多{chunk_frames}帧")
                process_video_in_chunks(self.args, self.bbox_list, chunk_frames=chunk_frames)
            else:
                main(self.args, self.bbox_list)
            
            # 处理完成
            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            
            self.progress_update.emit(f"处理完成，总耗时: {minutes}分{seconds}秒")
            self.progress_update.emit(f"处理速度: {total_frames / elapsed_time:.1f} FPS")
            
            # 尝试加载处理后的视频进行预览
            try:
                if self.args.save_to_video:
                    self.progress_update.emit("正在加载预览...")
                    preview_cap = cv2.VideoCapture(self.args.video_output_path)
                    frame_count = int(preview_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
                    for i in range(frame_count):
                        ret, frame = preview_cap.read()
                        if ret:
                            self.frame_processed.emit(frame, i, frame_count)
                            # 放慢预览速度
                            self.msleep(30)
                        else:
                            break
                    
                    preview_cap.release()
            except Exception as e:
                self.progress_update.emit(f"加载处理后的视频预览时出错: {str(e)}")
            
            # 处理成功
            self.processing_finished.emit(True, "视频处理成功")
            
        except Exception as e:
            import traceback
            error_message = str(e)
            stack_trace = traceback.format_exc()
            self.progress_update.emit(f"错误: {error_message}")
            self.progress_update.emit(f"堆栈跟踪:\n{stack_trace}")
            self.processing_finished.emit(False, error_message)
        finally:
            # 清理临时文件
            if 'bbox_file' in locals() and bbox_file.exists():
                bbox_file.unlink()
    
    def stop(self):
        """停止处理线程"""
        self.is_running = False

# 添加高分辨率UI图层类
class OverlayLayer(QGraphicsItem):
    """高分辨率UI元素覆盖层"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 高分辨率比例因子，使覆盖层分辨率高于视频
        self.resolution_factor = 2.0
        self.bboxes = []  # 边界框列表 [[x1, y1, x2, y2, id], ...]
        self.selected_bbox = -1  # 选中的边界框索引
        self.colors = []  # 颜色列表
        self.tracks = {}  # 轨迹点 {obj_id: [points], ...}
        self.object_features = {}  # 对象特征(长短轴、角度等)
        self.id_labels = []  # ID标签位置和内容
        self.frame_size = (640, 480)  # 帧大小
        self.drawing = False  # 是否正在绘制
        self.current_bbox = [0, 0, 0, 0, -1]  # 当前正在绘制的边界框
        
        # 使用预定义的颜色列表
        try:
            from utils.color import COLOR
            self.colors = COLOR
        except ImportError:
            # 如果无法导入，使用默认颜色列表
            self.colors = [
                (0, 255, 0),    # 绿色
                (255, 0, 0),    # 蓝色
                (0, 0, 255),    # 红色
                (255, 255, 0),  # 青色
                (255, 0, 255),  # 品红色
                (0, 255, 255),  # 黄色
                (128, 0, 0),    # 深蓝色
                (0, 128, 0),    # 深绿色
                (0, 0, 128),    # 深红色
                (128, 128, 0),  # 深青色
            ]
        
        # 设置为可接收悬停事件
        self.setAcceptHoverEvents(True)
    
    def boundingRect(self):
        """返回图层的边界矩形"""
        # 使用帧大小乘以分辨率因子作为边界
        return QRectF(0, 0, self.frame_size[0], self.frame_size[1])
    
    def paint(self, painter, option, widget):
        """绘制所有UI元素"""
        # 启用抗锯齿
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # 绘制边界框
        self._draw_bboxes(painter)
        
        # 绘制轨迹线
        self._draw_tracks(painter)
        
        # 绘制对象特征(长短轴、角度等)
        self._draw_object_features(painter)
        
        # 绘制ID标签
        self._draw_id_labels(painter)
        
        # 如果正在绘制，显示当前边界框
        if self.drawing:
            self._draw_current_bbox(painter)
    
    def _draw_bboxes(self, painter):
        """绘制所有边界框"""
        for i, bbox in enumerate(self.bboxes):
            color = self.colors[i % len(self.colors)]
            qcolor = QColor(color[0], color[1], color[2])
            
            # 设置画笔
            pen = QPen(qcolor)
            pen.setWidth(2)  # 设置线宽
            
            if i == self.selected_bbox:
                # 选中的边界框使用虚线
                pen.setStyle(Qt.DashLine)
                pen.setWidth(3)  # 选中边界框线宽稍大
            
            painter.setPen(pen)
            # 明确设置无填充
            painter.setBrush(Qt.NoBrush)
            
            # 绘制矩形，确保使用整数坐标
            painter.drawRect(
                int(bbox[0]), 
                int(bbox[1]), 
                int(bbox[2] - bbox[0]), 
                int(bbox[3] - bbox[1])
            )
    
    def _draw_current_bbox(self, painter):
        """绘制当前正在绘制的边界框"""
        if not self.drawing:
            return
        
        # 设置画笔 - 使用黄色
        pen = QPen(QColor(255, 255, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        # 明确设置无填充
        painter.setBrush(Qt.NoBrush)
        
        # 绘制矩形，确保使用整数坐标
        painter.drawRect(
            int(self.current_bbox[0]), 
            int(self.current_bbox[1]), 
            int(self.current_bbox[2] - self.current_bbox[0]), 
            int(self.current_bbox[3] - self.current_bbox[1])
        )
    
    def _draw_tracks(self, painter):
        """绘制对象轨迹"""
        for obj_id, points in self.tracks.items():
            if len(points) < 2:
                continue
            
            # 获取颜色
            color_idx = obj_id % len(self.colors) if obj_id >= 0 else 0
            color = self.colors[color_idx]
            qcolor = QColor(color[0], color[1], color[2])
            
            # 设置画笔
            pen = QPen(qcolor)
            pen.setWidth(2)
            painter.setPen(pen)
            
            # 绘制轨迹线，确保使用整数坐标
            for i in range(1, len(points)):
                painter.drawLine(
                    int(points[i-1][0]), int(points[i-1][1]),
                    int(points[i][0]), int(points[i][1])
                )
    
    def _draw_object_features(self, painter):
        """绘制对象特征(长短轴等)"""
        for obj_id, features in self.object_features.items():
            if 'center' not in features:
                continue
            
            center = features['center']
            
            # 如果有主轴和次轴，绘制它们
            if 'major_axis' in features and 'minor_axis' in features and 'angle' in features:
                major_axis = features['major_axis']
                minor_axis = features['minor_axis']
                angle = features['angle']
                
                # 绘制主轴（红色）
                pen = QPen(QColor(255, 0, 0))
                pen.setWidth(2)
                painter.setPen(pen)
                
                # 计算主轴端点
                angle_rad = np.deg2rad(angle)
                dx_major = major_axis * np.cos(angle_rad)
                dy_major = major_axis * np.sin(angle_rad)
                
                # 绘制主轴，确保使用整数坐标
                painter.drawLine(
                    int(center[0] - dx_major), int(center[1] - dy_major),
                    int(center[0] + dx_major), int(center[1] + dy_major)
                )
                
                # 绘制次轴（蓝色）
                pen = QPen(QColor(0, 0, 255))
                pen.setWidth(2)
                painter.setPen(pen)
                
                # 计算次轴端点
                minor_angle_rad = angle_rad + np.pi/2
                dx_minor = minor_axis * np.cos(minor_angle_rad)
                dy_minor = minor_axis * np.sin(minor_angle_rad)
                
                # 绘制次轴，确保使用整数坐标
                painter.drawLine(
                    int(center[0] - dx_minor), int(center[1] - dy_minor),
                    int(center[0] + dx_minor), int(center[1] + dy_minor)
                )
    
    def _draw_id_labels(self, painter):
        """绘制ID标签 - 显示在边界框左上角外部"""
        # 设置字体
        font = QFont("Arial", 10)
        font.setBold(True)
        painter.setFont(font)
        
        for i, bbox in enumerate(self.bboxes):
            obj_id = bbox[4]
            
            # 获取颜色
            color_idx = obj_id % len(self.colors) if obj_id >= 0 else 0
            color = self.colors[color_idx]
            
            # 为选中的边界框添加特殊标记
            is_selected = (i == self.selected_bbox)
            
            # 设置文本
            text = f"obj_{obj_id}"
            if is_selected:
                text = f"* {text} *"  # 为选中的边界框添加标记
            
            # 设置文本位置 - 边界框左上角外部
            text_x = int(bbox[0])
            text_y = int(bbox[1] - 5)  # 在边界框上方5个像素处
            
            # 直接绘制文本，无背景
            painter.setPen(QColor(color[0], color[1], color[2]))
            painter.drawText(text_x, text_y, text)
    
    def update_frame_size(self, width, height):
        """更新底层视频帧大小"""
        self.frame_size = (width, height)
        # 更新图层边界
        self.prepareGeometryChange()
    
    def clear_all(self):
        """清除所有UI元素"""
        self.bboxes = []
        self.selected_bbox = -1
        self.tracks = {}
        self.object_features = {}
        self.id_labels = []
        self.drawing = False
        self.current_bbox = [0, 0, 0, 0, -1]
        # 触发重绘
        self.update()
    
    def start_drawing(self, x, y, next_id):
        """开始绘制新边界框"""
        self.drawing = True
        self.current_bbox = [x, y, x, y, next_id]
        self.update()
    
    def update_drawing(self, x, y):
        """更新正在绘制的边界框"""
        if not self.drawing:
            return
        
        self.current_bbox[2] = x
        self.current_bbox[3] = y
        self.update()
    
    def finish_drawing(self):
        """完成绘制当前边界框"""
        if not self.drawing:
            return None
        
        self.drawing = False
        
        # 确保边界框的坐标是正确排序的 (左上, 右下)
        x1 = min(self.current_bbox[0], self.current_bbox[2])
        y1 = min(self.current_bbox[1], self.current_bbox[3])
        x2 = max(self.current_bbox[0], self.current_bbox[2])
        y2 = max(self.current_bbox[1], self.current_bbox[3])
        
        # 检查边界框大小是否有效
        bbox_id = self.current_bbox[4]
        if (x2 - x1) > 10 and (y2 - y1) > 10:
            self.bboxes.append([x1, y1, x2, y2, bbox_id])
            # 添加轨迹初始点
            self.tracks[bbox_id] = [(int((x1+x2)/2), int((y1+y2)/2))]
            # 添加对象特征 - 默认将中心点放在边界框左上角，用于显示ID标签
            self.object_features[bbox_id] = {
                'center': (x1, y1)
            }
            
            # 立即更新显示
            self.update()
            
            # 返回新绘制的边界框
            return [x1, y1, x2, y2, bbox_id]
        
        return None
    
    def select_bbox(self, x, y):
        """选择点击位置的边界框"""
        old_selected = self.selected_bbox
        self.selected_bbox = -1
        
        for i, bbox in enumerate(self.bboxes):
            if (bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]):
                self.selected_bbox = i
                self.update()
                return i
        
        # 如果选择状态发生变化，更新显示
        if old_selected != self.selected_bbox:
            self.update()
        
        return -1
    
    def delete_selected_bbox(self):
        """删除选中的边界框"""
        if self.selected_bbox == -1:
            return -1
        
        deleted_id = self.bboxes[self.selected_bbox][4]
        del self.bboxes[self.selected_bbox]
        
        # 如果存在，也删除轨迹和特征
        if deleted_id in self.tracks:
            del self.tracks[deleted_id]
        if deleted_id in self.object_features:
            del self.object_features[deleted_id]
        
        # 重置选中状态
        self.selected_bbox = -1
        self.update()
        
        return deleted_id
    
    def clear_bboxes(self):
        """清除所有边界框"""
        count = len(self.bboxes)
        self.bboxes = []
        self.selected_bbox = -1
        self.tracks = {}
        self.object_features = {}
        self.update()
        return count
    
    def update_object_feature(self, obj_id, feature_name, value):
        """更新对象特征"""
        if obj_id not in self.object_features:
            self.object_features[obj_id] = {}
        
        self.object_features[obj_id][feature_name] = value
        self.update()
    
    def add_track_point(self, obj_id, point):
        """添加轨迹点"""
        if obj_id not in self.tracks:
            self.tracks[obj_id] = []
        
        self.tracks[obj_id].append(point)
        self.update()

# 多层视频视图类
class MultiLayerVideoView(QGraphicsView):
    """多层视频视图，支持高分辨率UI元素"""
    
    # 添加信号定义
    bbox_added = pyqtSignal(list)  # 添加边界框时发出信号
    bbox_selected = pyqtSignal(int)  # 选择边界框时发出信号
    bbox_deleted = pyqtSignal(int)  # 删除边界框时发出信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("border: 1px solid #c0c0c0; background-color: #f0f0f0;")
        
        # 设置焦点策略，使其能接收键盘事件
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 创建场景
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # 视频帧图层（底层）
        self.frame_layer = QGraphicsPixmapItem()
        self.scene.addItem(self.frame_layer)
        
        # 高分辨率UI元素图层（顶层）
        self.overlay_layer = OverlayLayer()
        self.scene.addItem(self.overlay_layer)
        
        # 启用抗锯齿
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 启用视图转换
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        # 设置视图的默认属性
        self.scale_factor = 1.0
        self.frame = None
        self.original_pixmap = None
    
    def set_frame(self, frame):
        """设置视频帧"""
        self.frame = frame
        if self.frame is not None:
            self._update_display()
    
    def _update_display(self):
        """更新显示"""
        if self.frame is None:
            return
        
        # 转换OpenCV帧为QPixmap
        h, w, c = self.frame.shape
        bytes_per_line = c * w
        q_img = QImage(self.frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
        
        # 保存原始像素图以便在大小变化时使用
        self.original_pixmap = pixmap
        
        # 设置视频帧图层
        self.frame_layer.setPixmap(pixmap)
        
        # 更新UI覆盖层大小
        self.overlay_layer.update_frame_size(w, h)
        
        # 重置视图以适应新内容
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.scale_factor = 1.0
    
    def resizeEvent(self, event):
        """处理大小调整事件"""
        super().resizeEvent(event)
        
        # 当视图大小改变时，调整视图以适应场景
        if self.frame is not None:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if self.frame is None:
            return
        
        # 获取焦点，以便能接收键盘事件
        self.setFocus()
        
        # 将视图坐标转换为场景坐标
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        
        # 检查是否点击了现有边界框
        selected_bbox = self.overlay_layer.select_bbox(x, y)
        
        if selected_bbox >= 0:
            # 发出选择信号
            self.bbox_selected.emit(selected_bbox)
            return
        
        # 否则开始绘制新边界框
        next_id = len(self.overlay_layer.bboxes)
        self.overlay_layer.start_drawing(x, y, next_id)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.frame is None:
            return
        
        # 将视图坐标转换为场景坐标
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        
        # 更新正在绘制的边界框
        self.overlay_layer.update_drawing(x, y)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.frame is None:
            return
        
        # 获取视图坐标转换为场景坐标
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        
        # 完成绘制边界框
        new_bbox = self.overlay_layer.finish_drawing()
        
        # 如果创建了新边界框，发出信号并立即添加ID标签
        if new_bbox:
            # 添加中心点作为标签位置
            center_x = int((new_bbox[0] + new_bbox[2]) / 2)
            center_y = int((new_bbox[1] + new_bbox[3]) / 2)
            obj_id = new_bbox[4]
            
            # 在边界框左上角外部添加ID标签位置
            self.overlay_layer.update_object_feature(obj_id, 'center', (new_bbox[0], new_bbox[1]))
            
            # 发送添加信号
            self.bbox_added.emit(new_bbox)
            
            # 强制更新场景
            self.overlay_layer.update()
            self.scene.update()
    
    def keyPressEvent(self, event):
        """键盘按键事件"""
        # 删除选中的边界框
        if event.key() == Qt.Key_Delete:
            deleted_id = self.overlay_layer.delete_selected_bbox()
            if deleted_id >= 0:
                # 发出删除信号
                self.bbox_deleted.emit(deleted_id)
                event.accept()
                return
        
        # 处理播放控制键
        elif event.key() in (Qt.Key_Space, Qt.Key_F, Qt.Key_D):
            # 将键盘事件传递给主窗口
            if self.window() and isinstance(self.window(), QMainWindow):
                self.window().keyPressEvent(event)
                event.accept()
                return
        
        super().keyPressEvent(event)
    
    def get_bbox_list(self):
        """返回用于处理的边界框列表，格式为 [[x1, y1, x2, y2], ...]"""
        return [[bbox[0], bbox[1], bbox[2], bbox[3]] for bbox in self.overlay_layer.bboxes]
    
    def clear_bboxes(self):
        """清除所有边界框"""
        return self.overlay_layer.clear_bboxes()
    
    def add_object_feature(self, obj_id, center=None, major_axis=None, minor_axis=None, angle=None):
        """添加对象特征"""
        if center:
            self.overlay_layer.update_object_feature(obj_id, 'center', center)
        if major_axis is not None:
            self.overlay_layer.update_object_feature(obj_id, 'major_axis', major_axis)
        if minor_axis is not None:
            self.overlay_layer.update_object_feature(obj_id, 'minor_axis', minor_axis)
        if angle is not None:
            self.overlay_layer.update_object_feature(obj_id, 'angle', angle)
    
    def add_track_point(self, obj_id, point):
        """添加轨迹点"""
        self.overlay_layer.add_track_point(obj_id, point)
    
    def clear_ui_elements(self):
        """清除所有UI元素但保留视频帧"""
        self.overlay_layer.clear_all()

# 修改VideoLabel类，使用MultiLayerVideoView实现
class VideoLabel(MultiLayerVideoView):
    """可绘制边界框的视频标签控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid #c0c0c0; background-color: #f0f0f0;")

# 修改ResultVideoLabel类，使用MultiLayerVideoView实现
class ResultVideoLabel(MultiLayerVideoView):
    """处理结果视频预览标签，支持自适应缩放"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid #c0c0c0; background-color: #f0f0f0;")
    
    def setVideoFrame(self, frame):
        """设置视频帧并显示"""
        self.set_frame(frame)
        
        # 解析视频帧中的UI元素，提取到覆盖层
        # 注意：这可能需要针对具体结果视频的内容格式进行定制
        if hasattr(self, 'process_result_frame'):
            self.process_result_frame(frame)

# 需要更新ProcessingThread类中的frame_processed信号处理，将UI元素分离
def modify_processing_thread_frame_processed_signal(self, frame, current_idx, total_frames):
    """处理视频帧并提取UI元素数据"""
    # 原始代码将UI元素直接绘制在视频帧上
    # 现在需要分离UI元素数据，以便在高分辨率图层上绘制
    
    # 这里需要根据视频帧格式分析提取UI元素数据
    # 如边界框位置、轨迹线点、对象ID和位置等
    
    # 示例代码，实际处理需要根据具体业务逻辑调整
    # self.ui_elements_data = extract_ui_elements(frame)
    # self.result_label.set_ui_elements(self.ui_elements_data)
    
    # 发送处理后的帧和UI元素数据
    self.frame_processed.emit(frame, current_idx, total_frames)

# 需要更新FilterVideoThread类中的frame_ready信号处理，将UI元素分离
def modify_filter_video_thread_frame_ready_signal(self, frame):
    """处理过滤后的视频帧并提取UI元素数据"""
    # 与ProcessingThread类似，需要提取UI元素数据
    
    # 示例代码，实际处理需要根据具体业务逻辑调整
    # self.ui_elements_data = extract_filter_ui_elements(frame)
    # self.filter_video_label.set_ui_elements(self.ui_elements_data)
    
    # 发送处理后的帧和UI元素数据
    self.frame_ready.emit(frame)

class FilterMaskThread(QThread):
    """掩膜筛选线程，用于分析、筛选掩膜并生成预览视频"""
    progress_update = pyqtSignal(str)  # 进度更新信号
    progress_percent = pyqtSignal(int)  # 进度百分比信号
    filter_finished = pyqtSignal(bool, str)  # 筛选完成信号，参数为(成功与否, 消息)
    frame_processed = pyqtSignal(np.ndarray, int, int)  # 帧处理信号，参数为(帧, 当前索引, 总帧数)
    stats_update = pyqtSignal(int, int)  # 统计信息更新信号，参数为(总对象数, 通过筛选的对象数)
    
    def __init__(self, masks_dir, fps=1.0, um_per_pixel=1.0, filter_params=None):
        super().__init__()
        self.masks_dir = masks_dir
        self.fps = fps
        self.um_per_pixel = um_per_pixel
        self.filter_params = filter_params or {}
        self.is_running = True
        
        # 存储筛选结果
        self.filtered_masks = []  # 存储筛选后的掩膜数据
        self.object_trajectories = {}  # 存储对象轨迹数据
        self.filtered_metadata = {}  # 存储已筛选对象的元数据(面积、中心点、长轴、短轴、角度等)
        
        # 处理中间数据
        self.all_masks = []  # 所有掩膜文件
        self.total_objects = 0  # 总对象数
        self.passed_objects = 0  # 通过筛选的对象数
        self.original_masks = []  # 原始掩膜数据
        
        # 添加记录对象筛选结果和原因的字典
        self.object_filter_results = {}  # 格式: {obj_id: {"result": "passed|filtered|truncated", "reason": "原因描述"}}
    
    def run(self):
        try:
            self.progress_update.emit("正在加载掩膜图片...")
            self.progress_percent.emit(0)
            
            # 1. 加载所有掩膜图片
            mask_files = sorted([f for f in os.listdir(self.masks_dir) if f.endswith('.png') and f.startswith('frame_')])
            if not mask_files:
                raise Exception(f"未在 {self.masks_dir} 中找到掩膜图片")
            
            self.all_masks = mask_files
            total_frames = len(mask_files)
            self.progress_update.emit(f"找到 {total_frames} 个掩膜图片")
            
            # 2. 分析所有掩膜，提取对象ID和轨迹
            self.progress_update.emit("正在分析掩膜数据...")
            
            # 首先读取所有掩膜数据
            masks_data = []
            object_ids = set()
            
            for i, mask_file in enumerate(mask_files):
                # 更新进度
                percent = int((i / total_frames) * 30)  # 占总进度的30%
                self.progress_percent.emit(percent)
                
                # 读取掩膜
                mask_path = os.path.join(self.masks_dir, mask_file)
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                
                if mask is None:
                    self.progress_update.emit(f"警告: 无法读取掩膜文件 {mask_file}")
                    continue
                
                # 提取当前掩膜中的所有对象ID
                unique_ids = np.unique(mask)
                unique_ids = unique_ids[unique_ids > 0]  # 排除背景(值为0)
                
                # 更新所有对象ID集合
                for obj_id in unique_ids:
                    object_ids.add(int(obj_id))
                
                # 存储掩膜数据
                masks_data.append(mask)
                
                # 每处理10个掩膜更新一次日志
                if i % 10 == 0 or i == total_frames - 1:
                    self.progress_update.emit(f"已处理 {i+1}/{total_frames} 个掩膜图片")
            
            self.original_masks = masks_data
            self.total_objects = len(object_ids)
            self.progress_update.emit(f"共检测到 {self.total_objects} 个对象")
            
            # 3. 应用筛选条件
            self.progress_update.emit("开始应用筛选条件...")
            
            # 初始化每个对象的有效帧范围 (默认全部有效)
            object_valid_frames = {obj_id: (0, total_frames-1) for obj_id in object_ids}
            
            # 收集所有对象的轨迹数据
            self.progress_update.emit("正在计算对象属性...")
            
            # 存储所有对象在每一帧的数据
            object_data = {obj_id: [] for obj_id in object_ids}
            
            # 对每一帧处理
            for frame_idx, mask in enumerate(masks_data):
                # 更新进度
                percent = 30 + int((frame_idx / total_frames) * 30)  # 占总进度的30%到60%
                self.progress_percent.emit(percent)
                
                # 处理当前帧中的每个对象
                frame_objects = np.unique(mask)
                frame_objects = frame_objects[frame_objects > 0]  # 排除背景(值为0)
                
                for obj_id in frame_objects:
                    # 提取当前对象的掩膜
                    obj_mask = (mask == obj_id).astype(np.uint8) * 255
                    
                    # 计算对象的位置和形状
                    contours, _ = cv2.findContours(obj_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if not contours:
                        continue
                    
                    # 获取最大轮廓
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    # 计算面积 (单位: μm²)
                    area_pixels = cv2.contourArea(largest_contour)
                    area_um2 = area_pixels * (self.um_per_pixel ** 2)
                    
                    # 计算质心
                    M = cv2.moments(largest_contour)
                    if M["m00"] == 0:
                        continue
                    
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # 转换为实际单位 (μm)
                    cx_um = cx * self.um_per_pixel
                    cy_um = cy * self.um_per_pixel
                    
                    # 尝试椭圆拟合
                    major_axis = 0
                    minor_axis = 0
                    angle = 0
                    
                    if len(largest_contour) >= 5:  # 需要至少5个点才能拟合椭圆
                        try:
                            ellipse = cv2.fitEllipse(largest_contour)
                            center, axes, angle = ellipse
                            
                            # 转换为实际单位 (μm)
                            major_axis = max(axes) * self.um_per_pixel / 2
                            minor_axis = min(axes) * self.um_per_pixel / 2
                            
                            # 确保角度在0-180度范围内
                            angle = angle % 180
                        except:
                            pass
                    
                    # 检查是否接触边界
                    touches_boundary = self._check_touches_boundary(obj_mask)
                    
                    # 存储数据
                    frame_data = {
                        'frame': frame_idx,
                        'area': area_um2,
                        'center_x': cx_um,
                        'center_y': cy_um,
                        'center_x_px': cx,
                        'center_y_px': cy,
                        'major_axis': major_axis,
                        'minor_axis': minor_axis,
                        'angle': angle,
                        'touches_boundary': touches_boundary,
                        'contour': largest_contour
                    }
                    
                    object_data[obj_id].append(frame_data)
                
                # 每处理10个掩膜更新一次日志
                if frame_idx % 10 == 0 or frame_idx == total_frames - 1:
                    self.progress_update.emit(f"计算对象属性: {frame_idx+1}/{total_frames}")
            
            # 4. 应用筛选条件
            self.progress_update.emit("正在应用筛选条件...")
            excluded_ids = set()
            
            # 4.0 排除指定对象ID
            if 'exclude_ids' in self.filter_params and self.filter_params['exclude_ids']:
                excluded_ids.update(self.filter_params['exclude_ids'])
                self.progress_update.emit(f"已排除指定对象: {self.filter_params['exclude_ids']}")
            
            # 保存通过筛选的对象
            valid_objects = {}
            
            # 对每个对象应用筛选条件
            for obj_id in object_ids:
                # 如果对象在排除列表中，则跳过
                if obj_id in excluded_ids:
                    self.object_filter_results[obj_id] = {
                        "result": "filtered", 
                        "reason": "用户手动排除"
                    }
                    continue
                
                # 检查对象是否有足够的帧数据
                obj_frames = object_data[obj_id]
                if len(obj_frames) < 2:
                    self.object_filter_results[obj_id] = {
                        "result": "filtered", 
                        "reason": "有效帧数少于2帧"
                    }
                    continue
                
                # 首先获取对象全部有效帧范围
                valid_start = 0
                valid_end = len(obj_frames) - 1
                obj_valid = True
                
                # 根据筛选条件调整有效帧范围
                
                # 4.1 面积区间筛选
                if self.filter_params.get('area_filter', False):
                    min_area = self.filter_params.get('area_min', 0)
                    max_area = self.filter_params.get('area_max', float('inf'))
                    
                    for i, frame_data in enumerate(obj_frames):
                        area = frame_data['area']
                        if area < min_area or area > max_area:
                            obj_valid = False
                            self.object_filter_results[obj_id] = {
                                "result": "filtered", 
                                "reason": f"面积不在指定范围内 ({min_area}~{max_area} μm²)"
                            }
                            break
                
                if not obj_valid:
                    continue
                
                # 4.2 面积变化率筛选
                if self.filter_params.get('area_change_filter', False):
                    area_change_threshold = self.filter_params.get('area_change_threshold', 0.5)
                    truncated = False
                    
                    for i in range(len(obj_frames) - 1):
                        area1 = obj_frames[i]['area']
                        area2 = obj_frames[i + 1]['area']
                        
                        if area1 == 0 or area2 == 0:
                            continue
                        
                        # 计算面积变化率 (小/大)
                        area_ratio = min(area1, area2) / max(area1, area2)
                        
                        if area_ratio < area_change_threshold:
                            valid_end = i
                            truncated = True
                            # 记录截断原因和位置
                            frame_time = obj_frames[i]['frame'] / self.fps
                            self.object_filter_results[obj_id] = {
                                "result": "truncated", 
                                "reason": f"在第{i+1}帧(时刻{frame_time:.2f}s)处面积变化率({area_ratio:.3f})低于阈值({area_change_threshold})",
                                "truncated_at": i,
                                "original_frames": len(obj_frames)
                            }
                            break
                
                # 4.3 瞬时速度区间筛选
                if self.filter_params.get('velocity_filter', False):
                    min_velocity = self.filter_params.get('velocity_min', 0)
                    max_velocity = self.filter_params.get('velocity_max', float('inf'))
                    truncated = False
                    
                    for i in range(len(obj_frames) - 1):
                        # 检查是否已经在之前的筛选中截断了
                        if i > valid_end:
                            break
                        
                        # 计算相邻帧的时间差 (秒)
                        time_diff = 1.0 / self.fps
                        
                        # 计算位移 (μm)
                        x1, y1 = obj_frames[i]['center_x'], obj_frames[i]['center_y']
                        x2, y2 = obj_frames[i + 1]['center_x'], obj_frames[i + 1]['center_y']
                        displacement = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                        
                        # 计算速度 (μm/s)
                        velocity = displacement / time_diff
                        
                        if velocity < min_velocity or velocity > max_velocity:
                            valid_end = i
                            truncated = True
                            # 记录截断原因和位置
                            frame_time = obj_frames[i]['frame'] / self.fps
                            self.object_filter_results[obj_id] = {
                                "result": "truncated", 
                                "reason": f"在第{i+1}帧(时刻{frame_time:.2f}s)处瞬时速度({velocity:.2f} μm/s)超出范围({min_velocity}~{max_velocity} μm/s)",
                                "truncated_at": i,
                                "original_frames": len(obj_frames)
                            }
                            break
                
                # 4.4 总位移区间筛选
                if self.filter_params.get('displacement_filter', False):
                    min_displacement = self.filter_params.get('displacement_min', 0)
                    max_displacement = self.filter_params.get('displacement_max', float('inf'))
                    
                    # 计算对象的总位移
                    first_frame = obj_frames[valid_start]
                    last_frame = obj_frames[valid_end]
                    
                    x1, y1 = first_frame['center_x'], first_frame['center_y']
                    x2, y2 = last_frame['center_x'], last_frame['center_y']
                    total_displacement = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    
                    if total_displacement < min_displacement or total_displacement > max_displacement:
                        obj_valid = False
                        self.object_filter_results[obj_id] = {
                            "result": "filtered", 
                            "reason": f"总位移({total_displacement:.2f} μm)超出范围({min_displacement}~{max_displacement} μm)"
                        }
                
                if not obj_valid:
                    continue
                
                # 4.5 边界截断筛选
                if self.filter_params.get('boundary_filter', False):
                    truncated = False
                    
                    for i, frame_data in enumerate(obj_frames):
                        # 检查是否已经在之前的筛选中截断了
                        if i > valid_end:
                            break
                        
                        if frame_data['touches_boundary']:
                            valid_end = i - 1  # 不包含接触边界的那一帧
                            truncated = True
                            # 记录截断原因和位置
                            frame_time = frame_data['frame'] / self.fps
                            self.object_filter_results[obj_id] = {
                                "result": "truncated", 
                                "reason": f"在第{i+1}帧(时刻{frame_time:.2f}s)处接触图像边界",
                                "truncated_at": i-1,
                                "original_frames": len(obj_frames)
                            }
                            break
                
                # 4.6 相互最短距离筛选
                if self.filter_params.get('min_distance_filter', False):
                    min_distance_threshold = self.filter_params.get('min_distance_threshold', 10)
                    truncated = False
                    
                    # 对每一帧检查
                    for frame_idx in range(valid_start, valid_end + 1):
                        # 获取当前帧的所有对象
                        current_frame_objects = {}
                        for other_id in object_ids:
                            if other_id == obj_id:
                                continue
                                
                            # 找到该对象在当前帧的数据
                            other_frame_data = None
                            for data in object_data.get(other_id, []):
                                if data['frame'] == obj_frames[frame_idx]['frame']:
                                    other_frame_data = data
                                    break
                            
                            if other_frame_data:
                                current_frame_objects[other_id] = other_frame_data
                        
                        # 计算与其他对象的距离
                        obj_contour = obj_frames[frame_idx]['contour']
                        obj_mask_position = None
                        
                        too_close = False
                        close_obj_id = None
                        min_distance_found = float('inf')
                        
                        for other_id, other_data in current_frame_objects.items():
                            other_contour = other_data['contour']
                            
                            # 计算两个轮廓之间的最短距离
                            min_dist = self._calculate_contour_distance(obj_contour, other_contour)
                            
                            # 转换为实际距离 (μm)
                            min_dist_um = min_dist * self.um_per_pixel
                            
                            if min_dist_um < min_distance_threshold and min_dist_um < min_distance_found:
                                too_close = True
                                close_obj_id = other_id
                                min_distance_found = min_dist_um
                        
                        if too_close:
                            valid_end = frame_idx - 1
                            truncated = True
                            # 记录截断原因和位置
                            frame_time = obj_frames[frame_idx]['frame'] / self.fps
                            self.object_filter_results[obj_id] = {
                                "result": "truncated", 
                                "reason": f"在第{frame_idx+1}帧(时刻{frame_time:.2f}s)处与对象{close_obj_id}的距离({min_distance_found:.2f} μm)小于阈值({min_distance_threshold} μm)",
                                "truncated_at": frame_idx-1,
                                "original_frames": len(obj_frames)
                            }
                            break
                
                # 检查有效帧范围
                if valid_end < valid_start or valid_end - valid_start < 1:
                    # 如果有效帧数不足2帧，则排除该对象
                    self.object_filter_results[obj_id] = {
                        "result": "filtered", 
                        "reason": "截断后有效帧数少于2帧"
                    }
                    continue
                
                # 保存有效帧范围
                valid_objects[obj_id] = (valid_start, valid_end)
                
                # 如果对象通过所有筛选条件
                if obj_id not in self.object_filter_results:
                    self.object_filter_results[obj_id] = {
                        "result": "passed", 
                        "reason": "通过所有筛选条件",
                        "frames": valid_end - valid_start + 1,
                        "original_frames": len(obj_frames)
                    }
            
            # 5. 生成筛选后的掩膜和数据
            self.progress_update.emit("正在生成筛选后的结果...")
            
            # 初始化输出数据
            filtered_masks = []
            object_trajectories = {}
            filtered_metadata = {}
            
            # 为轨迹可视化分配颜色
            colors = []
            for i in range(30):  # 预设30种颜色
                h = i * 12 % 180  # 色调均匀分布在0-180之间
                s = 200  # 饱和度固定
                v = 255  # 明度固定
                
                # 转换为RGB
                c = QColor()
                c.setHsv(h, s, v)
                r, g, b = c.red(), c.green(), c.blue()
                colors.append((r, g, b))
            
            # 随机打乱颜色
            np.random.shuffle(colors)
            
            # 为每个有效对象分配颜色
            object_colors = {}
            for i, obj_id in enumerate(valid_objects.keys()):
                object_colors[obj_id] = colors[i % len(colors)]
            
            # 对每一帧生成筛选后的掩膜
            for frame_idx in range(total_frames):
                # 更新进度
                percent = 60 + int((frame_idx / total_frames) * 40)  # 占总进度的60%到100%
                self.progress_percent.emit(percent)
                
                # 创建空白掩膜
                original_mask = masks_data[frame_idx]
                h, w = original_mask.shape
                
                # 创建彩色输出图像
                colored_mask = np.zeros((h, w, 3), dtype=np.uint8)
                
                # 存储该帧各对象的轨迹点
                frame_trajectory_points = {}
                
                # 处理每个有效对象
                for obj_id, (valid_start, valid_end) in valid_objects.items():
                    # 在对象数据中找到当前帧
                    obj_frame_data = None
                    obj_frame_idx = -1
                    
                    for idx, data in enumerate(object_data[obj_id]):
                        if data['frame'] == frame_idx:
                            obj_frame_data = data
                            obj_frame_idx = idx
                            break
                    
                    if obj_frame_data is None:
                        continue
                    
                    # 检查是否在有效帧范围内
                    if obj_frame_idx < valid_start or obj_frame_idx > valid_end:
                        continue
                    
                    # 提取对象掩膜
                    obj_mask = (original_mask == obj_id).astype(np.uint8) * 255
                    
                    # 为对象着色
                    color = object_colors.get(obj_id, (255, 255, 255))
                    colored_mask[obj_mask > 0] = color
                    
                    # 获取对象轨迹点以绘制轨迹
                    trajectory_points = []
                    for i in range(valid_start, min(obj_frame_idx + 1, valid_end + 1)):
                        point = (object_data[obj_id][i]['center_x_px'], object_data[obj_id][i]['center_y_px'])
                        trajectory_points.append(point)
                    
                    frame_trajectory_points[obj_id] = {
                        'points': trajectory_points,
                        'color': color,
                        'center': (obj_frame_data['center_x_px'], obj_frame_data['center_y_px']),
                        'major_axis': obj_frame_data['major_axis'],
                        'minor_axis': obj_frame_data['minor_axis'],
                        'angle': obj_frame_data['angle']
                    }
                    
                    # 记录对象轨迹数据
                    if obj_id not in object_trajectories:
                        object_trajectories[obj_id] = []
                    
                    # 记录当前帧对象的属性
                    time_seconds = frame_idx / self.fps
                    
                    # 若在有效帧范围内，添加到轨迹数据中
                    if valid_start <= obj_frame_idx <= valid_end:
                        # 添加到轨迹数据
                        object_trajectories[obj_id].append({
                            'time': time_seconds,
                            'area': obj_frame_data['area'],
                            'center_x': obj_frame_data['center_x'],
                            'center_y': obj_frame_data['center_y'],
                            'major_axis': obj_frame_data['major_axis'],
                            'minor_axis': obj_frame_data['minor_axis'],
                            'angle': obj_frame_data['angle']
                        })
                
                # 绘制轨迹和特征
                vis_mask = colored_mask.copy()
                
                # 先保存所有对象的ID标签参数，以便最后绘制在最上层
                id_labels = []
                
                # 绘制轨迹和中心点
                for obj_id, trajectory_data in frame_trajectory_points.items():
                    points = trajectory_data['points']
                    color = trajectory_data['color']
                    center = trajectory_data['center']
                    major_axis = trajectory_data['major_axis']
                    minor_axis = trajectory_data['minor_axis']
                    angle = trajectory_data['angle']
                    
                    # 绘制轨迹
                    if len(points) > 1:
                        for i in range(1, len(points)):
                            pt1 = tuple(map(int, points[i-1]))
                            pt2 = tuple(map(int, points[i]))
                            cv2.line(vis_mask, pt1, pt2, color, 2)
                    
                    # 收集对象ID标签信息，但暂不绘制
                    center_pt = tuple(map(int, center))
                    # 创建ID标签文本
                    id_text = str(obj_id)
                    # 计算文本大小以进行居中放置
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 1.0  # 调整为较小的字体大小
                    thickness = 2     # 调整为较细的线条粗细
                    (text_width, text_height), baseline = cv2.getTextSize(id_text, font, font_scale, thickness)
                    # 计算文本位置使其居中
                    text_x = int(center_pt[0] - text_width/2)
                    text_y = int(center_pt[1] + text_height/2)
                    # 保存标签信息，稍后绘制
                    id_labels.append((id_text, (text_x, text_y), font, font_scale, thickness))
                    
                    # 绘制主轴（红色）和次轴（蓝色）
                    if major_axis > 0 and minor_axis > 0:
                        # 转换为像素单位
                        major_axis_px = major_axis / self.um_per_pixel
                        minor_axis_px = minor_axis / self.um_per_pixel
                        
                        # 获取椭圆原始参数
                        ellipse_data = None
                        for data in object_data[obj_id]:
                            if data['frame'] == frame_idx:
                                # 重新获取轮廓并拟合椭圆以确保正确性
                                contour = data['contour']
                                if len(contour) >= 5:  # 需要至少5个点才能拟合椭圆
                                    try:
                                        ellipse = cv2.fitEllipse(contour)
                                        center_point, axes_len, ellipse_angle = ellipse
                                        
                                        # 判断哪个是主轴（较长的轴）
                                        is_width_major = axes_len[0] > axes_len[1]
                                        
                                        # 如果宽是主轴，则角度不变；如果高是主轴，则角度加90度
                                        if is_width_major:
                                            major_angle = ellipse_angle
                                        else:
                                            major_angle = (ellipse_angle + 90) % 180
                                            
                                        # 次轴垂直于主轴
                                        minor_angle = (major_angle + 90) % 180
                                        
                                        # 转换角度为弧度
                                        major_angle_rad = np.deg2rad(major_angle)
                                        minor_angle_rad = np.deg2rad(minor_angle)
                                        
                                        # 计算主轴端点
                                        dx_major = major_axis_px * np.cos(major_angle_rad)
                                        dy_major = major_axis_px * np.sin(major_angle_rad)
                                        
                                        # 计算次轴端点
                                        dx_minor = minor_axis_px * np.cos(minor_angle_rad)
                                        dy_minor = minor_axis_px * np.sin(minor_angle_rad)
                                        
                                        # 绘制主轴（红色）
                                        pt1_major = (int(center[0] - dx_major), int(center[1] - dy_major))
                                        pt2_major = (int(center[0] + dx_major), int(center[1] + dy_major))
                                        cv2.line(vis_mask, pt1_major, pt2_major, (0, 0, 255), 2)
                                        
                                        # 绘制次轴（蓝色）
                                        pt1_minor = (int(center[0] - dx_minor), int(center[1] - dy_minor))
                                        pt2_minor = (int(center[0] + dx_minor), int(center[1] + dy_minor))
                                        cv2.line(vis_mask, pt1_minor, pt2_minor, (255, 0, 0), 2)
                                        
                                        break
                                    except:
                                        # 如果重新拟合失败，使用简化的方法
                                        angle_rad = np.deg2rad(angle)
                                        
                                        # 计算主轴端点
                                        dx_major = major_axis_px * np.cos(angle_rad)
                                        dy_major = major_axis_px * np.sin(angle_rad)
                                        
                                        # 计算次轴端点（垂直于主轴）
                                        dx_minor = minor_axis_px * np.cos(angle_rad + np.pi/2)
                                        dy_minor = minor_axis_px * np.sin(angle_rad + np.pi/2)
                                        
                                        # 绘制主轴（红色）
                                        pt1_major = (int(center[0] - dx_major), int(center[1] - dy_major))
                                        pt2_major = (int(center[0] + dx_major), int(center[1] + dy_major))
                                        cv2.line(vis_mask, pt1_major, pt2_major, (0, 0, 255), 2)
                                        
                                        # 绘制次轴（蓝色）
                                        pt1_minor = (int(center[0] - dx_minor), int(center[1] - dy_minor))
                                        pt2_minor = (int(center[0] + dx_minor), int(center[1] + dy_minor))
                                        cv2.line(vis_mask, pt1_minor, pt2_minor, (255, 0, 0), 2)
                                break
                
                # 最后，在所有绘制完成后，绘制ID标签，确保它们位于最上层
                for id_text, pos, font, font_scale, thickness in id_labels:
                    # 绘制黑色文本
                    cv2.putText(vis_mask, id_text, pos, font, font_scale, (255, 255, 255), thickness)
                
                # 添加到筛选后的掩膜列表
                filtered_masks.append(vis_mask)
                
                # 每处理10个掩膜更新一次日志
                if frame_idx % 10 == 0 or frame_idx == total_frames - 1:
                    self.progress_update.emit(f"生成筛选结果: {frame_idx+1}/{total_frames}")
            
            # 保存最终结果
            self.filtered_masks = filtered_masks
            self.object_trajectories = object_trajectories
            self.filtered_metadata = filtered_metadata

            # 统计完全通过筛选和部分截断的对象
            passed_count = 0
            truncated_count = 0
            for obj_id, result in self.object_filter_results.items():
                if result['result'] == 'passed':
                    passed_count += 1
                elif result['result'] == 'truncated':
                    truncated_count += 1
            
            # 通过筛选数量包括完全通过和部分截断的对象
            self.passed_objects = passed_count + truncated_count
            
            # 发送统计信息
            self.stats_update.emit(self.total_objects, self.passed_objects)
            
            # 完成筛选
            self.progress_percent.emit(100)
            self.progress_update.emit(f"筛选完成! 原始对象数: {self.total_objects}, 通过筛选: {self.passed_objects} (完全通过: {passed_count}, 部分截断: {truncated_count})")
            
            # 预览第一帧
            if self.filtered_masks:
                self.frame_processed.emit(self.filtered_masks[0], 0, len(self.filtered_masks))
            
            self.filter_finished.emit(True, "筛选完成")
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            
            self.progress_update.emit(f"错误: {error_msg}")
            self.progress_update.emit(f"堆栈跟踪:\n{stack_trace}")
            self.filter_finished.emit(False, error_msg)
    
    def _check_touches_boundary(self, mask):
        """检查掩膜是否接触图像边界"""
        h, w = mask.shape
        
        # 检查四个边界
        top_boundary = mask[0, :]
        bottom_boundary = mask[h-1, :]
        left_boundary = mask[:, 0]
        right_boundary = mask[:, w-1]
        
        return (np.any(top_boundary > 0) or 
                np.any(bottom_boundary > 0) or 
                np.any(left_boundary > 0) or 
                np.any(right_boundary > 0))
    
    def _calculate_contour_distance(self, contour1, contour2):
        """计算两个轮廓间的最短距离"""
        min_distance = float('inf')
        
        # 简化计算，每隔几个点采样
        step = max(1, len(contour1) // 20)
        
        for i in range(0, len(contour1), step):
            pt1 = contour1[i][0]
            
            for j in range(0, len(contour2), step):
                pt2 = contour2[j][0]
                
                # 计算两点间距离
                dist = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
                
                if dist < min_distance:
                    min_distance = dist
        
        return min_distance

class FilterVideoThread(QThread):
    """筛选结果视频播放线程"""
    frame_ready = pyqtSignal(np.ndarray)
    frame_index_changed = pyqtSignal(int)
    
    def __init__(self, filtered_masks):
        super().__init__()
        self.filtered_masks = filtered_masks
        self.running = True
        self.paused = True
        self.frame_index = 0
        self.total_frames = len(filtered_masks) if filtered_masks else 0
        self.fps = 10  # 默认播放帧率
        self.frame_time_ms = int(1000 / self.fps)
        self.mutex = QMutex()
        self.frame_changed = False
        self.last_frame_time = 0
    
    def run(self):
        if not self.filtered_masks:
            return
            
        # 设置初始帧
        self.frame_ready.emit(self.filtered_masks[0])
        self.frame_index_changed.emit(0)
        
        self.last_frame_time = QDateTime.currentMSecsSinceEpoch()
        
        while self.running:
            current_time = QDateTime.currentMSecsSinceEpoch()
            
            self.mutex.lock()
            paused = self.paused
            current_index = self.frame_index
            frame_changed = self.frame_changed
            self.frame_changed = False
            self.mutex.unlock()
            
            if not paused or frame_changed:
                # 发送当前帧
                self.frame_ready.emit(self.filtered_masks[current_index])
                self.frame_index_changed.emit(current_index)
                
                # 更新时间戳
                self.last_frame_time = current_time
                
                # 如果不是暂停状态且没有特定帧的请求，则自动前进到下一帧
                if not paused and not frame_changed:
                    self.mutex.lock()
                    next_index = (current_index + 1) % self.total_frames
                    self.frame_index = next_index
                    self.mutex.unlock()
            
            # 计算下一帧应该等待的时间
            if not paused:
                # 基于上一帧的时间和帧率计算下一帧应显示的时间
                next_frame_time = self.last_frame_time + self.frame_time_ms
                current_time = QDateTime.currentMSecsSinceEpoch()
                
                # 计算需要等待的时间
                wait_time = next_frame_time - current_time
                
                # 如果需要等待，则等待合适的时间；否则立即处理下一帧
                if wait_time > 1:
                    self.msleep(int(wait_time))
                else:
                    # 如果处理时间已经超过了帧间隔，至少休眠1毫秒避免CPU占用过高
                    self.msleep(1)
            else:
                # 如果暂停，则较长时间休眠以减少CPU使用
                self.msleep(100)
    
    def stop(self):
        self.running = False
        self.wait()
    
    def set_frame_index(self, index):
        """设置要显示的帧索引"""
        self.mutex.lock()
        self.frame_index = max(0, min(index, self.total_frames - 1))
        self.frame_changed = True
        self.mutex.unlock()
    
    def toggle_pause(self):
        """切换暂停/播放状态"""
        self.mutex.lock()
        self.paused = not self.paused
        # 重置时间戳，保证从暂停恢复播放时帧率正确
        if not self.paused:
            self.last_frame_time = QDateTime.currentMSecsSinceEpoch()
        self.mutex.unlock()
    
    def set_fps(self, fps):
        """设置播放帧率"""
        self.mutex.lock()
        self.fps = max(1, fps)
        self.frame_time_ms = int(1000 / self.fps)
        self.mutex.unlock()

class MicroTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Micro Tracker | 显微视频目标分割和追踪工具")
        self.setMinimumSize(1200, 900)  # 调整最小窗口大小，更合理的尺寸
        self.setStyleSheet(STYLE)  # 应用全局样式
        
        # 添加应用图标
        app_icon = QIcon("icons/icon.png") if os.path.exists("icons/icon.png") else QIcon.fromTheme("video-x-generic")
        self.setWindowIcon(app_icon)
        
        self.video_path = ""
        self.model_path = "models/sam2/checkpoints/sam2.1_hiera_tiny.pt"  # 设置默认模型路径
        self.output_path = ""
        self.mask_dir = ""
        self.save_mask_enabled = True  # 默认启用掩码保存
        
        self.video_thread = None
        self.processing_thread = None
        self.result_video_thread = None  # 添加结果视频线程变量
        
        # 记录当前聚焦的视频标签，用于键盘控制
        self.focused_video = None
        
        self.init_ui()
    
    def init_ui(self):
        # 全局控件样式优化
        QApplication.setStyle('Fusion')  # 使用统一的Fusion风格
        
        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)  # 稍微增加组件之间的间距
        
        # 为表单标签设置全局样式
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + """
            QFormLayout QLabel {
                margin-top: 1px;
                margin-bottom: 1px;
                min-height: 24px;
                line-height: 24px;
                padding-top: 0px;
                qproperty-alignment: 'AlignVCenter | AlignRight';
            }
        """)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        # 连接标签页切换信号，用于聚焦相应视频控件
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        # ===== 标签页1: 参数设置与标注 =====
        setup_tab = QWidget()
        self.tab_widget.addTab(setup_tab, "参数设置与标注")
        
        setup_layout = QHBoxLayout(setup_tab)
        setup_layout.setContentsMargins(5, 10, 5, 5)
        setup_layout.setSpacing(12)  # 增加左右面板之间的间距
        
        # 左侧控制面板
        left_panel = QWidget()
        left_panel.setMinimumWidth(400)  # 设置最小宽度
        left_panel.setMaximumWidth(500)  # 设置最大宽度
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)  # 增加组件间的垂直间距
        
        # 文件选择区域
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
        self.video_path_edit = QLineEdit()
        self.video_path_edit.setReadOnly(True)
        self.video_path_edit.setPlaceholderText("选择输入视频文件...")
        self.video_path_edit.setMinimumHeight(24)  # 设置输入框高度
        video_browse_btn = QPushButton("浏览")
        video_browse_btn.setIcon(QIcon.fromTheme("document-open"))
        video_browse_btn.setMinimumWidth(60)
        video_browse_btn.setMaximumWidth(60)
        video_browse_btn.setMinimumHeight(24)  # 设置按钮高度与输入框一致
        video_browse_btn.clicked.connect(self.browse_video)
        video_layout.addWidget(self.video_path_edit)
        video_layout.addWidget(video_browse_btn)
        file_layout.addRow("<b>输入视频:</b>", video_layout)
        
        # 模型文件选择
        model_layout = QHBoxLayout()
        model_layout.setSpacing(8)
        self.model_path_edit = QLineEdit(self.model_path)
        self.model_path_edit.setReadOnly(True)
        self.model_path_edit.setMinimumHeight(24)  # 设置输入框高度
        model_browse_btn = QPushButton("浏览")
        model_browse_btn.setIcon(QIcon.fromTheme("document-open"))
        model_browse_btn.setMinimumWidth(60)
        model_browse_btn.setMaximumWidth(60)
        model_browse_btn.setMinimumHeight(24)  # 设置按钮高度与输入框一致
        model_browse_btn.clicked.connect(self.browse_model)
        model_layout.addWidget(self.model_path_edit)
        model_layout.addWidget(model_browse_btn)
        file_layout.addRow("<b>SAM2 模型:</b>", model_layout)
        
        # 输出视频路径
        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setReadOnly(True)
        self.output_path_edit.setPlaceholderText("(默认由系统自动设置)")
        self.output_path_edit.setMinimumHeight(24)  # 设置输入框高度
        output_browse_btn = QPushButton("浏览")
        output_browse_btn.setIcon(QIcon.fromTheme("document-save"))
        output_browse_btn.setMinimumWidth(60)
        output_browse_btn.setMaximumWidth(60)
        output_browse_btn.setMinimumHeight(24)  # 设置按钮高度与输入框一致
        output_browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(output_browse_btn)
        file_layout.addRow("<b>输出视频:</b>", output_layout)
        
        # 掩码保存目录
        mask_layout = QHBoxLayout()
        mask_layout.setSpacing(8)
        self.mask_dir_edit = QLineEdit()
        self.mask_dir_edit.setReadOnly(True)
        self.mask_dir_edit.setPlaceholderText("(默认由系统自动设置)")
        self.mask_dir_edit.setMinimumHeight(24)  # 设置输入框高度
        mask_browse_btn = QPushButton("浏览")
        mask_browse_btn.setIcon(QIcon.fromTheme("folder"))
        mask_browse_btn.setMinimumWidth(60)
        mask_browse_btn.setMaximumWidth(60)
        mask_browse_btn.setMinimumHeight(24)  # 设置按钮高度与输入框一致
        mask_browse_btn.clicked.connect(self.browse_mask_dir)
        mask_layout.addWidget(self.mask_dir_edit)
        mask_layout.addWidget(mask_browse_btn)
        file_layout.addRow("<b>掩码目录:</b>", mask_layout)
        
        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)
        
        # 参数设置区域
        param_group = QGroupBox("参数设置")
        param_layout = QFormLayout()
        param_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        param_layout.setContentsMargins(10, 15, 10, 15)  # 增加底部边距
        param_layout.setSpacing(15)  # 增加设置项间距
        param_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        param_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 设备选择
        self.device_combo = QComboBox()
        self.device_combo.setMinimumHeight(24)  # 设置下拉框高度
        self.device_combo.addItem("CUDA:0 (默认)", "cuda:0")
        self.device_combo.addItem("CPU", "cpu")
        # 如果有多个 GPU，添加它们
        if torch.cuda.is_available():
            for i in range(1, torch.cuda.device_count()):
                self.device_combo.addItem(f"CUDA:{i}", f"cuda:{i}")
        # 确保下拉箭头显示
        self.device_combo.setStyleSheet("""
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
        """)
        param_layout.addRow("<b>处理设备:</b>", self.device_combo)
        
        # 保存视频选项
        save_options_layout = QHBoxLayout()
        save_options_layout.setSpacing(20)
        
        video_save_layout = QHBoxLayout()
        video_save_layout.setSpacing(5)
        self.save_video_check = QCheckBox()
        self.save_video_check.setChecked(True)
        self.save_video_check.setMinimumHeight(24)  # 设置复选框高度
        video_save_label = QLabel("保存处理视频")
        video_save_label.setStyleSheet("font-weight: normal;")
        video_save_layout.addWidget(self.save_video_check)
        video_save_layout.addWidget(video_save_label)
        video_save_layout.addStretch(1)
        
        mask_save_layout = QHBoxLayout()
        mask_save_layout.setSpacing(5)
        self.save_mask_check = QCheckBox()
        self.save_mask_check.setChecked(True)  # 默认选中
        self.save_mask_check.setMinimumHeight(24)  # 设置复选框高度
        mask_save_label = QLabel("保存分割掩码")
        mask_save_label.setStyleSheet("font-weight: normal;")
        mask_save_layout.addWidget(self.save_mask_check)
        mask_save_layout.addWidget(mask_save_label)
        mask_save_layout.addStretch(1)
        
        save_options_layout.addLayout(video_save_layout)
        save_options_layout.addLayout(mask_save_layout)
        
        param_layout.addRow("输出选项:", save_options_layout)
        
        param_group.setLayout(param_layout)
        param_group.setMinimumHeight(120)  # 降低最小高度，原为180
        left_layout.addWidget(param_group)
        
        # 创建一个垂直布局的伸缩器，使后面的处理进度区域占据所有剩余空间
        left_bottom_container = QWidget()
        left_bottom_layout = QVBoxLayout(left_bottom_container)
        left_bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # 处理进度区域 - 移至左下方并占据所有可用空间
        progress_group = QGroupBox("处理进度")
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(10, 15, 10, 15)
        progress_layout.setSpacing(10)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        # 确保日志文本区域总是显示滚动条
        self.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.log_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 设置更新的样式，确保滚动条可见
        self.log_text.setStyleSheet("""
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
        # 移除最小/最大高度限制，让其自动填充可用空间
        progress_layout.addWidget(self.log_text)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% (%v/%m)")
        self.progress_bar.setStyleSheet("""
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
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # 添加一个函数来确保滚动条正确显示
        def ensure_scrollbars_visible():
            # 添加一些测试文本确保滚动条初始化正确
            for i in range(20):
                self.log_text.append(f"初始化日志行 {i+1}")
            
            # 强制更新UI并滚动到顶部
            QApplication.processEvents()
            self.log_text.clear()
            QApplication.processEvents()
        
        # 在UI初始化完成后调用此函数
        QTimer.singleShot(100, ensure_scrollbars_visible)
        
        progress_group.setLayout(progress_layout)
        # 设置处理进度区域为垂直方向可扩展
        progress_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_bottom_layout.addWidget(progress_group, 1)  # 添加权重1，让其占据所有空间
        
        # 开始处理按钮
        self.start_btn = QPushButton("开 始 处 理")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_processing)
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
        
        # 将左下角容器添加到左侧面板，并设置为占据所有剩余空间
        left_layout.addWidget(left_bottom_container, 1)  # 设置伸缩因子为1，占据所有剩余空间
        
        # 右侧预览面板
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
        self.video_label = VideoLabel()
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        self.video_label.setStyleSheet("""
            border: 1px solid #e0e0e0; 
            background-color: #f8f8f8;
            border-radius: 4px;
        """)
        preview_layout.addWidget(self.video_label)
        
        # 连接边界框相关信号
        self.video_label.bbox_added.connect(self.on_bbox_added)
        self.video_label.bbox_selected.connect(self.on_bbox_selected)
        self.video_label.bbox_deleted.connect(self.on_bbox_deleted)
        
        # 视频预览控制
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 12, 0, 0)  # 增加顶部间距
        control_layout.setSpacing(15)
        
        # 添加播放/暂停按钮
        self.play_pause_btn = QPushButton("播放")
        self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_pause_btn.setMinimumWidth(90)
        self.play_pause_btn.setMaximumWidth(110)
        self.play_pause_btn.setEnabled(False)
        self.play_pause_btn.setStyleSheet("font-weight: bold;")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setEnabled(False)
        self.frame_slider.setMinimumHeight(28)  # 增加滑块高度
        self.frame_slider.valueChanged.connect(self.set_frame_index)
        
        self.frame_info_label = QLabel("当前帧: 0 / 0")
        self.frame_info_label.setMinimumWidth(100)
        self.frame_info_label.setStyleSheet("font-weight: bold; color: #455a64;")
        
        clear_bbox_btn = QPushButton("清除边界框")
        clear_bbox_btn.setIcon(QIcon.fromTheme("edit-delete"))
        clear_bbox_btn.setMinimumWidth(80)
        clear_bbox_btn.setMaximumWidth(100)
        clear_bbox_btn.setStyleSheet("background-color: #f44336;")
        clear_bbox_btn.clicked.connect(self.video_label.clear_bboxes)
        
        control_layout.addWidget(self.play_pause_btn)
        control_layout.addWidget(self.frame_slider)
        control_layout.addWidget(self.frame_info_label)
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
        
        setup_layout.addWidget(left_panel, 2)
        setup_layout.addWidget(right_panel, 3)  # 调整左右面板比例为2:3
        
        # ===== 标签页2: 处理和结果 =====
        process_tab = QWidget()
        self.tab_widget.addTab(process_tab, "结果预览")
        
        process_layout = QVBoxLayout(process_tab)
        process_layout.setContentsMargins(15, 15, 15, 15)  # 增加边距
        process_layout.setSpacing(12)  # 增加间距
        
        # 结果预览区域
        result_group = QGroupBox("处理结果视频预览")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(15, 20, 15, 15)  # 增加内边距
        result_layout.setSpacing(12)  # 增加间距
        
        self.result_label = ResultVideoLabel()
        self.result_label.setMinimumSize(800, 500)  # 增加最小尺寸
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            border: 1px solid #e0e0e0; 
            background-color: #f8f8f8;
            border-radius: 4px;
        """)
        self.result_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        result_layout.addWidget(self.result_label)
        
        # 预览控制器
        result_control_layout = QHBoxLayout()
        result_control_layout.setContentsMargins(0, 12, 0, 0)  # 增加上边距
        result_control_layout.setSpacing(15)  # 增加组件间距
        
        # 添加播放/暂停按钮
        self.result_play_pause_btn = QPushButton("播放")
        self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.result_play_pause_btn.setMinimumWidth(90)
        self.result_play_pause_btn.setMaximumWidth(110)
        self.result_play_pause_btn.setEnabled(False)
        self.result_play_pause_btn.setStyleSheet("font-weight: bold;")
        self.result_play_pause_btn.clicked.connect(self.toggle_result_play_pause)
        
        self.result_slider = QSlider(Qt.Horizontal)
        self.result_slider.setEnabled(False)
        self.result_slider.setMinimumHeight(30)  # 增加滑块高度
        self.result_slider.valueChanged.connect(self.set_result_frame_index)
        
        self.result_info_label = QLabel("处理结果: 0 / 0")
        self.result_info_label.setMinimumWidth(120)  # 增加标签宽度
        self.result_info_label.setStyleSheet("font-weight: bold; color: #455a64;")  # 添加粗体样式
        
        open_output_btn = QPushButton("打开输出文件夹")
        open_output_btn.setIcon(QIcon.fromTheme("folder-open"))  # 添加图标
        open_output_btn.clicked.connect(self.open_output_folder)
        open_output_btn.setMinimumWidth(120)
        open_output_btn.setMaximumWidth(130)
        open_output_btn.setMinimumHeight(36)  # 增加按钮高度
        open_output_btn.setStyleSheet("background-color: #03A9F4;")  # 使用蓝色突出此按钮
        
        result_control_layout.addWidget(self.result_play_pause_btn)
        result_control_layout.addWidget(self.result_slider)
        result_control_layout.addWidget(self.result_info_label)
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
        
        # ===== 标签页3: 筛选过滤 =====
        filter_tab = QWidget()
        self.tab_widget.addTab(filter_tab, "筛选过滤")
        
        filter_layout = QHBoxLayout(filter_tab)
        filter_layout.setContentsMargins(5, 10, 5, 5)
        filter_layout.setSpacing(12)  # 增加左右面板之间的间距
        
        # 左侧控制面板
        filter_left_panel = QWidget()
        filter_left_panel.setMinimumWidth(400)  # 设置最小宽度
        filter_left_panel.setMaximumWidth(500)  # 设置最大宽度
        filter_left_layout = QVBoxLayout(filter_left_panel)
        filter_left_layout.setContentsMargins(0, 0, 0, 0)
        filter_left_layout.setSpacing(10)  # 增加组件间的垂直间距
        
        # 右侧预览面板
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
        self.filter_video_label = ResultVideoLabel()
        self.filter_video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.filter_video_label.setStyleSheet("""
            border: 1px solid #e0e0e0; 
            background-color: #f8f8f8;
            border-radius: 4px;
        """)
        filter_preview_layout.addWidget(self.filter_video_label)
        
        # 筛选结果控制
        filter_control_layout = QHBoxLayout()
        filter_control_layout.setContentsMargins(0, 12, 0, 0)
        filter_control_layout.setSpacing(15)
        
        # 播放/暂停按钮
        self.filter_play_pause_btn = QPushButton("播放")
        self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.filter_play_pause_btn.setMinimumWidth(90)
        self.filter_play_pause_btn.setMaximumWidth(110)
        self.filter_play_pause_btn.setEnabled(False)
        self.filter_play_pause_btn.setStyleSheet("font-weight: bold;")
        self.filter_play_pause_btn.clicked.connect(self.toggle_filter_play_pause)
        
        self.filter_slider = QSlider(Qt.Horizontal)
        self.filter_slider.setEnabled(False)
        self.filter_slider.setMinimumHeight(28)
        self.filter_slider.valueChanged.connect(self.set_filter_frame_index)
        
        self.filter_info_label = QLabel("筛选结果: 0 / 0")
        self.filter_info_label.setMinimumWidth(100)
        self.filter_info_label.setStyleSheet("font-weight: bold; color: #455a64;")
        
        # 保存按钮
        self.save_filter_btn = QPushButton("输出保存")
        self.save_filter_btn.setIcon(QIcon.fromTheme("document-save"))
        self.save_filter_btn.setMinimumWidth(100)
        self.save_filter_btn.setMaximumWidth(110)
        self.save_filter_btn.setEnabled(False)
        self.save_filter_btn.setStyleSheet("background-color: #03A9F4;")
        self.save_filter_btn.clicked.connect(self.save_filter_results)
        
        filter_control_layout.addWidget(self.filter_play_pause_btn)
        filter_control_layout.addWidget(self.filter_slider)
        filter_control_layout.addWidget(self.filter_info_label)
        filter_control_layout.addWidget(self.save_filter_btn)
        
        filter_preview_layout.addLayout(filter_control_layout)
        
        # 统计信息面板
        filter_stats_layout = QHBoxLayout()
        filter_stats_layout.setSpacing(20)
        
        self.filter_stats_label = QLabel("对象数量: 0 | 通过筛选: 0")
        self.filter_stats_label.setStyleSheet("""
            background-color: #e8f5e9; 
            padding: 8px; 
            border-radius: 5px; 
            border: 1px solid #a5d6a7;
            color: #2e7d32;
            font-weight: bold;
        """)
        self.filter_stats_label.setAlignment(Qt.AlignCenter)
        
        filter_stats_layout.addWidget(self.filter_stats_label)
        filter_preview_layout.addLayout(filter_stats_layout)
        
        # 添加键盘控制说明
        filter_keyboard_help = QLabel("键盘控制: 空格键-播放/暂停, F键-下一帧, D键-上一帧")
        filter_keyboard_help.setStyleSheet("color: #666666; font-style: italic;")
        filter_keyboard_help.setAlignment(Qt.AlignCenter)
        filter_preview_layout.addWidget(filter_keyboard_help)
        
        filter_preview_group.setLayout(filter_preview_layout)
        filter_right_layout.addWidget(filter_preview_group)
        
        # 添加左右面板到主布局
        filter_layout.addWidget(filter_left_panel, 2)
        filter_layout.addWidget(filter_right_panel, 3)
        
        # 1. 掩膜图片序列选择
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
        self.filter_mask_dir_edit = QLineEdit()
        self.filter_mask_dir_edit.setReadOnly(True)
        self.filter_mask_dir_edit.setPlaceholderText("选择掩膜图片文件夹...")
        self.filter_mask_dir_edit.setMinimumHeight(24)
        mask_folder_browse_btn = QPushButton("浏览")
        mask_folder_browse_btn.setIcon(QIcon.fromTheme("folder"))
        mask_folder_browse_btn.setMinimumWidth(60)
        mask_folder_browse_btn.setMaximumWidth(60)
        mask_folder_browse_btn.setMinimumHeight(24)
        mask_folder_browse_btn.clicked.connect(self.browse_filter_mask_dir)
        mask_folder_layout.addWidget(self.filter_mask_dir_edit)
        mask_folder_layout.addWidget(mask_folder_browse_btn)
        mask_select_layout.addRow("<b>掩膜文件夹:</b>", mask_folder_layout)
        
        mask_select_group.setLayout(mask_select_layout)
        filter_left_layout.addWidget(mask_select_group)
        
        # 2. 参数设置
        param_setting_group = QGroupBox("参数设置")
        param_setting_layout = QFormLayout()
        param_setting_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        param_setting_layout.setContentsMargins(15, 20, 15, 15)
        param_setting_layout.setSpacing(15)
        param_setting_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        param_setting_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 帧率设置
        self.fps_input = QLineEdit("1.00000")
        self.fps_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,5})?')))
        self.fps_input.setMinimumHeight(24)
        param_setting_layout.addRow("<b>帧率 (FPS):</b>", self.fps_input)
        
        # 像素比例系数
        self.um_per_pixel_input = QLineEdit("1.00000")
        self.um_per_pixel_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,5})?')))
        self.um_per_pixel_input.setMinimumHeight(24)
        param_setting_layout.addRow("<b>比例系数 (</b>" + "<span style='font-family: \"Times New Roman\", Arial, sans-serif;'>μm</span>" + "<b>/pixel):</b>", self.um_per_pixel_input)
        
        param_setting_group.setLayout(param_setting_layout)
        filter_left_layout.addWidget(param_setting_group)
        
        # 3. 筛选条件
        filter_conditions_group = QGroupBox("筛选条件")
        filter_conditions_layout = QVBoxLayout()
        filter_conditions_layout.setContentsMargins(15, 20, 15, 15)
        filter_conditions_layout.setSpacing(15)
        
        # 3.1 面积区间
        area_filter_layout = QHBoxLayout()
        area_filter_layout.setSpacing(10)
        
        area_filter_layout.addWidget(QLabel("<b>面积区间:</b>"))
        
        self.area_filter_check = QCheckBox("启用")
        self.area_filter_check.setMinimumHeight(24)
        
        area_range_layout = QHBoxLayout()
        area_range_layout.setSpacing(5)
        self.area_min_input = QLineEdit("0")
        self.area_min_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.area_min_input.setMinimumHeight(24)
        self.area_min_input.setFixedWidth(80)
        
        area_range_label = QLabel("至")
        
        self.area_max_input = QLineEdit("999999")
        self.area_max_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.area_max_input.setMinimumHeight(24)
        self.area_max_input.setFixedWidth(80)
        
        area_unit_label = self.create_unit_label("μm²")
        
        area_range_layout.addWidget(self.area_min_input)
        area_range_layout.addWidget(area_range_label)
        area_range_layout.addWidget(self.area_max_input)
        area_range_layout.addWidget(area_unit_label)
        
        area_filter_layout.addWidget(self.area_filter_check)
        area_filter_layout.addLayout(area_range_layout)
        area_filter_layout.addStretch(1)
        
        filter_conditions_layout.addLayout(area_filter_layout)
        
        # 3.2 面积变化率阈值
        area_change_filter_layout = QHBoxLayout()
        area_change_filter_layout.setSpacing(10)
        
        area_change_filter_layout.addWidget(QLabel("<b>面积变化率阈值:</b>"))
        
        self.area_change_check = QCheckBox("启用")
        self.area_change_check.setMinimumHeight(24)
        
        area_change_threshold_layout = QHBoxLayout()
        area_change_threshold_layout.setSpacing(5)
        self.area_change_input = QLineEdit("0.5")
        self.area_change_input.setValidator(QRegExpValidator(QRegExp(r'0(\.[0-9]{0,2})?|1(\.0{0,2})?')))
        self.area_change_input.setMinimumHeight(24)
        self.area_change_input.setFixedWidth(80)
        
        area_change_unit_label = self.create_unit_label("比例值(0~1)")
        
        area_change_threshold_layout.addWidget(self.area_change_input)
        area_change_threshold_layout.addWidget(area_change_unit_label)
        
        area_change_filter_layout.addWidget(self.area_change_check)
        area_change_filter_layout.addLayout(area_change_threshold_layout)
        area_change_filter_layout.addStretch(1)
        
        filter_conditions_layout.addLayout(area_change_filter_layout)
        
        # 3.3 瞬时速度区间
        velocity_filter_layout = QHBoxLayout()
        velocity_filter_layout.setSpacing(10)
        
        velocity_filter_layout.addWidget(QLabel("<b>瞬时速度区间:</b>"))
        
        self.velocity_check = QCheckBox("启用")
        self.velocity_check.setMinimumHeight(24)
        
        velocity_range_layout = QHBoxLayout()
        velocity_range_layout.setSpacing(5)
        self.velocity_min_input = QLineEdit("0")
        self.velocity_min_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.velocity_min_input.setMinimumHeight(24)
        self.velocity_min_input.setFixedWidth(80)
        
        velocity_range_label = QLabel("至")
        
        self.velocity_max_input = QLineEdit("999999")
        self.velocity_max_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.velocity_max_input.setMinimumHeight(24)
        self.velocity_max_input.setFixedWidth(80)
        
        velocity_unit_label = self.create_unit_label("μm/s")
        
        velocity_range_layout.addWidget(self.velocity_min_input)
        velocity_range_layout.addWidget(velocity_range_label)
        velocity_range_layout.addWidget(self.velocity_max_input)
        velocity_range_layout.addWidget(velocity_unit_label)
        
        velocity_filter_layout.addWidget(self.velocity_check)
        velocity_filter_layout.addLayout(velocity_range_layout)
        velocity_filter_layout.addStretch(1)
        
        filter_conditions_layout.addLayout(velocity_filter_layout)
        
        # 3.4 总位移区间
        displacement_filter_layout = QHBoxLayout()
        displacement_filter_layout.setSpacing(10)
        
        displacement_filter_layout.addWidget(QLabel("<b>总位移区间:</b>"))
        
        self.displacement_check = QCheckBox("启用")
        self.displacement_check.setMinimumHeight(24)
        
        displacement_range_layout = QHBoxLayout()
        displacement_range_layout.setSpacing(5)
        self.displacement_min_input = QLineEdit("0")
        self.displacement_min_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.displacement_min_input.setMinimumHeight(24)
        self.displacement_min_input.setFixedWidth(80)
        
        displacement_range_label = QLabel("至")
        
        self.displacement_max_input = QLineEdit("999999")
        self.displacement_max_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.displacement_max_input.setMinimumHeight(24)
        self.displacement_max_input.setFixedWidth(80)
        
        displacement_unit_label = self.create_unit_label("μm")
        
        displacement_range_layout.addWidget(self.displacement_min_input)
        displacement_range_layout.addWidget(displacement_range_label)
        displacement_range_layout.addWidget(self.displacement_max_input)
        displacement_range_layout.addWidget(displacement_unit_label)
        
        displacement_filter_layout.addWidget(self.displacement_check)
        displacement_filter_layout.addLayout(displacement_range_layout)
        displacement_filter_layout.addStretch(1)
        
        filter_conditions_layout.addLayout(displacement_filter_layout)
        
        # 3.5 边界截断排除
        boundary_filter_layout = QHBoxLayout()
        boundary_filter_layout.setSpacing(10)
        
        boundary_filter_layout.addWidget(QLabel("<b>边界截断排除:</b>"))
        
        self.boundary_check = QCheckBox("启用边界截断排除")
        self.boundary_check.setMinimumHeight(24)
        
        boundary_filter_layout.addWidget(self.boundary_check)
        boundary_filter_layout.addStretch(1)
        
        filter_conditions_layout.addLayout(boundary_filter_layout)
        
        # 3.6 相互最短距离阈值
        min_distance_filter_layout = QHBoxLayout()
        min_distance_filter_layout.setSpacing(10)
        
        min_distance_filter_layout.addWidget(QLabel("<b>相互最短距离阈值:</b>"))
        
        self.min_distance_check = QCheckBox("启用")
        self.min_distance_check.setMinimumHeight(24)
        
        min_distance_threshold_layout = QHBoxLayout()
        min_distance_threshold_layout.setSpacing(5)
        self.min_distance_input = QLineEdit("10")
        self.min_distance_input.setValidator(QRegExpValidator(QRegExp(r'[0-9]+(\.[0-9]{0,2})?')))
        self.min_distance_input.setMinimumHeight(24)
        self.min_distance_input.setFixedWidth(80)
        
        min_distance_unit_label = self.create_unit_label("μm")
        
        min_distance_threshold_layout.addWidget(self.min_distance_input)
        min_distance_threshold_layout.addWidget(min_distance_unit_label)
        
        min_distance_filter_layout.addWidget(self.min_distance_check)
        min_distance_filter_layout.addLayout(min_distance_threshold_layout)
        min_distance_filter_layout.addStretch(1)
        
        filter_conditions_layout.addLayout(min_distance_filter_layout)
        
        filter_conditions_group.setLayout(filter_conditions_layout)
        filter_left_layout.addWidget(filter_conditions_group)
        
        # 4. 排除指定对象
        exclude_group = QGroupBox("排除指定对象")
        exclude_layout = QHBoxLayout()  # 改为水平布局
        exclude_layout.setContentsMargins(15, 20, 15, 15)
        exclude_layout.setSpacing(10)
        
        # 创建标签并添加到布局
        exclude_label = QLabel("<b>排除对象ID:</b>")
        exclude_label.setMinimumWidth(75)
        exclude_layout.addWidget(exclude_label)
        
        # 创建输入框并添加到布局
        self.exclude_ids_input = QLineEdit()
        self.exclude_ids_input.setPlaceholderText("输入要排除的对象ID，用逗号分隔，如: 1,2,3")
        self.exclude_ids_input.setMinimumHeight(24)
        exclude_layout.addWidget(self.exclude_ids_input)
        
        exclude_group.setLayout(exclude_layout)
        filter_left_layout.addWidget(exclude_group)
        
        # 5. 应用筛选按钮
        self.apply_filter_btn = QPushButton("应 用 筛 选")
        self.apply_filter_btn.setEnabled(False)
        self.apply_filter_btn.clicked.connect(self.apply_mask_filter)
        self.apply_filter_btn.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            padding: 5px;
            background-color: #4CAF50;
            border-radius: 6px;
        """)
        self.apply_filter_btn.setMinimumHeight(40)
        self.apply_filter_btn.setIcon(QIcon.fromTheme("view-filter"))
        filter_left_layout.addWidget(self.apply_filter_btn)
        
        # 添加筛选处理进度区域
        filter_progress_group = QGroupBox("筛选处理进度")
        filter_progress_layout = QVBoxLayout()
        filter_progress_layout.setContentsMargins(10, 15, 10, 15)
        filter_progress_layout.setSpacing(10)
        
        # 筛选处理日志文本区域
        self.filter_log_text = QTextEdit()
        self.filter_log_text.setReadOnly(True)
        self.filter_log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.filter_log_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.filter_log_text.setStyleSheet("""
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
        filter_progress_layout.addWidget(self.filter_log_text, 1)  # 添加伸缩因子1
        
        # 添加一个函数来确保滚动条正确显示
        def ensure_filter_scrollbars_visible():
            # 添加一些测试文本确保滚动条初始化正确
            for i in range(20):
                self.filter_log_text.append(f"初始化日志行 {i+1}")
            
            # 强制更新UI并滚动到顶部
            QApplication.processEvents()
            self.filter_log_text.clear()
            QApplication.processEvents()
        
        # 在UI初始化完成后调用此函数
        QTimer.singleShot(100, ensure_filter_scrollbars_visible)
        
        # 筛选进度条（使用和主界面相同的进度条样式）
        self.filter_progress_bar = QProgressBar()
        self.filter_progress_bar.setRange(0, 100)
        self.filter_progress_bar.setValue(0)
        self.filter_progress_bar.setTextVisible(True)
        self.filter_progress_bar.setFormat("%p% (%v/%m)")
        self.filter_progress_bar.setStyleSheet("""
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
        self.filter_progress_bar.setVisible(False)  # 默认隐藏进度条
        filter_progress_layout.addWidget(self.filter_progress_bar)
        
        filter_progress_group.setLayout(filter_progress_layout)
        # 设置筛选处理进度区域为可扩展的
        filter_progress_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        filter_left_layout.addWidget(filter_progress_group, 1)  # 添加伸缩因子1，让进度区域自动扩展
        
        # ===== 标签页4: 使用指南 =====
        guide_tab = QWidget()
        self.tab_widget.addTab(guide_tab, "使用指南")
        
        guide_layout = QVBoxLayout(guide_tab)
        guide_layout.setContentsMargins(15, 15, 15, 15)
        
        guide_text = QTextEdit()
        guide_text.setReadOnly(True)
        guide_text.setStyleSheet("""
            font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
            font-size: 10pt; 
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 8px;
            color: #424242;
            
            /* 滚动条样式 */
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
            
            /* 水平滚动条样式 */
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 14px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: #505050;  /* 黑灰色 */
                min-width: 30px;
                margin: 2px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #404040;  /* 更深的黑灰色 */
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: #f0f0f0;
            }
        """)
        guide_text.setHtml("""
        <style>
            h2 { color: #1976D2; margin-top: 20px; margin-bottom: 16px; }
            h3 { color: #2979FF; margin-top: 18px; margin-bottom: 12px; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px; }
            h4 { color: #455A64; margin-top: 16px; margin-bottom: 8px; }
            p { text-align: justify; margin: 8px 0; line-height: 1.5; }
            ul, ol { margin-top: 8px; margin-bottom: 8px; }
            li { margin: 4px 0; line-height: 1.5; }
            b { color: #37474F; }
            .highlight { background-color: #FFF9C4; padding: 2px 4px; border-radius: 3px; }
            .note { background-color: #E3F2FD; padding: 12px; border-left: 4px solid #2196F3; margin: 12px 0; border-radius: 4px; }
            .warning { background-color: #FFF3E0; padding: 12px; border-left: 4px solid #FF9800; margin: 12px 0; border-radius: 4px; }
        </style>
        <h2>Micro Tracker 使用指南</h2>
        <div class="note" style="margin-bottom: 15px;">
            <h3 style="margin-top: 15px;">作者信息</h3>
            <p style="margin: 5px 0;">作者：LUCIEN</p>
            <p style="margin: 5px 0;">邮箱：lucien-6@qq.com</p>
            <p style="margin: 5px 0;">版本：1.2.0</p>
            <p style="margin: 5px 0;">发布日期：2025年5月7日</p>
            <p style="margin: 5px 0;">Copyright © 2025 LUCIEN. 保留所有权利。</p>
        </div>
        <p>Micro Tracker 是一个基于 SAM2 (Segment Anything Model 2) 的显微视频对象分割和跟踪工具。本工具采用最新的 SAM2 模型，可以帮助您对显微视频中的多个对象进行高精度自动分割和跟踪，广泛适用于视频分析、对象检测和视觉效果制作等场景。</p>
        
        <h3>基本使用流程：</h3>
        <ol>
            <li><b>选择视频文件：</b> 点击"浏览..."按钮选择要处理的视频文件。支持常见视频格式，如MP4、AVI、MOV和MKV等。</li>
            <li><b>确认模型路径：</b> 确保 SAM2 模型路径正确，默认为 models/sam2/checkpoints/sam2.1_hiera_tiny.pt。如需使用其他模型，可点击"浏览..."按钮选择模型文件。</li>
            <li><b>设置输出选项：</b> 指定输出视频路径和掩码保存目录（可选）。掩码目录用于保存对象分割的二进制掩码，便于后续处理和分析。</li>
            <li><b>标注初始边界框：</b> 在视频第一帧上，通过拖动鼠标绘制要跟踪对象的边界框。可以标注多个对象，系统会为每个对象分配唯一标识符。</li>
            <li><b>开始处理：</b> 点击"开始处理"按钮启动视频处理。处理过程中可以实时查看进度和预计完成时间。</li>
            <li><b>查看处理进度：</b> 在处理进度栏中查看实时处理日志，包括初始化信息、处理速度和预计剩余时间等。不同类型的信息以不同颜色显示，便于快速识别。</li>
            <li><b>查看结果：</b> 处理完成后自动切换到"结果预览"标签页查看处理结果。您可以播放、暂停并浏览处理后的视频，查看分割和跟踪效果。</li>
            <li><b>筛选数据：</b> 处理完成后，可以切换到"筛选过滤"标签页，对掩膜对象进行高级筛选、分析和数据导出。</li>
        </ol>
        
        <h3>界面功能详解：</h3>
        <h4>1. 参数设置与标注</h4>
        <ul>
            <li><b>文件选择区域：</b> 用于选择输入视频、模型文件、设置输出路径和掩码保存目录。</li>
            <li><b>参数设置区域：</b> 选择处理设备（CPU或GPU）和其他处理选项。</li>
            <li><b>视频预览区域：</b> 显示原始视频，并允许通过拖动鼠标绘制边界框标注要跟踪的对象。</li>
            <li><b>视频控制：</b> 
                <ul>
                    <li>播放/暂停按钮：控制视频播放状态</li>
                    <li>帧滑块：快速浏览视频的不同帧</li>
                    <li>清除边界框按钮：移除所有已标注的边界框</li>
                </ul>
            </li>
            <li><b>处理进度区域：</b> 显示处理日志和进度条，提供实时反馈。</li>
        </ul>
        
        <h4>2. 结果预览</h4>
        <ul>
            <li><b>结果视频预览：</b> 显示处理后的视频，包含分割掩码和对象边界框。</li>
            <li><b>视频控制：</b> 与参数设置页类似，但用于控制结果视频的播放和浏览。</li>
            <li><b>打开输出文件夹：</b> 直接访问输出视频所在的文件夹。</li>
        </ul>
        
        <h4>3. 筛选过滤</h4>
        <ul>
            <li><b>掩膜图片序列选择：</b> 选择包含掩膜图像的文件夹（通常是处理步骤自动生成的）。掩膜图像是8位灰度PNG图片，每个像素值表示对象ID，背景为0。</li>
            <li><b>参数设置：</b> 
                <ul>
                    <li>帧率 (FPS)：设置分析时的帧率，影响时间和速度计算</li>
                    <li>比例系数 (μm/pixel)：设置像素到实际物理尺寸的转换系数，影响尺寸和距离计算</li>
                </ul>
            </li>
            <li><b>筛选条件：</b> 可以设置六种不同的筛选条件
                <ul>
                    <li>面积区间：根据对象面积（μm²）筛选</li>
                    <li>面积变化率阈值：当相邻帧之间面积变化超过阈值时截断对象轨迹</li>
                    <li>瞬时速度区间：根据对象的瞬时移动速度（μm/s）筛选</li>
                    <li>总位移区间：根据对象从起点到终点的总位移（μm）筛选</li>
                    <li>边界截断排除：去除接触图像边界的对象部分</li>
                    <li>相互最短距离阈值：当两个对象距离小于阈值时截断轨迹</li>
                </ul>
            </li>
            <li><b>排除指定对象：</b> 可以手动输入要排除的对象ID（逗号分隔）</li>
            <li><b>筛选结果预览：</b> 显示筛选后的对象可视化，包括：
                <ul>
                    <li>彩色对象表示：每个对象赋予不同颜色</li>
                    <li>对象ID标签：清晰显示每个对象的唯一标识符</li>
                    <li>椭圆主轴和次轴：红色直线表示主轴（长轴），蓝色直线表示次轴（短轴）</li>
                    <li>对象轨迹：显示对象移动路径</li>
                </ul>
            </li>
            <li><b>统计信息：</b> 显示原始对象总数和通过筛选的对象数量</li>
            <li><b>筛选日志：</b> 详细记录筛选过程和每个对象的筛选结果及原因</li>
            <li><b>保存功能：</b> 将筛选结果保存为图像序列和数据表格（Excel/CSV）</li>
        </ul>
        
        <h4>4. 使用指南</h4>
        <ul>
            <li>提供详细的软件使用说明和功能介绍（当前页面）。</li>
        </ul>
        
        <h3>筛选过滤功能深度解析：</h3>
        <p>筛选过滤模块是本软件的关键高级功能，提供了对分割轨迹数据的深度分析和筛选能力。以下是详细的使用流程和功能解释：</p>
        
        <h4>1. 参数设置理解</h4>
        <ul>
            <li><b>帧率 (FPS)：</b> 定义每秒帧数，对计算对象速度和时间关系至关重要。例如，如果实际视频以1帧/秒拍摄，应设置为1.0；如果是每20秒一帧，则应设置为0.05。帧率调整会影响瞬时速度的计算，以及时间相关的数据分析。</li>
            <li><b>比例系数 (μm/pixel)：</b> 将像素单位转换为实际物理单位的系数。这个值应根据您的显微镜和摄像设置确定。例如，如果1个像素代表2.5微米，则设置为2.5。此系数会影响所有空间测量，包括面积、距离和速度。</li>
        </ul>
        
        <h4>2. 筛选条件详解</h4>
        <ul>
            <li><b>面积区间筛选：</b> 
                <ul>
                    <li>功能：筛选出面积在指定范围内的对象</li>
                    <li>单位：μm²（平方微米）</li>
                    <li>应用场景：去除过小的噪点或过大的聚合体/背景残留</li>
                    <li>工作原理：计算每个对象的像素面积，并乘以比例系数的平方转换为实际面积</li>
                </ul>
            </li>
            <li><b>面积变化率筛选：</b> 
                <ul>
                    <li>功能：当对象面积变化超过阈值时截断其轨迹</li>
                    <li>取值范围：0到1（比例值），表示小面积/大面积的比值</li>
                    <li>应用场景：检测对象融合、分裂或跟踪错误</li>
                    <li>工作原理：计算相邻帧之间面积比（较小值/较大值），低于阈值时判定为显著变化</li>
                </ul>
            </li>
            <li><b>瞬时速度区间：</b> 
                <ul>
                    <li>功能：根据对象的瞬时移动速度筛选</li>
                    <li>单位：μm/s（微米每秒）</li>
                    <li>应用场景：区分不同运动状态的对象，或识别跟踪跳变</li>
                    <li>工作原理：计算相邻帧之间质心位移除以时间间隔</li>
                </ul>
            </li>
            <li><b>总位移区间：</b> 
                <ul>
                    <li>功能：根据对象从起点到终点的直线距离筛选</li>
                    <li>单位：μm（微米）</li>
                    <li>应用场景：区分迁移和非迁移对象</li>
                    <li>工作原理：计算对象第一帧与最后一帧质心之间的直线距离</li>
                </ul>
            </li>
            <li><b>边界截断排除：</b> 
                <ul>
                    <li>功能：当对象接触图像边界时，截断其轨迹</li>
                    <li>应用场景：确保分析的是完整对象，避免部分截断的对象干扰分析</li>
                    <li>工作原理：检测掩膜像素是否接触图像四边</li>
                </ul>
            </li>
            <li><b>相互最短距离阈值：</b> 
                <ul>
                    <li>功能：当两个对象距离小于阈值时截断轨迹</li>
                    <li>单位：μm（微米）</li>
                    <li>应用场景：避免对象交互或拥挤状态的干扰</li>
                    <li>工作原理：计算对象轮廓间的最短距离，低于阈值时截断</li>
                </ul>
            </li>
        </ul>
        
        <h4>3. 筛选结果理解</h4>
        <ul>
            <li><b>完全通过：</b> 对象的整个轨迹都满足所有筛选条件</li>
            <li><b>部分截断：</b> 对象轨迹在某个时间点不满足条件，轨迹被截断但保留有效部分</li>
            <li><b>完全过滤：</b> 对象完全不满足筛选条件，或满足条件的帧数不足以形成有效轨迹</li>
        </ul>
        
        <h4>4. 可视化元素详解</h4>
        <ul>
            <li><b>彩色对象：</b> 每个对象以唯一颜色显示，便于区分</li>
            <li><b>对象ID：</b> 显示在对象中心，与处理阶段的ID一致</li>
            <li><b>椭圆主轴和次轴：</b> 对象经过椭圆拟合后的长轴（红色）和短轴（蓝色），用于分析对象形状和方向</li>
            <li><b>轨迹线：</b> 显示对象从出现到当前帧的移动路径</li>
        </ul>
        
        <h4>5. 数据保存与导出</h4>
        <p>点击"输出保存"按钮可以保存两类数据：</p>
        <ul>
            <li><b>筛选后的掩膜图像：</b> 保存为Filtered_Masks文件夹下的PNG序列，仅包含通过筛选的对象</li>
            <li><b>轨迹数据表格：</b> 保存为Excel（优先）或CSV格式，包含每个通过筛选的对象在各帧的详细属性数据：
                <ul>
                    <li>时间 (time)：以秒为单位</li>
                    <li>面积 (area)：以μm²为单位</li>
                    <li>质心坐标 (center_x, center_y)：以μm为单位</li>
                    <li>主轴长度 (major axis length)：椭圆长轴长度，以μm为单位</li>
                    <li>次轴长度 (minor axis length)：椭圆短轴长度，以μm为单位</li>
                    <li>姿态角度 (posture angle)：cv2.fitEllipse返回的原始角度值，表示椭圆方向，以度为单位</li>
                </ul>
            </li>
        </ul>
        
        <div class="note">
            <h4>关于姿态角度(posture angle)的理解：</h4>
            <p>导出的轨迹数据中的姿态角度是OpenCV的cv2.fitEllipse函数直接返回的原始角度值，表示椭圆的方向。这个角度测量的是椭圆宽度方向（可能是长轴或短轴）与水平线的夹角，范围为0-180度。</p>
            <p>注意：在可视化显示中，系统会自动确定哪个是主轴（长轴）并用红色显示，哪个是次轴（短轴）并用蓝色显示。但保存的角度数据始终是cv2.fitEllipse的原始返回值，没有经过调整。</p>
        </div>
        
        <h3>高级操作指南：</h3>
        
        <h4>边界框操作</h4>
        <ul>
            <li><b>绘制边界框：</b> 在视频画面上按住鼠标左键并拖动来绘制矩形边界框。</li>
            <li><b>选择边界框：</b> 点击已绘制的边界框可以选中它（边界框会以虚线显示）。</li>
            <li><b>删除边界框：</b> 选中边界框后按Delete键可以删除它。</li>
            <li><b>清除所有边界框：</b> 点击"清除边界框"按钮可以移除所有已绘制的边界框。</li>
        </ul>
        
        <h4>视频处理选项</h4>
        <ul>
            <li><b>处理设备选择：</b> 从下拉菜单中选择要使用的处理设备。推荐使用CUDA设备（GPU）以获得最佳性能。</li>
            <li><b>保存处理视频：</b> 选择是否将处理结果保存为视频文件。取消选中此选项可以只保存掩码而不生成视频。</li>
            <li><b>掩码保存：</b> 如果设置了掩码保存目录，系统会将每帧的分割掩码保存为单张8位灰度PNG图像，命名格式为"frame_yyyy.png"，其中yyyy是帧索引。在掩码中，不同对象用不同灰度值表示(对象ID+1)，背景为0值。这种统一格式减少了文件数量，便于后期处理和应用。</li>
        </ul>
        
        <h4>视频预览控制</h4>
        <ul>
            <li><b>帧率控制：</b> 系统会自动按照视频原始帧率播放视频，确保播放速度与原始视频一致。</li>
            <li><b>帧滑块：</b> 可以拖动滑块快速跳转到视频的任意位置。</li>
            <li><b>循环播放：</b> 视频播放到结尾后会自动循环回到开始。</li>
        </ul>
        
        <h4>筛选过滤策略建议</h4>
        <ul>
            <li><b>渐进式筛选：</b> 建议先使用较宽松的条件，然后逐步调整为更严格的参数。</li>
            <li><b>优先使用面积筛选：</b> 首先筛选出合适大小的对象，再应用其他条件。</li>
            <li><b>特定分析策略：</b>
                <ul>
                    <li>研究对象运动：重点使用速度和位移筛选</li>
                    <li>研究对象形态：重点使用面积和面积变化率筛选</li>
                    <li>研究对象相互作用：重点使用相互距离筛选</li>
                </ul>
            </li>
            <li><b>查看筛选日志：</b> 日志区域会详细记录每个对象的筛选结果和原因，帮助您理解和优化筛选策略。</li>
        </ul>
        
        <h3>处理性能优化：</h3>
        <ul>
            <li><b>视频分块处理：</b> 对于超过1000帧的视频，系统会自动使用分块处理策略（每块最多500帧），以减少内存消耗并提高稳定性。</li>
            <li><b>GPU加速：</b> 使用CUDA设备可以显著提高处理速度，特别是对于高分辨率视频。</li>
            <li><b>内存管理：</b> 系统会在处理过程中自动优化内存使用，减少内存占用。</li>
            <li><b>CPU处理：</b> 如果没有可用的GPU，系统会自动回退到CPU处理模式，但处理速度会显著降低。</li>
        </ul>
        
        <h3>常见问题解答：</h3>
        <ol>
            <li>
                <b>问：为什么"开始处理"按钮处于灰色状态？</b><br>
                <b>答：</b>可能原因包括：1) 未选择视频文件；2) 模型文件路径不正确或文件不存在；3) 未标注任何边界框。请确保完成这些步骤后再尝试。
            </li>
            <li>
                <b>问：处理速度很慢，如何提高？</b><br>
                <b>答：</b>处理速度主要受以下因素影响：1) 使用GPU而非CPU；2) 视频分辨率（较低分辨率处理更快）；3) 跟踪对象的数量（更少的对象处理更快）；4) 硬件配置。
            </li>
            <li>
                <b>问：如何提高跟踪准确性？</b><br>
                <b>答：</b>1) 确保第一帧上的标注边界框尽可能准确覆盖整个目标对象；2) 对于快速移动或变形严重的对象，可能需要在关键帧上重新标注；3) 避免标注过小或细节不清晰的对象。
            </li>
            <li>
                <b>问：可以处理多长的视频？</b><br>
                <b>答：</b>理论上没有时长限制，但建议对超长视频（如超过10分钟）进行分段处理，以获得更好的效果和更高的稳定性。
            </li>
            <li>
                <b>问：如何使用保存的掩码？</b><br>
                <b>答：</b>掩码以8位灰度图像格式保存，每个像素值代表不同的对象ID(值 = 对象ID + 1)或背景(值 = 0)。与传统方法不同，我们将所有对象保存在同一张图像中，减少文件数量。这些掩码可用于后期处理如视觉特效、背景替换、对象统计分析等。
            </li>
            <li>
                <b>问：为什么轨迹数据中的姿态角度与可视化显示的方向不同？</b><br>
                <b>答：</b>轨迹数据中保存的是cv2.fitEllipse函数返回的原始角度值，表示椭圆宽度方向与水平线的夹角。而可视化显示中，系统会自动确定哪个是长轴并用红色显示，哪个是短轴并用蓝色显示。数据保存时没有对角度进行调整，保留了原始值以便进行精确分析。
            </li>
            <li>
                <b>问：如何确定合适的比例系数(μm/pixel)？</b><br>
                <b>答：</b>比例系数应根据您的显微镜和摄像设置确定。常见的方法包括：1) 使用已知尺寸的校准标尺；2) 根据显微镜规格和摄像头像素尺寸计算；3) 参考显微镜软件提供的数值。正确的比例系数对于获得准确的测量结果至关重要。
            </li>
        </ol>
        
        <h3>技术规格：</h3>
        <ul>
            <li><b>支持的视频格式：</b> MP4, AVI, MOV, MKV</li>
            <li><b>支持的模型：</b> SAM2 (Segment Anything Model 2)</li>
            <li><b>处理设备：</b> CUDA (GPU) 或 CPU</li>
            <li><b>输出格式：</b> 视频文件 (MP4) 和/或二值掩码图像 (PNG)</li>
            <li><b>数据导出格式：</b> Excel (.xlsx) 或 CSV (.csv)</li>
            <li><b>系统要求：</b> 
                <ul>
                    <li>最低: CPU处理模式下4GB内存</li>
                    <li>推荐: CUDA兼容GPU，8GB+ VRAM，16GB系统内存</li>
                </ul>
            </li>
        </ul>
        
        <h3>注意事项：</h3>
        <ul>
            <li>处理速度取决于视频长度、分辨率和计算设备性能。</li>
            <li>强烈建议使用支持CUDA的GPU进行处理以获得更好的性能。</li>
            <li>对于较长的视频，系统会自动使用分块处理方式以减少内存消耗。</li>
            <li>初始边界框的质量会直接影响跟踪效果，请确保准确标注目标对象。</li>
            <li>处理过程中可能会出现警告信息，多数与优化相关，不影响最终结果。</li>
            <li>如需中断处理，可以关闭应用程序，下次重新打开后重新开始处理。</li>
            <li>轨迹数据保存的角度值是原始的椭圆拟合角度，在数据分析时需正确理解其含义。</li>
        </ul>
        """)
        guide_layout.addWidget(guide_text)
    
    def on_bbox_added(self, bbox):
        """当添加新边界框时的处理"""
        self.log_message(f"添加边界框: ID={bbox[4]}, 坐标=({int(bbox[0])},{int(bbox[1])},{int(bbox[2])},{int(bbox[3])})", "success")
    
    def on_bbox_selected(self, index):
        """当选中边界框时的处理"""
        if index >= 0 and index < len(self.video_label.overlay_layer.bboxes):
            bbox = self.video_label.overlay_layer.bboxes[index]
            self.log_message(f"选中边界框: ID={bbox[4]}", "info")
    
    def on_bbox_deleted(self, bbox_id):
        """当删除边界框时的处理"""
        self.log_message(f"删除边界框: ID={bbox_id}", "warning")
    
    def browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*)"
        )
        if file_path:
            self.video_path = file_path
            self.video_path_edit.setText(os.path.basename(file_path))
            self.video_path_edit.setToolTip(file_path)
            
            # 获取原视频所在目录和文件名（不含扩展名）
            video_dir = os.path.dirname(file_path)
            video_filename = os.path.basename(file_path)
            video_name_without_ext = os.path.splitext(video_filename)[0]
            
            # 设置输出视频路径为原视频同级目录下的processed_{原视频文件名}
            self.output_path = os.path.join(video_dir, f"processed_{video_filename}")
            self.output_path_edit.setText(self.output_path)
            self.output_path_edit.setToolTip(self.output_path)
            
            # 设置掩码保存目录为原视频同级目录下的masks_{原视频文件名}文件夹
            self.mask_dir = os.path.join(video_dir, f"masks_{video_name_without_ext}")
            self.mask_dir_edit.setText(self.mask_dir)
            self.mask_dir_edit.setToolTip(self.mask_dir)
            
            # 将文件选择记录到日志
            self.log_message(f"选择视频文件: {file_path}", "info")
            self.log_message(f"输出视频将保存到: {self.output_path}", "info")
            self.log_message(f"掩码图片将保存到: {self.mask_dir}", "info")
            
            # 加载视频第一帧
            self.load_video()
            
            # 检查是否可以启用开始按钮
            self.check_start_enabled()
    
    def browse_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择SAM2模型文件", "", "模型文件 (*.pt *.pth);;所有文件 (*)"
        )
        if file_path:
            self.model_path = file_path
            self.model_path_edit.setText(os.path.basename(file_path))
            self.model_path_edit.setToolTip(file_path)
            self.log_message(f"选择模型文件: {file_path}", "info")
            self.check_start_enabled()
    
    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "设置输出视频文件", self.output_path_edit.text(), "视频文件 (*.mp4 *.avi);;所有文件 (*)"
        )
        if file_path:
            self.output_path = file_path
            self.output_path_edit.setText(file_path)  # 显示完整路径
            self.output_path_edit.setToolTip(file_path)
            self.log_message(f"设置输出视频: {file_path}", "info")
    
    def browse_mask_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择掩码保存目录", ""
        )
        if dir_path:
            self.mask_dir = dir_path
            self.mask_dir_edit.setText(dir_path)  # 显示完整路径
            self.mask_dir_edit.setToolTip(dir_path)
            self.log_message(f"设置掩码保存目录: {dir_path}", "info")
    
    def load_video(self):
        if not self.video_path or not os.path.exists(self.video_path):
            return
        
        # 清空日志
        self.log_text.clear()
        self.log_message(f"加载视频: {self.video_path}", "highlight")
        
        # 停止之前的视频线程
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
        
        # 获取视频信息
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.log_message(f"错误: 无法打开视频文件 {self.video_path}", "error")
            return
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()
        
        self.log_message(f"视频分辨率: {width}x{height}", "info")
        self.log_message(f"帧率: {fps:.2f} FPS", "info")
        self.log_message(f"总帧数: {total_frames}", "info")
        self.log_message(f"时长: {duration:.2f} 秒", "info")
        
        # 设置滑块范围
        self.frame_slider.setRange(0, total_frames - 1)
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(True)
        self.frame_info_label.setText(f"当前帧: 1 / {total_frames}")
        
        # 启用播放/暂停按钮
        self.play_pause_btn.setEnabled(True)
        self.play_pause_btn.setText("播放")
        self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        
        # 清除之前的边界框
        count = self.video_label.clear_bboxes()
        if count > 0:
            self.log_message(f"清除了 {count} 个已有边界框", "warning")
        
        # 创建新的视频线程
        self.video_thread = VideoThread(self.video_path)
        self.video_thread.frame_ready.connect(self.update_video_frame)
        self.video_thread.frame_index_changed.connect(self.update_frame_slider)  # 连接帧索引变化信号
        
        # 启动视频线程 - 线程默认已设置为暂停状态
        self.video_thread.start()
        self.log_message("视频加载完成，请在第一帧上标注目标边界框", "success")
    
    def update_frame_slider(self, frame_index):
        """更新当前帧滑块位置，但不触发新的帧加载"""
        # 暂时断开滑块的valueChanged信号连接，避免循环触发
        self.frame_slider.blockSignals(True)
        self.frame_slider.setValue(frame_index)
        self.frame_slider.blockSignals(False)
        
        # 更新帧信息标签，将帧索引加1使其从1开始显示
        total_frames = self.video_thread.total_frames if self.video_thread else 0
        self.frame_info_label.setText(f"当前帧: {frame_index+1} / {total_frames}")
    
    def update_video_frame(self, frame):
        if frame is not None:
            self.video_label.set_frame(frame)
    
    def set_frame_index(self, index):
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.set_frame_index(index)
    
    def check_start_enabled(self):
        # 启用开始按钮的条件
        video_ok = bool(self.video_path and os.path.exists(self.video_path))
        model_ok = bool(self.model_path and os.path.exists(self.model_path))
        
        # 如果模型路径设置为默认值但文件不存在，检查是否创建了该目录结构
        if not model_ok and self.model_path == "models/sam2/checkpoints/sam2.1_hiera_tiny.pt":
            # 仅在用户有明确加载视频的意图时启用按钮
            model_ok = bool(self.video_path and os.path.exists(self.video_path))
        
        self.start_btn.setEnabled(video_ok and model_ok)
        
        # 如果条件满足，更改按钮样式为突出显示
        if video_ok and model_ok:
            self.start_btn.setStyleSheet("""
                font-weight: bold; 
                font-size: 14px; 
                padding: 12px;
                background-color: #4CAF50;
                border-radius: 6px;
            """)
        else:
            self.start_btn.setStyleSheet("""
                font-weight: bold; 
                font-size: 14px; 
                padding: 12px;
                background-color: #cccccc;
                color: #888888;
                border-radius: 6px;
            """)
    
    def start_processing(self):
        # 获取边界框列表
        bbox_list = self.video_label.get_bbox_list()
        if not bbox_list:
            self.log_message("错误: 未标注任何边界框！", "error")
            QMessageBox.warning(self, "警告", "请至少绘制一个边界框！")
            return
        
        # 准备处理参数
        class Args:
            pass
        
        args = Args()
        args.video_path = self.video_path
        args.model_path = self.model_path
        args.video_output_path = self.output_path_edit.text() if os.path.isabs(self.output_path_edit.text()) else self.output_path
        args.save_to_video = self.save_video_check.isChecked()
        
        # 根据保存掩码选项决定是否使用掩码保存目录
        if self.save_mask_check.isChecked():
            # 确保掩码目录存在
            mask_dir = Path(self.mask_dir)
            if not mask_dir.exists():
                os.makedirs(self.mask_dir, exist_ok=True)
                self.log_message(f"创建掩码保存目录: {self.mask_dir}", "info")
            args.mask_dir = self.mask_dir
        else:
            args.mask_dir = None
            
        args.device = self.device_combo.currentData()
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        
        # 清空日志
        self.log_text.clear()
        self.log_message("====== 开始处理视频 ======", "highlight")
        self.log_message("参数设置:", "highlight")
        self.log_message(f"输入视频: {args.video_path}", "info")
        self.log_message(f"使用模型: {args.model_path}", "info")
        self.log_message(f"输出路径: {args.video_output_path}", "info")
        self.log_message(f"处理设备: {args.device}", "info")
        if args.mask_dir:
            self.log_message(f"掩码保存目录: {args.mask_dir}", "info")
            self.log_message("掩码格式: 每帧一张8位灰度图像，像素值表示对象ID+1，背景为0", "info")
        else:
            self.log_message("不保存掩码", "warning")
        self.log_message(f"保存处理视频: {'是' if args.save_to_video else '否'}", "info")
        
        self.log_message("标注信息:", "highlight")
        self.log_message(f"边界框数量: {len(bbox_list)}", "info")
        for i, bbox in enumerate(bbox_list):
            self.log_message(f"边界框 {i}: ({int(bbox[0])},{int(bbox[1])},{int(bbox[2])},{int(bbox[3])})", "info")
        
        self.log_message("-" * 50, "info")
        self.log_message("正在准备处理环境...", "info")
        
        # 创建处理线程
        self.processing_thread = ProcessingThread(args, bbox_list)
        self.processing_thread.progress_update.connect(self.update_progress)
        self.processing_thread.progress_percent.connect(self.update_progress_bar)
        self.processing_thread.processing_finished.connect(self.processing_done)
        self.processing_thread.frame_processed.connect(self.update_result_frame)
        
        # 重置并显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 禁用开始按钮
        self.start_btn.setEnabled(False)
        
        # 开始处理
        self.processing_thread.start()
    
    def update_progress(self, message):
        # 根据消息内容确定类型
        msg_type = "info"
        if "错误" in message or "出错" in message:
            msg_type = "error"
        elif "警告" in message:
            msg_type = "warning"
        elif "完成" in message or "成功" in message:
            msg_type = "success"
        elif "初始化" in message or "开始" in message:
            msg_type = "highlight"
            
        self.log_message(message, msg_type)
    
    def processing_done(self, success, message):
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 更新日志
        if success:
            self.log_message("====== 处理完成 ======", "highlight")
            self.log_message(f"处理成功！输出文件: {self.output_path_edit.text()}", "success")
            # 显示成功提示
            QMessageBox.information(self, "处理完成", f"视频处理成功！\n输出文件: {self.output_path_edit.text()}")
            # 自动切换到结果预览标签页
            self.tab_widget.setCurrentIndex(1)  # 第二个标签页是结果预览
            
            # 启用结果预览的播放/暂停按钮
            self.result_play_pause_btn.setEnabled(True)
            
            # 初始化结果视频线程
            self.load_result_video()
            
            # 如果掩膜目录存在，自动设置到筛选过滤标签页
            if self.mask_dir and os.path.exists(self.mask_dir):
                self.filter_mask_dir_edit.setText(self.mask_dir)
                self.filter_mask_dir_edit.setToolTip(self.mask_dir)
                
                # 检查掩膜目录中是否有图片
                mask_files = [f for f in os.listdir(self.mask_dir) if f.endswith('.png') and f.startswith('frame_')]
                if mask_files:
                    self.apply_filter_btn.setEnabled(True)
                    self.log_message(f"已自动加载掩膜目录: {self.mask_dir}", "info")
        else:
            self.log_message("====== 处理失败 ======", "highlight")
            self.log_message(f"处理失败: {message}", "error")
            # 显示错误提示
            QMessageBox.critical(self, "处理失败", f"视频处理失败！\n错误信息: {message}")
        
        # 重新启用开始按钮
        self.start_btn.setEnabled(True)
    
    def load_result_video(self):
        """加载处理后的视频用于预览"""
        output_path = self.output_path_edit.text()
        if not os.path.exists(output_path):
            self.log_message(f"警告: 无法找到输出视频文件 {output_path}", "warning")
            return
            
        self.log_message(f"正在加载处理结果视频: {output_path}", "info")
        
        # 停止之前的结果视频线程
        if self.result_video_thread and self.result_video_thread.isRunning():
            self.result_video_thread.stop()
        
        # 创建新的视频线程用于结果预览
        self.result_video_thread = VideoThread(output_path)
        self.result_video_thread.frame_ready.connect(self.update_result_video_frame)
        self.result_video_thread.frame_index_changed.connect(self.update_result_frame_slider)
        
        # 启动视频线程 - 保持暂停状态
        self.result_video_thread.start()
        
        # 获取视频信息
        try:
            cap = cv2.VideoCapture(output_path)
            if cap.isOpened():
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                self.log_message(f"结果视频信息: {width}x{height}, {fps:.1f} FPS, {total_frames} 帧", "info")
        except Exception as e:
            self.log_message(f"获取结果视频信息时出错: {str(e)}", "warning")
        
        # 更新播放按钮状态
        self.result_play_pause_btn.setText("播放")
        self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.result_play_pause_btn.setEnabled(True)
    
    def update_result_frame_slider(self, frame_index):
        """更新结果预览帧滑块位置，但不触发新的帧加载"""
        # 暂时断开滑块的valueChanged信号连接，避免循环触发
        self.result_slider.blockSignals(True)
        self.result_slider.setValue(frame_index)
        self.result_slider.blockSignals(False)
        
        # 更新帧信息标签
        total_frames = self.result_video_thread.total_frames if self.result_video_thread else 0
        percent = int((frame_index + 1) / total_frames * 100) if total_frames > 0 else 0
        self.result_info_label.setText(f"处理结果: {frame_index+1} / {total_frames} ({percent}%)")
    
    def update_result_video_frame(self, frame):
        """更新结果预览的视频帧"""
        if frame is not None:
            self.result_label.setVideoFrame(frame)
    
    def set_result_frame_index(self, index):
        """设置结果预览的帧索引"""
        if self.result_video_thread and self.result_video_thread.isRunning():
            self.result_video_thread.set_frame_index(index)
    
    def toggle_result_play_pause(self):
        """切换结果预览的播放/暂停状态"""
        if self.result_video_thread and self.result_video_thread.isRunning():
            self.result_video_thread.toggle_pause()
            
            # 获取当前状态以更新按钮
            mutex = QMutex()
            mutex.lock()
            is_paused = self.result_video_thread.paused
            mutex.unlock()
            
            # 更新按钮文本
            if is_paused:
                self.result_play_pause_btn.setText("播放")
                self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            else:
                self.result_play_pause_btn.setText("暂停")
                self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
    
    def open_output_folder(self):
        output_path = self.output_path
        if not output_path:
            return
        
        output_dir = os.path.dirname(os.path.abspath(output_path))
        if os.path.exists(output_dir):
            # 打开输出目录
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', output_dir])
            else:  # Linux
                subprocess.run(['xdg-open', output_dir])

    def toggle_play_pause(self):
        """切换视频播放/暂停状态"""
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.toggle_pause()
            
            # 获取当前状态以更新按钮
            mutex = QMutex()
            mutex.lock()
            is_paused = self.video_thread.paused
            mutex.unlock()
            
            # 更新按钮文本
            if is_paused:
                self.play_pause_btn.setText("播放")
                self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
                self.log_message("视频预览已暂停", "info")
            else:
                self.play_pause_btn.setText("暂停")
                self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
                self.log_message("视频预览开始播放", "info")

    def update_progress_bar(self, percent):
        """更新进度条百分比"""
        self.progress_bar.setValue(percent)

    # 添加日志记录方法，用不同颜色区分信息类型
    def log_message(self, message, msg_type="info"):
        """记录信息到日志区域，使用不同颜色区分不同类型
        
        参数:
            message: 要显示的消息文本
            msg_type: 消息类型，可以是 "info"(默认), "warning", "error", "success"
        """
        # 根据消息类型设置颜色
        colors = {
            "info": "black",
            "warning": "#FF8C00",  # 深橙色
            "error": "#FF0000",    # 红色
            "success": "#008000",  # 绿色
            "highlight": "#0000FF" # 蓝色，用于高亮重要信息
        }
        
        color = colors.get(msg_type, "black")
        
        # 添加带颜色的文本
        self.log_text.append(f'<span style="color:{color};">{message}</span>')
        
        # 确保滚动到最新内容并强制更新滚动条
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()
        
        # 强制刷新滚动条
        QApplication.processEvents()

    def update_result_frame(self, frame, current_idx, total_frames):
        """更新结果预览帧"""
        if frame is None:
            return
        
        # 更新结果预览标签
        self.result_label.setVideoFrame(frame)
        
        # 更新结果预览滑块
        if self.result_slider.maximum() != total_frames - 1:
            self.result_slider.setRange(0, total_frames - 1)
        self.result_slider.setValue(current_idx)
        self.result_slider.setEnabled(True)
        
        # 更新结果信息标签
        percent = int((current_idx + 1) / total_frames * 100)
        self.result_info_label.setText(f"处理结果: {current_idx+1} / {total_frames} ({percent}%)")
        
        # 定期更新日志（避免大量更新），每50帧或达到100%时更新一次
        if current_idx % 50 == 0 or current_idx == total_frames - 1:
            self.log_message(f"已处理: {current_idx+1}/{total_frames} 帧 ({percent}%)", "info")
    
    # ===== 筛选过滤功能相关方法 =====
    
    def browse_filter_mask_dir(self):
        """浏览掩膜文件夹"""
        # 先尝试使用已有的掩膜目录
        initial_dir = ""
        if hasattr(self, 'mask_dir') and self.mask_dir and os.path.exists(self.mask_dir):
            initial_dir = self.mask_dir
        
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择掩膜图片文件夹", initial_dir
        )
        
        if dir_path:
            self.filter_mask_dir_edit.setText(dir_path)
            self.filter_mask_dir_edit.setToolTip(dir_path)
            
            # 检查是否含有掩膜图片
            mask_files = [f for f in os.listdir(dir_path) if f.endswith('.png') and f.startswith('frame_')]
            
            if mask_files:
                self.log_message(f"找到 {len(mask_files)} 个掩膜图片", "info")
                self.apply_filter_btn.setEnabled(True)
            else:
                self.log_message(f"警告: 在所选文件夹中未找到掩膜图片", "warning")
                self.apply_filter_btn.setEnabled(False)
    
    def apply_mask_filter(self):
        """应用掩膜筛选"""
        # 获取掩膜目录
        mask_dir = self.filter_mask_dir_edit.text()
        if not mask_dir or not os.path.exists(mask_dir):
            self.log_message("错误: 请先选择有效的掩膜文件夹", "error")
            return
        
        # 获取参数
        try:
            fps = float(self.fps_input.text())
            um_per_pixel = float(self.um_per_pixel_input.text())
        except ValueError:
            self.log_message("错误: 帧率和像素比例必须为有效数字", "error")
            return
        
        # 解析排除ID列表
        exclude_ids = []
        if self.exclude_ids_input.text().strip():
            try:
                exclude_ids = [int(x.strip()) for x in self.exclude_ids_input.text().split(',')]
            except ValueError:
                self.log_message("错误: 排除ID必须为整数，多个ID用逗号分隔", "error")
                return
        
        # 构建筛选参数
        filter_params = {
            'exclude_ids': exclude_ids
        }
        
        # 面积区间
        if self.area_filter_check.isChecked():
            try:
                area_min = float(self.area_min_input.text())
                area_max = float(self.area_max_input.text())
                filter_params['area_filter'] = True
                filter_params['area_min'] = area_min
                filter_params['area_max'] = area_max
            except ValueError:
                self.log_message("错误: 面积区间必须为有效数字", "error")
                return
        
        # 面积变化率
        if self.area_change_check.isChecked():
            try:
                area_change_threshold = float(self.area_change_input.text())
                if not 0 <= area_change_threshold <= 1:
                    raise ValueError("面积变化率必须在0到1之间")
                filter_params['area_change_filter'] = True
                filter_params['area_change_threshold'] = area_change_threshold
            except ValueError as e:
                self.log_message(f"错误: {str(e)}", "error")
                return
        
        # 瞬时速度区间
        if self.velocity_check.isChecked():
            try:
                velocity_min = float(self.velocity_min_input.text())
                velocity_max = float(self.velocity_max_input.text())
                filter_params['velocity_filter'] = True
                filter_params['velocity_min'] = velocity_min
                filter_params['velocity_max'] = velocity_max
            except ValueError:
                self.log_message("错误: 速度区间必须为有效数字", "error")
                return
        
        # 总位移区间
        if self.displacement_check.isChecked():
            try:
                displacement_min = float(self.displacement_min_input.text())
                displacement_max = float(self.displacement_max_input.text())
                filter_params['displacement_filter'] = True
                filter_params['displacement_min'] = displacement_min
                filter_params['displacement_max'] = displacement_max
            except ValueError:
                self.log_message("错误: 位移区间必须为有效数字", "error")
                return
        
        # 边界截断排除
        filter_params['boundary_filter'] = self.boundary_check.isChecked()
        
        # 相互最短距离
        if self.min_distance_check.isChecked():
            try:
                min_distance_threshold = float(self.min_distance_input.text())
                filter_params['min_distance_filter'] = True
                filter_params['min_distance_threshold'] = min_distance_threshold
            except ValueError:
                self.log_message("错误: 距离阈值必须为有效数字", "error")
                return
        
        # 清空筛选日志区域
        self.filter_log_text.clear()
        
        # 记录筛选参数到日志
        self.filter_log_message("====== 开始筛选掩膜数据 ======", "highlight")
        self.filter_log_message(f"掩膜文件夹: {mask_dir}", "info")
        self.filter_log_message(f"帧率: {fps} FPS", "info")
        self.filter_log_message(f"像素比例: {um_per_pixel} μm/pixel", "info")
        
        # 记录启用的筛选条件
        active_filters = []
        if filter_params.get('area_filter', False):
            active_filters.append(f"面积区间: {filter_params['area_min']} - {filter_params['area_max']} μm²")
        if filter_params.get('area_change_filter', False):
            active_filters.append(f"面积变化率阈值: {filter_params['area_change_threshold']}")
        if filter_params.get('velocity_filter', False):
            active_filters.append(f"瞬时速度区间: {filter_params['velocity_min']} - {filter_params['velocity_max']} μm/s")
        if filter_params.get('displacement_filter', False):
            active_filters.append(f"总位移区间: {filter_params['displacement_min']} - {filter_params['displacement_max']} μm")
        if filter_params.get('boundary_filter', False):
            active_filters.append("边界截断排除")
        if filter_params.get('min_distance_filter', False):
            active_filters.append(f"相互最短距离阈值: {filter_params['min_distance_threshold']} μm")
        if filter_params.get('exclude_ids', []):
            active_filters.append(f"排除指定ID: {', '.join(map(str, filter_params['exclude_ids']))}")
        
        if active_filters:
            self.filter_log_message("启用的筛选条件:", "highlight")
            for f in active_filters:
                self.filter_log_message(f"- {f}", "info")
        else:
            self.filter_log_message("未启用任何筛选条件，将保留所有对象", "warning")
        
        # 创建并启动筛选线程
        self.filter_thread = FilterMaskThread(mask_dir, fps, um_per_pixel, filter_params)
        self.filter_thread.progress_update.connect(self.update_filter_progress)
        self.filter_thread.progress_percent.connect(self.update_filter_progress_bar)
        self.filter_thread.filter_finished.connect(self.filter_processing_done)
        self.filter_thread.frame_processed.connect(self.update_filter_frame)
        self.filter_thread.stats_update.connect(self.update_filter_stats)
        
        # 显示进度条
        self.filter_progress_bar.setValue(0)
        self.filter_progress_bar.setVisible(True)
        
        # 禁用筛选按钮
        self.apply_filter_btn.setEnabled(False)
        
        # 开始筛选
        self.filter_thread.start()
    
    def update_filter_stats(self, total_objects, passed_objects):
        """更新筛选统计信息"""
        self.filter_stats_label.setText(f"对象数量: {total_objects} | 通过筛选: {passed_objects}")
    
    def update_filter_frame(self, frame, current_idx, total_frames):
        """更新筛选结果预览帧"""
        if frame is None:
            return
        
        # 更新筛选预览标签
        self.filter_video_label.setVideoFrame(frame)
        
        # 更新滑块
        if self.filter_slider.maximum() != total_frames - 1:
            self.filter_slider.setRange(0, total_frames - 1)
        self.filter_slider.setValue(current_idx)
        self.filter_slider.setEnabled(True)
        
        # 更新信息标签
        percent = int((current_idx + 1) / total_frames * 100)
        self.filter_info_label.setText(f"筛选结果: {current_idx+1}/{total_frames} ({percent}%)")
    
    def start_filter_video_playback(self):
        """初始化并开始筛选结果视频播放"""
        if not hasattr(self, 'filter_thread') or not self.filter_thread.filtered_masks:
            return
        
        # 停止之前的视频线程
        if hasattr(self, 'filter_video_thread') and self.filter_video_thread.isRunning():
            self.filter_video_thread.stop()
        
        # 创建新的视频线程
        self.filter_video_thread = FilterVideoThread(self.filter_thread.filtered_masks)
        self.filter_video_thread.frame_ready.connect(self.filter_video_label.setVideoFrame)
        self.filter_video_thread.frame_index_changed.connect(self.update_filter_slider)
        
        # 设置帧率
        try:
            fps = float(self.fps_input.text())
            # 限制预览帧率在合理范围
            preview_fps = min(max(fps, 1), 30)
            self.filter_video_thread.set_fps(preview_fps)
        except:
            pass
        
        # 开始线程
        self.filter_video_thread.start()
        
        # 更新播放按钮状态
        self.filter_play_pause_btn.setText("播放")
        self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
    
    def update_filter_slider(self, frame_index):
        """更新筛选预览滑块位置"""
        # 暂时断开滑块的valueChanged信号连接，避免循环触发
        self.filter_slider.blockSignals(True)
        self.filter_slider.setValue(frame_index)
        self.filter_slider.blockSignals(False)
        
        # 更新帧信息标签
        total_frames = len(self.filter_thread.filtered_masks) if hasattr(self, 'filter_thread') else 0
        percent = int((frame_index + 1) / total_frames * 100) if total_frames > 0 else 0
        self.filter_info_label.setText(f"筛选结果: {frame_index+1}/{total_frames} ({percent}%)")
    
    def set_filter_frame_index(self, index):
        """设置筛选预览的帧索引"""
        if hasattr(self, 'filter_video_thread') and self.filter_video_thread.isRunning():
            self.filter_video_thread.set_frame_index(index)
    
    def toggle_filter_play_pause(self):
        """切换筛选预览的播放/暂停状态"""
        if hasattr(self, 'filter_video_thread') and self.filter_video_thread.isRunning():
            self.filter_video_thread.toggle_pause()
            
            # 获取当前状态以更新按钮
            mutex = QMutex()
            mutex.lock()
            is_paused = self.filter_video_thread.paused
            mutex.unlock()
            
            # 更新按钮文本
            if is_paused:
                self.filter_play_pause_btn.setText("播放")
                self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            else:
                self.filter_play_pause_btn.setText("暂停")
                self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
    
    def save_filter_results(self):
        """保存筛选结果"""
        if not hasattr(self, 'filter_thread') or not self.filter_thread.object_trajectories:
            self.log_message("错误: 没有可保存的筛选结果", "error")
            return
        
        # 获取当前日期时间用于文件名
        now = QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')
        
        try:
            # 1. 创建保存文件夹
            mask_dir = self.filter_mask_dir_edit.text()
            base_dir = os.path.dirname(mask_dir)
            
            # 创建Filtered_Masks文件夹
            filtered_masks_dir = os.path.join(base_dir, "Filtered_Masks")
            os.makedirs(filtered_masks_dir, exist_ok=True)
            
            # 2. 保存筛选后的掩膜图片
            self.log_message("正在保存筛选后的掩膜图片...", "info")
            
            # 获取原始掩膜尺寸
            h, w = self.filter_thread.original_masks[0].shape if self.filter_thread.original_masks else (0, 0)
            
            # 创建新的掩膜图像保存筛选后的对象
            total_frames = len(self.filter_thread.original_masks)
            object_ids = list(self.filter_thread.object_trajectories.keys())
            
            # 对每一帧保存筛选后的掩膜
            for frame_idx in range(total_frames):
                # 创建空白掩膜
                filtered_mask = np.zeros((h, w), dtype=np.uint8)
                
                # 查找当前帧中通过筛选的对象
                for obj_id in object_ids:
                    # 检查该对象是否在当前帧有数据
                    obj_in_frame = False
                    obj_data = self.filter_thread.object_trajectories[obj_id]
                    
                    for data_point in obj_data:
                        time_sec = data_point['time']
                        frame_time = frame_idx / float(self.fps_input.text())
                        
                        # 允许一定的误差
                        if abs(time_sec - frame_time) < 0.001:
                            obj_in_frame = True
                            break
                    
                    if obj_in_frame:
                        # 从原始掩膜提取此对象
                        original_mask = self.filter_thread.original_masks[frame_idx]
                        obj_pixels = (original_mask == obj_id)
                        
                        # 将对象添加到新掩膜
                        filtered_mask[obj_pixels] = obj_id
                
                # 保存结果掩膜
                output_path = os.path.join(filtered_masks_dir, f"frame_{frame_idx:04d}.png")
                cv2.imwrite(output_path, filtered_mask)
                
                # 每保存10个掩膜更新一次进度
                if frame_idx % 10 == 0 or frame_idx == total_frames - 1:
                    percent = int((frame_idx + 1) / total_frames * 100)
                    self.log_message(f"掩膜保存进度: {frame_idx+1}/{total_frames} ({percent}%)", "info")
            
            # 3. 保存轨迹数据到Excel
            self.log_message("正在保存轨迹数据到Excel...", "info")
            
            try:
                import pandas as pd
                
                # 创建Excel文件
                excel_path = os.path.join(base_dir, f"Trajectories_Results_{now}.xlsx")
                
                # 创建ExcelWriter
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    for obj_id, trajectory in self.filter_thread.object_trajectories.items():
                        # 转换为DataFrame
                        df = pd.DataFrame(trajectory)
                        
                        # 重命名列
                        df = df.rename(columns={
                            'time': 'time (s)',
                            'area': 'area (μm²)',
                            'center_x': 'center_x (μm)',
                            'center_y': 'center_y (μm)',
                            'major_axis': 'major axis length (μm)',
                            'minor_axis': 'minor axis length (μm)',
                            'angle': 'posture angle (°)'
                        })
                        
                        # 保存到Excel的sheet
                        sheet_name = f"Object_{obj_id}"
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # 自适应列宽
                        worksheet = writer.sheets[sheet_name]
                        for i, col in enumerate(df.columns):
                            max_width = max(
                                df[col].astype(str).map(len).max(),
                                len(col)
                            ) + 2  # 添加一些额外空间
                            worksheet.column_dimensions[chr(65 + i)].width = max_width
                
                self.log_message(f"轨迹数据已保存到: {excel_path}", "success")
                
            except ImportError:
                # 如果没有pandas，使用CSV格式保存
                self.log_message("警告: 未安装pandas库，将使用CSV格式保存轨迹数据", "warning")
                
                # 为每个对象创建CSV文件
                for obj_id, trajectory in self.filter_thread.object_trajectories.items():
                    csv_path = os.path.join(base_dir, f"Object_{obj_id}_Trajectory_{now}.csv")
                    
                    with open(csv_path, 'w', newline='') as csvfile:
                        # 写入标题行
                        header = "time (s),area (μm²),center_x (μm),center_y (μm),major axis length (μm),minor axis length (μm),posture angle (°)\n"
                        csvfile.write(header)
                        
                        # 写入数据行
                        for point in trajectory:
                            line = f"{point['time']},{point['area']},{point['center_x']},{point['center_y']},{point['major_axis']},{point['minor_axis']},{point['angle']}\n"
                            csvfile.write(line)
                
                self.log_message(f"轨迹数据已保存到CSV文件", "success")
            
            # 完成保存
            self.log_message("====== 保存完成 ======", "highlight")
            self.log_message(f"筛选掩膜已保存到: {filtered_masks_dir}", "success")
            
            # 显示成功消息
            QMessageBox.information(self, "保存成功", 
                f"筛选结果保存成功！\n\n掩膜保存路径:\n{filtered_masks_dir}\n\n轨迹数据保存路径:\n{excel_path}")
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            
            self.log_message(f"保存失败: {error_msg}", "error")
            self.log_message(f"堆栈跟踪:\n{stack_trace}", "error")
            
            # 显示错误消息
            QMessageBox.critical(self, "保存失败", f"保存筛选结果时出错:\n{error_msg}")

    def filter_log_message(self, message, msg_type="info"):
        """在筛选过滤日志区域添加消息，并根据消息类型设置样式"""
        color_map = {
            "info": "#424242",     # 黑色 - 一般信息
            "success": "#2E7D32",  # 绿色 - 成功消息
            "warning": "#FF8F00",  # 橙色 - 警告消息
            "error": "#C62828",    # 红色 - 错误消息
            "highlight": "#1565C0", # 蓝色 - 高亮信息
            "progress": "#6A1B9A"  # 紫色 - 进度信息
        }
        
        # 设置文本颜色
        color = color_map.get(msg_type, "#424242")
        
        # 直接设置带颜色的消息文本，不添加时间前缀
        formatted_message = f"<span style='color: {color};'>{message}</span>"
        
        # 添加到文本框
        self.filter_log_text.append(formatted_message)
        
        # 滚动到底部
        self.filter_log_text.verticalScrollBar().setValue(
            self.filter_log_text.verticalScrollBar().maximum()
        )
        
        # 如果有错误或警告，也记录到主日志中
        if msg_type in ["error", "warning"]:
            self.log_message(message, msg_type)
        
        # 更新UI
        QApplication.processEvents()
    
    def update_filter_progress(self, message):
        """更新筛选处理进度信息"""
        # 根据消息内容确定类型
        msg_type = "info"
        if "错误" in message:
            msg_type = "error"
        elif "警告" in message:
            msg_type = "warning"
        elif "成功" in message or "完成" in message:
            msg_type = "success"
        elif "进度" in message or "剩余时间" in message or "帧" in message:
            msg_type = "progress"
        
        # 在筛选日志区域显示消息
        self.filter_log_message(message, msg_type)
    
    def update_filter_progress_bar(self, percent):
        """更新筛选进度条"""
        self.filter_progress_bar.setValue(percent)
        QApplication.processEvents()
    
    def filter_processing_done(self, success, message):
        """筛选处理完成回调"""
        # 隐藏进度条
        self.filter_progress_bar.setVisible(False)
        
        # 更新日志
        if success:
            self.filter_log_message("====== 筛选完成 ======", "highlight")
            self.filter_log_message(message, "success")
            
            # 汇报各对象的筛选截断情况及具体原因
            if hasattr(self.filter_thread, 'object_filter_results') and self.filter_thread.object_filter_results:
                # 分组统计各类结果
                result_counts = {'passed': 0, 'truncated': 0, 'filtered': 0}
                for obj_id, result in self.filter_thread.object_filter_results.items():
                    if result['result'] in result_counts:
                        result_counts[result['result']] += 1
                
                self.filter_log_message("", "info")  # 添加空行
                self.filter_log_message("===== 对象筛选结果汇总 =====", "highlight")
                self.filter_log_message(f"总对象数: {self.filter_thread.total_objects}", "info")
                # 修改通过筛选的对象数量，包括完全通过的对象和部分截断的对象
                passed_total = result_counts['passed'] + result_counts['truncated']
                self.filter_log_message(f"通过筛选: {passed_total} 个对象 (完全通过: {result_counts['passed']}, 部分截断: {result_counts['truncated']})", "success")
                self.filter_log_message(f"完全过滤: {result_counts['filtered']} 个对象", "error")
                self.filter_log_message("", "info")  # 添加空行
                
                # 按对象ID排序
                sorted_obj_ids = sorted(self.filter_thread.object_filter_results.keys())
                
                # 显示通过筛选的对象
                if result_counts['passed'] > 0:
                    self.filter_log_message("【完全通过筛选的对象】", "success")
                    for obj_id in sorted_obj_ids:
                        result = self.filter_thread.object_filter_results[obj_id]
                        if result['result'] == 'passed':
                            frames_info = f"{result['frames']}/{result['original_frames']} 帧"
                            self.filter_log_message(f"对象 {obj_id}: {frames_info} - {result['reason']}", "success")
                    self.filter_log_message("", "info")  # 添加空行
                
                # 显示部分截断的对象
                if result_counts['truncated'] > 0:
                    self.filter_log_message("【部分截断的对象】", "warning")
                    for obj_id in sorted_obj_ids:
                        result = self.filter_thread.object_filter_results[obj_id]
                        if result['result'] == 'truncated':
                            truncated_at = result.get('truncated_at', 0)
                            original_frames = result.get('original_frames', 0)
                            valid_frames = truncated_at + 1
                            frames_percent = int((valid_frames / original_frames) * 100) if original_frames > 0 else 0
                            frames_info = f"保留 {valid_frames}/{original_frames} 帧 ({frames_percent}%)"
                            self.filter_log_message(f"对象 {obj_id}: {frames_info} - {result['reason']}", "warning")
                    self.filter_log_message("", "info")  # 添加空行
                
                # 显示完全过滤的对象
                if result_counts['filtered'] > 0:
                    self.filter_log_message("【完全过滤的对象】", "error")
                    for obj_id in sorted_obj_ids:
                        result = self.filter_thread.object_filter_results[obj_id]
                        if result['result'] == 'filtered':
                            self.filter_log_message(f"对象 {obj_id}: {result['reason']}", "error")
                    self.filter_log_message("", "info")  # 添加空行
            
            # 启用播放按钮和保存按钮
            self.filter_play_pause_btn.setEnabled(True)
            self.save_filter_btn.setEnabled(True)
            
            # 初始化筛选视频播放线程
            self.start_filter_video_playback()
            
            # 重新启用筛选按钮，使用户可以修改参数后再次执行
            self.apply_filter_btn.setEnabled(True)
        else:
            self.filter_log_message("====== 筛选失败 ======", "highlight")
            self.filter_log_message(f"筛选失败: {message}", "error")
            
            # 重新启用筛选按钮
            self.apply_filter_btn.setEnabled(True)

    def keyPressEvent(self, event):
        """处理键盘按键事件"""
        # 根据当前激活的标签页来判断要控制哪个视频
        current_tab = self.tab_widget.currentIndex()
        
        # 第一个标签页（参数设置与标注）- 控制原始视频
        if current_tab == 0 and self.video_thread and self.video_thread.isRunning():
            # 空格键 - 播放/暂停
            if event.key() == Qt.Key_Space:
                self.toggle_play_pause()
                event.accept()
                return
            # F键 - 下一帧
            elif event.key() == Qt.Key_F:
                self.next_frame(self.video_thread, self.frame_slider)
                event.accept()
                return
            # D键 - 上一帧
            elif event.key() == Qt.Key_D:
                self.previous_frame(self.video_thread, self.frame_slider)
                event.accept()
                return
        
        # 第二个标签页（结果预览）- 控制结果视频
        elif current_tab == 1 and self.result_video_thread and self.result_video_thread.isRunning():
            # 空格键 - 播放/暂停
            if event.key() == Qt.Key_Space:
                self.toggle_result_play_pause()
                event.accept()
                return
            # F键 - 下一帧
            elif event.key() == Qt.Key_F:
                self.next_frame(self.result_video_thread, self.result_slider)
                event.accept()
                return
            # D键 - 上一帧
            elif event.key() == Qt.Key_D:
                self.previous_frame(self.result_video_thread, self.result_slider)
                event.accept()
                return
        
        # 第三个标签页（筛选过滤）- 控制筛选视频
        elif current_tab == 2 and hasattr(self, 'filter_video_thread') and self.filter_video_thread.isRunning():
            # 空格键 - 播放/暂停
            if event.key() == Qt.Key_Space:
                self.toggle_filter_play_pause()
                event.accept()
                return
            # F键 - 下一帧
            elif event.key() == Qt.Key_F:
                self.next_frame(self.filter_video_thread, self.filter_slider)
                event.accept()
                return
            # D键 - 上一帧
            elif event.key() == Qt.Key_D:
                self.previous_frame(self.filter_video_thread, self.filter_slider)
                event.accept()
                return
        
        # 调用父类的keyPressEvent以确保其他按键事件正常处理
        super().keyPressEvent(event)
    
    def next_frame(self, video_thread, slider):
        """播放下一帧"""
        if not video_thread or not video_thread.isRunning():
            return
        
        # 确保视频是暂停状态
        mutex = QMutex()
        mutex.lock()
        is_paused = video_thread.paused
        mutex.unlock()
        
        if not is_paused:
            # 如果正在播放，先暂停
            video_thread.toggle_pause()
            # 更新对应按钮的状态（根据video_thread类型）
            if video_thread is self.video_thread:
                self.play_pause_btn.setText("播放")
                self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            elif video_thread is self.result_video_thread:
                self.result_play_pause_btn.setText("播放")
                self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            elif hasattr(self, 'filter_video_thread') and video_thread is self.filter_video_thread:
                self.filter_play_pause_btn.setText("播放")
                self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        
        # 计算下一帧的索引
        current_idx = slider.value()
        next_idx = min(current_idx + 1, slider.maximum())
        
        # 设置新的帧索引
        if next_idx != current_idx:
            slider.setValue(next_idx)  # 这会通过滑块的valueChanged信号间接调用set_frame_index
    
    def previous_frame(self, video_thread, slider):
        """播放上一帧"""
        if not video_thread or not video_thread.isRunning():
            return
        
        # 确保视频是暂停状态
        mutex = QMutex()
        mutex.lock()
        is_paused = video_thread.paused
        mutex.unlock()
        
        if not is_paused:
            # 如果正在播放，先暂停
            video_thread.toggle_pause()
            # 更新对应按钮的状态（根据video_thread类型）
            if video_thread is self.video_thread:
                self.play_pause_btn.setText("播放")
                self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            elif video_thread is self.result_video_thread:
                self.result_play_pause_btn.setText("播放")
                self.result_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            elif hasattr(self, 'filter_video_thread') and video_thread is self.filter_video_thread:
                self.filter_play_pause_btn.setText("播放")
                self.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        
        # 计算上一帧的索引
        current_idx = slider.value()
        prev_idx = max(current_idx - 1, 0)
        
        # 设置新的帧索引
        if prev_idx != current_idx:
            slider.setValue(prev_idx)  # 这会通过滑块的valueChanged信号间接调用set_frame_index

    # 添加这个方法来处理标签页切换
    def on_tab_changed(self, index):
        """当切换标签页时让相应的视频控件获得焦点"""
        # 第一个标签页 - 视频标注
        if index == 0 and hasattr(self, 'video_label'):
            self.video_label.setFocus()
        # 第二个标签页 - 结果预览
        elif index == 1 and hasattr(self, 'result_label'):
            self.result_label.setFocus()
        # 第三个标签页 - 筛选过滤
        elif index == 2 and hasattr(self, 'filter_video_label'):
            self.filter_video_label.setFocus()

    # 在MicroTrackerApp类中添加一个辅助方法，用于创建带有微米符号的标签
    def create_unit_label(self, unit_text):
        """创建统一样式的单位标签，特别处理带有微米符号的单位"""
        label = QLabel(unit_text)
        label.setStyleSheet("""
            font-family: "Times New Roman", Arial, sans-serif;
            font-size: 10pt;
        """)
        return label

def main():
    # 启用高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格，更现代的外观
    
    # Suppress all warnings
    warnings.filterwarnings("ignore")

    # 设置应用程序图标
    app_icon = QIcon("icons/icon.png") if os.path.exists("icons/icon.png") else QIcon.fromTheme("video-x-generic")
    app.setWindowIcon(app_icon)
    
    # 创建并显示主窗口
    window = MicroTrackerApp()
    window.show()
    
    # 使用定时器确保GUI完全初始化后再显示欢迎消息
    QTimer.singleShot(100, lambda: window.log_message("欢迎使用 Micro Tracker - 显微视频目标分割和追踪工具", "highlight"))
    QTimer.singleShot(200, lambda: window.log_message("请选择一个视频文件开始...", "info"))
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 