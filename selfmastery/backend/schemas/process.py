"""
业务流程相关数据模式
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime


class BusinessProcessBase(BaseModel):
    """业务流程基础模式"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: str = "medium"
    status: str = "draft"

    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'medium', 'high', 'critical']
        if v not in allowed_priorities:
            raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['draft', 'active', 'inactive', 'archived']
        if v not in allowed_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v


class BusinessProcessCreate(BusinessProcessBase):
    """业务流程创建模式"""
    system_id: int
    owner_id: int


class BusinessProcessUpdate(BaseModel):
    """业务流程更新模式"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            allowed_priorities = ['low', 'medium', 'high', 'critical']
            if v not in allowed_priorities:
                raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['draft', 'active', 'inactive', 'archived']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v


class BusinessProcessResponse(BusinessProcessBase):
    """业务流程响应模式"""
    id: int
    system_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProcessStepBase(BaseModel):
    """流程步骤基础模式"""
    name: str
    description: Optional[str] = None
    step_type: str = "manual"
    position: int
    is_required: bool = True
    estimated_duration: Optional[int] = None  # 预估时长(分钟)
    config: Optional[Dict[str, Any]] = None

    @validator('step_type')
    def validate_step_type(cls, v):
        allowed_types = ['manual', 'automated', 'approval', 'notification', 'condition']
        if v not in allowed_types:
            raise ValueError(f'步骤类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class ProcessStepCreate(ProcessStepBase):
    """流程步骤创建模式"""
    process_id: int


class ProcessStepUpdate(BaseModel):
    """流程步骤更新模式"""
    name: Optional[str] = None
    description: Optional[str] = None
    step_type: Optional[str] = None
    position: Optional[int] = None
    is_required: Optional[bool] = None
    estimated_duration: Optional[int] = None
    config: Optional[Dict[str, Any]] = None

    @validator('step_type')
    def validate_step_type(cls, v):
        if v is not None:
            allowed_types = ['manual', 'automated', 'approval', 'notification', 'condition']
            if v not in allowed_types:
                raise ValueError(f'步骤类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class ProcessStepResponse(ProcessStepBase):
    """流程步骤响应模式"""
    id: int
    process_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProcessConnectionBase(BaseModel):
    """流程连接基础模式"""
    from_step_id: int
    to_step_id: int
    condition: Optional[str] = None
    condition_type: str = "always"

    @validator('condition_type')
    def validate_condition_type(cls, v):
        allowed_types = ['always', 'success', 'failure', 'condition']
        if v not in allowed_types:
            raise ValueError(f'条件类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class ProcessConnectionCreate(ProcessConnectionBase):
    """流程连接创建模式"""
    process_id: int


class ProcessConnectionResponse(ProcessConnectionBase):
    """流程连接响应模式"""
    id: int
    process_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessProcessDetail(BusinessProcessResponse):
    """业务流程详情模式"""
    steps: List[ProcessStepResponse] = []
    connections: List[ProcessConnectionResponse] = []
    steps_count: int = 0
    sops_count: int = 0


class ProcessExecution(BaseModel):
    """流程执行模式"""
    process_id: int
    executor_id: int
    input_data: Optional[Dict[str, Any]] = None
    priority: str = "medium"

    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'medium', 'high', 'critical']
        if v not in allowed_priorities:
            raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v


class ProcessExecutionStatus(BaseModel):
    """流程执行状态模式"""
    execution_id: int
    status: str
    current_step_id: Optional[int] = None
    progress: float = 0.0
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ProcessTemplate(BaseModel):
    """流程模板模式"""
    name: str
    description: Optional[str] = None
    category: str
    industry: Optional[str] = None
    template_data: Dict[str, Any]
    is_public: bool = False


class ProcessAnalytics(BaseModel):
    """流程分析模式"""
    process_id: int
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration: Optional[float] = None
    bottleneck_steps: List[int] = []
    efficiency_score: Optional[float] = None


class ProcessList(BaseModel):
    """流程列表模式"""
    items: List[BusinessProcessResponse]
    total: int
    page: int
    size: int
    pages: int


class ProcessSearch(BaseModel):
    """流程搜索模式"""
    query: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    system_id: Optional[int] = None
    owner_id: Optional[int] = None