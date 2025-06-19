"""
API路由模块初始化
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router

# 创建主API路由器
api_router = APIRouter()

# 包含各个子路由
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["认证"]
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["用户管理"]
)

# TODO: 添加其他路由
# api_router.include_router(
#     systems_router,
#     prefix="/systems",
#     tags=["业务系统"]
# )
# 
# api_router.include_router(
#     processes_router,
#     prefix="/processes",
#     tags=["业务流程"]
# )
# 
# api_router.include_router(
#     sops_router,
#     prefix="/sops",
#     tags=["SOP文档"]
# )
# 
# api_router.include_router(
#     kpis_router,
#     prefix="/kpis",
#     tags=["KPI指标"]
# )
# 
# api_router.include_router(
#     tasks_router,
#     prefix="/tasks",
#     tags=["任务管理"]
# )

__all__ = ["api_router"]