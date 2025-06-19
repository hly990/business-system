"""
SOP相关数据模型
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class SOP(BaseModel):
    """SOP标准操作程序表"""
    
    __tablename__ = "sops"
    
    # 基本信息
    title = Column(
        String(200),
        nullable=False,
        comment="SOP标题"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="SOP内容（Markdown格式）"
    )
    
    version = Column(
        String(20),
        default="1.0",
        comment="版本号"
    )
    
    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="作者ID"
    )
    
    status = Column(
        String(50),
        default="draft",
        comment="状态: draft, review, approved, archived"
    )
    
    media_refs = Column(
        Text,
        comment="媒体文件引用（JSON格式）"
    )
    
    template_id = Column(
        Integer,
        ForeignKey("sop_templates.id"),
        nullable=True,
        comment="模板ID"
    )
    
    # 关系定义
    author = relationship(
        "User",
        back_populates="authored_sops",
        foreign_keys=[author_id]
    )
    
    template = relationship(
        "SOPTemplate",
        back_populates="sops"
    )
    
    versions = relationship(
        "SOPVersion",
        back_populates="sop",
        cascade="all, delete-orphan",
        order_by="SOPVersion.version_number.desc()"
    )
    
    processes = relationship(
        "BusinessProcess",
        back_populates="sop"
    )
    
    def __repr__(self):
        return f"<SOP(id={self.id}, title='{self.title}', version='{self.version}')>"
    
    @property
    def latest_version(self):
        """获取最新版本"""
        if self.versions:
            return self.versions[0]
        return None
    
    def create_new_version(self, content: str, author_id: int, change_notes: str = None) -> 'SOPVersion':
        """创建新版本"""
        latest = self.latest_version
        new_version_number = (latest.version_number + 1) if latest else 1
        
        new_version = SOPVersion(
            sop_id=self.id,
            version_number=new_version_number,
            content=content,
            author_id=author_id,
            change_notes=change_notes
        )
        
        # 更新主表版本号
        self.version = f"{new_version_number}.0"
        self.content = content
        
        return new_version


class SOPVersion(BaseModel):
    """SOP版本表"""
    
    __tablename__ = "sop_versions"
    
    sop_id = Column(
        Integer,
        ForeignKey("sops.id"),
        nullable=False,
        comment="SOP ID"
    )
    
    version_number = Column(
        Integer,
        nullable=False,
        comment="版本号"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="版本内容"
    )
    
    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="版本作者ID"
    )
    
    change_notes = Column(
        Text,
        comment="变更说明"
    )
    
    is_current = Column(
        Boolean,
        default=False,
        comment="是否为当前版本"
    )
    
    # 关系定义
    sop = relationship(
        "SOP",
        back_populates="versions"
    )
    
    author = relationship("User")
    
    def __repr__(self):
        return f"<SOPVersion(id={self.id}, sop_id={self.sop_id}, version={self.version_number})>"


class SOPTemplate(BaseModel):
    """SOP模板表"""
    
    __tablename__ = "sop_templates"
    
    name = Column(
        String(200),
        nullable=False,
        comment="模板名称"
    )
    
    category = Column(
        String(100),
        comment="模板分类"
    )
    
    content_template = Column(
        Text,
        nullable=False,
        comment="模板内容"
    )
    
    variables = Column(
        Text,
        comment="模板变量（JSON格式）"
    )
    
    is_public = Column(
        Boolean,
        default=False,
        comment="是否公开模板"
    )
    
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="创建者ID"
    )
    
    # 关系定义
    creator = relationship(
        "User",
        back_populates="created_templates"
    )
    
    sops = relationship(
        "SOP",
        back_populates="template"
    )
    
    def __repr__(self):
        return f"<SOPTemplate(id={self.id}, name='{self.name}')>"


class IndustryTemplate(BaseModel):
    """行业模板表"""
    
    __tablename__ = "industry_templates"
    
    name = Column(
        String(200),
        nullable=False,
        comment="模板名称"
    )
    
    industry = Column(
        String(100),
        nullable=False,
        comment="行业类型"
    )
    
    description = Column(
        Text,
        comment="模板描述"
    )
    
    template_data = Column(
        Text,
        nullable=False,
        comment="模板数据（JSON格式）"
    )
    
    systems_count = Column(
        Integer,
        default=0,
        comment="包含系统数量"
    )
    
    processes_count = Column(
        Integer,
        default=0,
        comment="包含流程数量"
    )
    
    is_featured = Column(
        Boolean,
        default=False,
        comment="是否为推荐模板"
    )
    
    download_count = Column(
        Integer,
        default=0,
        comment="下载次数"
    )
    
    def __repr__(self):
        return f"<IndustryTemplate(id={self.id}, name='{self.name}', industry='{self.industry}')>"


class WizardProgress(BaseModel):
    """向导进度表"""
    
    __tablename__ = "wizard_progress"
    
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    current_step = Column(
        String(50),
        nullable=False,
        comment="当前步骤"
    )
    
    completed_steps = Column(
        Text,
        comment="已完成步骤（JSON数组）"
    )
    
    template_id = Column(
        Integer,
        ForeignKey("industry_templates.id"),
        nullable=True,
        comment="选择的模板ID"
    )
    
    configuration = Column(
        Text,
        comment="配置数据（JSON格式）"
    )
    
    is_completed = Column(
        Boolean,
        default=False,
        comment="是否完成向导"
    )
    
    # 关系定义
    user = relationship(
        "User",
        back_populates="wizard_progress"
    )
    
    template = relationship("IndustryTemplate")
    
    def __repr__(self):
        return f"<WizardProgress(id={self.id}, user_id={self.user_id}, step='{self.current_step}')>"


class AIConversation(BaseModel):
    """AI对话历史表"""
    
    __tablename__ = "ai_conversations"
    
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    session_id = Column(
        String(100),
        nullable=False,
        comment="会话ID"
    )
    
    message_type = Column(
        String(20),
        nullable=False,
        comment="消息类型: user, assistant, system"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="消息内容"
    )
    
    context_data = Column(
        Text,
        comment="上下文数据（JSON格式）"
    )
    
    # 关系定义
    user = relationship(
        "User",
        back_populates="ai_conversations"
    )
    
    def __repr__(self):
        return f"<AIConversation(id={self.id}, user_id={self.user_id}, type='{self.message_type}')>"


class SystemConfig(BaseModel):
    """系统配置表"""
    
    __tablename__ = "system_config"
    
    config_key = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="配置键"
    )
    
    config_value = Column(
        Text,
        comment="配置值"
    )
    
    config_type = Column(
        String(50),
        default="string",
        comment="配置类型"
    )
    
    description = Column(
        Text,
        comment="配置描述"
    )
    
    is_encrypted = Column(
        Boolean,
        default=False,
        comment="是否加密存储"
    )
    
    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key='{self.config_key}')>"


# 创建索引
Index('idx_sops_author', SOP.author_id)
Index('idx_sops_status', SOP.status)
Index('idx_sops_template', SOP.template_id)

Index('idx_sop_versions_sop', SOPVersion.sop_id)
Index('idx_sop_versions_current', SOPVersion.sop_id, SOPVersion.is_current)

Index('idx_sop_templates_category', SOPTemplate.category)
Index('idx_sop_templates_public', SOPTemplate.is_public)
Index('idx_sop_templates_creator', SOPTemplate.created_by)

Index('idx_industry_templates_industry', IndustryTemplate.industry)
Index('idx_industry_templates_featured', IndustryTemplate.is_featured)

Index('idx_wizard_progress_user', WizardProgress.user_id)
Index('idx_wizard_progress_step', WizardProgress.current_step)

Index('idx_ai_conversations_user_session', AIConversation.user_id, AIConversation.session_id)
Index('idx_ai_conversations_created', AIConversation.created_at)

Index('idx_system_config_key', SystemConfig.config_key)