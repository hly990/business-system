"""
登录对话框
"""
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QMessageBox, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

from ...services.auth_manager import get_auth_manager
from ..components.custom_widgets import CustomLineEdit, CustomButton, LoadingSpinner


class LoginWorker(QThread):
    """登录工作线程"""
    
    login_success = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    
    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password
        self.auth_manager = get_auth_manager()
        
    def run(self):
        """执行登录"""
        try:
            if self.auth_manager.login(self.email, self.password):
                user_data = self.auth_manager.get_current_user()
                self.login_success.emit(user_data)
            else:
                self.login_failed.emit("登录失败")
        except Exception as e:
            self.login_failed.emit(str(e))


class LoginDialog(QDialog):
    """登录对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.auth_manager = get_auth_manager()
        self.login_worker = None
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("用户登录 - SelfMastery B2B系统")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo和标题区域
        self.create_header(main_layout)
        
        # 登录表单
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
        logo_label = QLabel()
        # 这里可以设置实际的logo图片
        logo_label.setText("🏢")
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
        title_label = QLabel("SelfMastery B2B")
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
        subtitle_label = QLabel("业务流程管理系统")
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
        """创建登录表单"""
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
        
        # 记住密码选项
        options_layout = QHBoxLayout()
        
        self.remember_checkbox = QCheckBox("记住密码")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #666;
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
        options_layout.addWidget(self.remember_checkbox)
        
        options_layout.addStretch()
        
        # 忘记密码链接
        self.forgot_password_btn = QPushButton("忘记密码？")
        self.forgot_password_btn.setFlat(True)
        self.forgot_password_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #1976d2;
                font-size: 13px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #1565c0;
            }
        """)
        self.forgot_password_btn.clicked.connect(self.show_forgot_password)
        options_layout.addWidget(self.forgot_password_btn)
        
        form_layout.addRow("", options_layout)
        
        layout.addWidget(form_frame)
        
    def create_buttons(self, layout):
        """创建按钮区域"""
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # 登录按钮
        self.login_btn = CustomButton("登录", "", "primary")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setStyleSheet(self.login_btn.styleSheet() + """
            QPushButton {
                font-size: 16px;
                font-weight: 500;
            }
        """)
        self.login_btn.clicked.connect(self.login)
        button_layout.addWidget(self.login_btn)
        
        # 加载指示器
        self.loading_layout = QHBoxLayout()
        self.loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.loading_spinner = LoadingSpinner(24)
        self.loading_spinner.setVisible(False)
        self.loading_layout.addWidget(self.loading_spinner)
        
        self.loading_label = QLabel("正在登录...")
        self.loading_label.setVisible(False)
        self.loading_label.setStyleSheet("color: #666; font-size: 14px;")
        self.loading_layout.addWidget(self.loading_label)
        
        button_layout.addLayout(self.loading_layout)
        
        # 注册按钮
        self.register_btn = CustomButton("没有账号？立即注册", "", "secondary")
        self.register_btn.setMinimumHeight(40)
        self.register_btn.clicked.connect(self.show_register)
        button_layout.addWidget(self.register_btn)
        
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
        # 回车键登录
        self.email_edit.returnPressed.connect(self.login)
        self.password_edit.returnPressed.connect(self.login)
        
        # 认证管理器信号
        self.auth_manager.login_success.connect(self.on_login_success)
        self.auth_manager.login_failed.connect(self.on_login_failed)
        
    def login(self):
        """执行登录"""
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        
        # 验证输入
        if not email:
            QMessageBox.warning(self, "输入错误", "请输入邮箱地址")
            self.email_edit.setFocus()
            return
            
        if not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            self.password_edit.setFocus()
            return
            
        # 显示加载状态
        self.set_loading_state(True)
        
        # 创建登录工作线程
        self.login_worker = LoginWorker(email, password)
        self.login_worker.login_success.connect(self.on_login_success)
        self.login_worker.login_failed.connect(self.on_login_failed)
        self.login_worker.finished.connect(lambda: self.set_loading_state(False))
        self.login_worker.start()
        
    def set_loading_state(self, loading):
        """设置加载状态"""
        self.login_btn.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        self.email_edit.setEnabled(not loading)
        self.password_edit.setEnabled(not loading)
        self.remember_checkbox.setEnabled(not loading)
        self.forgot_password_btn.setEnabled(not loading)
        
        self.loading_spinner.setVisible(loading)
        self.loading_label.setVisible(loading)
        
        if loading:
            self.login_btn.setText("登录中...")
        else:
            self.login_btn.setText("登录")
            
    def on_login_success(self, user_data):
        """登录成功处理"""
        self.logger.info(f"用户登录成功: {user_data.get('name')}")
        
        # 保存记住密码选项
        if self.remember_checkbox.isChecked():
            # TODO: 实现记住密码功能
            pass
            
        # 关闭对话框
        self.accept()
        
    def on_login_failed(self, error_msg):
        """登录失败处理"""
        self.logger.warning(f"登录失败: {error_msg}")
        QMessageBox.critical(self, "登录失败", error_msg)
        self.password_edit.clear()
        self.password_edit.setFocus()
        
    def show_register(self):
        """显示注册对话框"""
        from .register_dialog import RegisterDialog
        register_dialog = RegisterDialog(self)
        if register_dialog.exec() == QDialog.DialogCode.Accepted:
            # 注册成功，可以自动填入邮箱
            email = register_dialog.get_email()
            if email:
                self.email_edit.setText(email)
                self.password_edit.setFocus()
                
    def show_forgot_password(self):
        """显示忘记密码对话框"""
        from .forgot_password_dialog import ForgotPasswordDialog
        forgot_dialog = ForgotPasswordDialog(self)
        forgot_dialog.exec()
        
    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
            
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.login_worker and self.login_worker.isRunning():
            self.login_worker.terminate()
            self.login_worker.wait()
        event.accept()