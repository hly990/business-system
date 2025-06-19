# SelfMastery B2B业务管理系统

## 项目简介

SelfMastery B2B业务管理系统是一个现代化的企业级业务管理平台，采用前后端分离架构，提供完整的B2B业务解决方案。

### 技术栈

**后端 (Backend)**
- **FastAPI** - 现代、快速的Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **PostgreSQL** - 企业级关系型数据库
- **Redis** - 内存数据库，用于缓存和消息队列
- **Celery** - 分布式任务队列

**前端 (Frontend)**
- **PyQt6** - 跨平台桌面应用程序框架
- **Qt Designer** - 可视化界面设计工具

**开发工具**
- **pytest** - Python测试框架
- **Black** - 代码格式化工具
- **isort** - 导入排序工具
- **Flake8** - 代码质量检查
- **MyPy** - 静态类型检查
- **Sentry** - 错误监控和性能分析

## 项目结构

```
selfmastery/
├── backend/              # FastAPI后端服务
│   ├── api/             # API路由模块
│   ├── models/          # 数据模型
│   ├── services/        # 业务逻辑服务
│   ├── utils/           # 工具函数
│   └── main.py          # 后端应用入口
├── frontend/            # PyQt6桌面应用
│   ├── ui/              # UI组件
│   ├── widgets/         # 自定义控件
│   ├── resources/       # 资源文件（图标、样式等）
│   └── main.py          # 前端应用入口
├── shared/              # 前后端共享代码
├── tests/               # 测试代码
├── config/              # 配置文件
│   ├── database.py      # 数据库配置
│   └── settings.py      # 应用设置
├── requirements.txt     # Python依赖包
├── setup.py            # 安装配置
├── .env.example        # 环境变量模板
└── README.md           # 项目说明文档
```

## 快速开始

### 环境要求

- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd selfmastery
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置数据库连接等信息
   ```
   
   **重要配置项：**
   - `DATABASE_URL` - 数据库连接字符串
   - `SECRET_KEY` - JWT密钥（生产环境必须修改）
   - `SENTRY_DSN` - Sentry监控DSN（可选，用于错误监控）
   - `REDIS_HOST` - Redis服务器地址

5. **初始化数据库**
   ```bash
   # 确保PostgreSQL服务已启动
   # 创建数据库
   createdb selfmastery_db
   ```

6. **启动Redis服务**
   ```bash
   # Windows (如果使用WSL)
   sudo service redis-server start
   
   # macOS
   brew services start redis
   
   # 或直接运行
   redis-server
   ```

### 运行应用

#### 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

- API文档: `http://localhost:8000/docs`
- ReDoc文档: `http://localhost:8000/redoc`

#### 启动前端应用

```bash
cd frontend
python main.py
```

#### 启动Celery任务队列（可选）

```bash
# 启动Celery Worker
celery -A backend.celery_app worker --loglevel=info

# 启动Celery Beat（定时任务）
celery -A backend.celery_app beat --loglevel=info
```

## 开发指南

### 代码规范

项目使用以下工具确保代码质量：

```bash
# 代码格式化
black .

# 导入排序
isort .

# 代码质量检查
flake8 .

# 类型检查
mypy .
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述信息"

# 执行迁移
alembic upgrade head
```

## 功能模块

### 核心功能

- **用户管理** - 用户注册、登录、权限管理
- **企业管理** - 企业信息管理、组织架构
- **产品管理** - 产品信息、库存管理
- **订单管理** - 订单处理、状态跟踪
- **财务管理** - 账单、支付、报表
- **系统设置** - 系统配置、参数管理

### 技术特性

- **异步处理** - 基于FastAPI的异步API
- **任务队列** - Celery异步任务处理
- **缓存机制** - Redis缓存提升性能
- **数据库ORM** - SQLAlchemy对象关系映射
- **API文档** - 自动生成的Swagger文档
- **桌面应用** - PyQt6现代化界面
- **配置管理** - 灵活的环境配置
- **错误监控** - Sentry实时错误跟踪和性能分析
- **日志系统** - 完整的日志记录
- **测试覆盖** - 全面的单元测试

## 监控配置

### Sentry 错误监控

系统集成了 Sentry 错误监控和性能分析，帮助快速定位和解决问题。

1. **配置 Sentry DSN**
   ```bash
   # 在 .env 文件中配置
   SENTRY_DSN="https://your-dsn@sentry.io/project-id"
   SENTRY_ENVIRONMENT="development"  # development, staging, production
   ```

2. **测试 Sentry 集成**
   ```bash
   python scripts/test_sentry.py
   ```

3. **监控功能**
   - 自动捕获未处理的异常
   - API 请求性能监控
   - 数据库查询性能分析
   - 用户操作跟踪
   - 自定义错误和事件

详细配置请参考：[Sentry 监控配置指南](docs/sentry-monitoring-setup.md)

## 部署说明

### 开发环境

使用上述"快速开始"步骤即可搭建开发环境。

### 生产环境

1. **使用Docker部署**
   ```bash
   # 构建镜像
   docker build -t selfmastery-backend ./backend
   docker build -t selfmastery-frontend ./frontend
   
   # 使用docker-compose
   docker-compose up -d
   ```

2. **使用Gunicorn部署后端**
   ```bash
   gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **配置反向代理**
   使用Nginx作为反向代理服务器。

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: [GitHub Repository](https://github.com/selfmastery/b2b-system)
- 问题反馈: [Issues](https://github.com/selfmastery/b2b-system/issues)
- 文档: [Documentation](https://docs.selfmastery.com/b2b-system)

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础框架搭建
- 核心功能模块实现