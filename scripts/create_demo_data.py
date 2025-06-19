#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 演示数据创建脚本
创建完整的演示数据，包括用户、业务系统、流程、SOP、KPI和任务
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

class DemoDataCreator:
    """演示数据创建器"""
    
    def __init__(self):
        self.project_root = project_root
        self.db_path = project_root / "data" / "selfmastery.db"
        self.demo_data = {
            "users": [],
            "business_systems": [],
            "processes": [],
            "sops": [],
            "kpis": [],
            "tasks": []
        }
        
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def create_all_demo_data(self):
        """创建所有演示数据"""
        self.log("开始创建演示数据", "INFO")
        
        try:
            # 确保数据库存在
            self._ensure_database()
            
            # 创建演示用户
            self._create_demo_users()
            
            # 创建演示业务系统
            self._create_demo_business_systems()
            
            # 创建演示流程
            self._create_demo_processes()
            
            # 创建演示SOP文档
            self._create_demo_sops()
            
            # 创建演示KPI数据
            self._create_demo_kpis()
            
            # 创建演示任务
            self._create_demo_tasks()
            
            # 保存演示数据到JSON文件
            self._save_demo_data_json()
            
            # 生成数据统计报告
            self._generate_data_report()
            
            self.log("演示数据创建完成", "INFO")
            
        except Exception as e:
            self.log(f"创建演示数据时发生错误: {str(e)}", "ERROR")
            raise
    
    def _ensure_database(self):
        """确保数据库存在"""
        if not self.db_path.exists():
            self.log("数据库不存在，尝试初始化", "WARNING")
            init_script = self.project_root / "scripts" / "init_db.py"
            if init_script.exists():
                import subprocess
                subprocess.run([sys.executable, str(init_script)], check=True)
            else:
                raise Exception("数据库初始化脚本不存在")
    
    def _create_demo_users(self):
        """创建演示用户"""
        self.log("创建演示用户", "INFO")
        
        demo_users = [
            {
                "username": "admin",
                "email": "admin@selfmastery.com",
                "password_hash": "hashed_password_admin",
                "full_name": "系统管理员",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "username": "manager",
                "email": "manager@selfmastery.com",
                "password_hash": "hashed_password_manager",
                "full_name": "业务经理",
                "role": "manager",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "username": "employee1",
                "email": "employee1@selfmastery.com",
                "password_hash": "hashed_password_emp1",
                "full_name": "员工张三",
                "role": "employee",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "username": "employee2",
                "email": "employee2@selfmastery.com",
                "password_hash": "hashed_password_emp2",
                "full_name": "员工李四",
                "role": "employee",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "username": "analyst",
                "email": "analyst@selfmastery.com",
                "password_hash": "hashed_password_analyst",
                "full_name": "数据分析师",
                "role": "analyst",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
        ]
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for user in demo_users:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (username, email, password_hash, full_name, role, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user["username"], user["email"], user["password_hash"],
                    user["full_name"], user["role"], user["is_active"],
                    user["created_at"]
                ))
                self.demo_data["users"].append(user)
                self.log(f"创建用户: {user['username']}", "INFO")
            except Exception as e:
                self.log(f"创建用户失败 {user['username']}: {str(e)}", "ERROR")
        
        conn.commit()
        conn.close()
    
    def _create_demo_business_systems(self):
        """创建演示业务系统"""
        self.log("创建演示业务系统", "INFO")
        
        demo_systems = [
            {
                "name": "客户关系管理系统",
                "description": "管理客户信息、销售机会和客户服务的综合系统",
                "type": "CRM",
                "status": "active",
                "owner_id": 1,  # admin
                "created_at": datetime.now().isoformat(),
                "config": json.dumps({
                    "modules": ["客户管理", "销售管理", "服务管理"],
                    "integrations": ["邮件系统", "电话系统"],
                    "permissions": {"read": ["all"], "write": ["manager", "admin"]}
                })
            },
            {
                "name": "人力资源管理系统",
                "description": "员工信息管理、招聘、培训和绩效考核系统",
                "type": "HRM",
                "status": "active",
                "owner_id": 2,  # manager
                "created_at": datetime.now().isoformat(),
                "config": json.dumps({
                    "modules": ["员工档案", "招聘管理", "培训管理", "绩效考核"],
                    "integrations": ["考勤系统", "薪资系统"],
                    "permissions": {"read": ["manager", "admin"], "write": ["admin"]}
                })
            },
            {
                "name": "项目管理系统",
                "description": "项目计划、任务分配、进度跟踪和资源管理",
                "type": "PM",
                "status": "active",
                "owner_id": 2,  # manager
                "created_at": datetime.now().isoformat(),
                "config": json.dumps({
                    "modules": ["项目计划", "任务管理", "资源管理", "进度跟踪"],
                    "integrations": ["时间跟踪", "文档系统"],
                    "permissions": {"read": ["all"], "write": ["manager", "admin"]}
                })
            },
            {
                "name": "财务管理系统",
                "description": "财务报表、预算管理、成本控制和资金流管理",
                "type": "Finance",
                "status": "development",
                "owner_id": 1,  # admin
                "created_at": datetime.now().isoformat(),
                "config": json.dumps({
                    "modules": ["财务报表", "预算管理", "成本控制", "资金流管理"],
                    "integrations": ["银行系统", "税务系统"],
                    "permissions": {"read": ["manager", "admin"], "write": ["admin"]}
                })
            }
        ]
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for system in demo_systems:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO business_systems 
                    (name, description, type, status, owner_id, created_at, config)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    system["name"], system["description"], system["type"],
                    system["status"], system["owner_id"], system["created_at"],
                    system["config"]
                ))
                self.demo_data["business_systems"].append(system)
                self.log(f"创建业务系统: {system['name']}", "INFO")
            except Exception as e:
                self.log(f"创建业务系统失败 {system['name']}: {str(e)}", "ERROR")
        
        conn.commit()
        conn.close()
    
    def _create_demo_processes(self):
        """创建演示流程"""
        self.log("创建演示流程", "INFO")
        
        demo_processes = [
            {
                "name": "客户入驻流程",
                "description": "新客户从注册到正式入驻的完整流程",
                "system_id": 1,  # CRM系统
                "type": "business",
                "status": "active",
                "owner_id": 2,  # manager
                "created_at": datetime.now().isoformat(),
                "steps": json.dumps([
                    {"id": 1, "name": "客户注册", "type": "form", "required": True},
                    {"id": 2, "name": "资料审核", "type": "approval", "required": True},
                    {"id": 3, "name": "合同签署", "type": "document", "required": True},
                    {"id": 4, "name": "系统开通", "type": "system", "required": True},
                    {"id": 5, "name": "培训交付", "type": "training", "required": False}
                ]),
                "config": json.dumps({
                    "auto_assign": True,
                    "notification": True,
                    "deadline": 7,
                    "escalation": True
                })
            },
            {
                "name": "员工入职流程",
                "description": "新员工从录用到正式入职的标准流程",
                "system_id": 2,  # HRM系统
                "type": "hr",
                "status": "active",
                "owner_id": 1,  # admin
                "created_at": datetime.now().isoformat(),
                "steps": json.dumps([
                    {"id": 1, "name": "录用通知", "type": "notification", "required": True},
                    {"id": 2, "name": "入职资料收集", "type": "form", "required": True},
                    {"id": 3, "name": "背景调查", "type": "verification", "required": True},
                    {"id": 4, "name": "合同签署", "type": "document", "required": True},
                    {"id": 5, "name": "系统账号开通", "type": "system", "required": True},
                    {"id": 6, "name": "入职培训", "type": "training", "required": True},
                    {"id": 7, "name": "导师分配", "type": "assignment", "required": False}
                ]),
                "config": json.dumps({
                    "auto_assign": True,
                    "notification": True,
                    "deadline": 14,
                    "escalation": True
                })
            },
            {
                "name": "项目立项流程",
                "description": "新项目从提案到正式立项的审批流程",
                "system_id": 3,  # PM系统
                "type": "project",
                "status": "active",
                "owner_id": 2,  # manager
                "created_at": datetime.now().isoformat(),
                "steps": json.dumps([
                    {"id": 1, "name": "项目提案", "type": "form", "required": True},
                    {"id": 2, "name": "可行性分析", "type": "analysis", "required": True},
                    {"id": 3, "name": "预算评估", "type": "budget", "required": True},
                    {"id": 4, "name": "风险评估", "type": "risk", "required": True},
                    {"id": 5, "name": "管理层审批", "type": "approval", "required": True},
                    {"id": 6, "name": "资源分配", "type": "allocation", "required": True},
                    {"id": 7, "name": "项目启动", "type": "kickoff", "required": True}
                ]),
                "config": json.dumps({
                    "auto_assign": False,
                    "notification": True,
                    "deadline": 21,
                    "escalation": True
                })
            }
        ]
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for process in demo_processes:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO processes 
                    (name, description, system_id, type, status, owner_id, created_at, steps, config)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    process["name"], process["description"], process["system_id"],
                    process["type"], process["status"], process["owner_id"],
                    process["created_at"], process["steps"], process["config"]
                ))
                self.demo_data["processes"].append(process)
                self.log(f"创建流程: {process['name']}", "INFO")
            except Exception as e:
                self.log(f"创建流程失败 {process['name']}: {str(e)}", "ERROR")
        
        conn.commit()
        conn.close()
    
    def _create_demo_sops(self):
        """创建演示SOP文档"""
        self.log("创建演示SOP文档", "INFO")
        
        demo_sops = [
            {
                "title": "客户服务标准操作程序",
                "description": "客户服务团队处理客户咨询和投诉的标准流程",
                "process_id": 1,  # 客户入驻流程
                "category": "customer_service",
                "version": "1.0",
                "status": "published",
                "author_id": 2,  # manager
                "created_at": datetime.now().isoformat(),
                "content": json.dumps({
                    "sections": [
                        {
                            "title": "1. 客户咨询处理",
                            "content": "接到客户咨询时，应在2分钟内响应，详细了解客户需求，提供准确信息。",
                            "steps": [
                                "礼貌问候客户",
                                "仔细倾听客户需求",
                                "查询相关信息",
                                "提供解决方案",
                                "确认客户满意度"
                            ]
                        },
                        {
                            "title": "2. 投诉处理流程",
                            "content": "客户投诉需要及时处理，确保客户满意。",
                            "steps": [
                                "记录投诉详情",
                                "向客户道歉",
                                "调查问题原因",
                                "制定解决方案",
                                "跟进处理结果"
                            ]
                        }
                    ],
                    "attachments": ["客户服务话术模板.docx", "投诉处理表格.xlsx"],
                    "related_docs": ["客户管理制度", "服务质量标准"]
                }),
                "tags": json.dumps(["客户服务", "标准流程", "质量管理"])
            },
            {
                "title": "新员工培训标准操作程序",
                "description": "新员工入职培训的详细操作指南",
                "process_id": 2,  # 员工入职流程
                "category": "hr_training",
                "version": "2.1",
                "status": "published",
                "author_id": 1,  # admin
                "created_at": datetime.now().isoformat(),
                "content": json.dumps({
                    "sections": [
                        {
                            "title": "1. 入职前准备",
                            "content": "为新员工准备必要的培训材料和工作环境。",
                            "steps": [
                                "准备培训材料",
                                "安排工作座位",
                                "开通系统账号",
                                "准备欢迎礼品",
                                "通知相关同事"
                            ]
                        },
                        {
                            "title": "2. 第一天培训",
                            "content": "新员工第一天的培训安排和注意事项。",
                            "steps": [
                                "公司介绍",
                                "部门介绍",
                                "岗位职责说明",
                                "系统操作培训",
                                "安全培训"
                            ]
                        },
                        {
                            "title": "3. 第一周跟进",
                            "content": "新员工第一周的跟进和辅导。",
                            "steps": [
                                "每日工作指导",
                                "问题答疑",
                                "工作反馈",
                                "适应情况评估",
                                "调整培训计划"
                            ]
                        }
                    ],
                    "attachments": ["员工手册.pdf", "培训课件.pptx", "考核表.xlsx"],
                    "related_docs": ["员工管理制度", "培训管理办法"]
                }),
                "tags": json.dumps(["人力资源", "员工培训", "入职管理"])
            },
            {
                "title": "项目风险管理标准操作程序",
                "description": "项目执行过程中的风险识别、评估和应对措施",
                "process_id": 3,  # 项目立项流程
                "category": "project_management",
                "version": "1.5",
                "status": "published",
                "author_id": 2,  # manager
                "created_at": datetime.now().isoformat(),
                "content": json.dumps({
                    "sections": [
                        {
                            "title": "1. 风险识别",
                            "content": "系统性识别项目可能面临的各种风险。",
                            "steps": [
                                "召开风险识别会议",
                                "使用风险检查清单",
                                "分析历史项目经验",
                                "咨询专家意见",
                                "建立风险登记册"
                            ]
                        },
                        {
                            "title": "2. 风险评估",
                            "content": "对识别出的风险进行概率和影响评估。",
                            "steps": [
                                "评估风险概率",
                                "评估风险影响",
                                "计算风险值",
                                "确定风险等级",
                                "优先级排序"
                            ]
                        },
                        {
                            "title": "3. 风险应对",
                            "content": "制定和实施风险应对策略。",
                            "steps": [
                                "制定应对策略",
                                "分配责任人",
                                "实施应对措施",
                                "监控风险状态",
                                "更新风险登记册"
                            ]
                        }
                    ],
                    "attachments": ["风险登记册模板.xlsx", "风险评估矩阵.png"],
                    "related_docs": ["项目管理制度", "质量管理体系"]
                }),
                "tags": json.dumps(["项目管理", "风险管理", "质量控制"])
            }
        ]
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for sop in demo_sops:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO sops 
                    (title, description, process_id, category, version, status, author_id, created_at, content, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sop["title"], sop["description"], sop["process_id"],
                    sop["category"], sop["version"], sop["status"],
                    sop["author_id"], sop["created_at"], sop["content"], sop["tags"]
                ))
                self.demo_data["sops"].append(sop)
                self.log(f"创建SOP: {sop['title']}", "INFO")
            except Exception as e:
                self.log(f"创建SOP失败 {sop['title']}: {str(e)}", "ERROR")
        
        conn.commit()
        conn.close()
    
    def _create_demo_kpis(self):
        """创建演示KPI数据"""
        self.log("创建演示KPI数据", "INFO")
        
        # 生成过去12个月的KPI数据
        base_date = datetime.now() - timedelta(days=365)
        demo_kpis = []
        
        # 客户满意度KPI
        for i in range(12):
            month_date = base_date + timedelta(days=30*i)
            demo_kpis.append({
                "name": "客户满意度",
                "description": "客户服务满意度评分",
                "system_id": 1,  # CRM系统
                "category": "quality",
                "type": "percentage",
                "target_value": 95.0,
                "actual_value": 92.5 + (i * 0.3),  # 逐月提升
                "unit": "%",
                "period": "monthly",
                "date": month_date.isoformat(),
                "owner_id": 2,  # manager
                "created_at": month_date.isoformat(),
                "metadata": json.dumps({
                    "data_source": "客户调研",
                    "sample_size": 150 + i*10,
                    "collection_method": "在线问卷"
                })
            })
        
        # 员工培训完成率KPI
        for i in range(12):
            month_date = base_date + timedelta(days=30*i)
            demo_kpis.append({
                "name": "员工培训完成率",
                "description": "当月员工培训计划完成率",
                "system_id": 2,  # HRM系统
                "category": "hr",
                "type": "percentage",
                "target_value": 100.0,
                "actual_value": 85.0 + (i * 1.2),  # 逐月提升
                "unit": "%",
                "period": "monthly",
                "date": month_date.isoformat(),
                "owner_id": 1,  # admin
                "created_at": month_date.isoformat(),
                "metadata": json.dumps({
                    "data_source": "培训系统",
                    "total_employees": 50,
                    "training_hours": 40
                })
            })
        
        # 项目按时完成率KPI
        for i in range(12):
            month_date = base_date + timedelta(days=30*i)
            demo_kpis.append({
                "name": "项目按时完成率",
                "description": "项目按计划时间完成的比率",
                "system_id": 3,  # PM系统
                "category": "efficiency",
                "type": "percentage",
                "target_value": 90.0,
                "actual_value": 75.0 + (i * 1.5),  # 逐月提升
                "unit": "%",
                "period": "monthly",
                "date": month_date.isoformat(),
                "owner_id": 2,  # manager
                "created_at": month_date.isoformat(),
                "metadata": json.dumps({
                    "data_source": "项目管理系统",
                    "total_projects": 15 + i,
                    "completed_projects": int((15 + i) * (75.0 + i * 1.5) / 100)
                })
            })
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for kpi in demo_kpis:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO kpis 
                    (name, description, system_id, category, type, target_value, actual_value, 
                     unit, period, date, owner_id, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    kpi["name"], kpi["description"], kpi["system_id"],
                    kpi["category"], kpi["type"], kpi["target_value"],
                    kpi["actual_value"], kpi["unit"], kpi["period"],
                    kpi["date"], kpi["owner_id"], kpi["created_at"], kpi["metadata"]
                ))
                self.demo_data["kpis"].append(kpi)
            except Exception as e:
                self.log(f"创建KPI失败 {kpi['name']}: {str(e)}", "ERROR")
        
        conn.commit()
        conn.close()
        self.log(f"创建了 {len(demo_kpis)} 个KPI数据点", "INFO")
    
    def _create_demo_tasks(self):
        """创建演示任务"""
        self.log("创建演示任务", "INFO")
        
        demo_tasks = [
            {
                "title": "客户ABC公司入驻审核",
                "description": "审核ABC公司的入驻申请材料，确认资质符合要求",
                "process_id": 1,  # 客户入驻流程
                "assignee_id": 3,  # employee1
                "creator_id": 2,  # manager
                "status": "in_progress",
                "priority": "high",
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                "metadata": json.dumps({
                    "customer_name": "ABC公司",
                    "application_id": "APP-2024-001",
                    "documents": ["营业执照", "税务登记证", "银行开户许可证"]
                })
            },
            {
                "title": "新员工王五入职培训",
                "description": "为新员工王五安排入职培训，包括公司介绍和岗位培训",
                "process_id": 2,  # 员工入职流程
                "assignee_id": 1,  # admin
                "creator_id": 2,  # manager
                "status": "pending",
                "priority": "medium",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "metadata": json.dumps({
                    "employee_name": "王五",
                    "position": "软件工程师",
                    "department": "技术部",
                    "start_date": (datetime.now() + timedelta(days=5)).isoformat()
                })
            },
            {
                "title": "移动应用项目立项评估",
                "description": "评估移动应用开发项目的可行性和资源需求",
                "process_id": 3,  # 项目立项流程
                "assignee_id": 5,  # analyst
                "creator_id": 2,  # manager
                "status": "completed",
                "priority": "high",
                "due_date": (datetime.now() - timedelta(days=5)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
                "completed_at": (datetime.now() - timedelta(days=3)).isoformat(),
                "metadata": json.dumps({
                    "project_name": "移动应用开发",
                    "estimated_budget": 500000,
                    "estimated_duration": 6,
                    "team_size": 8
                })
            },
            {
                "title": "客户DEF公司合同签署",
                "description": "与DEF公司签署服务合同，确认服务条款和价格",
                "process_id": 1,  # 客户入驻流程
                "assignee_id": 2,  # manager
                "creator_id": 1,  # admin
                "status": "in_progress",
                "priority": "high",
                "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
                "metadata": json.dumps({
                    "customer_name": "DEF公司",
                    "contract_value": 120000,
                    "service_type": "年度服务",
                    "contact_person": "张经理"
                })
            },
            {
                "title": "季度KPI数据分析报告",
                "description": "分析本季度各项KPI指标完成情况，提出改进建议",
                "process_id": 3,  # 项目立项流程
                "assignee_id": 5,  # analyst
                "creator_id": 2,  # manager
                "status": "pending",
                "priority": "medium",
                "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "created_at": datetime.now().isoformat(),
                "metadata": json.dumps({
                    "report_type": "季度分析",
                    "kpi_categories": ["质量", "效率", "人力资源"],
                    "analysis_period": "Q4 2024"
                })
            }
        ]
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for task in demo_tasks:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO tasks
                    (title, description, process_id, assignee_id, creator_id, status, priority,
                     due_date, created_at, completed_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task["title"], task["description"], task["process_id"],
                    task["assignee_id"], task["creator_id"], task["status"],
                    task["priority"], task["due_date"], task["created_at"],
                    task.get("completed_at"), task["metadata"]
                ))
                self.demo_data["tasks"].append(task)
                self.log(f"创建任务: {task['title']}", "INFO")
            except Exception as e:
                self.log(f"创建任务失败 {task['title']}: {str(e)}", "ERROR")
        
        conn.commit()
        conn.close()
    
    def _save_demo_data_json(self):
        """保存演示数据到JSON文件"""
        self.log("保存演示数据到JSON文件", "INFO")
        
        demo_data_file = self.project_root / "demo_data.json"
        with open(demo_data_file, "w", encoding="utf-8") as f:
            json.dump(self.demo_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"演示数据已保存到: {demo_data_file}", "INFO")
    
    def _generate_data_report(self):
        """生成数据统计报告"""
        self.log("生成数据统计报告", "INFO")
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 统计各表的记录数
        tables = ["users", "business_systems", "processes", "sops", "kpis", "tasks"]
        stats = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except Exception as e:
                stats[table] = f"错误: {str(e)}"
        
        conn.close()
        
        # 生成报告
        report = {
            "generation_time": datetime.now().isoformat(),
            "project": "SelfMastery B2B业务系统 - 演示数据",
            "statistics": stats,
            "summary": {
                "total_records": sum(v for v in stats.values() if isinstance(v, int)),
                "tables_created": len([v for v in stats.values() if isinstance(v, int) and v > 0])
            },
            "data_overview": {
                "users": "5个演示用户（管理员、经理、员工、分析师）",
                "business_systems": "4个业务系统（CRM、HRM、PM、Finance）",
                "processes": "3个核心流程（客户入驻、员工入职、项目立项）",
                "sops": "3个标准操作程序文档",
                "kpis": "36个KPI数据点（12个月 × 3个指标）",
                "tasks": "5个演示任务（不同状态和优先级）"
            }
        }
        
        # 保存报告
        report_file = self.project_root / "demo_data_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印报告摘要
        print("\n" + "="*60)
        print("SelfMastery B2B业务系统 - 演示数据创建报告")
        print("="*60)
        print(f"生成时间: {report['generation_time']}")
        print(f"总记录数: {report['summary']['total_records']}")
        print(f"成功创建表: {report['summary']['tables_created']}/{len(tables)}")
        print("="*60)
        
        for table, count in stats.items():
            print(f"{table}: {count}")
        
        print("="*60)
        print("数据概览:")
        for key, desc in report["data_overview"].items():
            print(f"  {key}: {desc}")
        
        print("="*60)
        self.log(f"数据统计报告已保存到: {report_file}", "INFO")


def main():
    """主函数"""
    print("SelfMastery B2B业务系统 - 演示数据创建工具")
    print("="*50)
    
    creator = DemoDataCreator()
    creator.create_all_demo_data()
    
    print("\n演示数据创建完成！")
    print("您可以使用以下数据进行测试：")
    print("- 管理员账号: admin / hashed_password_admin")
    print("- 经理账号: manager / hashed_password_manager")
    print("- 员工账号: employee1 / hashed_password_emp1")
    print("- 分析师账号: analyst / hashed_password_analyst")


if __name__ == "__main__":
    main()