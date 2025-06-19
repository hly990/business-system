"""
数据模型包初始化
"""

# 导入基础模型
from .base import BaseModel, TimestampMixin, SoftDeleteMixin

# 导入用户相关模型
from .user import User

# 导入业务系统相关模型
from .system import BusinessSystem

# 导入流程相关模型
from .process import (
    BusinessProcess,
    ProcessStep,
    ProcessConnection,
    Responsibility,
    Authorization
)

# 导入SOP相关模型
from .sop import (
    SOP,
    SOPVersion,
    SOPTemplate,
    IndustryTemplate,
    WizardProgress,
    AIConversation,
    SystemConfig
)

# 导入KPI相关模型
from .kpi import (
    KPI,
    KPIData,
    KPIAlert,
    KPIDashboard,
    KPITarget
)

# 导入任务相关模型
from .task import (
    Task,
    TaskComment,
    TaskAttachment,
    TaskTimeLog,
    Notification
)

# 导出所有模型类
__all__ = [
    # 基础模型
    'BaseModel',
    'TimestampMixin',
    'SoftDeleteMixin',
    
    # 用户相关
    'User',
    
    # 业务系统相关
    'BusinessSystem',
    
    # 流程相关
    'BusinessProcess',
    'ProcessStep',
    'ProcessConnection',
    'Responsibility',
    'Authorization',
    
    # SOP相关
    'SOP',
    'SOPVersion',
    'SOPTemplate',
    'IndustryTemplate',
    'WizardProgress',
    'AIConversation',
    'SystemConfig',
    
    # KPI相关
    'KPI',
    'KPIData',
    'KPIAlert',
    'KPIDashboard',
    'KPITarget',
    
    # 任务相关
    'Task',
    'TaskComment',
    'TaskAttachment',
    'TaskTimeLog',
    'Notification',
]