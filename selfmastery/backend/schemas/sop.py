"""
SOP相关数据模式
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime


class SOPBase(BaseModel):
    """SOP基础模式"""
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    status: str = "draft"
    priority: str = "medium"

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['draft', 'review', 'published', 'archived']
        if v not in allowed_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'medium', 'high', 'critical']
        if v not in allowed_priorities:
            raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v


class SOPCreate(SOPBase):
    """SOP创建模式"""
    process_id: Optional[int] = None
    author_id: int


class SOPUpdate(BaseModel):
    """SOP更新模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    priority: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['draft', 'review', 'published', 'archived']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            allowed_priorities = ['low', 'medium', 'high', 'critical']
            if v not in allowed_priorities:
                raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v


class SOPResponse(SOPBase):
    """SOP响应模式"""
    id: int
    process_id: Optional[int] = None
    author_id: int
    current_version: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SOPVersionBase(BaseModel):
    """SOP版本基础模式"""
    version_number: int
    content: str
    change_summary: Optional[str] = None
    is_current: bool = False


class SOPVersionCreate(SOPVersionBase):
    """SOP版本创建模式"""
    sop_id: int


class SOPVersionUpdate(BaseModel):
    """SOP版本更新模式"""
    content: Optional[str] = None
    change_summary: Optional[str] = None
    is_current: Optional[bool] = None


class SOPVersionResponse(SOPVersionBase):
    """SOP版本响应模式"""
    id: int
    sop_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SOPDetail(SOPResponse):
    """SOP详情模式"""
    versions: List[SOPVersionResponse] = []
    current_content: Optional[str] = None
    versions_count: int = 0


class SOPTemplateBase(BaseModel):
    """SOP模板基础模式"""
    name: str
    description: Optional[str] = None
    category: str
    industry: Optional[str] = None
    template_content: str
    is_public: bool = False


class SOPTemplateCreate(SOPTemplateBase):
    """SOP模板创建模式"""
    creator_id: int


class SOPTemplateUpdate(BaseModel):
    """SOP模板更新模式"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    industry: Optional[str] = None
    template_content: Optional[str] = None
    is_public: Optional[bool] = None


class SOPTemplateResponse(SOPTemplateBase):
    """SOP模板响应模式"""
    id: int
    creator_id: int
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IndustryTemplateBase(BaseModel):
    """行业模板基础模式"""
    name: str
    industry: str
    description: Optional[str] = None
    template_data: Dict[str, Any]
    is_active: bool = True


class IndustryTemplateResponse(IndustryTemplateBase):
    """行业模板响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WizardProgressBase(BaseModel):
    """向导进度基础模式"""
    current_step: int = 1
    total_steps: int = 5
    step_data: Optional[Dict[str, Any]] = None
    is_completed: bool = False


class WizardProgressUpdate(BaseModel):
    """向导进度更新模式"""
    current_step: Optional[int] = None
    step_data: Optional[Dict[str, Any]] = None
    is_completed: Optional[bool] = None


class WizardProgressResponse(WizardProgressBase):
    """向导进度响应模式"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIConversationBase(BaseModel):
    """AI对话基础模式"""
    conversation_type: str = "sop_generation"
    messages: List[Dict[str, Any]] = []
    context: Optional[Dict[str, Any]] = None
    is_active: bool = True

    @validator('conversation_type')
    def validate_conversation_type(cls, v):
        allowed_types = ['sop_generation', 'process_optimization', 'general_help']
        if v not in allowed_types:
            raise ValueError(f'对话类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class AIConversationCreate(AIConversationBase):
    """AI对话创建模式"""
    user_id: int


class AIConversationUpdate(BaseModel):
    """AI对话更新模式"""
    messages: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AIConversationResponse(AIConversationBase):
    """AI对话响应模式"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SOPList(BaseModel):
    """SOP列表模式"""
    items: List[SOPResponse]
    total: int
    page: int
    size: int
    pages: int


class SOPSearch(BaseModel):
    """SOP搜索模式"""
    query: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    author_id: Optional[int] = None
    process_id: Optional[int] = None


class SOPExport(BaseModel):
    """SOP导出模式"""
    sop_ids: List[int]
    format: str = "pdf"
    include_versions: bool = False

    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['pdf', 'docx', 'html', 'markdown']
        if v not in allowed_formats:
            raise ValueError(f'导出格式必须是以下之一: {", ".join(allowed_formats)}')
        return v


class SOPImport(BaseModel):
    """SOP导入模式"""
    file_path: str
    format: str = "docx"
    author_id: int
    process_id: Optional[int] = None

    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['docx', 'pdf', 'html', 'markdown', 'txt']
        if v not in allowed_formats:
            raise ValueError(f'导入格式必须是以下之一: {", ".join(allowed_formats)}')
        return v


class SOPAnalytics(BaseModel):
    """SOP分析模式"""
    sop_id: int
    view_count: int = 0
    download_count: int = 0
    usage_frequency: float = 0.0
    last_accessed: Optional[datetime] = None
    feedback_score: Optional[float] = None