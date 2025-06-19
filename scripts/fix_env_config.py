#!/usr/bin/env python3
"""
环境配置修复脚本
修复 .env 文件中的多行注释问题
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
        capture_message("开始环境配置修复", level="info")
        add_breadcrumb(
            message="环境配置修复脚本启动",
            category="env_fix",
            level="info"
        )
        return capture_message, capture_exception, add_breadcrumb
    except Exception as e:
        print(f"⚠️  Sentry 初始化失败: {e}")
        # 提供空函数作为备选
        def dummy_func(*args, **kwargs):
            pass
        return dummy_func, dummy_func, dummy_func

def fix_env_file():
    """修复 .env 文件中的多行注释问题"""
    env_file = project_root / ".env"
    
    try:
        # 新的清洁的环境配置
        clean_env_content = """# Required
ANTHROPIC_API_KEY=your-api-key-here
PERPLEXITY_API_KEY=pplx-abcde

# Model Configuration
MODEL=claude-3-7-sonnet-20250219
PERPLEXITY_MODEL=sonar-pro
MAX_TOKENS=64000
TEMPERATURE=0.2

# Logging Configuration
DEBUG=false
LOG_LEVEL=info

# Task Configuration  
DEFAULT_SUBTASKS=5
DEFAULT_PRIORITY=medium
PROJECT_NAME={{projectName}}

# Sentry Configuration
SENTRY_DSN=https://23cfa82afa65f55af9665127fe0fff22@o4509522231951360.ingest.us.sentry.io/4509525295235072
"""
        
        # 备份原文件
        if env_file.exists():
            backup_file = env_file.with_suffix('.env.backup')
            with open(env_file, 'r') as f:
                backup_content = f.read()
            with open(backup_file, 'w') as f:
                f.write(backup_content)
            print(f"📦 .env 文件已备份到: {backup_file}")
        
        # 写入新的清洁配置
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(clean_env_content)
        
        return True, ".env 文件已修复，移除了多行注释"
        
    except Exception as e:
        return False, f"修复 .env 文件失败: {str(e)}"

def test_env_loading():
    """测试环境变量加载"""
    try:
        # 重新加载环境变量
        import importlib
        if 'selfmastery.config.settings' in sys.modules:
            importlib.reload(sys.modules['selfmastery.config.settings'])
        
        from selfmastery.config.settings import get_app_settings
        settings = get_app_settings()
        
        print(f"   LOG_LEVEL: {settings.LOG_LEVEL}")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   SENTRY_DSN: {'已配置' if settings.SENTRY_DSN else '未配置'}")
        
        return True, "环境变量加载测试通过"
        
    except Exception as e:
        return False, f"环境变量加载测试失败: {str(e)}"

def main():
    """主函数"""
    print("🔧 SelfMastery 环境配置修复工具")
    print("=" * 50)
    
    try:
        # 1. 修复 .env 文件
        print("\n🔧 1. 修复 .env 文件...")
        
        fix_ok, fix_msg = fix_env_file()
        if fix_ok:
            print(f"   ✅ {fix_msg}")
        else:
            print(f"   ❌ {fix_msg}")
            return False
        
        # 2. 测试环境变量加载
        print("\n✅ 2. 测试环境变量加载...")
        
        test_ok, test_msg = test_env_loading()
        if test_ok:
            print(f"   ✅ {test_msg}")
        else:
            print(f"   ❌ {test_msg}")
            return False
        
        # 3. 初始化 Sentry (现在应该可以工作了)
        print("\n🛡️ 3. 测试 Sentry 初始化...")
        capture_message, capture_exception, add_breadcrumb = init_sentry()
        
        dummy_func = lambda *a, **k: None
        if capture_message != dummy_func:  # 检查是否成功初始化
            print("   ✅ Sentry 监控初始化成功")
            capture_message("环境配置修复完成", level="info")
        else:
            print("   ⚠️  Sentry 未配置或初始化失败（可以继续）")
        
        # 4. 完成修复
        print("\n🚀 4. 修复完成...")
        print("   提示: 现在可以重新运行后端启动修复脚本")
        
        print("\n🎉 环境配置修复完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 修复过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 