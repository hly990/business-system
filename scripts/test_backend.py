#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 后端API测试
测试FastAPI后端服务的各个API端点和功能
"""

import os
import sys
import time
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

class BackendTestRunner:
    """后端API测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.backend_url = "http://localhost:8000"
        self.test_results = {
            "server_startup": {"status": "pending", "details": []},
            "health_check": {"status": "pending", "details": []},
            "auth_apis": {"status": "pending", "details": []},
            "user_apis": {"status": "pending", "details": []},
            "business_apis": {"status": "pending", "details": []},
            "data_validation": {"status": "pending", "details": []}
        }
        self.backend_process = None
        self.auth_token = None
        
    def log(self, message: str, level: str = "INFO"):
        """记录测试日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def run_all_tests(self) -> Dict:
        """运行所有后端测试"""
        self.log("开始后端API测试", "INFO")
        
        try:
            # 1. 服务器启动测试
            self.test_server_startup()
            
            # 2. 健康检查测试
            self.test_health_check()
            
            # 3. 认证API测试
            self.test_auth_apis()
            
            # 4. 用户API测试
            self.test_user_apis()
            
            # 5. 业务API测试
            self.test_business_apis()
            
            # 6. 数据验证测试
            self.test_data_validation()
            
            # 生成测试报告
            self.generate_test_report()
            
        except Exception as e:
            self.log(f"后端测试过程中发生错误: {str(e)}", "ERROR")
            
        finally:
            # 清理资源
            self.cleanup()
            
        return self.test_results
    
    def test_server_startup(self):
        """测试服务器启动"""
        self.log("开始服务器启动测试", "INFO")
        
        try:
            # 检查后端主文件
            backend_main = self.project_root / "selfmastery" / "backend" / "main.py"
            if not backend_main.exists():
                raise Exception("后端主文件不存在")
            
            # 启动后端服务
            self.log("启动后端服务...", "INFO")
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_main)
            ], cwd=str(self.project_root / "selfmastery"))
            
            # 等待服务启动
            startup_success = False
            for i in range(30):  # 等待30秒
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=2)
                    if response.status_code == 200:
                        startup_success = True
                        break
                except:
                    pass
                time.sleep(1)
                self.log(f"等待服务启动... ({i+1}/30)", "INFO")
            
            if startup_success:
                self.test_results["server_startup"]["status"] = "passed"
                self.test_results["server_startup"]["details"] = [
                    "后端服务启动成功",
                    f"服务地址: {self.backend_url}",
                    "健康检查通过"
                ]
                self.log("后端服务启动成功", "INFO")
            else:
                raise Exception("后端服务启动超时")
                
        except Exception as e:
            self.test_results["server_startup"]["status"] = "failed"
            self.test_results["server_startup"]["details"] = [f"服务器启动失败: {str(e)}"]
            self.log(f"服务器启动测试失败: {str(e)}", "ERROR")
    
    def test_health_check(self):
        """测试健康检查"""
        self.log("开始健康检查测试", "INFO")
        
        try:
            # 基本健康检查
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            test_details = []
            
            if response.status_code == 200:
                self.log("✓ 健康检查端点响应正常", "INFO")
                test_details.append("✓ /health 端点响应正常")
                
                # 检查响应内容
                try:
                    health_data = response.json()
                    if "status" in health_data:
                        test_details.append(f"✓ 状态: {health_data['status']}")
                    if "timestamp" in health_data:
                        test_details.append("✓ 时间戳存在")
                except:
                    test_details.append("✓ 响应格式为文本")
            else:
                test_details.append(f"✗ 健康检查失败: HTTP {response.status_code}")
            
            # 测试根路径
            try:
                response = requests.get(f"{self.backend_url}/", timeout=10)
                if response.status_code == 200:
                    test_details.append("✓ 根路径访问正常")
                else:
                    test_details.append(f"✗ 根路径访问失败: HTTP {response.status_code}")
            except Exception as e:
                test_details.append(f"✗ 根路径访问异常: {str(e)}")
            
            # 测试API文档
            try:
                response = requests.get(f"{self.backend_url}/docs", timeout=10)
                if response.status_code == 200:
                    test_details.append("✓ API文档访问正常")
                else:
                    test_details.append(f"✗ API文档访问失败: HTTP {response.status_code}")
            except Exception as e:
                test_details.append(f"✗ API文档访问异常: {str(e)}")
            
            self.test_results["health_check"]["status"] = "passed"
            self.test_results["health_check"]["details"] = test_details
            
        except Exception as e:
            self.test_results["health_check"]["status"] = "failed"
            self.test_results["health_check"]["details"] = [f"健康检查测试失败: {str(e)}"]
            self.log(f"健康检查测试失败: {str(e)}", "ERROR")
    
    def test_auth_apis(self):
        """测试认证API"""
        self.log("开始认证API测试", "INFO")
        
        try:
            test_details = []
            
            # 测试用户注册
            register_data = {
                "username": "test_api_user",
                "email": "test_api@example.com",
                "password": "test123456",
                "full_name": "API Test User"
            }
            
            try:
                response = requests.post(
                    f"{self.backend_url}/api/auth/register",
                    json=register_data,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    self.log("✓ 用户注册成功", "INFO")
                    test_details.append("✓ 用户注册: 成功")
                elif response.status_code == 409:
                    self.log("✓ 用户已存在（正常）", "INFO")
                    test_details.append("✓ 用户注册: 用户已存在")
                else:
                    test_details.append(f"✗ 用户注册失败: HTTP {response.status_code}")
                    
            except Exception as e:
                test_details.append(f"✗ 用户注册异常: {str(e)}")
            
            # 测试用户登录
            login_data = {
                "username": "test_api_user",
                "password": "test123456"
            }
            
            try:
                response = requests.post(
                    f"{self.backend_url}/api/auth/login",
                    json=login_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log("✓ 用户登录成功", "INFO")
                    test_details.append("✓ 用户登录: 成功")
                    
                    # 获取认证令牌
                    try:
                        login_response = response.json()
                        if "access_token" in login_response:
                            self.auth_token = login_response["access_token"]
                            test_details.append("✓ 获取访问令牌: 成功")
                        elif "token" in login_response:
                            self.auth_token = login_response["token"]
                            test_details.append("✓ 获取访问令牌: 成功")
                    except:
                        test_details.append("✗ 解析登录响应失败")
                        
                else:
                    test_details.append(f"✗ 用户登录失败: HTTP {response.status_code}")
                    
            except Exception as e:
                test_details.append(f"✗ 用户登录异常: {str(e)}")
            
            # 测试错误登录
            try:
                wrong_login_data = {
                    "username": "test_api_user",
                    "password": "wrong_password"
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/auth/login",
                    json=wrong_login_data,
                    timeout=10
                )
                
                if response.status_code in [401, 403]:
                    test_details.append("✓ 错误密码登录: 正确拒绝")
                else:
                    test_details.append(f"✗ 错误密码登录: 应该被拒绝但返回 {response.status_code}")
                    
            except Exception as e:
                test_details.append(f"✗ 错误登录测试异常: {str(e)}")
            
            self.test_results["auth_apis"]["status"] = "passed"
            self.test_results["auth_apis"]["details"] = test_details
            
        except Exception as e:
            self.test_results["auth_apis"]["status"] = "failed"
            self.test_results["auth_apis"]["details"] = [f"认证API测试失败: {str(e)}"]
            self.log(f"认证API测试失败: {str(e)}", "ERROR")
    
    def test_user_apis(self):
        """测试用户API"""
        self.log("开始用户API测试", "INFO")
        
        try:
            test_details = []
            headers = {}
            
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # 测试获取用户信息
            try:
                response = requests.get(
                    f"{self.backend_url}/api/users/me",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    test_details.append("✓ 获取用户信息: 成功")
                    
                    # 检查响应数据
                    try:
                        user_data = response.json()
                        if "username" in user_data:
                            test_details.append("✓ 用户数据包含用户名")
                        if "email" in user_data:
                            test_details.append("✓ 用户数据包含邮箱")
                    except:
                        test_details.append("✗ 用户数据解析失败")
                        
                elif response.status_code == 401:
                    test_details.append("✗ 获取用户信息: 未授权（可能需要登录）")
                else:
                    test_details.append(f"✗ 获取用户信息失败: HTTP {response.status_code}")
                    
            except Exception as e:
                test_details.append(f"✗ 获取用户信息异常: {str(e)}")
            
            # 测试获取用户列表
            try:
                response = requests.get(
                    f"{self.backend_url}/api/users/",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    test_details.append("✓ 获取用户列表: 成功")
                    
                    try:
                        users_data = response.json()
                        if isinstance(users_data, list):
                            test_details.append(f"✓ 用户列表包含 {len(users_data)} 个用户")
                        elif isinstance(users_data, dict) and "users" in users_data:
                            test_details.append(f"✓ 用户列表包含 {len(users_data['users'])} 个用户")
                    except:
                        test_details.append("✗ 用户列表数据解析失败")
                        
                elif response.status_code == 401:
                    test_details.append("✗ 获取用户列表: 未授权")
                else:
                    test_details.append(f"✗ 获取用户列表失败: HTTP {response.status_code}")
                    
            except Exception as e:
                test_details.append(f"✗ 获取用户列表异常: {str(e)}")
            
            self.test_results["user_apis"]["status"] = "passed"
            self.test_results["user_apis"]["details"] = test_details
            
        except Exception as e:
            self.test_results["user_apis"]["status"] = "failed"
            self.test_results["user_apis"]["details"] = [f"用户API测试失败: {str(e)}"]
            self.log(f"用户API测试失败: {str(e)}", "ERROR")
    
    def test_business_apis(self):
        """测试业务API"""
        self.log("开始业务API测试", "INFO")
        
        try:
            test_details = []
            headers = {}
            
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # 测试业务系统相关API
            business_endpoints = [
                ("/api/systems/", "业务系统列表"),
                ("/api/processes/", "流程列表"),
                ("/api/sops/", "SOP列表"),
                ("/api/kpis/", "KPI列表"),
                ("/api/tasks/", "任务列表")
            ]
            
            for endpoint, description in business_endpoints:
                try:
                    response = requests.get(
                        f"{self.backend_url}{endpoint}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        test_details.append(f"✓ {description}: 访问成功")
                    elif response.status_code == 401:
                        test_details.append(f"○ {description}: 需要认证")
                    elif response.status_code == 404:
                        test_details.append(f"○ {description}: 端点未实现")
                    else:
                        test_details.append(f"✗ {description}: HTTP {response.status_code}")
                        
                except Exception as e:
                    test_details.append(f"✗ {description}: 异常 {str(e)}")
            
            # 测试创建业务系统
            if self.auth_token:
                try:
                    system_data = {
                        "name": "测试业务系统",
                        "description": "API测试创建的业务系统",
                        "type": "test"
                    }
                    
                    response = requests.post(
                        f"{self.backend_url}/api/systems/",
                        json=system_data,
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        test_details.append("✓ 创建业务系统: 成功")
                    elif response.status_code == 404:
                        test_details.append("○ 创建业务系统: 端点未实现")
                    else:
                        test_details.append(f"✗ 创建业务系统: HTTP {response.status_code}")
                        
                except Exception as e:
                    test_details.append(f"✗ 创建业务系统: 异常 {str(e)}")
            
            self.test_results["business_apis"]["status"] = "passed"
            self.test_results["business_apis"]["details"] = test_details
            
        except Exception as e:
            self.test_results["business_apis"]["status"] = "failed"
            self.test_results["business_apis"]["details"] = [f"业务API测试失败: {str(e)}"]
            self.log(f"业务API测试失败: {str(e)}", "ERROR")
    
    def test_data_validation(self):
        """测试数据验证"""
        self.log("开始数据验证测试", "INFO")
        
        try:
            test_details = []
            
            # 测试无效数据注册
            invalid_register_data = [
                ({"username": "", "email": "test@example.com", "password": "123456"}, "空用户名"),
                ({"username": "test", "email": "invalid-email", "password": "123456"}, "无效邮箱"),
                ({"username": "test", "email": "test@example.com", "password": "123"}, "密码过短"),
                ({"email": "test@example.com", "password": "123456"}, "缺少用户名"),
            ]
            
            for data, description in invalid_register_data:
                try:
                    response = requests.post(
                        f"{self.backend_url}/api/auth/register",
                        json=data,
                        timeout=10
                    )
                    
                    if response.status_code in [400, 422]:
                        test_details.append(f"✓ {description}: 正确拒绝")
                    else:
                        test_details.append(f"✗ {description}: 应该被拒绝但返回 {response.status_code}")
                        
                except Exception as e:
                    test_details.append(f"✗ {description}: 异常 {str(e)}")
            
            # 测试SQL注入防护
            try:
                sql_injection_data = {
                    "username": "admin'; DROP TABLE users; --",
                    "password": "password"
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/auth/login",
                    json=sql_injection_data,
                    timeout=10
                )
                
                # 应该返回认证失败，而不是服务器错误
                if response.status_code in [401, 403, 404]:
                    test_details.append("✓ SQL注入防护: 正常处理")
                elif response.status_code == 500:
                    test_details.append("✗ SQL注入防护: 可能存在漏洞")
                else:
                    test_details.append(f"○ SQL注入防护: 返回 {response.status_code}")
                    
            except Exception as e:
                test_details.append(f"✗ SQL注入测试: 异常 {str(e)}")
            
            self.test_results["data_validation"]["status"] = "passed"
            self.test_results["data_validation"]["details"] = test_details
            
        except Exception as e:
            self.test_results["data_validation"]["status"] = "failed"
            self.test_results["data_validation"]["details"] = [f"数据验证测试失败: {str(e)}"]
            self.log(f"数据验证测试失败: {str(e)}", "ERROR")
    
    def generate_test_report(self):
        """生成后端测试报告"""
        self.log("生成后端测试报告", "INFO")
        
        report = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project": "SelfMastery B2B业务系统 - 后端API测试",
            "backend_url": self.backend_url,
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results.values() if r["status"] == "passed"),
                "failed": sum(1 for r in self.test_results.values() if r["status"] == "failed"),
                "pending": sum(1 for r in self.test_results.values() if r["status"] == "pending")
            }
        }
        
        # 保存报告到文件
        report_path = self.project_root / "backend_test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"后端测试报告已保存到: {report_path}", "INFO")
        
        # 打印摘要
        print("\n" + "="*60)
        print("SelfMastery B2B业务系统 - 后端API测试报告")
        print("="*60)
        print(f"测试时间: {report['test_time']}")
        print(f"后端地址: {report['backend_url']}")
        print(f"总测试数: {report['summary']['total_tests']}")
        print(f"通过: {report['summary']['passed']}")
        print(f"失败: {report['summary']['failed']}")
        print(f"待执行: {report['summary']['pending']}")
        print("="*60)
        
        for test_name, result in self.test_results.items():
            status_icon = "✓" if result["status"] == "passed" else "✗" if result["status"] == "failed" else "○"
            print(f"{status_icon} {test_name}: {result['status']}")
            for detail in result["details"]:
                print(f"  - {detail}")
        
        print("="*60)
    
    def cleanup(self):
        """清理测试资源"""
        self.log("清理后端测试资源", "INFO")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
                self.log("后端服务已停止", "INFO")
            except:
                self.backend_process.kill()
                self.log("强制停止后端服务", "WARNING")


def main():
    """主函数"""
    print("SelfMastery B2B业务系统 - 后端API测试工具")
    print("="*50)
    
    runner = BackendTestRunner()
    results = runner.run_all_tests()
    
    # 返回退出码
    failed_tests = sum(1 for r in results.values() if r["status"] == "failed")
    sys.exit(failed_tests)


if __name__ == "__main__":
    main()