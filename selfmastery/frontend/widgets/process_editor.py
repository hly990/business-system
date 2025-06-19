"""
流程编辑器组件
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel,
    QToolBar, QTabWidget, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ..ui.components.custom_widgets import (
    CustomButton, CustomLineEdit, CustomTextEdit,
    CustomComboBox, CustomSpinBox
)
from ..services.data_manager import DataManager


class ProcessEditor(QWidget):
    """流程编辑器组件"""
    
    # 信号定义
    process_saved = pyqtSignal(dict)
    process_changed = pyqtSignal(dict)
    
    def __init__(self, process_data=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = DataManager()
        
        self.process_data = process_data or {}
        self.is_modified = False
        
        self.init_ui()
        self.setup_connections()
        self.load_process_data()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # 左侧：流程步骤树
        self.create_steps_panel(main_splitter)
        
        # 右侧：属性编辑器
        self.create_properties_panel(main_splitter)
        
        main_splitter.setSizes([300, 500])
        
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        
        # 保存按钮
        save_btn = CustomButton("保存", ":/icons/save.png", "primary")
        save_btn.clicked.connect(self.save_process)
        self.toolbar.addWidget(save_btn)
        
        self.toolbar.addSeparator()
        
        # 添加步骤按钮
        add_step_btn = CustomButton("添加步骤", ":/icons/add.png", "secondary")
        add_step_btn.clicked.connect(self.add_step)
        self.toolbar.addWidget(add_step_btn)
        
        # 删除步骤按钮
        delete_step_btn = CustomButton("删除步骤", ":/icons/delete.png", "danger")
        delete_step_btn.clicked.connect(self.delete_step)
        self.toolbar.addWidget(delete_step_btn)
        
    def create_steps_panel(self, parent):
        """创建步骤面板"""
        steps_widget = QWidget()
        steps_layout = QVBoxLayout(steps_widget)
        
        # 标题
        title_label = QLabel("流程步骤")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        steps_layout.addWidget(title_label)
        
        # 步骤树
        self.steps_tree = QTreeWidget()
        self.steps_tree.setHeaderLabels(["步骤", "负责人", "状态"])
        self.steps_tree.setRootIsDecorated(False)
        steps_layout.addWidget(self.steps_tree)
        
        parent.addWidget(steps_widget)
        
    def create_properties_panel(self, parent):
        """创建属性面板"""
        properties_widget = QWidget()
        properties_layout = QVBoxLayout(properties_widget)
        
        # 标签页
        self.tab_widget = QTabWidget()
        properties_layout.addWidget(self.tab_widget)
        
        # 基本信息标签页
        self.create_basic_info_tab()
        
        # 步骤详情标签页
        self.create_step_details_tab()
        
        # SOP文档标签页
        self.create_sop_tab()
        
        parent.addWidget(properties_widget)
        
    def create_basic_info_tab(self):
        """创建基本信息标签页"""
        basic_widget = QWidget()
        layout = QFormLayout(basic_widget)
        
        # 流程名称
        self.name_edit = CustomLineEdit()
        layout.addRow("流程名称:", self.name_edit)
        
        # 所属系统
        self.system_combo = CustomComboBox()
        layout.addRow("所属系统:", self.system_combo)
        
        # 流程描述
        self.description_edit = CustomTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addRow("流程描述:", self.description_edit)
        
        # 流程状态
        self.status_combo = CustomComboBox()
        self.status_combo.addItems(["草稿", "激活", "停用", "归档"])
        layout.addRow("流程状态:", self.status_combo)
        
        # 优先级
        self.priority_spin = CustomSpinBox()
        self.priority_spin.setRange(1, 5)
        self.priority_spin.setValue(3)
        layout.addRow("优先级:", self.priority_spin)
        
        # 预估时间
        self.duration_spin = CustomSpinBox()
        self.duration_spin.setRange(1, 9999)
        self.duration_spin.setSuffix(" 分钟")
        layout.addRow("预估时间:", self.duration_spin)
        
        self.tab_widget.addTab(basic_widget, "基本信息")
        
    def create_step_details_tab(self):
        """创建步骤详情标签页"""
        step_widget = QWidget()
        layout = QVBoxLayout(step_widget)
        
        # 步骤信息组
        step_group = QGroupBox("步骤信息")
        step_form = QFormLayout(step_group)
        
        self.step_name_edit = CustomLineEdit()
        step_form.addRow("步骤名称:", self.step_name_edit)
        
        self.step_description_edit = CustomTextEdit()
        self.step_description_edit.setMaximumHeight(80)
        step_form.addRow("步骤描述:", self.step_description_edit)
        
        self.step_role_edit = CustomLineEdit()
        step_form.addRow("负责角色:", self.step_role_edit)
        
        self.step_duration_spin = CustomSpinBox()
        self.step_duration_spin.setRange(1, 999)
        self.step_duration_spin.setSuffix(" 分钟")
        step_form.addRow("执行时间:", self.step_duration_spin)
        
        layout.addWidget(step_group)
        layout.addStretch()
        
        self.tab_widget.addTab(step_widget, "步骤详情")
        
    def create_sop_tab(self):
        """创建SOP标签页"""
        sop_widget = QWidget()
        layout = QVBoxLayout(sop_widget)
        
        # SOP选择
        sop_layout = QHBoxLayout()
        self.sop_combo = CustomComboBox()
        sop_layout.addWidget(QLabel("关联SOP:"))
        sop_layout.addWidget(self.sop_combo)
        
        create_sop_btn = CustomButton("创建SOP", "", "secondary")
        create_sop_btn.clicked.connect(self.create_sop)
        sop_layout.addWidget(create_sop_btn)
        
        layout.addLayout(sop_layout)
        
        # SOP预览
        self.sop_preview = QTextEdit()
        self.sop_preview.setReadOnly(True)
        layout.addWidget(self.sop_preview)
        
        self.tab_widget.addTab(sop_widget, "SOP文档")
        
    def setup_connections(self):
        """设置信号连接"""
        # 步骤树选择变化
        self.steps_tree.itemSelectionChanged.connect(self.on_step_selection_changed)
        
        # 表单字段变化
        self.name_edit.textChanged.connect(self.on_data_changed)
        self.description_edit.textChanged.connect(self.on_data_changed)
        self.status_combo.currentTextChanged.connect(self.on_data_changed)
        self.priority_spin.valueChanged.connect(self.on_data_changed)
        self.duration_spin.valueChanged.connect(self.on_data_changed)
        
    def load_process_data(self):
        """加载流程数据"""
        if self.process_data:
            # 加载基本信息
            self.name_edit.setText(self.process_data.get('name', ''))
            self.description_edit.setPlainText(self.process_data.get('description', ''))
            
            # 设置状态
            status_map = {'draft': 0, 'active': 1, 'inactive': 2, 'archived': 3}
            status_index = status_map.get(self.process_data.get('status', 'draft'), 0)
            self.status_combo.setCurrentIndex(status_index)
            
            self.priority_spin.setValue(self.process_data.get('priority', 3))
            self.duration_spin.setValue(self.process_data.get('estimated_duration', 60))
            
            # 加载步骤
            self.load_process_steps()
            
        # 加载系统列表
        self.load_systems()
        
        # 加载SOP列表
        self.load_sops()
        
    def load_process_steps(self):
        """加载流程步骤"""
        self.steps_tree.clear()
        
        # 从数据管理器获取步骤数据
        try:
            steps = self.data_manager.get_process_steps(self.process_data.get('id'))
            for step in steps:
                item = QTreeWidgetItem([
                    step.get('name', ''),
                    step.get('responsible_role', ''),
                    '必需' if step.get('is_required', True) else '可选'
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, step)
                self.steps_tree.addTopLevelItem(item)
        except Exception as e:
            self.logger.error(f"加载流程步骤失败: {e}")
            
    def load_systems(self):
        """加载系统列表"""
        self.system_combo.clear()
        try:
            systems = self.data_manager.get_systems()
            for system in systems:
                self.system_combo.addItem(system.get('name', ''), system.get('id'))
                
            # 设置当前系统
            if self.process_data.get('system_id'):
                for i in range(self.system_combo.count()):
                    if self.system_combo.itemData(i) == self.process_data.get('system_id'):
                        self.system_combo.setCurrentIndex(i)
                        break
        except Exception as e:
            self.logger.error(f"加载系统列表失败: {e}")
            
    def load_sops(self):
        """加载SOP列表"""
        self.sop_combo.clear()
        self.sop_combo.addItem("无关联SOP", None)
        
        try:
            sops = self.data_manager.get_sops()
            for sop in sops:
                self.sop_combo.addItem(sop.get('title', ''), sop.get('id'))
                
            # 设置当前SOP
            if self.process_data.get('sop_id'):
                for i in range(self.sop_combo.count()):
                    if self.sop_combo.itemData(i) == self.process_data.get('sop_id'):
                        self.sop_combo.setCurrentIndex(i)
                        break
        except Exception as e:
            self.logger.error(f"加载SOP列表失败: {e}")
            
    def add_step(self):
        """添加步骤"""
        step_data = {
            'name': '新步骤',
            'description': '',
            'responsible_role': '',
            'estimated_duration': 30,
            'is_required': True,
            'step_order': self.steps_tree.topLevelItemCount() + 1
        }
        
        item = QTreeWidgetItem([
            step_data['name'],
            step_data['responsible_role'],
            '必需' if step_data['is_required'] else '可选'
        ])
        item.setData(0, Qt.ItemDataRole.UserRole, step_data)
        self.steps_tree.addTopLevelItem(item)
        
        # 选择新添加的步骤
        self.steps_tree.setCurrentItem(item)
        self.on_data_changed()
        
    def delete_step(self):
        """删除步骤"""
        current_item = self.steps_tree.currentItem()
        if current_item:
            index = self.steps_tree.indexOfTopLevelItem(current_item)
            self.steps_tree.takeTopLevelItem(index)
            self.on_data_changed()
            
    def on_step_selection_changed(self):
        """步骤选择变化处理"""
        current_item = self.steps_tree.currentItem()
        if current_item:
            step_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if step_data:
                # 更新步骤详情表单
                self.step_name_edit.setText(step_data.get('name', ''))
                self.step_description_edit.setPlainText(step_data.get('description', ''))
                self.step_role_edit.setText(step_data.get('responsible_role', ''))
                self.step_duration_spin.setValue(step_data.get('estimated_duration', 30))
                
    def on_data_changed(self):
        """数据变化处理"""
        self.is_modified = True
        self.process_changed.emit(self.get_process_data())
        
    def get_process_data(self):
        """获取流程数据"""
        status_map = {0: 'draft', 1: 'active', 2: 'inactive', 3: 'archived'}
        
        data = {
            'name': self.name_edit.text(),
            'description': self.description_edit.toPlainText(),
            'system_id': self.system_combo.currentData(),
            'status': status_map.get(self.status_combo.currentIndex(), 'draft'),
            'priority': self.priority_spin.value(),
            'estimated_duration': self.duration_spin.value(),
            'sop_id': self.sop_combo.currentData()
        }
        
        # 添加ID（如果是编辑现有流程）
        if self.process_data.get('id'):
            data['id'] = self.process_data['id']
            
        return data
        
    def save_process(self):
        """保存流程"""
        try:
            process_data = self.get_process_data()
            
            if process_data.get('id'):
                # 更新现有流程
                updated_process = self.data_manager.update_process(
                    process_data['id'], process_data
                )
            else:
                # 创建新流程
                updated_process = self.data_manager.create_process(process_data)
                
            self.process_data = updated_process
            self.is_modified = False
            self.process_saved.emit(updated_process)
            
            self.logger.info(f"流程保存成功: {updated_process.get('name')}")
            
        except Exception as e:
            self.logger.error(f"保存流程失败: {e}")
            
    def create_sop(self):
        """创建SOP"""
        # TODO: 打开SOP编辑器
        pass
        
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        return self.is_modified
        
    def save(self):
        """保存"""
        self.save_process()
        
    def undo(self):
        """撤销"""
        # TODO: 实现撤销功能
        pass
        
    def redo(self):
        """重做"""
        # TODO: 实现重做功能
        pass