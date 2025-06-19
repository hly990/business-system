"""
业务系统相关数据模式
"""
from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime


class BusinessSystemBase(BaseModel):
    """业务系统基础模式"""
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    status: str = "active"

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['active', 'inactive', 'archived']
        if v not in allowed_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @validator('company_size')
    def validate_company_size(cls, v):
        if v is not None:
            allowed_sizes = ['startup', 'small', 'medium', 'large', 'enterprise']
            if v not in allowed_sizes:
                raise ValueError(f'公司规模必须是以下之一: {", ".join(allowed_sizes)}')
        return v


class BusinessSystemCreate(BusinessSystemBase):
    """业务系统创建模式"""
    owner_id: int


class BusinessSystemUpdate(BaseModel):
    """业务系统更新模式"""
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['active', 'inactive', 'archived']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @validator('company_size')
    def validate_company_size(cls, v):
        if v is not None:
            allowed_sizes = ['startup', 'small', 'medium', 'large', 'enterprise']
            if v not in allowed_sizes:
                raise ValueError(f'公司规模必须是以下之一: {", ".join(allowed_sizes)}')
        return v


class BusinessSystemResponse(BusinessSystemBase):
    """业务系统响应模式"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessSystemDetail(BusinessSystemResponse):
    """业务系统详情模式"""
    processes_count: int = 0
    sops_count: int = 0
    tasks_count: int = 0
    active_tasks_count: int = 0


class BusinessSystemStats(BaseModel):
    """业务系统统计模式"""
    total_processes: int = 0
    active_processes: int = 0
    total_sops: int = 0
    published_sops: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0


class BusinessSystemList(BaseModel):
    """业务系统列表模式"""
    items: List[BusinessSystemResponse]
    total: int
    page: int
    size: int
    pages: int


class BusinessSystemSearch(BaseModel):
    """业务系统搜索模式"""
    query: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[int] = None


class BusinessSystemExport(BaseModel):
    """业务系统导出模式"""
    format: str = "json"  # json, csv, excel
    include_processes: bool = True
    include_sops: bool = True
    include_tasks: bool = False

    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['json', 'csv', 'excel']
        if v not in allowed_formats:
            raise ValueError(f'导出格式必须是以下之一: {", ".join(allowed_formats)}')
        return v


class BusinessSystemImport(BaseModel):
    """业务系统导入模式"""
    file_path: str
    format: str = "json"
    overwrite_existing: bool = False

    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['json', 'csv', 'excel']
        if v not in allowed_formats:
            raise ValueError(f'导入格式必须是以下之一: {", ".join(allowed_formats)}')
        return v