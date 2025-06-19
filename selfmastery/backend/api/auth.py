"""
认证相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ..schemas.user import (
    UserLogin, UserRegister, Token, UserResponse,
    PasswordReset, PasswordResetConfirm
)
from ..services.auth_service import AuthService
from ..middleware.auth import get_current_active_user
from ..utils.responses import APIResponse
from ..utils.exceptions import (
    AuthenticationError, UserAlreadyExistsError,
    ValidationError, DatabaseError
)
from config.database import get_db

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=dict, summary="用户登录")
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    - **email**: 用户邮箱
    - **password**: 用户密码
    
    返回访问令牌和刷新令牌
    """
    try:
        auth_service = AuthService(db)
        token = auth_service.login(login_data)
        
        return APIResponse.success(
            data={
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "token_type": token.token_type,
                "expires_in": token.expires_in
            },
            message="登录成功"
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.post("/register", response_model=dict, summary="用户注册")
async def register(
    register_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    - **name**: 用户姓名
    - **email**: 用户邮箱
    - **password**: 密码
    - **confirm_password**: 确认密码
    - **role**: 用户角色（可选，默认为user）
    """
    try:
        auth_service = AuthService(db)
        
        # 创建用户数据
        from ..schemas.user import UserCreate
        user_data = UserCreate(
            name=register_data.name,
            email=register_data.email,
            password=register_data.password,
            role=register_data.role,
            timezone=register_data.timezone
        )
        
        user = auth_service.register(user_data)
        
        return APIResponse.created(
            data={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at
            },
            message="注册成功"
        )
        
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败"
        )


@router.post("/refresh", response_model=dict, summary="刷新令牌")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    
    返回新的访问令牌
    """
    try:
        auth_service = AuthService(db)
        token = auth_service.refresh_token(refresh_token)
        
        return APIResponse.success(
            data={
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "token_type": token.token_type,
                "expires_in": token.expires_in
            },
            message="令牌刷新成功"
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新失败"
        )


@router.post("/logout", response_model=dict, summary="用户登出")
async def logout(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    用户登出
    
    注意：由于使用JWT令牌，实际的登出需要在客户端删除令牌
    这个端点主要用于记录登出事件和清理服务器端状态
    """
    try:
        # TODO: 可以在这里添加令牌黑名单逻辑
        # TODO: 可以在这里记录登出日志
        
        return APIResponse.success(message="登出成功")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        )


@router.get("/me", response_model=dict, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    获取当前登录用户的信息
    """
    try:
        return APIResponse.success(
            data={
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "role": current_user.role,
                "timezone": current_user.timezone,
                "is_active": current_user.is_active,
                "created_at": current_user.created_at,
                "updated_at": current_user.updated_at
            },
            message="获取用户信息成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )


@router.post("/change-password", response_model=dict, summary="修改密码")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码
    
    - **old_password**: 原密码
    - **new_password**: 新密码
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.change_password(
            current_user.id,
            old_password,
            new_password
        )
        
        if success:
            return APIResponse.success(message="密码修改成功")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码修改失败"
            )
            
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败"
        )


@router.post("/reset-password", response_model=dict, summary="请求密码重置")
async def request_password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    请求密码重置
    
    - **email**: 用户邮箱
    
    发送密码重置邮件（实际实现中需要集成邮件服务）
    """
    try:
        auth_service = AuthService(db)
        reset_token = auth_service.reset_password(reset_data.email)
        
        # TODO: 在实际实现中，这里应该发送邮件而不是返回令牌
        # 这里为了演示目的返回令牌
        return APIResponse.success(
            data={"reset_token": reset_token},
            message="密码重置邮件已发送"
        )
        
    except Exception as e:
        # 为了安全，不暴露用户是否存在的信息
        return APIResponse.success(
            message="如果邮箱存在，密码重置邮件已发送"
        )


@router.post("/reset-password/confirm", response_model=dict, summary="确认密码重置")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    确认密码重置
    
    - **token**: 重置令牌
    - **new_password**: 新密码
    - **confirm_password**: 确认新密码
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.confirm_password_reset(
            reset_data.token,
            reset_data.new_password
        )
        
        if success:
            return APIResponse.success(message="密码重置成功")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码重置失败"
            )
            
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置失败"
        )


@router.post("/verify-token", response_model=dict, summary="验证令牌")
async def verify_token(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    验证当前令牌是否有效
    """
    try:
        return APIResponse.success(
            data={"valid": True, "user_id": current_user.id},
            message="令牌有效"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效"
        )