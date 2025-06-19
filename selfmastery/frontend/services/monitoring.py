"""
前端 Sentry 监控集成模块
"""
import logging
import sys
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from config.settings import get_pyqt_settings

logger = logging.getLogger(__name__)


def init_frontend_sentry_monitoring():
    """初始化前端 Sentry 监控"""
    settings = get_pyqt_settings()
    
    if not settings.SENTRY_DSN:
        logger.warning("SENTRY_DSN 未配置，跳过前端 Sentry 初始化")
        return
    
    # 配置日志集成
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # 捕获 info 及以上级别的日志
        event_level=logging.ERROR  # 将 error 及以上级别的日志作为事件发送
    )
    
    # 初始化 Sentry
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        sample_rate=settings.SENTRY_SAMPLE_RATE,
        send_default_pii=settings.SENTRY_SEND_DEFAULT_PII,
        attach_stacktrace=settings.SENTRY_ATTACH_STACKTRACE,
        integrations=[
            sentry_logging,
        ],
        # 添加前端特定的标签
        before_send=filter_frontend_events,
    )
    
    # 设置全局标签
    sentry_sdk.set_tag("service", "selfmastery-frontend")
    sentry_sdk.set_tag("platform", "PyQt6")
    sentry_sdk.set_tag("python_version", f"{sys.version_info.major}.{sys.version_info.minor}")
    
    logger.info(f"前端 Sentry 监控已初始化，环境: {settings.SENTRY_ENVIRONMENT}")


def filter_frontend_events(event, hint):
    """过滤前端事件，只发送重要的错误"""
    # 过滤掉一些常见的非关键错误
    if 'exception' in event:
        exc_info = hint.get('exc_info')
        if exc_info:
            exc_type, exc_value, exc_traceback = exc_info
            
            # 过滤掉一些PyQt相关的非关键警告
            if 'QObject' in str(exc_value) and 'destroyed' in str(exc_value):
                return None
                
            # 过滤掉网络超时等常见错误
            if 'timeout' in str(exc_value).lower():
                return None
    
    return event


def capture_frontend_exception(exception: Exception, **kwargs):
    """捕获前端异常到 Sentry"""
    try:
        # 添加前端特定的额外信息
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("component", "frontend")
            
        sentry_sdk.capture_exception(exception, **kwargs)
    except Exception as e:
        logger.error(f"前端 Sentry 异常捕获失败: {e}")


def capture_frontend_message(message: str, level: str = "info", **kwargs):
    """发送前端消息到 Sentry"""
    try:
        sentry_sdk.capture_message(message, level=level, **kwargs)
    except Exception as e:
        logger.error(f"前端 Sentry 消息发送失败: {e}")


def set_frontend_user_context(user_id: str, email: str = None, username: str = None):
    """设置前端用户上下文"""
    try:
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username
        })
    except Exception as e:
        logger.error(f"前端 Sentry 用户上下文设置失败: {e}")


def add_frontend_breadcrumb(message: str, category: str = "ui", level: str = "info", data=None):
    """添加前端面包屑"""
    try:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )
    except Exception as e:
        logger.error(f"前端 Sentry 面包屑添加失败: {e}")


def install_exception_handler():
    """安装全局异常处理器"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """全局异常处理器"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 允许 Ctrl+C 正常退出
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # 发送到 Sentry
        capture_frontend_exception(exc_value)
        
        # 调用默认异常处理器
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception 