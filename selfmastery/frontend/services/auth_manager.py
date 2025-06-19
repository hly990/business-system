"""
认证管理器
"""
import json
import logging
from typing import Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QSettings, QTimer
from PyQt6.QtWidgets import QMessageBox

from .api_client import get_api_client, APIException


class AuthManager(QObject):
    """认证管理器"""
    
    # 信号定义
    login_success = pyqtSignal(dict)        # 登录成功
    login_failed = pyqtSignal(str)          # 登录失败
    logout_success = pyqtSignal()           # 登出成功
    token_refreshed = pyqtSignal()          # 令牌刷新
    session_expired = pyqtSignal()          # 会话过期
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.api_client = get_api_client()
        self.settings = QSettings('SelfMastery', 'B2BSystem')
        
        # 当前用户信息
        self.current_user = None
        self.access_token = None
        self.refresh_token = None
        
        # 令牌刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_token_if_needed)
        
        # 初始化时尝试恢复会话
        self.restore_session()
        
    def login(self, email: str, password: str) -> bool:
        """用户登录"""
        try:
            self.logger.info(f"尝试登录用户: {email}")
            
            # 调用API登录
            response = self.api_client.login(email, password)
            
            # 提取令牌和用户信息
            self.access_token = response.get('access_token')
            self.refresh_token = response.get('refresh_token')
            self.current_user = response.get('user')
            
            if not self.access_token or not self.current_user:
                raise APIException("登录响应格式错误")
                
            # 设置API客户端的认证令牌
            self.api_client.set_auth_token(self.access_token, self.refresh_token)
            
            # 保存会话信息
            self.save_session()
            
            # 启动令牌刷新定时器
            self.start_refresh_timer()
            
            self.logger.info(f"用户登录成功: {self.current_user.get('name')}")
            self.login_success.emit(self.current_user)
            
            return True
            
        except APIException as e:
            error_msg = f"登录失败: {str(e)}"
            self.logger.error(error_msg)
            self.login_failed.emit(error_msg)
            return False
            
        except Exception as e:
            error_msg = f"登录过程中发生错误: {str(e)}"
            self.logger.error(error_msg)
            self.login_failed.emit(error_msg)
            return False
            
    def logout(self) -> bool:
        """用户登出"""
        try:
            self.logger.info("用户登出")
            
            # 调用API登出
            try:
                self.api_client.logout()
            except Exception as e:
                self.logger.warning(f"API登出失败: {e}")
                
            # 清除本地会话信息
            self.clear_session()
            
            # 停止令牌刷新定时器
            self.refresh_timer.stop()
            
            self.logout_success.emit()
            return True
            
        except Exception as e:
            self.logger.error(f"登出过程中发生错误: {e}")
            return False
            
    def register(self, user_data: Dict) -> bool:
        """用户注册"""
        try:
            self.logger.info(f"尝试注册用户: {user_data.get('email')}")
            
            # 调用API注册
            response = self.api_client.register(user_data)
            
            self.logger.info("用户注册成功")
            return True
            
        except APIException as e:
            error_msg = f"注册失败: {str(e)}"
            self.logger.error(error_msg)
            return False
            
        except Exception as e:
            error_msg = f"注册过程中发生错误: {str(e)}"
            self.logger.error(error_msg)
            return False
            
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.current_user is not None and self.access_token is not None
        
    def get_current_user(self) -> Optional[Dict]:
        """获取当前用户信息"""
        return self.current_user
        
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        return self.access_token
        
    def refresh_user_info(self) -> bool:
        """刷新用户信息"""
        try:
            if not self.is_logged_in():
                return False
                
            # 从API获取最新用户信息
            user_data = self.api_client.get_current_user()
            self.current_user = user_data
            
            # 更新保存的会话信息
            self.save_session()
            
            return True
            
        except APIException as e:
            self.logger.error(f"刷新用户信息失败: {e}")
            if e.status_code == 401:
                # 认证失败，清除会话
                self.handle_session_expired()
            return False
            
        except Exception as e:
            self.logger.error(f"刷新用户信息过程中发生错误: {e}")
            return False
            
    def refresh_token_if_needed(self):
        """如果需要则刷新令牌"""
        try:
            if not self.is_logged_in():
                return
                
            # 尝试获取用户信息来验证令牌是否有效
            self.api_client.get_current_user()
            
        except APIException as e:
            if e.status_code == 401:
                # 令牌过期，尝试刷新
                if self.refresh_token:
                    self.logger.info("令牌过期，尝试刷新")
                    # API客户端会自动处理令牌刷新
                    try:
                        self.api_client.get_current_user()
                        self.token_refreshed.emit()
                        self.logger.info("令牌刷新成功")
                    except Exception:
                        self.handle_session_expired()
                else:
                    self.handle_session_expired()
            else:
                self.logger.error(f"验证令牌时发生错误: {e}")
                
        except Exception as e:
            self.logger.error(f"刷新令牌过程中发生错误: {e}")
            
    def handle_session_expired(self):
        """处理会话过期"""
        self.logger.warning("会话已过期")
        self.clear_session()
        self.refresh_timer.stop()
        self.session_expired.emit()
        
    def save_session(self):
        """保存会话信息"""
        try:
            session_data = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'user': self.current_user
            }
            
            # 加密保存到本地设置
            session_json = json.dumps(session_data)
            self.settings.setValue('session', session_json)
            self.settings.sync()
            
            self.logger.debug("会话信息已保存")
            
        except Exception as e:
            self.logger.error(f"保存会话信息失败: {e}")
            
    def restore_session(self):
        """恢复会话信息"""
        try:
            session_json = self.settings.value('session')
            if not session_json:
                return False
                
            session_data = json.loads(session_json)
            
            self.access_token = session_data.get('access_token')
            self.refresh_token = session_data.get('refresh_token')
            self.current_user = session_data.get('user')
            
            if self.access_token and self.current_user:
                # 设置API客户端的认证令牌
                self.api_client.set_auth_token(self.access_token, self.refresh_token)
                
                # 验证会话是否仍然有效
                try:
                    self.api_client.get_current_user()
                    self.start_refresh_timer()
                    self.logger.info(f"会话恢复成功: {self.current_user.get('name')}")
                    return True
                except Exception:
                    # 会话无效，清除
                    self.clear_session()
                    return False
            else:
                self.clear_session()
                return False
                
        except Exception as e:
            self.logger.error(f"恢复会话信息失败: {e}")
            self.clear_session()
            return False
            
    def clear_session(self):
        """清除会话信息"""
        self.current_user = None
        self.access_token = None
        self.refresh_token = None
        
        # 清除API客户端的认证信息
        self.api_client.clear_auth()
        
        # 清除本地保存的会话信息
        self.settings.remove('session')
        self.settings.sync()
        
        self.logger.debug("会话信息已清除")
        
    def start_refresh_timer(self):
        """启动令牌刷新定时器"""
        # 每30分钟检查一次令牌状态
        self.refresh_timer.start(30 * 60 * 1000)
        
    def change_password(self, old_password: str, new_password: str) -> bool:
        """修改密码"""
        try:
            if not self.is_logged_in():
                return False
                
            # 调用API修改密码
            self.api_client.post('/auth/change-password', json_data={
                'old_password': old_password,
                'new_password': new_password
            })
            
            self.logger.info("密码修改成功")
            return True
            
        except APIException as e:
            self.logger.error(f"修改密码失败: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"修改密码过程中发生错误: {e}")
            return False
            
    def update_profile(self, profile_data: Dict) -> bool:
        """更新用户资料"""
        try:
            if not self.is_logged_in():
                return False
                
            # 调用API更新资料
            updated_user = self.api_client.put('/auth/profile', json_data=profile_data)
            
            # 更新本地用户信息
            self.current_user.update(updated_user)
            self.save_session()
            
            self.logger.info("用户资料更新成功")
            return True
            
        except APIException as e:
            self.logger.error(f"更新用户资料失败: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"更新用户资料过程中发生错误: {e}")
            return False
            
    def request_password_reset(self, email: str) -> bool:
        """请求密码重置"""
        try:
            # 调用API请求密码重置
            self.api_client.post('/auth/forgot-password', json_data={
                'email': email
            })
            
            self.logger.info(f"密码重置请求已发送: {email}")
            return True
            
        except APIException as e:
            self.logger.error(f"请求密码重置失败: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"请求密码重置过程中发生错误: {e}")
            return False
            
    def reset_password(self, token: str, new_password: str) -> bool:
        """重置密码"""
        try:
            # 调用API重置密码
            self.api_client.post('/auth/reset-password', json_data={
                'token': token,
                'new_password': new_password
            })
            
            self.logger.info("密码重置成功")
            return True
            
        except APIException as e:
            self.logger.error(f"重置密码失败: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"重置密码过程中发生错误: {e}")
            return False
            
    def verify_email(self, token: str) -> bool:
        """验证邮箱"""
        try:
            # 调用API验证邮箱
            self.api_client.post('/auth/verify-email', json_data={
                'token': token
            })
            
            self.logger.info("邮箱验证成功")
            return True
            
        except APIException as e:
            self.logger.error(f"邮箱验证失败: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"邮箱验证过程中发生错误: {e}")
            return False
            
    def has_permission(self, resource_type: str, resource_id: int, permission: str) -> bool:
        """检查用户权限"""
        try:
            if not self.is_logged_in():
                return False
                
            # 调用API检查权限
            response = self.api_client.get('/auth/permissions', params={
                'resource_type': resource_type,
                'resource_id': resource_id,
                'permission': permission
            })
            
            return response.get('has_permission', False)
            
        except Exception as e:
            self.logger.error(f"检查权限失败: {e}")
            return False
            
    def get_user_permissions(self) -> Dict:
        """获取用户权限列表"""
        try:
            if not self.is_logged_in():
                return {}
                
            # 调用API获取权限列表
            response = self.api_client.get('/auth/permissions')
            return response.get('permissions', {})
            
        except Exception as e:
            self.logger.error(f"获取用户权限失败: {e}")
            return {}


# 单例模式的认证管理器实例
_auth_manager_instance = None

def get_auth_manager() -> AuthManager:
    """获取认证管理器单例"""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
    return _auth_manager_instance