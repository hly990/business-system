"""
用户相关数据模式
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式"""
    name: str
    email: EmailStr
    role: str = "user"
    timezone: str = "Asia/Shanghai"
    is_active: bool = True

    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['admin', 'manager', 'user', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f'角色必须是以下之一: {", ".join(allowed_roles)}')
        return v


class UserCreate(UserBase):
    """用户创建模式"""
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class UserUpdate(BaseModel):
    """用户更新模式"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ['admin', 'manager', 'user', 'viewer']
            if v not in allowed_roles:
                raise ValueError(f'角色必须是以下之一: {", ".join(allowed_roles)}')
        return v

    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模式"""
    email: EmailStr
    password: str


class UserRegister(UserCreate):
    """用户注册模式"""
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v


class Token(BaseModel):
    """令牌模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """令牌数据模式"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class PasswordReset(BaseModel):
    """密码重置模式"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """密码重置确认模式"""
    token: str
    new_password: str
    confirm_password: str

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


class UserProfile(BaseModel):
    """用户档案模式"""
    name: str
    email: EmailStr
    timezone: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """用户统计模式"""
    total_systems: int = 0
    total_processes: int = 0
    total_sops: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0