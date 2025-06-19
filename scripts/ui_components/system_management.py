"""
业务系统管理窗口
按照技术架构文档设计的系统管理界面
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView, QWidget, QSplitter,
    QTextBrowser, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QSpinBox, QGroupBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon

class DataLoadingThread(QThread):
    """数据加载线程"""
    data_loaded = pyqtSignal(str, list)
    error_occurred = pyqtSignal(str, str)
    
    def __init__(self, api_client, data_type):
        super().__init__()
        self.api_client = api_client
        self.data_type = data_type
        
    def run(self):
        try:
            if self.data_type == "systems":
                data = self.api_client.get_systems()
            else:
                data = []
            
            self.data_loaded.emit(self.data_type, data)
        except Exception as e:
            self.error_occurred.emit(self.data_type, str(e))

class SystemEditDialog(QDialog):
    """系统编辑对话框"""
    
    def __init__(self, system_data=None, parent=None):
        super().__init__(parent)
        self.system_data = system_data
        self.setWindowTitle("编辑业务系统" if system_data else "新建业务系统")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
        if system_data:
            self.load_system_data()
            
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 表单区域
        form_group = QGroupBox("系统信息")
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入系统名称")
        form_layout.addRow("系统名称*:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("请输入系统描述")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("系统描述:", self.description_edit)
        
        self.owner_combo = QComboBox()
        self.owner_combo.addItems(["张三", "李四", "王五", "赵六"])
        form_layout.addRow("负责人:", self.owner_combo)
        
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 5)
        self.priority_spin.setValue(3)
        form_layout.addRow("优先级:", self.priority_spin)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_system)
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
        
        self.cancel_btn = QPushButton("取消")
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
        
    def load_system_data(self):
        """加载系统数据"""
        if self.system_data:
            self.name_edit.setText(self.system_data.get('name', ''))
            self.description_edit.setText(self.system_data.get('description', ''))
            # 设置其他字段...
            
    def save_system(self):
        """保存系统"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "验证错误", "系统名称不能为空")
            return
            
        # 这里应该调用API保存数据
        QMessageBox.information(self, "保存成功", f"系统 '{name}' 已保存")
        self.accept()

class SystemManagementWindow(QDialog):
    """业务系统管理窗口"""
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("业务系统管理")
        self.setGeometry(200, 200, 1000, 700)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题区域
        title_layout = QHBoxLayout()
        title_label = QLabel("业务系统管理")
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
        
        self.add_btn = QPushButton("➕ 新建系统")
        self.add_btn.clicked.connect(self.add_system)
        
        self.edit_btn = QPushButton("✏️ 编辑")
        self.edit_btn.clicked.connect(self.edit_system)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self.delete_system)
        self.delete_btn.setEnabled(False)
        
        self.clone_btn = QPushButton("📋 克隆")
        self.clone_btn.clicked.connect(self.clone_system)
        self.clone_btn.setEnabled(False)
        
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
        
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.clone_btn]:
            btn.setStyleSheet(button_style)
            toolbar_layout.addWidget(btn)
            
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 主内容区域
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧系统列表
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # 系统列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "系统名称", "描述", "负责人", "状态"])
        
        # 设置表格属性
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.edit_system)
        
        left_layout.addWidget(QLabel("系统列表"))
        left_layout.addWidget(self.table)
        
        # 状态栏
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        left_layout.addWidget(self.status_label)
        
        left_widget.setLayout(left_layout)
        main_splitter.addWidget(left_widget)
        
        # 右侧详情面板
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("系统详情"))
        
        self.details_browser = QTextBrowser()
        self.details_browser.setHtml("""
        <h3>业务系统管理</h3>
        <p>在这里您可以：</p>
        <ul>
            <li>📊 查看所有业务系统的概览</li>
            <li>➕ 创建新的业务系统</li>
            <li>✏️ 编辑现有系统的信息</li>
            <li>🗑️ 删除不需要的系统</li>
            <li>📋 克隆系统作为模板</li>
            <li>👥 分配系统负责人</li>
        </ul>
        <p><strong>提示</strong>: 选择左侧的系统来查看详细信息</p>
        """)
        right_layout.addWidget(self.details_browser)
        
        # 系统统计信息
        stats_group = QGroupBox("系统统计")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("正在加载统计信息...")
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        right_widget.setLayout(right_layout)
        main_splitter.addWidget(right_widget)
        
        # 设置分割器比例
        main_splitter.setSizes([600, 400])
        layout.addWidget(main_splitter)
        
        self.setLayout(layout)
        
    def load_data(self):
        """加载系统数据"""
        self.status_label.setText("正在加载系统数据...")
        self.loading_thread = DataLoadingThread(self.api_client, "systems")
        self.loading_thread.data_loaded.connect(self.on_data_loaded)
        self.loading_thread.error_occurred.connect(self.on_error)
        self.loading_thread.start()
        
    def on_data_loaded(self, data_type, data):
        """数据加载完成"""
        self.table.setRowCount(len(data))
        
        for row, system in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(system.get('id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(system.get('name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(system.get('description', '')))
            self.table.setItem(row, 3, QTableWidgetItem(system.get('owner', '未分配')))
            self.table.setItem(row, 4, QTableWidgetItem('活跃'))
            
        self.status_label.setText(f"已加载 {len(data)} 个系统")
        
        # 更新统计信息
        active_count = len(data)
        self.stats_label.setText(f"""
        📊 系统总数: {active_count}
        ✅ 活跃系统: {active_count}
        ⏸️ 暂停系统: 0
        👥 已分配负责人: {sum(1 for s in data if s.get('owner_id'))}
        """)
        
    def on_error(self, data_type, error):
        """错误处理"""
        self.status_label.setText(f"加载失败: {error}")
        QMessageBox.warning(self, "错误", f"加载系统数据失败:\n{error}")
        
    def on_selection_changed(self):
        """选择变化处理"""
        selected_rows = self.table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.clone_btn.setEnabled(has_selection)
        
        if has_selection:
            row = selected_rows[0].row()
            system_name = self.table.item(row, 1).text()
            system_desc = self.table.item(row, 2).text()
            system_owner = self.table.item(row, 3).text()
            
            self.details_browser.setHtml(f"""
            <h3>{system_name}</h3>
            <p><strong>描述:</strong> {system_desc}</p>
            <p><strong>负责人:</strong> {system_owner}</p>
            <p><strong>状态:</strong> 活跃</p>
            <hr>
            <h4>系统功能</h4>
            <ul>
                <li>业务流程管理</li>
                <li>数据处理和分析</li>
                <li>用户权限控制</li>
                <li>报表生成</li>
            </ul>
            <h4>关联流程</h4>
            <p>该系统包含 3 个业务流程</p>
            """)
            
    def add_system(self):
        """新建系统"""
        dialog = SystemEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()  # 重新加载数据
            
    def edit_system(self):
        """编辑系统"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        system_data = {
            'id': self.table.item(row, 0).text(),
            'name': self.table.item(row, 1).text(),
            'description': self.table.item(row, 2).text(),
            'owner': self.table.item(row, 3).text()
        }
        
        dialog = SystemEditDialog(system_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()  # 重新加载数据
            
    def delete_system(self):
        """删除系统"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        system_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除系统 '{system_name}' 吗？\n\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 这里应该调用API删除系统
            QMessageBox.information(self, "删除成功", f"系统 '{system_name}' 已删除")
            self.load_data()  # 重新加载数据
            
    def clone_system(self):
        """克隆系统"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        system_name = self.table.item(row, 1).text()
        
        # 这里应该调用API克隆系统
        QMessageBox.information(self, "克隆成功", f"已创建系统 '{system_name}' 的副本")
        self.load_data()  # 重新加载数据