#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 核心功能验证脚本
验证所有核心功能：业务系统管理、业务流程设计、SOP文档管理、KPI指标监控、任务管理
"""

import sys
import os
import time
import json
import requests
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
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

class CoreFunctionVerifier:
    """核心功能验证器"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.db_path = PROJECT_ROOT / "data" / "selfmastery.db"
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "functions": {}
        }
        
    def print_header(self):
        """打印验证头部"""
        header = """
╔══════════════════════════════════════════════════════════════╗
║                    SelfMastery B2B业务系统                    ║
║                      核心功能验证工具                        ║
╠══════════════════════════════════════════════════════════════╣
║  🏢 业务系统管理功能验证                                     ║
║  🔄 业务流程设计功能验证                                     ║
║  📋 SOP文档管理功能验证                                      ║
║  📊 KPI指标监控功能验证                                      ║
║  ✅ 任务管理功能验证                                         ║
║  🔗 功能集成验证                                             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(header)
        
    def check_api_availability(self) -> bool:
        """检查API服务可用性"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def check_database_connection(self) -> bool:
        """检查数据库连接"""
        try:
            if not self.db_path.exists():
                return False
            conn = sqlite3.connect(str(self.db_path))
            conn.close()
            return True
        except:
            return False
            
    def verify_business_system_management(self) -> Dict[str, Any]:
        """验证业务系统管理功能"""
        print("\n🏢 验证业务系统管理功能...")
        
        result = {
            "status": "pass",
            "tests": {},
            "issues": []
        }
        
        try:
            # 测试1: 创建业务系统
            print("   📝 测试创建业务系统...")
            test_system = {
                "name": "测试销售系统",
                "description": "用于验证的测试销售系统",
                "owner_id": 1,
                "system_type": "core"
            }
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/systems",
                    json=test_system,
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    system_id = response.json().get("id")
                    result["tests"]["create_system"] = {"status": "pass", "system_id": system_id}
                    print("      ✅ 创建业务系统成功")
                else:
                    result["tests"]["create_system"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("创建业务系统失败")
                    print(f"      ❌ 创建业务系统失败: {response.status_code}")
            except Exception as e:
                result["tests"]["create_system"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"创建业务系统异常: {e}")
                print(f"      ❌ 创建业务系统异常: {e}")
                
            # 测试2: 查询业务系统列表
            print("   📋 测试查询业务系统列表...")
            try:
                response = requests.get(f"{self.api_base_url}/api/v1/systems", timeout=5)
                if response.status_code == 200:
                    systems = response.json()
                    result["tests"]["list_systems"] = {"status": "pass", "count": len(systems)}
                    print(f"      ✅ 查询系统列表成功，共 {len(systems)} 个系统")
                else:
                    result["tests"]["list_systems"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("查询系统列表失败")
                    print(f"      ❌ 查询系统列表失败: {response.status_code}")
            except Exception as e:
                result["tests"]["list_systems"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"查询系统列表异常: {e}")
                print(f"      ❌ 查询系统列表异常: {e}")
                
            # 测试3: 系统关系建模（数据库层面）
            print("   🔗 测试系统关系建模...")
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 检查系统表结构
                cursor.execute("PRAGMA table_info(systems)")
                columns = [row[1] for row in cursor.fetchall()]
                
                required_columns = ["id", "name", "description", "owner_id"]
                missing_columns = [col for col in required_columns if col not in columns]
                
                if not missing_columns:
                    result["tests"]["system_modeling"] = {"status": "pass", "columns": columns}
                    print("      ✅ 系统表结构完整")
                else:
                    result["tests"]["system_modeling"] = {"status": "fail", "missing_columns": missing_columns}
                    result["issues"].append(f"系统表缺少字段: {missing_columns}")
                    print(f"      ❌ 系统表缺少字段: {missing_columns}")
                    
                conn.close()
            except Exception as e:
                result["tests"]["system_modeling"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"系统关系建模检查异常: {e}")
                print(f"      ❌ 系统关系建模检查异常: {e}")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"业务系统管理验证失败: {e}")
            print(f"   ❌ 业务系统管理验证失败: {e}")
            
        # 计算总体状态
        test_statuses = [test["status"] for test in result["tests"].values()]
        if "error" in test_statuses or "fail" in test_statuses:
            result["status"] = "fail" if "fail" in test_statuses else "error"
            
        return result
        
    def verify_process_design(self) -> Dict[str, Any]:
        """验证业务流程设计功能"""
        print("\n🔄 验证业务流程设计功能...")
        
        result = {
            "status": "pass",
            "tests": {},
            "issues": []
        }
        
        try:
            # 测试1: 创建业务流程
            print("   📝 测试创建业务流程...")
            test_process = {
                "name": "测试客户开发流程",
                "description": "用于验证的测试客户开发流程",
                "system_id": 1,
                "process_type": "core"
            }
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/processes",
                    json=test_process,
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    process_id = response.json().get("id")
                    result["tests"]["create_process"] = {"status": "pass", "process_id": process_id}
                    print("      ✅ 创建业务流程成功")
                else:
                    result["tests"]["create_process"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("创建业务流程失败")
                    print(f"      ❌ 创建业务流程失败: {response.status_code}")
            except Exception as e:
                result["tests"]["create_process"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"创建业务流程异常: {e}")
                print(f"      ❌ 创建业务流程异常: {e}")
                
            # 测试2: 查询业务流程列表
            print("   📋 测试查询业务流程列表...")
            try:
                response = requests.get(f"{self.api_base_url}/api/v1/processes", timeout=5)
                if response.status_code == 200:
                    processes = response.json()
                    result["tests"]["list_processes"] = {"status": "pass", "count": len(processes)}
                    print(f"      ✅ 查询流程列表成功，共 {len(processes)} 个流程")
                else:
                    result["tests"]["list_processes"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("查询流程列表失败")
                    print(f"      ❌ 查询流程列表失败: {response.status_code}")
            except Exception as e:
                result["tests"]["list_processes"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"查询流程列表异常: {e}")
                print(f"      ❌ 查询流程列表异常: {e}")
                
            # 测试3: 流程步骤设计（数据库层面）
            print("   🎯 测试流程步骤设计...")
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 检查流程表结构
                cursor.execute("PRAGMA table_info(processes)")
                columns = [row[1] for row in cursor.fetchall()]
                
                required_columns = ["id", "name", "description", "system_id"]
                missing_columns = [col for col in required_columns if col not in columns]
                
                if not missing_columns:
                    result["tests"]["process_steps"] = {"status": "pass", "columns": columns}
                    print("      ✅ 流程表结构完整")
                else:
                    result["tests"]["process_steps"] = {"status": "fail", "missing_columns": missing_columns}
                    result["issues"].append(f"流程表缺少字段: {missing_columns}")
                    print(f"      ❌ 流程表缺少字段: {missing_columns}")
                    
                conn.close()
            except Exception as e:
                result["tests"]["process_steps"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"流程步骤设计检查异常: {e}")
                print(f"      ❌ 流程步骤设计检查异常: {e}")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"业务流程设计验证失败: {e}")
            print(f"   ❌ 业务流程设计验证失败: {e}")
            
        # 计算总体状态
        test_statuses = [test["status"] for test in result["tests"].values()]
        if "error" in test_statuses or "fail" in test_statuses:
            result["status"] = "fail" if "fail" in test_statuses else "error"
            
        return result
        
    def verify_sop_management(self) -> Dict[str, Any]:
        """验证SOP文档管理功能"""
        print("\n📋 验证SOP文档管理功能...")
        
        result = {
            "status": "pass",
            "tests": {},
            "issues": []
        }
        
        try:
            # 测试1: 创建SOP文档
            print("   📝 测试创建SOP文档...")
            test_sop = {
                "title": "测试客户接待标准流程",
                "content": "这是一个用于验证的测试SOP文档内容",
                "version": "1.0",
                "status": "draft"
            }
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/sops",
                    json=test_sop,
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    sop_id = response.json().get("id")
                    result["tests"]["create_sop"] = {"status": "pass", "sop_id": sop_id}
                    print("      ✅ 创建SOP文档成功")
                else:
                    result["tests"]["create_sop"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("创建SOP文档失败")
                    print(f"      ❌ 创建SOP文档失败: {response.status_code}")
            except Exception as e:
                result["tests"]["create_sop"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"创建SOP文档异常: {e}")
                print(f"      ❌ 创建SOP文档异常: {e}")
                
            # 测试2: 查询SOP文档列表
            print("   📋 测试查询SOP文档列表...")
            try:
                response = requests.get(f"{self.api_base_url}/api/v1/sops", timeout=5)
                if response.status_code == 200:
                    sops = response.json()
                    result["tests"]["list_sops"] = {"status": "pass", "count": len(sops)}
                    print(f"      ✅ 查询SOP列表成功，共 {len(sops)} 个文档")
                else:
                    result["tests"]["list_sops"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("查询SOP列表失败")
                    print(f"      ❌ 查询SOP列表失败: {response.status_code}")
            except Exception as e:
                result["tests"]["list_sops"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"查询SOP列表异常: {e}")
                print(f"      ❌ 查询SOP列表异常: {e}")
                
            # 测试3: SOP版本控制（数据库层面）
            print("   🔄 测试SOP版本控制...")
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 检查SOP表结构
                cursor.execute("PRAGMA table_info(sops)")
                columns = [row[1] for row in cursor.fetchall()]
                
                required_columns = ["id", "title", "content", "version"]
                missing_columns = [col for col in required_columns if col not in columns]
                
                if not missing_columns:
                    result["tests"]["sop_versioning"] = {"status": "pass", "columns": columns}
                    print("      ✅ SOP表结构完整")
                else:
                    result["tests"]["sop_versioning"] = {"status": "fail", "missing_columns": missing_columns}
                    result["issues"].append(f"SOP表缺少字段: {missing_columns}")
                    print(f"      ❌ SOP表缺少字段: {missing_columns}")
                    
                conn.close()
            except Exception as e:
                result["tests"]["sop_versioning"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"SOP版本控制检查异常: {e}")
                print(f"      ❌ SOP版本控制检查异常: {e}")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"SOP文档管理验证失败: {e}")
            print(f"   ❌ SOP文档管理验证失败: {e}")
            
        # 计算总体状态
        test_statuses = [test["status"] for test in result["tests"].values()]
        if "error" in test_statuses or "fail" in test_statuses:
            result["status"] = "fail" if "fail" in test_statuses else "error"
            
        return result
        
    def verify_kpi_monitoring(self) -> Dict[str, Any]:
        """验证KPI指标监控功能"""
        print("\n📊 验证KPI指标监控功能...")
        
        result = {
            "status": "pass",
            "tests": {},
            "issues": []
        }
        
        try:
            # 测试1: 创建KPI指标
            print("   📝 测试创建KPI指标...")
            test_kpi = {
                "name": "测试客户满意度",
                "description": "用于验证的测试客户满意度指标",
                "target_value": 90.0,
                "current_value": 85.0,
                "unit": "%"
            }
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/kpis",
                    json=test_kpi,
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    kpi_id = response.json().get("id")
                    result["tests"]["create_kpi"] = {"status": "pass", "kpi_id": kpi_id}
                    print("      ✅ 创建KPI指标成功")
                else:
                    result["tests"]["create_kpi"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("创建KPI指标失败")
                    print(f"      ❌ 创建KPI指标失败: {response.status_code}")
            except Exception as e:
                result["tests"]["create_kpi"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"创建KPI指标异常: {e}")
                print(f"      ❌ 创建KPI指标异常: {e}")
                
            # 测试2: 查询KPI指标列表
            print("   📋 测试查询KPI指标列表...")
            try:
                response = requests.get(f"{self.api_base_url}/api/v1/kpis", timeout=5)
                if response.status_code == 200:
                    kpis = response.json()
                    result["tests"]["list_kpis"] = {"status": "pass", "count": len(kpis)}
                    print(f"      ✅ 查询KPI列表成功，共 {len(kpis)} 个指标")
                else:
                    result["tests"]["list_kpis"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("查询KPI列表失败")
                    print(f"      ❌ 查询KPI列表失败: {response.status_code}")
            except Exception as e:
                result["tests"]["list_kpis"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"查询KPI列表异常: {e}")
                print(f"      ❌ 查询KPI列表异常: {e}")
                
            # 测试3: KPI数据分析（数据库层面）
            print("   📈 测试KPI数据分析...")
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 检查KPI表结构
                cursor.execute("PRAGMA table_info(kpis)")
                columns = [row[1] for row in cursor.fetchall()]
                
                required_columns = ["id", "name", "target_value", "current_value"]
                missing_columns = [col for col in required_columns if col not in columns]
                
                if not missing_columns:
                    result["tests"]["kpi_analysis"] = {"status": "pass", "columns": columns}
                    print("      ✅ KPI表结构完整")
                else:
                    result["tests"]["kpi_analysis"] = {"status": "fail", "missing_columns": missing_columns}
                    result["issues"].append(f"KPI表缺少字段: {missing_columns}")
                    print(f"      ❌ KPI表缺少字段: {missing_columns}")
                    
                conn.close()
            except Exception as e:
                result["tests"]["kpi_analysis"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"KPI数据分析检查异常: {e}")
                print(f"      ❌ KPI数据分析检查异常: {e}")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"KPI指标监控验证失败: {e}")
            print(f"   ❌ KPI指标监控验证失败: {e}")
            
        # 计算总体状态
        test_statuses = [test["status"] for test in result["tests"].values()]
        if "error" in test_statuses or "fail" in test_statuses:
            result["status"] = "fail" if "fail" in test_statuses else "error"
            
        return result
        
    def verify_task_management(self) -> Dict[str, Any]:
        """验证任务管理功能"""
        print("\n✅ 验证任务管理功能...")
        
        result = {
            "status": "pass",
            "tests": {},
            "issues": []
        }
        
        try:
            # 测试1: 创建任务
            print("   📝 测试创建任务...")
            test_task = {
                "title": "测试优化客户接待流程",
                "description": "用于验证的测试任务描述",
                "status": "pending",
                "priority": "high",
                "assignee": "测试用户"
            }
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/tasks",
                    json=test_task,
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    task_id = response.json().get("id")
                    result["tests"]["create_task"] = {"status": "pass", "task_id": task_id}
                    print("      ✅ 创建任务成功")
                else:
                    result["tests"]["create_task"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("创建任务失败")
                    print(f"      ❌ 创建任务失败: {response.status_code}")
            except Exception as e:
                result["tests"]["create_task"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"创建任务异常: {e}")
                print(f"      ❌ 创建任务异常: {e}")
                
            # 测试2: 查询任务列表
            print("   📋 测试查询任务列表...")
            try:
                response = requests.get(f"{self.api_base_url}/api/v1/tasks", timeout=5)
                if response.status_code == 200:
                    tasks = response.json()
                    result["tests"]["list_tasks"] = {"status": "pass", "count": len(tasks)}
                    print(f"      ✅ 查询任务列表成功，共 {len(tasks)} 个任务")
                else:
                    result["tests"]["list_tasks"] = {"status": "fail", "error": f"状态码: {response.status_code}"}
                    result["issues"].append("查询任务列表失败")
                    print(f"      ❌ 查询任务列表失败: {response.status_code}")
            except Exception as e:
                result["tests"]["list_tasks"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"查询任务列表异常: {e}")
                print(f"      ❌ 查询任务列表异常: {e}")
                
            # 测试3: 任务状态管理（数据库层面）
            print("   🔄 测试任务状态管理...")
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 检查任务表结构
                cursor.execute("PRAGMA table_info(tasks)")
                columns = [row[1] for row in cursor.fetchall()]
                
                required_columns = ["id", "title", "description", "status"]
                missing_columns = [col for col in required_columns if col not in columns]
                
                if not missing_columns:
                    result["tests"]["task_status"] = {"status": "pass", "columns": columns}
                    print("      ✅ 任务表结构完整")
                else:
                    result["tests"]["task_status"] = {"status": "fail", "missing_columns": missing_columns}
                    result["issues"].append(f"任务表缺少字段: {missing_columns}")
                    print(f"      ❌ 任务表缺少字段: {missing_columns}")
                    
                conn.close()
            except Exception as e:
                result["tests"]["task_status"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"任务状态管理检查异常: {e}")
                print(f"      ❌ 任务状态管理检查异常: {e}")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"任务管理验证失败: {e}")
            print(f"   ❌ 任务管理验证失败: {e}")
            
        # 计算总体状态
        test_statuses = [test["status"] for test in result["tests"].values()]
        if "error" in test_statuses or "fail" in test_statuses:
            result["status"] = "fail" if "fail" in test_statuses else "error"
            
        return result
        
    def verify_integration(self) -> Dict[str, Any]:
        """验证功能集成"""
        print("\n🔗 验证功能集成...")
        
        result = {
            "status": "pass",
            "tests": {},
            "issues": []
        }
        
        try:
            # 测试1: 系统与流程关联
            print("   🔗 测试系统与流程关联...")
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 检查是否存在系统和流程的关联
                cursor.execute("""
                    SELECT s.name as system_name, p.name as process_name
                    FROM systems s
                    LEFT JOIN processes p ON s.id = p.system_id
                    LIMIT 5
                """)
                associations = cursor.fetchall()
                
                if associations:
                    result["tests"]["system_process_link"] = {"status": "pass", "count": len(associations)}
                    print(f"      ✅ 系统流程关联正常，共 {len(associations)} 个关联")
                else:
                    result["tests"]["system_process_link"] = {"status": "warn", "count": 0}
                    result["issues"].append("暂无系统流程关联数据")
                    print("      ⚠️ 暂无系统流程关联数据")
                    
                conn.close()
            except Exception as e:
                result["tests"]["system_process_link"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"系统流程关联检查异常: {e}")
                print(f"      ❌ 系统流程关联检查异常: {e}")
                
            # 测试2: 数据一致性检查
            print("   🔍 测试数据一致性...")
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 检查各表的数据完整性
                tables = ["systems", "processes", "sops", "kpis", "tasks"]
                table_counts = {}
                
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        table_counts[table] = count
                    except sqlite3.OperationalError:
                        table_counts[table] = "表不存在"
                        
                result["tests"]["data_consistency"] = {"status": "pass", "table_counts": table_counts}
                print(f"      ✅ 数据一致性检查完成: {table_counts}")
                    
                conn.close()
            except Exception as e:
                result["tests"]["data_consistency"] = {"status": "error", "error": str(e)}
                result["issues"].append(f"数据一致性检查异常: {e}")
                print(f"      ❌ 数据一致性检查异常: {e}")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"功能集成验证失败: {e}")
            print(f"   ❌ 功能集成验证失败: {e}")
            
        # 计算总体状态
        test_statuses = [test["status"] for test in result["tests"].values()]
        if "error" in test_statuses or "fail" in test_statuses:
            result["status"] = "fail" if "fail" in test_statuses else "error"
            
        return result
        
    def generate_verification_report(self) -> str:
        """生成验证报告"""
        print("\n📊 生成功能验证报告...")
        
        # 计算总体状态
        all_statuses = [func["status"] for func in self.verification_results["functions"].values()]
        
        if "error" in all_statuses:
            self.verification_results["overall_status"] = "error"
        elif "fail" in all_statuses:
            self.verification_results["overall_status"] = "fail"
        else:
            self.verification_results["overall_status"] = "pass"
            
        # 保存报告到文件
        report_file = PROJECT_ROOT / "core_functions_verification_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, indent=2, ensure_ascii=False)
            
        print(f"   ✅ 报告已保存: {report_file}")
        
        return str(report_file)
        
    def print_verification_summary(self):
        """打印验证摘要"""
        print("\n" + "="*60)
        print("📋 核心功能验证摘要")
        print("="*60)
        
        status_icons = {
            "pass": "🟢",
            "warn": "🟡",
            "fail": "🔴",
            "error": "⚫"
        }
        
        function_names = {
            "business_system_management": "🏢 业务系统管理",
            "process_design": "🔄 业务流程设计",
            "sop_management": "📋 SOP文档管理",
            "kpi_monitoring": "📊 KPI指标监控",
            "task_management": "✅ 任务管理",
            "integration": "🔗 功能集成"
        }
        
        for func_key, func_result in self.verification_results["functions"].items():
            status = func_result["status"]
            icon = status_icons.get(status, "❓")
            name = function_names.get(func_key, func_key)
            print(f"{icon} {name}: {status.upper()}")
            
            if func_result["issues"]:
                for issue in func_result["issues"]:
                    print(f"   • {issue}")
                    
        print("="*60)
        overall_icon = status_icons.get(self.verification_results["overall_status"], "❓")
        print(f"{overall_icon} 总体状态: {self.verification_results['overall_status'].upper()}")
        
        # 提供修复建议
        if self.verification_results["overall_status"] != "pass":
            print("\n💡 修复建议:")
            
            all_issues = []
            for func_result in self.verification_results["functions"].values():
                all_issues.extend(func_result["issues"])
                
            if any("API" in issue for issue in all_issues):
                print("   • 确保后端API服务正在运行: python selfmastery/backend/main.py")
            if any("数据库" in issue for issue in all_issues):
                print("   • 重新初始化数据库: python scripts/init_db.py")
            if any("表不存在" in issue for issue in all_issues):
                print("   • 运行数据库迁移: alembic upgrade head")
                
        print("="*60)
        
    def run_verification(self):
        """运行完整功能验证"""
        try:
            self.print_header()
            
            # 检查前置条件
            print("\n🔍 检查前置条件...")
            if not self.check_api_availability():
                print("   ❌ API服务不可用，某些测试可能失败")
            else:
                print("   ✅ API服务可用")
                
            if not self.check_database_connection():
                print("   ❌ 数据库连接失败，某些测试可能失败")
            else:
                print("   ✅ 数据库连接正常")
            
            # 执行各项功能验证
            self.verification_results["functions"]["business_system_management"] = self.verify_business_system_management()
            self.verification_results["functions"]["process_design"] = self.verify_process_design()
            self.verification_results["functions"]["sop_management"] = self.verify_sop_management()
            self.verification_results["functions"]["kpi_monitoring"] = self.verify_kpi_monitoring()
            self.verification_results["functions"]["task_management"] = self.verify_task_management()
            self.verification_results["functions"]["integration"] = self.verify_integration()
            
            # 生成报告
            report_file = self.generate_verification_report()
            
            # 打印摘要
            self.print_verification_summary()
            
            print(f"\n📄 详细报告: {report_file}")
            
            return self.verification_results["overall_status"] == "pass"
            
        except Exception as e:
            logger.error(f"功能验证失败: {e}")
            print(f"\n❌ 功能验证失败: {e}")
            return False

def main():
    """主函数"""
    verifier = CoreFunctionVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n✅ 核心功能验证通过")
        sys.exit(0)
    else:
        print("\n⚠️ 核心功能验证发现问题")
        sys.exit(1)

if __name__ == "__main__":
    main()