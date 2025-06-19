# SelfMastery B2B业务系统 - UI界面启动指南

## 概述

本指南介绍如何启动SelfMastery B2B业务系统的用户界面(UI)。系统包含后端API服务和前端PyQt6桌面应用程序。

## 系统架构

```
SelfMastery B2B业务系统
├── 后端API服务 (FastAPI) - 端口8000
│   ├── 用户认证
│   ├── 业务数据管理
│   ├── 系统配置
│   └── Sentry监控
├── 前端UI界面 (PyQt6)
│   ├── 系统图谱
│   ├── 业务流程编辑器
│   ├── SOP文档管理
│   ├── KPI仪表板
│   └── 任务管理
└── 数据库 (SQLite)
    ├── 用户数据
    ├── 业务系统数据
    ├── 流程数据
    └── KPI数据
```

## 启动步骤

### 1. 启动后端服务

首先启动后端API服务：

```bash
# 方法1：使用启动脚本（推荐）
python scripts/final_startup_fix.py

# 方法2：直接启动
python -m uvicorn selfmastery.backend.main:app --host 0.0.0.0 --port 8000
```

**验证后端启动成功：**
- 浏览器访问：http://localhost:8000/health
- API文档：http://localhost:8000/docs
- 看到JSON响应表示后端正常运行

### 2. 启动UI界面

有两种方式启动UI界面：

#### 方法1：使用简化UI启动脚本（推荐）

```bash
python scripts/start_ui_simple.py
```

这会启动一个简化版本的UI界面，包含：
- 系统标题和状态显示
- 主要功能模块按钮
- 后端连接状态提示
- 操作指引信息

#### 方法2：尝试完整UI

```bash
# 如果依赖完整，可以尝试启动完整版本
python scripts/start_ui.py
```

## UI界面功能

### 主要模块

1. **🏢 业务系统管理**
   - 管理业务系统架构
   - 系统组件配置

2. **🔄 业务流程设计**
   - 可视化流程设计
   - 流程优化建议

3. **📋 SOP文档管理**
   - 标准作业程序文档
   - 文档版本控制

4. **📊 KPI指标监控**
   - 关键绩效指标dashboard
   - 实时数据监控

5. **✅ 任务管理**
   - 项目任务跟踪
   - 进度管理

### 界面特性

- **现代化设计**：基于Material Design风格
- **响应式布局**：适配不同屏幕尺寸
- **多标签页**：支持多任务并行
- **主题切换**：支持明暗主题
- **实时监控**：集成Sentry错误监控

## 故障排除

### 常见问题

#### 1. PyQt6未安装

**错误信息：**
```
ImportError: No module named 'PyQt6'
```

**解决方案：**
```bash
pip install PyQt6
```

#### 2. 后端服务未启动

**现象：** UI显示后端连接失败

**解决方案：**
```bash
python scripts/final_startup_fix.py
```

#### 3. 模块导入错误

**错误信息：**
```
ImportError: attempted relative import beyond top-level package
```

**解决方案：** 使用简化UI启动脚本：
```bash
python scripts/start_ui_simple.py
```

#### 4. 数据库连接问题

**解决方案：**
```bash
# 重新初始化数据库
python scripts/init_db.py

# 或运行完整的启动修复
python scripts/final_startup_fix.py
```

### 日志查看

查看系统日志获取详细错误信息：

```bash
# 应用日志
cat logs/application.log

# 后端日志
cat logs/backend.log

# 数据库日志  
cat logs/database.log
```

## 开发模式

### 热重载开发

对于开发者，可以启用热重载模式：

```bash
# 后端热重载
uvicorn selfmastery.backend.main:app --reload --host 0.0.0.0 --port 8000

# 前端开发模式
export DEBUG=true
python scripts/start_ui_simple.py
```

### 调试模式

启用详细日志输出：

```bash
export LOG_LEVEL=debug
export DEBUG=true
python scripts/start_ui_simple.py
```

## 系统要求

### 软件依赖

- **Python**: 3.8+
- **PyQt6**: 6.0+
- **FastAPI**: 0.68+
- **SQLite**: 3.0+

### 硬件要求

- **内存**: 最少2GB，推荐4GB+
- **磁盘**: 500MB可用空间
- **显示器**: 1280x720分辨率以上

### 操作系统

- **macOS**: 10.14+
- **Windows**: 10+  
- **Linux**: Ubuntu 18.04+

## 快速启动命令

创建一个便捷的启动脚本：

```bash
#!/bin/bash
# start_system.sh

echo "🚀 启动SelfMastery B2B业务系统"

# 启动后端
echo "1. 启动后端服务..."
python scripts/final_startup_fix.py &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 启动UI
echo "2. 启动UI界面..."
python scripts/start_ui_simple.py

# 清理
kill $BACKEND_PID
```

使用方法：
```bash
chmod +x start_system.sh
./start_system.sh
```

## 技术支持

如果遇到问题：

1. **查看日志**：检查 `logs/` 目录下的日志文件
2. **Sentry监控**：系统集成了Sentry错误监控
3. **重新安装**：删除虚拟环境重新安装依赖
4. **问题反馈**：记录错误信息和复现步骤

## 更新历史

- **v1.0.0** (2024-01): 初始版本
  - 基础UI框架
  - 后端API集成
  - Sentry监控集成

---

*本指南持续更新中，如有问题请查看最新版本或联系技术支持。* 