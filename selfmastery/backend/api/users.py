"""
用户管理API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserStats, UserProfile
)
from ..services.user_service import UserService
from ..middleware.auth import (
    get_current_active_user, require_admin, require_manager_or_admin,
    require_user_management
)
from ..utils.responses import APIResponse
from ..utils.exceptions import (
    UserNotFoundError, UserAlreadyExistsError,
    ValidationError, DatabaseError, AuthorizationError
)
from config.database import get_db

router = APIRouter()


@router.get("/", response_model=dict, summary="获取用户列表")
async def get_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    role: Optional[str] = Query(None, description="按角色过滤"),
    is_active: Optional[bool] = Query(None, description="按状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: UserResponse = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户列表
    
    需要管理员或经理权限
    """
    try:
        user_service = UserService(db)
        
        if search:
            users = user_service.search_users(
                query=search,
                skip=skip,
                limit=limit,
                role=role,
                is_active=is_active
            )
            total = len(users)  # 搜索结果的总数（简化实现）
        else:
            # 构建过滤条件
            filters = {}
            if role:
                filters["role"] = role
            if is_active is not None:
                filters["is_active"] = is_active
            
            users = user_service.get_multi(
                skip=skip,
                limit=limit,
                filters=filters
            )
            total = user_service.count(filters=filters)
        
        # 转换为响应格式
        user_data = []
        for user in users:
            user_data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "timezone": user.timezone,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            })
        
        return APIResponse.paginated(
            data=user_data,
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            message="获取用户列表成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )


@router.post("/", response_model=dict, summary="创建用户")
async def create_user(
    user_data: UserCreate,
    current_user: UserResponse = Depends(require_user_management),
    db: Session = Depends(get_db)
):
    """
    创建新用户
    
    需要用户管理权限
    """
    try:
        user_service = UserService(db)
        user = user_service.create_user(user_data)
        
        return APIResponse.created(
            data={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "timezone": user.timezone,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            },
            message="用户创建成功"
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
            detail="用户创建失败"
        )


@router.get("/{user_id}", response_model=dict, summary="获取用户详情")
async def get_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户详情
    
    用户只能查看自己的详情，管理员可以查看所有用户
    """
    try:
        user_service = UserService(db)
        
        # 检查权限：用户只能查看自己的信息，管理员可以查看所有
        if current_user.id != user_id and current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        user = user_service.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return APIResponse.success(
            data={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "timezone": user.timezone,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            },
            message="获取用户详情成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户详情失败"
        )


@router.put("/{user_id}", response_model=dict, summary="更新用户信息")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    
    用户可以更新自己的基本信息，管理员可以更新所有用户信息
    """
    try:
        user_service = UserService(db)
        
        # 检查权限
        if current_user.id != user_id and current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 普通用户不能修改角色和状态
        if current_user.id == user_id and current_user.role not in ["admin"]:
            if user_data.role is not None or user_data.is_active is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权修改角色或状态"
                )
        
        user = user_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return APIResponse.updated(
            data={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "timezone": user.timezone,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            },
            message="用户信息更新成功"
        )
        
    except HTTPException:
        raise
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户信息更新失败"
        )


@router.delete("/{user_id}", response_model=dict, summary="删除用户")
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    删除用户
    
    需要管理员权限
    """
    try:
        user_service = UserService(db)
        
        # 不能删除自己
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除自己"
            )
        
        success = user_service.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return APIResponse.deleted(message="用户删除成功")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户删除失败"
        )


@router.post("/{user_id}/deactivate", response_model=dict, summary="停用用户")
async def deactivate_user(
    user_id: int,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    停用用户
    
    需要管理员权限
    """
    try:
        user_service = UserService(db)
        
        # 不能停用自己
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能停用自己"
            )
        
        success = user_service.deactivate_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return APIResponse.success(message="用户已停用")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户停用失败"
        )


@router.post("/{user_id}/activate", response_model=dict, summary="激活用户")
async def activate_user(
    user_id: int,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    激活用户
    
    需要管理员权限
    """
    try:
        user_service = UserService(db)
        
        success = user_service.activate_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return APIResponse.success(message="用户已激活")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户激活失败"
        )


@router.get("/{user_id}/stats", response_model=dict, summary="获取用户统计")
async def get_user_stats(
    user_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计信息
    
    用户可以查看自己的统计，管理员可以查看所有用户统计
    """
    try:
        # 检查权限
        if current_user.id != user_id and current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        user_service = UserService(db)
        stats = user_service.get_user_stats(user_id)
        
        return APIResponse.success(
            data={
                "total_systems": stats.total_systems,
                "total_processes": stats.total_processes,
                "total_sops": stats.total_sops,
                "total_tasks": stats.total_tasks,
                "completed_tasks": stats.completed_tasks,
                "pending_tasks": stats.pending_tasks
            },
            message="获取用户统计成功"
        )
        
    except HTTPException:
        raise
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户统计失败"
        )


@router.put("/{user_id}/role", response_model=dict, summary="修改用户角色")
async def change_user_role(
    user_id: int,
    new_role: str,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    修改用户角色
    
    需要管理员权限
    """
    try:
        user_service = UserService(db)
        
        # 不能修改自己的角色
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能修改自己的角色"
            )
        
        user = user_service.change_user_role(user_id, new_role)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return APIResponse.updated(
            data={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active
            },
            message="用户角色修改成功"
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户角色修改失败"
        )


@router.get("/{user_id}/permissions", response_model=dict, summary="获取用户权限")
async def get_user_permissions(
    user_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户权限信息
    
    用户可以查看自己的权限，管理员可以查看所有用户权限
    """
    try:
        # 检查权限
        if current_user.id != user_id and current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        user_service = UserService(db)
        permissions = user_service.get_user_permissions(user_id)
        
        return APIResponse.success(
            data=permissions,
            message="获取用户权限成功"
        )
        
    except HTTPException:
        raise
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户权限失败"
        )