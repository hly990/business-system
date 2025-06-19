# Sentry 监控配置指南

SelfMastery B2B业务系统已集成 Sentry 监控，用于实时跟踪错误和性能问题。

## 快速开始

### 1. 安装依赖

Sentry SDK 已包含在 `requirements.txt` 中：

```bash
pip install -r selfmastery/requirements.txt
```

### 2. 创建 Sentry 项目

1. 访问 [Sentry.io](https://sentry.io/)
2. 创建账户或登录
3. 创建新项目：
   - 选择 Python 平台
   - 为后端和前端分别创建项目（推荐）或使用同一个项目
4. 获取 DSN（Data Source Name）

### 3. 配置环境变量

在项目根目录创建 `.env` 文件并添加以下配置：

```bash
# Sentry监控配置
SENTRY_DSN="https://your-dsn@sentry.io/project-id"
SENTRY_ENVIRONMENT="development"  # development, staging, production
SENTRY_SAMPLE_RATE=1.0  # 错误采样率 (0.0-1.0)
SENTRY_TRACES_SAMPLE_RATE=0.1  # 性能监控采样率
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 性能分析采样率
SENTRY_SEND_DEFAULT_PII=False  # 是否发送个人身份信息
SENTRY_ATTACH_STACKTRACE=True  # 是否附加堆栈跟踪
```

### 4. 重启应用

配置完成后重启后端和前端应用以使配置生效。

## 配置说明

### 环境配置

- **development**: 开发环境，建议 `SAMPLE_RATE=1.0` 捕获所有错误
- **staging**: 测试环境，建议 `SAMPLE_RATE=1.0`
- **production**: 生产环境，建议 `SAMPLE_RATE` 根据流量调整（0.1-1.0）

### 采样率配置

- **SENTRY_SAMPLE_RATE**: 错误事件采样率
  - `1.0`: 捕获所有错误（推荐开发环境）
  - `0.1`: 捕获 10% 的错误（适合高流量生产环境）

- **SENTRY_TRACES_SAMPLE_RATE**: 性能监控采样率
  - `0.1`: 监控 10% 的请求性能（推荐）
  - `1.0`: 监控所有请求（仅适合低流量环境）

- **SENTRY_PROFILES_SAMPLE_RATE**: 性能分析采样率
  - `0.1`: 分析 10% 的请求（推荐）

### 隐私配置

- **SENTRY_SEND_DEFAULT_PII**: 是否发送个人身份信息
  - `False`: 不发送用户 IP、用户 ID 等敏感信息（推荐）
  - `True`: 发送完整的用户信息（仅适合内部系统）

## 监控功能

### 后端监控

已集成以下监控功能：

- **异常捕获**: 自动捕获所有未处理的异常
- **性能监控**: 监控 API 请求性能
- **数据库监控**: 监控 SQLAlchemy 查询性能
- **HTTP 请求监控**: 监控外部 HTTP 请求
- **自定义标签**: 
  - `service: selfmastery-backend`
  - `version: [应用版本]`

### 前端监控

已集成以下监控功能：

- **异常捕获**: 捕获 PyQt 应用中的未处理异常
- **用户操作跟踪**: 记录关键用户操作
- **性能监控**: 监控 UI 响应性能
- **自定义标签**:
  - `service: selfmastery-frontend`
  - `platform: PyQt6`
  - `python_version: [Python版本]`

## 使用方法

### 手动发送事件

```python
from selfmastery.backend.utils.monitoring import capture_exception, capture_message

# 捕获异常
try:
    risky_operation()
except Exception as e:
    capture_exception(e)

# 发送消息
capture_message("重要事件发生", level="info")
```

### 设置用户上下文

```python
from selfmastery.backend.utils.monitoring import set_user_context

set_user_context(
    user_id="12345",
    email="user@example.com",
    username="username"
)
```

### 添加面包屑

```python
from selfmastery.backend.utils.monitoring import add_breadcrumb

add_breadcrumb(
    message="用户执行了重要操作",
    category="user_action",
    level="info",
    data={"action": "create_order", "order_id": "12345"}
)
```

## 最佳实践

### 1. 环境隔离

为不同环境使用不同的 Sentry 项目或至少不同的环境标签：

```bash
# 开发环境
SENTRY_ENVIRONMENT="development"

# 测试环境
SENTRY_ENVIRONMENT="staging"

# 生产环境
SENTRY_ENVIRONMENT="production"
```

### 2. 采样率调优

根据流量和预算调整采样率：

```bash
# 高流量生产环境
SENTRY_SAMPLE_RATE=0.1
SENTRY_TRACES_SAMPLE_RATE=0.01

# 低流量或开发环境
SENTRY_SAMPLE_RATE=1.0
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### 3. 过滤敏感信息

确保不发送敏感信息：

```bash
SENTRY_SEND_DEFAULT_PII=False
```

### 4. 监控关键业务流程

在关键业务流程中添加面包屑和自定义标签：

```python
# 在订单处理流程中
add_breadcrumb("开始处理订单", category="business", data={"order_id": order_id})
```

## 故障排除

### 1. DSN 配置错误

如果看到 "SENTRY_DSN 未配置" 警告：
- 检查 `.env` 文件是否存在
- 确认 DSN 格式正确
- 重启应用

### 2. 网络连接问题

如果事件无法发送到 Sentry：
- 检查网络连接
- 确认防火墙设置
- 检查 Sentry 服务状态

### 3. 采样率过低

如果事件数量太少：
- 增加 `SENTRY_SAMPLE_RATE`
- 检查错误过滤规则

### 4. 性能影响

如果 Sentry 影响性能：
- 降低采样率
- 检查网络延迟
- 考虑使用本地 Sentry 实例

## 相关链接

- [Sentry Python SDK 文档](https://docs.sentry.io/platforms/python/)
- [FastAPI 集成指南](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [性能监控指南](https://docs.sentry.io/product/performance/)
- [错误监控最佳实践](https://docs.sentry.io/product/error-monitoring/) 