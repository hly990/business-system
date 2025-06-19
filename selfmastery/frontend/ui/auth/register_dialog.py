"""
注册对话框
"""
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

from ...services.auth_manager import get_auth_manager
from ..components.custom_widgets import CustomLineEdit, CustomButton, LoadingSpinner


class RegisterWorker(QThread):
    """注册工作线程"""
    
    register_success = pyqtSignal()
    register_failed = pyqtSignal(str)
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.auth_manager = get_auth_manager()
        
    def run(self):
        """执行注册"""
        try:
            if self.auth_manager.register(self.user_data):
                self.register_success.emit()
            else:
                self.register_failed.emit("注册失败")
        except Exception as e:
            self.register_failed.emit(str(e))


class RegisterDialog(QDialog):
    """注册对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.auth_manager = get_auth_manager()
        self.register_worker = None
        self.registered_email = None
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("用户注册 - SelfMastery B2B系统")
        self.setFixedSize(450, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo和标题区域
        self.create_header(main_layout)
        
        # 注册表单
        self.create_form(main_layout)
        
        # 按钮区域
        self.create_buttons(main_layout)
        
        # 底部链接
        self.create_footer(main_layout)
        
        # 应用样式
        self.apply_styles()
        
    def create_header(self, layout):
        """创建头部区域"""
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo
        logo_label = QLabel("👤")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #1976d2;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(logo_label)
        
        # 标题
        title_label = QLabel("创建新账户")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }
        """)
        header_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("加入SelfMastery B2B业务管理平台")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                margin-bottom: 20px;
            }
        """)
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
    def create_form(self, layout):
        """创建注册表单"""
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        
        # 姓名输入
        name_label = QLabel("姓名:")
        name_label.setStyleSheet("font-weight: 500; color: #333;")
        self.name_edit = CustomLineEdit("请输入您的姓名")
        self.name_edit.setMinimumHeight(40)
        form_layout.addRow(name_label, self.name_edit)
        
        # 邮箱输入
        email_label = QLabel("邮箱地址:")
        email_label.setStyleSheet("font-weight: 500; color: #333;")
        self.email_edit = CustomLineEdit("请输入邮箱地址")
        self.email_edit.setMinimumHeight(40)
        form_layout.addRow(email_label, self.email_edit)
        
        # 密码输入
        password_label = QLabel("密码:")
        password_label.setStyleSheet("font-weight: 500; color: #333;")
        self.password_edit = CustomLineEdit("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(40)
        form_layout.addRow(password_label, self.password_edit)
        
        # 确认密码输入
        confirm_password_label = QLabel("确认密码:")
        confirm_password_label.setStyleSheet("font-weight: 500; color: #333;")
        self.confirm_password_edit = CustomLineEdit("请再次输入密码")
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setMinimumHeight(40)
        form_layout.addRow(confirm_password_label, self.confirm_password_edit)
        
        # 公司名称输入
        company_label = QLabel("公司名称:")
        company_label.setStyleSheet("font-weight: 500; color: #333;")
        self.company_edit = CustomLineEdit("请输入公司名称（可选）")
        self.company_edit.setMinimumHeight(40)
        form_layout.addRow(company_label, self.company_edit)
        
        # 职位输入
        position_label = QLabel("职位:")
        position_label.setStyleSheet("font-weight: 500; color: #333;")
        self.position_edit = CustomLineEdit("请输入您的职位（可选）")
        self.position_edit.setMinimumHeight(40)
        form_layout.addRow(position_label, self.position_edit)
        
        # 服务条款同意
        self.terms_checkbox = QCheckBox("我已阅读并同意《服务条款》和《隐私政策》")
        self.terms_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #666;
                margin-top: 10px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #1976d2;
                border-radius: 3px;
                background-color: #1976d2;
                image: url(:/icons/check.png);
            }
        """)
        form_layout.addRow("", self.terms_checkbox)
        
        layout.addWidget(form_frame)
        
    def create_buttons(self, layout):
        """创建按钮区域"""
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # 注册按钮
        self.register_btn = CustomButton("创建账户", "", "primary")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.setStyleSheet(self.register_btn.styleSheet() + """
            QPushButton {
                font-size: 16px;
                font-weight: 500;
            }
        """)
        self.register_btn.clicked.connect(self.register)
        button_layout.addWidget(self.register_btn)
        
        # 加载指示器
        self.loading_layout = QHBoxLayout()
        self.loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.loading_spinner = LoadingSpinner(24)
        self.loading_spinner.setVisible(False)
        self.loading_layout.addWidget(self.loading_spinner)
        
        self.loading_label = QLabel("正在注册...")
        self.loading_label.setVisible(False)
        self.loading_label.setStyleSheet("color: #666; font-size: 14px;")
        self.loading_layout.addWidget(self.loading_label)
        
        button_layout.addLayout(self.loading_layout)
        
        # 登录按钮
        self.login_btn = CustomButton("已有账号？立即登录", "", "secondary")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self.show_login)
        button_layout.addWidget(self.login_btn)
        
        layout.addLayout(button_layout)
        
    def create_footer(self, layout):
        """创建底部区域"""
        footer_layout = QVBoxLayout()
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #e0e0e0;")
        footer_layout.addWidget(separator)
        
        # 版权信息
        copyright_label = QLabel("© 2024 SelfMastery. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #999;
                margin-top: 10px;
            }
        """)
        footer_layout.addWidget(copyright_label)
        
        layout.addLayout(footer_layout)
        
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
        """)
        
    def setup_connections(self):
        """设置信号连接"""
        # 回车键注册
        self.confirm_password_edit.returnPressed.connect(self.register)
        
        # 密码确认验证
        self.confirm_password_edit.textChanged.connect(self.validate_password_match)
        
    def validate_input(self):
        """验证输入"""
        # 检查必填字段
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "输入错误", "请输入您的姓名")
            self.name_edit.setFocus()
            return False
            
        if not self.email_edit.text().strip():
            QMessageBox.warning(self, "输入错误", "请输入邮箱地址")
            self.email_edit.setFocus()
            return False
            
        # 验证邮箱格式
        email = self.email_edit.text().strip()
        if '@' not in email or '.' not in email:
            QMessageBox.warning(self, "输入错误", "请输入有效的邮箱地址")
            self.email_edit.setFocus()
            return False
            
        # 检查密码
        password = self.password_edit.text()
        if len(password) < 6:
            QMessageBox.warning(self, "输入错误", "密码长度至少为6位")
            self.password_edit.setFocus()
            return False
            
        # 检查密码确认
        if password != self.confirm_password_edit.text():
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            self.confirm_password_edit.setFocus()
            return False
            
        # 检查服务条款同意
        if not self.terms_checkbox.isChecked():
            QMessageBox.warning(self, "输入错误", "请先同意服务条款和隐私政策")
            return False
            
        return True
        
    def validate_password_match(self):
        """验证密码匹配"""
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        if confirm_password and password != confirm_password:
            self.confirm_password_edit.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #f44336;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 14px;
                    background-color: white;
                }
            """)
        else:
            self.confirm_password_edit.setStyleSheet("")
            
    def register(self):
        """执行注册"""
        if not self.validate_input():
            return
            
        # 准备用户数据
        user_data = {
            'name': self.name_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'password': self.password_edit.text(),
            'company': self.company_edit.text().strip(),
            'position': self.position_edit.text().strip(),
            'role': 'user'
        }
        
        # 显示加载状态
        self.set_loading_state(True)
        
        # 创建注册工作线程
        self.register_worker = RegisterWorker(user_data)
        self.register_worker.register_success.connect(self.on_register_success)
        self.register_worker.register_failed.connect(self.on_register_failed)
        self.register_worker.finished.connect(lambda: self.set_loading_state(False))
        self.register_worker.start()
        
    def set_loading_state(self, loading):
        """设置加载状态"""
        self.register_btn.setEnabled(not loading)
        self.login_btn.setEnabled(not loading)
        self.name_edit.setEnabled(not loading)
        self.email_edit.setEnabled(not loading)
        self.password_edit.setEnabled(not loading)
        self.confirm_password_edit.setEnabled(not loading)
        self.company_edit.setEnabled(not loading)
        self.position_edit.setEnabled(not loading)
        self.terms_checkbox.setEnabled(not loading)
        
        self.loading_spinner.setVisible(loading)
        self.loading_label.setVisible(loading)
        
        if loading:
            self.register_btn.setText("注册中...")
        else:
            self.register_btn.setText("创建账户")
            
    def on_register_success(self):
        """注册成功处理"""
        self.logger.info("用户注册成功")
        self.registered_email = self.email_edit.text().strip()
        
        QMessageBox.information(
            self, "注册成功", 
            "账户创建成功！\n请使用您的邮箱和密码登录。"
        )
        
        # 关闭对话框
        self.accept()
        
    def on_register_failed(self, error_msg):
        """注册失败处理"""
        self.logger.warning(f"注册失败: {error_msg}")
        QMessageBox.critical(self, "注册失败", error_msg)
        
    def show_login(self):
        """显示登录对话框"""
        self.reject()
        
    def get_email(self):
        """获取注册的邮箱（用于登录对话框自动填入）"""
        return self.registered_email
        
    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
            
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.register_worker and self.register_worker.isRunning():
            self.register_worker.terminate()
            self.register_worker.wait()
        event.accept()