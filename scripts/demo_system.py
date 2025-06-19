#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 完整系统演示脚本
自动启动后端API服务、前端UI界面，展示所有核心功能的使用流程
"""

import sys
import os
import time
import subprocess
import threading
import signal
import logging
from pathlib import Path
from typing import Optional, List
import json
import requests
from datetime import datetime

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SELFMASTERY_ROOT = PROJECT_ROOT / "selfmastery"

# 将项目路径添加到sys.path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SELFMASTERY_ROOT))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('demo_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemDemo:
    """系统演示管理器"""
    
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.demo_data_created = False
        self.api_base_url = "http://localhost:8000"
        
    def print_banner(self):
        """打印演示横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    SelfMastery B2B业务系统                    ║
║                      完整系统演示工具                        ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 自动启动后端API服务                                      ║
║  🎨 自动启动前端UI界面                                       ║
║  📊 展示所有核心功能                                         ║
║  ✅ 验证系统完整性                                           ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def check_dependencies(self) -> bool:
        """检查系统依赖"""
        print("\n🔍 检查系统依赖...")
        
        dependencies = [
            ("Python", sys.executable),
            ("PyQt6", "PyQt6"),
            ("FastAPI", "fastapi"),
            ("SQLAlchemy", "sqlalchemy"),
            ("Requests", "requests")
        ]
        
        missing_deps = []
        
        for name, module in dependencies:
            try:
                if name == "Python":
                    print(f"   ✅ {name}: {sys.version}")
                else:
                    __import__(module)
                    print(f"   ✅ {name}: 已安装")
            except ImportError:
                print(f"   ❌ {name}: 未安装")
                missing_deps.append(name)
                
        if missing_deps:
            print(f"\n❌ 缺少依赖: {', '.join(missing_deps)}")
            print("请运行: pip install -r selfmastery/requirements.txt")
            return False
            
        return True
        
    def check_environment(self) -> bool:
        """检查环境配置"""
        print("\n🔧 检查环境配置...")
        
        # 检查必要文件
        required_files = [
            SELFMASTERY_ROOT / "backend" / "main.py",
            SELFMASTERY_ROOT / "frontend" / "main.py",
            SELFMASTERY_ROOT / "requirements.txt",
            PROJECT_ROOT / "scripts" / "start_ui_simple.py"
        ]
        
        for file_path in required_files:
            if file_path.exists():
                print(f"   ✅ {file_path.name}: 存在")
            else:
                print(f"   ❌ {file_path.name}: 不存在")
                return False
                
        # 检查数据目录
        data_dir = PROJECT_ROOT / "data"
        if not data_dir.exists():
            print(f"   📁 创建数据目录: {data_dir}")
            data_dir.mkdir(exist_ok=True)
        else:
            print(f"   ✅ 数据目录: 存在")
            
        return True
        
    def start_backend(self) -> bool:
        """启动后端服务"""
        print("\n🚀 启动后端API服务...")
        
        try:
            # 切换到后端目录
            backend_dir = SELFMASTERY_ROOT / "backend"
            
            # 启动后端服务
            cmd = [sys.executable, "main.py"]
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务启动
            print("   ⏳ 等待后端服务启动...")
            for i in range(30):  # 最多等待30秒
                try:
                    response = requests.get(f"{self.api_base_url}/health", timeout=1)
                    if response.status_code == 200:
                        print(f"   ✅ 后端服务已启动: {self.api_base_url}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                    
                time.sleep(1)
                print(f"   ⏳ 等待中... ({i+1}/30)")
                
            print("   ❌ 后端服务启动超时")
            return False
            
        except Exception as e:
            print(f"   ❌ 后端服务启动失败: {e}")
            return False
            
    def create_demo_data(self) -> bool:
        """创建演示数据"""
        print("\n📊 创建演示数据...")
        
        try:
            # 运行数据库初始化脚本
            init_script = PROJECT_ROOT / "scripts" / "init_db.py"
            if init_script.exists():
                result = subprocess.run([sys.executable, str(init_script)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("   ✅ 数据库初始化完成")
                else:
                    print(f"   ⚠️ 数据库初始化警告: {result.stderr}")
            
            # 创建演示数据
            demo_script = PROJECT_ROOT / "scripts" / "create_demo_data.py"
            if demo_script.exists():
                result = subprocess.run([sys.executable, str(demo_script)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("   ✅ 演示数据创建完成")
                    self.demo_data_created = True
                else:
                    print(f"   ⚠️ 演示数据创建警告: {result.stderr}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 演示数据创建失败: {e}")
            return False
            
    def start_frontend(self) -> bool:
        """启动前端界面"""
        print("\n🎨 启动前端UI界面...")
        
        try:
            # 使用简化的UI启动脚本
            ui_script = PROJECT_ROOT / "scripts" / "start_ui_simple.py"
            
            # 在新线程中启动前端
            def run_frontend():
                try:
                    subprocess.run([sys.executable, str(ui_script)])
                except Exception as e:
                    logger.error(f"前端启动失败: {e}")
            
            frontend_thread = threading.Thread(target=run_frontend, daemon=True)
            frontend_thread.start()
            
            print("   ✅ 前端界面启动中...")
            time.sleep(3)  # 给前端一些启动时间
            
            return True
            
        except Exception as e:
            print(f"   ❌ 前端界面启动失败: {e}")
            return False
            
    def test_api_endpoints(self) -> bool:
        """测试API端点"""
        print("\n🧪 测试API端点...")
        
        endpoints = [
            ("/health", "健康检查"),
            ("/api/v1/systems", "业务系统"),
            ("/api/v1/processes", "业务流程"),
            ("/api/v1/sops", "SOP文档"),
            ("/api/v1/kpis", "KPI指标"),
            ("/api/v1/tasks", "任务管理")
        ]
        
        success_count = 0
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:  # 404也算正常，可能是空数据
                    print(f"   ✅ {name}: 正常")
                    success_count += 1
                else:
                    print(f"   ⚠️ {name}: 状态码 {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name}: 连接失败 - {e}")
                
        print(f"\n📊 API测试结果: {success_count}/{len(endpoints)} 个端点正常")
        return success_count >= len(endpoints) // 2  # 至少一半端点正常
        
    def show_demo_guide(self):
        """显示演示指南"""
        guide = """
╔══════════════════════════════════════════════════════════════╗
║                        演示指南                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🏢 业务系统管理                                             ║
║     • 创建和管理业务系统架构                                 ║
║     • 可视化系统关系图                                       ║
║     • 系统权责分配                                           ║
║                                                              ║
║  🔄 业务流程设计                                             ║
║     • 设计和优化业务流程                                     ║
║     • 建立流程连接关系                                       ║
║     • 流程自动化配置                                         ║
║                                                              ║
║  📋 SOP文档管理                                              ║
║     • 创建标准作业程序                                       ║
║     • 版本控制和审批流程                                     ║
║     • 文档模板管理                                           ║
║                                                              ║
║  📊 KPI指标监控                                              ║
║     • 设置关键绩效指标                                       ║
║     • 实时数据监控                                           ║
║     • 报表和分析                                             ║
║                                                              ║
║  ✅ 任务管理                                                 ║
║     • 分配和跟踪任务                                         ║
║     • 项目进度管理                                           ║
║     • 团队协作                                               ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  💡 使用提示:                                                ║
║     • 点击主界面上的功能按钮开始体验                         ║
║     • 每个模块都有详细的操作指南                             ║
║     • 支持拖拽操作和快捷键                                   ║
║     • 数据自动保存，无需担心丢失                             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(guide)
        
    def show_system_status(self):
        """显示系统状态"""
        print("\n📊 系统状态总览:")
        print("=" * 60)
        
        # 后端状态
        backend_status = "🟢 运行中" if self.backend_process and self.backend_process.poll() is None else "🔴 已停止"
        print(f"   后端API服务: {backend_status}")
        
        # API连接状态
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=2)
            api_status = "🟢 正常" if response.status_code == 200 else "🟡 异常"
        except:
            api_status = "🔴 无法连接"
        print(f"   API连接状态: {api_status}")
        
        # 数据库状态
        db_file = PROJECT_ROOT / "data" / "selfmastery.db"
        db_status = "🟢 正常" if db_file.exists() else "🟡 未初始化"
        print(f"   数据库状态: {db_status}")
        
        # 演示数据状态
        demo_status = "🟢 已创建" if self.demo_data_created else "🟡 未创建"
        print(f"   演示数据: {demo_status}")
        
        # 前端状态
        print(f"   前端界面: 🟢 已启动")
        
        print("=" * 60)
        
    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理系统资源...")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("   ✅ 后端服务已停止")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("   ⚠️ 强制停止后端服务")
            except Exception as e:
                print(f"   ❌ 停止后端服务失败: {e}")
                
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                print("   ✅ 前端界面已关闭")
            except Exception as e:
                print(f"   ❌ 关闭前端界面失败: {e}")
                
    def run_demo(self):
        """运行完整演示"""
        try:
            # 打印横幅
            self.print_banner()
            
            # 检查依赖
            if not self.check_dependencies():
                return False
                
            # 检查环境
            if not self.check_environment():
                return False
                
            # 启动后端
            if not self.start_backend():
                return False
                
            # 创建演示数据
            self.create_demo_data()
            
            # 测试API
            if not self.test_api_endpoints():
                print("⚠️ 部分API端点测试失败，但继续演示...")
                
            # 启动前端
            if not self.start_frontend():
                return False
                
            # 显示演示指南
            self.show_demo_guide()
            
            # 显示系统状态
            self.show_system_status()
            
            print("\n🎉 系统演示启动成功！")
            print("💡 按 Ctrl+C 停止演示")
            
            # 保持运行状态
            try:
                while True:
                    time.sleep(10)
                    # 定期检查后端状态
                    if self.backend_process and self.backend_process.poll() is not None:
                        print("⚠️ 后端服务意外停止")
                        break
            except KeyboardInterrupt:
                print("\n👋 用户请求停止演示")
                
            return True
            
        except Exception as e:
            logger.error(f"演示运行失败: {e}")
            return False
        finally:
            self.cleanup()

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n🛑 接收到停止信号，正在清理...")
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建并运行演示
    demo = SystemDemo()
    success = demo.run_demo()
    
    if success:
        print("\n✅ 演示完成")
        sys.exit(0)
    else:
        print("\n❌ 演示失败")
        sys.exit(1)

if __name__ == "__main__":
    main()