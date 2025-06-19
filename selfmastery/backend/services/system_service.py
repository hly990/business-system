"""
业务系统服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.system import BusinessSystem
from ..schemas.system import BusinessSystemCreate, BusinessSystemUpdate, BusinessSystemStats
from ..utils.exceptions import (
    SystemNotFoundError,
    DatabaseError,
    AuthorizationError,
    ValidationError
)
from .base_service import BaseService


class SystemService(BaseService[BusinessSystem]):
    """业务系统服务类"""
    
    def __init__(self, db: Session):
        super().__init__(BusinessSystem, db)
    
    def create_system(self, system_data: BusinessSystemCreate, current_user_id: int) -> BusinessSystem:
        """创建业务系统"""
        try:
            # 确保创建者是系统所有者
            system_dict = system_data.dict()
            system_dict["owner_id"] = current_user_id
            
            system = self.create(system_dict)
            return system
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"业务系统创建失败: {str(e)}")
    
    def update_system(self, system_id: int, system_data: BusinessSystemUpdate, current_user_id: int) -> Optional[BusinessSystem]:
        """更新业务系统"""
        try:
            system = self.get(system_id)
            if not system:
                raise SystemNotFoundError("业务系统不存在")
            
            # 检查权限：只有系统所有者可以更新
            if system.owner_id != current_user_id:
                raise AuthorizationError("只有系统所有者可以更新系统")
            
            # 过滤掉None值
            update_data = {k: v for k, v in system_data.dict().items() if v is not None}
            
            if not update_data:
                return system
            
            updated_system = self.update(system_id, update_data)
            return updated_system
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"业务系统更新失败: {str(e)}")
    
    def delete_system(self, system_id: int, current_user_id: int) -> bool:
        """删除业务系统"""
        try:
            system = self.get(system_id)
            if not system:
                raise SystemNotFoundError("业务系统不存在")
            
            # 检查权限：只有系统所有者可以删除
            if system.owner_id != current_user_id:
                raise AuthorizationError("只有系统所有者可以删除系统")
            
            # 检查是否有关联的流程或SOP
            if system.processes or system.sops:
                raise ValidationError("系统下还有关联的流程或SOP，无法删除")
            
            return self.delete(system_id)
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"业务系统删除失败: {str(e)}")
    
    def get_user_systems(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BusinessSystem]:
        """获取用户的业务系统列表"""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"owner_id": user_id}
        )
    
    def get_systems_by_industry(self, industry: str, skip: int = 0, limit: int = 100) -> List[BusinessSystem]:
        """根据行业获取业务系统列表"""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"industry": industry}
        )
    
    def get_systems_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[BusinessSystem]:
        """根据状态获取业务系统列表"""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"status": status}
        )
    
    def search_systems(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        industry: Optional[str] = None,
        status: Optional[str] = None,
        owner_id: Optional[int] = None
    ) -> List[BusinessSystem]:
        """搜索业务系统"""
        # 构建过滤条件
        filters = {}
        if industry:
            filters["industry"] = industry
        if status:
            filters["status"] = status
        if owner_id:
            filters["owner_id"] = owner_id
        
        # 如果有过滤条件，先应用过滤再搜索
        if filters:
            systems = self.get_multi(filters=filters, limit=1000)
            # 在内存中进行搜索过滤
            search_results = []
            for system in systems:
                if (query.lower() in system.name.lower() or 
                    (system.description and query.lower() in system.description.lower())):
                    search_results.append(system)
            
            # 应用分页
            return search_results[skip:skip + limit]
        else:
            # 直接使用数据库搜索
            return self.search(
                search_term=query,
                search_fields=["name", "description"],
                skip=skip,
                limit=limit
            )
    
    def get_system_stats(self, system_id: int) -> BusinessSystemStats:
        """获取业务系统统计信息"""
        try:
            system = self.get(system_id)
            if not system:
                raise SystemNotFoundError("业务系统不存在")
            
            stats = BusinessSystemStats()
            
            # 统计流程数量
            processes = system.processes
            stats.total_processes = len(processes)
            stats.active_processes = len([p for p in processes if p.status == "active"])
            
            # 统计SOP数量
            sops = system.sops
            stats.total_sops = len(sops)
            stats.published_sops = len([s for s in sops if s.status == "published"])
            
            # 统计任务数量（通过流程关联）
            all_tasks = []
            for process in processes:
                all_tasks.extend(process.tasks)
            
            stats.total_tasks = len(all_tasks)
            stats.completed_tasks = len([t for t in all_tasks if t.status == "completed"])
            stats.pending_tasks = len([t for t in all_tasks if t.status in ["pending", "in_progress"]])
            
            # 统计逾期任务
            from datetime import datetime
            now = datetime.now()
            stats.overdue_tasks = len([
                t for t in all_tasks 
                if t.due_date and t.due_date < now and t.status != "completed"
            ])
            
            return stats
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"获取系统统计失败: {str(e)}")
    
    def archive_system(self, system_id: int, current_user_id: int) -> Optional[BusinessSystem]:
        """归档业务系统"""
        try:
            system = self.get(system_id)
            if not system:
                raise SystemNotFoundError("业务系统不存在")
            
            # 检查权限
            if system.owner_id != current_user_id:
                raise AuthorizationError("只有系统所有者可以归档系统")
            
            updated_system = self.update(system_id, {"status": "archived"})
            return updated_system
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"系统归档失败: {str(e)}")
    
    def activate_system(self, system_id: int, current_user_id: int) -> Optional[BusinessSystem]:
        """激活业务系统"""
        try:
            system = self.get(system_id)
            if not system:
                raise SystemNotFoundError("业务系统不存在")
            
            # 检查权限
            if system.owner_id != current_user_id:
                raise AuthorizationError("只有系统所有者可以激活系统")
            
            updated_system = self.update(system_id, {"status": "active"})
            return updated_system
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"系统激活失败: {str(e)}")
    
    def get_system_processes(self, system_id: int, skip: int = 0, limit: int = 100):
        """获取系统的流程列表"""
        try:
            system = self.get(system_id)
            if not system:
                raise SystemNotFoundError("业务系统不存在")
            
            processes = system.processes
            # 应用分页
            return processes[skip:skip + limit]
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"获取系统流程失败: {str(e)}")
    
    def get_system_sops(self, system_id: int, skip: int = 0, limit: int = 100):
        """获取系统的SOP列表"""
        try:
            system = self.get(system_id)
            if not system:
                raise SystemNotFoundError("业务系统不存在")
            
            sops = system.sops
            # 应用分页
            return sops[skip:skip + limit]
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"获取系统SOP失败: {str(e)}")
    
    def clone_system(self, system_id: int, new_name: str, current_user_id: int) -> BusinessSystem:
        """克隆业务系统"""
        try:
            original_system = self.get(system_id)
            if not original_system:
                raise SystemNotFoundError("原始业务系统不存在")
            
            # 创建新系统数据
            system_data = {
                "name": new_name,
                "description": f"克隆自: {original_system.name}",
                "industry": original_system.industry,
                "company_size": original_system.company_size,
                "status": "active",
                "owner_id": current_user_id
            }
            
            cloned_system = self.create(system_data)
            return cloned_system
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"系统克隆失败: {str(e)}")
    
    def transfer_ownership(self, system_id: int, new_owner_id: int, current_user_id: int) -> Optional[BusinessSystem]:
        """转移系统所有权"""
        try:
            system = self.get(system_id)
            if not system:
                raise SystemNotFoundError("业务系统不存在")
            
            # 检查权限：只有当前所有者可以转移
            if system.owner_id != current_user_id:
                raise AuthorizationError("只有系统所有者可以转移所有权")
            
            # 验证新所有者存在
            from .user_service import UserService
            user_service = UserService(self.db)
            new_owner = user_service.get(new_owner_id)
            if not new_owner:
                raise ValidationError("新所有者不存在")
            
            updated_system = self.update(system_id, {"owner_id": new_owner_id})
            return updated_system
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"所有权转移失败: {str(e)}")
    
    def get_systems_by_company_size(self, company_size: str, skip: int = 0, limit: int = 100) -> List[BusinessSystem]:
        """根据公司规模获取业务系统"""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"company_size": company_size}
        )
    
    def bulk_update_systems(self, updates: List[Dict[str, Any]], current_user_id: int) -> List[BusinessSystem]:
        """批量更新业务系统"""
        try:
            updated_systems = []
            for update_data in updates:
                system_id = update_data.get("id")
                if not system_id:
                    continue
                
                system = self.get(system_id)
                if not system:
                    continue
                
                # 检查权限
                if system.owner_id != current_user_id:
                    continue
                
                # 移除id字段
                update_fields = {k: v for k, v in update_data.items() if k != "id"}
                
                if update_fields:
                    updated_system = self.update(system_id, update_fields)
                    if updated_system:
                        updated_systems.append(updated_system)
            
            return updated_systems
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"批量更新系统失败: {str(e)}")