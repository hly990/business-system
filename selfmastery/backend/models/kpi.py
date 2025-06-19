"""
KPI相关数据模型
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class KPI(BaseModel):
    """KPI指标表"""
    
    __tablename__ = "kpis"
    
    # 基本信息
    process_id = Column(
        Integer,
        ForeignKey("business_processes.id"),
        nullable=False,
        comment="关联流程ID"
    )
    
    name = Column(
        String(200),
        nullable=False,
        comment="KPI名称"
    )
    
    description = Column(
        Text,
        comment="KPI描述"
    )
    
    # 指标配置
    metric_type = Column(
        String(50),
        nullable=False,
        comment="指标类型: count, percentage, amount, duration, ratio"
    )
    
    target_value = Column(
        Float,
        comment="目标值"
    )
    
    current_value = Column(
        Float,
        default=0.0,
        comment="当前值"
    )
    
    unit = Column(
        String(50),
        comment="单位"
    )
    
    # 数据源配置
    data_source = Column(
        String(100),
        comment="数据源: manual, api, webhook, file, database"
    )
    
    source_config = Column(
        Text,
        comment="数据源配置（JSON格式）"
    )
    
    update_frequency = Column(
        String(50),
        default="daily",
        comment="更新频率: realtime, hourly, daily, weekly, monthly"
    )
    
    # 阈值配置
    warning_threshold = Column(
        Float,
        comment="警告阈值"
    )
    
    critical_threshold = Column(
        Float,
        comment="严重阈值"
    )
    
    threshold_direction = Column(
        String(10),
        default="above",
        comment="阈值方向: above, below"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 关系定义
    process = relationship(
        "BusinessProcess",
        back_populates="kpis"
    )
    
    data_points = relationship(
        "KPIData",
        back_populates="kpi",
        cascade="all, delete-orphan",
        order_by="KPIData.recorded_at.desc()"
    )
    
    def __repr__(self):
        return f"<KPI(id={self.id}, name='{self.name}', type='{self.metric_type}')>"
    
    @property
    def latest_value(self) -> Float:
        """获取最新数据值"""
        if self.data_points:
            return self.data_points[0].value
        return self.current_value
    
    @property
    def achievement_rate(self) -> Float:
        """获取达成率"""
        if self.target_value and self.target_value != 0:
            return (self.current_value / self.target_value) * 100
        return 0.0
    
    @property
    def status(self) -> str:
        """获取状态"""
        current = self.current_value
        
        if self.critical_threshold:
            if self.threshold_direction == "above" and current >= self.critical_threshold:
                return "critical"
            elif self.threshold_direction == "below" and current <= self.critical_threshold:
                return "critical"
        
        if self.warning_threshold:
            if self.threshold_direction == "above" and current >= self.warning_threshold:
                return "warning"
            elif self.threshold_direction == "below" and current <= self.warning_threshold:
                return "warning"
        
        return "normal"
    
    def add_data_point(self, value: float, source: str = None, notes: str = None) -> 'KPIData':
        """添加数据点"""
        data_point = KPIData(
            kpi_id=self.id,
            value=value,
            source=source,
            notes=notes
        )
        
        # 更新当前值
        self.current_value = value
        
        return data_point


class KPIData(BaseModel):
    """KPI历史数据表"""
    
    __tablename__ = "kpi_data"
    
    kpi_id = Column(
        Integer,
        ForeignKey("kpis.id"),
        nullable=False,
        comment="KPI ID"
    )
    
    value = Column(
        Float,
        nullable=False,
        comment="数据值"
    )
    
    recorded_at = Column(
        DateTime,
        nullable=False,
        comment="记录时间"
    )
    
    source = Column(
        String(100),
        comment="数据来源"
    )
    
    notes = Column(
        Text,
        comment="备注说明"
    )
    
    # 关系定义
    kpi = relationship(
        "KPI",
        back_populates="data_points"
    )
    
    def __repr__(self):
        return f"<KPIData(id={self.id}, kpi_id={self.kpi_id}, value={self.value})>"


class KPIAlert(BaseModel):
    """KPI预警表"""
    
    __tablename__ = "kpi_alerts"
    
    kpi_id = Column(
        Integer,
        ForeignKey("kpis.id"),
        nullable=False,
        comment="KPI ID"
    )
    
    alert_type = Column(
        String(50),
        nullable=False,
        comment="预警类型: threshold, trend, anomaly"
    )
    
    severity = Column(
        String(20),
        nullable=False,
        comment="严重程度: info, warning, critical"
    )
    
    message = Column(
        Text,
        nullable=False,
        comment="预警消息"
    )
    
    trigger_value = Column(
        Float,
        comment="触发值"
    )
    
    is_acknowledged = Column(
        Boolean,
        default=False,
        comment="是否已确认"
    )
    
    acknowledged_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="确认人ID"
    )
    
    acknowledged_at = Column(
        DateTime,
        nullable=True,
        comment="确认时间"
    )
    
    # 关系定义
    kpi = relationship("KPI")
    acknowledger = relationship("User")
    
    def __repr__(self):
        return f"<KPIAlert(id={self.id}, kpi_id={self.kpi_id}, severity='{self.severity}')>"


class KPIDashboard(BaseModel):
    """KPI仪表盘表"""
    
    __tablename__ = "kpi_dashboards"
    
    name = Column(
        String(200),
        nullable=False,
        comment="仪表盘名称"
    )
    
    description = Column(
        Text,
        comment="仪表盘描述"
    )
    
    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="所有者ID"
    )
    
    layout_config = Column(
        Text,
        comment="布局配置（JSON格式）"
    )
    
    kpi_config = Column(
        Text,
        comment="KPI配置（JSON格式）"
    )
    
    is_public = Column(
        Boolean,
        default=False,
        comment="是否公开"
    )
    
    refresh_interval = Column(
        Integer,
        default=300,
        comment="刷新间隔（秒）"
    )
    
    # 关系定义
    owner = relationship("User")
    
    def __repr__(self):
        return f"<KPIDashboard(id={self.id}, name='{self.name}')>"


class KPITarget(BaseModel):
    """KPI目标表"""
    
    __tablename__ = "kpi_targets"
    
    kpi_id = Column(
        Integer,
        ForeignKey("kpis.id"),
        nullable=False,
        comment="KPI ID"
    )
    
    target_period = Column(
        String(50),
        nullable=False,
        comment="目标周期: daily, weekly, monthly, quarterly, yearly"
    )
    
    target_value = Column(
        Float,
        nullable=False,
        comment="目标值"
    )
    
    start_date = Column(
        DateTime,
        nullable=False,
        comment="开始日期"
    )
    
    end_date = Column(
        DateTime,
        nullable=False,
        comment="结束日期"
    )
    
    description = Column(
        Text,
        comment="目标描述"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        comment="是否激活"
    )
    
    # 关系定义
    kpi = relationship("KPI")
    
    def __repr__(self):
        return f"<KPITarget(id={self.id}, kpi_id={self.kpi_id}, period='{self.target_period}')>"


# 创建索引
Index('idx_kpis_process', KPI.process_id)
Index('idx_kpis_active', KPI.is_active)
Index('idx_kpis_type', KPI.metric_type)
Index('idx_kpis_source', KPI.data_source)

Index('idx_kpi_data_kpi', KPIData.kpi_id)
Index('idx_kpi_data_recorded', KPIData.recorded_at)
Index('idx_kpi_data_kpi_time', KPIData.kpi_id, KPIData.recorded_at)

Index('idx_kpi_alerts_kpi', KPIAlert.kpi_id)
Index('idx_kpi_alerts_severity', KPIAlert.severity)
Index('idx_kpi_alerts_acknowledged', KPIAlert.is_acknowledged)

Index('idx_kpi_dashboards_owner', KPIDashboard.owner_id)
Index('idx_kpi_dashboards_public', KPIDashboard.is_public)

Index('idx_kpi_targets_kpi', KPITarget.kpi_id)
Index('idx_kpi_targets_period', KPITarget.target_period)
Index('idx_kpi_targets_active', KPITarget.is_active)
Index('idx_kpi_targets_dates', KPITarget.start_date, KPITarget.end_date)