"""
SelfMastery B2B业务系统 - PyQt6桌面应用入口
"""
import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QSplashScreen, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QFont

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_pyqt_settings, get_app_settings
from frontend.ui.main_window import MainWindow
from frontend.styles.themes import get_theme_manager
from frontend.services.monitoring import (
    init_frontend_sentry_monitoring,
    install_exception_handler,
    capture_frontend_exception,
    add_frontend_breadcrumb
)


class SplashScreen(QSplashScreen):
    """启动画面"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(500, 350)
        
        # 创建启动画面内容
        pixmap = QPixmap(500, 350)
        pixmap.fill(Qt.GlobalColor.white)
        self.setPixmap(pixmap)
        
        # 显示启动信息
        self.showMessage(
            "正在启动SelfMastery B2B业务系统...",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            Qt.GlobalColor.black
        )
        
        # 应用样式
        self.setStyleSheet("""
            QSplashScreen {
                background-color: white;
                border: 2px solid #1976d2;
                border-radius: 10px;
            }
        """)


class Application:
    """应用程序类"""
    
    def __init__(self):
        # 创建QApplication实例
        self.app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app_settings = get_app_settings()
        self.app.setApplicationName(app_settings.APP_NAME)
        self.app.setApplicationVersion(app_settings.APP_VERSION)
        self.app.setOrganizationName("SelfMastery")
        self.app.setOrganizationDomain("selfmastery.com")
        
        # 设置应用程序图标
        self.app.setWindowIcon(QIcon(":/icons/app_icon.png"))
        
        # 获取设置
        self.pyqt_settings = get_pyqt_settings()
        self.app_settings = app_settings
        
        # 初始化组件
        self.main_window = None
        self.splash = None
        self.theme_manager = get_theme_manager()
        
        # 创建必要的目录
        self.create_directories()
        
        # 设置日志
        self.setup_logging()
        
        # 初始化 Sentry 监控
        self.setup_monitoring()
        
        # 设置字体
        self.setup_fonts()
        
        # 设置样式
        self.setup_styles()
        
    def create_directories(self):
        """创建必要的目录"""
        directories = [
            "logs",
            self.pyqt_settings.LOCAL_DATA_DIR,
            self.pyqt_settings.CACHE_DIR,
            "frontend/resources/icons",
            "frontend/resources/images",
            "frontend/resources/fonts"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def setup_logging(self):
        """设置日志系统"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_level = logging.DEBUG if self.app_settings.DEBUG else logging.INFO
        
        # 配置根日志记录器
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/application.log', encoding='utf-8')
            ]
        )
        
        # 创建应用程序日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"启动 {self.app_settings.APP_NAME} v{self.app_settings.APP_VERSION}")
        
    def setup_monitoring(self):
        """设置监控系统"""
        try:
            # 初始化 Sentry 监控
            init_frontend_sentry_monitoring()
            
            # 安装全局异常处理器
            install_exception_handler()
            
            # 添加启动面包屑
            add_frontend_breadcrumb(
                message="应用程序启动",
                category="lifecycle",
                data={"version": self.app_settings.APP_VERSION}
            )
            
            self.logger.info("监控系统初始化完成")
            
        except Exception as e:
            self.logger.error(f"监控系统初始化失败: {e}")
        
    def setup_fonts(self):
        """设置字体"""
        # 设置默认字体
        font = QFont(self.pyqt_settings.FONT_FAMILY, self.pyqt_settings.FONT_SIZE)
        self.app.setFont(font)
        
        # 加载自定义字体
        font_paths = [
            "frontend/resources/fonts/SourceHanSansCN-Regular.otf",
            "frontend/resources/fonts/SourceHanSansCN-Bold.otf"
        ]
        
        for font_path in font_paths:
            if Path(font_path).exists():
                font_id = self.app.addApplicationFont(font_path)
                if font_id != -1:
                    font_families = self.app.fontFamilies(font_id)
                    self.logger.info(f"加载字体: {font_families}")
                    
    def setup_styles(self):
        """设置样式"""
        # 应用默认主题
        default_theme = self.pyqt_settings.THEME
        self.theme_manager.apply_theme(self.app, default_theme)
        
    def show_splash_screen(self):
        """显示启动画面"""
        if self.pyqt_settings.SHOW_SPLASH_SCREEN:
            self.splash = SplashScreen()
            self.splash.show()
            
            # 处理事件以显示启动画面
            self.app.processEvents()
            
            # 设置定时器关闭启动画面
            QTimer.singleShot(self.pyqt_settings.SPLASH_TIMEOUT, self.show_main_window)
        else:
            self.show_main_window()
            
    def show_main_window(self):
        """显示主窗口"""
        try:
            # 关闭启动画面
            if self.splash:
                self.splash.close()
                self.splash = None
                
            # 创建主窗口
            self.main_window = MainWindow()
            
            # 连接信号
            self.setup_main_window_connections()
            
            # 显示主窗口
            self.main_window.show()
            
            # 如果是最大化启动
            if self.pyqt_settings.START_MAXIMIZED:
                self.main_window.showMaximized()
                
            self.logger.info("主窗口显示完成")
            
        except Exception as e:
            self.logger.error(f"显示主窗口失败: {e}")
            
            # 发送到 Sentry
            try:
                capture_frontend_exception(e)
            except Exception as sentry_error:
                self.logger.error(f"Sentry 异常捕获失败: {sentry_error}")
            
            self.show_error_message("启动失败", f"无法显示主窗口: {e}")
            sys.exit(1)
            
    def setup_main_window_connections(self):
        """设置主窗口信号连接"""
        if self.main_window:
            # 连接主题变更信号
            self.theme_manager.theme_changed.connect(self.on_theme_changed)
            
    def on_theme_changed(self, theme_name):
        """主题变更处理"""
        self.logger.info(f"主题已切换到: {theme_name}")
        
    def show_error_message(self, title, message):
        """显示错误消息"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """全局异常处理"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 忽略键盘中断
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        # 记录异常
        self.logger.error(
            "未捕获的异常",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # 发送到 Sentry
        try:
            capture_frontend_exception(exc_value)
        except Exception as e:
            self.logger.error(f"Sentry 异常捕获失败: {e}")
        
        # 显示错误对话框
        error_msg = f"发生未预期的错误:\n{exc_type.__name__}: {exc_value}"
        self.show_error_message("系统错误", error_msg)
        
    def cleanup(self):
        """清理资源"""
        try:
            if self.main_window:
                self.main_window.cleanup()
                
            self.logger.info("应用程序清理完成")
            
        except Exception as e:
            self.logger.error(f"清理资源时发生错误: {e}")
            
    def run(self):
        """运行应用程序"""
        try:
            # 设置全局异常处理
            sys.excepthook = self.handle_exception
            
            # 显示启动画面
            self.show_splash_screen()
            
            # 运行事件循环
            exit_code = self.app.exec()
            
            # 清理资源
            self.cleanup()
            
            return exit_code
            
        except Exception as e:
            self.logger.error(f"运行应用程序时发生错误: {e}")
            
            # 发送到 Sentry
            try:
                capture_frontend_exception(e)
            except Exception as sentry_error:
                self.logger.error(f"Sentry 异常捕获失败: {sentry_error}")
            
            self.show_error_message("启动错误", f"应用程序启动失败: {e}")
            return 1


def check_dependencies():
    """检查依赖项"""
    required_modules = [
        'PyQt6',
        'requests',
        'sqlalchemy'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
            
    if missing_modules:
        print(f"缺少必需的模块: {', '.join(missing_modules)}")
        print("请运行: pip install -r requirements.txt")
        return False
        
    return True


def check_system_requirements():
    """检查系统要求"""
    import platform
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"需要Python 3.8或更高版本，当前版本: {python_version.major}.{python_version.minor}")
        return False
        
    # 检查操作系统
    system = platform.system()
    if system not in ['Windows', 'Darwin', 'Linux']:
        print(f"不支持的操作系统: {system}")
        return False
        
    return True


def main():
    """主函数"""
    try:
        # 检查系统要求
        if not check_system_requirements():
            sys.exit(1)
            
        # 检查依赖项
        if not check_dependencies():
            sys.exit(1)
            
        # 创建并运行应用程序
        app = Application()
        exit_code = app.run()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n应用程序被用户中断")
        sys.exit(0)
        
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()