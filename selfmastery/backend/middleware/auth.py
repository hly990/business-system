"""
认证中间件
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..services.auth_service import AuthService
from ..models.user import User
from ..utils.exceptions import AuthenticationError, AuthorizationError
from config.database import get_db

# HTTP Bearer 认证方案
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_current_user(credentials.credentials)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取可选的当前用户（用于可选认证的端点）"""
    if not credentials:
        return None
    
    try:
        auth_service = AuthService(db)
        user = auth_service.get_current_user(credentials.credentials)
        return user
    except AuthenticationError:
        return None


class RoleChecker:
    """角色检查器"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_active_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        from ..services.user_service import UserService
        user_service = UserService(db)
        
        if not user_service.check_user_permission(current_user.id, self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {self.required_permission}"
            )
        return current_user


class ResourceOwnerChecker:
    """资源所有者检查器"""
    
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
    
    def __call__(
        self,
        resource_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """检查用户是否是资源的所有者"""
        try:
            if self.resource_type == "system":
                from ..services.system_service import SystemService
                service = SystemService(db)
                resource = service.get(resource_id)
                if not resource or resource.owner_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="只有资源所有者可以执行此操作"
                    )
            elif self.resource_type == "process":
                from ..services.process_service import ProcessService
                service = ProcessService(db)
                resource = service.get(resource_id)
                if not resource or resource.owner_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="只有资源所有者可以执行此操作"
                    )
            elif self.resource_type == "sop":
                from ..services.sop_service import SOPService
                service = SOPService(db)
                resource = service.get(resource_id)
                if not resource or resource.author_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="只有资源所有者可以执行此操作"
                    )
            elif self.resource_type == "task":
                from ..services.task_service import TaskService
                service = TaskService(db)
                resource = service.get(resource_id)
                if not resource or resource.assignee_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="只有任务分配者可以执行此操作"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不支持的资源类型"
                )
            
            return current_user
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="权限检查失败"
            )


# 预定义的角色检查器
require_admin = RoleChecker(["admin"])
require_manager_or_admin = RoleChecker(["admin", "manager"])
require_user_or_above = RoleChecker(["admin", "manager", "user"])

# 预定义的权限检查器
require_system_create = PermissionChecker("can_create_system")
require_system_edit = PermissionChecker("can_edit_system")
require_system_delete = PermissionChecker("can_delete_system")
require_process_create = PermissionChecker("can_create_process")
require_process_edit = PermissionChecker("can_edit_process")
require_process_delete = PermissionChecker("can_delete_process")
require_sop_create = PermissionChecker("can_create_sop")
require_sop_edit = PermissionChecker("can_edit_sop")
require_sop_delete = PermissionChecker("can_delete_sop")
require_user_management = PermissionChecker("can_manage_users")
require_analytics_view = PermissionChecker("can_view_analytics")

# 预定义的资源所有者检查器
require_system_owner = ResourceOwnerChecker("system")
require_process_owner = ResourceOwnerChecker("process")
require_sop_owner = ResourceOwnerChecker("sop")
require_task_assignee = ResourceOwnerChecker("task")


def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """验证令牌依赖项（不返回用户，只验证令牌有效性）"""
    try:
        auth_service = AuthService(db)
        auth_service.verify_token(credentials.credentials)
        return True
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_from_token(
    token: str,
    db: Session = Depends(get_db)
) -> User:
    """从令牌获取用户（用于内部服务调用）"""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_current_user(token)
        return user
    except AuthenticationError as e:
        raise AuthenticationError(str(e))


class APIKeyChecker:
    """API密钥检查器（用于外部API调用）"""
    
    def __init__(self, required_scopes: list = None):
        self.required_scopes = required_scopes or []
    
    def __call__(self, api_key: str = Depends(security)):
        # TODO: 实现API密钥验证逻辑
        # 这里可以添加API密钥的验证逻辑
        pass


def rate_limit_checker(max_requests: int = 100, window_seconds: int = 3600):
    """速率限制检查器"""
    def checker(
        current_user: User = Depends(get_current_active_user),
        # TODO: 添加Redis或其他缓存依赖来实现速率限制
    ):
        # TODO: 实现速率限制逻辑
        # 这里可以添加基于用户的速率限制逻辑
        return current_user
    
    return checker