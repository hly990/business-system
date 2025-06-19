"""
任务管理器组件
"""
import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QToolBar, QComboBox, QLabel, QCalendarWidget,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon

from ..ui.components.custom_widgets import (
    CustomButton, CustomLineEdit, StatusIndicator
)
from ..services.data_manager import DataManager


class TaskTableWidget(QTableWidget):
    """任务表格组件"""
    
    task_selected = pyqtSignal(dict)
    task_double_clicked = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
        
    def setup_table(self):
        """设置表格"""
        # 设置列
        headers = ["状态", "任务名称", "优先级", "负责人", "截止日期", "进度", "所属流程"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # 设置表格属性
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        
        # 设置列宽
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.setColumnWidth(0, 60)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(5, 100)
        
        # 连接信号
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
    def load_tasks(self, tasks_data):
        """加载任务数据"""
        self.setRowCount(len(tasks_data))
        
        for row, task in enumerate(tasks_data):
            # 状态指示器
            status = task.get('status', 'pending')
            status_widget = StatusIndicator(self.get_status_type(status))
            self.setCellWidget(row, 0, status_widget)
            
            # 任务名称
            name_item = QTableWidgetItem(task.get('title', ''))
            name_item.setData(Qt.ItemDataRole.UserRole, task)
            self.setItem(row, 1, name_item)
            
            # 优先级
            priority = task.get('priority', 'medium')
            priority_item = QTableWidgetItem(self.get_priority_text(priority))
            priority_item.setForeground(QColor(self.get_priority_color(priority)))
            self.setItem(row, 2, priority_item)
            
            # 负责人
            assignee = task.get('assignee_name', '未分配')
            self.setItem(row, 3, QTableWidgetItem(assignee))
            
            # 截止日期
            due_date = task.get('due_date', '')
            due_item = QTableWidgetItem(due_date)
            if self.is_overdue(due_date):
                due_item.setForeground(QColor('#f44336'))
            self.setItem(row, 4, due_item)
            
            # 进度
            progress = task.get('progress', 0)
            progress_widget = self.create_progress_widget(progress)
            self.setCellWidget(row, 5, progress_widget)
            
            # 所属流程
            process_name = task.get('process_name', '')
            self.setItem(row, 6, QTableWidgetItem(process_name))
            
    def get_status_type(self, status):
        """获取状态类型"""
        status_map = {
            'pending': 'info',
            'in_progress': 'warning',
            'completed': 'normal',
            'cancelled': 'error',
            'overdue': 'error'
        }
        return status_map.get(status, 'inactive')
        
    def get_priority_text(self, priority):
        """获取优先级文本"""
        priority_map = {
            'low': '低',
            'medium': '中',
            'high': '高',
            'urgent': '紧急'
        }
        return priority_map.get(priority, '中')
        
    def get_priority_color(self, priority):
        """获取优先级颜色"""
        color_map = {
            'low': '#4caf50',
            'medium': '#ff9800',
            'high': '#f44336',
            'urgent': '#9c27b0'
        }
        return color_map.get(priority, '#ff9800')
        
    def is_overdue(self, due_date_str):
        """检查是否过期"""
        if not due_date_str:
            return False
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            return due_date.date() < datetime.now().date()
        except:
            return False
            
    def create_progress_widget(self, progress):
        """创建进度条组件"""
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(progress)
        progress_bar.setTextVisible(True)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1976d2;
                border-radius: 3px;
            }
        """)
        return progress_bar
        
    def on_selection_changed(self):
        """选择变化处理"""
        current_row = self.currentRow()
        if current_row >= 0:
            name_item = self.item(current_row, 1)
            if name_item:
                task_data = name_item.data(Qt.ItemDataRole.UserRole)
                if task_data:
                    self.task_selected.emit(task_data)
                    
    def on_item_double_clicked(self, item):
        """双击处理"""
        if item.column() == 1:  # 任务名称列
            task_data = item.data(Qt.ItemDataRole.UserRole)
            if task_data:
                self.task_double_clicked.emit(task_data)


class TaskManager(QWidget):
    """任务管理器组件"""
    
    # 信号定义
    task_selected = pyqtSignal(dict)
    task_created = pyqtSignal(dict)
    task_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = DataManager()
        
        # 数据缓存
        self.tasks_data = []
        self.filtered_tasks = []
        
        # 当前选中的任务
        self.current_task = None
        
        # 刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        
        self.init_ui()
        self.setup_connections()
        self.load_data()
        
        # 启动自动刷新（每2分钟）
        self.refresh_timer.start(120000)
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # 左侧：任务列表
        self.create_task_list_panel(main_splitter)
        
        # 右侧：任务详情和日历
        self.create_details_panel(main_splitter)
        
        main_splitter.setSizes([600, 400])
        
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        
        # 新建任务按钮
        new_task_btn = CustomButton("新建任务", ":/icons/add_task.png", "primary")
        new_task_btn.clicked.connect(self.create_new_task)
        self.toolbar.addWidget(new_task_btn)
        
        self.toolbar.addSeparator()
        
        # 刷新按钮
        refresh_btn = CustomButton("刷新", ":/icons/refresh.png", "secondary")
        refresh_btn.clicked.connect(self.refresh_data)
        self.toolbar.addWidget(refresh_btn)
        
        self.toolbar.addSeparator()
        
        # 筛选器
        self.toolbar.addWidget(QLabel("状态:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "待处理", "进行中", "已完成", "已取消", "已过期"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        self.toolbar.addWidget(self.status_filter)
        
        self.toolbar.addWidget(QLabel("优先级:"))
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["全部", "低", "中", "高", "紧急"])
        self.priority_filter.currentTextChanged.connect(self.apply_filters)
        self.toolbar.addWidget(self.priority_filter)
        
        self.toolbar.addSeparator()
        
        # 搜索框
        self.search_edit = CustomLineEdit("搜索任务...")
        self.search_edit.textChanged.connect(self.apply_filters)
        self.toolbar.addWidget(self.search_edit)
        
    def create_task_list_panel(self, parent):
        """创建任务列表面板"""
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        # 统计信息
        self.create_stats_section(list_layout)
        
        # 任务表格
        self.task_table = TaskTableWidget()
        list_layout.addWidget(self.task_table)
        
        parent.addWidget(list_widget)
        
    def create_stats_section(self, layout):
        """创建统计信息区域"""
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 10)
        
        # 总任务数
        self.total_label = QLabel("总任务: 0")
        self.total_label.setStyleSheet("font-weight: bold; color: #333;")
        stats_layout.addWidget(self.total_label)
        
        # 待处理
        self.pending_label = QLabel("待处理: 0")
        self.pending_label.setStyleSheet("color: #2196f3;")
        stats_layout.addWidget(self.pending_label)
        
        # 进行中
        self.in_progress_label = QLabel("进行中: 0")
        self.in_progress_label.setStyleSheet("color: #ff9800;")
        stats_layout.addWidget(self.in_progress_label)
        
        # 已完成
        self.completed_label = QLabel("已完成: 0")
        self.completed_label.setStyleSheet("color: #4caf50;")
        stats_layout.addWidget(self.completed_label)
        
        # 已过期
        self.overdue_label = QLabel("已过期: 0")
        self.overdue_label.setStyleSheet("color: #f44336;")
        stats_layout.addWidget(self.overdue_label)
        
        stats_layout.addStretch()
        
        layout.addWidget(stats_widget)
        
    def create_details_panel(self, parent):
        """创建详情面板"""
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # 标签页
        self.details_tabs = QTabWidget()
        details_layout.addWidget(self.details_tabs)
        
        # 任务详情标签页
        self.create_task_details_tab()
        
        # 日历标签页
        self.create_calendar_tab()
        
        # 甘特图标签页
        self.create_gantt_tab()
        
        parent.addWidget(details_widget)
        
    def create_task_details_tab(self):
        """创建任务详情标签页"""
        details_widget = QWidget()
        layout = QVBoxLayout(details_widget)
        
        # 任务信息显示区域
        self.task_info_widget = QWidget()
        self.task_info_layout = QVBoxLayout(self.task_info_widget)
        
        # 默认显示提示
        no_selection_label = QLabel("请选择一个任务查看详情")
        no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_selection_label.setStyleSheet("color: #999; font-size: 14px;")
        self.task_info_layout.addWidget(no_selection_label)
        
        layout.addWidget(self.task_info_widget)
        
        self.details_tabs.addTab(details_widget, "任务详情")
        
    def create_calendar_tab(self):
        """创建日历标签页"""
        calendar_widget = QWidget()
        layout = QVBoxLayout(calendar_widget)
        
        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_calendar_date_clicked)
        layout.addWidget(self.calendar)
        
        # 当日任务列表
        today_tasks_label = QLabel("当日任务:")
        today_tasks_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(today_tasks_label)
        
        self.today_tasks_tree = QTreeWidget()
        self.today_tasks_tree.setHeaderLabels(["任务", "状态", "优先级"])
        self.today_tasks_tree.setRootIsDecorated(False)
        layout.addWidget(self.today_tasks_tree)
        
        self.details_tabs.addTab(calendar_widget, "日历视图")
        
    def create_gantt_tab(self):
        """创建甘特图标签页"""
        gantt_widget = QWidget()
        layout = QVBoxLayout(gantt_widget)
        
        # 甘特图占位符
        gantt_label = QLabel("甘特图视图")
        gantt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gantt_label.setStyleSheet("color: #999; font-size: 16px;")
        layout.addWidget(gantt_label)
        
        # TODO: 实现甘特图组件
        
        self.details_tabs.addTab(gantt_widget, "甘特图")
        
    def setup_connections(self):
        """设置信号连接"""
        # 任务表格信号
        self.task_table.task_selected.connect(self.on_task_selected)
        self.task_table.task_double_clicked.connect(self.on_task_double_clicked)
        
        # 数据管理器信号
        self.data_manager.data_loaded.connect(self.on_data_loaded)
        self.data_manager.error_occurred.connect(self.on_error_occurred)
        
    def load_data(self):
        """加载数据"""
        try:
            self.data_manager.load_tasks()
        except Exception as e:
            self.logger.error(f"加载任务数据失败: {e}")
            
    def refresh_data(self):
        """刷新数据"""
        self.load_data()
        
    def on_data_loaded(self, data_type):
        """数据加载完成处理"""
        if data_type == 'tasks':
            self.tasks_data = self.data_manager.get_tasks()
            self.apply_filters()
            self.update_stats()
            self.update_calendar()
            
    def on_error_occurred(self, error_msg):
        """错误处理"""
        self.logger.error(f"任务管理器错误: {error_msg}")
        
    def apply_filters(self):
        """应用筛选器"""
        filtered_tasks = self.tasks_data.copy()
        
        # 状态筛选
        status_filter = self.status_filter.currentText()
        if status_filter != "全部":
            status_map = {
                "待处理": "pending",
                "进行中": "in_progress",
                "已完成": "completed",
                "已取消": "cancelled",
                "已过期": "overdue"
            }
            target_status = status_map.get(status_filter)
            if target_status:
                filtered_tasks = [t for t in filtered_tasks if t.get('status') == target_status]
                
        # 优先级筛选
        priority_filter = self.priority_filter.currentText()
        if priority_filter != "全部":
            priority_map = {"低": "low", "中": "medium", "高": "high", "紧急": "urgent"}
            target_priority = priority_map.get(priority_filter)
            if target_priority:
                filtered_tasks = [t for t in filtered_tasks if t.get('priority') == target_priority]
                
        # 搜索筛选
        search_text = self.search_edit.text().strip().lower()
        if search_text:
            filtered_tasks = [
                t for t in filtered_tasks
                if search_text in t.get('title', '').lower() or
                   search_text in t.get('description', '').lower()
            ]
            
        self.filtered_tasks = filtered_tasks
        self.task_table.load_tasks(filtered_tasks)
        
    def update_stats(self):
        """更新统计信息"""
        total = len(self.tasks_data)
        pending = len([t for t in self.tasks_data if t.get('status') == 'pending'])
        in_progress = len([t for t in self.tasks_data if t.get('status') == 'in_progress'])
        completed = len([t for t in self.tasks_data if t.get('status') == 'completed'])
        overdue = len([t for t in self.tasks_data if t.get('status') == 'overdue'])
        
        self.total_label.setText(f"总任务: {total}")
        self.pending_label.setText(f"待处理: {pending}")
        self.in_progress_label.setText(f"进行中: {in_progress}")
        self.completed_label.setText(f"已完成: {completed}")
        self.overdue_label.setText(f"已过期: {overdue}")
        
    def update_calendar(self):
        """更新日历"""
        # 标记有任务的日期
        # TODO: 实现日历日期标记功能
        pass
        
    def on_task_selected(self, task_data):
        """任务选择处理"""
        self.current_task = task_data
        self.update_task_details(task_data)
        self.task_selected.emit(task_data)
        
    def on_task_double_clicked(self, task_data):
        """任务双击处理"""
        # TODO: 打开任务编辑对话框
        self.logger.info(f"双击任务: {task_data.get('title')}")
        
    def update_task_details(self, task_data):
        """更新任务详情显示"""
        # 清除现有内容
        for i in reversed(range(self.task_info_layout.count())):
            child = self.task_info_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        # 创建详情显示
        title_label = QLabel(task_data.get('title', ''))
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.task_info_layout.addWidget(title_label)
        
        # 基本信息
        info_text = f"""
        <b>状态:</b> {task_data.get('status', '')}<br>
        <b>优先级:</b> {task_data.get('priority', '')}<br>
        <b>负责人:</b> {task_data.get('assignee_name', '未分配')}<br>
        <b>截止日期:</b> {task_data.get('due_date', '')}<br>
        <b>进度:</b> {task_data.get('progress', 0)}%<br>
        <b>所属流程:</b> {task_data.get('process_name', '')}<br>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        self.task_info_layout.addWidget(info_label)
        
        # 描述
        if task_data.get('description'):
            desc_label = QLabel(f"<b>描述:</b><br>{task_data.get('description')}")
            desc_label.setWordWrap(True)
            self.task_info_layout.addWidget(desc_label)
            
        self.task_info_layout.addStretch()
        
    def on_calendar_date_clicked(self, date):
        """日历日期点击处理"""
        selected_date = date.toString("yyyy-MM-dd")
        
        # 筛选当日任务
        daily_tasks = [
            t for t in self.tasks_data
            if t.get('due_date') == selected_date
        ]
        
        # 更新当日任务列表
        self.today_tasks_tree.clear()
        for task in daily_tasks:
            item = QTreeWidgetItem([
                task.get('title', ''),
                task.get('status', ''),
                task.get('priority', '')
            ])
            self.today_tasks_tree.addTopLevelItem(item)
            
    def create_new_task(self):
        """创建新任务"""
        # TODO: 打开任务创建对话框
        self.logger.info("创建新任务")
        
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        return False
        
    def save(self):
        """保存"""
        pass