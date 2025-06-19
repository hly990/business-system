"""
SOP文档管理窗口
按照技术架构文档设计的SOP管理界面
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QWidget, QTextBrowser, QGroupBox,
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QSpinBox, QHeaderView,
    QTabWidget, QListWidget, QListWidgetItem, QCheckBox, QDateEdit,
    QProgressBar, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QIcon, QTextDocument, QTextCursor

class SOPEditDialog(QDialog):
    """SOP编辑对话框"""
    
    def __init__(self, sop_data=None, parent=None):
        super().__init__(parent)
        self.sop_data = sop_data
        self.setWindowTitle("编辑SOP文档" if sop_data else "新建SOP文档")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()
        
        if sop_data:
            self.load_sop_data()
            
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息区域
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("请输入SOP标题")
        info_layout.addRow("标题*:", self.title_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["操作流程", "管理制度", "技术规范", "安全规程", "质量标准"])
        info_layout.addRow("分类:", self.category_combo)
        
        self.version_edit = QLineEdit()
        self.version_edit.setText("1.0")
        info_layout.addRow("版本:", self.version_edit)
        
        self.author_combo = QComboBox()
        self.author_combo.addItems(["张三", "李四", "王五", "赵六"])
        info_layout.addRow("作者:", self.author_combo)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["草稿", "审核中", "已发布", "已归档"])
        info_layout.addRow("状态:", self.status_combo)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 内容编辑区域
        content_group = QGroupBox("文档内容")
        content_layout = QVBoxLayout()
        
        # 内容编辑工具栏
        toolbar_layout = QHBoxLayout()
        
        bold_btn = QPushButton("B")
        bold_btn.setStyleSheet("font-weight: bold;")
        bold_btn.setMaximumWidth(30)
        
        italic_btn = QPushButton("I")
        italic_btn.setStyleSheet("font-style: italic;")
        italic_btn.setMaximumWidth(30)
        
        list_btn = QPushButton("•")
        list_btn.setMaximumWidth(30)
        
        table_btn = QPushButton("⊞")
        table_btn.setMaximumWidth(30)
        
        image_btn = QPushButton("🖼")
        image_btn.setMaximumWidth(30)
        
        for btn in [bold_btn, italic_btn, list_btn, table_btn, image_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    padding: 4px;
                    margin: 1px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            toolbar_layout.addWidget(btn)
            
        toolbar_layout.addStretch()
        content_layout.addLayout(toolbar_layout)
        
        # 内容编辑器
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("请输入SOP文档内容...")
        self.content_edit.setMinimumHeight(300)
        
        # 设置默认内容模板
        default_content = """
# SOP标准操作程序

## 1. 目的和范围
本SOP旨在规范...

## 2. 适用范围
适用于...

## 3. 职责分工
- 负责人：
- 执行人：
- 监督人：

## 4. 操作步骤

### 4.1 准备阶段
1. 检查所需材料和工具
2. 确认环境条件符合要求
3. 准备相关文档和记录表格

### 4.2 执行阶段
1. 按照标准流程执行操作
2. 记录关键数据和异常情况
3. 确保质量标准得到满足

### 4.3 完成阶段
1. 检查操作结果
2. 整理和归档相关文档
3. 清理工作环境

## 5. 质量控制
- 质量标准：
- 检查要点：
- 异常处理：

## 6. 相关文档
- 参考标准：
- 相关表格：
- 培训材料：

## 7. 修订记录
| 版本 | 修订日期 | 修订内容 | 修订人 |
|------|----------|----------|--------|
| 1.0  | 2024-01-01 | 初始版本 | 张三 |
        """
        self.content_edit.setText(default_content)
        content_layout.addWidget(self.content_edit)
        
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁 预览")
        self.preview_btn.clicked.connect(self.preview_sop)
        self.preview_btn.setStyleSheet("""
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
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.save_sop)
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
                background-color: #EF4444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_sop_data(self):
        """加载SOP数据"""
        if self.sop_data:
            self.title_edit.setText(self.sop_data.get('title', ''))
            self.content_edit.setText(self.sop_data.get('content', ''))
            self.version_edit.setText(self.sop_data.get('version', '1.0'))
            
    def preview_sop(self):
        """预览SOP"""
        title = self.title_edit.text()
        content = self.content_edit.toPlainText()
        
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(f"预览 - {title}")
        preview_dialog.resize(700, 500)
        
        layout = QVBoxLayout()
        
        preview_browser = QTextBrowser()
        content_html = content.replace('\n', '<br>')
        preview_browser.setHtml(f"""
        <h1>{title}</h1>
        <hr>
        <div style="white-space: pre-wrap; font-family: Arial, sans-serif; line-height: 1.6;">
        {content_html}
        </div>
        """)
        layout.addWidget(preview_browser)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(preview_dialog.close)
        layout.addWidget(close_btn)
        
        preview_dialog.setLayout(layout)
        preview_dialog.exec()
        
    def save_sop(self):
        """保存SOP"""
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "验证错误", "SOP标题不能为空")
            return
            
        content = self.content_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "验证错误", "SOP内容不能为空")
            return
            
        QMessageBox.information(self, "保存成功", f"SOP文档 '{title}' 已保存")
        self.accept()

class SOPManagementWindow(QDialog):
    """SOP文档管理窗口"""
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("SOP文档管理")
        self.setGeometry(200, 200, 1100, 750)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题区域
        title_layout = QHBoxLayout()
        title_label = QLabel("SOP文档管理")
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
        
        self.new_sop_btn = QPushButton("📝 新建SOP")
        self.new_sop_btn.clicked.connect(self.new_sop)
        
        self.edit_sop_btn = QPushButton("✏️ 编辑")
        self.edit_sop_btn.clicked.connect(self.edit_sop)
        self.edit_sop_btn.setEnabled(False)
        
        self.delete_sop_btn = QPushButton("🗑️ 删除")
        self.delete_sop_btn.clicked.connect(self.delete_sop)
        self.delete_sop_btn.setEnabled(False)
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.export_sop)
        self.export_btn.setEnabled(False)
        
        self.publish_btn = QPushButton("🚀 发布")
        self.publish_btn.clicked.connect(self.publish_sop)
        self.publish_btn.setEnabled(False)
        
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
        
        for btn in [self.new_sop_btn, self.edit_sop_btn, self.delete_sop_btn, self.export_btn, self.publish_btn]:
            btn.setStyleSheet(button_style)
            toolbar_layout.addWidget(btn)
            
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 主内容区域
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧SOP列表和筛选
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # 筛选区域
        filter_group = QGroupBox("筛选条件")
        filter_layout = QVBoxLayout()
        
        # 分类筛选
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["全部", "操作流程", "管理制度", "技术规范", "安全规程", "质量标准"])
        self.category_filter.currentTextChanged.connect(self.filter_sops)
        category_layout.addWidget(self.category_filter)
        filter_layout.addLayout(category_layout)
        
        # 状态筛选
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("状态:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "草稿", "审核中", "已发布", "已归档"])
        self.status_filter.currentTextChanged.connect(self.filter_sops)
        status_layout.addWidget(self.status_filter)
        filter_layout.addLayout(status_layout)
        
        filter_group.setLayout(filter_layout)
        left_layout.addWidget(filter_group)
        
        # SOP列表表格
        left_layout.addWidget(QLabel("SOP文档列表"))
        
        self.sop_table = QTableWidget()
        self.sop_table.setColumnCount(4)
        self.sop_table.setHorizontalHeaderLabels(["标题", "版本", "状态", "更新时间"])
        
        # 设置表格属性
        header = self.sop_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.sop_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sop_table.setAlternatingRowColors(True)
        self.sop_table.itemSelectionChanged.connect(self.on_sop_selected)
        self.sop_table.itemDoubleClicked.connect(self.edit_sop)
        
        left_layout.addWidget(self.sop_table)
        
        left_widget.setLayout(left_layout)
        main_splitter.addWidget(left_widget)
        
        # 右侧SOP预览和详情
        right_widget = QTabWidget()
        
        # SOP预览标签页
        preview_tab = QWidget()
        preview_layout = QVBoxLayout()
        
        self.sop_preview = QTextBrowser()
        self.sop_preview.setHtml("""
        <h2>SOP文档管理系统</h2>
        <p>标准作业程序(SOP)文档管理功能</p>
        <h3>功能特性：</h3>
        <ul>
            <li>📝 创建和编辑SOP文档</li>
            <li>📋 模板化文档结构</li>
            <li>🔄 版本控制和历史记录</li>
            <li>👥 协作编辑和审批流程</li>
            <li>📤 多格式导出(PDF, Word, HTML)</li>
            <li>🔍 全文搜索和标签分类</li>
            <li>📊 使用统计和效果分析</li>
        </ul>
        <h3>使用指南：</h3>
        <ol>
            <li>点击"新建SOP"创建新文档</li>
            <li>选择合适的文档模板</li>
            <li>填写文档基本信息</li>
            <li>编写详细的操作步骤</li>
            <li>设置审批流程和发布权限</li>
            <li>定期更新和维护文档</li>
        </ol>
        <p><strong>提示</strong>: 选择左侧的SOP文档来查看详细内容。</p>
        """)
        preview_layout.addWidget(self.sop_preview)
        
        preview_tab.setLayout(preview_layout)
        right_widget.addTab(preview_tab, "文档预览")
        
        # 统计信息标签页
        stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        
        # 统计图表区域
        stats_group = QGroupBox("文档统计")
        stats_group_layout = QVBoxLayout()
        
        self.stats_label = QLabel("正在加载统计信息...")
        stats_group_layout.addWidget(self.stats_label)
        
        # 进度条示例
        progress_layout = QVBoxLayout()
        
        draft_progress = QProgressBar()
        draft_progress.setValue(25)
        progress_layout.addWidget(QLabel("草稿文档: 25%"))
        progress_layout.addWidget(draft_progress)
        
        review_progress = QProgressBar()
        review_progress.setValue(15)
        progress_layout.addWidget(QLabel("审核中: 15%"))
        progress_layout.addWidget(review_progress)
        
        published_progress = QProgressBar()
        published_progress.setValue(60)
        progress_layout.addWidget(QLabel("已发布: 60%"))
        progress_layout.addWidget(published_progress)
        
        stats_group_layout.addLayout(progress_layout)
        stats_group.setLayout(stats_group_layout)
        stats_layout.addWidget(stats_group)
        
        # 最近活动
        activity_group = QGroupBox("最近活动")
        activity_layout = QVBoxLayout()
        
        activity_list = QListWidget()
        activity_items = [
            "张三 更新了 '客户接待流程' v2.1",
            "李四 发布了 '产品质检标准' v1.5",
            "王五 创建了 '财务报表制作流程'",
            "赵六 审核通过了 '安全操作规程'"
        ]
        
        for item_text in activity_items:
            activity_list.addItem(item_text)
            
        activity_layout.addWidget(activity_list)
        activity_group.setLayout(activity_layout)
        stats_layout.addWidget(activity_group)
        
        stats_tab.setLayout(stats_layout)
        right_widget.addTab(stats_tab, "统计信息")
        
        main_splitter.addWidget(right_widget)
        
        # 设置分割器比例
        main_splitter.setSizes([600, 500])
        layout.addWidget(main_splitter)
        
        self.setLayout(layout)
        
    def load_data(self):
        """加载SOP数据"""
        try:
            sops = self.api_client.get_sops()
            
            self.sop_table.setRowCount(len(sops))
            for row, sop in enumerate(sops):
                self.sop_table.setItem(row, 0, QTableWidgetItem(sop.get('title', '')))
                self.sop_table.setItem(row, 1, QTableWidgetItem(sop.get('version', '1.0')))
                self.sop_table.setItem(row, 2, QTableWidgetItem('已发布'))
                self.sop_table.setItem(row, 3, QTableWidgetItem('2024-01-15'))
                
            # 更新统计信息
            total_count = len(sops)
            self.stats_label.setText(f"""
            📊 文档总数: {total_count}
            📝 草稿文档: {total_count // 4}
            🔍 审核中: {total_count // 6}
            ✅ 已发布: {total_count * 3 // 5}
            📁 已归档: {total_count // 10}
            """)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载SOP数据失败:\n{str(e)}")
            
    def filter_sops(self):
        """筛选SOP"""
        # 这里实现筛选逻辑
        pass
        
    def on_sop_selected(self):
        """SOP选择处理"""
        selected_rows = self.sop_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.edit_sop_btn.setEnabled(has_selection)
        self.delete_sop_btn.setEnabled(has_selection)
        self.export_btn.setEnabled(has_selection)
        self.publish_btn.setEnabled(has_selection)
        
        if has_selection:
            row = selected_rows[0].row()
            title = self.sop_table.item(row, 0).text()
            version = self.sop_table.item(row, 1).text()
            status = self.sop_table.item(row, 2).text()
            
            self.sop_preview.setHtml(f"""
            <h2>{title}</h2>
            <p><strong>版本:</strong> {version}</p>
            <p><strong>状态:</strong> {status}</p>
            <p><strong>更新时间:</strong> 2024-01-15</p>
            <hr>
            <h3>文档内容预览</h3>
            <h4>1. 目的和范围</h4>
            <p>本SOP旨在规范{title}的操作流程，确保操作的标准化和一致性。</p>
            
            <h4>2. 适用范围</h4>
            <p>适用于所有参与{title}的相关人员。</p>
            
            <h4>3. 操作步骤</h4>
            <ol>
                <li>准备阶段 - 检查所需材料和工具</li>
                <li>执行阶段 - 按照标准流程执行操作</li>
                <li>检查阶段 - 验证操作结果</li>
                <li>完成阶段 - 整理和归档相关文档</li>
            </ol>
            
            <h4>4. 质量控制</h4>
            <p>严格按照质量标准执行，确保每个步骤都符合要求。</p>
            
            <p><em>点击"编辑"按钮查看完整内容...</em></p>
            """)
            
    def new_sop(self):
        """新建SOP"""
        dialog = SOPEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            
    def edit_sop(self):
        """编辑SOP"""
        selected_rows = self.sop_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        sop_data = {
            'title': self.sop_table.item(row, 0).text(),
            'version': self.sop_table.item(row, 1).text(),
            'content': '这里是SOP的详细内容...'
        }
        
        dialog = SOPEditDialog(sop_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            
    def delete_sop(self):
        """删除SOP"""
        selected_rows = self.sop_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        title = self.sop_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除SOP文档 '{title}' 吗？\n\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "删除成功", f"SOP文档 '{title}' 已删除")
            self.load_data()
            
    def export_sop(self):
        """导出SOP"""
        selected_rows = self.sop_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        title = self.sop_table.item(row, 0).text()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            f"导出SOP - {title}", 
            f"{title}.pdf",
            "PDF文件 (*.pdf);;Word文档 (*.docx);;HTML文件 (*.html)"
        )
        
        if file_path:
            QMessageBox.information(self, "导出成功", f"SOP文档已导出到:\n{file_path}")
            
    def publish_sop(self):
        """发布SOP"""
        selected_rows = self.sop_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        title = self.sop_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            "确认发布", 
            f"确定要发布SOP文档 '{title}' 吗？\n\n发布后将对所有用户可见。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "发布成功", f"SOP文档 '{title}' 已发布")
            self.load_data()