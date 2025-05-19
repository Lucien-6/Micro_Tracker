import sys
import warnings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import os

from micro_tracker.ui.main_window import MainWindow

def main():
    """程序入口点"""
    # 启用高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格，更现代的外观
    
    # 忽略所有警告
    warnings.filterwarnings("ignore")

    # 设置应用程序图标
    app_icon = QIcon("icons/icon.png") if os.path.exists("icons/icon.png") else QIcon.fromTheme("video-x-generic")
    app.setWindowIcon(app_icon)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 使用定时器确保GUI完全初始化后再显示欢迎消息
    QTimer.singleShot(100, lambda: window.log_message("欢迎使用 Micro Tracker - 显微视频目标分割和追踪工具", "highlight"))
    QTimer.singleShot(200, lambda: window.log_message("请选择一个视频文件开始...", "info"))
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 