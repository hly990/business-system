"""
任务管理窗口
按照技术架构文档设计的任务管理界面
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QWidget, QTextBrowser, QGroupBox,
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QSpinBox, QHeaderView,
    QTabWidget, QListWidget, QListWidgetItem, QCheckBox, QDateEdit,
    QProgressBar, QFrame, QSplitter, QCalendarWidget, QTimeEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate, QTime, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

class TaskEditDialog(QDialog):
    """任务编辑对话框"""
    
    def __init__(self, task_data=None, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setWindowTitle("编辑任务" if task_data else "新建任务")
        self.setModal(True)
        self.resize(600, 500)
        self.setup_ui()
        
        if task_data:
            self.load_task_data()
            
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息区域
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("请输入任务标题")
        info_layout.addRow("任务标题*:", self.title_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("请输入任务描述")
        self.description_edit.setMaximumHeight(100)
        info_layout.addRow("任务描述:", self.description_edit)
        
        self.process_combo = QComboBox()
        self.process_combo.addItems(["客户开发流程", "订单处理流程", "生产计划流程", "质量控制流程"])
        info_layout.addRow("关联流程:", self.process_combo)
        
        self.assignee_combo = QComboBox()
        self.assignee_combo.addItems(["张三", "李四", "王五", "赵六", "未分配"])
        info_layout.addRow("负责人:", self.assignee_combo)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 任务设置区域
        settings_group = QGroupBox("任务设置")
        settings_layout = QFormLayout()
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["低", "中", "高", "紧急"])
        self.priority_combo.setCurrentText("中")
        settings_layout.addRow("优先级:", self.priority_combo)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["待开始", "进行中", "已完成", "已取消", "已暂停"])
        settings_layout.addRow("任务状态:", self.status_combo)
        
        self.progress_spin = QSpinBox()
        self.progress_spin.setRange(0, 100)
        self.progress_spin.setSuffix("%")
        settings_layout.addRow("完成进度:", self.progress_spin)
        
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(7))
        self.due_date.setCalendarPopup(True)
        settings_layout.addRow("截止日期:", self.due_date)
        
        self.due_time = QTimeEdit()
        self.due_time.setTime(QTime(18, 0))
        settings_layout.addRow("截止时间:", self.due_time)
        
        self.estimated_hours = QSpinBox()
        self.estimated_hours.setRange(1, 999)
        self.estimated_hours.setValue(8)
        self.estimated_hours.setSuffix(" 小时")
        settings_layout.addRow("预计工时:", self.estimated_hours)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 附加信息区域
        extra_group = QGroupBox("附加信息")
        extra_layout = QFormLayout()
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("用逗号分隔多个标签")
        extra_layout.addRow("标签:", self.tags_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("任务备注信息")
        self.notes_edit.setMaximumHeight(80)
        extra_layout.addRow("备注:", self.notes_edit)
        
        extra_group.setLayout(extra_layout)
        layout.addWidget(extra_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.save_task)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        
        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_task_data(self):
        """加载任务数据"""
        if self.task_data:
            self.title_edit.setText(self.task_data.get('title', ''))
            self.description_edit.setText(self.task_data.get('description', ''))
            self.assignee_combo.setCurrentText(self.task_data.get('assignee', '未分配'))
            self.priority_combo.setCurrentText(self.task_data.get('priority', '中'))
            self.status_combo.setCurrentText(self.task_data.get('status', '待开始'))
            
    def save_task(self):
        """保存任务"""
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "验证错误", "任务标题不能为空")
            return
            
        assignee = self.assignee_combo.currentText()
        if assignee == "未分配":
            reply = QMessageBox.question(
                self, 
                "确认保存", 
                "任务尚未分配负责人，确定要保存吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
                
        QMessageBox.information(self, "保存成功", f"任务 '{title}' 已保存")
        self.accept()

class TaskCard(QFrame):
    """任务卡片组件"""
    
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.Box)
        
        # 根据优先级设置边框颜色
        priority = self.task_data.get('priority', '中')
        if priority == "紧急":
            border_color = "#EF4444"
        elif priority == "高":
            border_color = "#F59E0B"
        elif priority == "中":
            border_color = "#1976d2"
        else:
            border_color = "#6B7280"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {border_color};
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
            }}
            QFrame:hover {{
                border-color: {border_color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout()
        
        # 任务标题
        title_label = QLabel(self.task_data.get('title', '未命名任务'))
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #374151;
                margin-bottom: 4px;
            }
        """)
        layout.addWidget(title_label)
        
        # 任务信息
        info_layout = QHBoxLayout()
        
        # 负责人
        assignee = self.task_data.get('assignee', '未分配')
        assignee_label = QLabel(f"👤 {assignee}")
        assignee_label.setStyleSheet("font-size: 12px; color: #6B7280;")
        info_layout.addWidget(assignee_label)
        
        # 优先级
        priority_label = QLabel(f"🔥 {priority}")
        priority_label.setStyleSheet(f"font-size: 12px; color: {border_color}; font-weight: bold;")
        info_layout.addWidget(priority_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # 进度条
        progress = self.task_data.get('progress', 0)
        if isinstance(progress, str):
            progress = int(progress.rstrip('%'))
            
        progress_bar = QProgressBar()
        progress_bar.setValue(progress)
        progress_bar.setMaximumHeight(6)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: #F3F4F6;
            }}
            QProgressBar::chunk {{
                background-color: {border_color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress_bar)
        
        # 截止日期
        due_date = self.task_data.get('due_date', '未设置')
        due_label = QLabel(f"📅 {due_date}")
        due_label.setStyleSheet("font-size: 11px; color: #9CA3AF; margin-top: 4px;")
        layout.addWidget(due_label)
        
        self.setLayout(layout)
        self.setMaximumHeight(120)

class TaskManagementWindow(QDialog):
    """任务管理窗口"""
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("任务管理")
        self.setGeometry(200, 200, 1200, 800)
        self.task_cards = []
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题区域
        title_layout = QHBoxLayout()
        title_label = QLabel("任务管理")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1976d2;
                margin: 10px 0;
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.load_data)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.refresh_btn)
        layout.addLayout(title_layout)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.new_task_btn = QPushButton("➕ 新建任务")
        self.new_task_btn.clicked.connect(self.new_task)
        
        self.edit_task_btn = QPushButton("✏️ 编辑任务")
        self.edit_task_btn.clicked.connect(self.edit_task)
        self.edit_task_btn.setEnabled(False)
        
        self.complete_task_btn = QPushButton("✅ 完成任务")
        self.complete_task_btn.clicked.connect(self.complete_task)
        self.complete_task_btn.setEnabled(False)
        
        self.delete_task_btn = QPushButton("🗑️ 删除任务")
        self.delete_task_btn.clicked.connect(self.delete_task)
        self.delete_task_btn.setEnabled(False)
        
        self.batch_assign_btn = QPushButton("👥 批量分配")
        self.batch_assign_btn.clicked.connect(self.batch_assign)
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """
        
        for btn in [self.new_task_btn, self.edit_task_btn, self.complete_task_btn, self.delete_task_btn, self.batch_assign_btn]:
            btn.setStyleSheet(button_style)
            toolbar_layout.addWidget(btn)
            
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 主内容区域
        main_tab_widget = QTabWidget()
        
        # 看板视图标签页
        kanban_tab = QWidget()
        kanban_layout = QHBoxLayout()
        
        # 创建看板列
        columns = [
            ("待开始", "#6B7280"),
            ("进行中", "#1976d2"),
            ("已完成", "#10B981"),
            ("已暂停", "#F59E0B")
        ]
        
        self.kanban_columns = {}
        for column_name, color in columns:
            column_widget = QWidget()
            column_layout = QVBoxLayout()
            
            # 列标题
            header = QLabel(column_name)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
            """)
            column_layout.addWidget(header)
            
            # 任务列表
            task_list = QListWidget()
            task_list.setDragDropMode(QListWidget.DragDropMode.DragDrop)
            task_list.setDefaultDropAction(Qt.DropAction.MoveAction)
            self.kanban_columns[column_name] = task_list
            column_layout.addWidget(task_list)
            
            column_widget.setLayout(column_layout)
            kanban_layout.addWidget(column_widget)
            
        kanban_tab.setLayout(kanban_layout)
        main_tab_widget.addTab(kanban_tab, "看板视图")
        
        # 列表视图标签页
        list_tab = QWidget()
        list_layout = QVBoxLayout()
        
        # 筛选区域
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("筛选:"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部状态", "待开始", "进行中", "已完成", "已暂停"])
        self.status_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(self.status_filter)
        
        self.assignee_filter = QComboBox()
        self.assignee_filter.addItems(["全部人员", "张三", "李四", "王五", "赵六", "未分配"])
        self.assignee_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(self.assignee_filter)
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["全部优先级", "紧急", "高", "中", "低"])
        self.priority_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(self.priority_filter)
        
        filter_layout.addStretch()
        list_layout.addLayout(filter_layout)
        
        # 任务表格
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(7)
        self.task_table.setHorizontalHeaderLabels(["任务标题", "负责人", "状态", "优先级", "进度", "截止日期", "创建时间"])
        
        # 设置表格属性
        header = self.task_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.task_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.itemSelectionChanged.connect(self.on_task_selected)
        self.task_table.itemDoubleClicked.connect(self.edit_task)
        
        list_layout.addWidget(self.task_table)
        
        list_tab.setLayout(list_layout)
        main_tab_widget.addTab(list_tab, "列表视图")
        
        # 日历视图标签页
        calendar_tab = QWidget()
        calendar_layout = QHBoxLayout()
        
        # 左侧日历
        calendar_left = QWidget()
        calendar_left_layout = QVBoxLayout()
        
        calendar_left_layout.addWidget(QLabel("任务日历"))
        
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_selected)
        calendar_left_layout.addWidget(self.calendar)
        
        calendar_left.setLayout(calendar_left_layout)
        calendar_left.setMaximumWidth(350)
        calendar_layout.addWidget(calendar_left)
        
        # 右侧任务详情
        calendar_right = QWidget()
        calendar_right_layout = QVBoxLayout()
        
        self.selected_date_label = QLabel("今日任务")
        self.selected_date_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1976d2;
                margin: 10px 0;
            }
        """)
        calendar_right_layout.addWidget(self.selected_date_label)
        
        self.daily_tasks = QListWidget()
        calendar_right_layout.addWidget(self.daily_tasks)
        
        # 任务统计
        stats_group = QGroupBox("任务统计")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("正在加载统计信息...")
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        calendar_right_layout.addWidget(stats_group)
        
        calendar_right.setLayout(calendar_right_layout)
        calendar_layout.addWidget(calendar_right)
        
        calendar_tab.setLayout(calendar_layout)
        main_tab_widget.addTab(calendar_tab, "日历视图")
        
        layout.addWidget(main_tab_widget)
        self.setLayout(layout)
        
    def load_data(self):
        """加载任务数据"""
        try:
            tasks = self.api_client.get_tasks()
            
            # 更新看板视图
            for column_name, task_list in self.kanban_columns.items():
                task_list.clear()
                
            for task in tasks:
                status = task.get('status', '待开始')
                if status in self.kanban_columns:
                    card = TaskCard(task)
                    item = QListWidgetItem()
                    item.setSizeHint(card.sizeHint())
                    self.kanban_columns[status].addItem(item)
                    self.kanban_columns[status].setItemWidget(item, card)
                    
            # 更新列表视图
            self.task_table.setRowCount(len(tasks))
            for row, task in enumerate(tasks):
                self.task_table.setItem(row, 0, QTableWidgetItem(task.get('title', '')))
                self.task_table.setItem(row, 1, QTableWidgetItem(task.get('assignee', '未分配')))
                self.task_table.setItem(row, 2, QTableWidgetItem(task.get('status', '')))
                self.task_table.setItem(row, 3, QTableWidgetItem(task.get('priority', '')))
                self.task_table.setItem(row, 4, QTableWidgetItem(f"{task.get('progress', 0)}%"))
                self.task_table.setItem(row, 5, QTableWidgetItem(task.get('due_date', '')))
                self.task_table.setItem(row, 6, QTableWidgetItem('2024-01-15'))
                
            # 更新统计信息
            total_count = len(tasks)
            completed_count = sum(1 for t in tasks if t.get('status') == '已完成')
            in_progress_count = sum(1 for t in tasks if t.get('status') == '进行中')
            pending_count = sum(1 for t in tasks if t.get('status') == '待开始')
            
            self.stats_label.setText(f"""
            📊 任务总数: {total_count}
            ✅ 已完成: {completed_count}
            🔄 进行中: {in_progress_count}
            ⏳ 待开始: {pending_count}
            📈 完成率: {(completed_count/total_count*100):.1f}%
            """)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载任务数据失败:\n{str(e)}")
            
    def filter_tasks(self):
        """筛选任务"""
        # 这里实现筛选逻辑
        pass
        
    def on_task_selected(self):
        """任务选择处理"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.edit_task_btn.setEnabled(has_selection)
        self.complete_task_btn.setEnabled(has_selection)
        self.delete_task_btn.setEnabled(has_selection)
        
    def on_date_selected(self, date):
        """日期选择处理"""
        date_str = date.toString("yyyy-MM-dd")
        self.selected_date_label.setText(f"{date_str} 的任务")
        
        # 模拟加载当日任务
        self.daily_tasks.clear()
        daily_task_items = [
            "📋 完成客户需求分析报告",
            "📞 与供应商确认交货时间",
            "✅ 审核产品质量检测结果",
            "📊 更新项目进度报告"
        ]
        
        for item_text in daily_task_items:
            self.daily_tasks.addItem(item_text)
            
    def new_task(self):
        """新建任务"""
        dialog = TaskEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            
    def edit_task(self):
        """编辑任务"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        task_data = {
            'title': self.task_table.item(row, 0).text(),
            'assignee': self.task_table.item(row, 1).text(),
            'status': self.task_table.item(row, 2).text(),
            'priority': self.task_table.item(row, 3).text(),
            'progress': self.task_table.item(row, 4).text(),
            'due_date': self.task_table.item(row, 5).text()
        }
        
        dialog = TaskEditDialog(task_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            
    def complete_task(self):
        """完成任务"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        task_title = self.task_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            "确认完成", 
            f"确定要将任务 '{task_title}' 标记为已完成吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "任务完成", f"任务 '{task_title}' 已标记为完成")
            self.load_data()
            
    def delete_task(self):
        """删除任务"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        task_title = self.task_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除任务 '{task_title}' 吗？\n\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "删除成功", f"任务 '{task_title}' 已删除")
            self.load_data()
            
    def batch_assign(self):
        """批量分配任务"""
        QMessageBox.information(
            self, 
            "批量分配", 
            "批量分配任务功能\n\n支持操作:\n• 批量分配负责人\n• 批量修改优先级\n• 批量设置截止日期\n• 批量更新状态\n\n功能开发中..."
        )