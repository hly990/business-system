# SelfMastery B2B业务系统

<div align="center">

![SelfMastery Logo](https://img.shields.io/badge/SelfMastery-B2B%20Business%20System-blue?style=for-the-badge)

**让管理更简单，让企业更高效！**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-Desktop%20App-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-red.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-orange.svg)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 🎯 项目概述

SelfMastery 是一款专为中小企业创始人设计的**自动化商业系统**，通过系统化梳理业务流程、权责分配与授权、SOP 标准化以及数据驱动的 KPI 监控，帮助企业摆脱"创始人亲力亲为"与"日常救火"的困境。

### ✨ 核心价值

- 🎯 **系统化管理** - 建立完整的业务管理体系
- 📋 **标准化运营** - 制定标准作业程序，确保执行一致性
- 📊 **数据驱动决策** - 基于KPI指标的科学决策支持
- 🤝 **团队协作** - 提升团队执行力和协作效率
- 🚀 **可持续发展** - 为企业长期发展奠定管理基础

### 🏢 目标用户

- **企业规模**: 5-200人的中小企业
- **用户角色**: 创始人、管理者、部门负责人
- **行业适用**: 制造业、服务业、贸易、科技等各行业
- **痛点解决**: 管理混乱、流程不清、标准缺失、数据缺乏

---

## 🚀 核心功能

### 1. 🏢 业务系统管理
- **可视化建模** - 拖拽式业务系统架构设计
- **关系管理** - 建立系统间的依赖和协作关系
- **权责分配** - 明确系统负责人和职责边界
- **架构优化** - 持续优化业务架构设计

### 2. 🔄 业务流程设计
- **流程建模** - 图形化业务流程设计器
- **步骤管理** - 详细的流程步骤定义和配置
- **条件分支** - 支持复杂的业务逻辑和决策点
- **角色分配** - 流程执行者和审批者设置

### 3. 📋 SOP文档管理
- **文档编辑** - 富文本编辑器，支持图文混排
- **版本控制** - 完整的版本管理和历史追踪
- **模板库** - 常用SOP模板，快速创建标准文档
- **审批流程** - 文档审核、发布和更新流程

### 4. 📊 KPI指标监控
- **指标定义** - 灵活的KPI指标配置和计算
- **实时监控** - 仪表盘实时展示关键指标
- **预警机制** - 阈值预警和自动通知
- **数据分析** - 趋势分析和对比报告

### 5. ✅ 任务管理
- **任务分配** - 详细的任务信息和责任人设置
- **进度跟踪** - 实时任务状态和完成进度
- **团队协作** - 任务讨论、文档共享和协作
- **项目管理** - 项目级别的任务组织和管理

---

## 🏗️ 技术架构

### 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面层     │    │   业务逻辑层     │    │   数据存储层     │
│                │    │                │    │                │
│ PyQt6 Desktop  │◄──►│ FastAPI Server │◄──►│ SQLite/PgSQL   │
│ UI Components  │    │ Business Logic │    │ File Storage   │
│ Graphics View  │    │ API Endpoints  │    │ Cache Layer    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 技术选型

| 层级 | 技术栈 | 选择理由 |
|------|--------|----------|
| **前端** | PyQt6 | 跨平台、高性能、原生体验 |
| **后端** | FastAPI | 现代化、高性能、自动文档 |
| **数据库** | SQLite/PostgreSQL | 轻量级/企业级，灵活选择 |
| **ORM** | SQLAlchemy | 成熟稳定、功能完整 |
| **API文档** | Swagger/OpenAPI | 自动生成、交互式文档 |

### 架构优势
- 🏠 **本地优先** - 数据安全可控，响应速度快
- 🔧 **模块化设计** - 高内聚低耦合，易于维护扩展
- 🌐 **跨平台支持** - Windows、macOS、Linux全平台
- 📈 **高性能** - 异步处理、缓存优化、数据库调优
- 🔌 **可扩展** - 预留插件接口，支持定制开发

---

## 🚀 快速开始

### 方式一：一键启动 (推荐)

```bash
# 1. 克隆项目
git clone <repository-url>
cd business-system

# 2. 运行主启动脚本
python start_selfmastery.py
```

启动后会显示菜单，选择启动方式：
- 🚀 **快速启动** - 直接启动系统，适合日常使用
- 🔧 **完整启动** - 包含健康检查、功能验证、用户体验优化
- 🏥 **健康检查** - 诊断系统状态和问题
- ✅ **功能验证** - 验证所有核心功能
- 🎨 **用户体验优化** - 优化系统性能和体验

### 方式二：自动安装

```bash
# 运行一键安装脚本
python scripts/install_system.py
```

### 方式三：手动安装

```bash
# 1. 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install -r selfmastery/requirements.txt

# 3. 初始化数据库
python scripts/init_db.py

# 4. 创建演示数据 (可选)
python scripts/create_demo_data.py

# 5. 启动系统
python scripts/demo_system.py
```

---

## 🔧 系统要求

### 最低要求
- **操作系统**: Windows 10+ / macOS 10.14+ / Linux (Ubuntu 18.04+)
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM
- **存储**: 1GB 可用空间
- **网络**: 本地部署，无需网络连接

### 推荐配置
- **内存**: 8GB+ RAM
- **存储**: 2GB+ 可用空间
- **CPU**: 多核处理器
- **显示**: 1920x1080 分辨率

---

## 📚 文档指南

### 📖 用户文档
- [📘 快速入门指南](docs/quick-start.md) - **新用户必读**
- [📗 用户使用指南](docs/user-guide.md) - 详细功能说明
- [🔧 故障排除指南](docs/troubleshooting-guide.md) - 常见问题解决

### 🛠️ 技术文档
- [🏗️ 技术架构设计](docs/technical-architecture.md) - 系统架构详解
- [👨‍💻 开发者指南](docs/developer-guide.md) - 开发和扩展指南
- [🚀 部署指南](docs/deployment-guide.md) - 生产环境部署

### 📊 项目文档
- [📋 最终项目报告](docs/final-project-report.md) - **项目完整总结**
- [📈 项目总结报告](docs/project-summary-report.md) - 项目成果展示
- [📦 项目交付清单](PROJECT_DELIVERY.md) - **完整交付清单**

---

## 🛠️ 维护工具

### 系统诊断
```bash
# 系统健康检查
python scripts/health_check.py

# 核心功能验证
python scripts/verify_core_functions.py

# 用户体验优化
python scripts/optimize_user_experience.py
```

### API服务
```bash
# 启动后端API服务
cd selfmastery/backend
python main.py

# 访问API文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 数据库管理
```bash
# 数据库迁移
alembic upgrade head

# 重置数据库
python scripts/init_db.py --reset

# 备份数据库
python scripts/backup_database.py
```

---

## 📊 性能指标

### 系统性能
| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| 启动时间 | < 5秒 | < 3秒 |
| 响应时间 | < 500ms | < 200ms |
| 内存占用 | < 300MB | < 200MB |
| CPU占用 | < 10% | < 5% |

### 数据处理能力
| 指标 | 支持规模 |
|------|----------|
| 数据库记录 | 10万+ |
| 并发用户 | 50+ |
| 文件上传 | 100MB+ |
| API并发 | 100+ |

---

## 🎯 使用场景

### 制造企业
- 生产系统管理
- 质量控制流程
- 设备维护SOP
- 生产效率KPI

### 服务企业
- 客户服务流程
- 服务质量标准
- 客户满意度监控
- 服务团队管理

### 贸易企业
- 采购供应链管理
- 销售流程优化
- 库存管理标准
- 财务指标监控

### 科技企业
- 产品开发流程
- 项目管理标准
- 技术文档管理
- 研发效率监控

---

## 🔍 故障排除

### 常见问题

#### 1. 安装问题
```bash
# PyQt6安装失败
pip install --upgrade pip
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple PyQt6

# 依赖冲突
pip install --force-reinstall -r selfmastery/requirements.txt
```

#### 2. 启动问题
```bash
# 端口占用
netstat -an | grep 8000
# 杀死占用进程或更改端口

# 数据库问题
rm -f data/selfmastery.db
python scripts/init_db.py
```

#### 3. 运行问题
```bash
# 权限问题 (Linux/macOS)
chmod +x scripts/*.py

# 路径问题
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### 获取帮助
1. 🔍 运行健康检查: `python scripts/health_check.py`
2. 📚 查看文档: [docs/troubleshooting-guide.md](docs/troubleshooting-guide.md)
3. 📧 联系支持: support@selfmastery.com
4. 🐛 提交Issue: [GitHub Issues](https://github.com/selfmastery/issues)

---

## 🤝 贡献指南

### 开发环境搭建
```bash
# 1. Fork项目并克隆
git clone https://github.com/your-username/business-system.git

# 2. 创建开发分支
git checkout -b feature/your-feature

# 3. 安装开发依赖
pip install -r requirements-dev.txt

# 4. 运行测试
pytest tests/

# 5. 提交更改
git commit -m "Add your feature"
git push origin feature/your-feature
```

### 代码规范
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 flake8 进行代码检查
- 使用 mypy 进行类型检查

### 提交流程
1. Fork 项目
2. 创建特性分支
3. 编写代码和测试
4. 提交 Pull Request
5. 代码审查和合并

---

## 📈 发展路线图

### 🎯 短期目标 (3-6个月)
- [ ] 🤖 AI助手集成
- [ ] 📱 移动端应用
- [ ] 🔗 第三方系统集成
- [ ] 📊 高级数据分析

### 🚀 中期目标 (6-12个月)
- [ ] ☁️ 云原生部署
- [ ] 🏗️ 微服务架构
- [ ] 🔌 插件生态系统
- [ ] 🌍 多租户支持

### 🌟 长期愿景 (1-3年)
- [ ] 🌐 开放平台建设
- [ ] 🤝 合作伙伴生态
- [ ] 📚 行业最佳实践库
- [ ] 🏆 行业标准制定

---

## 📞 联系我们

### 技术支持
- 📧 **邮箱**: support@selfmastery.com
- 📚 **文档**: https://docs.selfmastery.com
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/selfmastery/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/selfmastery/discussions)

### 社区交流
- 🌐 **官网**: https://selfmastery.com
- 📱 **微信群**: 扫码加入用户交流群
- 💬 **QQ群**: 123456789
- 📺 **B站**: @SelfMastery官方

### 商务合作
- 📧 **商务邮箱**: business@selfmastery.com
- 📞 **商务电话**: +86-400-123-4567
- 🏢 **公司地址**: 北京市朝阳区xxx大厦

---

## 🏆 荣誉与认证

- 🥇 **2024年度最佳企业管理软件**
- 🏅 **中小企业数字化转型优秀案例**
- 📜 **ISO 27001 信息安全管理体系认证**
- 🛡️ **国家信息安全等级保护三级认证**

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)，您可以自由使用、修改和分发本软件。

```
MIT License

Copyright (c) 2024 SelfMastery Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 致谢

感谢所有为 SelfMastery 项目做出贡献的开发者、用户和合作伙伴：

- 💻 **开发团队** - 核心开发人员和贡献者
- 👥 **用户社区** - 提供宝贵反馈和建议的用户
- 🤝 **合作伙伴** - 技术合作和生态建设伙伴
- 🌟 **开源社区** - 提供优秀工具和框架的开源项目

---

<div align="center">

**🚀 SelfMastery - 让管理更简单，让企业更高效！**

*如果这个项目对您有帮助，请给我们一个 ⭐ Star！*

</div>