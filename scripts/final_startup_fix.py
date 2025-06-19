#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 最终启动修复脚本
完全解决所有问题，使用 Sentry 监控
"""
import os
import sys
import time
import sqlite3
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def init_sentry():
    """尝试初始化 Sentry 监控"""
    try:
        # 直接设置环境变量，避免配置文件问题
        os.environ['SENTRY_DSN'] = 'https://23cfa82afa65f55af9665127fe0fff22@o4509522231951360.ingest.us.sentry.io/4509525295235072'
        os.environ['SENTRY_ENVIRONMENT'] = 'development'
        
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_logging = LoggingIntegration(
            level=20,  # INFO level
            event_level=40  # ERROR level
        )
        
        sentry_sdk.init(
            dsn=os.environ['SENTRY_DSN'],
            integrations=[sentry_logging, SqlalchemyIntegration()],
            traces_sample_rate=0.1,
            environment=os.environ.get('SENTRY_ENVIRONMENT', 'development'),
            release='selfmastery@1.0.0'
        )
        
        sentry_sdk.capture_message("最终启动修复脚本开始", level="info")
        print("   ✅ Sentry 监控初始化成功")
        return True
    except Exception as e:
        print(f"   ⚠️  Sentry 监控初始化失败: {e}")
        return False

def check_and_fix_database():
    """检查并修复数据库"""
    print("🗄️ 检查数据库状态...")
    
    db_path = project_root / "data" / "selfmastery.db"
    
    try:
        # 确保数据目录存在
        db_path.parent.mkdir(exist_ok=True)
        
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查所需的表
        required_tables = [
            'users', 'systems', 'business_processes', 'sops', 'kpis', 'tasks'
        ]
        
        # 获取现有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"   ⚠️  缺少表: {', '.join(missing_tables)}")
            print("   🔧 创建缺少的表...")
            
            # 创建基本表结构
            table_schemas = {
                'users': '''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'systems': '''
                    CREATE TABLE IF NOT EXISTS systems (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        version VARCHAR(50) DEFAULT '1.0.0',
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'business_processes': '''
                    CREATE TABLE IF NOT EXISTS business_processes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        category VARCHAR(50),
                        priority VARCHAR(20) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'sops': '''
                    CREATE TABLE IF NOT EXISTS sops (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(200) NOT NULL,
                        content TEXT,
                        process_id INTEGER,
                        version VARCHAR(20) DEFAULT '1.0',
                        status VARCHAR(20) DEFAULT 'draft',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (process_id) REFERENCES business_processes (id)
                    )
                ''',
                'kpis': '''
                    CREATE TABLE IF NOT EXISTS kpis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        target_value REAL,
                        current_value REAL DEFAULT 0,
                        unit VARCHAR(50),
                        frequency VARCHAR(20) DEFAULT 'monthly',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'tasks': '''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        assigned_to INTEGER,
                        priority VARCHAR(20) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'pending',
                        due_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (assigned_to) REFERENCES users (id)
                    )
                '''
            }
            
            for table in missing_tables:
                if table in table_schemas:
                    cursor.execute(table_schemas[table])
                    print(f"      ✅ 创建表: {table}")
            
            # 提交更改
            conn.commit()
            print("   ✅ 数据库修复完成")
        else:
            print("   ✅ 数据库表检查通过")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 数据库检查/修复失败: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def start_backend_simple():
    """简单方式启动后端"""
    print("🚀 启动后端服务...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env.update({
            'PYTHONPATH': f"{project_root}:{project_root}/selfmastery",
            'LOG_LEVEL': 'INFO',
            'DEBUG': 'false'
        })
        
        # 使用 uvicorn 直接启动
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'selfmastery.backend.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--log-level', 'info'
        ]
        
        print(f"   执行命令: {' '.join(cmd)}")
        
        # 启动进程
        process = subprocess.Popen(
            cmd,
            cwd=str(project_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        print("   ✅ 后端进程已启动")
        
        # 等待服务启动
        startup_success = False
        for i in range(20):
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    startup_success = True
                    print("   ✅ 后端服务启动成功")
                    break
            except:
                pass
            
            time.sleep(1)
            
            # 检查进程是否还在运行
            if process.poll() is not None:
                print("   ❌ 后端进程意外退出")
                # 输出错误信息
                output, _ = process.communicate()
                if output:
                    print(f"   错误输出: {output}")
                return False, None
        
        if startup_success:
            return True, process
        else:
            print("   ❌ 后端服务启动超时")
            process.terminate()
            return False, None
            
    except Exception as e:
        print(f"   ❌ 后端启动失败: {e}")
        return False, None

def main():
    """主函数"""
    print("🎯 SelfMastery B2B业务系统 - 最终启动修复工具")
    print("=" * 60)
    
    try:
        # 1. 初始化 Sentry
        print("\n🛡️ 1. 初始化 Sentry 监控...")
        sentry_ok = init_sentry()
        
        # 2. 检查和修复数据库
        print("\n🗄️ 2. 检查数据库...")
        db_ok = check_and_fix_database()
        if not db_ok:
            print("❌ 数据库修复失败，无法继续")
            return False
        
        # 3. 启动后端服务
        print("\n🚀 3. 启动后端服务...")
        backend_ok, backend_process = start_backend_simple()
        if not backend_ok:
            print("❌ 后端服务启动失败")
            return False
        
        # 4. 显示成功信息
        print("\n" + "="*60)
        print("🎉 SelfMastery B2B业务系统启动成功！")
        print("="*60)
        print("📊 系统状态:")
        print("   ✅ 数据库: 正常")
        print("   ✅ 后端服务: 运行中 (http://localhost:8000)")
        print(f"   {'✅' if sentry_ok else '⚠️ '} Sentry 监控: {'正常' if sentry_ok else '未配置'}")
        
        print("\n🔗 快速链接:")
        print("   • API 文档: http://localhost:8000/docs")
        print("   • 健康检查: http://localhost:8000/health")
        print("   • API 根路径: http://localhost:8000/api/v1")
        
        print("\n⚡ 提示: 按 Ctrl+C 停止系统")
        
        if sentry_ok:
            import sentry_sdk
            sentry_sdk.capture_message("系统启动成功", level="info")
        
        # 保持运行
        try:
            while True:
                time.sleep(10)
                if backend_process.poll() is not None:
                    print("⚠️  后端进程已退出")
                    break
        except KeyboardInterrupt:
            print("\n📝 收到停止信号...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 启动过程中发生错误: {str(e)}")
        if 'sentry_ok' in locals() and sentry_ok:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
        return False
        
    finally:
        # 清理
        if 'backend_process' in locals() and backend_process:
            backend_process.terminate()
            print("🧹 后端进程已停止")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 