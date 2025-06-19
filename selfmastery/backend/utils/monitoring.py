"""
Sentry 监控集成模块
"""
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration

from config.settings import get_app_settings

logger = logging.getLogger(__name__)


def init_sentry_monitoring():
    """初始化 Sentry 监控"""
    settings = get_app_settings()
    
    if not settings.SENTRY_DSN:
        logger.warning("SENTRY_DSN 未配置，跳过 Sentry 初始化")
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
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        send_default_pii=settings.SENTRY_SEND_DEFAULT_PII,
        attach_stacktrace=settings.SENTRY_ATTACH_STACKTRACE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            AsyncioIntegration(),
            sentry_logging,
            HttpxIntegration(),
        ],
        # 添加全局标签
        _experiments={
            "profiles_sample_rate": settings.SENTRY_PROFILES_SAMPLE_RATE,
        }
    )
    
    # 设置全局标签
    sentry_sdk.set_tag("service", "selfmastery-backend")
    sentry_sdk.set_tag("version", settings.APP_VERSION)
    
    logger.info(f"Sentry 监控已初始化，环境: {settings.SENTRY_ENVIRONMENT}")


def capture_exception(exception: Exception, **kwargs):
    """捕获异常到 Sentry"""
    try:
        sentry_sdk.capture_exception(exception, **kwargs)
    except Exception as e:
        logger.error(f"Sentry 异常捕获失败: {e}")


def capture_message(message: str, level: str = "info", **kwargs):
    """发送消息到 Sentry"""
    try:
        sentry_sdk.capture_message(message, level=level, **kwargs)
    except Exception as e:
        logger.error(f"Sentry 消息发送失败: {e}")


def set_user_context(user_id: str, email: str = None, username: str = None):
    """设置用户上下文"""
    try:
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username
        })
    except Exception as e:
        logger.error(f"Sentry 用户上下文设置失败: {e}")


def set_extra_context(key: str, value):
    """设置额外上下文"""
    try:
        sentry_sdk.set_extra(key, value)
    except Exception as e:
        logger.error(f"Sentry 额外上下文设置失败: {e}")


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data=None):
    """添加面包屑"""
    try:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )
    except Exception as e:
        logger.error(f"Sentry 面包屑添加失败: {e}") 