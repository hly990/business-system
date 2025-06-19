"""
自定义异常类
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """基础API异常类"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationError(BaseAPIException):
    """数据验证异常"""
    
    def __init__(self, detail: str = "数据验证失败", error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code
        )


class AuthenticationError(BaseAPIException):
    """认证异常"""
    
    def __init__(self, detail: str = "认证失败", error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(BaseAPIException):
    """授权异常"""
    
    def __init__(self, detail: str = "权限不足", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )


class NotFoundError(BaseAPIException):
    """资源不存在异常"""
    
    def __init__(self, detail: str = "资源不存在", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )


class ConflictError(BaseAPIException):
    """资源冲突异常"""
    
    def __init__(self, detail: str = "资源冲突", error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code
        )


class BusinessLogicError(BaseAPIException):
    """业务逻辑异常"""
    
    def __init__(self, detail: str = "业务逻辑错误", error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class DatabaseError(BaseAPIException):
    """数据库操作异常"""
    
    def __init__(self, detail: str = "数据库操作失败", error_code: str = "DATABASE_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code
        )


class ExternalServiceError(BaseAPIException):
    """外部服务异常"""
    
    def __init__(self, detail: str = "外部服务调用失败", error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code=error_code
        )


class RateLimitError(BaseAPIException):
    """频率限制异常"""
    
    def __init__(self, detail: str = "请求频率过高", error_code: str = "RATE_LIMIT_ERROR"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code
        )


class FileUploadError(BaseAPIException):
    """文件上传异常"""
    
    def __init__(self, detail: str = "文件上传失败", error_code: str = "FILE_UPLOAD_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class TokenExpiredError(AuthenticationError):
    """令牌过期异常"""
    
    def __init__(self, detail: str = "令牌已过期", error_code: str = "TOKEN_EXPIRED"):
        super().__init__(detail=detail, error_code=error_code)


class InvalidTokenError(AuthenticationError):
    """无效令牌异常"""
    
    def __init__(self, detail: str = "无效的令牌", error_code: str = "INVALID_TOKEN"):
        super().__init__(detail=detail, error_code=error_code)


class UserNotFoundError(NotFoundError):
    """用户不存在异常"""
    
    def __init__(self, detail: str = "用户不存在", error_code: str = "USER_NOT_FOUND"):
        super().__init__(detail=detail, error_code=error_code)


class UserAlreadyExistsError(ConflictError):
    """用户已存在异常"""
    
    def __init__(self, detail: str = "用户已存在", error_code: str = "USER_ALREADY_EXISTS"):
        super().__init__(detail=detail, error_code=error_code)


class SystemNotFoundError(NotFoundError):
    """业务系统不存在异常"""
    
    def __init__(self, detail: str = "业务系统不存在", error_code: str = "SYSTEM_NOT_FOUND"):
        super().__init__(detail=detail, error_code=error_code)


class ProcessNotFoundError(NotFoundError):
    """业务流程不存在异常"""
    
    def __init__(self, detail: str = "业务流程不存在", error_code: str = "PROCESS_NOT_FOUND"):
        super().__init__(detail=detail, error_code=error_code)


class SOPNotFoundError(NotFoundError):
    """SOP不存在异常"""
    
    def __init__(self, detail: str = "SOP不存在", error_code: str = "SOP_NOT_FOUND"):
        super().__init__(detail=detail, error_code=error_code)


class TaskNotFoundError(NotFoundError):
    """任务不存在异常"""
    
    def __init__(self, detail: str = "任务不存在", error_code: str = "TASK_NOT_FOUND"):
        super().__init__(detail=detail, error_code=error_code)


class KPINotFoundError(NotFoundError):
    """KPI不存在异常"""
    
    def __init__(self, detail: str = "KPI不存在", error_code: str = "KPI_NOT_FOUND"):
        super().__init__(detail=detail, error_code=error_code)


class InsufficientPermissionError(AuthorizationError):
    """权限不足异常"""
    
    def __init__(self, detail: str = "权限不足，无法执行此操作", error_code: str = "INSUFFICIENT_PERMISSION"):
        super().__init__(detail=detail, error_code=error_code)


class ResourceLockError(ConflictError):
    """资源锁定异常"""
    
    def __init__(self, detail: str = "资源被锁定，无法操作", error_code: str = "RESOURCE_LOCKED"):
        super().__init__(detail=detail, error_code=error_code)


class DataIntegrityError(BusinessLogicError):
    """数据完整性异常"""
    
    def __init__(self, detail: str = "数据完整性约束违反", error_code: str = "DATA_INTEGRITY_ERROR"):
        super().__init__(detail=detail, error_code=error_code)