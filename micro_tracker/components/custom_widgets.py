from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QPushButton, QProgressBar, QLineEdit, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, pyqtProperty, Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
import math

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


# RippleButton - 带Material Design波纹效果的按钮
class RippleButton(QPushButton):
    """带波纹效果的按钮"""
    
    def __init__(self, text="", tooltip="", parent=None):
        super().__init__(text, parent)
        if tooltip:
            self.setToolTip(tooltip)
        
        # 波纹动画属性
        self._ripple_radius = 0
        self._ripple_opacity = 0
        self._ripple_pos = QPoint()
        self._ripple_animation = None
        self._opacity_animation = None
    
    @pyqtProperty(float)
    def ripple_radius(self):
        return self._ripple_radius
    
    @ripple_radius.setter
    def ripple_radius(self, value):
        self._ripple_radius = value
        self.update()
    
    @pyqtProperty(float)
    def ripple_opacity(self):
        return self._ripple_opacity
    
    @ripple_opacity.setter
    def ripple_opacity(self, value):
        self._ripple_opacity = value
        self.update()
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._ripple_pos = event.pos()
        self._create_ripple_animation()
    
    def _create_ripple_animation(self):
        """创建波纹扩散动画"""
        # 计算最大半径（按钮对角线长度）
        max_radius = math.sqrt(self.width()**2 + self.height()**2)
        
        # 停止之前的动画
        if self._ripple_animation:
            self._ripple_animation.stop()
        if self._opacity_animation:
            self._opacity_animation.stop()
        
        # 半径动画
        self._ripple_animation = QPropertyAnimation(self, b"ripple_radius")
        self._ripple_animation.setDuration(600)
        self._ripple_animation.setStartValue(0)
        self._ripple_animation.setEndValue(max_radius)
        self._ripple_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 透明度动画
        self._opacity_animation = QPropertyAnimation(self, b"ripple_opacity")
        self._opacity_animation.setDuration(600)
        self._opacity_animation.setStartValue(0.4)
        self._opacity_animation.setEndValue(0.0)
        self._opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 启动动画
        self._ripple_animation.start()
        self._opacity_animation.start()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        # 绘制波纹效果
        if self._ripple_opacity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 设置波纹颜色（白色，透明度根据动画变化）
            color = QColor(255, 255, 255, int(self._ripple_opacity * 255))
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color))
            
            # 绘制圆形波纹
            painter.drawEllipse(self._ripple_pos, int(self._ripple_radius), int(self._ripple_radius))
            painter.end()


# AnimatedProgressBar - 带水平波浪动画的进度条
class AnimatedProgressBar(QProgressBar):
    """带波浪滚动效果的进度条"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 强制设置文字居中对齐
        self.setAlignment(Qt.AlignCenter)
        
        # 波浪动画属性
        self._wave_offset = 0
        self._wave_animation = None
        self._is_animating = False
        
        # 监听进度变化
        self.valueChanged.connect(self._on_value_changed)
    
    @pyqtProperty(float)
    def wave_offset(self):
        return self._wave_offset
    
    @wave_offset.setter
    def wave_offset(self, value):
        self._wave_offset = value % 40  # 波长为40px，循环
        self.update()
    
    def _on_value_changed(self, value):
        """进度变化时启动或停止动画"""
        if value > 0 and value < 100:
            if not self._is_animating:
                self._start_animation()
        else:
            if self._is_animating:
                self._stop_animation()
    
    def _start_animation(self):
        """启动水平滚动动画"""
        if not self._wave_animation:
            self._wave_animation = QPropertyAnimation(self, b"wave_offset")
            self._wave_animation.setDuration(1500)  # 1.5秒/循环
            self._wave_animation.setStartValue(0)
            self._wave_animation.setEndValue(40)  # 波长
            self._wave_animation.setLoopCount(-1)  # 无限循环
            self._wave_animation.setEasingCurve(QEasingCurve.Linear)
        
        if not self._is_animating:
            self._wave_animation.start()
            self._is_animating = True
    
    def _stop_animation(self):
        """停止动画"""
        if self._wave_animation and self._is_animating:
            self._wave_animation.stop()
            self._is_animating = False
            self._wave_offset = 0
            self.update()
    
    def paintEvent(self, event):
        """绘制带波浪渐变的进度条"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        bg_rect = self.rect()
        painter.setBrush(QBrush(QColor("#f5f5f5")))
        painter.setPen(QPen(QColor("#e0e0e0")))
        painter.drawRoundedRect(bg_rect, 6, 6)
        
        # 计算进度条宽度
        progress = self.value() - self.minimum()
        total = self.maximum() - self.minimum()
        if total > 0:
            progress_width = int((progress / total) * (self.width() - 2))
            
            if progress_width > 0:
                # 创建波浪渐变
                gradient = QLinearGradient(self._wave_offset, 0, self._wave_offset + 40, 0)
                gradient.setSpread(QLinearGradient.RepeatSpread)
                
                # 渐变定义：浅绿→深绿→浅绿
                gradient.setColorAt(0.0, QColor("#66BB6A"))  # 浅绿
                gradient.setColorAt(0.5, QColor("#4CAF50"))  # 深绿
                gradient.setColorAt(1.0, QColor("#66BB6A"))  # 浅绿
                
                # 绘制进度填充
                progress_rect = self.rect().adjusted(1, 1, -self.width() + progress_width + 1, -1)
                painter.setBrush(QBrush(gradient))
                painter.setPen(QPen(QColor("#4CAF50"), 0))
                painter.drawRoundedRect(progress_rect, 5, 5)
        
        # 绘制文字（强制居中对齐）
        if self.isTextVisible():
            painter.setPen(QPen(QColor("#424242")))
            painter.drawText(self.rect(), Qt.AlignCenter, self.text())
        
        painter.end()


# FocusGlowLineEdit - 带焦点发光效果的输入框
class FocusGlowLineEdit(QLineEdit):
    """带焦点发光效果的输入框"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        # 创建阴影效果（但初始不应用）
        self._glow_effect = QGraphicsDropShadowEffect()
        self._glow_effect.setColor(QColor("#0D47A1"))  # 学术深蓝
        self._glow_effect.setBlurRadius(6)
        self._glow_effect.setOffset(0, 0)
        self._glow_effect.setEnabled(False)
        self.setGraphicsEffect(self._glow_effect)
    
    def focusInEvent(self, event):
        """获得焦点时应用发光效果"""
        super().focusInEvent(event)
        if self._glow_effect:
            self._glow_effect.setEnabled(True)
    
    def focusOutEvent(self, event):
        """失去焦点时移除发光效果"""
        super().focusOutEvent(event)
        if self._glow_effect:
            self._glow_effect.setEnabled(False)

