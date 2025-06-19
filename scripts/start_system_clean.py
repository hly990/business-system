#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 清洁启动脚本
绕过环境变量缓存问题，使用 Sentry 监控
"""
import os
import sys
import time
import subprocess
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

def init_sentry():
    """初始化 Sentry 监控（如果可用）"""
    try:
        from selfmastery.backend.utils.monitoring import (
            init_sentry_monitoring,
            capture_message,
            capture_exception,
            add_breadcrumb
        )
        
        init_sentry_monitoring()
        capture_message("开始系统清洁启动", level="info")
        add_breadcrumb(
            message="系统清洁启动脚本",
            category="system_start",
            level="info"
        )
        return capture_message, capture_exception, add_breadcrumb
    except Exception as e:
        print(f"⚠️  Sentry 监控不可用: {e}")
        # 提供空函数作为备选
        def dummy_func(*args, **kwargs):
            pass
        return dummy_func, dummy_func, dummy_func

def start_backend_clean():
    """清洁启动后端服务"""
    print("🚀 启动后端服务...")
    
    try:
        # 使用新的进程环境，直接启动后端
        backend_main = project_root / "selfmastery" / "backend" / "main.py"
        
        # 创建干净的环境变量
        clean_env = os.environ.copy()
        clean_env.update({
            'PYTHONPATH': f"{project_root}:{project_root}/selfmastery",
            'LOG_LEVEL': 'INFO',
            'DEBUG': 'false',
            'APP_NAME': 'SelfMastery B2B Business System',
            'API_HOST': '0.0.0.0',
            'API_PORT': '8000'
        })
        
        # 启动后端进程
        backend_process = subprocess.Popen([
            sys.executable, "-c", f"""
import sys
sys.path.insert(0, '{project_root}')
sys.path.insert(0, '{project_root}/selfmastery')

# 直接导入并启动
import uvicorn
from selfmastery.backend.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
"""
        ], 
        cwd=str(project_root),
        env=clean_env
        )
        
        print("   ✅ 后端进程已启动")
        
        # 等待服务启动
        print("   ⏳ 等待后端服务启动...")
        backend_url = "http://localhost:8000"
        startup_success = False
        
        for i in range(30):  # 等待30秒
            try:
                response = requests.get(f"{backend_url}/health", timeout=2)
                if response.status_code == 200:
                    startup_success = True
                    print(f"   ✅ 后端服务启动成功: {backend_url}")
                    break
            except:
                pass
            
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                print(f"   ⏳ 等待中... ({i}/30 秒)")
        
        if startup_success:
            print(f"   🌐 API 文档: {backend_url}/docs")
            print(f"   📊 健康检查: {backend_url}/health")
            return True, backend_process
        else:
            print("   ❌ 后端服务启动超时")
            backend_process.terminate()
            return False, None
            
    except Exception as e:
        print(f"   ❌ 后端启动失败: {e}")
        return False, None

def start_frontend_clean():
    """清洁启动前端应用"""
    print("\n🎨 启动前端应用...")
    
    try:
        frontend_main = project_root / "selfmastery" / "frontend" / "main.py"
        
        if not frontend_main.exists():
            print("   ⚠️  前端主文件不存在，跳过前端启动")
            return True, None
        
        # 创建干净的环境变量
        clean_env = os.environ.copy()
        clean_env.update({
            'PYTHONPATH': f"{project_root}:{project_root}/selfmastery",
            'QT_QPA_PLATFORM': 'cocoa',  # macOS 特定
        })
        
        # 启动前端进程（在后台）
        frontend_process = subprocess.Popen([
            sys.executable, str(frontend_main)
        ], 
        cwd=str(project_root),
        env=clean_env
        )
        
        print("   ✅ 前端进程已启动")
        
        # 等待一段时间检查进程是否正常运行
        time.sleep(3)
        
        if frontend_process.poll() is None:
            print("   ✅ 前端进程运行正常")
            return True, frontend_process
        else:
            print("   ❌ 前端进程启动后立即退出")
            return False, None
            
    except Exception as e:
        print(f"   ❌ 前端启动失败: {e}")
        return False, None

def main():
    """主函数"""
    print("🎯 SelfMastery B2B业务系统 - 清洁启动工具")
    print("=" * 60)
    
    # 初始化 Sentry
    capture_message, capture_exception, add_breadcrumb = init_sentry()
    
    backend_process = None
    frontend_process = None
    
    try:
        # 1. 启动后端服务
        add_breadcrumb(
            message="启动后端服务",
            category="backend_start",
            level="info"
        )
        
        backend_ok, backend_process = start_backend_clean()
        if backend_ok:
            capture_message("后端服务启动成功", level="info")
        else:
            capture_exception(Exception("后端服务启动失败"))
            print("\n❌ 后端服务启动失败，无法继续")
            return False
        
        # 2. 启动前端应用
        add_breadcrumb(
            message="启动前端应用",
            category="frontend_start",
            level="info"
        )
        
        frontend_ok, frontend_process = start_frontend_clean()
        if frontend_ok:
            capture_message("前端应用启动成功", level="info")
        else:
            print("   ⚠️  前端应用启动失败（不影响后端服务）")
        
        # 3. 显示系统状态
        print("\n" + "="*60)
        print("🎉 SelfMastery B2B业务系统启动完成！")
        print("="*60)
        print("📊 系统状态:")
        print(f"   ✅ 后端服务: 运行中 (http://localhost:8000)")
        print(f"   {'✅' if frontend_ok else '❌'} 前端应用: {'运行中' if frontend_ok else '未运行'}")
        print("\n🔗 快速链接:")
        print("   • API 文档: http://localhost:8000/docs")
        print("   • 健康检查: http://localhost:8000/health")
        print("   • API 根路径: http://localhost:8000/api/v1")
        
        print("\n⚡ 提示:")
        print("   • 按 Ctrl+C 停止系统")
        print("   • 查看日志获取详细信息")
        
        capture_message("系统启动完成", level="info")
        
        # 保持运行，等待用户中断
        print("\n⏳ 系统正在运行，按 Ctrl+C 停止...")
        try:
            while True:
                time.sleep(10)
                # 检查进程状态
                if backend_process and backend_process.poll() is not None:
                    print("⚠️  后端进程已退出")
                    break
        except KeyboardInterrupt:
            print("\n📝 收到停止信号...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 系统启动过程中发生错误: {str(e)}")
        capture_exception(e)
        return False
        
    finally:
        # 清理进程
        print("🧹 正在清理进程...")
        if backend_process:
            backend_process.terminate()
            print("   ✅ 后端进程已停止")
        if frontend_process:
            frontend_process.terminate()
            print("   ✅ 前端进程已停止")
        
        print("👋 系统已完全停止")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 