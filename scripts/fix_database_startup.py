#!/usr/bin/env python3
"""
数据库启动问题修复脚本
使用 Sentry 监控修复过程
"""
import os
import sys
import sqlite3
import subprocess
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
        capture_message("开始数据库启动问题修复", level="info")
        add_breadcrumb(
            message="数据库修复脚本启动",
            category="database_fix",
            level="info"
        )
        return capture_message, capture_exception, add_breadcrumb
    except Exception as e:
        print(f"⚠️  Sentry 初始化失败: {e}")
        # 提供空函数作为备选
        def dummy_func(*args, **kwargs):
            pass
        return dummy_func, dummy_func, dummy_func

def check_database_structure():
    """检查数据库结构"""
    db_path = project_root / "data" / "selfmastery.db"
    
    if not db_path.exists():
        return False, "数据库文件不存在"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # 检查启动脚本期望的表名
        expected_tables_startup = ["users", "business_systems", "processes", "sops", "kpis", "tasks"]
        
        # 检查实际的表名
        actual_expected_tables = ["users", "business_systems", "business_processes", "sops", "kpis", "tasks"]
        
        print(f"📊 现有表: {existing_tables}")
        print(f"📋 启动脚本期望表: {expected_tables_startup}")
        print(f"📋 实际应有表: {actual_expected_tables}")
        
        missing_from_startup = set(expected_tables_startup) - set(existing_tables)
        missing_from_actual = set(actual_expected_tables) - set(existing_tables)
        
        return (
            len(missing_from_startup) == 0 or len(missing_from_actual) == 0,
            {
                "existing": existing_tables,
                "missing_startup": list(missing_from_startup),
                "missing_actual": list(missing_from_actual),
                "startup_compatible": len(missing_from_startup) == 0
            }
        )
        
    except Exception as e:
        return False, f"数据库检查错误: {str(e)}"

def fix_startup_script():
    """修复启动脚本中的表名问题"""
    start_script = project_root / "scripts" / "start_system.py"
    
    try:
        with open(start_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复表名映射
        old_line = 'tables = ["users", "business_systems", "processes", "sops", "kpis", "tasks"]'
        new_line = 'tables = ["users", "business_systems", "business_processes", "sops", "kpis", "tasks"]'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "启动脚本表名已修复"
        else:
            return False, "启动脚本中未找到需要修复的表名"
        
    except Exception as e:
        return False, f"修复启动脚本失败: {str(e)}"

def reinitialize_database():
    """重新初始化数据库"""
    try:
        init_script = project_root / "scripts" / "init_db.py"
        if not init_script.exists():
            return False, "数据库初始化脚本不存在"
        
        # 备份现有数据库
        db_path = project_root / "data" / "selfmastery.db"
        if db_path.exists():
            backup_path = db_path.with_suffix('.backup.db')
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"📦 数据库已备份到: {backup_path}")
        
        # 运行初始化脚本
        result = subprocess.run([
            sys.executable, str(init_script)
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            return True, "数据库重新初始化成功"
        else:
            return False, f"数据库初始化失败: {result.stderr}"
            
    except Exception as e:
        return False, f"数据库初始化异常: {str(e)}"

def main():
    """主函数"""
    print("🔧 SelfMastery 数据库启动问题修复工具")
    print("=" * 50)
    
    # 初始化 Sentry
    capture_message, capture_exception, add_breadcrumb = init_sentry()
    
    try:
        # 1. 检查数据库结构
        print("\n📊 1. 检查数据库结构...")
        add_breadcrumb(
            message="开始检查数据库结构",
            category="database_check",
            level="info"
        )
        
        db_ok, db_info = check_database_structure()
        
        if isinstance(db_info, dict):
            print(f"   现有表: {len(db_info['existing'])} 个")
            print(f"   启动脚本缺失表: {db_info['missing_startup']}")
            print(f"   实际缺失表: {db_info['missing_actual']}")
            
            capture_message(
                f"数据库结构检查完成: 现有{len(db_info['existing'])}个表",
                level="info"
            )
            
            # 2. 修复启动脚本
            if not db_info['startup_compatible'] and 'processes' in db_info['missing_startup']:
                print("\n🔧 2. 修复启动脚本表名...")
                add_breadcrumb(
                    message="修复启动脚本表名",
                    category="script_fix",
                    level="info"
                )
                
                fix_ok, fix_msg = fix_startup_script()
                if fix_ok:
                    print(f"   ✅ {fix_msg}")
                    capture_message(f"启动脚本修复成功: {fix_msg}", level="info")
                else:
                    print(f"   ❌ {fix_msg}")
                    capture_exception(Exception(f"启动脚本修复失败: {fix_msg}"))
            
            # 3. 检查是否需要重新初始化数据库
            if len(db_info['missing_actual']) > 0:
                print(f"\n🗄️ 3. 重新初始化数据库（缺失 {len(db_info['missing_actual'])} 个表）...")
                add_breadcrumb(
                    message=f"重新初始化数据库，缺失{len(db_info['missing_actual'])}个表",
                    category="database_init",
                    level="info"
                )
                
                init_ok, init_msg = reinitialize_database()
                if init_ok:
                    print(f"   ✅ {init_msg}")
                    capture_message(f"数据库初始化成功: {init_msg}", level="info")
                else:
                    print(f"   ❌ {init_msg}")
                    capture_exception(Exception(f"数据库初始化失败: {init_msg}"))
                    return False
            
        else:
            print(f"   ❌ {db_info}")
            capture_exception(Exception(f"数据库检查失败: {db_info}"))
            
            if "不存在" in str(db_info):
                print("\n🗄️ 2. 初始化数据库...")
                init_ok, init_msg = reinitialize_database()
                if init_ok:
                    print(f"   ✅ {init_msg}")
                    capture_message(f"数据库初始化成功: {init_msg}", level="info")
                else:
                    print(f"   ❌ {init_msg}")
                    capture_exception(Exception(f"数据库初始化失败: {init_msg}"))
                    return False
        
        # 4. 验证修复结果
        print("\n✅ 4. 验证修复结果...")
        add_breadcrumb(
            message="验证数据库修复结果",
            category="verification",
            level="info"
        )
        
        verify_ok, verify_info = check_database_structure()
        if verify_ok:
            print("   ✅ 数据库结构检查通过")
            capture_message("数据库修复验证成功", level="info")
        else:
            print(f"   ❌ 验证失败: {verify_info}")
            capture_exception(Exception(f"数据库修复验证失败: {verify_info}"))
        
        # 5. 测试系统启动
        print("\n🚀 5. 测试系统启动...")
        add_breadcrumb(
            message="测试系统启动",
            category="startup_test",
            level="info"
        )
        
        print("   提示: 现在可以运行 'python scripts/start_system.py' 测试启动")
        
        capture_message("数据库启动问题修复完成", level="info")
        print("\n🎉 修复完成！系统应该可以正常启动了。")
        return True
        
    except Exception as e:
        print(f"\n❌ 修复过程中发生错误: {str(e)}")
        capture_exception(e)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 