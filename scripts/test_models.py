"""
测试数据模型导入
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_model_imports():
    """测试模型导入"""
    try:
        print("测试基础模型导入...")
        from selfmastery.backend.models.base import BaseModel, TimestampMixin, SoftDeleteMixin
        print("✓ 基础模型导入成功")
        
        print("测试用户模型导入...")
        from selfmastery.backend.models.user import User
        print("✓ 用户模型导入成功")
        
        print("测试业务系统模型导入...")
        from selfmastery.backend.models.system import BusinessSystem
        print("✓ 业务系统模型导入成功")
        
        print("测试流程模型导入...")
        from selfmastery.backend.models.process import (
            BusinessProcess, ProcessStep, ProcessConnection, 
            Responsibility, Authorization
        )
        print("✓ 流程模型导入成功")
        
        print("测试SOP模型导入...")
        from selfmastery.backend.models.sop import (
            SOP, SOPVersion, SOPTemplate, IndustryTemplate,
            WizardProgress, AIConversation, SystemConfig
        )
        print("✓ SOP模型导入成功")
        
        print("测试KPI模型导入...")
        from selfmastery.backend.models.kpi import (
            KPI, KPIData, KPIAlert, KPIDashboard, KPITarget
        )
        print("✓ KPI模型导入成功")
        
        print("测试任务模型导入...")
        from selfmastery.backend.models.task import (
            Task, TaskComment, TaskAttachment, TaskTimeLog, Notification
        )
        print("✓ 任务模型导入成功")
        
        print("测试模型包导入...")
        import selfmastery.backend.models
        print("✓ 模型包导入成功")
        
        print("测试数据库配置导入...")
        from selfmastery.config.database import db_settings, Base, engine
        print("✓ 数据库配置导入成功")
        
        print("测试基础服务导入...")
        from selfmastery.backend.services.base_service import BaseService
        print("✓ 基础服务导入成功")
        
        print("\n所有模型导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 模型导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_creation():
    """测试模型实例化"""
    try:
        print("\n测试模型实例化...")
        
        from selfmastery.backend.models.user import User
        user = User(
            name="测试用户",
            email="test@example.com",
            role="user"
        )
        print("✓ 用户模型实例化成功")
        
        from selfmastery.backend.models.system import BusinessSystem
        system = BusinessSystem(
            name="测试系统",
            description="测试描述",
            owner_id=1
        )
        print("✓ 业务系统模型实例化成功")
        
        print("模型实例化测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 模型实例化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试 SelfMastery 数据模型...")
    print("=" * 50)
    
    # 测试导入
    import_success = test_model_imports()
    
    if import_success:
        # 测试实例化
        creation_success = test_model_creation()
        
        if creation_success:
            print("\n" + "=" * 50)
            print("所有测试通过！数据模型实现正确。")
        else:
            print("\n" + "=" * 50)
            print("模型实例化测试失败！")
            sys.exit(1)
    else:
        print("\n" + "=" * 50)
        print("模型导入测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()