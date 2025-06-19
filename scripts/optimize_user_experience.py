#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 用户体验优化脚本
优化界面响应、错误提示、功能操作、数据展示
"""

import sys
import os
import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
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

class UserExperienceOptimizer:
    """用户体验优化器"""
    
    def __init__(self):
        self.db_path = PROJECT_ROOT / "data" / "selfmastery.db"
        self.optimization_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "optimizations": {}
        }
        
    def print_header(self):
        """打印优化头部"""
        header = """
╔══════════════════════════════════════════════════════════════╗
║                    SelfMastery B2B业务系统                    ║
║                      用户体验优化工具                        ║
╠══════════════════════════════════════════════════════════════╣
║  🎨 界面响应优化                                             ║
║  💬 错误提示优化                                             ║
║  🖱️ 功能操作优化                                             ║
║  📊 数据展示优化                                             ║
║  ⚡ 性能调优                                                 ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(header)
        
    def optimize_interface_responsiveness(self) -> Dict[str, Any]:
        """优化界面响应性"""
        print("\n🎨 优化界面响应性...")
        
        result = {
            "status": "success",
            "optimizations": [],
            "issues": []
        }
        
        try:
            # 1. 优化数据库查询
            print("   📊 优化数据库查询...")
            if self.db_path.exists():
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 创建索引以提升查询性能
                indexes = [
                    ("idx_systems_name", "CREATE INDEX IF NOT EXISTS idx_systems_name ON systems(name)"),
                    ("idx_processes_system_id", "CREATE INDEX IF NOT EXISTS idx_processes_system_id ON processes(system_id)"),
                    ("idx_sops_title", "CREATE INDEX IF NOT EXISTS idx_sops_title ON sops(title)"),
                    ("idx_kpis_name", "CREATE INDEX IF NOT EXISTS idx_kpis_name ON kpis(name)"),
                    ("idx_tasks_status", "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)"),
                    ("idx_tasks_assignee", "CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee)")
                ]
                
                for index_name, sql in indexes:
                    try:
                        cursor.execute(sql)
                        result["optimizations"].append(f"创建索引: {index_name}")
                        print(f"      ✅ 创建索引: {index_name}")
                    except sqlite3.Error as e:
                        result["issues"].append(f"索引创建失败: {index_name} - {e}")
                        print(f"      ⚠️ 索引创建失败: {index_name}")
                
                conn.commit()
                conn.close()
                
            # 2. 优化UI组件配置
            print("   🎨 优化UI组件配置...")
            ui_config = {
                "table_row_height": 30,
                "icon_size": 24,
                "font_size": 12,
                "animation_duration": 200,
                "lazy_loading": True,
                "cache_size": 1000
            }
            
            config_file = PROJECT_ROOT / "ui_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(ui_config, f, indent=2, ensure_ascii=False)
            
            result["optimizations"].append("UI配置文件已优化")
            print("      ✅ UI配置文件已优化")
            
            # 3. 优化样式表
            print("   🎭 优化样式表...")
            optimized_styles = """
            /* 优化的样式表 */
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            QTableWidget {
                gridline-color: #e9ecef;
                background-color: white;
                selection-background-color: #e3f2fd;
                alternate-background-color: #f8f9fa;
            }
            
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            
            QTableWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
            
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #1976d2;
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background-color: #0d47a1;
                transform: translateY(0px);
            }
            
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
            
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #2196f3;
                outline: none;
            }
            
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #f5f5f5;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #2196f3;
                color: white;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e3f2fd;
            }
            
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                background-color: #f5f5f5;
            }
            
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 2px;
            }
            
            QStatusBar {
                background-color: #f5f5f5;
                border-top: 1px solid #e0e0e0;
            }
            
            QToolTip {
                background-color: #263238;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            """
            
            styles_file = PROJECT_ROOT / "optimized_styles.qss"
            with open(styles_file, 'w', encoding='utf-8') as f:
                f.write(optimized_styles)
            
            result["optimizations"].append("样式表已优化")
            print("      ✅ 样式表已优化")
            
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"界面响应优化失败: {e}")
            print(f"   ❌ 界面响应优化失败: {e}")
            
        return result
        
    def optimize_error_messages(self) -> Dict[str, Any]:
        """优化错误提示"""
        print("\n💬 优化错误提示...")
        
        result = {
            "status": "success",
            "optimizations": [],
            "issues": []
        }
        
        try:
            # 创建友好的错误消息映射
            error_messages = {
                "connection_error": {
                    "title": "连接错误",
                    "message": "无法连接到服务器，请检查网络连接或稍后重试。",
                    "suggestions": [
                        "检查网络连接是否正常",
                        "确认服务器是否正在运行",
                        "尝试重新启动应用程序"
                    ]
                },
                "database_error": {
                    "title": "数据库错误",
                    "message": "数据库操作失败，请稍后重试。",
                    "suggestions": [
                        "检查数据库文件是否存在",
                        "确认数据库文件权限",
                        "尝试重新初始化数据库"
                    ]
                },
                "validation_error": {
                    "title": "输入验证错误",
                    "message": "输入的数据格式不正确，请检查后重新输入。",
                    "suggestions": [
                        "检查必填字段是否已填写",
                        "确认数据格式是否正确",
                        "参考输入示例进行填写"
                    ]
                },
                "permission_error": {
                    "title": "权限错误",
                    "message": "您没有执行此操作的权限。",
                    "suggestions": [
                        "联系管理员获取权限",
                        "确认您的用户角色",
                        "尝试重新登录"
                    ]
                },
                "file_error": {
                    "title": "文件操作错误",
                    "message": "文件操作失败，请检查文件状态。",
                    "suggestions": [
                        "检查文件是否存在",
                        "确认文件权限",
                        "检查磁盘空间是否充足"
                    ]
                }
            }
            
            # 保存错误消息配置
            error_config_file = PROJECT_ROOT / "error_messages.json"
            with open(error_config_file, 'w', encoding='utf-8') as f:
                json.dump(error_messages, f, indent=2, ensure_ascii=False)
            
            result["optimizations"].append("错误消息配置已创建")
            print("      ✅ 错误消息配置已创建")
            
            # 创建错误处理工具类
            error_handler_code = '''
"""
用户友好的错误处理工具
"""
import json
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox, QWidget
from typing import Optional, Dict, Any

class FriendlyErrorHandler:
    """友好的错误处理器"""
    
    def __init__(self):
        self.error_config = self._load_error_config()
        
    def _load_error_config(self) -> Dict[str, Any]:
        """加载错误配置"""
        try:
            config_file = Path(__file__).parent.parent / "error_messages.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
        
    def show_error(self, parent: Optional[QWidget], error_type: str, 
                   details: str = "", custom_message: str = ""):
        """显示友好的错误对话框"""
        config = self.error_config.get(error_type, {})
        
        title = config.get("title", "错误")
        message = custom_message or config.get("message", "操作失败")
        suggestions = config.get("suggestions", [])
        
        # 构建完整消息
        full_message = message
        if details:
            full_message += f"\\n\\n详细信息: {details}"
        if suggestions:
            full_message += "\\n\\n建议解决方案:"
            for i, suggestion in enumerate(suggestions, 1):
                full_message += f"\\n{i}. {suggestion}"
        
        # 显示消息框
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(full_message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
    def show_success(self, parent: Optional[QWidget], message: str):
        """显示成功消息"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("成功")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
    def show_warning(self, parent: Optional[QWidget], message: str):
        """显示警告消息"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("警告")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
    def confirm_action(self, parent: Optional[QWidget], message: str, 
                      title: str = "确认操作") -> bool:
        """确认操作对话框"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        return msg_box.exec() == QMessageBox.StandardButton.Yes

# 全局错误处理器实例
error_handler = FriendlyErrorHandler()
'''
            
            error_handler_file = PROJECT_ROOT / "scripts" / "error_handler.py"
            with open(error_handler_file, 'w', encoding='utf-8') as f:
                f.write(error_handler_code)
            
            result["optimizations"].append("错误处理工具类已创建")
            print("      ✅ 错误处理工具类已创建")
            
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"错误提示优化失败: {e}")
            print(f"   ❌ 错误提示优化失败: {e}")
            
        return result
        
    def optimize_operation_flow(self) -> Dict[str, Any]:
        """优化功能操作流程"""
        print("\n🖱️ 优化功能操作流程...")
        
        result = {
            "status": "success",
            "optimizations": [],
            "issues": []
        }
        
        try:
            # 创建操作指南
            operation_guide = {
                "keyboard_shortcuts": {
                    "Ctrl+N": "新建",
                    "Ctrl+S": "保存",
                    "Ctrl+O": "打开",
                    "Ctrl+F": "查找",
                    "Ctrl+Z": "撤销",
                    "Ctrl+Y": "重做",
                    "F5": "刷新",
                    "Escape": "取消"
                },
                "mouse_operations": {
                    "single_click": "选择项目",
                    "double_click": "编辑项目",
                    "right_click": "显示上下文菜单",
                    "drag_drop": "移动或重新排序"
                },
                "workflow_tips": [
                    "使用拖拽操作可以快速调整系统和流程的位置",
                    "双击表格行可以快速编辑项目",
                    "右键点击可以查看更多操作选项",
                    "使用Ctrl+点击可以多选项目",
                    "按住Shift+点击可以范围选择"
                ]
            }
            
            guide_file = PROJECT_ROOT / "operation_guide.json"
            with open(guide_file, 'w', encoding='utf-8') as f:
                json.dump(operation_guide, f, indent=2, ensure_ascii=False)
            
            result["optimizations"].append("操作指南已创建")
            print("      ✅ 操作指南已创建")
            
            # 创建快捷操作配置
            quick_actions = {
                "toolbar_actions": [
                    {"name": "新建系统", "icon": "system_add", "shortcut": "Ctrl+Shift+S"},
                    {"name": "新建流程", "icon": "process_add", "shortcut": "Ctrl+Shift+P"},
                    {"name": "新建SOP", "icon": "sop_add", "shortcut": "Ctrl+Shift+O"},
                    {"name": "新建KPI", "icon": "kpi_add", "shortcut": "Ctrl+Shift+K"},
                    {"name": "新建任务", "icon": "task_add", "shortcut": "Ctrl+Shift+T"}
                ],
                "context_menu_actions": [
                    {"name": "编辑", "icon": "edit"},
                    {"name": "删除", "icon": "delete"},
                    {"name": "复制", "icon": "copy"},
                    {"name": "导出", "icon": "export"},
                    {"name": "属性", "icon": "properties"}
                ]
            }
            
            actions_file = PROJECT_ROOT / "quick_actions.json"
            with open(actions_file, 'w', encoding='utf-8') as f:
                json.dump(quick_actions, f, indent=2, ensure_ascii=False)
            
            result["optimizations"].append("快捷操作配置已创建")
            print("      ✅ 快捷操作配置已创建")
            
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"操作流程优化失败: {e}")
            print(f"   ❌ 操作流程优化失败: {e}")
            
        return result
        
    def optimize_data_display(self) -> Dict[str, Any]:
        """优化数据展示"""
        print("\n📊 优化数据展示...")
        
        result = {
            "status": "success",
            "optimizations": [],
            "issues": []
        }
        
        try:
            # 创建数据展示配置
            display_config = {
                "table_settings": {
                    "row_height": 35,
                    "header_height": 40,
                    "alternating_colors": True,
                    "grid_visible": True,
                    "sort_enabled": True,
                    "filter_enabled": True
                },
                "chart_settings": {
                    "default_colors": ["#2196F3", "#4CAF50", "#FF9800", "#F44336", "#9C27B0"],
                    "animation_enabled": True,
                    "legend_position": "bottom",
                    "grid_visible": True
                },
                "pagination": {
                    "page_size": 50,
                    "show_page_info": True,
                    "show_total_count": True
                },
                "formatting": {
                    "date_format": "YYYY-MM-DD",
                    "datetime_format": "YYYY-MM-DD HH:mm:ss",
                    "number_format": "0,0.00",
                    "percentage_format": "0.0%"
                }
            }
            
            display_file = PROJECT_ROOT / "display_config.json"
            with open(display_file, 'w', encoding='utf-8') as f:
                json.dump(display_config, f, indent=2, ensure_ascii=False)
            
            result["optimizations"].append("数据展示配置已创建")
            print("      ✅ 数据展示配置已创建")
            
            # 优化数据库视图
            if self.db_path.exists():
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 创建有用的视图
                views = [
                    ("system_summary", """
                        CREATE VIEW IF NOT EXISTS system_summary AS
                        SELECT 
                            s.id,
                            s.name,
                            s.description,
                            COUNT(p.id) as process_count,
                            s.created_at
                        FROM systems s
                        LEFT JOIN processes p ON s.id = p.system_id
                        GROUP BY s.id, s.name, s.description, s.created_at
                    """),
                    ("task_summary", """
                        CREATE VIEW IF NOT EXISTS task_summary AS
                        SELECT 
                            status,
                            priority,
                            COUNT(*) as count,
                            AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completion_rate
                        FROM tasks
                        GROUP BY status, priority
                    """),
                    ("kpi_dashboard", """
                        CREATE VIEW IF NOT EXISTS kpi_dashboard AS
                        SELECT 
                            name,
                            current_value,
                            target_value,
                            unit,
                            CASE 
                                WHEN current_value >= target_value THEN 'good'
                                WHEN current_value >= target_value * 0.8 THEN 'warning'
                                ELSE 'critical'
                            END as status
                        FROM kpis
                    """)
                ]
                
                for view_name, sql in views:
                    try:
                        cursor.execute(sql)
                        result["optimizations"].append(f"创建视图: {view_name}")
                        print(f"      ✅ 创建视图: {view_name}")
                    except sqlite3.Error as e:
                        result["issues"].append(f"视图创建失败: {view_name} - {e}")
                        print(f"      ⚠️ 视图创建失败: {view_name}")
                
                conn.commit()
                conn.close()
            
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"数据展示优化失败: {e}")
            print(f"   ❌ 数据展示优化失败: {e}")
            
        return result
        
    def optimize_performance(self) -> Dict[str, Any]:
        """优化系统性能"""
        print("\n⚡ 优化系统性能...")
        
        result = {
            "status": "success",
            "optimizations": [],
            "issues": []
        }
        
        try:
            # 创建性能配置
            performance_config = {
                "cache_settings": {
                    "enable_cache": True,
                    "cache_size": 1000,
                    "cache_ttl": 300
                },
                "database_settings": {
                    "connection_pool_size": 5,
                    "query_timeout": 30,
                    "batch_size": 100
                },
                "ui_settings": {
                    "lazy_loading": True,
                    "virtual_scrolling": True,
                    "debounce_delay": 300
                },
                "memory_settings": {
                    "max_memory_usage": "200MB",
                    "gc_threshold": 1000
                }
            }
            
            perf_file = PROJECT_ROOT / "performance_config.json"
            with open(perf_file, 'w', encoding='utf-8') as f:
                json.dump(performance_config, f, indent=2, ensure_ascii=False)
            
            result["optimizations"].append("性能配置已创建")
            print("      ✅ 性能配置已创建")
            
            # 数据库性能优化
            if self.db_path.exists():
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # 设置SQLite性能参数
                optimizations = [
                    "PRAGMA journal_mode = WAL",
                    "PRAGMA synchronous = NORMAL",
                    "PRAGMA cache_size = 10000",
                    "PRAGMA temp_store = MEMORY"
                ]
                
                for pragma in optimizations:
                    try:
                        cursor.execute(pragma)
                        result["optimizations"].append(f"数据库优化: {pragma}")
                        print(f"      ✅ 数据库优化: {pragma}")
                    except sqlite3.Error as e:
                        result["issues"].append(f"数据库优化失败: {pragma} - {e}")
                        print(f"      ⚠️ 数据库优化失败: {pragma}")
                
                conn.close()
            
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"性能优化失败: {e}")
            print(f"   ❌ 性能优化失败: {e}")
            
        return result
        
    def generate_optimization_report(self):
        """生成优化报告"""
        print("\n📊 生成优化报告...")
        
        # 计算总体状态
        all_statuses = [opt["status"] for opt in self.optimization_results["optimizations"].values()]
        
        if "error" in all_statuses:
            overall_status = "部分失败"
        else:
            overall_status = "成功"
            
        self.optimization_results["overall_status"] = overall_status
        
        # 保存报告
        report_file = PROJECT_ROOT / "user_experience_optimization_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_results, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 优化报告已保存: {report_file}")
        
        return str(report_file)
        
    def print_optimization_summary(self):
        """打印优化摘要"""
        print("\n" + "="*60)
        print("📋 用户体验优化摘要")
        print("="*60)
        
        for opt_name, opt_result in self.optimization_results["optimizations"].items():
            status_icon = "✅" if opt_result["status"] == "success" else "❌"
            print(f"{status_icon} {opt_name}: {opt_result['status'].upper()}")
            
            for optimization in opt_result["optimizations"]:
                print(f"   • {optimization}")
                
            if opt_result["issues"]:
                for issue in opt_result["issues"]:
                    print(f"   ⚠️ {issue}")
        
        print("="*60)
        print(f"🎯 总体状态: {self.optimization_results['overall_status']}")
        print("="*60)
        
    def run_optimization(self):
        """运行完整优化流程"""
        try:
            self.print_header()
            
            # 执行各项优化
            self.optimization_results["optimizations"]["interface_responsiveness"] = self.optimize_interface_responsiveness()
            self.optimization_results["optimizations"]["error_messages"] = self.optimize_error_messages()
            self.optimization_results["optimizations"]["operation_flow"] = self.optimize_operation_flow()
            self.optimization_results["optimizations"]["data_display"] = self.optimize_data_display()
            self.optimization_results["optimizations"]["performance"] = self.optimize_performance()
            
            # 生成报告
            report_file = self.generate_optimization_report()
            
            # 打印摘要
            self.print_optimization_summary()
            
            print(f"\n📄 详细报告: {report_file}")
            print("\n🎉 用户体验优化完成！")
            
            return True
            
        except Exception as e:
            logger.error(f"用户体验优化失败: {e}")
            print(f"\n❌ 用户体验优化失败: {e}")
            return False

def main():
    """主函数"""
    optimizer = UserExperienceOptimizer()
    success = optimizer.run_optimization()
    
    if success:
        print("\n✅ 用户体验优化成功")
        sys.exit(0)
    else:
        print("\n❌ 用户体验优化失败")
        sys.exit(1)

if __name__ == "__main__":
    main()