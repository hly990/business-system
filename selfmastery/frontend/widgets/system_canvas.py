"""
业务系统图谱画布组件
"""
import logging
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsLineItem, QMenu, QInputDialog, QMessageBox, QLabel,
    QSlider, QComboBox
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPainter, QFont, QPolygonF,
    QWheelEvent, QMouseEvent, QPainterPath
)

from ..services.data_manager import DataManager
from ..ui.components.custom_widgets import CustomButton
from ..graphics.canvas import GraphicsCanvas
from ..graphics.items import SystemItem, ProcessItem, ConnectionItem
from ..graphics.layouts import AutoLayoutManager


class SystemCanvas(QWidget):
    """系统图谱画布组件"""
    
    # 信号定义
    system_selected = pyqtSignal(dict)      # 系统选择信号
    process_selected = pyqtSignal(dict)     # 流程选择信号
    item_moved = pyqtSignal(dict)           # 项目移动信号
    connection_created = pyqtSignal(dict)   # 连接创建信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = DataManager()
        
        # 画布状态
        self.current_mode = "select"  # select, pan, connect
        self.zoom_level = 1.0
        self.is_modified = False
        
        # 数据缓存
        self.systems_data = []
        self.processes_data = []
        self.connections_data = []
        
        # 图形项目映射
        self.system_items = {}      # id -> SystemItem
        self.process_items = {}     # id -> ProcessItem
        self.connection_items = {}  # id -> ConnectionItem
        
        self.init_ui()
        self.setup_connections()
        self.load_data()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # 画布区域
        self.canvas = GraphicsCanvas()
        self.canvas.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.canvas.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.canvas.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 设置画布样式
        self.canvas.setStyleSheet("""
            QGraphicsView {
                border: 1px solid #e0e0e0;
                background-color: #fafafa;
            }
        """)
        
        layout.addWidget(self.canvas)
        
        # 状态栏
        self.create_status_bar()
        layout.addWidget(self.status_bar)
        
        # 设置场景
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.canvas.setScene(self.scene)
        
        # 自动布局管理器
        self.layout_manager = AutoLayoutManager(self.scene)
        
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        
        # 模式选择
        mode_label = QLabel("模式:")
        self.toolbar.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["选择", "平移", "连接"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        self.toolbar.addWidget(self.mode_combo)
        
        self.toolbar.addSeparator()
        
        # 新建按钮
        new_system_btn = CustomButton("新建系统", ":/icons/add_system.png", "primary")
        new_system_btn.clicked.connect(self.create_new_system)
        self.toolbar.addWidget(new_system_btn)
        
        new_process_btn = CustomButton("新建流程", ":/icons/add_process.png", "secondary")
        new_process_btn.clicked.connect(self.create_new_process)
        self.toolbar.addWidget(new_process_btn)
        
        self.toolbar.addSeparator()
        
        # 布局按钮
        auto_layout_btn = CustomButton("自动布局", ":/icons/auto_layout.png", "secondary")
        auto_layout_btn.clicked.connect(self.auto_layout)
        self.toolbar.addWidget(auto_layout_btn)
        
        align_btn = CustomButton("对齐", ":/icons/align.png", "secondary")
        align_btn.clicked.connect(self.align_items)
        self.toolbar.addWidget(align_btn)
        
        self.toolbar.addSeparator()
        
        # 缩放控制
        zoom_label = QLabel("缩放:")
        self.toolbar.addWidget(zoom_label)
        
        zoom_out_btn = CustomButton("-", "", "secondary")
        zoom_out_btn.setFixedSize(30, 30)
        zoom_out_btn.clicked.connect(self.zoom_out)
        self.toolbar.addWidget(zoom_out_btn)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        self.toolbar.addWidget(self.zoom_slider)
        
        zoom_in_btn = CustomButton("+", "", "secondary")
        zoom_in_btn.setFixedSize(30, 30)
        zoom_in_btn.clicked.connect(self.zoom_in)
        self.toolbar.addWidget(zoom_in_btn)
        
        fit_btn = CustomButton("适应", ":/icons/fit.png", "secondary")
        fit_btn.clicked.connect(self.zoom_fit)
        self.toolbar.addWidget(fit_btn)
        
        self.toolbar.addSeparator()
        
        # 保存按钮
        save_btn = CustomButton("保存", ":/icons/save.png", "primary")
        save_btn.clicked.connect(self.save_layout)
        self.toolbar.addWidget(save_btn)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("就绪")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.coord_label = QLabel("坐标: (0, 0)")
        status_layout.addWidget(self.coord_label)
        
        self.zoom_label = QLabel("缩放: 100%")
        status_layout.addWidget(self.zoom_label)
        
        self.items_label = QLabel("项目: 0")
        status_layout.addWidget(self.items_label)
        
    def setup_connections(self):
        """设置信号连接"""
        # 画布信号
        self.canvas.mouse_moved.connect(self.on_mouse_moved)
        self.canvas.item_selected.connect(self.on_item_selected)
        self.canvas.item_moved.connect(self.on_item_moved)
        self.canvas.connection_requested.connect(self.on_connection_requested)
        
        # 场景信号
        self.scene.selectionChanged.connect(self.on_selection_changed)
        
        # 数据管理器信号
        self.data_manager.data_loaded.connect(self.on_data_loaded)
        self.data_manager.error_occurred.connect(self.on_error_occurred)
        
    def load_data(self):
        """加载数据"""
        try:
            self.data_manager.load_systems()
            self.data_manager.load_processes()
            self.data_manager.load_process_connections()
        except Exception as e:
            self.logger.error(f"加载画布数据失败: {e}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")
            
    def build_canvas(self):
        """构建画布内容"""
        # 清空现有内容
        self.scene.clear()
        self.system_items.clear()
        self.process_items.clear()
        self.connection_items.clear()
        
        # 创建系统项目
        for system in self.systems_data:
            self.create_system_item(system)
            
        # 创建流程项目
        for process in self.processes_data:
            self.create_process_item(process)
            
        # 创建连接
        for connection in self.connections_data:
            self.create_connection_item(connection)
            
        # 更新状态
        self.update_items_count()
        
    def create_system_item(self, system_data):
        """创建系统图形项目"""
        item = SystemItem(system_data)
        item.setPos(system_data.get('position_x', 0), system_data.get('position_y', 0))
        
        # 设置系统颜色
        color = QColor(system_data.get('color', '#1976d2'))
        item.set_color(color)
        
        self.scene.addItem(item)
        self.system_items[system_data['id']] = item
        
        return item
        
    def create_process_item(self, process_data):
        """创建流程图形项目"""
        item = ProcessItem(process_data)
        item.setPos(process_data.get('position_x', 0), process_data.get('position_y', 0))
        
        # 设置流程状态颜色
        status_colors = {
            'draft': '#9e9e9e',
            'active': '#4caf50',
            'inactive': '#ff9800',
            'archived': '#f44336'
        }
        status = process_data.get('status', 'draft')
        color = QColor(status_colors.get(status, '#9e9e9e'))
        item.set_status_color(color)
        
        self.scene.addItem(item)
        self.process_items[process_data['id']] = item
        
        return item
        
    def create_connection_item(self, connection_data):
        """创建连接图形项目"""
        from_id = connection_data.get('from_process_id')
        to_id = connection_data.get('to_process_id')
        
        from_item = self.process_items.get(from_id)
        to_item = self.process_items.get(to_id)
        
        if from_item and to_item:
            item = ConnectionItem(from_item, to_item, connection_data)
            self.scene.addItem(item)
            self.connection_items[connection_data['id']] = item
            return item
            
        return None
        
    def change_mode(self, mode_text):
        """切换操作模式"""
        mode_map = {
            "选择": "select",
            "平移": "pan",
            "连接": "connect"
        }
        
        self.current_mode = mode_map.get(mode_text, "select")
        
        if self.current_mode == "select":
            self.canvas.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        elif self.current_mode == "pan":
            self.canvas.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        elif self.current_mode == "connect":
            self.canvas.setDragMode(QGraphicsView.DragMode.NoDrag)
            
        self.status_label.setText(f"当前模式: {mode_text}")
        
    def create_new_system(self):
        """创建新系统"""
        name, ok = QInputDialog.getText(self, "新建系统", "请输入系统名称:")
        if ok and name.strip():
            try:
                # 在画布中心创建系统
                center = self.canvas.mapToScene(self.canvas.rect().center())
                
                system_data = {
                    'name': name.strip(),
                    'description': '',
                    'position_x': center.x(),
                    'position_y': center.y(),
                    'color': '#1976d2'
                }
                
                # 保存到数据库
                created_system = self.data_manager.create_system(system_data)
                
                # 在画布上创建图形项目
                self.create_system_item(created_system)
                self.update_items_count()
                self.set_modified(True)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建系统失败: {e}")
                
    def create_new_process(self):
        """创建新流程"""
        # 检查是否选择了系统
        selected_items = self.scene.selectedItems()
        selected_system = None
        
        for item in selected_items:
            if isinstance(item, SystemItem):
                selected_system = item
                break
                
        if not selected_system:
            QMessageBox.information(self, "提示", "请先选择一个系统，然后创建流程")
            return
            
        name, ok = QInputDialog.getText(self, "新建流程", "请输入流程名称:")
        if ok and name.strip():
            try:
                # 在选中系统附近创建流程
                system_pos = selected_system.pos()
                
                process_data = {
                    'name': name.strip(),
                    'description': '',
                    'system_id': selected_system.data['id'],
                    'position_x': system_pos.x() + 150,
                    'position_y': system_pos.y(),
                    'status': 'draft'
                }
                
                # 保存到数据库
                created_process = self.data_manager.create_process(process_data)
                
                # 在画布上创建图形项目
                self.create_process_item(created_process)
                self.update_items_count()
                self.set_modified(True)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建流程失败: {e}")
                
    def auto_layout(self):
        """自动布局"""
        try:
            self.layout_manager.apply_hierarchical_layout(
                list(self.system_items.values()),
                list(self.process_items.values()),
                list(self.connection_items.values())
            )
            self.set_modified(True)
            self.status_label.setText("自动布局完成")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"自动布局失败: {e}")
            
    def align_items(self):
        """对齐选中项目"""
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.information(self, "提示", "请选择至少两个项目进行对齐")
            return
            
        # 简单的左对齐实现
        if selected_items:
            min_x = min(item.pos().x() for item in selected_items)
            for item in selected_items:
                item.setPos(min_x, item.pos().y())
                
        self.set_modified(True)
        self.status_label.setText("项目对齐完成")
        
    def zoom_in(self):
        """放大"""
        self.zoom_level = min(self.zoom_level * 1.2, 3.0)
        self.apply_zoom()
        
    def zoom_out(self):
        """缩小"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self.apply_zoom()
        
    def zoom_fit(self):
        """适应窗口"""
        if self.scene.items():
            self.canvas.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            transform = self.canvas.transform()
            self.zoom_level = transform.m11()
            self.update_zoom_controls()
        else:
            self.zoom_level = 1.0
            self.apply_zoom()
            
    def on_zoom_changed(self, value):
        """缩放滑块变化"""
        self.zoom_level = value / 100.0
        self.apply_zoom()
        
    def apply_zoom(self):
        """应用缩放"""
        self.canvas.setTransform(self.canvas.transform().scale(
            self.zoom_level / self.canvas.transform().m11(),
            self.zoom_level / self.canvas.transform().m22()
        ))
        self.update_zoom_controls()
        
    def update_zoom_controls(self):
        """更新缩放控件"""
        zoom_percent = int(self.zoom_level * 100)
        self.zoom_slider.setValue(zoom_percent)
        self.zoom_label.setText(f"缩放: {zoom_percent}%")
        
    def save_layout(self):
        """保存布局"""
        try:
            # 保存所有项目的位置
            for item_id, item in self.system_items.items():
                pos = item.pos()
                self.data_manager.update_system_position(item_id, pos.x(), pos.y())
                
            for item_id, item in self.process_items.items():
                pos = item.pos()
                self.data_manager.update_process_position(item_id, pos.x(), pos.y())
                
            self.set_modified(False)
            self.status_label.setText("布局已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存布局失败: {e}")
            
    def update_items_count(self):
        """更新项目计数"""
        total_items = len(self.system_items) + len(self.process_items)
        self.items_label.setText(f"项目: {total_items}")
        
    def set_modified(self, modified):
        """设置修改状态"""
        self.is_modified = modified
        
    # 事件处理
    def on_mouse_moved(self, scene_pos):
        """鼠标移动处理"""
        self.coord_label.setText(f"坐标: ({int(scene_pos.x())}, {int(scene_pos.y())})")
        
    def on_item_selected(self, item):
        """项目选择处理"""
        if isinstance(item, SystemItem):
            self.system_selected.emit(item.data)
        elif isinstance(item, ProcessItem):
            self.process_selected.emit(item.data)
            
    def on_item_moved(self, item):
        """项目移动处理"""
        self.set_modified(True)
        self.item_moved.emit({
            'type': 'system' if isinstance(item, SystemItem) else 'process',
            'id': item.data['id'],
            'position': {'x': item.pos().x(), 'y': item.pos().y()}
        })
        
    def on_selection_changed(self):
        """选择变化处理"""
        selected_items = self.scene.selectedItems()
        if selected_items:
            item = selected_items[0]
            self.on_item_selected(item)
            
    def on_connection_requested(self, from_item, to_item):
        """连接请求处理"""
        if isinstance(from_item, ProcessItem) and isinstance(to_item, ProcessItem):
            try:
                connection_data = {
                    'from_process_id': from_item.data['id'],
                    'to_process_id': to_item.data['id'],
                    'connection_type': 'sequence'
                }
                
                # 保存到数据库
                created_connection = self.data_manager.create_process_connection(connection_data)
                
                # 在画布上创建连接
                self.create_connection_item(created_connection)
                self.set_modified(True)
                
                self.connection_created.emit(created_connection)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建连接失败: {e}")
                
    # 数据管理器回调
    def on_data_loaded(self, data_type):
        """数据加载完成回调"""
        if data_type == 'systems':
            self.systems_data = self.data_manager.get_systems()
        elif data_type == 'processes':
            self.processes_data = self.data_manager.get_processes()
        elif data_type == 'process_connections':
            self.connections_data = self.data_manager.get_process_connections()
            
        # 当所有数据加载完成后重建画布
        if (hasattr(self, 'systems_data') and 
            hasattr(self, 'processes_data') and 
            hasattr(self, 'connections_data')):
            self.build_canvas()
            
    def on_error_occurred(self, error_msg):
        """错误处理回调"""
        self.logger.error(f"画布数据操作错误: {error_msg}")
        
    # 公共接口
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        return self.is_modified
        
    def save(self):
        """保存"""
        self.save_layout()
        
    def undo(self):
        """撤销"""
        # TODO: 实现撤销功能
        pass
        
    def redo(self):
        """重做"""
        # TODO: 实现重做功能
        pass
        
    def copy(self):
        """复制"""
        # TODO: 实现复制功能
        pass
        
    def paste(self):
        """粘贴"""
        # TODO: 实现粘贴功能
        pass