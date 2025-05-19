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
    selection-color: #000000;  /* 设置选中项文本颜色为黑色 */
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