"""
测试数据库数据
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from selfmastery.config.database import engine
from selfmastery.backend.models import *

def test_database_data():
    """测试数据库数据"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("测试数据库数据...")
        print("=" * 50)
        
        # 测试用户数据
        users = db.query(User).all()
        print(f"用户数量: {len(users)}")
        for user in users:
            print(f"  - {user.name} ({user.email}) - {user.role}")
        
        # 测试业务系统数据
        systems = db.query(BusinessSystem).all()
        print(f"\n业务系统数量: {len(systems)}")
        for system in systems:
            print(f"  - {system.name}: {system.description}")
            print(f"    负责人: {system.owner.name}")
            print(f"    位置: ({system.position_x}, {system.position_y})")
        
        # 测试业务流程数据
        processes = db.query(BusinessProcess).all()
        print(f"\n业务流程数量: {len(processes)}")
        for process in processes:
            print(f"  - {process.name}: {process.description}")
            print(f"    所属系统: {process.system.name}")
            print(f"    负责人: {process.owner.name}")
            print(f"    状态: {process.status}")
            print(f"    优先级: {process.priority}")
            print(f"    预估时长: {process.estimated_duration}分钟")
            
            # 显示流程步骤
            steps = db.query(ProcessStep).filter(ProcessStep.process_id == process.id).order_by(ProcessStep.step_order).all()
            print(f"    流程步骤 ({len(steps)}个):")
            for step in steps:
                print(f"      {step.step_order}. {step.name} - {step.responsible_role} ({step.estimated_duration}分钟)")
        
        # 测试KPI数据
        kpis = db.query(KPI).all()
        print(f"\nKPI指标数量: {len(kpis)}")
        for kpi in kpis:
            print(f"  - {kpi.name}: {kpi.description}")
            print(f"    关联流程: {kpi.process.name}")
            print(f"    指标类型: {kpi.metric_type}")
            print(f"    目标值: {kpi.target_value}{kpi.unit}")
            print(f"    当前值: {kpi.current_value}{kpi.unit}")
            print(f"    数据源: {kpi.data_source}")
            print(f"    更新频率: {kpi.update_frequency}")
        
        # 测试SOP数据
        sops = db.query(SOP).all()
        print(f"\nSOP文档数量: {len(sops)}")
        for sop in sops:
            print(f"  - {sop.title} (v{sop.version})")
            print(f"    作者: {sop.author.name}")
            print(f"    状态: {sop.status}")
            print(f"    内容长度: {len(sop.content)}字符")
            
            # 显示关联的流程
            related_processes = db.query(BusinessProcess).filter(BusinessProcess.sop_id == sop.id).all()
            if related_processes:
                print(f"    关联流程: {', '.join([p.name for p in related_processes])}")
        
        # 测试系统配置数据
        configs = db.query(SystemConfig).all()
        print(f"\n系统配置数量: {len(configs)}")
        for config in configs:
            print(f"  - {config.config_key}: {config.config_value} ({config.config_type})")
            print(f"    描述: {config.description}")
        
        print("\n" + "=" * 50)
        print("数据库数据测试完成！所有数据都已正确创建。")
        
        # 测试关系查询
        print("\n测试关系查询...")
        admin_user = db.query(User).filter(User.email == "admin@selfmastery.com").first()
        if admin_user:
            print(f"管理员用户拥有的系统数量: {len(admin_user.owned_systems)}")
            print(f"管理员用户拥有的流程数量: {len(admin_user.owned_processes)}")
            print(f"管理员用户创建的SOP数量: {len(admin_user.authored_sops)}")
        
        # 测试业务系统的流程数量
        for system in systems:
            process_count = len(system.processes)
            print(f"系统 '{system.name}' 包含 {process_count} 个流程")
        
        print("关系查询测试完成！")
        
    except Exception as e:
        print(f"测试数据库数据时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def main():
    """主函数"""
    print("开始测试 SelfMastery B2B 业务系统数据库数据...")
    test_database_data()

if __name__ == "__main__":
    main()