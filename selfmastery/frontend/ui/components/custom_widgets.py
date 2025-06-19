"""
自定义UI组件
"""
from PyQt6.QtWidgets import (
    QPushButton, QLineEdit, QTextEdit, QComboBox, 
    QSpinBox, QDateEdit, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QPalette, QIcon


class CustomButton(QPushButton):
    """自定义按钮"""
    
    def __init__(self, text="", icon=None, button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        
        if icon:
            self.setIcon(QIcon(icon))
            
        self.setup_style()
        
    def setup_style(self):
        """设置样式"""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
            QPushButton:disabled {
                opacity: 0.6;
            }
        """
        
        if self.button_type == "primary":
            style = base_style + """
                QPushButton {
                    background-color: #1976d2;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0d47a1;
                }
            """
        elif self.button_type == "secondary":
            style = base_style + """
                QPushButton {
                    background-color: #f5f5f5;
                    color: #333;
                    border: 1px solid #ddd;
                }
                QPushButton:hover {
                    background-color: #eeeeee;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
            """
        elif self.button_type == "danger":
            style = base_style + """
                QPushButton {
                    background-color: #d32f2f;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #c62828;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
            """
        else:
            style = base_style
            
        self.setStyleSheet(style)


class CustomLineEdit(QLineEdit):
    """自定义单行输入框"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setup_style()
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1976d2;
                outline: none;
            }
            QLineEdit:disabled {
                background-color: #f5f5f5;
                color: #999;
            }
        """)


class CustomTextEdit(QTextEdit):
    """自定义多行文本编辑器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QTextEdit:focus {
                border-color: #1976d2;
            }
            QTextEdit:disabled {
                background-color: #f5f5f5;
                color: #999;
            }
        """)


class CustomComboBox(QComboBox):
    """自定义下拉框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #1976d2;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(:/icons/arrow_down.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #1976d2;
                selection-color: white;
            }
        """)


class CustomSpinBox(QSpinBox):
    """自定义数字输入框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QSpinBox {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #1976d2;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                width: 20px;
                background-color: transparent;
            }
            QSpinBox::up-arrow {
                image: url(:/icons/arrow_up.png);
                width: 10px;
                height: 10px;
            }
            QSpinBox::down-arrow {
                image: url(:/icons/arrow_down.png);
                width: 10px;
                height: 10px;
            }
        """)


class CustomDateEdit(QDateEdit):
    """自定义日期选择器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDate(QDate.currentDate())
        self.setCalendarPopup(True)
        self.setup_style()
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QDateEdit {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QDateEdit:focus {
                border-color: #1976d2;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::down-arrow {
                image: url(:/icons/calendar.png);
                width: 12px;
                height: 12px;
            }
        """)


class StatusIndicator(QLabel):
    """状态指示器"""
    
    def __init__(self, status="normal", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(12, 12)
        self.update_status(status)
        
    def update_status(self, status):
        """更新状态"""
        self.status = status
        colors = {
            "normal": "#4caf50",    # 绿色
            "warning": "#ff9800",   # 橙色
            "error": "#f44336",     # 红色
            "info": "#2196f3",      # 蓝色
            "inactive": "#9e9e9e"   # 灰色
        }
        
        color = colors.get(status, "#9e9e9e")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)


class SeparatorLine(QFrame):
    """分隔线"""
    
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        if orientation == Qt.Orientation.Horizontal:
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFixedHeight(1)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
            self.setFixedWidth(1)
            
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("""
            QFrame {
                color: #e0e0e0;
                background-color: #e0e0e0;
            }
        """)


class IconLabel(QLabel):
    """图标标签"""
    
    clicked = pyqtSignal()
    
    def __init__(self, icon_path="", text="", parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.text_content = text
        
        if icon_path:
            self.setPixmap(QIcon(icon_path).pixmap(16, 16))
        if text:
            self.setText(text)
            
        self.setStyleSheet("""
            QLabel {
                padding: 4px;
                border-radius: 4px;
            }
            QLabel:hover {
                background-color: #f0f0f0;
            }
        """)
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class LoadingSpinner(QLabel):
    """加载动画"""
    
    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 这里可以添加旋转动画的实现
        self.setText("⟳")
        self.setStyleSheet(f"""
            QLabel {{
                font-size: {size//2}px;
                color: #1976d2;
            }}
        """)