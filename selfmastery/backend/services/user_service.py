"""
用户服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserStats
from ..utils.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    DatabaseError,
    ValidationError
)
from .base_service import BaseService


class UserService(BaseService[User]):
    """用户服务类"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        try:
            # 检查邮箱是否已存在
            existing_user = self.get_by_field("email", user_data.email)
            if existing_user:
                raise UserAlreadyExistsError("邮箱已被注册")
            
            # 创建用户数据字典
            user_dict = user_data.dict()
            
            # 创建用户
            user = self.create(user_dict)
            return user
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"用户创建失败: {str(e)}")
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            # 如果更新邮箱，检查是否已存在
            if user_data.email and user_data.email != user.email:
                existing_user = self.get_by_field("email", user_data.email)
                if existing_user:
                    raise UserAlreadyExistsError("邮箱已被其他用户使用")
            
            # 过滤掉None值
            update_data = {k: v for k, v in user_data.dict().items() if v is not None}
            
            if not update_data:
                return user
            
            updated_user = self.update(user_id, update_data)
            return updated_user
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"用户更新失败: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.get_by_field("email", email)
    
    def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """根据角色获取用户列表"""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"role": role}
        )
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取活跃用户列表"""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"is_active": True}
        )
    
    def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """搜索用户"""
        # 构建过滤条件
        filters = {}
        if role:
            filters["role"] = role
        if is_active is not None:
            filters["is_active"] = is_active
        
        # 如果有过滤条件，先应用过滤再搜索
        if filters:
            users = self.get_multi(filters=filters, limit=1000)  # 获取更多数据用于搜索
            # 在内存中进行搜索过滤
            search_results = []
            for user in users:
                if (query.lower() in user.name.lower() or 
                    query.lower() in user.email.lower()):
                    search_results.append(user)
            
            # 应用分页
            return search_results[skip:skip + limit]
        else:
            # 直接使用数据库搜索
            return self.search(
                search_term=query,
                search_fields=["name", "email"],
                skip=skip,
                limit=limit
            )
    
    def get_user_stats(self, user_id: int) -> UserStats:
        """获取用户统计信息"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            # 统计用户相关数据
            stats = UserStats()
            
            # 统计拥有的业务系统数量
            stats.total_systems = len(user.owned_systems)
            
            # 统计拥有的业务流程数量
            stats.total_processes = len(user.owned_processes)
            
            # 统计创建的SOP数量
            stats.total_sops = len(user.authored_sops)
            
            # 统计分配的任务数量
            assigned_tasks = user.assigned_tasks
            stats.total_tasks = len(assigned_tasks)
            
            # 统计已完成和待处理的任务
            completed_tasks = [task for task in assigned_tasks if task.status == "completed"]
            pending_tasks = [task for task in assigned_tasks if task.status in ["pending", "in_progress"]]
            
            stats.completed_tasks = len(completed_tasks)
            stats.pending_tasks = len(pending_tasks)
            
            return stats
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"获取用户统计失败: {str(e)}")
    
    def deactivate_user(self, user_id: int) -> bool:
        """停用用户"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            self.update(user_id, {"is_active": False})
            return True
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"用户停用失败: {str(e)}")
    
    def activate_user(self, user_id: int) -> bool:
        """激活用户"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            self.update(user_id, {"is_active": True})
            return True
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"用户激活失败: {str(e)}")
    
    def change_user_role(self, user_id: int, new_role: str) -> Optional[User]:
        """修改用户角色"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            # 验证角色
            allowed_roles = ['admin', 'manager', 'user', 'viewer']
            if new_role not in allowed_roles:
                raise ValidationError(f"无效的角色: {new_role}")
            
            updated_user = self.update(user_id, {"role": new_role})
            return updated_user
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"角色修改失败: {str(e)}")
    
    def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        """根据ID列表获取用户"""
        try:
            users = []
            for user_id in user_ids:
                user = self.get(user_id)
                if user:
                    users.append(user)
            return users
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"批量获取用户失败: {str(e)}")
    
    def bulk_update_users(self, updates: List[Dict[str, Any]]) -> List[User]:
        """批量更新用户"""
        try:
            updated_users = []
            for update_data in updates:
                user_id = update_data.get("id")
                if not user_id:
                    continue
                
                user = self.get(user_id)
                if not user:
                    continue
                
                # 移除id字段
                update_fields = {k: v for k, v in update_data.items() if k != "id"}
                
                if update_fields:
                    updated_user = self.update(user_id, update_fields)
                    if updated_user:
                        updated_users.append(updated_user)
            
            return updated_users
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"批量更新用户失败: {str(e)}")
    
    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """获取用户权限信息"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            # 根据角色定义权限
            permissions = {
                "can_create_system": False,
                "can_edit_system": False,
                "can_delete_system": False,
                "can_create_process": False,
                "can_edit_process": False,
                "can_delete_process": False,
                "can_create_sop": False,
                "can_edit_sop": False,
                "can_delete_sop": False,
                "can_manage_users": False,
                "can_view_analytics": False,
            }
            
            if user.role == "admin":
                # 管理员拥有所有权限
                permissions = {k: True for k in permissions.keys()}
            elif user.role == "manager":
                # 管理者拥有大部分权限
                permissions.update({
                    "can_create_system": True,
                    "can_edit_system": True,
                    "can_create_process": True,
                    "can_edit_process": True,
                    "can_create_sop": True,
                    "can_edit_sop": True,
                    "can_view_analytics": True,
                })
            elif user.role == "user":
                # 普通用户拥有基本权限
                permissions.update({
                    "can_create_process": True,
                    "can_edit_process": True,
                    "can_create_sop": True,
                    "can_edit_sop": True,
                })
            # viewer角色保持默认权限（只读）
            
            return permissions
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"获取用户权限失败: {str(e)}")
    
    def check_user_permission(self, user_id: int, permission: str) -> bool:
        """检查用户是否拥有特定权限"""
        permissions = self.get_user_permissions(user_id)
        return permissions.get(permission, False)