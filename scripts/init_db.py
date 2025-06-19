"""
数据库初始化脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from selfmastery.config.database import db_settings, Base
from selfmastery.backend.models import *


def create_database():
    """创建数据库和表"""
    print("正在创建数据库...")
    
    # 确保数据目录存在
    if db_settings.DB_TYPE == "sqlite":
        db_path = Path(db_settings.DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建数据库引擎
    engine = create_engine(db_settings.database_url, echo=True)
    
    # 如果是 SQLite，设置性能优化参数
    if db_settings.DB_TYPE == "sqlite":
        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=10000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))
            conn.execute(text("PRAGMA mmap_size=268435456"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    
    return engine


def create_initial_data(engine):
    """创建初始数据"""
    print("正在创建初始数据...")
    
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 创建默认管理员用户
        admin_user = User(
            name="系统管理员",
            email="admin@selfmastery.com",
            role="admin",
            timezone="Asia/Shanghai",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"创建管理员用户: {admin_user.name} (ID: {admin_user.id})")
        
        # 创建示例业务系统
        sample_system = BusinessSystem(
            name="销售管理系统",
            description="负责客户开发、销售跟进、合同管理等销售相关业务",
            owner_id=admin_user.id,
            position_x=100.0,
            position_y=100.0,
            color="#1E40AF"
        )
        db.add(sample_system)
        db.commit()
        db.refresh(sample_system)
        print(f"创建示例系统: {sample_system.name} (ID: {sample_system.id})")
        
        # 创建示例业务流程
        sample_process = BusinessProcess(
            system_id=sample_system.id,
            name="客户开发流程",
            description="从潜在客户识别到成交的完整流程",
            owner_id=admin_user.id,
            status="active",
            priority=1,
            estimated_duration=480,  # 8小时
            position_x=200.0,
            position_y=200.0
        )
        db.add(sample_process)
        db.commit()
        db.refresh(sample_process)
        print(f"创建示例流程: {sample_process.name} (ID: {sample_process.id})")
        
        # 创建流程步骤
        steps = [
            {
                "step_order": 1,
                "name": "潜在客户识别",
                "description": "通过各种渠道识别潜在客户",
                "responsible_role": "销售代表",
                "estimated_duration": 60
            },
            {
                "step_order": 2,
                "name": "初步接触",
                "description": "与潜在客户建立初步联系",
                "responsible_role": "销售代表",
                "estimated_duration": 30
            },
            {
                "step_order": 3,
                "name": "需求分析",
                "description": "深入了解客户需求和痛点",
                "responsible_role": "销售代表",
                "estimated_duration": 120
            },
            {
                "step_order": 4,
                "name": "方案制定",
                "description": "根据客户需求制定解决方案",
                "responsible_role": "方案经理",
                "estimated_duration": 180
            },
            {
                "step_order": 5,
                "name": "商务谈判",
                "description": "与客户进行价格和条款谈判",
                "responsible_role": "销售经理",
                "estimated_duration": 60
            },
            {
                "step_order": 6,
                "name": "合同签署",
                "description": "完成合同签署和款项收取",
                "responsible_role": "销售经理",
                "estimated_duration": 30
            }
        ]
        
        for step_data in steps:
            step = ProcessStep(
                process_id=sample_process.id,
                **step_data
            )
            db.add(step)
        
        db.commit()
        print(f"创建了 {len(steps)} 个流程步骤")
        
        # 创建示例KPI
        sample_kpi = KPI(
            process_id=sample_process.id,
            name="客户转化率",
            description="从潜在客户到成交客户的转化率",
            metric_type="percentage",
            target_value=25.0,
            current_value=0.0,
            unit="%",
            data_source="manual",
            update_frequency="weekly"
        )
        db.add(sample_kpi)
        db.commit()
        db.refresh(sample_kpi)
        print(f"创建示例KPI: {sample_kpi.name} (ID: {sample_kpi.id})")
        
        # 创建示例SOP
        sample_sop = SOP(
            title="客户开发标准操作程序",
            content="""# 客户开发标准操作程序

## 1. 目的
规范客户开发流程，提高销售效率和成功率。

## 2. 适用范围
适用于所有销售人员的客户开发活动。

## 3. 操作步骤

### 3.1 潜在客户识别
- 通过市场调研识别目标客户群体
- 利用网络资源搜集客户信息
- 参加行业展会和活动
- 客户推荐和转介绍

### 3.2 初步接触
- 电话联系或邮件沟通
- 简要介绍公司和产品
- 了解客户基本情况
- 预约正式会面时间

### 3.3 需求分析
- 深入了解客户业务现状
- 识别客户痛点和需求
- 评估客户预算和决策流程
- 确定关键决策人

### 3.4 方案制定
- 根据客户需求定制解决方案
- 准备详细的产品演示
- 制定价格策略
- 准备相关案例和证明材料

### 3.5 商务谈判
- 正式提交解决方案
- 进行产品演示和答疑
- 商讨价格和合作条款
- 处理客户异议

### 3.6 合同签署
- 准备正式合同文件
- 与客户确认最终条款
- 完成合同签署
- 安排后续服务对接

## 4. 注意事项
- 每个步骤都要做好记录
- 及时更新客户信息
- 遵守公司价格政策
- 保护客户商业机密
""",
            version="1.0",
            author_id=admin_user.id,
            status="approved"
        )
        db.add(sample_sop)
        db.commit()
        db.refresh(sample_sop)
        print(f"创建示例SOP: {sample_sop.title} (ID: {sample_sop.id})")
        
        # 关联SOP到流程
        sample_process.sop_id = sample_sop.id
        db.commit()
        
        # 创建系统配置
        configs = [
            {
                "config_key": "system_name",
                "config_value": "SelfMastery B2B业务系统",
                "config_type": "string",
                "description": "系统名称"
            },
            {
                "config_key": "system_version",
                "config_value": "1.0.0",
                "config_type": "string",
                "description": "系统版本"
            },
            {
                "config_key": "default_timezone",
                "config_value": "Asia/Shanghai",
                "config_type": "string",
                "description": "默认时区"
            },
            {
                "config_key": "max_file_size",
                "config_value": "10485760",
                "config_type": "integer",
                "description": "最大文件上传大小（字节）"
            }
        ]
        
        for config_data in configs:
            config = SystemConfig(**config_data)
            db.add(config)
        
        db.commit()
        print(f"创建了 {len(configs)} 个系统配置项")
        
        print("初始数据创建完成！")
        
    except Exception as e:
        print(f"创建初始数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """主函数"""
    print("开始初始化 SelfMastery B2B 业务系统数据库...")
    
    try:
        # 创建数据库和表
        engine = create_database()
        
        # 创建初始数据
        create_initial_data(engine)
        
        print("\n数据库初始化完成！")
        print("=" * 50)
        print("默认管理员账户:")
        print("邮箱: admin@selfmastery.com")
        print("角色: admin")
        print("=" * 50)
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()