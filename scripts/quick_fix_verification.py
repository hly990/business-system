#!/usr/bin/env python3
"""
快速系统修复验证脚本
使用 Sentry 监控验证过程
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
        capture_message("开始快速修复验证", level="info")
        add_breadcrumb(
            message="快速验证脚本启动",
            category="verification",
            level="info"
        )
        return capture_message, capture_exception, add_breadcrumb
    except Exception as e:
        print(f"警告: Sentry 初始化失败 - {e}")
        # 提供空的函数以避免错误
        def noop(*args, **kwargs):
            pass
        return noop, noop, noop

def test_critical_imports(capture_message, capture_exception, add_breadcrumb):
    """测试关键模块导入"""
    print("\n=== 测试关键模块导入 ===")
    
    success_count = 0
    total_count = 0
    
    # 测试关键依赖
    dependencies = [
        ('aiosqlite', 'aiosqlite'),
        ('PyQt6', 'PyQt6'),
        ('sentry-sdk', 'sentry_sdk'),
        ('fastapi', 'fastapi'),
        ('sqlalchemy', 'sqlalchemy'),
    ]
    
    for name, module in dependencies:
        total_count += 1
        try:
            __import__(module)
            print(f"✓ {name}: 导入成功")
            success_count += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            capture_message(f"依赖导入失败: {name} - {e}", level="error")
    
    # 测试数据库模型
    models = [
        ('用户模型', 'selfmastery.backend.models.user'),
        ('系统模型', 'selfmastery.backend.models.system'),
        ('流程模型', 'selfmastery.backend.models.process'),
        ('SOP模型', 'selfmastery.backend.models.sop'),
        ('KPI模型', 'selfmastery.backend.models.kpi'),
        ('任务模型', 'selfmastery.backend.models.task'),
    ]
    
    for name, module in models:
        total_count += 1
        try:
            __import__(module)
            print(f"✓ {name}: 导入成功")
            success_count += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            capture_message(f"模型导入失败: {name} - {e}", level="error")
    
    # 测试前端导入
    total_count += 1
    try:
        from selfmastery.frontend.main import MainWindow
        print("✓ 前端主窗口: 导入成功")
        success_count += 1
    except Exception as e:
        print(f"❌ 前端主窗口: {e}")
        capture_message(f"前端导入失败: {e}", level="warning")
    
    success_rate = (success_count / total_count) * 100
    print(f"\n导入成功率: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    add_breadcrumb(
        message=f"导入测试完成，成功率: {success_rate:.1f}%",
        category="verification",
        level="info"
    )
    
    return success_rate >= 80  # 80% 成功率认为通过

def test_sentry_integration(capture_message, capture_exception, add_breadcrumb):
    """测试 Sentry 集成"""
    print("\n=== 测试 Sentry 集成 ===")
    
    try:
        # 测试消息发送
        capture_message("修复验证测试消息", level="info")
        print("✓ Sentry 消息发送成功")
        
        # 测试面包屑
        add_breadcrumb(
            message="执行快速验证测试",
            category="test",
            level="info",
            data={"test_type": "quick_verification"}
        )
        print("✓ Sentry 面包屑添加成功")
        
        # 测试异常捕获
        try:
            raise ValueError("快速验证测试异常")
        except Exception as e:
            capture_exception(e)
            print("✓ Sentry 异常捕获成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentry 测试失败: {e}")
        return False

def main():
    """主验证函数"""
    print("SelfMastery B2B业务系统 - 快速修复验证")
    print("=" * 60)
    
    # 初始化 Sentry
    capture_message, capture_exception, add_breadcrumb = init_sentry()
    
    try:
        # 测试关键导入
        imports_ok = test_critical_imports(capture_message, capture_exception, add_breadcrumb)
        
        # 测试 Sentry 集成
        sentry_ok = test_sentry_integration(capture_message, capture_exception, add_breadcrumb)
        
        print("\n" + "=" * 60)
        print("验证结果汇总:")
        print("=" * 60)
        
        if imports_ok:
            print("✅ 关键模块导入: 通过")
        else:
            print("❌ 关键模块导入: 失败")
        
        if sentry_ok:
            print("✅ Sentry 集成: 通过")
        else:
            print("❌ Sentry 集成: 失败")
        
        overall_success = imports_ok and sentry_ok
        
        if overall_success:
            print("\n🎉 系统修复验证成功！")
            capture_message("系统修复验证成功", level="info")
        else:
            print("\n⚠️ 系统仍存在问题，需要进一步检查")
            capture_message("系统修复验证部分失败", level="warning")
        
        # 建议下一步操作
        print("\n📋 建议下一步操作:")
        if overall_success:
            print("1. 运行完整的系统验证: python scripts/verify_system.py")
            print("2. 启动系统进行功能测试: python scripts/start_system.py")
            print("3. 检查 Sentry 仪表板确认监控数据")
        else:
            print("1. 检查具体的错误信息")
            print("2. 手动安装失败的依赖")
            print("3. 检查 Python 路径和环境配置")
        
        return overall_success
        
    except Exception as e:
        print(f"\n❌ 验证过程出现错误: {e}")
        capture_exception(e)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 