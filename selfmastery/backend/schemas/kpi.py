"""
KPI相关数据模式
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, validator
from datetime import datetime, date
from decimal import Decimal


class KPIBase(BaseModel):
    """KPI基础模式"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = "number"
    target_value: Optional[float] = None
    target_type: str = "higher_better"
    frequency: str = "monthly"
    is_active: bool = True

    @validator('unit')
    def validate_unit(cls, v):
        allowed_units = ['number', 'percentage', 'currency', 'time', 'ratio']
        if v not in allowed_units:
            raise ValueError(f'单位必须是以下之一: {", ".join(allowed_units)}')
        return v

    @validator('target_type')
    def validate_target_type(cls, v):
        allowed_types = ['higher_better', 'lower_better', 'target_range']
        if v not in allowed_types:
            raise ValueError(f'目标类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('frequency')
    def validate_frequency(cls, v):
        allowed_frequencies = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        if v not in allowed_frequencies:
            raise ValueError(f'频率必须是以下之一: {", ".join(allowed_frequencies)}')
        return v


class KPICreate(KPIBase):
    """KPI创建模式"""
    system_id: Optional[int] = None
    process_id: Optional[int] = None


class KPIUpdate(BaseModel):
    """KPI更新模式"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    target_type: Optional[str] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('unit')
    def validate_unit(cls, v):
        if v is not None:
            allowed_units = ['number', 'percentage', 'currency', 'time', 'ratio']
            if v not in allowed_units:
                raise ValueError(f'单位必须是以下之一: {", ".join(allowed_units)}')
        return v

    @validator('target_type')
    def validate_target_type(cls, v):
        if v is not None:
            allowed_types = ['higher_better', 'lower_better', 'target_range']
            if v not in allowed_types:
                raise ValueError(f'目标类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('frequency')
    def validate_frequency(cls, v):
        if v is not None:
            allowed_frequencies = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
            if v not in allowed_frequencies:
                raise ValueError(f'频率必须是以下之一: {", ".join(allowed_frequencies)}')
        return v


class KPIResponse(KPIBase):
    """KPI响应模式"""
    id: int
    system_id: Optional[int] = None
    process_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KPIDataBase(BaseModel):
    """KPI数据基础模式"""
    value: float
    period_start: date
    period_end: date
    notes: Optional[str] = None
    data_source: Optional[str] = None


class KPIDataCreate(KPIDataBase):
    """KPI数据创建模式"""
    kpi_id: int


class KPIDataUpdate(BaseModel):
    """KPI数据更新模式"""
    value: Optional[float] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    notes: Optional[str] = None
    data_source: Optional[str] = None


class KPIDataResponse(KPIDataBase):
    """KPI数据响应模式"""
    id: int
    kpi_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KPIAlertBase(BaseModel):
    """KPI警报基础模式"""
    alert_type: str = "threshold"
    condition: str = "above"
    threshold_value: float
    message: Optional[str] = None
    is_active: bool = True

    @validator('alert_type')
    def validate_alert_type(cls, v):
        allowed_types = ['threshold', 'trend', 'anomaly']
        if v not in allowed_types:
            raise ValueError(f'警报类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('condition')
    def validate_condition(cls, v):
        allowed_conditions = ['above', 'below', 'equal', 'not_equal']
        if v not in allowed_conditions:
            raise ValueError(f'条件必须是以下之一: {", ".join(allowed_conditions)}')
        return v


class KPIAlertCreate(KPIAlertBase):
    """KPI警报创建模式"""
    kpi_id: int


class KPIAlertResponse(KPIAlertBase):
    """KPI警报响应模式"""
    id: int
    kpi_id: int
    triggered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KPIDashboardBase(BaseModel):
    """KPI仪表板基础模式"""
    name: str
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    is_public: bool = False


class KPIDashboardCreate(KPIDashboardBase):
    """KPI仪表板创建模式"""
    owner_id: int
    kpi_ids: List[int] = []


class KPIDashboardUpdate(BaseModel):
    """KPI仪表板更新模式"""
    name: Optional[str] = None
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    kpi_ids: Optional[List[int]] = None


class KPIDashboardResponse(KPIDashboardBase):
    """KPI仪表板响应模式"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KPITargetBase(BaseModel):
    """KPI目标基础模式"""
    target_value: float
    target_period_start: date
    target_period_end: date
    description: Optional[str] = None


class KPITargetCreate(KPITargetBase):
    """KPI目标创建模式"""
    kpi_id: int


class KPITargetResponse(KPITargetBase):
    """KPI目标响应模式"""
    id: int
    kpi_id: int
    achievement_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KPIDetail(KPIResponse):
    """KPI详情模式"""
    recent_data: List[KPIDataResponse] = []
    current_value: Optional[float] = None
    target_achievement: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    alerts: List[KPIAlertResponse] = []


class KPIAnalytics(BaseModel):
    """KPI分析模式"""
    kpi_id: int
    period_start: date
    period_end: date
    average_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    trend_direction: Optional[str] = None
    volatility: Optional[float] = None
    achievement_rate: Optional[float] = None


class KPIComparison(BaseModel):
    """KPI比较模式"""
    kpi_ids: List[int]
    period_start: date
    period_end: date
    comparison_type: str = "value"

    @validator('comparison_type')
    def validate_comparison_type(cls, v):
        allowed_types = ['value', 'trend', 'achievement']
        if v not in allowed_types:
            raise ValueError(f'比较类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class KPIReport(BaseModel):
    """KPI报告模式"""
    title: str
    period_start: date
    period_end: date
    kpi_ids: List[int]
    report_type: str = "summary"
    format: str = "pdf"

    @validator('report_type')
    def validate_report_type(cls, v):
        allowed_types = ['summary', 'detailed', 'trend', 'comparison']
        if v not in allowed_types:
            raise ValueError(f'报告类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['pdf', 'excel', 'html', 'json']
        if v not in allowed_formats:
            raise ValueError(f'格式必须是以下之一: {", ".join(allowed_formats)}')
        return v


class KPIList(BaseModel):
    """KPI列表模式"""
    items: List[KPIResponse]
    total: int
    page: int
    size: int
    pages: int


class KPISearch(BaseModel):
    """KPI搜索模式"""
    query: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None
    system_id: Optional[int] = None
    process_id: Optional[int] = None