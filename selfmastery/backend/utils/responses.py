"""
统一响应格式
"""
from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel
from datetime import datetime


class BaseResponse(BaseModel):
    """基础响应模式"""
    success: bool = True
    message: str = "操作成功"
    timestamp: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseResponse):
    """成功响应模式"""
    data: Optional[Any] = None
    
    def __init__(self, data: Any = None, message: str = "操作成功", **kwargs):
        super().__init__(success=True, message=message, data=data, **kwargs)


class ErrorResponse(BaseResponse):
    """错误响应模式"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    def __init__(
        self, 
        message: str = "操作失败", 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            success=False, 
            message=message, 
            error_code=error_code,
            details=details,
            **kwargs
        )


class PaginatedResponse(BaseResponse):
    """分页响应模式"""
    data: List[Any]
    pagination: Dict[str, Any]
    
    def __init__(
        self,
        data: List[Any],
        total: int,
        page: int,
        size: int,
        message: str = "获取数据成功",
        **kwargs
    ):
        pages = (total + size - 1) // size if size > 0 else 0
        pagination = {
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
        super().__init__(
            success=True,
            message=message,
            data=data,
            pagination=pagination,
            **kwargs
        )


class ValidationErrorResponse(ErrorResponse):
    """验证错误响应模式"""
    validation_errors: List[Dict[str, Any]]
    
    def __init__(
        self,
        validation_errors: List[Dict[str, Any]],
        message: str = "数据验证失败",
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            validation_errors=validation_errors,
            **kwargs
        )


def success_response(
    data: Any = None,
    message: str = "操作成功"
) -> Dict[str, Any]:
    """创建成功响应"""
    return SuccessResponse(data=data, message=message).dict()


def error_response(
    message: str = "操作失败",
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """创建错误响应"""
    return ErrorResponse(
        message=message,
        error_code=error_code,
        details=details
    ).dict()


def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    size: int,
    message: str = "获取数据成功"
) -> Dict[str, Any]:
    """创建分页响应"""
    return PaginatedResponse(
        data=data,
        total=total,
        page=page,
        size=size,
        message=message
    ).dict()


def validation_error_response(
    validation_errors: List[Dict[str, Any]],
    message: str = "数据验证失败"
) -> Dict[str, Any]:
    """创建验证错误响应"""
    return ValidationErrorResponse(
        validation_errors=validation_errors,
        message=message
    ).dict()


class APIResponse:
    """API响应工具类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
        """成功响应"""
        return success_response(data=data, message=message)
    
    @staticmethod
    def error(
        message: str = "操作失败",
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """错误响应"""
        return error_response(
            message=message,
            error_code=error_code,
            details=details
        )
    
    @staticmethod
    def paginated(
        data: List[Any],
        total: int,
        page: int,
        size: int,
        message: str = "获取数据成功"
    ) -> Dict[str, Any]:
        """分页响应"""
        return paginated_response(
            data=data,
            total=total,
            page=page,
            size=size,
            message=message
        )
    
    @staticmethod
    def validation_error(
        validation_errors: List[Dict[str, Any]],
        message: str = "数据验证失败"
    ) -> Dict[str, Any]:
        """验证错误响应"""
        return validation_error_response(
            validation_errors=validation_errors,
            message=message
        )
    
    @staticmethod
    def created(data: Any = None, message: str = "创建成功") -> Dict[str, Any]:
        """创建成功响应"""
        return success_response(data=data, message=message)
    
    @staticmethod
    def updated(data: Any = None, message: str = "更新成功") -> Dict[str, Any]:
        """更新成功响应"""
        return success_response(data=data, message=message)
    
    @staticmethod
    def deleted(message: str = "删除成功") -> Dict[str, Any]:
        """删除成功响应"""
        return success_response(message=message)
    
    @staticmethod
    def not_found(message: str = "资源不存在") -> Dict[str, Any]:
        """资源不存在响应"""
        return error_response(message=message, error_code="NOT_FOUND")
    
    @staticmethod
    def unauthorized(message: str = "认证失败") -> Dict[str, Any]:
        """认证失败响应"""
        return error_response(message=message, error_code="UNAUTHORIZED")
    
    @staticmethod
    def forbidden(message: str = "权限不足") -> Dict[str, Any]:
        """权限不足响应"""
        return error_response(message=message, error_code="FORBIDDEN")
    
    @staticmethod
    def conflict(message: str = "资源冲突") -> Dict[str, Any]:
        """资源冲突响应"""
        return error_response(message=message, error_code="CONFLICT")
    
    @staticmethod
    def internal_error(message: str = "内部服务器错误") -> Dict[str, Any]:
        """内部服务器错误响应"""
        return error_response(message=message, error_code="INTERNAL_ERROR")


# 常用响应消息
class ResponseMessages:
    """响应消息常量"""
    
    # 通用消息
    SUCCESS = "操作成功"
    ERROR = "操作失败"
    
    # 创建操作
    CREATED = "创建成功"
    CREATE_FAILED = "创建失败"
    
    # 更新操作
    UPDATED = "更新成功"
    UPDATE_FAILED = "更新失败"
    
    # 删除操作
    DELETED = "删除成功"
    DELETE_FAILED = "删除失败"
    
    # 查询操作
    FOUND = "查询成功"
    NOT_FOUND = "资源不存在"
    
    # 认证授权
    LOGIN_SUCCESS = "登录成功"
    LOGIN_FAILED = "登录失败"
    LOGOUT_SUCCESS = "退出成功"
    UNAUTHORIZED = "认证失败"
    FORBIDDEN = "权限不足"
    
    # 数据验证
    VALIDATION_ERROR = "数据验证失败"
    INVALID_PARAMETER = "参数无效"
    
    # 业务逻辑
    BUSINESS_ERROR = "业务逻辑错误"
    DUPLICATE_RESOURCE = "资源已存在"
    RESOURCE_LOCKED = "资源被锁定"
    
    # 系统错误
    INTERNAL_ERROR = "内部服务器错误"
    DATABASE_ERROR = "数据库操作失败"
    EXTERNAL_SERVICE_ERROR = "外部服务调用失败"