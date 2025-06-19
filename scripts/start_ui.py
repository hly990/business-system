#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - UI界面启动脚本
使用 Sentry 监控启动过程
"""
import os
import sys
import time
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

def init_sentry():
    """初始化 Sentry 监控"""
    try:
        # 直接设置环境变量
        os.environ['SENTRY_DSN'] = 'https://23cfa82afa65f55af9665127fe0fff22@o4509522231951360.ingest.us.sentry.io/4509525295235072'
        os.environ['SENTRY_ENVIRONMENT'] = 'development'
        
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_logging = LoggingIntegration(
            level=20,  # INFO level
            event_level=40  # ERROR level
        )
        
        sentry_sdk.init(
            dsn=os.environ['SENTRY_DSN'],
            integrations=[sentry_logging],
            traces_sample_rate=0.1,
            environment=os.environ.get('SENTRY_ENVIRONMENT', 'development'),
            release='selfmastery@1.0.0'
        )
        
        sentry_sdk.capture_message("UI界面启动脚本开始", level="info")
        print("   ✅ Sentry 监控初始化成功")
        return True
    except Exception as e:
        print(f"   ⚠️  Sentry 监控初始化失败: {e}")
        return False

def check_backend_running():
    """检查后端是否运行"""
    print("🔍 检查后端服务状态...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("   ✅ 后端服务正在运行")
            return True
        else:
            print(f"   ❌ 后端服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 无法连接到后端服务: {e}")
        return False

def check_dependencies():
    """检查UI依赖"""
    print("📦 检查UI依赖...")
    
    try:
        # 检查 PyQt6
        import PyQt6.QtCore
        print(f"   ✅ PyQt6: {PyQt6.QtCore.PYQT_VERSION_STR}")
        
        # 检查其他依赖
        dependencies = [
            'requests',
            'Pillow', 
            'matplotlib'
        ]
        
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"   ✅ {dep}: 已安装")
            except ImportError:
                print(f"   ⚠️  {dep}: 未安装")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 关键依赖缺失: {e}")
        return False

def start_ui():
    """启动UI界面"""
    print("🎨 启动UI界面...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env.update({
            'PYTHONPATH': f"{project_root}:{project_root}/selfmastery",
            'QT_QPA_PLATFORM': 'cocoa',  # macOS
            'QT_AUTO_SCREEN_SCALE_FACTOR': '1',
            'QT_ENABLE_HIGHDPI_SCALING': '1'
        })
        
        # 启动前端应用
        frontend_main = project_root / "selfmastery" / "frontend" / "main.py"
        
        print(f"   🚀 启动前端应用: {frontend_main}")
        
        # 使用 Python 直接启动
        process = subprocess.Popen([
            sys.executable, str(frontend_main)
        ], 
        cwd=str(project_root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
        
        print("   ✅ UI进程已启动")
        
        # 等待进程启动并检查状态
        time.sleep(2)
        
        if process.poll() is None:
            print("   ✅ UI界面正在运行")
            return True, process
        else:
            # 获取错误输出
            stdout, stderr = process.communicate()
            print(f"   ❌ UI进程启动失败")
            if stderr:
                print(f"   错误信息: {stderr.decode('utf-8')}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ UI启动失败: {e}")
        return False, None

def start_ui_simple():
    """简单模式启动UI"""
    print("🎨 简单模式启动UI...")
    
    try:
        # 直接在当前进程中启动UI
        os.chdir(str(project_root))
        
        # 设置环境变量
        os.environ['PYTHONPATH'] = f"{project_root}:{project_root}/selfmastery"
        
        # 导入并启动UI
        sys.path.insert(0, str(project_root / "selfmastery"))
        
        print("   📱 正在加载UI组件...")
        
        from frontend.main import main as start_frontend
        
        print("   🚀 启动UI界面...")
        start_frontend()
        
        return True
        
    except Exception as e:
        print(f"   ❌ 简单模式启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🎯 SelfMastery B2B业务系统 - UI界面启动工具")
    print("=" * 60)
    
    try:
        # 1. 初始化 Sentry
        print("\n🛡️ 1. 初始化 Sentry 监控...")
        sentry_ok = init_sentry()
        
        # 2. 检查依赖
        print("\n📦 2. 检查依赖...")
        deps_ok = check_dependencies()
        if not deps_ok:
            print("❌ 依赖检查失败，某些功能可能不可用")
        
        # 3. 检查后端
        print("\n🔍 3. 检查后端服务...")
        backend_ok = check_backend_running()
        if not backend_ok:
            print("⚠️  后端服务未运行，部分功能将不可用")
            print("   💡 提示: 运行 'python scripts/final_startup_fix.py' 启动后端")
        
        # 4. 启动UI
        print("\n🎨 4. 启动UI界面...")
        
        # 尝试简单模式启动
        ui_ok = start_ui_simple()
        
        if ui_ok:
            print("\n" + "="*60)
            print("🎉 SelfMastery B2B业务系统UI启动成功！")
            print("="*60)
            print("📊 界面状态:")
            print("   ✅ UI界面: 正在运行")
            print(f"   {'✅' if backend_ok else '⚠️ '} 后端连接: {'正常' if backend_ok else '断开'}")
            print(f"   {'✅' if sentry_ok else '⚠️ '} Sentry监控: {'正常' if sentry_ok else '未配置'}")
            
            if sentry_ok:
                import sentry_sdk
                sentry_sdk.capture_message("UI界面启动成功", level="info")
        else:
            print("\n❌ UI界面启动失败")
            if sentry_ok:
                import sentry_sdk
                sentry_sdk.capture_message("UI界面启动失败", level="error")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ UI启动过程中发生错误: {str(e)}")
        if 'sentry_ok' in locals() and sentry_ok:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 故障排除建议:")
        print("   1. 确保安装了 PyQt6: pip install PyQt6")
        print("   2. 确保后端服务运行: python scripts/final_startup_fix.py")
        print("   3. 检查日志文件: logs/application.log")
        print("   4. 尝试手动启动: cd selfmastery && python frontend/main.py")
    
    sys.exit(0 if success else 1) 