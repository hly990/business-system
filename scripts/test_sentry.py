#!/usr/bin/env python3
"""
Sentry 监控集成测试脚本
"""
import os
import sys
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

# 设置测试环境变量（如果未配置）
if not os.getenv("SENTRY_DSN"):
    print("警告: SENTRY_DSN 未配置，将跳过 Sentry 测试")
    print("请在 .env 文件中配置 SENTRY_DSN 以启用完整测试")

def test_backend_sentry():
    """测试后端 Sentry 集成"""
    print("\n=== 测试后端 Sentry 集成 ===")
    
    try:
        from selfmastery.backend.utils.monitoring import (
            init_sentry_monitoring,
            capture_exception,
            capture_message,
            set_user_context,
            add_breadcrumb
        )
        
        print("✓ 后端监控模块导入成功")
        
        # 初始化 Sentry
        init_sentry_monitoring()
        print("✓ Sentry 监控初始化完成")
        
        # 测试消息发送
        capture_message("后端 Sentry 测试消息", level="info")
        print("✓ 测试消息发送完成")
        
        # 测试用户上下文
        set_user_context(
            user_id="test_user_123",
            email="test@example.com",
            username="test_user"
        )
        print("✓ 用户上下文设置完成")
        
        # 测试面包屑
        add_breadcrumb(
            message="执行后端测试",
            category="test",
            level="info",
            data={"test_type": "backend", "timestamp": time.time()}
        )
        print("✓ 面包屑添加完成")
        
        # 测试异常捕获
        try:
            raise ValueError("这是一个测试异常（后端）")
        except Exception as e:
            capture_exception(e)
            print("✓ 测试异常捕获完成")
        
        print("✅ 后端 Sentry 集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 后端 Sentry 集成测试失败: {e}")
        return False


def test_frontend_sentry():
    """测试前端 Sentry 集成"""
    print("\n=== 测试前端 Sentry 集成 ===")
    
    try:
        from selfmastery.frontend.services.monitoring import (
            init_frontend_sentry_monitoring,
            capture_frontend_exception,
            capture_frontend_message,
            set_frontend_user_context,
            add_frontend_breadcrumb,
            install_exception_handler
        )
        
        print("✓ 前端监控模块导入成功")
        
        # 初始化前端 Sentry
        init_frontend_sentry_monitoring()
        print("✓ 前端 Sentry 监控初始化完成")
        
        # 安装异常处理器
        install_exception_handler()
        print("✓ 全局异常处理器安装完成")
        
        # 测试消息发送
        capture_frontend_message("前端 Sentry 测试消息", level="info")
        print("✓ 前端测试消息发送完成")
        
        # 测试用户上下文
        set_frontend_user_context(
            user_id="frontend_test_user_123",
            email="frontend_test@example.com",
            username="frontend_test_user"
        )
        print("✓ 前端用户上下文设置完成")
        
        # 测试面包屑
        add_frontend_breadcrumb(
            message="执行前端测试",
            category="test",
            level="info",
            data={"test_type": "frontend", "timestamp": time.time()}
        )
        print("✓ 前端面包屑添加完成")
        
        # 测试异常捕获
        try:
            raise RuntimeError("这是一个测试异常（前端）")
        except Exception as e:
            capture_frontend_exception(e)
            print("✓ 前端测试异常捕获完成")
        
        print("✅ 前端 Sentry 集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 前端 Sentry 集成测试失败: {e}")
        return False


def test_configuration():
    """测试配置"""
    print("\n=== 测试配置 ===")
    
    try:
        from selfmastery.config.settings import get_app_settings, get_pyqt_settings
        
        app_settings = get_app_settings()
        pyqt_settings = get_pyqt_settings()
        
        print(f"✓ 后端配置加载成功")
        print(f"  - SENTRY_DSN: {'已配置' if app_settings.SENTRY_DSN else '未配置'}")
        print(f"  - SENTRY_ENVIRONMENT: {app_settings.SENTRY_ENVIRONMENT}")
        print(f"  - SENTRY_SAMPLE_RATE: {app_settings.SENTRY_SAMPLE_RATE}")
        
        print(f"✓ 前端配置加载成功")
        print(f"  - SENTRY_DSN: {'已配置' if pyqt_settings.SENTRY_DSN else '未配置'}")
        print(f"  - SENTRY_ENVIRONMENT: {pyqt_settings.SENTRY_ENVIRONMENT}")
        print(f"  - SENTRY_SAMPLE_RATE: {pyqt_settings.SENTRY_SAMPLE_RATE}")
        
        if not app_settings.SENTRY_DSN:
            print("⚠️  SENTRY_DSN 未配置，Sentry 功能将不可用")
            print("   请在 .env 文件中配置 SENTRY_DSN")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def test_dependencies():
    """测试依赖"""
    print("\n=== 测试依赖 ===")
    
    try:
        import sentry_sdk
        print(f"✓ sentry-sdk 版本: {sentry_sdk.VERSION}")
        
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        print("✓ FastAPI 集成可用")
        
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        print("✓ SQLAlchemy 集成可用")
        
        from sentry_sdk.integrations.logging import LoggingIntegration
        print("✓ 日志集成可用")
        
        from sentry_sdk.integrations.httpx import HttpxIntegration
        print("✓ HTTPX 集成可用")
        
        print("✅ 所有 Sentry 依赖可用")
        return True
        
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        print("请运行: pip install -r selfmastery/requirements.txt")
        return False


def main():
    """主测试函数"""
    print("SelfMastery B2B业务系统 - Sentry 监控集成测试")
    print("=" * 60)
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_results = []
    
    # 运行测试
    test_results.append(("依赖测试", test_dependencies()))
    test_results.append(("配置测试", test_configuration()))
    test_results.append(("后端集成测试", test_backend_sentry()))
    test_results.append(("前端集成测试", test_frontend_sentry()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Sentry 监控集成成功")
        
        if os.getenv("SENTRY_DSN"):
            print("\n📊 请检查 Sentry 仪表板确认事件是否正确发送")
            print("   网址: https://sentry.io/")
        else:
            print("\n⚠️  要启用完整功能，请配置 SENTRY_DSN 环境变量")
            
        return 0
    else:
        print("❌ 部分测试失败，请检查配置和依赖")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 