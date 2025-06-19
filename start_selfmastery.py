#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 综合启动脚本
一键启动完整系统，包含健康检查、功能验证、用户体验优化
"""

import sys
import os
import time
import subprocess
import threading
from pathlib import Path
from typing import Optional
import logging

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent
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

class SelfMasteryLauncher:
    """SelfMastery系统启动器"""
    
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        
    def print_welcome_banner(self):
        """打印欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ███████╗███████╗██╗     ███████╗███╗   ███╗ █████╗        ║
║    ██╔════╝██╔════╝██║     ██╔════╝████╗ ████║██╔══██╗       ║
║    ███████╗█████╗  ██║     █████╗  ██╔████╔██║███████║       ║
║    ╚════██║██╔══╝  ██║     ██╔══╝  ██║╚██╔╝██║██╔══██║       ║
║    ███████║███████╗███████╗██║     ██║ ╚═╝ ██║██║  ██║       ║
║    ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝       ║
║                                                              ║
║                    B2B业务管理系统                           ║
║                                                              ║
║    🎯 让管理更简单，让企业更高效                              ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  欢迎使用 SelfMastery B2B业务系统！                          ║
║                                                              ║
║  🏢 业务系统管理 | 🔄 业务流程设计 | 📋 SOP文档管理           ║
║  📊 KPI指标监控 | ✅ 任务管理     | 🤝 团队协作             ║
║                                                              ║
║  正在为您启动系统，请稍候...                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def show_startup_menu(self) -> str:
        """显示启动菜单"""
        menu = """
╔══════════════════════════════════════════════════════════════╗
║                        启动选项                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. 🚀 快速启动 (推荐)                                       ║
║     直接启动系统，适合日常使用                               ║
║                                                              ║
║  2. 🔧 完整启动                                              ║
║     包含健康检查、功能验证、用户体验优化                     ║
║                                                              ║
║  3. 🏥 健康检查                                              ║
║     仅运行系统健康检查                                       ║
║                                                              ║
║  4. ✅ 功能验证                                              ║
║     仅运行核心功能验证                                       ║
║                                                              ║
║  5. 🎨 用户体验优化                                          ║
║     仅运行用户体验优化                                       ║
║                                                              ║
║  6. 📚 查看文档                                              ║
║     打开快速入门指南                                         ║
║                                                              ║
║  0. ❌ 退出                                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

请选择启动选项 (1-6, 0退出): """
        
        while True:
            try:
                choice = input(menu).strip()
                if choice in ['0', '1', '2', '3', '4', '5', '6']:
                    return choice
                else:
                    print("❌ 无效选择，请输入 0-6 之间的数字")
            except KeyboardInterrupt:
                print("\n👋 用户取消操作")
                return '0'
            except Exception:
                print("❌ 输入错误，请重试")
                
    def run_health_check(self) -> bool:
        """运行健康检查"""
        print("\n🏥 运行系统健康检查...")
        try:
            result = subprocess.run([
                sys.executable, "scripts/health_check.py"
            ], cwd=PROJECT_ROOT, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 系统健康检查通过")
                return True
            else:
                print("⚠️ 系统健康检查发现问题")
                print(result.stdout)
                return False
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False
            
    def run_function_verification(self) -> bool:
        """运行功能验证"""
        print("\n✅ 运行核心功能验证...")
        try:
            result = subprocess.run([
                sys.executable, "scripts/verify_core_functions.py"
            ], cwd=PROJECT_ROOT, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 核心功能验证通过")
                return True
            else:
                print("⚠️ 核心功能验证发现问题")
                print(result.stdout)
                return False
        except Exception as e:
            print(f"❌ 功能验证失败: {e}")
            return False
            
    def run_ux_optimization(self) -> bool:
        """运行用户体验优化"""
        print("\n🎨 运行用户体验优化...")
        try:
            result = subprocess.run([
                sys.executable, "scripts/optimize_user_experience.py"
            ], cwd=PROJECT_ROOT, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 用户体验优化完成")
                return True
            else:
                print("⚠️ 用户体验优化部分失败")
                print(result.stdout)
                return True  # 不影响系统启动
        except Exception as e:
            print(f"❌ 用户体验优化失败: {e}")
            return True  # 不影响系统启动
            
    def show_documentation(self):
        """显示文档"""
        print("\n📚 打开快速入门指南...")
        
        docs = [
            ("快速入门指南", "docs/quick-start.md"),
            ("用户指南", "docs/user-guide.md"),
            ("技术架构", "docs/technical-architecture.md"),
            ("最终项目报告", "docs/final-project-report.md")
        ]
        
        print("\n可用文档:")
        for i, (name, path) in enumerate(docs, 1):
            doc_path = PROJECT_ROOT / path
            status = "✅" if doc_path.exists() else "❌"
            print(f"  {i}. {status} {name}: {path}")
            
        print("\n💡 您可以使用文本编辑器或Markdown查看器打开这些文档")
        
    def start_system_demo(self) -> bool:
        """启动系统演示"""
        print("\n🚀 启动系统演示...")
        try:
            # 在新线程中启动演示系统
            def run_demo():
                subprocess.run([
                    sys.executable, "scripts/demo_system.py"
                ], cwd=PROJECT_ROOT)
            
            demo_thread = threading.Thread(target=run_demo, daemon=True)
            demo_thread.start()
            
            print("✅ 系统演示已启动")
            return True
        except Exception as e:
            print(f"❌ 系统演示启动失败: {e}")
            return False
            
    def start_ui_simple(self) -> bool:
        """启动简化UI"""
        print("\n🎨 启动用户界面...")
        try:
            # 在新线程中启动UI
            def run_ui():
                subprocess.run([
                    sys.executable, "scripts/start_ui_simple.py"
                ], cwd=PROJECT_ROOT)
            
            ui_thread = threading.Thread(target=run_ui, daemon=True)
            ui_thread.start()
            
            print("✅ 用户界面已启动")
            return True
        except Exception as e:
            print(f"❌ 用户界面启动失败: {e}")
            return False
            
    def show_system_info(self):
        """显示系统信息"""
        info = f"""
╔══════════════════════════════════════════════════════════════╗
║                        系统信息                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📁 项目目录: {PROJECT_ROOT}
║  🐍 Python版本: {sys.version.split()[0]}
║  💻 操作系统: {sys.platform}
║                                                              ║
║  🌐 后端API: http://localhost:8000                           ║
║  📊 API文档: http://localhost:8000/docs                      ║
║  🎨 前端界面: PyQt6桌面应用                                  ║
║                                                              ║
║  📚 文档目录: docs/                                          ║
║  🔧 脚本目录: scripts/                                       ║
║  🗄️ 数据目录: data/                                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(info)
        
    def show_usage_tips(self):
        """显示使用提示"""
        tips = """
╔══════════════════════════════════════════════════════════════╗
║                        使用提示                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🎯 快速上手:                                                ║
║     1. 点击主界面的功能按钮开始使用                          ║
║     2. 从业务系统管理开始，建立企业架构                      ║
║     3. 设计核心业务流程                                      ║
║     4. 创建标准作业程序(SOP)                                 ║
║     5. 设置关键绩效指标(KPI)                                 ║
║                                                              ║
║  ⌨️ 快捷键:                                                  ║
║     • Ctrl+N: 新建项目                                       ║
║     • Ctrl+S: 保存                                          ║
║     • Ctrl+F: 查找                                          ║
║     • F5: 刷新                                              ║
║     • Escape: 取消操作                                       ║
║                                                              ║
║  🖱️ 鼠标操作:                                                ║
║     • 单击: 选择项目                                         ║
║     • 双击: 编辑项目                                         ║
║     • 右键: 显示菜单                                         ║
║     • 拖拽: 移动位置                                         ║
║                                                              ║
║  🆘 获取帮助:                                                ║
║     • 查看 docs/quick-start.md                              ║
║     • 运行健康检查诊断问题                                   ║
║     • 联系技术支持                                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(tips)
        
    def wait_for_exit(self):
        """等待用户退出"""
        try:
            print("\n🎉 SelfMastery 系统正在运行...")
            print("💡 按 Ctrl+C 停止系统")
            
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 正在停止系统...")
            
    def run_launcher(self):
        """运行启动器"""
        try:
            self.print_welcome_banner()
            time.sleep(2)  # 让用户看到欢迎信息
            
            choice = self.show_startup_menu()
            
            if choice == '0':
                print("👋 再见！")
                return
            elif choice == '1':
                # 快速启动
                print("\n🚀 快速启动模式")
                self.show_system_info()
                self.start_ui_simple()
                self.show_usage_tips()
                self.wait_for_exit()
                
            elif choice == '2':
                # 完整启动
                print("\n🔧 完整启动模式")
                self.show_system_info()
                
                # 运行健康检查
                health_ok = self.run_health_check()
                if not health_ok:
                    print("⚠️ 健康检查未通过，但继续启动...")
                
                # 运行功能验证
                func_ok = self.run_function_verification()
                if not func_ok:
                    print("⚠️ 功能验证未通过，但继续启动...")
                
                # 运行用户体验优化
                self.run_ux_optimization()
                
                # 启动系统
                self.start_system_demo()
                self.show_usage_tips()
                self.wait_for_exit()
                
            elif choice == '3':
                # 仅健康检查
                self.run_health_check()
                input("\n按回车键返回...")
                self.run_launcher()
                
            elif choice == '4':
                # 仅功能验证
                self.run_function_verification()
                input("\n按回车键返回...")
                self.run_launcher()
                
            elif choice == '5':
                # 仅用户体验优化
                self.run_ux_optimization()
                input("\n按回车键返回...")
                self.run_launcher()
                
            elif choice == '6':
                # 查看文档
                self.show_documentation()
                input("\n按回车键返回...")
                self.run_launcher()
                
        except Exception as e:
            logger.error(f"启动器运行失败: {e}")
            print(f"\n❌ 启动器运行失败: {e}")
            print("\n💡 故障排除:")
            print("   1. 检查Python环境")
            print("   2. 检查项目文件完整性")
            print("   3. 运行健康检查: python scripts/health_check.py")

def main():
    """主函数"""
    launcher = SelfMasteryLauncher()
    launcher.run_launcher()

if __name__ == "__main__":
    main()