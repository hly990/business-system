"""
图形元素组件
"""
import math
from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsTextItem, QGraphicsPathItem, QStyleOptionGraphicsItem,
    QWidget, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QObject
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPainter, QFont, QPainterPath,
    QLinearGradient, QRadialGradient, QPolygonF
)


class BaseGraphicsItem(QGraphicsRectItem):
    """基础图形项目类"""
    
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data = data or {}
        
        # 设置基本属性
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        
        # 样式设置
        self.normal_pen = QPen(QColor("#e0e0e0"), 2)
        self.selected_pen = QPen(QColor("#1976d2"), 3)
        self.hover_pen = QPen(QColor("#42a5f5"), 2)
        self.connection_pen = QPen(QColor("#4caf50"), 3)
        
        self.normal_brush = QBrush(QColor("#ffffff"))
        self.selected_brush = QBrush(QColor("#e3f2fd"))
        self.hover_brush = QBrush(QColor("#f5f5f5"))
        
        # 状态
        self.is_hovered = False
        self.is_connection_highlighted = False
        
        # 文本项目
        self.text_item = None
        self.create_text_item()
        
    def create_text_item(self):
        """创建文本项目"""
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setFont(QFont("Arial", 10))
        self.text_item.setDefaultTextColor(QColor("#333333"))
        self.update_text()
        
    def update_text(self):
        """更新文本内容"""
        if self.text_item:
            text = self.get_display_text()
            self.text_item.setPlainText(text)
            self.center_text()
            
    def get_display_text(self):
        """获取显示文本"""
        return self.data.get('name', '未命名')
        
    def center_text(self):
        """居中文本"""
        if self.text_item:
            text_rect = self.text_item.boundingRect()
            item_rect = self.rect()
            x = (item_rect.width() - text_rect.width()) / 2
            y = (item_rect.height() - text_rect.height()) / 2
            self.text_item.setPos(x, y)
            
    def paint(self, painter, option, widget):
        """绘制项目"""
        # 选择画笔和画刷
        if self.is_connection_highlighted:
            pen = self.connection_pen
            brush = self.selected_brush
        elif self.isSelected():
            pen = self.selected_pen
            brush = self.selected_brush
        elif self.is_hovered:
            pen = self.hover_pen
            brush = self.hover_brush
        else:
            pen = self.normal_pen
            brush = self.normal_brush
            
        painter.setPen(pen)
        painter.setBrush(brush)
        
        # 绘制基本形状
        self.draw_shape(painter, option, widget)
        
        # 绘制装饰
        self.draw_decorations(painter, option, widget)
        
    def draw_shape(self, painter, option, widget):
        """绘制基本形状（子类重写）"""
        painter.drawRect(self.rect())
        
    def draw_decorations(self, painter, option, widget):
        """绘制装饰（子类重写）"""
        pass
        
    def hoverEnterEvent(self, event):
        """鼠标悬停进入"""
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """鼠标悬停离开"""
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)
        
    def itemChange(self, change, value):
        """项目变化处理"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # 位置变化时更新连接线
            self.update_connections()
            
        return super().itemChange(change, value)
        
    def update_connections(self):
        """更新连接线（子类重写）"""
        pass
        
    def can_connect(self):
        """是否可以连接"""
        return True
        
    def can_delete(self):
        """是否可以删除"""
        return True
        
    def set_connection_highlight(self, highlighted):
        """设置连接高亮"""
        self.is_connection_highlighted = highlighted
        self.update()
        
    def get_connection_point(self, direction="center"):
        """获取连接点"""
        rect = self.rect()
        if direction == "top":
            return QPointF(rect.center().x(), rect.top())
        elif direction == "bottom":
            return QPointF(rect.center().x(), rect.bottom())
        elif direction == "left":
            return QPointF(rect.left(), rect.center().y())
        elif direction == "right":
            return QPointF(rect.right(), rect.center().y())
        else:
            return rect.center()


class SystemItem(BaseGraphicsItem):
    """业务系统图形项目"""
    
    def __init__(self, data=None, parent=None):
        super().__init__(data, parent)
        
        # 设置默认大小
        self.setRect(0, 0, 120, 80)
        
        # 系统特有样式
        self.system_color = QColor(data.get('color', '#1976d2') if data else '#1976d2')
        self.update_colors()
        
        # 子系统列表
        self.child_systems = []
        
    def update_colors(self):
        """更新颜色"""
        self.normal_brush = QBrush(self.system_color.lighter(180))
        self.selected_brush = QBrush(self.system_color.lighter(160))
        self.hover_brush = QBrush(self.system_color.lighter(170))
        
    def set_color(self, color):
        """设置系统颜色"""
        self.system_color = color
        self.update_colors()
        self.update()
        
    def draw_shape(self, painter, option, widget):
        """绘制系统形状"""
        rect = self.rect()
        
        # 创建渐变
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, self.system_color.lighter(120))
        gradient.setColorAt(1, self.system_color)
        
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(rect, 8, 8)
        
    def draw_decorations(self, painter, option, widget):
        """绘制装饰"""
        rect = self.rect()
        
        # 绘制系统图标
        icon_rect = QRectF(rect.right() - 20, rect.top() + 5, 15, 15)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawEllipse(icon_rect)
        
        # 绘制层级指示器
        level = self.data.get('level', 0)
        if level > 0:
            for i in range(level):
                indicator_rect = QRectF(rect.left() + 5 + i * 8, rect.top() + 5, 6, 6)
                painter.setPen(QPen(self.system_color.darker(150), 1))
                painter.setBrush(QBrush(self.system_color.darker(150)))
                painter.drawRect(indicator_rect)
                
    def get_display_text(self):
        """获取显示文本"""
        name = self.data.get('name', '未命名系统')
        # 如果名称太长，截断并添加省略号
        if len(name) > 12:
            return name[:12] + "..."
        return name
        
    def add_child_system(self, child_item):
        """添加子系统"""
        if child_item not in self.child_systems:
            self.child_systems.append(child_item)
            
    def remove_child_system(self, child_item):
        """移除子系统"""
        if child_item in self.child_systems:
            self.child_systems.remove(child_item)


class ProcessItem(BaseGraphicsItem):
    """业务流程图形项目"""
    
    def __init__(self, data=None, parent=None):
        super().__init__(data, parent)
        
        # 设置默认大小
        self.setRect(0, 0, 100, 60)
        
        # 流程状态颜色
        self.status_colors = {
            'draft': QColor('#9e9e9e'),
            'active': QColor('#4caf50'),
            'inactive': QColor('#ff9800'),
            'archived': QColor('#f44336')
        }
        
        self.status_color = self.status_colors.get(
            data.get('status', 'draft') if data else 'draft',
            self.status_colors['draft']
        )
        
        # 连接点
        self.input_connections = []
        self.output_connections = []
        
    def set_status_color(self, color):
        """设置状态颜色"""
        self.status_color = color
        self.update()
        
    def draw_shape(self, painter, option, widget):
        """绘制流程形状"""
        rect = self.rect()
        
        # 绘制圆角矩形
        painter.drawRoundedRect(rect, 6, 6)
        
        # 绘制状态指示条
        status_rect = QRectF(rect.left(), rect.bottom() - 4, rect.width(), 4)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.status_color))
        painter.drawRect(status_rect)
        
    def draw_decorations(self, painter, option, widget):
        """绘制装饰"""
        rect = self.rect()
        
        # 绘制优先级指示器
        priority = self.data.get('priority', 3)
        if priority <= 2:  # 高优先级
            star_rect = QRectF(rect.right() - 15, rect.top() + 3, 10, 10)
            painter.setPen(QPen(QColor('#ff5722'), 1))
            painter.setBrush(QBrush(QColor('#ff5722')))
            self.draw_star(painter, star_rect)
            
        # 绘制连接点
        self.draw_connection_points(painter)
        
    def draw_star(self, painter, rect):
        """绘制星形"""
        center = rect.center()
        radius = rect.width() / 2
        
        star = QPolygonF()
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                r = radius
            else:
                r = radius * 0.5
            x = center.x() + r * math.cos(angle - math.pi / 2)
            y = center.y() + r * math.sin(angle - math.pi / 2)
            star.append(QPointF(x, y))
            
        painter.drawPolygon(star)
        
    def draw_connection_points(self, painter):
        """绘制连接点"""
        if self.is_hovered or self.isSelected():
            rect = self.rect()
            point_radius = 3
            
            # 输入点（左侧）
            input_point = QPointF(rect.left(), rect.center().y())
            painter.setPen(QPen(QColor('#4caf50'), 2))
            painter.setBrush(QBrush(QColor('#4caf50')))
            painter.drawEllipse(input_point, point_radius, point_radius)
            
            # 输出点（右侧）
            output_point = QPointF(rect.right(), rect.center().y())
            painter.setPen(QPen(QColor('#2196f3'), 2))
            painter.setBrush(QBrush(QColor('#2196f3')))
            painter.drawEllipse(output_point, point_radius, point_radius)
            
    def get_display_text(self):
        """获取显示文本"""
        name = self.data.get('name', '未命名流程')
        # 如果名称太长，截断并添加省略号
        if len(name) > 10:
            return name[:10] + "..."
        return name
        
    def get_input_point(self):
        """获取输入连接点"""
        rect = self.rect()
        return self.mapToScene(QPointF(rect.left(), rect.center().y()))
        
    def get_output_point(self):
        """获取输出连接点"""
        rect = self.rect()
        return self.mapToScene(QPointF(rect.right(), rect.center().y()))
        
    def add_input_connection(self, connection):
        """添加输入连接"""
        if connection not in self.input_connections:
            self.input_connections.append(connection)
            
    def add_output_connection(self, connection):
        """添加输出连接"""
        if connection not in self.output_connections:
            self.output_connections.append(connection)
            
    def remove_connection(self, connection):
        """移除连接"""
        if connection in self.input_connections:
            self.input_connections.remove(connection)
        if connection in self.output_connections:
            self.output_connections.remove(connection)
            
    def update_connections(self):
        """更新连接线"""
        for connection in self.input_connections + self.output_connections:
            connection.update_path()


class ConnectionItem(QGraphicsPathItem):
    """连接线图形项目"""
    
    def __init__(self, from_item, to_item, data=None, parent=None):
        super().__init__(parent)
        
        self.from_item = from_item
        self.to_item = to_item
        self.data = data or {}
        
        # 设置基本属性
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # 样式设置
        self.normal_pen = QPen(QColor("#666666"), 2)
        self.selected_pen = QPen(QColor("#1976d2"), 3)
        self.hover_pen = QPen(QColor("#42a5f5"), 2)
        
        # 箭头设置
        self.arrow_size = 10
        
        # 连接类型
        self.connection_type = data.get('connection_type', 'sequence') if data else 'sequence'
        
        # 更新路径
        self.update_path()
        
        # 注册到连接的项目
        if hasattr(from_item, 'add_output_connection'):
            from_item.add_output_connection(self)
        if hasattr(to_item, 'add_input_connection'):
            to_item.add_input_connection(self)
            
    def update_path(self):
        """更新连接路径"""
        if not self.from_item or not self.to_item:
            return
            
        # 获取连接点
        start_point = self.from_item.get_output_point()
        end_point = self.to_item.get_input_point()
        
        # 创建路径
        path = QPainterPath()
        
        if self.connection_type == 'sequence':
            self.create_straight_path(path, start_point, end_point)
        elif self.connection_type == 'condition':
            self.create_curved_path(path, start_point, end_point)
        elif self.connection_type == 'parallel':
            self.create_parallel_path(path, start_point, end_point)
        else:
            self.create_straight_path(path, start_point, end_point)
            
        self.setPath(path)
        
    def create_straight_path(self, path, start, end):
        """创建直线路径"""
        path.moveTo(start)
        path.lineTo(end)
        
        # 添加箭头
        self.add_arrow_to_path(path, start, end)
        
    def create_curved_path(self, path, start, end):
        """创建曲线路径"""
        # 计算控制点
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        control1 = QPointF(start.x() + dx * 0.5, start.y())
        control2 = QPointF(end.x() - dx * 0.5, end.y())
        
        path.moveTo(start)
        path.cubicTo(control1, control2, end)
        
        # 添加箭头
        self.add_arrow_to_path(path, control2, end)
        
    def create_parallel_path(self, path, start, end):
        """创建并行路径"""
        # 创建双线路径
        offset = 3
        
        # 计算垂直向量
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.sqrt(dx * dx + dy * dy)
        
        if length > 0:
            unit_x = dx / length
            unit_y = dy / length
            perp_x = -unit_y * offset
            perp_y = unit_x * offset
            
            # 第一条线
            start1 = QPointF(start.x() + perp_x, start.y() + perp_y)
            end1 = QPointF(end.x() + perp_x, end.y() + perp_y)
            path.moveTo(start1)
            path.lineTo(end1)
            
            # 第二条线
            start2 = QPointF(start.x() - perp_x, start.y() - perp_y)
            end2 = QPointF(end.x() - perp_x, end.y() - perp_y)
            path.moveTo(start2)
            path.lineTo(end2)
            
            # 添加箭头
            self.add_arrow_to_path(path, start, end)
        else:
            self.create_straight_path(path, start, end)
            
    def add_arrow_to_path(self, path, start, end):
        """添加箭头到路径"""
        # 计算箭头方向
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.sqrt(dx * dx + dy * dy)
        
        if length > 0:
            # 单位向量
            unit_x = dx / length
            unit_y = dy / length
            
            # 箭头点
            arrow_length = self.arrow_size
            arrow_width = self.arrow_size * 0.6
            
            # 箭头的三个点
            tip = end
            left = QPointF(
                end.x() - arrow_length * unit_x - arrow_width * unit_y,
                end.y() - arrow_length * unit_y + arrow_width * unit_x
            )
            right = QPointF(
                end.x() - arrow_length * unit_x + arrow_width * unit_y,
                end.y() - arrow_length * unit_y - arrow_width * unit_x
            )
            
            # 绘制箭头
            path.moveTo(left)
            path.lineTo(tip)
            path.lineTo(right)
            
    def paint(self, painter, option, widget):
        """绘制连接线"""
        # 选择画笔
        if self.isSelected():
            pen = self.selected_pen
        elif self.isHovered:
            pen = self.hover_pen
        else:
            pen = self.normal_pen
            
        painter.setPen(pen)
        painter.drawPath(self.path())
        
    def hoverEnterEvent(self, event):
        """鼠标悬停进入"""
        self.isHovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """鼠标悬停离开"""
        self.isHovered = False
        self.update()
        super().hoverLeaveEvent(event)
        
    def can_delete(self):
        """是否可以删除"""
        return True
        
    def remove_from_items(self):
        """从连接的项目中移除"""
        if hasattr(self.from_item, 'remove_connection'):
            self.from_item.remove_connection(self)
        if hasattr(self.to_item, 'remove_connection'):
            self.to_item.remove_connection(self)


class SOPItem(BaseGraphicsItem):
    """SOP文档图形项目"""
    
    def __init__(self, data=None, parent=None):
        super().__init__(data, parent)
        
        # 设置默认大小
        self.setRect(0, 0, 80, 100)
        
        # SOP特有样式
        self.document_color = QColor('#ffc107')
        
    def draw_shape(self, painter, option, widget):
        """绘制SOP形状"""
        rect = self.rect()
        
        # 绘制文档形状
        path = QPainterPath()
        fold_size = 12
        
        path.moveTo(rect.topLeft())
        path.lineTo(rect.topRight() - QPointF(fold_size, 0))
        path.lineTo(rect.topRight() + QPointF(0, fold_size))
        path.lineTo(rect.bottomRight())
        path.lineTo(rect.bottomLeft())
        path.closeSubpath()
        
        # 绘制折角
        fold_path = QPainterPath()
        fold_path.moveTo(rect.topRight() - QPointF(fold_size, 0))
        fold_path.lineTo(rect.topRight() - QPointF(fold_size, fold_size))
        fold_path.lineTo(rect.topRight() + QPointF(0, fold_size))
        
        painter.drawPath(path)
        painter.setPen(QPen(self.document_color.darker(120), 1))
        painter.drawPath(fold_path)
        
    def get_display_text(self):
        """获取显示文本"""
        title = self.data.get('title', '未命名文档')
        # 如果标题太长，截断并添加省略号
        if len(title) > 8:
            return title[:8] + "..."
        return title


class KPIItem(BaseGraphicsItem):
    """KPI指标图形项目"""
    
    def __init__(self, data=None, parent=None):
        super().__init__(data, parent)
        
        # 设置默认大小
        self.setRect(0, 0, 90, 70)
        
        # KPI特有样式
        self.kpi_color = QColor('#4caf50')
        
    def draw_shape(self, painter, option, widget):
        """绘制KPI形状"""
        rect = self.rect()
        
        # 绘制仪表盘形状
        painter.drawRoundedRect(rect, 8, 8)
        
        # 绘制指标图标
        icon_rect = QRectF(rect.center().x() - 10, rect.top() + 8, 20, 20)
        painter.setPen(QPen(self.kpi_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(icon_rect)
        
        # 绘制指针
        center = icon_rect.center()
        angle = math.pi * 0.25  # 45度
        end_x = center.x() + 8 * math.cos(angle)
        end_y = center.y() + 8 * math.sin(angle)
        painter.drawLine(center, QPointF(end_x, end_y))
        
    def get_display_text(self):
        """获取显示文本"""
        name = self.data.get('name', '未命名指标')
        # 如果名称太长，截断并添加省略号
        if len(name) > 8:
            return name[:8] + "..."
        return name