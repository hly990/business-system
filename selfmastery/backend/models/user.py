"""
用户相关数据模型
"""
from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    """用户表"""
    
    __tablename__ = "users"
    
    # 基本信息
    name = Column(
        String(100),
        nullable=False,
        comment="用户姓名"
    )
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="邮箱地址"
    )
    
    role = Column(
        String(50),
        nullable=False,
        default="user",
        comment="用户角色"
    )
    
    timezone = Column(
        String(50),
        default="Asia/Shanghai",
        comment="时区设置"
    )
    
    password_hash = Column(
        String(255),
        nullable=True,
        comment="密码哈希"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 关系定义
    owned_systems = relationship(
        "BusinessSystem",
        back_populates="owner",
        foreign_keys="BusinessSystem.owner_id"
    )
    
    owned_processes = relationship(
        "BusinessProcess",
        back_populates="owner",
        foreign_keys="BusinessProcess.owner_id"
    )
    
    authored_sops = relationship(
        "SOP",
        back_populates="author",
        foreign_keys="SOP.author_id"
    )
    
    assigned_tasks = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id"
    )
    
    granted_authorizations = relationship(
        "Authorization",
        back_populates="grantor",
        foreign_keys="Authorization.grantor_id"
    )
    
    received_authorizations = relationship(
        "Authorization",
        back_populates="grantee",
        foreign_keys="Authorization.grantee_id"
    )
    
    wizard_progress = relationship(
        "WizardProgress",
        back_populates="user",
        uselist=False
    )
    
    ai_conversations = relationship(
        "AIConversation",
        back_populates="user"
    )
    
    created_templates = relationship(
        "SOPTemplate",
        back_populates="creator"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


# 创建索引
Index('idx_users_email', User.email)
Index('idx_users_role', User.role)
Index('idx_users_active', User.is_active)