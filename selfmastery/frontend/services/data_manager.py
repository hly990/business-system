"""
数据管理器
"""
import logging
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QMutex, QTimer

from .api_client import get_api_client, APIException


class DataManager(QObject):
    """数据管理器"""
    
    # 信号定义
    data_loaded = pyqtSignal(str)           # 数据加载完成
    data_saved = pyqtSignal(str)            # 数据保存完成
    data_updated = pyqtSignal(str, dict)    # 数据更新
    error_occurred = pyqtSignal(str)        # 错误发生
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.api_client = get_api_client()
        
        # 数据缓存
        self._systems_cache = []
        self._processes_cache = []
        self._process_connections_cache = []
        self._sops_cache = []
        self._kpis_cache = []
        self._tasks_cache = []
        
        # 缓存状态
        self._cache_timestamps = {}
        self._cache_mutex = QMutex()
        
        # 自动刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_data)
        
        # 缓存过期时间（秒）
        self.cache_expiry = 300  # 5分钟
        
    def start_auto_refresh(self, interval_ms: int = 300000):
        """启动自动刷新（默认5分钟）"""
        self.refresh_timer.start(interval_ms)
        
    def stop_auto_refresh(self):
        """停止自动刷新"""
        self.refresh_timer.stop()
        
    def is_cache_valid(self, data_type: str) -> bool:
        """检查缓存是否有效"""
        import time
        timestamp = self._cache_timestamps.get(data_type, 0)
        return (time.time() - timestamp) < self.cache_expiry
        
    def update_cache_timestamp(self, data_type: str):
        """更新缓存时间戳"""
        import time
        self._cache_timestamps[data_type] = time.time()
        
    # 业务系统数据管理
    def load_systems(self, force_refresh: bool = False) -> List[Dict]:
        """加载业务系统数据"""
        try:
            if not force_refresh and self.is_cache_valid('systems'):
                self.data_loaded.emit('systems')
                return self._systems_cache
                
            self.logger.info("加载业务系统数据")
            systems = self.api_client.get_systems()
            
            with QMutex():
                self._systems_cache = systems
                self.update_cache_timestamp('systems')
                
            self.data_loaded.emit('systems')
            return systems
            
        except APIException as e:
            error_msg = f"加载业务系统数据失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []
            
    def get_systems(self) -> List[Dict]:
        """获取缓存的业务系统数据"""
        return self._systems_cache.copy()
        
    def get_system(self, system_id: int) -> Optional[Dict]:
        """获取单个业务系统"""
        for system in self._systems_cache:
            if system.get('id') == system_id:
                return system.copy()
        return None
        
    def create_system(self, system_data: Dict) -> Dict:
        """创建业务系统"""
        try:
            self.logger.info(f"创建业务系统: {system_data.get('name')}")
            created_system = self.api_client.create_system(system_data)
            
            # 更新缓存
            with QMutex():
                self._systems_cache.append(created_system)
                self.update_cache_timestamp('systems')
                
            self.data_updated.emit('systems', created_system)
            return created_system
            
        except APIException as e:
            error_msg = f"创建业务系统失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise
            
    def update_system(self, system_id: int, system_data: Dict) -> Dict:
        """更新业务系统"""
        try:
            self.logger.info(f"更新业务系统: {system_id}")
            updated_system = self.api_client.update_system(system_id, system_data)
            
            # 更新缓存
            with QMutex():
                for i, system in enumerate(self._systems_cache):
                    if system.get('id') == system_id:
                        self._systems_cache[i] = updated_system
                        break
                self.update_cache_timestamp('systems')
                
            self.data_updated.emit('systems', updated_system)
            return updated_system
            
        except APIException as e:
            error_msg = f"更新业务系统失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise
            
    def delete_system(self, system_id: int) -> bool:
        """删除业务系统"""
        try:
            self.logger.info(f"删除业务系统: {system_id}")
            self.api_client.delete_system(system_id)
            
            # 更新缓存
            with QMutex():
                self._systems_cache = [s for s in self._systems_cache if s.get('id') != system_id]
                self.update_cache_timestamp('systems')
                
            self.data_updated.emit('systems', {'id': system_id, 'deleted': True})
            return True
            
        except APIException as e:
            error_msg = f"删除业务系统失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    def update_system_position(self, system_id: int, x: float, y: float) -> bool:
        """更新系统位置"""
        try:
            system_data = {'position_x': x, 'position_y': y}
            self.update_system(system_id, system_data)
            return True
        except Exception:
            return False
            
    # 业务流程数据管理
    def load_processes(self, force_refresh: bool = False) -> List[Dict]:
        """加载业务流程数据"""
        try:
            if not force_refresh and self.is_cache_valid('processes'):
                self.data_loaded.emit('processes')
                return self._processes_cache
                
            self.logger.info("加载业务流程数据")
            processes = self.api_client.get_processes()
            
            with QMutex():
                self._processes_cache = processes
                self.update_cache_timestamp('processes')
                
            self.data_loaded.emit('processes')
            return processes
            
        except APIException as e:
            error_msg = f"加载业务流程数据失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []
            
    def get_processes(self) -> List[Dict]:
        """获取缓存的业务流程数据"""
        return self._processes_cache.copy()
        
    def get_process(self, process_id: int) -> Optional[Dict]:
        """获取单个业务流程"""
        for process in self._processes_cache:
            if process.get('id') == process_id:
                return process.copy()
        return None
        
    def create_process(self, process_data: Dict) -> Dict:
        """创建业务流程"""
        try:
            self.logger.info(f"创建业务流程: {process_data.get('name')}")
            created_process = self.api_client.create_process(process_data)
            
            # 更新缓存
            with QMutex():
                self._processes_cache.append(created_process)
                self.update_cache_timestamp('processes')
                
            self.data_updated.emit('processes', created_process)
            return created_process
            
        except APIException as e:
            error_msg = f"创建业务流程失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise
            
    def update_process(self, process_id: int, process_data: Dict) -> Dict:
        """更新业务流程"""
        try:
            self.logger.info(f"更新业务流程: {process_id}")
            updated_process = self.api_client.update_process(process_id, process_data)
            
            # 更新缓存
            with QMutex():
                for i, process in enumerate(self._processes_cache):
                    if process.get('id') == process_id:
                        self._processes_cache[i] = updated_process
                        break
                self.update_cache_timestamp('processes')
                
            self.data_updated.emit('processes', updated_process)
            return updated_process
            
        except APIException as e:
            error_msg = f"更新业务流程失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise
            
    def delete_process(self, process_id: int) -> bool:
        """删除业务流程"""
        try:
            self.logger.info(f"删除业务流程: {process_id}")
            self.api_client.delete_process(process_id)
            
            # 更新缓存
            with QMutex():
                self._processes_cache = [p for p in self._processes_cache if p.get('id') != process_id]
                self.update_cache_timestamp('processes')
                
            self.data_updated.emit('processes', {'id': process_id, 'deleted': True})
            return True
            
        except APIException as e:
            error_msg = f"删除业务流程失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    def update_process_position(self, process_id: int, x: float, y: float) -> bool:
        """更新流程位置"""
        try:
            process_data = {'position_x': x, 'position_y': y}
            self.update_process(process_id, process_data)
            return True
        except Exception:
            return False
            
    # 流程连接数据管理
    def load_process_connections(self, force_refresh: bool = False) -> List[Dict]:
        """加载流程连接数据"""
        try:
            if not force_refresh and self.is_cache_valid('process_connections'):
                self.data_loaded.emit('process_connections')
                return self._process_connections_cache
                
            self.logger.info("加载流程连接数据")
            connections = self.api_client.get_process_connections()
            
            with QMutex():
                self._process_connections_cache = connections
                self.update_cache_timestamp('process_connections')
                
            self.data_loaded.emit('process_connections')
            return connections
            
        except APIException as e:
            error_msg = f"加载流程连接数据失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []
            
    def get_process_connections(self) -> List[Dict]:
        """获取缓存的流程连接数据"""
        return self._process_connections_cache.copy()
        
    def create_process_connection(self, connection_data: Dict) -> Dict:
        """创建流程连接"""
        try:
            self.logger.info("创建流程连接")
            created_connection = self.api_client.create_process_connection(connection_data)
            
            # 更新缓存
            with QMutex():
                self._process_connections_cache.append(created_connection)
                self.update_cache_timestamp('process_connections')
                
            self.data_updated.emit('process_connections', created_connection)
            return created_connection
            
        except APIException as e:
            error_msg = f"创建流程连接失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise
            
    def delete_process_connection(self, connection_id: int) -> bool:
        """删除流程连接"""
        try:
            self.logger.info(f"删除流程连接: {connection_id}")
            self.api_client.delete_process_connection(connection_id)
            
            # 更新缓存
            with QMutex():
                self._process_connections_cache = [
                    c for c in self._process_connections_cache if c.get('id') != connection_id
                ]
                self.update_cache_timestamp('process_connections')
                
            self.data_updated.emit('process_connections', {'id': connection_id, 'deleted': True})
            return True
            
        except APIException as e:
            error_msg = f"删除流程连接失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    # SOP文档数据管理
    def load_sops(self, force_refresh: bool = False) -> List[Dict]:
        """加载SOP文档数据"""
        try:
            if not force_refresh and self.is_cache_valid('sops'):
                self.data_loaded.emit('sops')
                return self._sops_cache
                
            self.logger.info("加载SOP文档数据")
            sops = self.api_client.get_sops()
            
            with QMutex():
                self._sops_cache = sops
                self.update_cache_timestamp('sops')
                
            self.data_loaded.emit('sops')
            return sops
            
        except APIException as e:
            error_msg = f"加载SOP文档数据失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []
            
    def get_sops(self) -> List[Dict]:
        """获取缓存的SOP文档数据"""
        return self._sops_cache.copy()
        
    def get_sop(self, sop_id: int) -> Optional[Dict]:
        """获取单个SOP文档"""
        for sop in self._sops_cache:
            if sop.get('id') == sop_id:
                return sop.copy()
        return None
        
    def create_sop(self, sop_data: Dict) -> Dict:
        """创建SOP文档"""
        try:
            self.logger.info(f"创建SOP文档: {sop_data.get('title')}")
            created_sop = self.api_client.create_sop(sop_data)
            
            # 更新缓存
            with QMutex():
                self._sops_cache.append(created_sop)
                self.update_cache_timestamp('sops')
                
            self.data_updated.emit('sops', created_sop)
            return created_sop
            
        except APIException as e:
            error_msg = f"创建SOP文档失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise
            
    def update_sop(self, sop_id: int, sop_data: Dict) -> Dict:
        """更新SOP文档"""
        try:
            self.logger.info(f"更新SOP文档: {sop_id}")
            updated_sop = self.api_client.update_sop(sop_id, sop_data)
            
            # 更新缓存
            with QMutex():
                for i, sop in enumerate(self._sops_cache):
                    if sop.get('id') == sop_id:
                        self._sops_cache[i] = updated_sop
                        break
                self.update_cache_timestamp('sops')
                
            self.data_updated.emit('sops', updated_sop)
            return updated_sop
            
        except APIException as e:
            error_msg = f"更新SOP文档失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise
            
    def delete_sop(self, sop_id: int) -> bool:
        """删除SOP文档"""
        try:
            self.logger.info(f"删除SOP文档: {sop_id}")
            self.api_client.delete_sop(sop_id)
            
            # 更新缓存
            with QMutex():
                self._sops_cache = [s for s in self._sops_cache if s.get('id') != sop_id]
                self.update_cache_timestamp('sops')
                
            self.data_updated.emit('sops', {'id': sop_id, 'deleted': True})
            return True
            
        except APIException as e:
            error_msg = f"删除SOP文档失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    # KPI指标数据管理
    def load_kpis(self, force_refresh: bool = False) -> List[Dict]:
        """加载KPI指标数据"""
        try:
            if not force_refresh and self.is_cache_valid('kpis'):
                self.data_loaded.emit('kpis')
                return self._kpis_cache
                
            self.logger.info("加载KPI指标数据")
            kpis = self.api_client.get_kpis()
            
            with QMutex():
                self._kpis_cache = kpis
                self.update_cache_timestamp('kpis')
                
            self.data_loaded.emit('kpis')
            return kpis
            
        except APIException as e:
            error_msg = f"加载KPI指标数据失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []
            
    def get_kpis(self) -> List[Dict]:
        """获取缓存的KPI指标数据"""
        return self._kpis_cache.copy()
        
    # 任务数据管理
    def load_tasks(self, force_refresh: bool = False) -> List[Dict]:
        """加载任务数据"""
        try:
            if not force_refresh and self.is_cache_valid('tasks'):
                self.data_loaded.emit('tasks')
                return self._tasks_cache
                
            self.logger.info("加载任务数据")
            tasks = self.api_client.get_tasks()
            
            with QMutex():
                self._tasks_cache = tasks
                self.update_cache_timestamp('tasks')
                
            self.data_loaded.emit('tasks')
            return tasks
            
        except APIException as e:
            error_msg = f"加载任务数据失败: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []
            
    def get_tasks(self) -> List[Dict]:
        """获取缓存的任务数据"""
        return self._tasks_cache.copy()
        
    # 批量操作
    def refresh_all_data(self):
        """刷新所有数据"""
        self.logger.info("刷新所有数据")
        try:
            self.load_systems(force_refresh=True)
            self.load_processes(force_refresh=True)
            self.load_process_connections(force_refresh=True)
            self.load_sops(force_refresh=True)
            self.load_kpis(force_refresh=True)
            self.load_tasks(force_refresh=True)
        except Exception as e:
            self.logger.error(f"刷新数据失败: {e}")
            
    def clear_cache(self):
        """清空缓存"""
        with QMutex():
            self._systems_cache.clear()
            self._processes_cache.clear()
            self._process_connections_cache.clear()
            self._sops_cache.clear()
            self._kpis_cache.clear()
            self._tasks_cache.clear()
            self._cache_timestamps.clear()
            
    def cleanup(self):
        """清理资源"""
        self.stop_auto_refresh()
        self.clear_cache()


# 单例模式的数据管理器实例
_data_manager_instance = None

def get_data_manager() -> DataManager:
    """获取数据管理器单例"""
    global _data_manager_instance
    if _data_manager_instance is None:
        _data_manager_instance = DataManager()
    return _data_manager_instance