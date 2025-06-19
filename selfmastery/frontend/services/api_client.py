"""
HTTP API客户端
"""
import json
import logging
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QUrl, QByteArray

from ...config.settings import get_app_settings


class APIException(Exception):
    """API异常类"""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class APIClient(QObject):
    """HTTP API客户端"""
    
    # 信号定义
    request_started = pyqtSignal(str)       # 请求开始
    request_finished = pyqtSignal(str)      # 请求完成
    request_failed = pyqtSignal(str, str)   # 请求失败
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.settings = get_app_settings()
        
        # API配置
        self.base_url = self.settings.API_BASE_URL
        self.timeout = self.settings.API_TIMEOUT
        self.max_retries = 3
        
        # 认证信息
        self.access_token = None
        self.refresh_token = None
        
        # 初始化HTTP会话
        self.session = requests.Session()
        self.setup_session()
        
        # 网络管理器（用于Qt集成）
        self.network_manager = QNetworkAccessManager()
        
        # 请求队列和重试机制
        self.request_queue = []
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self.process_retry_queue)
        
    def setup_session(self):
        """设置HTTP会话"""
        # 重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': f'SelfMastery-Desktop/{self.settings.APP_VERSION}'
        })
        
    def set_auth_token(self, access_token: str, refresh_token: str = None):
        """设置认证令牌"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        
        if access_token:
            self.session.headers['Authorization'] = f'Bearer {access_token}'
        else:
            self.session.headers.pop('Authorization', None)
            
    def clear_auth(self):
        """清除认证信息"""
        self.access_token = None
        self.refresh_token = None
        self.session.headers.pop('Authorization', None)
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发起HTTP请求"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            self.request_started.emit(f"{method.upper()} {endpoint}")
            
            # 设置超时
            kwargs.setdefault('timeout', self.timeout)
            
            # 发起请求
            response = self.session.request(method, url, **kwargs)
            
            # 检查响应状态
            if response.status_code == 401:
                # 尝试刷新令牌
                if self.refresh_token and self._refresh_access_token():
                    # 重新发起请求
                    response = self.session.request(method, url, **kwargs)
                else:
                    raise APIException("认证失败", response.status_code)
                    
            response.raise_for_status()
            
            # 解析响应
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = {'message': response.text}
                
            self.request_finished.emit(f"{method.upper()} {endpoint}")
            return data
            
        except requests.exceptions.RequestException as e:
            error_msg = f"请求失败: {str(e)}"
            self.logger.error(error_msg)
            self.request_failed.emit(f"{method.upper()} {endpoint}", error_msg)
            raise APIException(error_msg)
            
    def _refresh_access_token(self) -> bool:
        """刷新访问令牌"""
        if not self.refresh_token:
            return False
            
        try:
            response = self.session.post(
                f"{self.base_url}/auth/refresh",
                json={'refresh_token': self.refresh_token},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get('access_token')
                if new_access_token:
                    self.set_auth_token(new_access_token, self.refresh_token)
                    return True
                    
        except Exception as e:
            self.logger.error(f"刷新令牌失败: {e}")
            
        return False
        
    # HTTP方法封装
    def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """GET请求"""
        return self._make_request('GET', endpoint, params=params)
        
    def post(self, endpoint: str, data: Dict = None, json_data: Dict = None) -> Dict[str, Any]:
        """POST请求"""
        kwargs = {}
        if data:
            kwargs['data'] = data
        if json_data:
            kwargs['json'] = json_data
        return self._make_request('POST', endpoint, **kwargs)
        
    def put(self, endpoint: str, data: Dict = None, json_data: Dict = None) -> Dict[str, Any]:
        """PUT请求"""
        kwargs = {}
        if data:
            kwargs['data'] = data
        if json_data:
            kwargs['json'] = json_data
        return self._make_request('PUT', endpoint, **kwargs)
        
    def patch(self, endpoint: str, data: Dict = None, json_data: Dict = None) -> Dict[str, Any]:
        """PATCH请求"""
        kwargs = {}
        if data:
            kwargs['data'] = data
        if json_data:
            kwargs['json'] = json_data
        return self._make_request('PATCH', endpoint, **kwargs)
        
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE请求"""
        return self._make_request('DELETE', endpoint)
        
    # 认证相关API
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        return self.post('/auth/login', json_data={
            'email': email,
            'password': password
        })
        
    def logout(self) -> Dict[str, Any]:
        """用户登出"""
        try:
            result = self.post('/auth/logout')
            self.clear_auth()
            return result
        except Exception:
            # 即使登出失败也清除本地认证信息
            self.clear_auth()
            return {'message': '已清除本地认证信息'}
            
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """用户注册"""
        return self.post('/auth/register', json_data=user_data)
        
    def get_current_user(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        return self.get('/auth/me')
        
    # 业务系统API
    def get_systems(self, params: Dict = None) -> List[Dict[str, Any]]:
        """获取业务系统列表"""
        response = self.get('/systems', params=params)
        return response.get('data', [])
        
    def get_system(self, system_id: int) -> Dict[str, Any]:
        """获取单个业务系统"""
        response = self.get(f'/systems/{system_id}')
        return response.get('data', {})
        
    def create_system(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建业务系统"""
        response = self.post('/systems', json_data=system_data)
        return response.get('data', {})
        
    def update_system(self, system_id: int, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新业务系统"""
        response = self.put(f'/systems/{system_id}', json_data=system_data)
        return response.get('data', {})
        
    def delete_system(self, system_id: int) -> Dict[str, Any]:
        """删除业务系统"""
        return self.delete(f'/systems/{system_id}')
        
    # 业务流程API
    def get_processes(self, params: Dict = None) -> List[Dict[str, Any]]:
        """获取业务流程列表"""
        response = self.get('/processes', params=params)
        return response.get('data', [])
        
    def get_process(self, process_id: int) -> Dict[str, Any]:
        """获取单个业务流程"""
        response = self.get(f'/processes/{process_id}')
        return response.get('data', {})
        
    def create_process(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建业务流程"""
        response = self.post('/processes', json_data=process_data)
        return response.get('data', {})
        
    def update_process(self, process_id: int, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新业务流程"""
        response = self.put(f'/processes/{process_id}', json_data=process_data)
        return response.get('data', {})
        
    def delete_process(self, process_id: int) -> Dict[str, Any]:
        """删除业务流程"""
        return self.delete(f'/processes/{process_id}')
        
    # 流程连接API
    def get_process_connections(self, params: Dict = None) -> List[Dict[str, Any]]:
        """获取流程连接列表"""
        response = self.get('/process-connections', params=params)
        return response.get('data', [])
        
    def create_process_connection(self, connection_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建流程连接"""
        response = self.post('/process-connections', json_data=connection_data)
        return response.get('data', {})
        
    def delete_process_connection(self, connection_id: int) -> Dict[str, Any]:
        """删除流程连接"""
        return self.delete(f'/process-connections/{connection_id}')
        
    # SOP文档API
    def get_sops(self, params: Dict = None) -> List[Dict[str, Any]]:
        """获取SOP文档列表"""
        response = self.get('/sops', params=params)
        return response.get('data', [])
        
    def get_sop(self, sop_id: int) -> Dict[str, Any]:
        """获取单个SOP文档"""
        response = self.get(f'/sops/{sop_id}')
        return response.get('data', {})
        
    def create_sop(self, sop_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建SOP文档"""
        response = self.post('/sops', json_data=sop_data)
        return response.get('data', {})
        
    def update_sop(self, sop_id: int, sop_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新SOP文档"""
        response = self.put(f'/sops/{sop_id}', json_data=sop_data)
        return response.get('data', {})
        
    def delete_sop(self, sop_id: int) -> Dict[str, Any]:
        """删除SOP文档"""
        return self.delete(f'/sops/{sop_id}')
        
    # KPI指标API
    def get_kpis(self, params: Dict = None) -> List[Dict[str, Any]]:
        """获取KPI指标列表"""
        response = self.get('/kpis', params=params)
        return response.get('data', [])
        
    def get_kpi(self, kpi_id: int) -> Dict[str, Any]:
        """获取单个KPI指标"""
        response = self.get(f'/kpis/{kpi_id}')
        return response.get('data', {})
        
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建KPI指标"""
        response = self.post('/kpis', json_data=kpi_data)
        return response.get('data', {})
        
    def update_kpi(self, kpi_id: int, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新KPI指标"""
        response = self.put(f'/kpis/{kpi_id}', json_data=kpi_data)
        return response.get('data', {})
        
    def delete_kpi(self, kpi_id: int) -> Dict[str, Any]:
        """删除KPI指标"""
        return self.delete(f'/kpis/{kpi_id}')
        
    # 任务管理API
    def get_tasks(self, params: Dict = None) -> List[Dict[str, Any]]:
        """获取任务列表"""
        response = self.get('/tasks', params=params)
        return response.get('data', [])
        
    def get_task(self, task_id: int) -> Dict[str, Any]:
        """获取单个任务"""
        response = self.get(f'/tasks/{task_id}')
        return response.get('data', {})
        
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建任务"""
        response = self.post('/tasks', json_data=task_data)
        return response.get('data', {})
        
    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新任务"""
        response = self.put(f'/tasks/{task_id}', json_data=task_data)
        return response.get('data', {})
        
    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """删除任务"""
        return self.delete(f'/tasks/{task_id}')
        
    # 文件上传API
    def upload_file(self, file_path: str, endpoint: str = '/upload') -> Dict[str, Any]:
        """上传文件"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(
                    f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}",
                    files=files,
                    timeout=self.timeout * 3  # 文件上传使用更长的超时时间
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise APIException(f"文件上传失败: {str(e)}")
            
    # 健康检查
    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = self.get('/health')
            return response.get('status') == 'ok'
        except Exception:
            return False
            
    def process_retry_queue(self):
        """处理重试队列"""
        # TODO: 实现请求重试机制
        pass


# 单例模式的API客户端实例
_api_client_instance = None

def get_api_client() -> APIClient:
    """获取API客户端单例"""
    global _api_client_instance
    if _api_client_instance is None:
        _api_client_instance = APIClient()
    return _api_client_instance