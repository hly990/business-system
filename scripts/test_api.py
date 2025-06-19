#!/usr/bin/env python3
"""
测试API框架的基本功能
"""
import sys
import os
import asyncio
import httpx
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/selfmastery.db")

async def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🚀 开始测试API端点...")
        
        # 测试根路由
        print("\n1. 测试根路由...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.json()}")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 测试健康检查
        print("\n2. 测试健康检查...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.json()}")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 测试API根路由
        print("\n3. 测试API根路由...")
        try:
            response = await client.get(f"{base_url}/api/v1/")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.json()}")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 测试用户注册
        print("\n4. 测试用户注册...")
        try:
            user_data = {
                "name": "测试用户",
                "email": "test@example.com",
                "password": "test123456",
                "confirm_password": "test123456",
                "role": "user"
            }
            response = await client.post(f"{base_url}/api/v1/auth/register", json=user_data)
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.json()}")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 测试用户登录
        print("\n5. 测试用户登录...")
        try:
            login_data = {
                "email": "test@example.com",
                "password": "test123456"
            }
            response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
            print(f"   状态码: {response.status_code}")
            result = response.json()
            print(f"   响应: {result}")
            
            # 保存访问令牌用于后续测试
            if response.status_code == 200 and result.get("success"):
                access_token = result["data"]["access_token"]
                
                # 测试获取当前用户信息
                print("\n6. 测试获取当前用户信息...")
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(f"{base_url}/api/v1/auth/me", headers=headers)
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
                
                # 测试获取用户列表（需要管理员权限，可能会失败）
                print("\n7. 测试获取用户列表...")
                response = await client.get(f"{base_url}/api/v1/users/", headers=headers)
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
                
        except Exception as e:
            print(f"   错误: {e}")
        
        print("\n✅ API测试完成!")


def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试配置导入
        from selfmastery.config.settings import get_app_settings
        settings = get_app_settings()
        print(f"   ✅ 配置模块导入成功: {settings.APP_NAME}")
        
        # 测试数据模型导入
        from selfmastery.backend.models import User, BusinessSystem
        print("   ✅ 数据模型导入成功")
        
        # 测试服务导入
        from selfmastery.backend.services.auth_service import AuthService
        from selfmastery.backend.services.user_service import UserService
        print("   ✅ 服务模块导入成功")
        
        # 测试API路由导入
        from selfmastery.backend.api import api_router
        print("   ✅ API路由导入成功")
        
        # 测试中间件导入
        from selfmastery.backend.middleware.auth import get_current_user
        from selfmastery.backend.middleware.cors import setup_cors
        print("   ✅ 中间件导入成功")
        
        # 测试工具模块导入
        from selfmastery.backend.utils.exceptions import AuthenticationError
        from selfmastery.backend.utils.responses import APIResponse
        print("   ✅ 工具模块导入成功")
        
        print("✅ 所有模块导入测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """测试数据库连接"""
    print("\n🗄️ 测试数据库连接...")
    
    try:
        from selfmastery.config.database import get_db, engine
        from sqlalchemy import text
        
        # 测试数据库连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ 数据库连接成功")
            
        # 测试数据库会话
        db = next(get_db())
        print("   ✅ 数据库会话创建成功")
        db.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        return False


def main():
    """主函数"""
    print("🧪 SelfMastery B2B API框架测试")
    print("=" * 50)
    
    # 测试模块导入
    if not test_imports():
        print("❌ 模块导入测试失败，退出测试")
        return
    
    # 测试数据库连接
    if not test_database_connection():
        print("❌ 数据库连接测试失败，退出测试")
        return
    
    print("\n🌐 启动API服务器进行端点测试...")
    print("请在另一个终端运行以下命令启动服务器:")
    print("cd selfmastery && python -m backend.main")
    print("\n然后按Enter键继续测试API端点...")
    input()
    
    # 测试API端点
    try:
        asyncio.run(test_api_endpoints())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 测试完成!")


if __name__ == "__main__":
    main()