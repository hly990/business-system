"""
左侧导航树组件
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QMenu, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction, QFont

from ..services.data_manager import DataManager
from ..ui.components.custom_widgets import CustomLineEdit, CustomButton


class NavigationTree(QWidget):
    """导航树组件"""
    
    # 信号定义
    item_selected = pyqtSignal(dict)        # 项目选择信号
    item_double_clicked = pyqtSignal(dict)  # 项目双击信号
    item_context_menu = pyqtSignal(dict)    # 右键菜单信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = DataManager()
        
        # 数据缓存
        self.systems_data = []
        self.processes_data = []
        self.sops_data = []
        
        # 搜索相关
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.init_ui()
        self.setup_connections()
        self.load_data()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QPushButton("业务导航")
        title_label.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                border: none;
                padding: 8px;
                text-align: left;
                background-color: transparent;
            }
        """)
        title_layout.addWidget(title_label)
        
        # 刷新按钮
        refresh_btn = CustomButton("", ":/icons/refresh.png", "secondary")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("刷新数据")
        refresh_btn.clicked.connect(self.refresh_data)
        title_layout.addWidget(refresh_btn)
        
        layout.addLayout(title_layout)
        
        # 搜索框
        self.search_edit = CustomLineEdit("搜索业务系统、流程或SOP...")
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_edit)
        
        # 树形控件
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setRootIsDecorated(True)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # 设置树形控件样式
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 4px;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: #1976d2;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #f0f0f0;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: url(:/icons/branch_closed.png);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: url(:/icons/branch_open.png);
            }
        """)
        
        layout.addWidget(self.tree_widget)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        
        add_system_btn = CustomButton("新建系统", ":/icons/add_system.png", "primary")
        add_system_btn.clicked.connect(self.add_system)
        button_layout.addWidget(add_system_btn)
        
        add_process_btn = CustomButton("新建流程", ":/icons/add_process.png", "secondary")
        add_process_btn.clicked.connect(self.add_process)
        button_layout.addWidget(add_process_btn)
        
        layout.addLayout(button_layout)
        
    def setup_connections(self):
        """设置信号连接"""
        # 树形控件信号
        self.tree_widget.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # 数据管理器信号
        self.data_manager.data_loaded.connect(self.on_data_loaded)
        self.data_manager.error_occurred.connect(self.on_error_occurred)
        
    def load_data(self):
        """加载数据"""
        try:
            # 加载业务系统数据
            self.data_manager.load_systems()
            
            # 加载流程数据
            self.data_manager.load_processes()
            
            # 加载SOP数据
            self.data_manager.load_sops()
            
        except Exception as e:
            self.logger.error(f"加载导航数据失败: {e}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")
            
    def refresh_data(self):
        """刷新数据"""
        self.tree_widget.clear()
        self.load_data()
        
    def build_tree(self):
        """构建树形结构"""
        self.tree_widget.clear()
        
        # 创建根节点
        systems_root = QTreeWidgetItem(self.tree_widget, ["业务系统"])
        systems_root.setIcon(0, QIcon(":/icons/systems.png"))
        systems_root.setExpanded(True)
        
        processes_root = QTreeWidgetItem(self.tree_widget, ["业务流程"])
        processes_root.setIcon(0, QIcon(":/icons/processes.png"))
        processes_root.setExpanded(True)
        
        sops_root = QTreeWidgetItem(self.tree_widget, ["SOP文档"])
        sops_root.setIcon(0, QIcon(":/icons/sops.png"))
        sops_root.setExpanded(True)
        
        # 构建业务系统树
        self.build_systems_tree(systems_root)
        
        # 构建流程树
        self.build_processes_tree(processes_root)
        
        # 构建SOP树
        self.build_sops_tree(sops_root)
        
    def build_systems_tree(self, parent_item):
        """构建业务系统树"""
        # 按层级组织系统数据
        root_systems = [s for s in self.systems_data if not s.get('parent_id')]
        
        for system in root_systems:
            self.add_system_item(parent_item, system)
            
    def add_system_item(self, parent_item, system_data):
        """添加系统项目"""
        item = QTreeWidgetItem(parent_item, [system_data.get('name', '未命名系统')])
        item.setIcon(0, QIcon(":/icons/system.png"))
        
        # 存储数据
        item.setData(0, Qt.ItemDataRole.UserRole, {
            'type': 'system',
            'id': system_data.get('id'),
            'data': system_data
        })
        
        # 添加子系统
        child_systems = [s for s in self.systems_data if s.get('parent_id') == system_data.get('id')]
        for child_system in child_systems:
            self.add_system_item(item, child_system)
            
        # 添加系统下的流程
        system_processes = [p for p in self.processes_data if p.get('system_id') == system_data.get('id')]
        for process in system_processes:
            process_item = QTreeWidgetItem(item, [process.get('name', '未命名流程')])
            process_item.setIcon(0, QIcon(":/icons/process.png"))
            process_item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'process',
                'id': process.get('id'),
                'data': process
            })
            
    def build_processes_tree(self, parent_item):
        """构建流程树"""
        # 按系统分组流程
        system_groups = {}
        for process in self.processes_data:
            system_id = process.get('system_id')
            if system_id not in system_groups:
                system_groups[system_id] = []
            system_groups[system_id].append(process)
            
        for system_id, processes in system_groups.items():
            # 找到对应的系统
            system = next((s for s in self.systems_data if s.get('id') == system_id), None)
            system_name = system.get('name', '未知系统') if system else '未知系统'
            
            system_item = QTreeWidgetItem(parent_item, [system_name])
            system_item.setIcon(0, QIcon(":/icons/system.png"))
            
            for process in processes:
                process_item = QTreeWidgetItem(system_item, [process.get('name', '未命名流程')])
                process_item.setIcon(0, QIcon(":/icons/process.png"))
                process_item.setData(0, Qt.ItemDataRole.UserRole, {
                    'type': 'process',
                    'id': process.get('id'),
                    'data': process
                })
                
    def build_sops_tree(self, parent_item):
        """构建SOP树"""
        # 按分类组织SOP
        categories = {}
        for sop in self.sops_data:
            category = sop.get('category', '其他')
            if category not in categories:
                categories[category] = []
            categories[category].append(sop)
            
        for category, sops in categories.items():
            category_item = QTreeWidgetItem(parent_item, [category])
            category_item.setIcon(0, QIcon(":/icons/folder.png"))
            
            for sop in sops:
                sop_item = QTreeWidgetItem(category_item, [sop.get('title', '未命名文档')])
                sop_item.setIcon(0, QIcon(":/icons/sop.png"))
                sop_item.setData(0, Qt.ItemDataRole.UserRole, {
                    'type': 'sop',
                    'id': sop.get('id'),
                    'data': sop
                })
                
    def on_search_text_changed(self, text):
        """搜索文本变化处理"""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms延迟搜索
        
    def perform_search(self):
        """执行搜索"""
        search_text = self.search_edit.text().strip().lower()
        
        if not search_text:
            # 显示所有项目
            self.show_all_items()
            return
            
        # 隐藏所有项目
        self.hide_all_items()
        
        # 搜索匹配项目
        self.search_items(self.tree_widget.invisibleRootItem(), search_text)
        
    def show_all_items(self):
        """显示所有项目"""
        iterator = QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()
            item.setHidden(False)
            iterator += 1
            
    def hide_all_items(self):
        """隐藏所有项目"""
        iterator = QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()
            if item.parent():  # 不隐藏根项目
                item.setHidden(True)
            iterator += 1
            
    def search_items(self, parent_item, search_text):
        """搜索项目"""
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            item_text = item.text(0).lower()
            
            # 检查当前项目是否匹配
            if search_text in item_text:
                self.show_item_and_parents(item)
                
            # 递归搜索子项目
            self.search_items(item, search_text)
            
    def show_item_and_parents(self, item):
        """显示项目及其父项目"""
        current = item
        while current:
            current.setHidden(False)
            if current.parent():
                current.parent().setExpanded(True)
            current = current.parent()
            
    def on_item_selection_changed(self):
        """项目选择变化处理"""
        current_item = self.tree_widget.currentItem()
        if current_item:
            item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data:
                self.item_selected.emit(item_data)
                
    def on_item_double_clicked(self, item, column):
        """项目双击处理"""
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        if item_data:
            self.item_double_clicked.emit(item_data)
            
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.tree_widget.itemAt(position)
        if not item:
            return
            
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not item_data:
            return
            
        menu = QMenu(self)
        item_type = item_data.get('type')
        
        if item_type == 'system':
            # 系统右键菜单
            edit_action = QAction("编辑系统", self)
            edit_action.triggered.connect(lambda: self.edit_system(item_data))
            menu.addAction(edit_action)
            
            add_process_action = QAction("添加流程", self)
            add_process_action.triggered.connect(lambda: self.add_process_to_system(item_data))
            menu.addAction(add_process_action)
            
            menu.addSeparator()
            
            delete_action = QAction("删除系统", self)
            delete_action.triggered.connect(lambda: self.delete_system(item_data))
            menu.addAction(delete_action)
            
        elif item_type == 'process':
            # 流程右键菜单
            edit_action = QAction("编辑流程", self)
            edit_action.triggered.connect(lambda: self.edit_process(item_data))
            menu.addAction(edit_action)
            
            create_sop_action = QAction("创建SOP", self)
            create_sop_action.triggered.connect(lambda: self.create_sop_for_process(item_data))
            menu.addAction(create_sop_action)
            
            menu.addSeparator()
            
            delete_action = QAction("删除流程", self)
            delete_action.triggered.connect(lambda: self.delete_process(item_data))
            menu.addAction(delete_action)
            
        elif item_type == 'sop':
            # SOP右键菜单
            edit_action = QAction("编辑SOP", self)
            edit_action.triggered.connect(lambda: self.edit_sop(item_data))
            menu.addAction(edit_action)
            
            menu.addSeparator()
            
            delete_action = QAction("删除SOP", self)
            delete_action.triggered.connect(lambda: self.delete_sop(item_data))
            menu.addAction(delete_action)
            
        if menu.actions():
            menu.exec(self.tree_widget.mapToGlobal(position))
            
    # 数据操作方法
    def add_system(self):
        """添加新系统"""
        name, ok = QInputDialog.getText(self, "新建系统", "请输入系统名称:")
        if ok and name.strip():
            try:
                system_data = {
                    'name': name.strip(),
                    'description': '',
                    'parent_id': None
                }
                # 调用数据管理器创建系统
                self.data_manager.create_system(system_data)
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建系统失败: {e}")
                
    def add_process(self):
        """添加新流程"""
        name, ok = QInputDialog.getText(self, "新建流程", "请输入流程名称:")
        if ok and name.strip():
            # 这里需要选择所属系统
            QMessageBox.information(self, "提示", "请先选择一个系统，然后右键添加流程")
            
    def add_process_to_system(self, system_data):
        """向系统添加流程"""
        name, ok = QInputDialog.getText(self, "新建流程", "请输入流程名称:")
        if ok and name.strip():
            try:
                process_data = {
                    'name': name.strip(),
                    'description': '',
                    'system_id': system_data['id']
                }
                self.data_manager.create_process(process_data)
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建流程失败: {e}")
                
    def edit_system(self, system_data):
        """编辑系统"""
        self.item_double_clicked.emit(system_data)
        
    def edit_process(self, process_data):
        """编辑流程"""
        self.item_double_clicked.emit(process_data)
        
    def edit_sop(self, sop_data):
        """编辑SOP"""
        self.item_double_clicked.emit(sop_data)
        
    def create_sop_for_process(self, process_data):
        """为流程创建SOP"""
        title, ok = QInputDialog.getText(self, "创建SOP", "请输入SOP标题:")
        if ok and title.strip():
            try:
                sop_data = {
                    'title': title.strip(),
                    'content': '',
                    'process_id': process_data['id']
                }
                self.data_manager.create_sop(sop_data)
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建SOP失败: {e}")
                
    def delete_system(self, system_data):
        """删除系统"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除系统 '{system_data['data']['name']}' 吗？\n这将同时删除其下的所有流程。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.data_manager.delete_system(system_data['id'])
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除系统失败: {e}")
                
    def delete_process(self, process_data):
        """删除流程"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除流程 '{process_data['data']['name']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.data_manager.delete_process(process_data['id'])
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除流程失败: {e}")
                
    def delete_sop(self, sop_data):
        """删除SOP"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除SOP '{sop_data['data']['title']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.data_manager.delete_sop(sop_data['id'])
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除SOP失败: {e}")
                
    # 数据管理器回调
    def on_data_loaded(self, data_type):
        """数据加载完成回调"""
        if data_type == 'systems':
            self.systems_data = self.data_manager.get_systems()
        elif data_type == 'processes':
            self.processes_data = self.data_manager.get_processes()
        elif data_type == 'sops':
            self.sops_data = self.data_manager.get_sops()
            
        # 当所有数据加载完成后重建树
        if (hasattr(self, 'systems_data') and 
            hasattr(self, 'processes_data') and 
            hasattr(self, 'sops_data')):
            self.build_tree()
            
    def on_error_occurred(self, error_msg):
        """错误处理回调"""
        self.logger.error(f"导航树数据操作错误: {error_msg}")