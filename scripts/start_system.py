#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 一键启动脚本
自动检查依赖、启动后端服务、启动前端应用，并提供系统状态监控
"""

import os
import sys
import time
import json
import subprocess
import threading
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

class SystemStarter:
    """系统启动器"""
    
    def __init__(self):
        self.project_root = project_root
        self.backend_url = "http://localhost:8000"
        self.backend_process = None
        self.frontend_process = None
        self.monitoring = False
        self.status = {
            "dependencies": {"status": "pending", "details": []},
            "database": {"status": "pending", "details": []},
            "backend": {"status": "pending", "details": []},
            "frontend": {"status": "pending", "details": []},
            "system": {"status": "pending", "details": []}
        }
        
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def start_system(self):
        """启动整个系统"""
        self.log("开始启动SelfMastery B2B业务系统", "INFO")
        
        try:
            # 1. 检查依赖
            if not self.check_dependencies():
                self.log("依赖检查失败，无法启动系统", "ERROR")
                return False
            
            # 2. 检查和初始化数据库
            if not self.check_database():
                self.log("数据库检查失败，无法启动系统", "ERROR")
                return False
            
            # 3. 启动后端服务
            if not self.start_backend():
                self.log("后端服务启动失败，无法启动系统", "ERROR")
                return False
            
            # 4. 启动前端应用
            if not self.start_frontend():
                self.log("前端应用启动失败", "WARNING")
                # 前端启动失败不阻止系统运行
            
            # 5. 开始系统监控
            self.start_monitoring()
            
            # 6. 显示系统状态
            self.display_system_status()
            
            return True
            
        except KeyboardInterrupt:
            self.log("收到中断信号，正在关闭系统...", "INFO")
            self.shutdown_system()
            return False
        except Exception as e:
            self.log(f"系统启动过程中发生错误: {str(e)}", "ERROR")
            self.shutdown_system()
            return False
    
    def check_dependencies(self) -> bool:
        """检查系统依赖"""
        self.log("检查系统依赖", "INFO")
        
        dependencies = []
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            dependencies.append("✓ Python版本: 符合要求")
            self.log(f"Python版本: {python_version.major}.{python_version.minor}", "INFO")
        else:
            dependencies.append("✗ Python版本: 需要3.8+")
            self.log(f"Python版本不符合要求: {python_version.major}.{python_version.minor}", "ERROR")
            self.status["dependencies"]["status"] = "failed"
            self.status["dependencies"]["details"] = dependencies
            return False
        
        # 检查必要的Python包
        required_packages = [
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
            ("sqlalchemy", "SQLAlchemy"),
            ("PyQt5", "PyQt5"),
            ("requests", "Requests")
        ]
        
        missing_packages = []
        for package, display_name in required_packages:
            try:
                __import__(package)
                dependencies.append(f"✓ {display_name}: 已安装")
                self.log(f"{display_name}: 已安装", "INFO")
            except ImportError:
                dependencies.append(f"✗ {display_name}: 未安装")
                missing_packages.append(package)
                self.log(f"{display_name}: 未安装", "ERROR")
        
        if missing_packages:
            dependencies.append(f"缺少包: {', '.join(missing_packages)}")
            dependencies.append("请运行: pip install -r requirements.txt")
            self.status["dependencies"]["status"] = "failed"
            self.status["dependencies"]["details"] = dependencies
            return False
        
        # 检查项目文件结构
        required_files = [
            "selfmastery/backend/main.py",
            "selfmastery/frontend/main.py",
            "selfmastery/config/settings.py",
            "selfmastery/requirements.txt"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                dependencies.append(f"✓ {file_path}: 存在")
            else:
                dependencies.append(f"✗ {file_path}: 不存在")
                missing_files.append(file_path)
        
        if missing_files:
            self.status["dependencies"]["status"] = "failed"
            self.status["dependencies"]["details"] = dependencies
            return False
        
        self.status["dependencies"]["status"] = "passed"
        self.status["dependencies"]["details"] = dependencies
        return True
    
    def check_database(self) -> bool:
        """检查和初始化数据库"""
        self.log("检查数据库", "INFO")
        
        db_details = []
        
        # 检查数据库文件
        db_path = self.project_root / "data" / "selfmastery.db"
        if db_path.exists():
            db_details.append(f"✓ 数据库文件存在: {db_path}")
            self.log("数据库文件存在", "INFO")
        else:
            db_details.append("✗ 数据库文件不存在，尝试初始化")
            self.log("数据库文件不存在，尝试初始化", "WARNING")
            
            # 尝试初始化数据库
            try:
                init_script = self.project_root / "scripts" / "init_db.py"
                if init_script.exists():
                    result = subprocess.run([
                        sys.executable, str(init_script)
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        db_details.append("✓ 数据库初始化成功")
                        self.log("数据库初始化成功", "INFO")
                    else:
                        db_details.append(f"✗ 数据库初始化失败: {result.stderr}")
                        self.log(f"数据库初始化失败: {result.stderr}", "ERROR")
                        self.status["database"]["status"] = "failed"
                        self.status["database"]["details"] = db_details
                        return False
                else:
                    db_details.append("✗ 数据库初始化脚本不存在")
                    self.status["database"]["status"] = "failed"
                    self.status["database"]["details"] = db_details
                    return False
            except Exception as e:
                db_details.append(f"✗ 数据库初始化异常: {str(e)}")
                self.status["database"]["status"] = "failed"
                self.status["database"]["details"] = db_details
                return False
        
        # 检查数据库连接
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 检查表是否存在
            tables = ["users", "business_systems", "business_processes", "sops", "kpis", "tasks"]
            existing_tables = []
            
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    existing_tables.append(table)
            
            conn.close()
            
            if len(existing_tables) == len(tables):
                db_details.append(f"✓ 所有数据表存在: {', '.join(existing_tables)}")
                self.log("数据库表结构完整", "INFO")
            else:
                missing_tables = set(tables) - set(existing_tables)
                db_details.append(f"✗ 缺少数据表: {', '.join(missing_tables)}")
                self.log(f"缺少数据表: {', '.join(missing_tables)}", "ERROR")
                self.status["database"]["status"] = "failed"
                self.status["database"]["details"] = db_details
                return False
                
        except Exception as e:
            db_details.append(f"✗ 数据库连接失败: {str(e)}")
            self.status["database"]["status"] = "failed"
            self.status["database"]["details"] = db_details
            return False
        
        self.status["database"]["status"] = "passed"
        self.status["database"]["details"] = db_details
        return True
    
    def start_backend(self) -> bool:
        """启动后端服务"""
        self.log("启动后端服务", "INFO")
        
        backend_details = []
        
        try:
            # 启动后端进程
            backend_main = self.project_root / "selfmastery" / "backend" / "main.py"
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_main)
            ], cwd=str(self.project_root))
            
            backend_details.append("✓ 后端进程已启动")
            self.log("后端进程已启动", "INFO")
            
            # 等待服务启动并检查健康状态
            self.log("等待后端服务启动...", "INFO")
            startup_success = False
            
            for i in range(30):  # 等待30秒
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=2)
                    if response.status_code == 200:
                        startup_success = True
                        backend_details.append(f"✓ 后端服务健康检查通过: {self.backend_url}")
                        self.log(f"后端服务启动成功: {self.backend_url}", "INFO")
                        break
                except:
                    pass
                
                time.sleep(1)
                if i % 5 == 0:
                    self.log(f"等待后端服务启动... ({i+1}/30)", "INFO")
            
            if not startup_success:
                backend_details.append("✗ 后端服务启动超时")
                self.log("后端服务启动超时", "ERROR")
                self.status["backend"]["status"] = "failed"
                self.status["backend"]["details"] = backend_details
                return False
            
            # 测试API端点
            try:
                response = requests.get(f"{self.backend_url}/docs", timeout=5)
                if response.status_code == 200:
                    backend_details.append(f"✓ API文档可访问: {self.backend_url}/docs")
                    self.log("API文档可访问", "INFO")
            except:
                backend_details.append("○ API文档访问失败（非关键）")
            
            self.status["backend"]["status"] = "passed"
            self.status["backend"]["details"] = backend_details
            return True
            
        except Exception as e:
            backend_details.append(f"✗ 后端启动异常: {str(e)}")
            self.status["backend"]["status"] = "failed"
            self.status["backend"]["details"] = backend_details
            return False
    
    def start_frontend(self) -> bool:
        """启动前端应用"""
        self.log("启动前端应用", "INFO")
        
        frontend_details = []
        
        try:
            # 检查前端文件
            frontend_main = self.project_root / "selfmastery" / "frontend" / "main.py"
            if not frontend_main.exists():
                frontend_details.append("✗ 前端主文件不存在")
                self.status["frontend"]["status"] = "failed"
                self.status["frontend"]["details"] = frontend_details
                return False
            
            # 启动前端进程（在后台）
            self.frontend_process = subprocess.Popen([
                sys.executable, str(frontend_main)
            ], cwd=str(self.project_root / "selfmastery"))
            
            frontend_details.append("✓ 前端进程已启动")
            self.log("前端应用已启动", "INFO")
            
            # 等待一段时间检查进程是否正常运行
            time.sleep(3)
            
            if self.frontend_process.poll() is None:
                frontend_details.append("✓ 前端进程运行正常")
                self.log("前端进程运行正常", "INFO")
            else:
                frontend_details.append("✗ 前端进程启动后立即退出")
                self.log("前端进程启动后立即退出", "ERROR")
                self.status["frontend"]["status"] = "failed"
                self.status["frontend"]["details"] = frontend_details
                return False
            
            self.status["frontend"]["status"] = "passed"
            self.status["frontend"]["details"] = frontend_details
            return True
            
        except Exception as e:
            frontend_details.append(f"✗ 前端启动异常: {str(e)}")
            self.status["frontend"]["status"] = "failed"
            self.status["frontend"]["details"] = frontend_details
            return False
    
    def start_monitoring(self):
        """开始系统监控"""
        self.log("开始系统监控", "INFO")
        self.monitoring = True
        
        # 在后台线程中运行监控
        monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        monitor_thread.start()
    
    def _monitor_system(self):
        """系统监控循环"""
        while self.monitoring:
            try:
                # 检查后端服务状态
                backend_status = "运行中"
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=5)
                    if response.status_code != 200:
                        backend_status = "异常"
                except:
                    backend_status = "离线"
                
                # 检查进程状态
                backend_process_status = "运行中" if self.backend_process and self.backend_process.poll() is None else "已停止"
                frontend_process_status = "运行中" if self.frontend_process and self.frontend_process.poll() is None else "已停止"
                
                # 更新系统状态
                self.status["system"]["details"] = [
                    f"后端服务: {backend_status}",
                    f"后端进程: {backend_process_status}",
                    f"前端进程: {frontend_process_status}",
                    f"监控时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                ]
                
                # 如果后端服务异常，尝试重启
                if backend_status == "离线" and backend_process_status == "运行中":
                    self.log("检测到后端服务异常，尝试重启", "WARNING")
                    # 这里可以添加重启逻辑
                
                time.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                self.log(f"监控过程中发生错误: {str(e)}", "ERROR")
                time.sleep(60)  # 出错时等待更长时间
    
    def display_system_status(self):
        """显示系统状态"""
        print("\n" + "="*70)
        print("SelfMastery B2B业务系统 - 启动完成")
        print("="*70)
        
        for component, status in self.status.items():
            status_icon = "✓" if status["status"] == "passed" else "✗" if status["status"] == "failed" else "○"
            print(f"{status_icon} {component}: {status['status']}")
            for detail in status["details"]:
                print(f"  - {detail}")
        
        print("="*70)
        print("系统访问地址:")
        print(f"  后端API: {self.backend_url}")
        print(f"  API文档: {self.backend_url}/docs")
        print("  前端应用: 已启动（PyQt窗口）")
        print("="*70)
        print("按 Ctrl+C 停止系统")
        print("="*70)
        
        # 保持运行状态
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("收到停止信号", "INFO")
            self.shutdown_system()
    
    def shutdown_system(self):
        """关闭系统"""
        self.log("正在关闭系统...", "INFO")
        
        # 停止监控
        self.monitoring = False
        
        # 关闭前端进程
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=10)
                self.log("前端进程已停止", "INFO")
            except:
                self.frontend_process.kill()
                self.log("强制停止前端进程", "WARNING")
        
        # 关闭后端进程
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
                self.log("后端进程已停止", "INFO")
            except:
                self.backend_process.kill()
                self.log("强制停止后端进程", "WARNING")
        
        self.log("系统已关闭", "INFO")


def main():
    """主函数"""
    print("SelfMastery B2B业务系统 - 一键启动工具")
    print("="*50)
    
    starter = SystemStarter()
    success = starter.start_system()
    
    if not success:
        print("\n系统启动失败！请检查错误信息并解决问题后重试。")
        sys.exit(1)


if __name__ == "__main__":
    main()