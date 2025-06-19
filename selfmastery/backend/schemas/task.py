"""
任务相关数据模式
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime, date


class TaskBase(BaseModel):
    """任务基础模式"""
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[List[str]] = []

    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'medium', 'high', 'urgent']
        if v not in allowed_priorities:
            raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'on_hold']
        if v not in allowed_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v


class TaskCreate(TaskBase):
    """任务创建模式"""
    assignee_id: Optional[int] = None
    process_id: Optional[int] = None
    sop_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """任务更新模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    tags: Optional[List[str]] = None
    assignee_id: Optional[int] = None

    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            allowed_priorities = ['low', 'medium', 'high', 'urgent']
            if v not in allowed_priorities:
                raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'on_hold']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v


class TaskResponse(TaskBase):
    """任务响应模式"""
    id: int
    assignee_id: Optional[int] = None
    process_id: Optional[int] = None
    sop_id: Optional[int] = None
    actual_hours: Optional[float] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskCommentBase(BaseModel):
    """任务评论基础模式"""
    content: str
    comment_type: str = "general"

    @validator('comment_type')
    def validate_comment_type(cls, v):
        allowed_types = ['general', 'status_update', 'question', 'solution']
        if v not in allowed_types:
            raise ValueError(f'评论类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class TaskCommentCreate(TaskCommentBase):
    """任务评论创建模式"""
    task_id: int
    author_id: int


class TaskCommentUpdate(BaseModel):
    """任务评论更新模式"""
    content: Optional[str] = None
    comment_type: Optional[str] = None

    @validator('comment_type')
    def validate_comment_type(cls, v):
        if v is not None:
            allowed_types = ['general', 'status_update', 'question', 'solution']
            if v not in allowed_types:
                raise ValueError(f'评论类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class TaskCommentResponse(TaskCommentBase):
    """任务评论响应模式"""
    id: int
    task_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskAttachmentBase(BaseModel):
    """任务附件基础模式"""
    filename: str
    file_path: str
    file_size: int
    file_type: str


class TaskAttachmentCreate(TaskAttachmentBase):
    """任务附件创建模式"""
    task_id: int
    uploaded_by: int


class TaskAttachmentResponse(TaskAttachmentBase):
    """任务附件响应模式"""
    id: int
    task_id: int
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskTimeLogBase(BaseModel):
    """任务时间记录基础模式"""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # 小时
    description: Optional[str] = None


class TaskTimeLogCreate(TaskTimeLogBase):
    """任务时间记录创建模式"""
    task_id: int
    user_id: int


class TaskTimeLogUpdate(BaseModel):
    """任务时间记录更新模式"""
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    description: Optional[str] = None


class TaskTimeLogResponse(TaskTimeLogBase):
    """任务时间记录响应模式"""
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    """通知基础模式"""
    title: str
    message: str
    notification_type: str = "info"
    is_read: bool = False

    @validator('notification_type')
    def validate_notification_type(cls, v):
        allowed_types = ['info', 'warning', 'error', 'success', 'reminder']
        if v not in allowed_types:
            raise ValueError(f'通知类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class NotificationCreate(NotificationBase):
    """通知创建模式"""
    user_id: int
    related_id: Optional[int] = None
    related_type: Optional[str] = None


class NotificationUpdate(BaseModel):
    """通知更新模式"""
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """通知响应模式"""
    id: int
    user_id: int
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskDetail(TaskResponse):
    """任务详情模式"""
    comments: List[TaskCommentResponse] = []
    attachments: List[TaskAttachmentResponse] = []
    time_logs: List[TaskTimeLogResponse] = []
    total_logged_hours: float = 0.0


class TaskAssignment(BaseModel):
    """任务分配模式"""
    task_id: int
    assignee_id: int
    assigned_by: int
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


class TaskBatch(BaseModel):
    """批量任务操作模式"""
    task_ids: List[int]
    action: str
    data: Optional[Dict[str, Any]] = None

    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['update_status', 'assign', 'set_priority', 'add_tags', 'delete']
        if v not in allowed_actions:
            raise ValueError(f'操作必须是以下之一: {", ".join(allowed_actions)}')
        return v


class TaskStats(BaseModel):
    """任务统计模式"""
    total_tasks: int = 0
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    completion_rate: float = 0.0
    average_completion_time: Optional[float] = None


class TaskAnalytics(BaseModel):
    """任务分析模式"""
    period_start: date
    period_end: date
    tasks_created: int = 0
    tasks_completed: int = 0
    average_completion_time: Optional[float] = None
    productivity_score: Optional[float] = None
    bottlenecks: List[str] = []


class TaskList(BaseModel):
    """任务列表模式"""
    items: List[TaskResponse]
    total: int
    page: int
    size: int
    pages: int


class TaskSearch(BaseModel):
    """任务搜索模式"""
    query: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    process_id: Optional[int] = None
    sop_id: Optional[int] = None
    tags: Optional[List[str]] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None


class TaskTemplate(BaseModel):
    """任务模板模式"""
    name: str
    description: Optional[str] = None
    template_data: Dict[str, Any]
    category: Optional[str] = None
    is_public: bool = False


class TaskWorkflow(BaseModel):
    """任务工作流模式"""
    name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]] = []
    is_active: bool = True