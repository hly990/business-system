"""
主题管理器
"""
import os
from typing import Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor


class ThemeManager(QObject):
    """主题管理器"""
    
    theme_changed = pyqtSignal(str)  # 主题变更信号
    
    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.themes = {
            "light": self.get_light_theme(),
            "dark": self.get_dark_theme()
        }
        
    def get_light_theme(self) -> Dict[str, Any]:
        """获取浅色主题"""
        return {
            "name": "light",
            "display_name": "浅色主题",
            "colors": {
                "primary": "#1976d2",
                "primary_dark": "#1565c0",
                "primary_light": "#42a5f5",
                "secondary": "#424242",
                "secondary_dark": "#212121",
                "secondary_light": "#616161",
                "background": "#ffffff",
                "surface": "#f5f5f5",
                "error": "#f44336",
                "warning": "#ff9800",
                "success": "#4caf50",
                "info": "#2196f3",
                "text_primary": "#212121",
                "text_secondary": "#757575",
                "text_disabled": "#bdbdbd",
                "divider": "#e0e0e0",
                "border": "#e0e0e0",
                "hover": "#f0f0f0",
                "selected": "#e3f2fd",
                "focus": "#1976d2"
            },
            "stylesheet": self.get_light_stylesheet()
        }
        
    def get_dark_theme(self) -> Dict[str, Any]:
        """获取深色主题"""
        return {
            "name": "dark",
            "display_name": "深色主题",
            "colors": {
                "primary": "#2196f3",
                "primary_dark": "#1976d2",
                "primary_light": "#64b5f6",
                "secondary": "#424242",
                "secondary_dark": "#212121",
                "secondary_light": "#616161",
                "background": "#121212",
                "surface": "#1e1e1e",
                "error": "#cf6679",
                "warning": "#ffb74d",
                "success": "#81c784",
                "info": "#64b5f6",
                "text_primary": "#ffffff",
                "text_secondary": "#b0b0b0",
                "text_disabled": "#666666",
                "divider": "#333333",
                "border": "#333333",
                "hover": "#2a2a2a",
                "selected": "#1e3a5f",
                "focus": "#2196f3"
            },
            "stylesheet": self.get_dark_stylesheet()
        }
        
    def get_light_stylesheet(self) -> str:
        """获取浅色主题样式表"""
        return """
        /* 主窗口 */
        QMainWindow {
            background-color: #ffffff;
            color: #212121;
        }
        
        /* 菜单栏 */
        QMenuBar {
            background-color: #f5f5f5;
            border-bottom: 1px solid #e0e0e0;
            padding: 4px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }
        
        QMenuBar::item:pressed {
            background-color: #d0d0d0;
        }
        
        /* 菜单 */
        QMenu {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        QMenu::separator {
            height: 1px;
            background-color: #e0e0e0;
            margin: 4px 8px;
        }
        
        /* 工具栏 */
        QToolBar {
            background-color: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 4px;
            spacing: 4px;
        }
        
        QToolBar::separator {
            width: 1px;
            background-color: #e0e0e0;
            margin: 4px 2px;
        }
        
        /* 状态栏 */
        QStatusBar {
            background-color: #f5f5f5;
            border-top: 1px solid #e0e0e0;
            padding: 4px;
        }
        
        /* 按钮 */
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
            color: #212121;
        }
        
        QPushButton:hover {
            background-color: #e0e0e0;
            border-color: #999999;
        }
        
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        
        QPushButton:disabled {
            background-color: #f5f5f5;
            color: #bdbdbd;
            border-color: #e0e0e0;
        }
        
        /* 输入框 */
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
            color: #212121;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #1976d2;
        }
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
            background-color: #f5f5f5;
            color: #bdbdbd;
        }
        
        /* 下拉框 */
        QComboBox {
            background-color: #ffffff;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: #212121;
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
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            selection-background-color: #e3f2fd;
            selection-color: #1976d2;
        }
        
        /* 列表和树 */
        QListWidget, QTreeWidget {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            alternate-background-color: #f9f9f9;
        }
        
        QListWidget::item, QTreeWidget::item {
            padding: 4px;
            border: none;
        }
        
        QListWidget::item:selected, QTreeWidget::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        QListWidget::item:hover, QTreeWidget::item:hover {
            background-color: #f0f0f0;
        }
        
        /* 表格 */
        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            gridline-color: #e0e0e0;
            alternate-background-color: #f9f9f9;
        }
        
        QTableWidget::item {
            padding: 8px;
            border: none;
        }
        
        QTableWidget::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        QHeaderView::section {
            background-color: #f5f5f5;
            border: 1px solid #e0e0e0;
            padding: 8px;
            font-weight: bold;
        }
        
        /* 标签页 */
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 2px solid #1976d2;
        }
        
        QTabBar::tab:hover {
            background-color: #eeeeee;
        }
        
        /* 滚动条 */
        QScrollBar:vertical {
            background-color: #f5f5f5;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #cccccc;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #999999;
        }
        
        QScrollBar:horizontal {
            background-color: #f5f5f5;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #cccccc;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #999999;
        }
        
        /* 分割器 */
        QSplitter::handle {
            background-color: #e0e0e0;
        }
        
        QSplitter::handle:horizontal {
            width: 2px;
        }
        
        QSplitter::handle:vertical {
            height: 2px;
        }
        
        /* 停靠窗口 */
        QDockWidget {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
        }
        
        QDockWidget::title {
            background-color: #f5f5f5;
            border-bottom: 1px solid #e0e0e0;
            padding: 8px;
            font-weight: bold;
        }
        
        /* 进度条 */
        QProgressBar {
            background-color: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #1976d2;
            border-radius: 6px;
        }
        
        /* 滑块 */
        QSlider::groove:horizontal {
            background-color: #e0e0e0;
            height: 4px;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background-color: #1976d2;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #1565c0;
        }
        """
        
    def get_dark_stylesheet(self) -> str:
        """获取深色主题样式表"""
        return """
        /* 主窗口 */
        QMainWindow {
            background-color: #121212;
            color: #ffffff;
        }
        
        /* 菜单栏 */
        QMenuBar {
            background-color: #1e1e1e;
            border-bottom: 1px solid #333333;
            padding: 4px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
            color: #ffffff;
        }
        
        QMenuBar::item:selected {
            background-color: #333333;
        }
        
        QMenuBar::item:pressed {
            background-color: #404040;
        }
        
        /* 菜单 */
        QMenu {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 6px;
            padding: 4px;
            color: #ffffff;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #1e3a5f;
            color: #64b5f6;
        }
        
        QMenu::separator {
            height: 1px;
            background-color: #333333;
            margin: 4px 8px;
        }
        
        /* 工具栏 */
        QToolBar {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 6px;
            padding: 4px;
            spacing: 4px;
        }
        
        QToolBar::separator {
            width: 1px;
            background-color: #333333;
            margin: 4px 2px;
        }
        
        /* 状态栏 */
        QStatusBar {
            background-color: #1e1e1e;
            border-top: 1px solid #333333;
            padding: 4px;
            color: #ffffff;
        }
        
        /* 按钮 */
        QPushButton {
            background-color: #2a2a2a;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background-color: #404040;
            border-color: #777777;
        }
        
        QPushButton:pressed {
            background-color: #1a1a1a;
        }
        
        QPushButton:disabled {
            background-color: #1a1a1a;
            color: #666666;
            border-color: #333333;
        }
        
        /* 输入框 */
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #1e1e1e;
            border: 2px solid #333333;
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
            color: #ffffff;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #2196f3;
        }
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
            background-color: #1a1a1a;
            color: #666666;
        }
        
        /* 下拉框 */
        QComboBox {
            background-color: #1e1e1e;
            border: 2px solid #333333;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: #ffffff;
        }
        
        QComboBox:focus {
            border-color: #2196f3;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: url(:/icons/arrow_down_white.png);
            width: 12px;
            height: 12px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 6px;
            selection-background-color: #1e3a5f;
            selection-color: #64b5f6;
            color: #ffffff;
        }
        
        /* 列表和树 */
        QListWidget, QTreeWidget {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 6px;
            alternate-background-color: #252525;
            color: #ffffff;
        }
        
        QListWidget::item, QTreeWidget::item {
            padding: 4px;
            border: none;
        }
        
        QListWidget::item:selected, QTreeWidget::item:selected {
            background-color: #1e3a5f;
            color: #64b5f6;
        }
        
        QListWidget::item:hover, QTreeWidget::item:hover {
            background-color: #2a2a2a;
        }
        
        /* 表格 */
        QTableWidget {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 6px;
            gridline-color: #333333;
            alternate-background-color: #252525;
            color: #ffffff;
        }
        
        QTableWidget::item {
            padding: 8px;
            border: none;
        }
        
        QTableWidget::item:selected {
            background-color: #1e3a5f;
            color: #64b5f6;
        }
        
        QHeaderView::section {
            background-color: #2a2a2a;
            border: 1px solid #333333;
            padding: 8px;
            font-weight: bold;
            color: #ffffff;
        }
        
        /* 标签页 */
        QTabWidget::pane {
            border: 1px solid #333333;
            border-radius: 6px;
            background-color: #1e1e1e;
        }
        
        QTabBar::tab {
            background-color: #2a2a2a;
            border: 1px solid #333333;
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            margin-right: 2px;
            color: #ffffff;
        }
        
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            border-bottom: 2px solid #2196f3;
        }
        
        QTabBar::tab:hover {
            background-color: #404040;
        }
        
        /* 滚动条 */
        QScrollBar:vertical {
            background-color: #2a2a2a;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #777777;
        }
        
        QScrollBar:horizontal {
            background-color: #2a2a2a;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555555;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #777777;
        }
        
        /* 分割器 */
        QSplitter::handle {
            background-color: #333333;
        }
        
        QSplitter::handle:horizontal {
            width: 2px;
        }
        
        QSplitter::handle:vertical {
            height: 2px;
        }
        
        /* 停靠窗口 */
        QDockWidget {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 6px;
            color: #ffffff;
        }
        
        QDockWidget::title {
            background-color: #2a2a2a;
            border-bottom: 1px solid #333333;
            padding: 8px;
            font-weight: bold;
        }
        
        /* 进度条 */
        QProgressBar {
            background-color: #2a2a2a;
            border: 1px solid #333333;
            border-radius: 6px;
            text-align: center;
            color: #ffffff;
        }
        
        QProgressBar::chunk {
            background-color: #2196f3;
            border-radius: 6px;
        }
        
        /* 滑块 */
        QSlider::groove:horizontal {
            background-color: #333333;
            height: 4px;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background-color: #2196f3;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #1976d2;
        }
        """
        
    def apply_theme(self, widget, theme_name: str):
        """应用主题到指定组件"""
        if theme_name not in self.themes:
            theme_name = "light"
            
        theme = self.themes[theme_name]
        self.current_theme = theme_name
        
        # 应用样式表
        widget.setStyleSheet(theme["stylesheet"])
        
        # 发出主题变更信号
        self.theme_changed.emit(theme_name)
        
    def get_current_theme(self) -> str:
        """获取当前主题名称"""
        return self.current_theme
        
    def get_theme_color(self, color_name: str) -> str:
        """获取当前主题的颜色值"""
        theme = self.themes.get(self.current_theme, self.themes["light"])
        return theme["colors"].get(color_name, "#000000")
        
    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题列表"""
        return {name: theme["display_name"] for name, theme in self.themes.items()}
        
    def register_theme(self, name: str, theme_data: Dict[str, Any]):
        """注册自定义主题"""
        self.themes[name] = theme_data
        
    def create_palette(self, theme_name: str) -> QPalette:
        """创建主题调色板"""
        if theme_name not in self.themes:
            theme_name = "light"
            
        theme = self.themes[theme_name]
        colors = theme["colors"]
        
        palette = QPalette()
        
        # 设置基础颜色
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["hover"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["selected"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["primary"]))
        
        return palette


# 单例模式的主题管理器实例
_theme_manager_instance = None

def get_theme_manager() -> ThemeManager:
    """获取主题管理器单例"""
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance