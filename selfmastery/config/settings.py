"""
应用程序设置配置模块
"""
import os
from typing import List, Optional

# 简化的设置类，避免Pydantic版本问题
class Settings:
    """应用程序配置设置"""
    
    def __init__(self):
        # 应用基础配置
        self.APP_NAME = os.getenv("APP_NAME", "SelfMastery B2B Business System")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "SelfMastery B2B业务管理系统")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        
        # API配置
        self.API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.API_WORKERS = int(os.getenv("API_WORKERS", "1"))
        
        # 安全配置
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        
        # 数据库配置
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/selfmastery.db")
        
        # CORS配置
        cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000")
        self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
        
        # 文件上传配置
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
        self.MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))  # 10MB
        allowed_ext = os.getenv("ALLOWED_EXTENSIONS", ".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.xls,.xlsx")
        self.ALLOWED_EXTENSIONS = [ext.strip() for ext in allowed_ext.split(",")]
        
        # 缓存配置
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1小时
        
        # Celery配置
        self.CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
        self.CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
        self.CELERY_TASK_SERIALIZER = os.getenv("CELERY_TASK_SERIALIZER", "json")
        self.CELERY_RESULT_SERIALIZER = os.getenv("CELERY_RESULT_SERIALIZER", "json")
        celery_content = os.getenv("CELERY_ACCEPT_CONTENT", "json")
        self.CELERY_ACCEPT_CONTENT = [content.strip() for content in celery_content.split(",")]
        self.CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "Asia/Shanghai")
        self.CELERY_ENABLE_UTC = os.getenv("CELERY_ENABLE_UTC", "True").lower() == "true"
        
        # 邮件配置
        self.SMTP_TLS = os.getenv("SMTP_TLS", "True").lower() == "true"
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
        self.SMTP_HOST = os.getenv("SMTP_HOST")
        self.SMTP_USER = os.getenv("SMTP_USER")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.EMAILS_FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL")
        self.EMAILS_FROM_NAME = os.getenv("EMAILS_FROM_NAME")
        
        # 业务配置
        self.PAGINATION_SIZE = int(os.getenv("PAGINATION_SIZE", "20"))
        self.MAX_PAGINATION_SIZE = int(os.getenv("MAX_PAGINATION_SIZE", "100"))
        
        # 第三方服务配置
        self.WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")
        self.WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")
        self.ALIPAY_APP_ID = os.getenv("ALIPAY_APP_ID")
        self.ALIPAY_PRIVATE_KEY = os.getenv("ALIPAY_PRIVATE_KEY")
        
        # Sentry监控配置
        self.SENTRY_DSN = os.getenv("SENTRY_DSN")
        self.SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "development")
        self.SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))
        self.SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
        self.SENTRY_PROFILES_SAMPLE_RATE = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))
        self.SENTRY_SEND_DEFAULT_PII = os.getenv("SENTRY_SEND_DEFAULT_PII", "False").lower() == "true"
        self.SENTRY_ATTACH_STACKTRACE = os.getenv("SENTRY_ATTACH_STACKTRACE", "True").lower() == "true"


class PyQtSettings:
    """PyQt桌面应用配置"""
    
    def __init__(self):
        # 窗口配置
        self.WINDOW_TITLE = os.getenv("WINDOW_TITLE", "SelfMastery B2B管理系统")
        self.WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1200"))
        self.WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "800"))
        self.WINDOW_MIN_WIDTH = int(os.getenv("WINDOW_MIN_WIDTH", "800"))
        self.WINDOW_MIN_HEIGHT = int(os.getenv("WINDOW_MIN_HEIGHT", "600"))
        
        # 主题配置
        self.THEME = os.getenv("THEME", "light")  # light, dark
        self.THEME_COLOR = os.getenv("THEME_COLOR", "#2196F3")
        self.FONT_FAMILY = os.getenv("FONT_FAMILY", "Microsoft YaHei")
        self.FONT_SIZE = int(os.getenv("FONT_SIZE", "10"))
        
        # 界面配置
        self.SHOW_SPLASH_SCREEN = os.getenv("SHOW_SPLASH_SCREEN", "True").lower() == "true"
        self.SPLASH_TIMEOUT = int(os.getenv("SPLASH_TIMEOUT", "3000"))  # 毫秒
        self.AUTO_SAVE_INTERVAL = int(os.getenv("AUTO_SAVE_INTERVAL", "300"))  # 秒
        
        # 本地存储配置
        self.LOCAL_DATA_DIR = os.getenv("LOCAL_DATA_DIR", "data")
        self.CONFIG_FILE = os.getenv("CONFIG_FILE", "config.json")
        self.CACHE_DIR = os.getenv("CACHE_DIR", "cache")
        
        # Sentry监控配置（继承后端配置）
        self.SENTRY_DSN = os.getenv("SENTRY_DSN")
        self.SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "development")
        self.SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))
        self.SENTRY_SEND_DEFAULT_PII = os.getenv("SENTRY_SEND_DEFAULT_PII", "False").lower() == "true"
        self.SENTRY_ATTACH_STACKTRACE = os.getenv("SENTRY_ATTACH_STACKTRACE", "True").lower() == "true"


# 全局设置实例
settings = Settings()
app_settings = settings  # 向后兼容
pyqt_settings = PyQtSettings()


def get_app_settings() -> Settings:
    """获取应用设置"""
    return settings


def get_pyqt_settings() -> PyQtSettings:
    """获取PyQt设置"""
    return pyqt_settings


# 向后兼容的导出
__all__ = ["settings", "app_settings", "pyqt_settings", "get_app_settings", "get_pyqt_settings"]