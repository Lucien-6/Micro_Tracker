from PyQt5.QtWidgets import QWidget

class BaseTab(QWidget):
    """
    基础标签页类，所有标签页继承此类
    提供共同的方法和属性
    """
    
    def __init__(self, main_window):
        """
        初始化标签页
        
        Args:
            main_window: 主窗口的引用，用于访问共享状态和方法
        """
        super().__init__()
        self.main_window = main_window
        
    def init_ui(self):
        """初始化UI组件，子类必须实现此方法"""
        raise NotImplementedError("子类必须实现init_ui方法")
    
    def log_message(self, message, msg_type="info"):
        """
        调用主窗口的日志记录方法
        
        Args:
            message: 要记录的消息
            msg_type: 消息类型("info", "warning", "error", "success", "highlight")
        """
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(message, msg_type) 