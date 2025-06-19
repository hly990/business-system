"""
基础数据模型类
"""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, DateTime, Boolean, text
from sqlalchemy.ext.declarative import declared_attr
from selfmastery.config.database import Base


class TimestampMixin:
    """时间戳混入类"""
    
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="创建时间"
        )
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="更新时间"
        )


class SoftDeleteMixin:
    """软删除混入类"""
    
    @declared_attr
    def is_deleted(cls):
        return Column(
            Boolean,
            default=False,
            server_default=text("FALSE"),
            nullable=False,
            comment="是否已删除"
        )
    
    @declared_attr
    def deleted_at(cls):
        return Column(
            DateTime,
            nullable=True,
            comment="删除时间"
        )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """基础模型类"""
    
    __abstract__ = True
    
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )
    
    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """转换为字典"""
        exclude = exclude or []
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude: Optional[list] = None) -> None:
        """从字典更新属性"""
        exclude = exclude or ['id', 'created_at', 'updated_at']
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
    
    def soft_delete(self) -> None:
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """恢复删除"""
        self.is_deleted = False
        self.deleted_at = None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"