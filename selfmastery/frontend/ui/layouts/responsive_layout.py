"""
响应式布局管理器
"""
from PyQt6.QtWidgets import QLayout, QLayoutItem, QWidget, QSizePolicy
from PyQt6.QtCore import QRect, QSize, Qt


class ResponsiveLayout(QLayout):
    """响应式布局管理器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_list = []
        self.min_width = 200
        self.spacing_x = 10
        self.spacing_y = 10
        
    def addItem(self, item):
        """添加布局项"""
        self.item_list.append(item)
        
    def count(self):
        """返回布局项数量"""
        return len(self.item_list)
        
    def itemAt(self, index):
        """获取指定索引的布局项"""
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
        
    def takeAt(self, index):
        """移除并返回指定索引的布局项"""
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
        
    def expandingDirections(self):
        """返回扩展方向"""
        return Qt.Orientation.Horizontal | Qt.Orientation.Vertical
        
    def hasHeightForWidth(self):
        """是否支持高度随宽度变化"""
        return True
        
    def heightForWidth(self, width):
        """根据宽度计算高度"""
        height = self.do_layout(QRect(0, 0, width, 0), True)
        return height
        
    def setGeometry(self, rect):
        """设置几何形状"""
        super().setGeometry(rect)
        self.do_layout(rect, False)
        
    def sizeHint(self):
        """返回建议大小"""
        return self.minimumSize()
        
    def minimumSize(self):
        """返回最小大小"""
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size
        
    def do_layout(self, rect, test_only):
        """执行布局计算"""
        x = rect.x()
        y = rect.y()
        line_height = 0
        
        for item in self.item_list:
            widget = item.widget()
            if not widget:
                continue
                
            space_x = self.spacing_x
            space_y = self.spacing_y
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
                
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
                
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
            
        return y + line_height - rect.y()
        
    def set_min_width(self, width):
        """设置最小宽度"""
        self.min_width = width
        
    def set_spacing(self, x, y):
        """设置间距"""
        self.spacing_x = x
        self.spacing_y = y