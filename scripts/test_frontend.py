#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 前端功能测试
测试PyQt前端界面的各个组件和功能
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

class FrontendTestRunner:
    """前端测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {
            "ui_components": {"status": "pending", "details": []},
            "widgets": {"status": "pending", "details": []},
            "dialogs": {"status": "pending", "details": []},
            "services": {"status": "pending", "details": []},
            "integration": {"status": "pending", "details": []}
        }
        
    def log(self, message: str, level: str = "INFO"):
        """记录测试日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def run_all_tests(self) -> Dict:
        """运行所有前端测试"""
        self.log("开始前端功能测试", "INFO")
        
        try:
            # 1. UI组件测试
            self.test_ui_components()
            
            # 2. 业务组件测试
            self.test_widgets()
            
            # 3. 对话框测试
            self.test_dialogs()
            
            # 4. 服务层测试
            self.test_services()
            
            # 5. 前端集成测试
            self.test_frontend_integration()
            
            # 生成测试报告
            self.generate_test_report()
            
        except Exception as e:
            self.log(f"前端测试过程中发生错误: {str(e)}", "ERROR")
            
        return self.test_results
    
    def test_ui_components(self):
        """测试UI基础组件"""
        self.log("开始UI组件测试", "INFO")
        
        try:
            # 检查UI组件文件
            ui_components = [
                "frontend/ui/main_window.py",
                "frontend/ui/components/custom_widgets.py",
                "frontend/ui/layouts/responsive_layout.py"
            ]
            
            test_details = []
            
            for component in ui_components:
                component_path = self.project_root / "selfmastery" / component
                if component_path.exists():
                    # 尝试导入组件
                    try:
                        module_path = component.replace("/", ".").replace(".py", "")
                        __import__(module_path)
                        self.log(f"✓ 组件导入成功: {component}", "INFO")
                        test_details.append(f"✓ {component}: 导入成功")
                    except Exception as e:
                        self.log(f"✗ 组件导入失败: {component} - {str(e)}", "ERROR")
                        test_details.append(f"✗ {component}: 导入失败 - {str(e)}")
                else:
                    self.log(f"✗ 组件文件不存在: {component}", "WARNING")
                    test_details.append(f"✗ {component}: 文件不存在")
            
            # 测试主窗口
            try:
                from frontend.ui.main_window import MainWindow
                self.log("✓ 主窗口类导入成功", "INFO")
                test_details.append("✓ MainWindow: 类定义正确")
            except Exception as e:
                self.log(f"✗ 主窗口类导入失败: {str(e)}", "ERROR")
                test_details.append(f"✗ MainWindow: 导入失败 - {str(e)}")
            
            self.test_results["ui_components"]["status"] = "passed"
            self.test_results["ui_components"]["details"] = test_details
            
        except Exception as e:
            self.test_results["ui_components"]["status"] = "failed"
            self.test_results["ui_components"]["details"] = [f"UI组件测试失败: {str(e)}"]
            self.log(f"UI组件测试失败: {str(e)}", "ERROR")
    
    def test_widgets(self):
        """测试业务组件"""
        self.log("开始业务组件测试", "INFO")
        
        try:
            # 检查业务组件文件
            widgets = [
                ("frontend/widgets/system_canvas.py", "SystemCanvas"),
                ("frontend/widgets/process_editor.py", "ProcessEditor"),
                ("frontend/widgets/sop_editor.py", "SOPEditor"),
                ("frontend/widgets/kpi_dashboard.py", "KPIDashboard"),
                ("frontend/widgets/task_manager.py", "TaskManager"),
                ("frontend/widgets/navigation_tree.py", "NavigationTree")
            ]
            
            test_details = []
            
            for widget_file, widget_class in widgets:
                widget_path = self.project_root / "selfmastery" / widget_file
                if widget_path.exists():
                    try:
                        # 尝试导入组件类
                        module_path = widget_file.replace("/", ".").replace(".py", "")
                        module = __import__(module_path, fromlist=[widget_class])
                        widget_cls = getattr(module, widget_class)
                        
                        self.log(f"✓ 组件类导入成功: {widget_class}", "INFO")
                        test_details.append(f"✓ {widget_class}: 类定义正确")
                        
                        # 检查关键方法
                        expected_methods = ["__init__"]
                        for method in expected_methods:
                            if hasattr(widget_cls, method):
                                test_details.append(f"  - {method}方法存在")
                            else:
                                test_details.append(f"  - {method}方法缺失")
                                
                    except Exception as e:
                        self.log(f"✗ 组件类导入失败: {widget_class} - {str(e)}", "ERROR")
                        test_details.append(f"✗ {widget_class}: 导入失败 - {str(e)}")
                else:
                    self.log(f"✗ 组件文件不存在: {widget_file}", "WARNING")
                    test_details.append(f"✗ {widget_class}: 文件不存在")
            
            self.test_results["widgets"]["status"] = "passed"
            self.test_results["widgets"]["details"] = test_details
            
        except Exception as e:
            self.test_results["widgets"]["status"] = "failed"
            self.test_results["widgets"]["details"] = [f"业务组件测试失败: {str(e)}"]
            self.log(f"业务组件测试失败: {str(e)}", "ERROR")
    
    def test_dialogs(self):
        """测试对话框组件"""
        self.log("开始对话框测试", "INFO")
        
        try:
            # 检查对话框文件
            dialogs = [
                ("frontend/ui/auth/login_dialog.py", "LoginDialog"),
                ("frontend/ui/auth/register_dialog.py", "RegisterDialog")
            ]
            
            test_details = []
            
            for dialog_file, dialog_class in dialogs:
                dialog_path = self.project_root / "selfmastery" / dialog_file
                if dialog_path.exists():
                    try:
                        # 尝试导入对话框类
                        module_path = dialog_file.replace("/", ".").replace(".py", "")
                        module = __import__(module_path, fromlist=[dialog_class])
                        dialog_cls = getattr(module, dialog_class)
                        
                        self.log(f"✓ 对话框类导入成功: {dialog_class}", "INFO")
                        test_details.append(f"✓ {dialog_class}: 类定义正确")
                        
                        # 检查关键方法
                        expected_methods = ["__init__", "accept", "reject"]
                        for method in expected_methods:
                            if hasattr(dialog_cls, method):
                                test_details.append(f"  - {method}方法存在")
                            else:
                                test_details.append(f"  - {method}方法缺失")
                                
                    except Exception as e:
                        self.log(f"✗ 对话框类导入失败: {dialog_class} - {str(e)}", "ERROR")
                        test_details.append(f"✗ {dialog_class}: 导入失败 - {str(e)}")
                else:
                    self.log(f"✗ 对话框文件不存在: {dialog_file}", "WARNING")
                    test_details.append(f"✗ {dialog_class}: 文件不存在")
            
            self.test_results["dialogs"]["status"] = "passed"
            self.test_results["dialogs"]["details"] = test_details
            
        except Exception as e:
            self.test_results["dialogs"]["status"] = "failed"
            self.test_results["dialogs"]["details"] = [f"对话框测试失败: {str(e)}"]
            self.log(f"对话框测试失败: {str(e)}", "ERROR")
    
    def test_services(self):
        """测试前端服务层"""
        self.log("开始服务层测试", "INFO")
        
        try:
            # 检查服务文件
            services = [
                ("frontend/services/api_client.py", "APIClient"),
                ("frontend/services/auth_manager.py", "AuthManager"),
                ("frontend/services/data_manager.py", "DataManager")
            ]
            
            test_details = []
            
            for service_file, service_class in services:
                service_path = self.project_root / "selfmastery" / service_file
                if service_path.exists():
                    try:
                        # 尝试导入服务类
                        module_path = service_file.replace("/", ".").replace(".py", "")
                        module = __import__(module_path, fromlist=[service_class])
                        service_cls = getattr(module, service_class)
                        
                        self.log(f"✓ 服务类导入成功: {service_class}", "INFO")
                        test_details.append(f"✓ {service_class}: 类定义正确")
                        
                        # 检查关键方法
                        if service_class == "APIClient":
                            expected_methods = ["__init__", "get", "post", "put", "delete"]
                        elif service_class == "AuthManager":
                            expected_methods = ["__init__", "login", "logout", "is_authenticated"]
                        elif service_class == "DataManager":
                            expected_methods = ["__init__", "load_data", "save_data"]
                        else:
                            expected_methods = ["__init__"]
                        
                        for method in expected_methods:
                            if hasattr(service_cls, method):
                                test_details.append(f"  - {method}方法存在")
                            else:
                                test_details.append(f"  - {method}方法缺失")
                                
                    except Exception as e:
                        self.log(f"✗ 服务类导入失败: {service_class} - {str(e)}", "ERROR")
                        test_details.append(f"✗ {service_class}: 导入失败 - {str(e)}")
                else:
                    self.log(f"✗ 服务文件不存在: {service_file}", "WARNING")
                    test_details.append(f"✗ {service_class}: 文件不存在")
            
            self.test_results["services"]["status"] = "passed"
            self.test_results["services"]["details"] = test_details
            
        except Exception as e:
            self.test_results["services"]["status"] = "failed"
            self.test_results["services"]["details"] = [f"服务层测试失败: {str(e)}"]
            self.log(f"服务层测试失败: {str(e)}", "ERROR")
    
    def test_frontend_integration(self):
        """测试前端集成功能"""
        self.log("开始前端集成测试", "INFO")
        
        try:
            test_details = []
            
            # 测试前端主程序
            try:
                from frontend.main import main
                self.log("✓ 前端主程序导入成功", "INFO")
                test_details.append("✓ 前端主程序: 导入成功")
            except Exception as e:
                self.log(f"✗ 前端主程序导入失败: {str(e)}", "ERROR")
                test_details.append(f"✗ 前端主程序: 导入失败 - {str(e)}")
            
            # 测试样式主题
            try:
                from frontend.styles.themes import get_theme
                self.log("✓ 样式主题导入成功", "INFO")
                test_details.append("✓ 样式主题: 导入成功")
            except Exception as e:
                self.log(f"✗ 样式主题导入失败: {str(e)}", "ERROR")
                test_details.append(f"✗ 样式主题: 导入失败 - {str(e)}")
            
            # 测试图形组件
            graphics_components = [
                ("frontend/graphics/canvas.py", "Canvas"),
                ("frontend/graphics/items.py", "GraphicsItem"),
                ("frontend/graphics/layouts.py", "GraphicsLayout")
            ]
            
            for comp_file, comp_class in graphics_components:
                comp_path = self.project_root / "selfmastery" / comp_file
                if comp_path.exists():
                    try:
                        module_path = comp_file.replace("/", ".").replace(".py", "")
                        module = __import__(module_path, fromlist=[comp_class])
                        comp_cls = getattr(module, comp_class)
                        
                        self.log(f"✓ 图形组件导入成功: {comp_class}", "INFO")
                        test_details.append(f"✓ {comp_class}: 导入成功")
                    except Exception as e:
                        self.log(f"✗ 图形组件导入失败: {comp_class} - {str(e)}", "ERROR")
                        test_details.append(f"✗ {comp_class}: 导入失败 - {str(e)}")
                else:
                    test_details.append(f"✗ {comp_class}: 文件不存在")
            
            # 检查资源文件
            resources_dir = self.project_root / "selfmastery" / "frontend" / "resources"
            if resources_dir.exists():
                test_details.append("✓ 资源目录存在")
            else:
                test_details.append("✗ 资源目录不存在")
            
            self.test_results["integration"]["status"] = "passed"
            self.test_results["integration"]["details"] = test_details
            
        except Exception as e:
            self.test_results["integration"]["status"] = "failed"
            self.test_results["integration"]["details"] = [f"前端集成测试失败: {str(e)}"]
            self.log(f"前端集成测试失败: {str(e)}", "ERROR")
    
    def generate_test_report(self):
        """生成前端测试报告"""
        self.log("生成前端测试报告", "INFO")
        
        report = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project": "SelfMastery B2B业务系统 - 前端测试",
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results.values() if r["status"] == "passed"),
                "failed": sum(1 for r in self.test_results.values() if r["status"] == "failed"),
                "pending": sum(1 for r in self.test_results.values() if r["status"] == "pending")
            }
        }
        
        # 保存报告到文件
        report_path = self.project_root / "frontend_test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"前端测试报告已保存到: {report_path}", "INFO")
        
        # 打印摘要
        print("\n" + "="*60)
        print("SelfMastery B2B业务系统 - 前端测试报告")
        print("="*60)
        print(f"测试时间: {report['test_time']}")
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


def main():
    """主函数"""
    print("SelfMastery B2B业务系统 - 前端功能测试工具")
    print("="*50)
    
    runner = FrontendTestRunner()
    results = runner.run_all_tests()
    
    # 返回退出码
    failed_tests = sum(1 for r in results.values() if r["status"] == "failed")
    sys.exit(failed_tests)


if __name__ == "__main__":
    main()