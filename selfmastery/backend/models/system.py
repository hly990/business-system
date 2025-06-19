"""
业务系统相关数据模型
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class BusinessSystem(BaseModel):
    """业务系统表"""
    
    __tablename__ = "business_systems"
    
    # 基本信息
    name = Column(
        String(200),
        nullable=False,
        comment="系统名称"
    )
    
    description = Column(
        Text,
        comment="系统描述"
    )
    
    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="负责人ID"
    )
    
    parent_id = Column(
        Integer,
        ForeignKey("business_systems.id"),
        nullable=True,
        comment="父系统ID"
    )
    
    # 图形位置信息
    position_x = Column(
        Float,
        default=0.0,
        comment="X坐标位置"
    )
    
    position_y = Column(
        Float,
        default=0.0,
        comment="Y坐标位置"
    )
    
    # 显示属性
    color = Column(
        String(7),
        default="#1E40AF",
        comment="显示颜色"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 关系定义
    owner = relationship(
        "User",
        back_populates="owned_systems",
        foreign_keys=[owner_id]
    )
    
    parent = relationship(
        "BusinessSystem",
        remote_side="BusinessSystem.id",
        back_populates="children"
    )
    
    children = relationship(
        "BusinessSystem",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
    processes = relationship(
        "BusinessProcess",
        back_populates="system",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<BusinessSystem(id={self.id}, name='{self.name}')>"
    
    @property
    def full_path(self) -> str:
        """获取完整路径"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    @property
    def level(self) -> int:
        """获取层级深度"""
        if self.parent:
            return self.parent.level + 1
        return 0
    
    def get_all_children(self) -> list:
        """获取所有子系统（递归）"""
        result = []
        for child in self.children:
            result.append(child)
            result.extend(child.get_all_children())
        return result
    
    def get_process_count(self) -> int:
        """获取流程数量（包含子系统）"""
        count = len(self.processes)
        for child in self.children:
            count += child.get_process_count()
        return count


# 创建索引
Index('idx_business_systems_owner', BusinessSystem.owner_id)
Index('idx_business_systems_parent', BusinessSystem.parent_id)
Index('idx_business_systems_active', BusinessSystem.is_active)
Index('idx_business_systems_name', BusinessSystem.name)