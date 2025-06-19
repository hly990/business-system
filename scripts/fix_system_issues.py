#!/usr/bin/env python3
"""
系统问题修复脚本
使用 Sentry 监控修复过程
"""
import os
import sys
import subprocess
import importlib.util
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
        capture_message("开始系统问题修复", level="info")
        add_breadcrumb(
            message="系统修复脚本启动",
            category="fix",
            level="info"
        )
        return capture_message, capture_exception, add_breadcrumb
    except Exception as e:
        print(f"警告: Sentry 初始化失败 - {e}")
        # 提供空的函数以避免错误
        def noop(*args, **kwargs):
            pass
        return noop, noop, noop

def check_module_import(module_name, import_path):
    """检查模块是否可以导入"""
    try:
        if '.' in import_path:
            # 处理相对导入
            spec = importlib.util.spec_from_file_location(
                module_name, 
                project_root / import_path.replace('.', '/') + '.py'
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        else:
            __import__(import_path)
        return True, None
    except Exception as e:
        return False, str(e)

def install_missing_dependencies(capture_message, capture_exception, add_breadcrumb):
    """安装缺失的依赖"""
    print("\n=== 修复依赖问题 ===")
    
    try:
        # 检查关键依赖
        critical_deps = [
            'aiosqlite',
            'PyQt6',
            'fastapi',
            'sqlalchemy',
            'sentry-sdk'
        ]
        
        missing_deps = []
        for dep in critical_deps:
            success, error = check_module_import(dep, dep.lower())
            if not success:
                missing_deps.append(dep)
                print(f"❌ 缺少依赖: {dep} - {error}")
            else:
                print(f"✓ 依赖可用: {dep}")
        
        if missing_deps:
            add_breadcrumb(
                message=f"发现缺失依赖: {missing_deps}",
                category="fix",
                level="warning"
            )
            
            # 安装缺失的依赖
            print(f"\n正在安装缺失的依赖: {missing_deps}")
            
            # 更新 pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True)
            
            # 重新安装所有依赖
            requirements_file = project_root / "selfmastery" / "requirements.txt"
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                         check=True)
            
            print("✅ 依赖安装完成")
            capture_message("依赖安装完成", level="info")
            
        else:
            print("✅ 所有关键依赖都可用")
            
    except Exception as e:
        print(f"❌ 依赖安装失败: {e}")
        capture_exception(e)
        return False
    
    return True

def fix_import_issues(capture_message, capture_exception, add_breadcrumb):
    """修复导入问题"""
    print("\n=== 修复导入问题 ===")
    
    try:
        # 检查模型导入
        models_to_check = [
            ('用户模型', 'selfmastery.backend.models.user'),
            ('系统模型', 'selfmastery.backend.models.system'),
            ('流程模型', 'selfmastery.backend.models.process'),
            ('SOP模型', 'selfmastery.backend.models.sop'),
            ('KPI模型', 'selfmastery.backend.models.kpi'),
            ('任务模型', 'selfmastery.backend.models.task'),
        ]
        
        failed_imports = []
        for name, module_path in models_to_check:
            success, error = check_module_import(name, module_path)
            if not success:
                failed_imports.append((name, error))
                print(f"❌ {name}: {error}")
            else:
                print(f"✓ {name}: 导入成功")
        
        if failed_imports:
            add_breadcrumb(
                message=f"导入失败的模块: {[name for name, _ in failed_imports]}",
                category="fix",
                level="error"
            )
            
            # 记录详细错误信息
            for name, error in failed_imports:
                capture_message(f"模块导入失败: {name} - {error}", level="error")
        
        # 检查前端导入
        try:
            from selfmastery.frontend.main import MainWindow
            print("✓ 前端主窗口: 导入成功")
        except Exception as e:
            print(f"❌ 前端主窗口: {e}")
            capture_message(f"前端导入失败: {e}", level="warning")
        
    except Exception as e:
        print(f"❌ 导入检查失败: {e}")
        capture_exception(e)
        return False
    
    return True

def run_system_verification(capture_message, add_breadcrumb):
    """运行系统验证"""
    print("\n=== 重新运行系统验证 ===")
    
    try:
        add_breadcrumb(
            message="开始重新验证系统",
            category="verification",
            level="info"
        )
        
        # 运行系统验证脚本
        result = subprocess.run([sys.executable, "scripts/verify_system.py"], 
                              capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ 系统验证通过")
            capture_message("系统验证通过", level="info")
        else:
            print("⚠️ 系统验证存在问题")
            print(result.stdout)
            if result.stderr:
                print("错误输出:", result.stderr)
            capture_message("系统验证仍存在问题", level="warning")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 系统验证失败: {e}")
        capture_exception(e)
        return False

def main():
    """主修复函数"""
    print("SelfMastery B2B业务系统 - 问题修复工具")
    print("=" * 60)
    
    # 初始化 Sentry
    capture_message, capture_exception, add_breadcrumb = init_sentry()
    
    try:
        # 修复依赖问题
        if not install_missing_dependencies(capture_message, capture_exception, add_breadcrumb):
            print("❌ 依赖修复失败")
            return False
        
        # 修复导入问题
        if not fix_import_issues(capture_message, capture_exception, add_breadcrumb):
            print("❌ 导入修复失败")
            return False
        
        # 重新验证系统
        verification_success = run_system_verification(capture_message, add_breadcrumb)
        
        if verification_success:
            print("\n🎉 系统问题修复完成！")
            capture_message("系统问题修复成功", level="info")
        else:
            print("\n⚠️ 部分问题仍需手动处理")
            capture_message("系统修复部分完成", level="warning")
        
        return verification_success
        
    except Exception as e:
        print(f"\n❌ 修复过程出现错误: {e}")
        capture_exception(e)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 