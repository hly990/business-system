#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 系统验证脚本
验证系统的基本功能和完整性
"""

import os
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "selfmastery"))

def log(message: str, level: str = "INFO"):
    """记录日志"""
    print(f"[{level}] {message}")

def verify_project_structure():
    """验证项目结构"""
    log("验证项目结构", "INFO")
    
    required_files = [
        "selfmastery/backend/main.py",
        "selfmastery/frontend/main.py",
        "selfmastery/config/settings.py",
        "selfmastery/backend/models/user.py",
        "selfmastery/backend/models/system.py",
        "selfmastery/backend/models/process.py",
        "selfmastery/backend/models/sop.py",
        "selfmastery/backend/models/kpi.py",
        "selfmastery/backend/models/task.py",
        "scripts/init_db.py",
        "scripts/create_demo_data.py",
        "scripts/start_system.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            log(f"✓ {file_path}", "INFO")
        else:
            log(f"✗ {file_path} 不存在", "ERROR")
            missing_files.append(file_path)
    
    if missing_files:
        log(f"缺少 {len(missing_files)} 个文件", "ERROR")
        return False
    else:
        log("项目结构完整", "INFO")
        return True

def verify_database():
    """验证数据库"""
    log("验证数据库", "INFO")
    
    db_path = project_root / "data" / "selfmastery.db"
    if not db_path.exists():
        log("数据库文件不存在", "ERROR")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查表是否存在
        tables = ["users", "business_systems", "business_processes", "sops", "kpis", "tasks"]
        existing_tables = []
        
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                existing_tables.append(table)
                log(f"✓ 表 {table} 存在", "INFO")
            else:
                log(f"✗ 表 {table} 不存在", "ERROR")
        
        # 检查数据
        for table in existing_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            log(f"  - {table}: {count} 条记录", "INFO")
        
        conn.close()
        
        if len(existing_tables) == len(tables):
            log("数据库结构完整", "INFO")
            return True
        else:
            log(f"缺少 {len(tables) - len(existing_tables)} 个表", "ERROR")
            return False
            
    except Exception as e:
        log(f"数据库验证失败: {str(e)}", "ERROR")
        return False

def verify_python_imports():
    """验证Python模块导入"""
    log("验证Python模块导入", "INFO")
    
    # 测试后端模块
    backend_modules = [
        ("config.settings", "配置模块"),
        ("backend.models.user", "用户模型"),
        ("backend.models.system", "系统模型"),
        ("backend.models.process", "流程模型"),
        ("backend.models.sop", "SOP模型"),
        ("backend.models.kpi", "KPI模型"),
        ("backend.models.task", "任务模型")
    ]
    
    success_count = 0
    for module_name, description in backend_modules:
        try:
            __import__(module_name)
            log(f"✓ {description}: 导入成功", "INFO")
            success_count += 1
        except Exception as e:
            log(f"✗ {description}: 导入失败 - {str(e)}", "ERROR")
    
    # 测试前端模块（可选，因为可能缺少PyQt5）
    try:
        from frontend.ui.main_window import MainWindow
        log("✓ 前端主窗口: 导入成功", "INFO")
        success_count += 1
    except Exception as e:
        log(f"○ 前端主窗口: 导入失败 - {str(e)} (可能缺少PyQt5)", "WARNING")
    
    log(f"模块导入成功率: {success_count}/{len(backend_modules) + 1}", "INFO")
    return success_count >= len(backend_modules)

def verify_configuration():
    """验证配置文件"""
    log("验证配置文件", "INFO")
    
    try:
        from config.settings import settings
        
        # 检查关键配置
        config_items = [
            ("DATABASE_URL", settings.DATABASE_URL),
            ("SECRET_KEY", settings.SECRET_KEY),
            ("ACCESS_TOKEN_EXPIRE_MINUTES", settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ]
        
        for key, value in config_items:
            if value:
                log(f"✓ {key}: 已配置", "INFO")
            else:
                log(f"✗ {key}: 未配置", "ERROR")
        
        log("配置验证完成", "INFO")
        return True
        
    except Exception as e:
        log(f"配置验证失败: {str(e)}", "ERROR")
        return False

def verify_scripts():
    """验证脚本文件"""
    log("验证脚本文件", "INFO")
    
    scripts = [
        "scripts/init_db.py",
        "scripts/create_demo_data.py",
        "scripts/start_system.py",
        "scripts/test_integration.py",
        "scripts/test_frontend.py",
        "scripts/test_backend.py"
    ]
    
    executable_count = 0
    for script in scripts:
        script_path = project_root / script
        if script_path.exists():
            if os.access(script_path, os.R_OK):
                log(f"✓ {script}: 可读", "INFO")
                executable_count += 1
            else:
                log(f"✗ {script}: 不可读", "ERROR")
        else:
            log(f"✗ {script}: 不存在", "ERROR")
    
    log(f"脚本可用性: {executable_count}/{len(scripts)}", "INFO")
    return executable_count == len(scripts)

def verify_documentation():
    """验证文档文件"""
    log("验证文档文件", "INFO")
    
    docs = [
        "docs/technical-architecture.md",
        "docs/user-guide.md",
        "docs/developer-guide.md",
        "docs/deployment-guide.md",
        "docs/troubleshooting-guide.md",
        "docs/project-summary-report.md"
    ]
    
    doc_count = 0
    for doc in docs:
        doc_path = project_root / doc
        if doc_path.exists():
            log(f"✓ {doc}: 存在", "INFO")
            doc_count += 1
        else:
            log(f"✗ {doc}: 不存在", "ERROR")
    
    log(f"文档完整性: {doc_count}/{len(docs)}", "INFO")
    return doc_count == len(docs)

def generate_verification_report():
    """生成验证报告"""
    log("生成系统验证报告", "INFO")
    
    # 运行所有验证
    results = {
        "项目结构": verify_project_structure(),
        "数据库": verify_database(),
        "Python模块": verify_python_imports(),
        "配置文件": verify_configuration(),
        "脚本文件": verify_scripts(),
        "文档文件": verify_documentation()
    }
    
    # 生成报告
    print("\n" + "="*60)
    print("SelfMastery B2B业务系统 - 验证报告")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"验证时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"验证项目: {total}")
    print(f"通过项目: {passed}")
    print(f"失败项目: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")
    print("="*60)
    
    for item, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} {item}")
    
    print("="*60)
    
    # 系统状态评估
    if passed == total:
        print("🎉 系统验证完全通过！系统已准备就绪。")
        status = "优秀"
    elif passed >= total * 0.8:
        print("✅ 系统验证基本通过，存在少量问题需要解决。")
        status = "良好"
    elif passed >= total * 0.6:
        print("⚠️  系统验证部分通过，存在一些问题需要修复。")
        status = "一般"
    else:
        print("❌ 系统验证失败较多，需要重点修复问题。")
        status = "需要改进"
    
    print(f"系统状态: {status}")
    print("="*60)
    
    # 保存报告到文件
    report_data = {
        "verification_time": __import__('datetime').datetime.now().isoformat(),
        "total_checks": total,
        "passed_checks": passed,
        "pass_rate": passed/total*100,
        "status": status,
        "results": results
    }
    
    import json
    report_file = project_root / "system_verification_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    log(f"验证报告已保存到: {report_file}", "INFO")
    
    return passed == total

def main():
    """主函数"""
    print("SelfMastery B2B业务系统 - 系统验证工具")
    print("="*50)
    
    success = generate_verification_report()
    
    if success:
        print("\n🎉 恭喜！系统验证完全通过。")
        print("您可以继续使用以下命令启动系统：")
        print("  python scripts/start_system.py")
        sys.exit(0)
    else:
        print("\n⚠️  系统验证发现问题，请根据上述报告进行修复。")
        sys.exit(1)

if __name__ == "__main__":
    main()