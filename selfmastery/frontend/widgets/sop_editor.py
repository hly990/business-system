"""
SOP编辑器组件
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QToolBar, QTabWidget, QFormLayout,
    QGroupBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QColor

from ..ui.components.custom_widgets import (
    CustomButton, CustomLineEdit, CustomTextEdit, CustomComboBox
)
from ..services.data_manager import DataManager


class SOPEditor(QWidget):
    """SOP编辑器组件"""
    
    # 信号定义
    sop_saved = pyqtSignal(dict)
    sop_changed = pyqtSignal(dict)
    
    def __init__(self, sop_data=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = DataManager()
        
        self.sop_data = sop_data or {}
        self.is_modified = False
        
        self.init_ui()
        self.setup_connections()
        self.load_sop_data()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # 左侧：大纲和模板
        self.create_outline_panel(main_splitter)
        
        # 右侧：编辑器和属性
        self.create_editor_panel(main_splitter)
        
        main_splitter.setSizes([250, 600])
        
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        
        # 保存按钮
        save_btn = CustomButton("保存", ":/icons/save.png", "primary")
        save_btn.clicked.connect(self.save_sop)
        self.toolbar.addWidget(save_btn)
        
        self.toolbar.addSeparator()
        
        # 格式化按钮
        bold_btn = CustomButton("B", "", "secondary")
        bold_btn.setFixedSize(30, 30)
        bold_btn.clicked.connect(self.format_bold)
        self.toolbar.addWidget(bold_btn)
        
        italic_btn = CustomButton("I", "", "secondary")
        italic_btn.setFixedSize(30, 30)
        italic_btn.clicked.connect(self.format_italic)
        self.toolbar.addWidget(italic_btn)
        
        underline_btn = CustomButton("U", "", "secondary")
        underline_btn.setFixedSize(30, 30)
        underline_btn.clicked.connect(self.format_underline)
        self.toolbar.addWidget(underline_btn)
        
        self.toolbar.addSeparator()
        
        # 插入按钮
        insert_table_btn = CustomButton("表格", ":/icons/table.png", "secondary")
        insert_table_btn.clicked.connect(self.insert_table)
        self.toolbar.addWidget(insert_table_btn)
        
        insert_image_btn = CustomButton("图片", ":/icons/image.png", "secondary")
        insert_image_btn.clicked.connect(self.insert_image)
        self.toolbar.addWidget(insert_image_btn)
        
    def create_outline_panel(self, parent):
        """创建大纲面板"""
        outline_widget = QWidget()
        outline_layout = QVBoxLayout(outline_widget)
        
        # 标签页
        outline_tabs = QTabWidget()
        outline_layout.addWidget(outline_tabs)
        
        # 大纲标签页
        self.outline_list = QListWidget()
        outline_tabs.addTab(self.outline_list, "大纲")
        
        # 模板标签页
        self.template_list = QListWidget()
        self.load_templates()
        outline_tabs.addTab(self.template_list, "模板")
        
        parent.addWidget(outline_widget)
        
    def create_editor_panel(self, parent):
        """创建编辑器面板"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # 标签页
        self.editor_tabs = QTabWidget()
        editor_layout.addWidget(self.editor_tabs)
        
        # 编辑器标签页
        self.create_editor_tab()
        
        # 属性标签页
        self.create_properties_tab()
        
        # 预览标签页
        self.create_preview_tab()
        
        parent.addWidget(editor_widget)
        
    def create_editor_tab(self):
        """创建编辑器标签页"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # 富文本编辑器
        self.content_editor = QTextEdit()
        self.content_editor.setFont(QFont("Consolas", 11))
        editor_layout.addWidget(self.content_editor)
        
        self.editor_tabs.addTab(editor_widget, "编辑")
        
    def create_properties_tab(self):
        """创建属性标签页"""
        properties_widget = QWidget()
        layout = QFormLayout(properties_widget)
        
        # SOP标题
        self.title_edit = CustomLineEdit()
        layout.addRow("SOP标题:", self.title_edit)
        
        # 关联流程
        self.process_combo = CustomComboBox()
        layout.addRow("关联流程:", self.process_combo)
        
        # 文档类型
        self.type_combo = CustomComboBox()
        self.type_combo.addItems(["操作手册", "工作指南", "质量标准", "安全规范", "其他"])
        layout.addRow("文档类型:", self.type_combo)
        
        # 版本号
        self.version_edit = CustomLineEdit()
        self.version_edit.setText("1.0")
        layout.addRow("版本号:", self.version_edit)
        
        # 作者
        self.author_edit = CustomLineEdit()
        layout.addRow("作者:", self.author_edit)
        
        # 审核人
        self.reviewer_edit = CustomLineEdit()
        layout.addRow("审核人:", self.reviewer_edit)
        
        # 状态
        self.status_combo = CustomComboBox()
        self.status_combo.addItems(["草稿", "审核中", "已发布", "已归档"])
        layout.addRow("状态:", self.status_combo)
        
        # 标签
        self.tags_edit = CustomLineEdit()
        self.tags_edit.setPlaceholderText("用逗号分隔多个标签")
        layout.addRow("标签:", self.tags_edit)
        
        self.editor_tabs.addTab(properties_widget, "属性")
        
    def create_preview_tab(self):
        """创建预览标签页"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # 预览区域
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        preview_layout.addWidget(self.preview_area)
        
        self.editor_tabs.addTab(preview_widget, "预览")
        
    def setup_connections(self):
        """设置信号连接"""
        # 内容变化
        self.content_editor.textChanged.connect(self.on_content_changed)
        self.title_edit.textChanged.connect(self.on_data_changed)
        self.type_combo.currentTextChanged.connect(self.on_data_changed)
        self.version_edit.textChanged.connect(self.on_data_changed)
        self.status_combo.currentTextChanged.connect(self.on_data_changed)
        
        # 标签页切换
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        
        # 模板选择
        self.template_list.itemDoubleClicked.connect(self.apply_template)
        
    def load_sop_data(self):
        """加载SOP数据"""
        if self.sop_data:
            self.title_edit.setText(self.sop_data.get('title', ''))
            self.content_editor.setHtml(self.sop_data.get('content', ''))
            self.version_edit.setText(self.sop_data.get('version', '1.0'))
            self.author_edit.setText(self.sop_data.get('author', ''))
            self.reviewer_edit.setText(self.sop_data.get('reviewer', ''))
            
            # 设置类型
            doc_type = self.sop_data.get('type', '操作手册')
            type_index = self.type_combo.findText(doc_type)
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)
                
            # 设置状态
            status = self.sop_data.get('status', '草稿')
            status_index = self.status_combo.findText(status)
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)
                
            # 设置标签
            tags = self.sop_data.get('tags', [])
            if tags:
                self.tags_edit.setText(', '.join(tags))
                
        # 加载流程列表
        self.load_processes()
        
        # 更新大纲
        self.update_outline()
        
    def load_processes(self):
        """加载流程列表"""
        self.process_combo.clear()
        self.process_combo.addItem("无关联流程", None)
        
        try:
            processes = self.data_manager.get_processes()
            for process in processes:
                self.process_combo.addItem(process.get('name', ''), process.get('id'))
                
            # 设置当前流程
            if self.sop_data.get('process_id'):
                for i in range(self.process_combo.count()):
                    if self.process_combo.itemData(i) == self.sop_data.get('process_id'):
                        self.process_combo.setCurrentIndex(i)
                        break
        except Exception as e:
            self.logger.error(f"加载流程列表失败: {e}")
            
    def load_templates(self):
        """加载模板列表"""
        templates = [
            "操作手册模板",
            "工作指南模板",
            "质量标准模板",
            "安全规范模板",
            "培训教程模板"
        ]
        
        for template in templates:
            item = QListWidgetItem(template)
            self.template_list.addItem(item)
            
    def update_outline(self):
        """更新大纲"""
        self.outline_list.clear()
        
        # 解析内容中的标题
        content = self.content_editor.toPlainText()
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#'):
                # Markdown风格标题
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                if title:
                    item = QListWidgetItem('  ' * (level - 1) + title)
                    item.setData(Qt.ItemDataRole.UserRole, i)
                    self.outline_list.addItem(item)
                    
    def apply_template(self, item):
        """应用模板"""
        template_name = item.text()
        template_content = self.get_template_content(template_name)
        
        if template_content:
            self.content_editor.setHtml(template_content)
            self.on_content_changed()
            
    def get_template_content(self, template_name):
        """获取模板内容"""
        templates = {
            "操作手册模板": """
            <h1>操作手册</h1>
            <h2>1. 概述</h2>
            <p>本操作手册描述了...</p>
            
            <h2>2. 操作步骤</h2>
            <h3>2.1 准备工作</h3>
            <p>在开始操作前，请确保...</p>
            
            <h3>2.2 具体操作</h3>
            <ol>
                <li>第一步：...</li>
                <li>第二步：...</li>
                <li>第三步：...</li>
            </ol>
            
            <h2>3. 注意事项</h2>
            <ul>
                <li>注意事项1</li>
                <li>注意事项2</li>
            </ul>
            
            <h2>4. 常见问题</h2>
            <p>Q: 问题1？</p>
            <p>A: 答案1</p>
            """,
            "工作指南模板": """
            <h1>工作指南</h1>
            <h2>目的</h2>
            <p>本指南旨在...</p>
            
            <h2>适用范围</h2>
            <p>适用于...</p>
            
            <h2>工作流程</h2>
            <p>详细的工作流程说明...</p>
            
            <h2>质量要求</h2>
            <p>质量标准和要求...</p>
            """
        }
        
        return templates.get(template_name, "")
        
    def format_bold(self):
        """加粗格式"""
        cursor = self.content_editor.textCursor()
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold)
        cursor.mergeCharFormat(format)
        
    def format_italic(self):
        """斜体格式"""
        cursor = self.content_editor.textCursor()
        format = QTextCharFormat()
        format.setFontItalic(True)
        cursor.mergeCharFormat(format)
        
    def format_underline(self):
        """下划线格式"""
        cursor = self.content_editor.textCursor()
        format = QTextCharFormat()
        format.setFontUnderline(True)
        cursor.mergeCharFormat(format)
        
    def insert_table(self):
        """插入表格"""
        table_html = """
        <table border="1" style="border-collapse: collapse;">
            <tr>
                <th>列1</th>
                <th>列2</th>
                <th>列3</th>
            </tr>
            <tr>
                <td>数据1</td>
                <td>数据2</td>
                <td>数据3</td>
            </tr>
        </table>
        """
        self.content_editor.insertHtml(table_html)
        
    def insert_image(self):
        """插入图片"""
        # TODO: 实现图片插入功能
        image_html = '<img src="image_placeholder.png" alt="图片描述" style="max-width: 100%;">'
        self.content_editor.insertHtml(image_html)
        
    def on_content_changed(self):
        """内容变化处理"""
        self.update_outline()
        self.on_data_changed()
        
    def on_data_changed(self):
        """数据变化处理"""
        self.is_modified = True
        self.sop_changed.emit(self.get_sop_data())
        
    def on_tab_changed(self, index):
        """标签页变化处理"""
        if index == 2:  # 预览标签页
            self.update_preview()
            
    def update_preview(self):
        """更新预览"""
        # 生成完整的HTML预览
        title = self.title_edit.text()
        content = self.content_editor.toHtml()
        version = self.version_edit.text()
        author = self.author_edit.text()
        
        preview_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #1976d2; border-bottom: 2px solid #1976d2; }}
                h2 {{ color: #424242; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .header {{ background-color: #f5f5f5; padding: 10px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{title}</h1>
                <p><strong>版本:</strong> {version} | <strong>作者:</strong> {author}</p>
            </div>
            {content}
        </body>
        </html>
        """
        
        self.preview_area.setHtml(preview_html)
        
    def get_sop_data(self):
        """获取SOP数据"""
        tags = [tag.strip() for tag in self.tags_edit.text().split(',') if tag.strip()]
        
        data = {
            'title': self.title_edit.text(),
            'content': self.content_editor.toHtml(),
            'process_id': self.process_combo.currentData(),
            'type': self.type_combo.currentText(),
            'version': self.version_edit.text(),
            'author': self.author_edit.text(),
            'reviewer': self.reviewer_edit.text(),
            'status': self.status_combo.currentText(),
            'tags': tags
        }
        
        # 添加ID（如果是编辑现有SOP）
        if self.sop_data.get('id'):
            data['id'] = self.sop_data['id']
            
        return data
        
    def save_sop(self):
        """保存SOP"""
        try:
            sop_data = self.get_sop_data()
            
            if sop_data.get('id'):
                # 更新现有SOP
                updated_sop = self.data_manager.update_sop(
                    sop_data['id'], sop_data
                )
            else:
                # 创建新SOP
                updated_sop = self.data_manager.create_sop(sop_data)
                
            self.sop_data = updated_sop
            self.is_modified = False
            self.sop_saved.emit(updated_sop)
            
            self.logger.info(f"SOP保存成功: {updated_sop.get('title')}")
            
        except Exception as e:
            self.logger.error(f"保存SOP失败: {e}")
            
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        return self.is_modified
        
    def save(self):
        """保存"""
        self.save_sop()
        
    def undo(self):
        """撤销"""
        self.content_editor.undo()
        
    def redo(self):
        """重做"""
        self.content_editor.redo()