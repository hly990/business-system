"""
基础服务类，提供通用的CRUD操作
"""
from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc
from ..models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseService(Generic[ModelType]):
    """基础服务类"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        初始化基础服务
        
        Args:
            model: 数据模型类
            db: 数据库会话
        """
        self.model = model
        self.db = db
    
    def create(self, obj_data: Dict[str, Any]) -> ModelType:
        """
        创建新记录
        
        Args:
            obj_data: 对象数据字典
            
        Returns:
            创建的对象实例
            
        Raises:
            SQLAlchemyError: 数据库操作异常
        """
        try:
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get(self, obj_id: int, include_deleted: bool = False) -> Optional[ModelType]:
        """
        根据ID获取单个记录
        
        Args:
            obj_id: 对象ID
            include_deleted: 是否包含已删除的记录
            
        Returns:
            对象实例或None
        """
        query = self.db.query(self.model).filter(self.model.id == obj_id)
        
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        return query.first()
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """
        获取多个记录
        
        Args:
            skip: 跳过记录数
            limit: 限制记录数
            include_deleted: 是否包含已删除的记录
            filters: 过滤条件字典
            order_by: 排序字段
            order_desc: 是否降序排列
            
        Returns:
            对象实例列表
        """
        query = self.db.query(self.model)
        
        # 软删除过滤
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, field).in_(value))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        # 排序
        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(asc(order_field))
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, obj_id: int, obj_data: Dict[str, Any]) -> Optional[ModelType]:
        """
        更新记录
        
        Args:
            obj_id: 对象ID
            obj_data: 更新数据字典
            
        Returns:
            更新后的对象实例或None
            
        Raises:
            SQLAlchemyError: 数据库操作异常
        """
        try:
            db_obj = self.get(obj_id)
            if db_obj:
                db_obj.update_from_dict(obj_data)
                self.db.commit()
                self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def delete(self, obj_id: int, soft_delete: bool = True) -> bool:
        """
        删除记录
        
        Args:
            obj_id: 对象ID
            soft_delete: 是否软删除
            
        Returns:
            是否删除成功
            
        Raises:
            SQLAlchemyError: 数据库操作异常
        """
        try:
            db_obj = self.get(obj_id)
            if db_obj:
                if soft_delete and hasattr(db_obj, 'soft_delete'):
                    db_obj.soft_delete()
                else:
                    self.db.delete(db_obj)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def restore(self, obj_id: int) -> Optional[ModelType]:
        """
        恢复软删除的记录
        
        Args:
            obj_id: 对象ID
            
        Returns:
            恢复后的对象实例或None
            
        Raises:
            SQLAlchemyError: 数据库操作异常
        """
        try:
            db_obj = self.get(obj_id, include_deleted=True)
            if db_obj and hasattr(db_obj, 'restore'):
                db_obj.restore()
                self.db.commit()
                self.db.refresh(db_obj)
                return db_obj
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def count(self, filters: Optional[Dict[str, Any]] = None, include_deleted: bool = False) -> int:
        """
        统计记录数量
        
        Args:
            filters: 过滤条件字典
            include_deleted: 是否包含已删除的记录
            
        Returns:
            记录数量
        """
        query = self.db.query(self.model)
        
        # 软删除过滤
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, field).in_(value))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        return query.count()
    
    def exists(self, obj_id: int, include_deleted: bool = False) -> bool:
        """
        检查记录是否存在
        
        Args:
            obj_id: 对象ID
            include_deleted: 是否包含已删除的记录
            
        Returns:
            是否存在
        """
        return self.get(obj_id, include_deleted) is not None
    
    def search(
        self,
        search_term: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        搜索记录
        
        Args:
            search_term: 搜索关键词
            search_fields: 搜索字段列表
            skip: 跳过记录数
            limit: 限制记录数
            include_deleted: 是否包含已删除的记录
            
        Returns:
            匹配的对象实例列表
        """
        query = self.db.query(self.model)
        
        # 软删除过滤
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        # 构建搜索条件
        if search_term and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    field_attr = getattr(self.model, field)
                    search_conditions.append(field_attr.ilike(f"%{search_term}%"))
            
            if search_conditions:
                query = query.filter(or_(*search_conditions))
        
        return query.offset(skip).limit(limit).all()
    
    def bulk_create(self, obj_data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        批量创建记录
        
        Args:
            obj_data_list: 对象数据字典列表
            
        Returns:
            创建的对象实例列表
            
        Raises:
            SQLAlchemyError: 数据库操作异常
        """
        try:
            db_objs = [self.model(**obj_data) for obj_data in obj_data_list]
            self.db.add_all(db_objs)
            self.db.commit()
            for db_obj in db_objs:
                self.db.refresh(db_obj)
            return db_objs
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> List[ModelType]:
        """
        批量更新记录
        
        Args:
            updates: 更新数据列表，每个字典必须包含'id'字段
            
        Returns:
            更新后的对象实例列表
            
        Raises:
            SQLAlchemyError: 数据库操作异常
        """
        try:
            updated_objs = []
            for update_data in updates:
                obj_id = update_data.pop('id')
                db_obj = self.get(obj_id)
                if db_obj:
                    db_obj.update_from_dict(update_data)
                    updated_objs.append(db_obj)
            
            self.db.commit()
            for db_obj in updated_objs:
                self.db.refresh(db_obj)
            return updated_objs
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_by_field(self, field: str, value: Any, include_deleted: bool = False) -> Optional[ModelType]:
        """
        根据指定字段获取记录
        
        Args:
            field: 字段名
            value: 字段值
            include_deleted: 是否包含已删除的记录
            
        Returns:
            对象实例或None
        """
        if not hasattr(self.model, field):
            return None
        
        query = self.db.query(self.model).filter(getattr(self.model, field) == value)
        
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        return query.first()