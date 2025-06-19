#!/usr/bin/env python3
"""
后端启动问题修复脚本
使用 Sentry 监控修复过程
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

def init_sentry():
    """初始化 Sentry 监控"""
    try:
        from selfmastery.backend.utils.monitoring import (
            init_sentry_monitoring,
            capture_message,
            capture_exception,
            add_breadcrumb
        )
        
        init_sentry_monitoring()
        capture_message("开始后端启动问题修复", level="info")
        add_breadcrumb(
            message="后端修复脚本启动",
            category="backend_fix",
            level="info"
        )
        return capture_message, capture_exception, add_breadcrumb
    except Exception as e:
        print(f"⚠️  Sentry 初始化失败: {e}")
        # 提供空函数作为备选
        def dummy_func(*args, **kwargs):
            pass
        return dummy_func, dummy_func, dummy_func

def fix_backend_imports():
    """修复后端导入问题"""
    backend_main = project_root / "selfmastery" / "backend" / "main.py"
    
    try:
        with open(backend_main, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复配置导入路径
        fixes = [
            ("from config.settings import get_app_settings", "from selfmastery.config.settings import get_app_settings"),
            ("from config.database import init_async_db", "from selfmastery.config.database import init_async_db"),
        ]
        
        changes_made = []
        for old_import, new_import in fixes:
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made.append(f"修复导入: {old_import}")
        
        if changes_made:
            with open(backend_main, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"后端导入已修复: {', '.join(changes_made)}"
        else:
            return False, "后端main.py中未找到需要修复的导入"
        
    except Exception as e:
        return False, f"修复后端导入失败: {str(e)}"

def fix_startup_script_backend():
    """修复启动脚本中的后端启动方式"""
    start_script = project_root / "scripts" / "start_system.py"
    
    try:
        with open(start_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复后端启动命令，使其从正确的目录启动
        old_pattern = '''self.backend_process = subprocess.Popen([
                sys.executable, str(backend_main)
            ], cwd=str(self.project_root / "selfmastery"))'''
        
        new_pattern = '''self.backend_process = subprocess.Popen([
                sys.executable, str(backend_main)
            ], cwd=str(self.project_root))'''
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "启动脚本后端启动路径已修复"
        else:
            return False, "启动脚本中未找到需要修复的后端启动路径"
        
    except Exception as e:
        return False, f"修复启动脚本失败: {str(e)}"

def test_backend_import():
    """测试后端模块导入"""
    try:
        # 测试配置导入
        from selfmastery.config.settings import get_app_settings
        settings = get_app_settings()
        
        # 测试后端模块导入
        from selfmastery.backend.main import app
        
        return True, "后端模块导入测试通过"
        
    except Exception as e:
        return False, f"后端模块导入测试失败: {str(e)}"

def main():
    """主函数"""
    print("🔧 SelfMastery 后端启动问题修复工具")
    print("=" * 50)
    
    # 初始化 Sentry
    capture_message, capture_exception, add_breadcrumb = init_sentry()
    
    try:
        # 1. 修复后端导入
        print("\n🔧 1. 修复后端导入路径...")
        add_breadcrumb(
            message="修复后端导入路径",
            category="import_fix",
            level="info"
        )
        
        import_ok, import_msg = fix_backend_imports()
        if import_ok:
            print(f"   ✅ {import_msg}")
            capture_message(f"后端导入修复成功: {import_msg}", level="info")
        else:
            print(f"   ❌ {import_msg}")
            # 这可能不是错误，可能已经修复过了
            print(f"   ℹ️  继续下一步验证...")
        
        # 2. 修复启动脚本
        print("\n🔧 2. 修复启动脚本...")
        add_breadcrumb(
            message="修复启动脚本后端启动方式",
            category="startup_fix",
            level="info"
        )
        
        startup_ok, startup_msg = fix_startup_script_backend()
        if startup_ok:
            print(f"   ✅ {startup_msg}")
            capture_message(f"启动脚本修复成功: {startup_msg}", level="info")
        else:
            print(f"   ❌ {startup_msg}")
            # 这可能不是错误，可能已经修复过了
        
        # 3. 测试后端导入
        print("\n✅ 3. 测试后端模块导入...")
        add_breadcrumb(
            message="测试后端模块导入",
            category="import_test",
            level="info"
        )
        
        test_ok, test_msg = test_backend_import()
        if test_ok:
            print(f"   ✅ {test_msg}")
            capture_message(f"后端导入测试成功: {test_msg}", level="info")
        else:
            print(f"   ❌ {test_msg}")
            capture_exception(Exception(f"后端导入测试失败: {test_msg}"))
            return False
        
        # 4. 完成修复
        print("\n🚀 4. 修复完成...")
        add_breadcrumb(
            message="后端启动问题修复完成",
            category="completion",
            level="info"
        )
        
        print("   提示: 现在可以重新运行 'python scripts/start_system.py' 测试启动")
        
        capture_message("后端启动问题修复完成", level="info")
        print("\n🎉 修复完成！后端应该可以正常启动了。")
        return True
        
    except Exception as e:
        print(f"\n❌ 修复过程中发生错误: {str(e)}")
        capture_exception(e)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 