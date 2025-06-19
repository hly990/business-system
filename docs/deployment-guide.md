# SelfMastery B2B业务系统 - 部署指南

## 目录

1. [部署概述](#部署概述)
2. [系统要求](#系统要求)
3. [开发环境部署](#开发环境部署)
4. [生产环境部署](#生产环境部署)
5. [Docker部署](#docker部署)
6. [云平台部署](#云平台部署)
7. [数据库配置](#数据库配置)
8. [安全配置](#安全配置)
9. [监控与日志](#监控与日志)
10. [故障排除](#故障排除)

## 部署概述

SelfMastery B2B业务系统采用前后端分离的架构，包含以下组件：

- **后端API服务**：基于FastAPI的RESTful API
- **前端桌面应用**：基于PyQt5的桌面客户端
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **文件存储**：本地文件系统或云存储

### 部署架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端客户端     │    │    后端API      │    │     数据库       │
│   (PyQt5)      │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│                │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   文件存储       │
                       │  (本地/云端)     │
                       └─────────────────┘
```

## 系统要求

### 最低配置

- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB可用空间
- **网络**: 100Mbps带宽

### 推荐配置

- **CPU**: 4核心或更多
- **内存**: 8GB RAM或更多
- **存储**: 100GB SSD
- **网络**: 1Gbps带宽

### 操作系统支持

- **Linux**: Ubuntu 18.04+, CentOS 7+, RHEL 7+
- **Windows**: Windows 10+, Windows Server 2016+
- **macOS**: macOS 10.14+

### 软件依赖

- **Python**: 3.8+
- **数据库**: PostgreSQL 12+ (生产环境)
- **Web服务器**: Nginx (可选，用于反向代理)
- **进程管理**: systemd, supervisor, 或 PM2

## 开发环境部署

### 快速启动

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd selfmastery-b2b-system
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   cd selfmastery
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑.env文件，配置必要参数
   ```

5. **初始化数据库**
   ```bash
   python ../scripts/init_db.py
   ```

6. **创建演示数据**
   ```bash
   python ../scripts/create_demo_data.py
   ```

7. **启动系统**
   ```bash
   python ../scripts/start_system.py
   ```

### 手动启动

如果需要分别启动各个组件：

```bash
# 启动后端API服务
cd selfmastery
python backend/main.py

# 在另一个终端启动前端应用
python frontend/main.py
```

### 开发环境配置

#### 环境变量配置 (`.env`)

```bash
# 应用配置
APP_NAME=SelfMastery B2B System
APP_VERSION=1.0.0
DEBUG=true

# 数据库配置
DATABASE_URL=sqlite:///./data/selfmastery.db

# 安全配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API配置
API_HOST=localhost
API_PORT=8000

# 日志配置
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log
```

## 生产环境部署

### 服务器准备

1. **更新系统**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt upgrade -y
   
   # CentOS/RHEL
   sudo yum update -y
   ```

2. **安装Python 3.8+**
   ```bash
   # Ubuntu/Debian
   sudo apt install python3.8 python3.8-venv python3.8-dev -y
   
   # CentOS/RHEL
   sudo yum install python38 python38-devel -y
   ```

3. **安装PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib -y
   
   # CentOS/RHEL
   sudo yum install postgresql-server postgresql-contrib -y
   sudo postgresql-setup initdb
   ```

4. **安装Nginx**
   ```bash
   # Ubuntu/Debian
   sudo apt install nginx -y
   
   # CentOS/RHEL
   sudo yum install nginx -y
   ```

### 应用部署

1. **创建应用用户**
   ```bash
   sudo useradd -m -s /bin/bash selfmastery
   sudo usermod -aG sudo selfmastery
   ```

2. **部署应用代码**
   ```bash
   sudo -u selfmastery git clone <repository-url> /opt/selfmastery
   cd /opt/selfmastery
   sudo chown -R selfmastery:selfmastery /opt/selfmastery
   ```

3. **创建虚拟环境**
   ```bash
   sudo -u selfmastery python3.8 -m venv /opt/selfmastery/venv
   sudo -u selfmastery /opt/selfmastery/venv/bin/pip install -r /opt/selfmastery/selfmastery/requirements.txt
   ```

4. **配置环境变量**
   ```bash
   sudo -u selfmastery cp /opt/selfmastery/selfmastery/.env.example /opt/selfmastery/selfmastery/.env
   sudo -u selfmastery nano /opt/selfmastery/selfmastery/.env
   ```

### 生产环境配置

#### 环境变量配置 (`.env`)

```bash
# 应用配置
APP_NAME=SelfMastery B2B System
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
DATABASE_URL=postgresql://selfmastery:password@localhost:5432/selfmastery_prod

# 安全配置
SECRET_KEY=your-very-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/selfmastery/app.log

# 文件上传配置
UPLOAD_DIR=/opt/selfmastery/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### 数据库初始化

```bash
# 创建数据库用户和数据库
sudo -u postgres psql << EOF
CREATE USER selfmastery WITH PASSWORD 'your-secure-password';
CREATE DATABASE selfmastery_prod OWNER selfmastery;
GRANT ALL PRIVILEGES ON DATABASE selfmastery_prod TO selfmastery;
\q
EOF

# 运行数据库迁移
cd /opt/selfmastery/selfmastery
sudo -u selfmastery /opt/selfmastery/venv/bin/python ../scripts/init_db.py
```

### 系统服务配置

#### 创建systemd服务

创建 `/etc/systemd/system/selfmastery-api.service`：

```ini
[Unit]
Description=SelfMastery B2B API Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=selfmastery
Group=selfmastery
WorkingDirectory=/opt/selfmastery/selfmastery
Environment=PATH=/opt/selfmastery/venv/bin
ExecStart=/opt/selfmastery/venv/bin/python backend/main.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/selfmastery /var/log/selfmastery

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable selfmastery-api
sudo systemctl start selfmastery-api
sudo systemctl status selfmastery-api
```

### Nginx反向代理配置

创建 `/etc/nginx/sites-available/selfmastery`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件
    location /static/ {
        alias /opt/selfmastery/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 文件上传
    location /uploads/ {
        alias /opt/selfmastery/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }

    # 限制请求大小
    client_max_body_size 10M;
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/selfmastery /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker部署

### Dockerfile

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY selfmastery/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY selfmastery/ .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # 数据库服务
  db:
    image: postgres:13-alpine
    environment:
      POSTGRES_DB: selfmastery
      POSTGRES_USER: selfmastery
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U selfmastery"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存 (可选)
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 后端API服务
  api:
    build: .
    environment:
      DATABASE_URL: postgresql://selfmastery:${DB_PASSWORD}@db:5432/selfmastery
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "false"
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

### 环境变量文件

创建 `.env`：

```bash
# 数据库密码
DB_PASSWORD=your-secure-db-password

# 应用密钥
SECRET_KEY=your-very-secure-secret-key

# 其他配置
COMPOSE_PROJECT_NAME=selfmastery
```

### 部署命令

```bash
# 构建和启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down

# 更新服务
docker-compose pull
docker-compose up -d
```

## 云平台部署

### AWS部署

#### 使用ECS (Elastic Container Service)

1. **创建ECR仓库**
   ```bash
   aws ecr create-repository --repository-name selfmastery-api
   ```

2. **构建和推送镜像**
   ```bash
   # 登录ECR
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

   # 构建镜像
   docker build -t selfmastery-api .

   # 标记镜像
   docker tag selfmastery-api:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/selfmastery-api:latest

   # 推送镜像
   docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/selfmastery-api:latest
   ```

3. **创建ECS任务定义**
   ```json
   {
     "family": "selfmastery-api",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "api",
         "image": "<account-id>.dkr.ecr.us-west-2.amazonaws.com/selfmastery-api:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DATABASE_URL",
             "value": "postgresql://username:password@rds-endpoint:5432/selfmastery"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/selfmastery-api",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

#### 使用RDS数据库

```bash
# 创建RDS实例
aws rds create-db-instance \
    --db-instance-identifier selfmastery-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username selfmastery \
    --master-user-password your-secure-password \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name default
```

### Google Cloud Platform部署

#### 使用Cloud Run

1. **构建镜像**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/selfmastery-api
   ```

2. **部署到Cloud Run**
   ```bash
   gcloud run deploy selfmastery-api \
     --image gcr.io/PROJECT-ID/selfmastery-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL="postgresql://user:pass@host:5432/db"
   ```

### Azure部署

#### 使用Container Instances

```bash
# 创建资源组
az group create --name selfmastery-rg --location eastus

# 部署容器
az container create \
  --resource-group selfmastery-rg \
  --name selfmastery-api \
  --image your-registry/selfmastery-api:latest \
  --dns-name-label selfmastery-api \
  --ports 8000 \
  --environment-variables DATABASE_URL="postgresql://user:pass@host:5432/db"
```

## 数据库配置

### PostgreSQL优化

#### 配置文件优化 (`postgresql.conf`)

```ini
# 内存配置
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# 连接配置
max_connections = 100
listen_addresses = '*'

# 日志配置
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000

# 性能配置
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

#### 访问控制 (`pg_hba.conf`)

```ini
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    selfmastery     selfmastery     10.0.0.0/8              md5
```

### 数据库备份

#### 自动备份脚本

创建 `/opt/selfmastery/scripts/backup.sh`：

```bash
#!/bin/bash

# 配置
DB_NAME="selfmastery"
DB_USER="selfmastery"
BACKUP_DIR="/opt/selfmastery/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/selfmastery_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

#### 设置定时备份

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点执行备份
0 2 * * * /opt/selfmastery/scripts/backup.sh
```

## 安全配置

### SSL/TLS配置

#### 获取Let's Encrypt证书

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

### 防火墙配置

#### UFW (Ubuntu)

```bash
# 启用UFW
sudo ufw enable

# 允许SSH
sudo ufw allow ssh

# 允许HTTP和HTTPS
sudo ufw allow 80
sudo ufw allow 443

# 允许PostgreSQL (仅本地)
sudo ufw allow from 127.0.0.1 to any port 5432

# 查看状态
sudo ufw status
```

#### iptables

```bash
# 基本规则
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP

# 保存规则
iptables-save > /etc/iptables/rules.v4
```

### 应用安全

#### 环境变量安全

```bash
# 设置文件权限
chmod 600 /opt/selfmastery/selfmastery/.env
chown selfmastery:selfmastery /opt/selfmastery/selfmastery/.env
```

#### 日志安全

```bash
# 创建日志目录
sudo mkdir -p /var/log/selfmastery
sudo chown selfmastery:selfmastery /var/log/selfmastery
sudo chmod 750 /var/log/selfmastery

# 配置logrotate
sudo tee /etc/logrotate.d/selfmastery << EOF
/var/log/selfmastery/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 selfmastery selfmastery
    postrotate
        systemctl reload selfmastery-api
    endscript
}
EOF
```

## 监控与日志

### 应用监控

#### 健康检查端点

在FastAPI应用中添加健康检查：

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "database": await check_database_health(),
        "memory_usage": get_memory_usage()
    }
```

#### Prometheus监控

安装prometheus-fastapi-instrumentator：

```bash
pip install prometheus-fastapi-instrumentator
```

在应用中添加：

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)
```

### 日志配置

#### 结构化日志

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_entry)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("/var/log/selfmastery/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.handlers[0].setFormatter(JSONFormatter())
```

### 系统监控

#### 使用htop监控系统资源

```bash
sudo apt install htop
htop
```

#### 使用netstat监控网络连接

```bash
# 查看监听端口
netstat -tlnp

# 查看连接状态
netstat -an | grep :8000
```

## 故障排除

### 常见问题

#### 1. 服务无法启动

**症状**: systemctl start失败

**排查步骤**:
```bash
# 查看服务状态
sudo systemctl status selfmastery-api

# 查看详细日志
sudo journalctl -u selfmastery-api -f

# 检查配置文件
sudo -u selfmastery /opt/selfmastery/venv/bin/python -c "from backend.config.settings import settings; print(settings)"
```

#### 2. 数据库连接失败

**症状**: 数据库连接错误

**排查步骤**:
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 测试数据库连接
psql -h localhost -U selfmastery -d selfmastery

# 检查连接配置
grep DATABASE_URL /opt/selfmastery/selfmastery/.env
```

#### 3. 内存使用过高

**症状**: 系统响应缓慢

**排查步骤**:
```bash
# 查看内存使用
free -h
top -p $(pgrep -f selfmastery)

# 查看进程内存使用
ps aux | grep selfmastery

# 重启服务释放内存
sudo systemctl restart selfmastery-api
```

#### 4. 磁盘空间不足

**症状**: 写入操作失败

**排查步骤**:
```bash
# 查看磁盘使用
df -h

# 查找大文件
du -sh /opt/selfmastery/* | sort -hr

# 清理日志文件
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -mtime +7 -delete
```

### 性能优化

#### 数据库优化

```sql
-- 查看慢查询
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- 分析表统计信息
ANALYZE;

-- 重建索引
REINDEX DATABASE selfmastery;
```

#### 应用优化

```python
# 使用连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 备份恢复

#### 数据恢复

```bash
# 从备份恢复数据库
gunzip -c /opt/selfmastery/backups/selfmastery_20241201_020000.sql.gz | psql -h localhost -U selfmastery -d selfmastery

# 恢复文件
rsync -av /opt/selfmastery/backups/uploads/ /opt/selfmastery/uploads/
```

#### 灾难恢复

1. **准备新服务器**
2. **安装必要软件**
3. **恢复数据库**
4. **恢复应用代码**
5. **恢复配置文件**
6. **启动服务**
7. **验证功能**

---

**版本信息**: 部署指南 v1.0  
**最后更新**: 2024年12月  
**适用版本**: SelfMastery B2B业务系统 v1.0+

如有部署相关问题，请参考故障排除章节或联系技术支持团队。