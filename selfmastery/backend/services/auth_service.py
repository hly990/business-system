"""
认证服务
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, Token, TokenData
from ..utils.exceptions import (
    AuthenticationError,
    UserNotFoundError,
    UserAlreadyExistsError,
    TokenExpiredError,
    InvalidTokenError,
    DatabaseError
)
from .base_service import BaseService
from config.settings import get_app_settings
from ..utils.monitoring import set_user_context

settings = get_app_settings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService(BaseService[User]):
    """认证服务类"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """用户认证"""
        try:
            user = self.get_by_field("email", email)
            if not user:
                return None
            
            if not user.is_active:
                return None
            
            if not user.password_hash:
                return None
            
            if not self.verify_password(password, user.password_hash):
                return None
            
            return user
        except SQLAlchemyError as e:
            raise DatabaseError(f"用户认证失败: {str(e)}")
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """验证令牌"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # 检查令牌类型
            if payload.get("type") != token_type:
                raise InvalidTokenError("令牌类型不匹配")
            
            user_id: int = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None:
                raise InvalidTokenError("令牌中缺少用户信息")
            
            token_data = TokenData(user_id=user_id, email=email)
            return token_data
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("令牌已过期")
        except jwt.JWTError:
            raise InvalidTokenError("无效的令牌")
    
    def get_current_user(self, token: str) -> User:
        """获取当前用户"""
        token_data = self.verify_token(token)
        user = self.get(token_data.user_id)
        if user is None:
            raise UserNotFoundError("用户不存在")
        if not user.is_active:
            raise AuthenticationError("用户已被禁用")
        return user
    
    def login(self, login_data: UserLogin) -> Token:
        """用户登录"""
        user = self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise AuthenticationError("邮箱或密码错误")
        
        # 创建令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = self.create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        refresh_token = self.create_refresh_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=refresh_token_expires
        )
        
        # 设置 Sentry 用户上下文
        try:
            set_user_context(
                user_id=str(user.id),
                email=user.email,
                username=user.username
            )
        except Exception as e:
            # 不要因为 Sentry 错误影响登录流程
            pass
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def refresh_token(self, refresh_token: str) -> Token:
        """刷新令牌"""
        token_data = self.verify_token(refresh_token, "refresh")
        user = self.get(token_data.user_id)
        
        if not user:
            raise UserNotFoundError("用户不存在")
        
        if not user.is_active:
            raise AuthenticationError("用户已被禁用")
        
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,  # 保持原有的刷新令牌
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def register(self, user_data: UserCreate) -> User:
        """用户注册"""
        try:
            # 检查邮箱是否已存在
            existing_user = self.get_by_field("email", user_data.email)
            if existing_user:
                raise UserAlreadyExistsError("邮箱已被注册")
            
            # 创建用户数据
            user_dict = user_data.dict()
            user_dict["password_hash"] = self.get_password_hash(user_data.password)
            del user_dict["password"]  # 删除明文密码
            
            # 创建用户
            user = self.create(user_dict)
            return user
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"用户注册失败: {str(e)}")
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            # 验证旧密码
            if not self.verify_password(old_password, user.password_hash):
                raise AuthenticationError("原密码错误")
            
            # 更新密码
            new_password_hash = self.get_password_hash(new_password)
            self.update(user_id, {"password_hash": new_password_hash})
            
            return True
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"密码修改失败: {str(e)}")
    
    def reset_password(self, email: str) -> str:
        """重置密码 - 生成重置令牌"""
        user = self.get_by_field("email", email)
        if not user:
            raise UserNotFoundError("用户不存在")
        
        # 创建重置令牌（有效期15分钟）
        reset_token_expires = timedelta(minutes=15)
        reset_token = self.create_access_token(
            data={"sub": user.id, "email": user.email, "purpose": "password_reset"},
            expires_delta=reset_token_expires
        )
        
        return reset_token
    
    def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """确认密码重置"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # 检查令牌用途
            if payload.get("purpose") != "password_reset":
                raise InvalidTokenError("无效的重置令牌")
            
            user_id: int = payload.get("sub")
            if user_id is None:
                raise InvalidTokenError("令牌中缺少用户信息")
            
            # 更新密码
            new_password_hash = self.get_password_hash(new_password)
            self.update(user_id, {"password_hash": new_password_hash})
            
            return True
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("重置令牌已过期")
        except jwt.JWTError:
            raise InvalidTokenError("无效的重置令牌")
        except SQLAlchemyError as e:
            raise DatabaseError(f"密码重置失败: {str(e)}")
    
    def deactivate_user(self, user_id: int) -> bool:
        """停用用户"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            self.update(user_id, {"is_active": False})
            return True
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"用户停用失败: {str(e)}")
    
    def activate_user(self, user_id: int) -> bool:
        """激活用户"""
        try:
            user = self.get(user_id)
            if not user:
                raise UserNotFoundError("用户不存在")
            
            self.update(user_id, {"is_active": True})
            return True
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"用户激活失败: {str(e)}")