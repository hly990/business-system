#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 一键安装脚本
自动安装依赖、初始化数据库、配置环境
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Optional
import logging
import json

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SELFMASTERY_ROOT = PROJECT_ROOT / "selfmastery"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemInstaller:
    """系统安装器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_executable = sys.executable
        self.installation_log = []
        
    def print_banner(self):
        """打印安装横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    SelfMastery B2B业务系统                    ║
║                      一键安装工具                            ║
╠══════════════════════════════════════════════════════════════╣
║  🔧 自动检查系统环境                                         ║
║  📦 自动安装Python依赖                                       ║
║  🗄️ 自动初始化数据库                                         ║
║  ⚙️ 自动配置系统环境                                         ║
║  🎯 创建演示数据                                             ║
║  ✅ 验证安装结果                                             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def log_step(self, message: str, success: bool = True):
        """记录安装步骤"""
        status = "✅" if success else "❌"
        print(f"{status} {message}")
        self.installation_log.append({
            "message": message,
            "success": success,
            "timestamp": str(Path().cwd())
        })
        
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("\n🐍 检查Python环境...")
        
        version = sys.version_info
        if version >= (3, 8):
            self.log_step(f"Python版本: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.log_step(f"Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)", False)
            return False
            
    def check_system_requirements(self) -> bool:
        """检查系统要求"""
        print("\n🔍 检查系统要求...")
        
        # 检查操作系统
        if self.system in ['windows', 'darwin', 'linux']:
            self.log_step(f"操作系统: {platform.system()} {platform.release()}")
        else:
            self.log_step(f"不支持的操作系统: {self.system}", False)
            return False
            
        # 检查pip
        try:
            result = subprocess.run([self.python_executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_step("pip工具: 可用")
            else:
                self.log_step("pip工具: 不可用", False)
                return False
        except Exception as e:
            self.log_step(f"pip检查失败: {e}", False)
            return False
            
        # 检查磁盘空间
        try:
            disk_usage = shutil.disk_usage(PROJECT_ROOT)
            free_gb = disk_usage.free / (1024**3)
            if free_gb >= 1.0:
                self.log_step(f"磁盘空间: {free_gb:.1f}GB 可用")
            else:
                self.log_step(f"磁盘空间不足: {free_gb:.1f}GB (需要至少1GB)", False)
                return False
        except Exception as e:
            self.log_step(f"磁盘空间检查失败: {e}", False)
            
        return True
        
    def create_virtual_environment(self) -> bool:
        """创建虚拟环境"""
        print("\n🏗️ 创建虚拟环境...")
        
        venv_path = PROJECT_ROOT / "venv"
        
        # 检查是否已存在虚拟环境
        if venv_path.exists():
            self.log_step("虚拟环境已存在，跳过创建")
            return True
            
        try:
            # 创建虚拟环境
            result = subprocess.run([
                self.python_executable, "-m", "venv", str(venv_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step("虚拟环境创建成功")
                return True
            else:
                self.log_step(f"虚拟环境创建失败: {result.stderr}", False)
                return False
                
        except Exception as e:
            self.log_step(f"虚拟环境创建异常: {e}", False)
            return False
            
    def install_dependencies(self) -> bool:
        """安装Python依赖"""
        print("\n📦 安装Python依赖...")
        
        requirements_file = SELFMASTERY_ROOT / "requirements.txt"
        if not requirements_file.exists():
            self.log_step("requirements.txt文件不存在", False)
            return False
            
        try:
            # 升级pip
            self.log_step("升级pip...")
            result = subprocess.run([
                self.python_executable, "-m", "pip", "install", "--upgrade", "pip"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log_step(f"pip升级失败: {result.stderr}", False)
                
            # 安装依赖
            self.log_step("安装项目依赖...")
            result = subprocess.run([
                self.python_executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step("Python依赖安装成功")
                return True
            else:
                self.log_step(f"依赖安装失败: {result.stderr}", False)
                return False
                
        except Exception as e:
            self.log_step(f"依赖安装异常: {e}", False)
            return False
            
    def setup_environment(self) -> bool:
        """设置环境配置"""
        print("\n⚙️ 配置系统环境...")
        
        try:
            # 创建数据目录
            data_dir = PROJECT_ROOT / "data"
            if not data_dir.exists():
                data_dir.mkdir(exist_ok=True)
                self.log_step("数据目录创建成功")
            else:
                self.log_step("数据目录已存在")
                
            # 创建日志目录
            logs_dir = PROJECT_ROOT / "logs"
            if not logs_dir.exists():
                logs_dir.mkdir(exist_ok=True)
                self.log_step("日志目录创建成功")
            else:
                self.log_step("日志目录已存在")
                
            # 创建上传目录
            uploads_dir = PROJECT_ROOT / "uploads"
            if not uploads_dir.exists():
                uploads_dir.mkdir(exist_ok=True)
                self.log_step("上传目录创建成功")
            else:
                self.log_step("上传目录已存在")
                
            # 检查环境变量文件
            env_file = SELFMASTERY_ROOT / ".env"
            env_example = SELFMASTERY_ROOT / ".env.example"
            
            if not env_file.exists() and env_example.exists():
                shutil.copy2(env_example, env_file)
                self.log_step("环境配置文件创建成功")
            else:
                self.log_step("环境配置文件已存在")
                
            return True
            
        except Exception as e:
            self.log_step(f"环境配置失败: {e}", False)
            return False
            
    def initialize_database(self) -> bool:
        """初始化数据库"""
        print("\n🗄️ 初始化数据库...")
        
        try:
            # 运行数据库初始化脚本
            init_script = PROJECT_ROOT / "scripts" / "init_db.py"
            if init_script.exists():
                result = subprocess.run([
                    self.python_executable, str(init_script)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_step("数据库初始化成功")
                else:
                    self.log_step(f"数据库初始化失败: {result.stderr}", False)
                    return False
            else:
                self.log_step("数据库初始化脚本不存在", False)
                return False
                
            return True
            
        except Exception as e:
            self.log_step(f"数据库初始化异常: {e}", False)
            return False
            
    def create_demo_data(self) -> bool:
        """创建演示数据"""
        print("\n📊 创建演示数据...")
        
        try:
            # 运行演示数据创建脚本
            demo_script = PROJECT_ROOT / "scripts" / "create_demo_data.py"
            if demo_script.exists():
                result = subprocess.run([
                    self.python_executable, str(demo_script)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_step("演示数据创建成功")
                else:
                    self.log_step(f"演示数据创建失败: {result.stderr}", False)
                    # 演示数据创建失败不影响整体安装
                    
            else:
                self.log_step("演示数据脚本不存在，跳过")
                
            return True
            
        except Exception as e:
            self.log_step(f"演示数据创建异常: {e}", False)
            return True  # 不影响整体安装
            
    def verify_installation(self) -> bool:
        """验证安装结果"""
        print("\n✅ 验证安装结果...")
        
        try:
            # 检查核心模块导入
            test_imports = [
                "PyQt6.QtWidgets",
                "fastapi",
                "sqlalchemy",
                "requests"
            ]
            
            for module in test_imports:
                try:
                    __import__(module)
                    self.log_step(f"模块 {module}: 可用")
                except ImportError:
                    self.log_step(f"模块 {module}: 不可用", False)
                    return False
                    
            # 检查数据库文件
            db_file = PROJECT_ROOT / "data" / "selfmastery.db"
            if db_file.exists():
                self.log_step("数据库文件: 存在")
            else:
                self.log_step("数据库文件: 不存在", False)
                return False
                
            # 检查关键脚本
            scripts = [
                "scripts/demo_system.py",
                "scripts/health_check.py",
                "scripts/start_ui_simple.py"
            ]
            
            for script in scripts:
                script_path = PROJECT_ROOT / script
                if script_path.exists():
                    self.log_step(f"脚本 {script}: 存在")
                else:
                    self.log_step(f"脚本 {script}: 不存在", False)
                    
            return True
            
        except Exception as e:
            self.log_step(f"安装验证异常: {e}", False)
            return False
            
    def create_shortcuts(self) -> bool:
        """创建快捷方式"""
        print("\n🔗 创建快捷方式...")
        
        try:
            # 创建启动脚本
            if self.system == "windows":
                # Windows批处理文件
                start_script = PROJECT_ROOT / "start_selfmastery.bat"
                with open(start_script, 'w', encoding='utf-8') as f:
                    f.write(f"""@echo off
cd /d "{PROJECT_ROOT}"
"{self.python_executable}" scripts/demo_system.py
pause
""")
                self.log_step("Windows启动脚本创建成功")
                
            else:
                # Unix shell脚本
                start_script = PROJECT_ROOT / "start_selfmastery.sh"
                with open(start_script, 'w', encoding='utf-8') as f:
                    f.write(f"""#!/bin/bash
cd "{PROJECT_ROOT}"
"{self.python_executable}" scripts/demo_system.py
""")
                # 添加执行权限
                os.chmod(start_script, 0o755)
                self.log_step("Unix启动脚本创建成功")
                
            return True
            
        except Exception as e:
            self.log_step(f"快捷方式创建失败: {e}", False)
            return True  # 不影响整体安装
            
    def save_installation_report(self):
        """保存安装报告"""
        report = {
            "installation_date": str(Path().cwd()),
            "system_info": {
                "os": platform.system(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "architecture": platform.architecture()[0]
            },
            "installation_log": self.installation_log
        }
        
        report_file = PROJECT_ROOT / "installation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 安装报告已保存: {report_file}")
        
    def print_success_message(self):
        """打印成功消息"""
        success_message = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎉 安装成功！                             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  SelfMastery B2B业务系统已成功安装到您的计算机上             ║
║                                                              ║
║  📁 安装目录: {PROJECT_ROOT}
║                                                              ║
║  🚀 启动方式:                                                ║
║     方式1: 双击 start_selfmastery.{'bat' if self.system == 'windows' else 'sh'}                        ║
║     方式2: python scripts/demo_system.py                    ║
║                                                              ║
║  📚 文档位置:                                                ║
║     • 快速入门: docs/quick-start.md                         ║
║     • 用户指南: docs/user-guide.md                          ║
║     • 技术文档: docs/technical-architecture.md             ║
║                                                              ║
║  🔧 管理工具:                                                ║
║     • 健康检查: python scripts/health_check.py             ║
║     • 功能验证: python scripts/verify_core_functions.py    ║
║                                                              ║
║  💡 如有问题，请查看故障排除指南或联系技术支持                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(success_message)
        
    def run_installation(self) -> bool:
        """运行完整安装流程"""
        try:
            self.print_banner()
            
            # 检查系统环境
            if not self.check_python_version():
                return False
                
            if not self.check_system_requirements():
                return False
                
            # 创建虚拟环境（可选）
            # self.create_virtual_environment()
            
            # 安装依赖
            if not self.install_dependencies():
                return False
                
            # 配置环境
            if not self.setup_environment():
                return False
                
            # 初始化数据库
            if not self.initialize_database():
                return False
                
            # 创建演示数据
            self.create_demo_data()
            
            # 验证安装
            if not self.verify_installation():
                return False
                
            # 创建快捷方式
            self.create_shortcuts()
            
            # 保存安装报告
            self.save_installation_report()
            
            # 打印成功消息
            self.print_success_message()
            
            return True
            
        except Exception as e:
            logger.error(f"安装过程异常: {e}")
            print(f"\n❌ 安装失败: {e}")
            return False

def main():
    """主函数"""
    installer = SystemInstaller()
    success = installer.run_installation()
    
    if success:
        print("\n✅ 安装完成")
        sys.exit(0)
    else:
        print("\n❌ 安装失败")
        print("\n💡 故障排除建议:")
        print("   1. 检查Python版本是否 >= 3.8")
        print("   2. 检查网络连接是否正常")
        print("   3. 检查磁盘空间是否充足")
        print("   4. 尝试手动安装依赖: pip install -r selfmastery/requirements.txt")
        print("   5. 查看安装日志获取详细错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()