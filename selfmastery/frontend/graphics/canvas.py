"""
QGraphicsView画布组件
"""
import math
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QRubberBand
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QWheelEvent, QMouseEvent, QKeyEvent, QPen, QBrush


class GraphicsCanvas(QGraphicsView):
    """图形画布组件"""
    
    # 信号定义
    mouse_moved = pyqtSignal(QPointF)           # 鼠标移动
    item_selected = pyqtSignal(object)          # 项目选择
    item_moved = pyqtSignal(object)             # 项目移动
    connection_requested = pyqtSignal(object, object)  # 连接请求
    zoom_changed = pyqtSignal(float)            # 缩放变化
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 画布设置
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # 拖拽设置
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRubberBandSelectionMode(Qt.ItemSelectionMode.IntersectsItemShape)
        
        # 滚动条设置
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 缩放设置
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_step = 1.15
        
        # 平移设置
        self.pan_mode = False
        self.last_pan_point = QPointF()
        
        # 连接模式
        self.connection_mode = False
        self.connection_start_item = None
        self.connection_line = None
        
        # 选择框
        self.selection_start = QPointF()
        self.selection_rect = None
        
        # 网格设置
        self.show_grid = True
        self.grid_size = 20
        self.grid_pen = QPen(Qt.GlobalColor.lightGray, 0.5, Qt.PenStyle.DotLine)
        
        # 背景设置
        self.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
        
        # 性能优化
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState)
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.delayed_update)
        
    def set_scene(self, scene):
        """设置场景"""
        self.setScene(scene)
        if scene:
            scene.selectionChanged.connect(self.on_selection_changed)
            
    def drawBackground(self, painter, rect):
        """绘制背景"""
        super().drawBackground(painter, rect)
        
        if self.show_grid:
            self.draw_grid(painter, rect)
            
    def draw_grid(self, painter, rect):
        """绘制网格"""
        painter.setPen(self.grid_pen)
        
        # 计算网格线的起始位置
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        
        # 绘制垂直线
        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += self.grid_size
            
        # 绘制水平线
        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += self.grid_size
            
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮事件 - 缩放"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl + 滚轮缩放
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            # 普通滚动
            super().wheelEvent(event)
            
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.MiddleButton:
            # 中键平移
            self.start_pan(event.position().toPoint())
        elif event.button() == Qt.MouseButton.LeftButton:
            if self.connection_mode:
                self.handle_connection_click(event)
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        scene_pos = self.mapToScene(event.position().toPoint())
        self.mouse_moved.emit(scene_pos)
        
        if self.pan_mode:
            self.update_pan(event.position().toPoint())
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.end_pan()
        else:
            super().mouseReleaseEvent(event)
            
    def keyPressEvent(self, event: QKeyEvent):
        """键盘按下事件"""
        if event.key() == Qt.Key.Key_Space:
            # 空格键临时平移模式
            if not self.pan_mode:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif event.key() == Qt.Key.Key_Delete:
            # 删除选中项目
            self.delete_selected_items()
        elif event.key() == Qt.Key.Key_Escape:
            # 取消当前操作
            self.cancel_current_operation()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_A:
                # Ctrl+A 全选
                self.select_all_items()
            elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Ctrl++ 放大
                self.zoom_in()
            elif event.key() == Qt.Key.Key_Minus:
                # Ctrl+- 缩小
                self.zoom_out()
            elif event.key() == Qt.Key.Key_0:
                # Ctrl+0 重置缩放
                self.reset_zoom()
        else:
            super().keyPressEvent(event)
            
    def keyReleaseEvent(self, event: QKeyEvent):
        """键盘释放事件"""
        if event.key() == Qt.Key.Key_Space:
            if not self.pan_mode:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().keyReleaseEvent(event)
        
    def start_pan(self, pos):
        """开始平移"""
        self.pan_mode = True
        self.last_pan_point = pos
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        
    def update_pan(self, pos):
        """更新平移"""
        if self.pan_mode:
            delta = pos - self.last_pan_point
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self.last_pan_point = pos
            
    def end_pan(self):
        """结束平移"""
        self.pan_mode = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
    def zoom_in(self):
        """放大"""
        if self.zoom_factor < self.max_zoom:
            self.scale(self.zoom_step, self.zoom_step)
            self.zoom_factor *= self.zoom_step
            self.zoom_changed.emit(self.zoom_factor)
            
    def zoom_out(self):
        """缩小"""
        if self.zoom_factor > self.min_zoom:
            self.scale(1.0 / self.zoom_step, 1.0 / self.zoom_step)
            self.zoom_factor /= self.zoom_step
            self.zoom_changed.emit(self.zoom_factor)
            
    def reset_zoom(self):
        """重置缩放"""
        self.resetTransform()
        self.zoom_factor = 1.0
        self.zoom_changed.emit(self.zoom_factor)
        
    def zoom_to_fit(self):
        """缩放到适合"""
        if self.scene():
            items_rect = self.scene().itemsBoundingRect()
            if not items_rect.isEmpty():
                self.fitInView(items_rect, Qt.AspectRatioMode.KeepAspectRatio)
                transform = self.transform()
                self.zoom_factor = transform.m11()
                self.zoom_changed.emit(self.zoom_factor)
                
    def zoom_to_selection(self):
        """缩放到选中项目"""
        selected_items = self.scene().selectedItems()
        if selected_items:
            # 计算选中项目的边界矩形
            bounding_rect = QRectF()
            for item in selected_items:
                bounding_rect = bounding_rect.united(item.sceneBoundingRect())
                
            if not bounding_rect.isEmpty():
                # 添加一些边距
                margin = 50
                bounding_rect.adjust(-margin, -margin, margin, margin)
                self.fitInView(bounding_rect, Qt.AspectRatioMode.KeepAspectRatio)
                transform = self.transform()
                self.zoom_factor = transform.m11()
                self.zoom_changed.emit(self.zoom_factor)
                
    def center_on_item(self, item):
        """居中显示项目"""
        if item:
            self.centerOn(item)
            
    def handle_connection_click(self, event):
        """处理连接模式下的点击"""
        scene_pos = self.mapToScene(event.position().toPoint())
        item = self.scene().itemAt(scene_pos, self.transform())
        
        if item and hasattr(item, 'can_connect') and item.can_connect():
            if not self.connection_start_item:
                # 开始连接
                self.connection_start_item = item
                item.set_connection_highlight(True)
            else:
                # 完成连接
                if item != self.connection_start_item:
                    self.connection_requested.emit(self.connection_start_item, item)
                self.cancel_connection()
        else:
            # 取消连接
            self.cancel_connection()
            
    def cancel_connection(self):
        """取消连接"""
        if self.connection_start_item:
            self.connection_start_item.set_connection_highlight(False)
            self.connection_start_item = None
            
    def set_connection_mode(self, enabled):
        """设置连接模式"""
        self.connection_mode = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.cancel_connection()
            
    def delete_selected_items(self):
        """删除选中的项目"""
        selected_items = self.scene().selectedItems()
        for item in selected_items:
            if hasattr(item, 'can_delete') and item.can_delete():
                self.scene().removeItem(item)
                
    def select_all_items(self):
        """选择所有项目"""
        if self.scene():
            for item in self.scene().items():
                if item.flags() & item.GraphicsItemFlag.ItemIsSelectable:
                    item.setSelected(True)
                    
    def cancel_current_operation(self):
        """取消当前操作"""
        self.cancel_connection()
        if self.scene():
            self.scene().clearSelection()
            
    def on_selection_changed(self):
        """选择变化处理"""
        selected_items = self.scene().selectedItems()
        if selected_items:
            self.item_selected.emit(selected_items[0])
            
    def set_grid_visible(self, visible):
        """设置网格可见性"""
        self.show_grid = visible
        self.viewport().update()
        
    def set_grid_size(self, size):
        """设置网格大小"""
        self.grid_size = size
        self.viewport().update()
        
    def get_visible_rect(self):
        """获取可见区域矩形"""
        return self.mapToScene(self.viewport().rect()).boundingRect()
        
    def delayed_update(self):
        """延迟更新"""
        self.viewport().update()
        
    def schedule_update(self):
        """计划更新"""
        if not self.update_timer.isActive():
            self.update_timer.start(16)  # 约60FPS
            
    def export_to_image(self, filename, size=None):
        """导出为图片"""
        if not self.scene():
            return False
            
        try:
            from PyQt6.QtGui import QPixmap, QPainter
            
            # 获取场景边界
            scene_rect = self.scene().itemsBoundingRect()
            if scene_rect.isEmpty():
                return False
                
            # 设置导出尺寸
            if size:
                pixmap = QPixmap(size)
            else:
                pixmap = QPixmap(scene_rect.size().toSize())
                
            pixmap.fill(Qt.GlobalColor.white)
            
            # 渲染场景到图片
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.scene().render(painter, pixmap.rect(), scene_rect)
            painter.end()
            
            # 保存图片
            return pixmap.save(filename)
            
        except Exception as e:
            print(f"导出图片失败: {e}")
            return False
            
    def print_canvas(self, printer):
        """打印画布"""
        if not self.scene():
            return False
            
        try:
            from PyQt6.QtGui import QPainter
            
            painter = QPainter(printer)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 获取场景边界
            scene_rect = self.scene().itemsBoundingRect()
            if scene_rect.isEmpty():
                return False
                
            # 渲染到打印机
            self.scene().render(painter, printer.pageRect(), scene_rect)
            painter.end()
            
            return True
            
        except Exception as e:
            print(f"打印失败: {e}")
            return False