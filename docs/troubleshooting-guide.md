# SelfMastery B2B业务系统 - 问题排查指南

## 目录

1. [常见问题分类](#常见问题分类)
2. [系统启动问题](#系统启动问题)
3. [数据库相关问题](#数据库相关问题)
4. [网络连接问题](#网络连接问题)
5. [性能问题](#性能问题)
6. [用户认证问题](#用户认证问题)
7. [前端界面问题](#前端界面问题)
8. [数据同步问题](#数据同步问题)
9. [日志分析指南](#日志分析指南)
10. [调试工具使用](#调试工具使用)

## 常见问题分类

### 问题严重级别

- **严重 (Critical)**: 系统无法启动或核心功能完全不可用
- **高 (High)**: 主要功能受影响，但系统仍可部分使用
- **中 (Medium)**: 部分功能异常，有替代方案
- **低 (Low)**: 界面显示问题或非关键功能异常

### 问题类型

- **启动问题**: 系统无法正常启动
- **连接问题**: 网络或数据库连接失败
- **性能问题**: 系统响应缓慢或资源占用过高
- **功能问题**: 特定功能无法正常工作
- **数据问题**: 数据丢失、损坏或不一致

## 系统启动问题

### 问题1: 后端服务无法启动

**症状描述**:
- 运行启动脚本时报错
- 服务进程启动后立即退出
- 无法访问API端点

**可能原因**:
1. 端口被占用
2. 数据库连接失败
3. 环境变量配置错误
4. Python依赖缺失

**排查步骤**:

1. **检查端口占用**
   ```bash
   # 检查8000端口是否被占用
   netstat -tlnp | grep :8000
   lsof -i :8000
   
   # 如果被占用，终止占用进程
   sudo kill -9 <PID>
   ```

2. **检查数据库连接**
   ```bash
   # 测试数据库连接
   python -c "
   from selfmastery.config.database import engine
   try:
       conn = engine.connect()
       print('数据库连接成功')
       conn.close()
   except Exception as e:
       print(f'数据库连接失败: {e}')
   "
   ```

3. **验证环境变量**
   ```bash
   # 检查.env文件
   cat selfmastery/.env
   
   # 验证关键配置
   python -c "
   from selfmastery.config.settings import settings
   print(f'DATABASE_URL: {settings.DATABASE_URL}')
   print(f'SECRET_KEY: {settings.SECRET_KEY[:10]}...')
   "
   ```

4. **检查Python依赖**
   ```bash
   # 验证关键依赖
   python -c "
   import fastapi, uvicorn, sqlalchemy, PyQt5
   print('所有依赖正常')
   "
   
   # 重新安装依赖
   pip install -r selfmastery/requirements.txt
   ```

**解决方案**:

```bash
# 1. 停止所有相关进程
pkill -f "python.*main.py"

# 2. 清理端口
sudo fuser -k 8000/tcp

# 3. 重新初始化数据库
python scripts/init_db.py

# 4. 重新启动系统
python scripts/start_system.py
```

### 问题2: 前端应用无法启动

**症状描述**:
- PyQt应用启动时崩溃
- 显示"No module named 'PyQt5'"错误
- 界面无法正常显示

**可能原因**:
1. PyQt5未正确安装
2. 显示环境配置问题
3. 权限不足
4. 系统缺少图形库

**排查步骤**:

1. **检查PyQt5安装**
   ```bash
   python -c "
   try:
       from PyQt5.QtWidgets import QApplication
       print('PyQt5安装正常')
   except ImportError as e:
       print(f'PyQt5安装异常: {e}')
   "
   ```

2. **检查显示环境**
   ```bash
   # Linux环境检查
   echo $DISPLAY
   xhost +local:
   
   # 测试X11转发
   xclock  # 如果能显示时钟，说明X11正常
   ```

3. **检查权限**
   ```bash
   # 检查文件权限
   ls -la selfmastery/frontend/
   
   # 检查用户组
   groups $USER
   ```

**解决方案**:

```bash
# 1. 重新安装PyQt5
pip uninstall PyQt5
pip install PyQt5

# 2. Linux环境配置
export DISPLAY=:0
xhost +local:

# 3. 安装系统依赖 (Ubuntu/Debian)
sudo apt-get install python3-pyqt5 python3-pyqt5.qtsvg

# 4. 以正确用户身份运行
python selfmastery/frontend/main.py
```

### 问题3: 数据库初始化失败

**症状描述**:
- init_db.py脚本执行失败
- 数据库表创建不完整
- 迁移脚本报错

**可能原因**:
1. 数据库服务未启动
2. 权限不足
3. 磁盘空间不足
4. 数据库版本不兼容

**排查步骤**:

1. **检查数据库服务**
   ```bash
   # SQLite检查
   ls -la data/selfmastery.db
   
   # PostgreSQL检查
   sudo systemctl status postgresql
   pg_isready -h localhost -p 5432
   ```

2. **检查磁盘空间**
   ```bash
   df -h
   du -sh data/
   ```

3. **手动测试数据库操作**
   ```bash
   # SQLite测试
   sqlite3 data/selfmastery.db ".tables"
   
   # PostgreSQL测试
   psql -h localhost -U selfmastery -d selfmastery -c "\dt"
   ```

**解决方案**:

```bash
# 1. 清理并重新创建数据库
rm -f data/selfmastery.db
mkdir -p data

# 2. 重新运行初始化
python scripts/init_db.py

# 3. 验证表结构
python -c "
from selfmastery.config.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'创建的表: {tables}')
"
```

## 数据库相关问题

### 问题4: 数据库连接超时

**症状描述**:
- API请求响应缓慢
- 数据库连接池耗尽
- 出现"connection timeout"错误

**可能原因**:
1. 数据库负载过高
2. 连接池配置不当
3. 网络延迟
4. 长时间运行的查询

**排查步骤**:

1. **检查数据库性能**
   ```sql
   -- PostgreSQL查询
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
   FROM pg_stat_activity 
   WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
   
   -- 查看连接数
   SELECT count(*) FROM pg_stat_activity;
   ```

2. **检查连接池状态**
   ```python
   from selfmastery.config.database import engine
   pool = engine.pool
   print(f"连接池大小: {pool.size()}")
   print(f"已检出连接: {pool.checkedout()}")
   print(f"溢出连接: {pool.overflow()}")
   ```

3. **监控系统资源**
   ```bash
   # 查看数据库进程
   ps aux | grep postgres
   
   # 查看内存使用
   free -h
   
   # 查看磁盘I/O
   iostat -x 1
   ```

**解决方案**:

```python
# 优化连接池配置
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # 增加连接池大小
    max_overflow=30,       # 增加溢出连接数
    pool_timeout=30,       # 设置获取连接超时
    pool_recycle=3600,     # 连接回收时间
    pool_pre_ping=True     # 连接前ping测试
)
```

### 问题5: 数据不一致

**症状描述**:
- 前端显示的数据与数据库不符
- 数据更新后未及时反映
- 出现重复或缺失数据

**可能原因**:
1. 事务处理不当
2. 缓存未及时更新
3. 并发操作冲突
4. 数据同步延迟

**排查步骤**:

1. **检查事务状态**
   ```sql
   -- 查看未提交事务
   SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';
   
   -- 查看锁等待
   SELECT * FROM pg_locks WHERE NOT granted;
   ```

2. **验证数据完整性**
   ```sql
   -- 检查数据一致性
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM business_systems;
   
   -- 检查外键约束
   SELECT conname, conrelid::regclass, confrelid::regclass 
   FROM pg_constraint WHERE contype = 'f';
   ```

3. **检查应用日志**
   ```bash
   # 查看数据库操作日志
   grep -i "database\|sql" /var/log/selfmastery/app.log
   
   # 查看错误日志
   grep -i "error\|exception" /var/log/selfmastery/app.log
   ```

**解决方案**:

```python
# 确保事务正确处理
from sqlalchemy.orm import Session
from contextlib import contextmanager

@contextmanager
def get_db_transaction():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# 使用示例
with get_db_transaction() as db:
    user = User(username="test")
    db.add(user)
    # 自动提交或回滚
```

## 网络连接问题

### 问题6: API请求失败

**症状描述**:
- 前端无法连接后端API
- 请求返回404或500错误
- 网络超时

**可能原因**:
1. 后端服务未启动
2. 防火墙阻止连接
3. 端口配置错误
4. 网络路由问题

**排查步骤**:

1. **测试网络连通性**
   ```bash
   # 测试本地连接
   curl http://localhost:8000/health
   
   # 测试端口连通性
   telnet localhost 8000
   
   # 检查路由
   traceroute api.example.com
   ```

2. **检查防火墙设置**
   ```bash
   # Ubuntu UFW
   sudo ufw status
   
   # CentOS/RHEL firewalld
   sudo firewall-cmd --list-all
   
   # iptables
   sudo iptables -L -n
   ```

3. **验证服务状态**
   ```bash
   # 检查进程
   ps aux | grep uvicorn
   
   # 检查端口监听
   netstat -tlnp | grep :8000
   ```

**解决方案**:

```bash
# 1. 重启后端服务
sudo systemctl restart selfmastery-api

# 2. 开放防火墙端口
sudo ufw allow 8000

# 3. 检查Nginx配置
sudo nginx -t
sudo systemctl reload nginx

# 4. 测试API连接
curl -v http://localhost:8000/api/health
```

### 问题7: 跨域请求被阻止

**症状描述**:
- 浏览器控制台显示CORS错误
- 前端无法访问API
- OPTIONS请求失败

**可能原因**:
1. CORS中间件配置错误
2. 请求头不被允许
3. 预检请求失败

**排查步骤**:

1. **检查CORS配置**
   ```python
   # 查看当前CORS设置
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # 检查是否正确配置
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **测试预检请求**
   ```bash
   curl -X OPTIONS \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     http://localhost:8000/api/users/
   ```

**解决方案**:

```python
# 正确配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 性能问题

### 问题8: 系统响应缓慢

**症状描述**:
- API请求响应时间过长
- 前端界面卡顿
- 数据库查询缓慢

**可能原因**:
1. 数据库查询未优化
2. 内存不足
3. CPU使用率过高
4. 磁盘I/O瓶颈

**排查步骤**:

1. **监控系统资源**
   ```bash
   # 查看CPU使用率
   top -p $(pgrep -f selfmastery)
   
   # 查看内存使用
   free -h
   ps aux --sort=-%mem | head
   
   # 查看磁盘I/O
   iostat -x 1 5
   ```

2. **分析数据库性能**
   ```sql
   -- 查看慢查询 (PostgreSQL)
   SELECT query, mean_time, calls, total_time
   FROM pg_stat_statements 
   ORDER BY mean_time DESC 
   LIMIT 10;
   
   -- 查看表大小
   SELECT schemaname,tablename,attname,n_distinct,correlation 
   FROM pg_stats;
   ```

3. **分析API性能**
   ```python
   # 添加性能监控
   import time
   from functools import wraps
   
   def monitor_performance(func):
       @wraps(func)
       async def wrapper(*args, **kwargs):
           start_time = time.time()
           result = await func(*args, **kwargs)
           end_time = time.time()
           print(f"{func.__name__} 执行时间: {end_time - start_time:.2f}秒")
           return result
       return wrapper
   ```

**解决方案**:

1. **数据库优化**
   ```sql
   -- 创建索引
   CREATE INDEX idx_users_username ON users(username);
   CREATE INDEX idx_tasks_status ON tasks(status);
   
   -- 更新统计信息
   ANALYZE;
   
   -- 清理无用数据
   VACUUM FULL;
   ```

2. **应用优化**
   ```python
   # 使用数据库连接池
   from sqlalchemy.pool import QueuePool
   
   # 添加查询缓存
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_user_by_id(user_id: int):
       return db.query(User).filter(User.id == user_id).first()
   ```

3. **系统优化**
   ```bash
   # 增加交换空间
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   
   # 优化内核参数
   echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
   ```

### 问题9: 内存泄漏

**症状描述**:
- 内存使用持续增长
- 系统变得越来越慢
- 最终导致OOM错误

**可能原因**:
1. 数据库连接未正确关闭
2. 大对象未及时释放
3. 循环引用
4. 缓存无限增长

**排查步骤**:

1. **监控内存使用**
   ```bash
   # 持续监控内存
   while true; do
     ps -p $(pgrep -f selfmastery) -o pid,vsz,rss,pmem,comm
     sleep 60
   done
   ```

2. **使用内存分析工具**
   ```python
   # 安装memory_profiler
   pip install memory-profiler
   
   # 在代码中添加装饰器
   from memory_profiler import profile
   
   @profile
   def memory_intensive_function():
       # 你的代码
       pass
   ```

3. **检查数据库连接**
   ```python
   # 确保连接正确关闭
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()  # 确保连接关闭
   ```

**解决方案**:

```python
# 1. 使用上下文管理器
from contextlib import contextmanager

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# 2. 限制缓存大小
from functools import lru_cache

@lru_cache(maxsize=100)  # 限制缓存大小
def cached_function(param):
    return expensive_operation(param)

# 3. 定期清理缓存
import gc
import threading

def cleanup_memory():
    gc.collect()
    # 清理自定义缓存
    cached_function.cache_clear()

# 每小时执行一次清理
timer = threading.Timer(3600, cleanup_memory)
timer.start()
```

## 用户认证问题

### 问题10: 登录失败

**症状描述**:
- 用户无法登录系统
- 提示"用户名或密码错误"
- JWT令牌验证失败

**可能原因**:
1. 密码哈希算法不匹配
2. JWT密钥配置错误
3. 用户账号被锁定
4. 数据库中用户数据异常

**排查步骤**:

1. **验证用户数据**
   ```sql
   -- 检查用户是否存在
   SELECT username, email, is_active FROM users WHERE username = 'testuser';
   
   -- 检查密码哈希
   SELECT username, password_hash FROM users WHERE username = 'testuser';
   ```

2. **测试密码验证**
   ```python
   from passlib.context import CryptContext
   
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   
   # 测试密码验证
   stored_hash = "从数据库获取的哈希值"
   plain_password = "用户输入的密码"
   
   is_valid = pwd_context.verify(plain_password, stored_hash)
   print(f"密码验证结果: {is_valid}")
   ```

3. **检查JWT配置**
   ```python
   from jose import jwt
   from selfmastery.config.settings import settings
   
   # 测试JWT生成和验证
   payload = {"sub": "testuser"}
   token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
   decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
   print(f"JWT测试成功: {decoded}")
   ```

**解决方案**:

```python
# 1. 重置用户密码
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_user_password(username: str, new_password: str):
    hashed_password = pwd_context.hash(new_password)
    # 更新数据库
    db.query(User).filter(User.username == username).update({
        "password_hash": hashed_password
    })
    db.commit()

# 2. 重新生成JWT密钥
import secrets

new_secret_key = secrets.token_urlsafe(32)
print(f"新的SECRET_KEY: {new_secret_key}")

# 3. 激活用户账号
db.query(User).filter(User.username == username).update({
    "is_active": True
})
db.commit()
```

### 问题11: 会话过期

**症状描述**:
- 用户频繁被要求重新登录
- JWT令牌提前过期
- 会话状态丢失

**可能原因**:
1. JWT过期时间设置过短
2. 系统时间不同步
3. 令牌存储问题
4. 中间件配置错误

**排查步骤**:

1. **检查JWT配置**
   ```python
   from selfmastery.config.settings import settings
   print(f"令牌过期时间: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} 分钟")
   ```

2. **验证系统时间**
   ```bash
   # 检查系统时间
   date
   
   # 同步时间
   sudo ntpdate -s time.nist.gov
   ```

3. **测试令牌有效期**
   ```python
   from jose import jwt
   from datetime import datetime, timedelta
   
   # 创建测试令牌
   expire = datetime.utcnow() + timedelta(minutes=30)
   payload = {"sub": "testuser", "exp": expire}
   token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
   
   # 验证令牌
   try:
       decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
       print("令牌有效")
   except jwt.ExpiredSignatureError:
       print("令牌已过期")
   ```

**解决方案**:

```python
# 1. 调整令牌过期时间
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8小时

# 2. 实现令牌刷新机制
from datetime import datetime, timedelta

def refresh_token(current_token: str):
    try:
        payload = jwt.decode(current_token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        
        # 生成新令牌
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_payload = {"sub": username, "exp": expire}
        new_token = jwt.encode(new_payload, settings.SECRET_KEY, algorithm="HS256")
        
        return new_token
    except jwt.ExpiredSignatureError:
        return None

# 3. 前端自动刷新令牌
class AuthManager:
    def __init__(self):
        self.token = None
        self.refresh_timer = None
    
    def set_token(self, token: str):
        self.token = token
        # 在令牌过期前5分钟刷新
        refresh_time = (settings.ACCESS_TOKEN_EXPIRE_MINUTES - 5) * 60
        self.refresh_timer = threading.Timer(refresh_time, self.refresh_token)
        self.refresh_timer.start()
    
    def refresh_token(self):
        new_token = self.api_client.refresh_token(self.token)
        if new_token:
            self.set_token(new_token)
```

## 前端界面问题

### 问题12: 界面显示异常

**症状描述**:
- 窗口无法正常显示
- 控件布局错乱
- 字体或图标缺失

**可能原因**:
1. PyQt5版本不兼容
2. 系统字体缺失
3. 显示分辨率问题
4. 主题配置错误

**排查步骤**:

1. **检查PyQt5版本**
   ```python
   from PyQt5.QtCore import QT_VERSION_STR
   from PyQt5.Qt import PYQT_VERSION_STR
   print(f"Qt版本: {QT_VERSION_STR}")
   print(f"PyQt版本: {PYQT_VERSION_STR}")
   ```

2. **测试基本显示**
   ```python
   from PyQt5.QtWidgets import QApplication, QLabel
   import sys
   
   app = QApplication(sys.argv)
   label = QLabel("测试显示")
   label.show()
   app.exec_()
   ```

3. **检查系统字体**
   ```bash
   # Linux
   fc-list | grep -i "microsoft\|arial\|helvetica"
   
   # 安装字体
   sudo apt-get install fonts-liberation
   ```

**解决方案**:

```python
# 1. 设置默认字体
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
font = QFont("Arial", 10)
app.setFont(font)

# 2. 处理高DPI显示
app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# 3. 设置样式表
app.setStyleSheet("""
    QMainWindow {
        background-color: #f0f0f0;
    }
    QPushButton {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
""")
```

### 问题13: 数据加载失败

**症状描述**:
- 界面数据无法加载
- 列表或表格显示为空
- 加载指示器一直显示

**可能原因**:
1. API请求失败
2. 数据格式不匹配
3. 网络连接问题
4. 权限不足

**排查步骤**:

1. **检查API连接**
   ```python
   from frontend.services.api_client import APIClient
   
   client = APIClient()
   try:
       response = client.get("/api/users/")
       print(f"API响应: {response}")
   except Exception as e:
       print(f"API请求失败: {e}")
   ```

2. **验证数据格式**
   ```python
   # 检查返回数据结构
   import json
   
   response_data = client.get("/api/users/")
   print(json.dumps(response_data, indent=2, ensure_ascii=False))
   ```

3. **测试权限**
   ```python
   # 检查认证状态
   from frontend.services.auth_manager import AuthManager
   
   auth = AuthManager()
   if auth.is_authenticated():
       print("用户已认证")
       print(f"当前用户: {auth.get_current_user()}")
   else:
       print("用户未认证")
   ```

**解决方案**:

```python
# 1. 添加错误处理
class DataLoader:
    def __init__(self):
        self.api_client = APIClient()
    
    def load_data(self, endpoint: str):
        try:
            data = self.api_client.get(endpoint)
            return data
        except requests.exceptions.ConnectionError:
            self.show_error("网络连接失败，请检查网络设置")
            return []
        except requests.exceptions.Timeout:
            self.show_error("请求超时，请稍后重试")
            return []
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.show_error("认证失败，请重新登录")
            else:
                self.show_error(f"服务器错误: {e.response.status_code}")
            return []
    
    def show_error(self, message: str):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(None, "错误", message)

# 2. 实现重试机制
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func