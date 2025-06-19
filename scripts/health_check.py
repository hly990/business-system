#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 系统健康检查脚本
检查所有依赖、数据库连接、API服务、前端组件状态
"""

import sys
import os
import time
import subprocess
import json
import sqlite3
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import logging

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SELFMASTERY_ROOT = PROJECT_ROOT / "selfmastery"

# 将项目路径添加到sys.path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SELFMASTERY_ROOT))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {}
        }
        self.api_base_url = "http://localhost:8000"
        
    def print_header(self):
        """打印检查头部"""
        header = """
╔══════════════════════════════════════════════════════════════╗
║                    SelfMastery B2B业务系统                    ║
║                      系统健康检查工具                        ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 检查系统依赖                                             ║
║  🗄️ 检查数据库状态                                           ║
║  🌐 检查API服务                                              ║
║  🎨 检查前端组件                                             ║
║  📊 生成健康报告                                             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(header)
        
    def check_python_environment(self) -> Dict[str, Any]:
        """检查Python环境"""
        print("\n🐍 检查Python环境...")
        
        result = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        try:
            # Python版本
            python_version = sys.version_info
            result["details"]["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            
            if python_version >= (3, 8):
                print(f"   ✅ Python版本: {result['details']['python_version']}")
            else:
                print(f"   ❌ Python版本过低: {result['details']['python_version']} (需要 >= 3.8)")
                result["status"] = "fail"
                result["issues"].append("Python版本过低")
                
            # 虚拟环境检查
            venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            result["details"]["virtual_env"] = venv_active
            
            if venv_active:
                print("   ✅ 虚拟环境: 已激活")
            else:
                print("   ⚠️ 虚拟环境: 未激活 (建议使用虚拟环境)")
                result["issues"].append("未使用虚拟环境")
                
            # 检查项目路径
            result["details"]["project_root"] = str(PROJECT_ROOT)
            result["details"]["selfmastery_root"] = str(SELFMASTERY_ROOT)
            
            if PROJECT_ROOT.exists() and SELFMASTERY_ROOT.exists():
                print(f"   ✅ 项目路径: {PROJECT_ROOT}")
            else:
                print(f"   ❌ 项目路径错误: {PROJECT_ROOT}")
                result["status"] = "fail"
                result["issues"].append("项目路径不存在")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Python环境检查失败: {e}")
            print(f"   ❌ Python环境检查失败: {e}")
            
        return result
        
    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖包"""
        print("\n📦 检查依赖包...")
        
        result = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # 核心依赖列表
        core_dependencies = [
            ("PyQt6", "PyQt6"),
            ("FastAPI", "fastapi"),
            ("SQLAlchemy", "sqlalchemy"),
            ("Requests", "requests"),
            ("Pydantic", "pydantic"),
            ("Uvicorn", "uvicorn"),
            ("Alembic", "alembic")
        ]
        
        # 可选依赖列表
        optional_dependencies = [
            ("Redis", "redis"),
            ("Celery", "celery"),
            ("Sentry SDK", "sentry_sdk"),
            ("Pytest", "pytest")
        ]
        
        try:
            # 检查核心依赖
            for name, module in core_dependencies:
                try:
                    imported_module = __import__(module)
                    version = getattr(imported_module, '__version__', 'unknown')
                    result["details"][module] = {
                        "installed": True,
                        "version": version,
                        "required": True
                    }
                    print(f"   ✅ {name}: {version}")
                except ImportError:
                    result["details"][module] = {
                        "installed": False,
                        "version": None,
                        "required": True
                    }
                    result["status"] = "fail"
                    result["issues"].append(f"缺少核心依赖: {name}")
                    print(f"   ❌ {name}: 未安装")
                    
            # 检查可选依赖
            for name, module in optional_dependencies:
                try:
                    imported_module = __import__(module)
                    version = getattr(imported_module, '__version__', 'unknown')
                    result["details"][module] = {
                        "installed": True,
                        "version": version,
                        "required": False
                    }
                    print(f"   ✅ {name}: {version}")
                except ImportError:
                    result["details"][module] = {
                        "installed": False,
                        "version": None,
                        "required": False
                    }
                    print(f"   ⚠️ {name}: 未安装 (可选)")
                    
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"依赖检查失败: {e}")
            print(f"   ❌ 依赖检查失败: {e}")
            
        return result
        
    def check_file_structure(self) -> Dict[str, Any]:
        """检查文件结构"""
        print("\n📁 检查文件结构...")
        
        result = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # 必需文件列表
        required_files = [
            "selfmastery/backend/main.py",
            "selfmastery/frontend/main.py",
            "selfmastery/requirements.txt",
            "selfmastery/config/settings.py",
            "selfmastery/config/database.py",
            "scripts/start_ui_simple.py",
            "scripts/init_db.py"
        ]
        
        # 必需目录列表
        required_dirs = [
            "selfmastery/backend",
            "selfmastery/frontend",
            "selfmastery/backend/api",
            "selfmastery/backend/models",
            "selfmastery/backend/services",
            "selfmastery/frontend/ui",
            "selfmastery/frontend/widgets",
            "data",
            "docs",
            "scripts"
        ]
        
        try:
            # 检查文件
            missing_files = []
            for file_path in required_files:
                full_path = PROJECT_ROOT / file_path
                if full_path.exists():
                    result["details"][file_path] = {"exists": True, "type": "file"}
                    print(f"   ✅ {file_path}")
                else:
                    result["details"][file_path] = {"exists": False, "type": "file"}
                    missing_files.append(file_path)
                    print(f"   ❌ {file_path}: 不存在")
                    
            # 检查目录
            missing_dirs = []
            for dir_path in required_dirs:
                full_path = PROJECT_ROOT / dir_path
                if full_path.exists() and full_path.is_dir():
                    result["details"][dir_path] = {"exists": True, "type": "directory"}
                    print(f"   ✅ {dir_path}/")
                else:
                    result["details"][dir_path] = {"exists": False, "type": "directory"}
                    missing_dirs.append(dir_path)
                    print(f"   ❌ {dir_path}/: 不存在")
                    
            if missing_files or missing_dirs:
                result["status"] = "fail"
                result["issues"].extend([f"缺少文件: {f}" for f in missing_files])
                result["issues"].extend([f"缺少目录: {d}" for d in missing_dirs])
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"文件结构检查失败: {e}")
            print(f"   ❌ 文件结构检查失败: {e}")
            
        return result
        
    def check_database(self) -> Dict[str, Any]:
        """检查数据库状态"""
        print("\n🗄️ 检查数据库状态...")
        
        result = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        try:
            # 检查数据库文件
            db_file = PROJECT_ROOT / "data" / "selfmastery.db"
            result["details"]["database_file"] = str(db_file)
            result["details"]["file_exists"] = db_file.exists()
            
            if db_file.exists():
                print(f"   ✅ 数据库文件: {db_file}")
                
                # 检查数据库连接
                try:
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    
                    # 检查表结构
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    result["details"]["tables"] = tables
                    
                    expected_tables = ["users", "systems", "processes", "sops", "kpis", "tasks"]
                    missing_tables = [t for t in expected_tables if t not in tables]
                    
                    if missing_tables:
                        result["status"] = "warn"
                        result["issues"].append(f"缺少数据表: {missing_tables}")
                        print(f"   ⚠️ 缺少数据表: {missing_tables}")
                    else:
                        print(f"   ✅ 数据表完整: {len(tables)} 个表")
                        
                    # 检查数据库大小
                    db_size = db_file.stat().st_size
                    result["details"]["database_size"] = db_size
                    print(f"   ✅ 数据库大小: {db_size / 1024:.1f} KB")
                    
                    conn.close()
                    
                except sqlite3.Error as e:
                    result["status"] = "fail"
                    result["issues"].append(f"数据库连接失败: {e}")
                    print(f"   ❌ 数据库连接失败: {e}")
                    
            else:
                result["status"] = "warn"
                result["issues"].append("数据库文件不存在")
                print(f"   ⚠️ 数据库文件不存在: {db_file}")
                print("   💡 运行 'python scripts/init_db.py' 初始化数据库")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"数据库检查失败: {e}")
            print(f"   ❌ 数据库检查失败: {e}")
            
        return result
        
    def check_api_service(self) -> Dict[str, Any]:
        """检查API服务状态"""
        print("\n🌐 检查API服务状态...")
        
        result = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        try:
            # 检查API服务是否运行
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=5)
                result["details"]["api_running"] = True
                result["details"]["status_code"] = response.status_code
                result["details"]["response_time"] = response.elapsed.total_seconds()
                
                if response.status_code == 200:
                    print(f"   ✅ API服务运行正常: {self.api_base_url}")
                    print(f"   ✅ 响应时间: {response.elapsed.total_seconds():.3f}s")
                    
                    # 测试主要API端点
                    endpoints = [
                        "/api/v1/systems",
                        "/api/v1/processes", 
                        "/api/v1/sops",
                        "/api/v1/kpis",
                        "/api/v1/tasks"
                    ]
                    
                    endpoint_results = {}
                    for endpoint in endpoints:
                        try:
                            ep_response = requests.get(f"{self.api_base_url}{endpoint}", timeout=3)
                            endpoint_results[endpoint] = {
                                "status_code": ep_response.status_code,
                                "accessible": ep_response.status_code in [200, 404, 422]
                            }
                            status = "✅" if endpoint_results[endpoint]["accessible"] else "❌"
                            print(f"   {status} {endpoint}: {ep_response.status_code}")
                        except Exception as e:
                            endpoint_results[endpoint] = {
                                "status_code": None,
                                "accessible": False,
                                "error": str(e)
                            }
                            print(f"   ❌ {endpoint}: 连接失败")
                            
                    result["details"]["endpoints"] = endpoint_results
                    
                else:
                    result["status"] = "fail"
                    result["issues"].append(f"API服务状态异常: {response.status_code}")
                    print(f"   ❌ API服务状态异常: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                result["details"]["api_running"] = False
                result["status"] = "fail"
                result["issues"].append("API服务未运行")
                print(f"   ❌ API服务未运行: {self.api_base_url}")
                print("   💡 运行 'python selfmastery/backend/main.py' 启动API服务")
                
            except requests.exceptions.Timeout:
                result["details"]["api_running"] = False
                result["status"] = "fail"
                result["issues"].append("API服务响应超时")
                print(f"   ❌ API服务响应超时: {self.api_base_url}")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"API服务检查失败: {e}")
            print(f"   ❌ API服务检查失败: {e}")
            
        return result
        
    def check_frontend_components(self) -> Dict[str, Any]:
        """检查前端组件状态"""
        print("\n🎨 检查前端组件状态...")
        
        result = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        try:
            # 检查PyQt6可用性
            try:
                import PyQt6.QtWidgets
                import PyQt6.QtCore
                import PyQt6.QtGui
                result["details"]["pyqt6_available"] = True
                print("   ✅ PyQt6: 可用")
                
                # 检查是否可以创建QApplication
                try:
                    from PyQt6.QtWidgets import QApplication
                    import sys
                    
                    # 检查是否已有QApplication实例
                    app = QApplication.instance()
                    if app is None:
                        # 创建临时应用测试
                        test_app = QApplication([])
                        result["details"]["qapplication_creatable"] = True
                        print("   ✅ QApplication: 可创建")
                        test_app.quit()
                    else:
                        result["details"]["qapplication_creatable"] = True
                        print("   ✅ QApplication: 已存在实例")
                        
                except Exception as e:
                    result["details"]["qapplication_creatable"] = False
                    result["status"] = "warn"
                    result["issues"].append(f"QApplication创建失败: {e}")
                    print(f"   ⚠️ QApplication创建失败: {e}")
                    
            except ImportError as e:
                result["details"]["pyqt6_available"] = False
                result["status"] = "fail"
                result["issues"].append("PyQt6不可用")
                print(f"   ❌ PyQt6不可用: {e}")
                
            # 检查UI组件文件
            ui_components = [
                "scripts/ui_components/system_management.py",
                "scripts/ui_components/process_design.py",
                "scripts/ui_components/sop_management.py",
                "scripts/ui_components/kpi_dashboard.py",
                "scripts/ui_components/task_management.py"
            ]
            
            component_status = {}
            for component in ui_components:
                component_path = PROJECT_ROOT / component
                component_name = component.split('/')[-1].replace('.py', '')
                
                if component_path.exists():
                    component_status[component_name] = {"exists": True}
                    print(f"   ✅ {component_name}: 存在")
                else:
                    component_status[component_name] = {"exists": False}
                    result["status"] = "warn"
                    result["issues"].append(f"UI组件缺失: {component_name}")
                    print(f"   ⚠️ {component_name}: 不存在")
                    
            result["details"]["ui_components"] = component_status
            
            # 检查启动脚本
            start_script = PROJECT_ROOT / "scripts" / "start_ui_simple.py"
            if start_script.exists():
                result["details"]["start_script_exists"] = True
                print("   ✅ UI启动脚本: 存在")
            else:
                result["details"]["start_script_exists"] = False
                result["status"] = "fail"
                result["issues"].append("UI启动脚本不存在")
                print("   ❌ UI启动脚本: 不存在")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"前端组件检查失败: {e}")
            print(f"   ❌ 前端组件检查失败: {e}")
            
        return result
        
    def generate_report(self) -> str:
        """生成健康检查报告"""
        print("\n📊 生成健康检查报告...")
        
        # 计算总体状态
        all_statuses = [check["status"] for check in self.results["checks"].values()]
        
        if "error" in all_statuses:
            self.results["overall_status"] = "error"
        elif "fail" in all_statuses:
            self.results["overall_status"] = "fail"
        elif "warn" in all_statuses:
            self.results["overall_status"] = "warn"
        else:
            self.results["overall_status"] = "pass"
            
        # 保存报告到文件
        report_file = PROJECT_ROOT / "health_check_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        print(f"   ✅ 报告已保存: {report_file}")
        
        return str(report_file)
        
    def print_summary(self):
        """打印检查摘要"""
        print("\n" + "="*60)
        print("📋 健康检查摘要")
        print("="*60)
        
        status_icons = {
            "pass": "🟢",
            "warn": "🟡", 
            "fail": "🔴",
            "error": "⚫"
        }
        
        for check_name, check_result in self.results["checks"].items():
            status = check_result["status"]
            icon = status_icons.get(status, "❓")
            print(f"{icon} {check_name}: {status.upper()}")
            
            if check_result["issues"]:
                for issue in check_result["issues"]:
                    print(f"   • {issue}")
                    
        print("="*60)
        overall_icon = status_icons.get(self.results["overall_status"], "❓")
        print(f"{overall_icon} 总体状态: {self.results['overall_status'].upper()}")
        
        # 提供修复建议
        if self.results["overall_status"] != "pass":
            print("\n💡 修复建议:")
            
            all_issues = []
            for check_result in self.results["checks"].values():
                all_issues.extend(check_result["issues"])
                
            if "缺少核心依赖" in str(all_issues):
                print("   • 运行: pip install -r selfmastery/requirements.txt")
            if "数据库文件不存在" in str(all_issues):
                print("   • 运行: python scripts/init_db.py")
            if "API服务未运行" in str(all_issues):
                print("   • 运行: python selfmastery/backend/main.py")
            if "PyQt6不可用" in str(all_issues):
                print("   • 运行: pip install PyQt6")
                
        print("="*60)
        
    def run_health_check(self):
        """运行完整健康检查"""
        try:
            self.print_header()
            
            # 执行各项检查
            self.results["checks"]["python_environment"] = self.check_python_environment()
            self.results["checks"]["dependencies"] = self.check_dependencies()
            self.results["checks"]["file_structure"] = self.check_file_structure()
            self.results["checks"]["database"] = self.check_database()
            self.results["checks"]["api_service"] = self.check_api_service()
            self.results["checks"]["frontend_components"] = self.check_frontend_components()
            
            # 生成报告
            report_file = self.generate_report()
            
            # 打印摘要
            self.print_summary()
            
            print(f"\n📄 详细报告: {report_file}")
            
            return self.results["overall_status"] == "pass"
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            print(f"\n❌ 健康检查失败: {e}")
            return False

def main():
    """主函数"""
    checker = HealthChecker()
    success = checker.run_health_check()
    
    if success:
        print("\n✅ 系统健康检查通过")
        sys.exit(0)
    else:
        print("\n⚠️ 系统健康检查发现问题")
        sys.exit(1)

if __name__ == "__main__":
    main()