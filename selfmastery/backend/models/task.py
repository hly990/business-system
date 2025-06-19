"""
任务相关数据模型
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Task(BaseModel):
    """任务表"""
    
    __tablename__ = "tasks"
    
    # 基本信息
    process_id = Column(
        Integer,
        ForeignKey("business_processes.id"),
        nullable=False,
        comment="关联流程ID"
    )
    
    title = Column(
        String(200),
        nullable=False,
        comment="任务标题"
    )
    
    description = Column(
        Text,
        comment="任务描述"
    )
    
    assignee_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="指派人ID"
    )
    
    creator_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="创建人ID"
    )
    
    # 任务属性
    status = Column(
        String(50),
        default="pending",
        comment="任务状态: pending, in_progress, completed, cancelled, on_hold"
    )
    
    priority = Column(
        Integer,
        default=3,
        comment="优先级: 1(最高) - 5(最低)"
    )
    
    task_type = Column(
        String(50),
        default="manual",
        comment="任务类型: manual, automated, review, approval"
    )
    
    # 时间管理
    due_date = Column(
        DateTime,
        nullable=True,
        comment="截止日期"
    )
    
    started_at = Column(
        DateTime,
        nullable=True,
        comment="开始时间"
    )
    
    completed_at = Column(
        DateTime,
        nullable=True,
        comment="完成时间"
    )
    
    estimated_hours = Column(
        Integer,
        comment="预估工时（小时）"
    )
    
    actual_hours = Column(
        Integer,
        comment="实际工时（小时）"
    )
    
    # 任务配置
    is_recurring = Column(
        Boolean,
        default=False,
        comment="是否循环任务"
    )
    
    recurrence_pattern = Column(
        Text,
        comment="循环模式配置（JSON格式）"
    )
    
    dependencies = Column(
        Text,
        comment="依赖任务ID列表（JSON格式）"
    )
    
    tags = Column(
        Text,
        comment="标签列表（JSON格式）"
    )
    
    # 关系定义
    process = relationship(
        "BusinessProcess",
        back_populates="tasks"
    )
    
    assignee = relationship(
        "User",
        foreign_keys=[assignee_id],
        back_populates="assigned_tasks"
    )
    
    creator = relationship(
        "User",
        foreign_keys=[creator_id]
    )
    
    comments = relationship(
        "TaskComment",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskComment.created_at.desc()"
    )
    
    attachments = relationship(
        "TaskAttachment",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    time_logs = relationship(
        "TaskTimeLog",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskTimeLog.start_time.desc()"
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def is_overdue(self) -> bool:
        """是否已逾期"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            from datetime import datetime
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def progress_percentage(self) -> float:
        """任务进度百分比"""
        if self.status == "completed":
            return 100.0
        elif self.status == "in_progress":
            return 50.0
        elif self.status == "pending":
            return 0.0
        else:
            return 0.0
    
    def start_task(self):
        """开始任务"""
        if self.status == "pending":
            from datetime import datetime
            self.status = "in_progress"
            self.started_at = datetime.utcnow()
    
    def complete_task(self):
        """完成任务"""
        if self.status in ["pending", "in_progress"]:
            from datetime import datetime
            self.status = "completed"
            self.completed_at = datetime.utcnow()
    
    def cancel_task(self):
        """取消任务"""
        if self.status not in ["completed", "cancelled"]:
            self.status = "cancelled"


class TaskComment(BaseModel):
    """任务评论表"""
    
    __tablename__ = "task_comments"
    
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
        comment="任务ID"
    )
    
    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="评论作者ID"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="评论内容"
    )
    
    comment_type = Column(
        String(50),
        default="comment",
        comment="评论类型: comment, status_change, assignment"
    )
    
    # 关系定义
    task = relationship(
        "Task",
        back_populates="comments"
    )
    
    author = relationship("User")
    
    def __repr__(self):
        return f"<TaskComment(id={self.id}, task_id={self.task_id})>"


class TaskAttachment(BaseModel):
    """任务附件表"""
    
    __tablename__ = "task_attachments"
    
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
        comment="任务ID"
    )
    
    filename = Column(
        String(255),
        nullable=False,
        comment="文件名"
    )
    
    file_path = Column(
        String(500),
        nullable=False,
        comment="文件路径"
    )
    
    file_size = Column(
        Integer,
        comment="文件大小（字节）"
    )
    
    mime_type = Column(
        String(100),
        comment="MIME类型"
    )
    
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="上传者ID"
    )
    
    # 关系定义
    task = relationship(
        "Task",
        back_populates="attachments"
    )
    
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<TaskAttachment(id={self.id}, filename='{self.filename}')>"


class TaskTimeLog(BaseModel):
    """任务时间记录表"""
    
    __tablename__ = "task_time_logs"
    
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
        comment="任务ID"
    )
    
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    start_time = Column(
        DateTime,
        nullable=False,
        comment="开始时间"
    )
    
    end_time = Column(
        DateTime,
        nullable=True,
        comment="结束时间"
    )
    
    duration_minutes = Column(
        Integer,
        comment="持续时间（分钟）"
    )
    
    description = Column(
        Text,
        comment="工作描述"
    )
    
    # 关系定义
    task = relationship(
        "Task",
        back_populates="time_logs"
    )
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<TaskTimeLog(id={self.id}, task_id={self.task_id}, duration={self.duration_minutes})>"
    
    def stop_logging(self):
        """停止时间记录"""
        if not self.end_time:
            from datetime import datetime
            self.end_time = datetime.utcnow()
            if self.start_time:
                delta = self.end_time - self.start_time
                self.duration_minutes = int(delta.total_seconds() / 60)


class Notification(BaseModel):
    """通知表"""
    
    __tablename__ = "notifications"
    
    # 接收者信息
    recipient_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment="接收者ID"
    )
    
    # 通知内容
    title = Column(
        String(200),
        nullable=False,
        comment="通知标题"
    )
    
    message = Column(
        Text,
        nullable=False,
        comment="通知内容"
    )
    
    notification_type = Column(
        String(50),
        nullable=False,
        comment="通知类型: task, kpi, system, process, deadline"
    )
    
    # 关联资源
    resource_type = Column(
        String(50),
        comment="关联资源类型"
    )
    
    resource_id = Column(
        Integer,
        comment="关联资源ID"
    )
    
    # 通知状态
    is_read = Column(
        Boolean,
        default=False,
        comment="是否已读"
    )
    
    read_at = Column(
        DateTime,
        nullable=True,
        comment="阅读时间"
    )
    
    # 发送配置
    send_email = Column(
        Boolean,
        default=False,
        comment="是否发送邮件"
    )
    
    email_sent = Column(
        Boolean,
        default=False,
        comment="邮件是否已发送"
    )
    
    priority = Column(
        String(20),
        default="normal",
        comment="优先级: low, normal, high, urgent"
    )
    
    # 关系定义
    recipient = relationship("User")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', recipient_id={self.recipient_id})>"
    
    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            from datetime import datetime
            self.is_read = True
            self.read_at = datetime.utcnow()


# 创建索引
Index('idx_tasks_process', Task.process_id)
Index('idx_tasks_assignee', Task.assignee_id)
Index('idx_tasks_creator', Task.creator_id)
Index('idx_tasks_status', Task.status)
Index('idx_tasks_due_date', Task.due_date)
Index('idx_tasks_priority', Task.priority)
Index('idx_tasks_assignee_status', Task.assignee_id, Task.status)

Index('idx_task_comments_task', TaskComment.task_id)
Index('idx_task_comments_author', TaskComment.author_id)

Index('idx_task_attachments_task', TaskAttachment.task_id)
Index('idx_task_attachments_uploader', TaskAttachment.uploaded_by)

Index('idx_task_time_logs_task', TaskTimeLog.task_id)
Index('idx_task_time_logs_user', TaskTimeLog.user_id)
Index('idx_task_time_logs_start_time', TaskTimeLog.start_time)

Index('idx_notifications_recipient', Notification.recipient_id)
Index('idx_notifications_type', Notification.notification_type)
Index('idx_notifications_read', Notification.is_read)
Index('idx_notifications_priority', Notification.priority)
Index('idx_notifications_recipient_read', Notification.recipient_id, Notification.is_read)