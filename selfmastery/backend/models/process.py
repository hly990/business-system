"""
业务流程相关数据模型
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class BusinessProcess(BaseModel):
    """业务流程表"""
    
    __tablename__ = "business_processes"
    
    # 基本信息
    system_id = Column(
        Integer,
        ForeignKey("business_systems.id"),
        nullable=False,
        comment="所属系统ID"
    )
    
    name = Column(
        String(200),
        nullable=False,
        comment="流程名称"
    )
    
    description = Column(
        Text,
        comment="流程描述"
    )
    
    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="负责人ID"
    )
    
    sop_id = Column(
        Integer,
        ForeignKey("sops.id"),
        nullable=True,
        comment="关联SOP文档ID"
    )
    
    # 流程属性
    status = Column(
        String(50),
        default="draft",
        comment="流程状态: draft, active, inactive, archived"
    )
    
    priority = Column(
        Integer,
        default=3,
        comment="优先级: 1-5"
    )
    
    estimated_duration = Column(
        Integer,
        comment="预估执行时间（分钟）"
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
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 关系定义
    system = relationship(
        "BusinessSystem",
        back_populates="processes"
    )
    
    owner = relationship(
        "User",
        back_populates="owned_processes",
        foreign_keys=[owner_id]
    )
    
    sop = relationship(
        "SOP",
        back_populates="processes"
    )
    
    steps = relationship(
        "ProcessStep",
        back_populates="process",
        cascade="all, delete-orphan",
        order_by="ProcessStep.step_order"
    )
    
    kpis = relationship(
        "KPI",
        back_populates="process",
        cascade="all, delete-orphan"
    )
    
    tasks = relationship(
        "Task",
        back_populates="process",
        cascade="all, delete-orphan"
    )
    
    responsibilities = relationship(
        "Responsibility",
        back_populates="process",
        cascade="all, delete-orphan"
    )
    
    # 流程连接关系
    outgoing_connections = relationship(
        "ProcessConnection",
        foreign_keys="ProcessConnection.from_process_id",
        back_populates="from_process",
        cascade="all, delete-orphan"
    )
    
    incoming_connections = relationship(
        "ProcessConnection",
        foreign_keys="ProcessConnection.to_process_id",
        back_populates="to_process",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<BusinessProcess(id={self.id}, name='{self.name}')>"
    
    @property
    def full_name(self) -> str:
        """获取完整名称（包含系统路径）"""
        return f"{self.system.full_path} > {self.name}"
    
    def get_next_processes(self) -> list:
        """获取下一步流程"""
        return [conn.to_process for conn in self.outgoing_connections]
    
    def get_previous_processes(self) -> list:
        """获取上一步流程"""
        return [conn.from_process for conn in self.incoming_connections]


class ProcessStep(BaseModel):
    """流程步骤表"""
    
    __tablename__ = "process_steps"
    
    process_id = Column(
        Integer,
        ForeignKey("business_processes.id"),
        nullable=False,
        comment="所属流程ID"
    )
    
    step_order = Column(
        Integer,
        nullable=False,
        comment="步骤顺序"
    )
    
    name = Column(
        String(200),
        nullable=False,
        comment="步骤名称"
    )
    
    description = Column(
        Text,
        comment="步骤描述"
    )
    
    responsible_role = Column(
        String(100),
        comment="负责角色"
    )
    
    estimated_duration = Column(
        Integer,
        comment="预估执行时间（分钟）"
    )
    
    is_required = Column(
        Boolean,
        default=True,
        comment="是否必需步骤"
    )
    
    # 关系定义
    process = relationship(
        "BusinessProcess",
        back_populates="steps"
    )
    
    def __repr__(self):
        return f"<ProcessStep(id={self.id}, name='{self.name}', order={self.step_order})>"


class ProcessConnection(BaseModel):
    """流程连接关系表"""
    
    __tablename__ = "process_connections"
    
    from_process_id = Column(
        Integer,
        ForeignKey("business_processes.id"),
        nullable=False,
        comment="起始流程ID"
    )
    
    to_process_id = Column(
        Integer,
        ForeignKey("business_processes.id"),
        nullable=False,
        comment="目标流程ID"
    )
    
    connection_type = Column(
        String(50),
        default="sequence",
        comment="连接类型: sequence, condition, parallel"
    )
    
    condition_expression = Column(
        Text,
        comment="条件表达式（JSON格式）"
    )
    
    # 关系定义
    from_process = relationship(
        "BusinessProcess",
        foreign_keys=[from_process_id],
        back_populates="outgoing_connections"
    )
    
    to_process = relationship(
        "BusinessProcess",
        foreign_keys=[to_process_id],
        back_populates="incoming_connections"
    )
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('from_process_id', 'to_process_id', name='uq_process_connection'),
    )
    
    def __repr__(self):
        return f"<ProcessConnection(from={self.from_process_id}, to={self.to_process_id})>"


class Responsibility(BaseModel):
    """权责分配表"""
    
    __tablename__ = "responsibilities"
    
    process_id = Column(
        Integer,
        ForeignKey("business_processes.id"),
        nullable=False,
        comment="流程ID"
    )
    
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    role_type = Column(
        String(50),
        nullable=False,
        comment="角色类型: owner, executor, reviewer, approver"
    )
    
    description = Column(
        Text,
        comment="职责描述"
    )
    
    # 关系定义
    process = relationship(
        "BusinessProcess",
        back_populates="responsibilities"
    )
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<Responsibility(process_id={self.process_id}, user_id={self.user_id}, role='{self.role_type}')>"


class Authorization(BaseModel):
    """授权管理表"""
    
    __tablename__ = "authorizations"
    
    grantor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="授权人ID"
    )
    
    grantee_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="被授权人ID"
    )
    
    resource_type = Column(
        String(50),
        nullable=False,
        comment="资源类型: system, process, kpi"
    )
    
    resource_id = Column(
        Integer,
        nullable=False,
        comment="资源ID"
    )
    
    permission_level = Column(
        String(50),
        nullable=False,
        comment="权限级别: read, write, admin"
    )
    
    start_date = Column(
        DateTime,
        comment="授权开始日期"
    )
    
    end_date = Column(
        DateTime,
        comment="授权结束日期"
    )
    
    conditions = Column(
        Text,
        comment="授权条件（JSON格式）"
    )
    
    status = Column(
        String(50),
        default="active",
        comment="授权状态: active, inactive, expired"
    )
    
    # 关系定义
    grantor = relationship(
        "User",
        foreign_keys=[grantor_id],
        back_populates="granted_authorizations"
    )
    
    grantee = relationship(
        "User",
        foreign_keys=[grantee_id],
        back_populates="received_authorizations"
    )
    
    def __repr__(self):
        return f"<Authorization(grantor={self.grantor_id}, grantee={self.grantee_id}, resource={self.resource_type}:{self.resource_id})>"


# 创建索引
Index('idx_business_processes_system', BusinessProcess.system_id)
Index('idx_business_processes_owner', BusinessProcess.owner_id)
Index('idx_business_processes_status', BusinessProcess.status)
Index('idx_business_processes_system_status', BusinessProcess.system_id, BusinessProcess.status)

Index('idx_process_steps_process', ProcessStep.process_id)
Index('idx_process_steps_order', ProcessStep.process_id, ProcessStep.step_order)

Index('idx_process_connections_from', ProcessConnection.from_process_id)
Index('idx_process_connections_to', ProcessConnection.to_process_id)

Index('idx_responsibilities_process', Responsibility.process_id)
Index('idx_responsibilities_user', Responsibility.user_id)

Index('idx_authorizations_grantee', Authorization.grantee_id)
Index('idx_authorizations_resource', Authorization.resource_type, Authorization.resource_id)
Index('idx_authorizations_active', Authorization.grantee_id, Authorization.status, Authorization.end_date)