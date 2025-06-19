"""
SelfMastery B2B业务系统 - FastAPI后端应用入口
"""
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from datetime import datetime
import traceback

from config.settings import get_app_settings
from config.database import init_async_db
from .api import api_router
from .utils.exceptions import BaseAPIException
from .utils.responses import APIResponse, ResponseMessages
from .utils.monitoring import init_sentry_monitoring, capture_exception, set_user_context, add_breadcrumb
from .middleware.cors import setup_cors

# 获取应用设置
settings = get_app_settings()

# 初始化 Sentry 监控
init_sentry_monitoring()

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE) if settings.LOG_FILE else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动SelfMastery B2B业务系统...")
    
    # 初始化数据库
    try:
        await init_async_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    # 创建必要的目录
    Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("应用启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭应用...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 设置CORS中间件
setup_cors(app)

# 添加受信任主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", settings.API_HOST, "*"]
)


@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """自定义API异常处理器"""
    logger.warning(f"API异常: {exc.detail} - 路径: {request.url}")
    
    # 记录到 Sentry（仅记录严重错误）
    if exc.status_code >= 500:
        capture_exception(exc)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            message=exc.detail,
            error_code=getattr(exc, 'error_code', None)
        )
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.detail} - 状态码: {exc.status_code} - 路径: {request.url}")
    
    # 记录到 Sentry（仅记录服务器错误）
    if exc.status_code >= 500:
        capture_exception(exc)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            message=exc.detail,
            error_code="HTTP_ERROR"
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.warning(f"验证异常: {exc.errors()} - 路径: {request.url}")
    
    # 格式化验证错误
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content=APIResponse.validation_error(
            validation_errors=validation_errors,
            message=ResponseMessages.VALIDATION_ERROR
        )
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {exc} - 路径: {request.url}", exc_info=True)
    
    # 记录到 Sentry
    capture_exception(exc)
    
    # 在调试模式下返回详细错误信息
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content=APIResponse.error(
                message=f"内部服务器错误: {str(exc)}",
                error_code="INTERNAL_ERROR",
                details={
                    "traceback": traceback.format_exc(),
                    "exception_type": type(exc).__name__
                }
            )
        )
    else:
        return JSONResponse(
            status_code=500,
            content=APIResponse.error(
                message=ResponseMessages.INTERNAL_ERROR,
                error_code="INTERNAL_ERROR"
            )
        )


# 根路由
@app.get("/", summary="系统信息")
async def root():
    """根路由 - 系统信息"""
    return APIResponse.success(
        data={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "api_url": settings.API_V1_STR
        },
        message=f"欢迎使用{settings.APP_NAME}"
    )


# 健康检查路由
@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查"""
    return APIResponse.success(
        data={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": settings.APP_VERSION,
            "uptime": "运行中"
        },
        message="系统运行正常"
    )


# API路由组
@app.get(f"{settings.API_V1_STR}/", summary="API信息")
async def api_root():
    """API根路由"""
    return APIResponse.success(
        data={
            "name": f"{settings.APP_NAME} API",
            "version": settings.APP_VERSION,
            "api_version": "v1",
            "endpoints": {
                "auth": f"{settings.API_V1_STR}/auth",
                "users": f"{settings.API_V1_STR}/users",
                "systems": f"{settings.API_V1_STR}/systems",
                "processes": f"{settings.API_V1_STR}/processes",
                "sops": f"{settings.API_V1_STR}/sops",
                "kpis": f"{settings.API_V1_STR}/kpis",
                "tasks": f"{settings.API_V1_STR}/tasks"
            }
        },
        message="API服务正常运行"
    )


# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    """直接运行应用"""
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )