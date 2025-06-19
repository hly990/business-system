# SelfMastery B2B业务系统 - 开发者指南

## 目录

1. [开发环境搭建](#开发环境搭建)
2. [项目结构](#项目结构)
3. [技术栈](#技术栈)
4. [后端开发](#后端开发)
5. [前端开发](#前端开发)
6. [数据库设计](#数据库设计)
7. [API文档](#api文档)
8. [测试指南](#测试指南)
9. [部署指南](#部署指南)
10. [贡献指南](#贡献指南)

## 开发环境搭建

### 系统要求

- **Python**: 3.8+
- **Node.js**: 14+ (如果需要前端构建工具)
- **Git**: 最新版本
- **IDE**: PyCharm、VSCode或其他Python IDE

### 环境配置

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd selfmastery-b2b-system
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
   cd selfmastery
   pip install -r requirements.txt
   ```

4. **环境变量配置**
   ```bash
   cp .env.example .env
   # 编辑.env文件，配置数据库连接等参数
   ```

5. **初始化数据库**
   ```bash
   python ../scripts/init_db.py
   ```

6. **运行测试**
   ```bash
   python -m pytest tests/
   ```

### 开发工具配置

#### VSCode配置

创建`.vscode/settings.json`：
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm配置

1. 设置Python解释器为虚拟环境中的Python
2. 配置代码格式化工具（Black）
3. 启用pytest作为测试运行器
4. 配置数据库连接

## 项目结构

```
selfmastery-b2b-system/
├── selfmastery/                    # 主应用目录
│   ├── backend/                    # 后端代码
│   │   ├── api/                    # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # 认证相关API
│   │   │   └── users.py           # 用户管理API
│   │   ├── models/                 # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # 基础模型
│   │   │   ├── user.py            # 用户模型
│   │   │   ├── system.py          # 业务系统模型
│   │   │   ├── process.py         # 流程模型
│   │   │   ├── sop.py             # SOP模型
│   │   │   ├── kpi.py             # KPI模型
│   │   │   └── task.py            # 任务模型
│   │   ├── schemas/                # Pydantic模式
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── system.py
│   │   │   ├── process.py
│   │   │   ├── sop.py
│   │   │   ├── kpi.py
│   │   │   └── task.py
│   │   ├── services/               # 业务逻辑服务
│   │   │   ├── __init__.py
│   │   │   ├── base_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   └── system_service.py
│   │   ├── middleware/             # 中间件
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── cors.py
│   │   ├── utils/                  # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── exceptions.py
│   │   │   └── responses.py
│   │   └── main.py                 # FastAPI应用入口
│   ├── frontend/                   # 前端代码
│   │   ├── ui/                     # 用户界面
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py     # 主窗口
│   │   │   ├── auth/              # 认证界面
│   │   │   │   ├── login_dialog.py
│   │   │   │   └── register_dialog.py
│   │   │   ├── components/        # 通用组件
│   │   │   │   └── custom_widgets.py
│   │   │   └── layouts/           # 布局管理
│   │   │       └── responsive_layout.py
│   │   ├── widgets/               # 业务组件
│   │   │   ├── __init__.py
│   │   │   ├── system_canvas.py   # 系统画布
│   │   │   ├── process_editor.py  # 流程编辑器
│   │   │   ├── sop_editor.py      # SOP编辑器
│   │   │   ├── kpi_dashboard.py   # KPI仪表板
│   │   │   ├── task_manager.py    # 任务管理器
│   │   │   └── navigation_tree.py # 导航树
│   │   ├── services/              # 前端服务
│   │   │   ├── __init__.py
│   │   │   ├── api_client.py      # API客户端
│   │   │   ├── auth_manager.py    # 认证管理
│   │   │   └── data_manager.py    # 数据管理
│   │   ├── graphics/              # 图形组件
│   │   │   ├── __init__.py
│   │   │   ├── canvas.py          # 画布组件
│   │   │   ├── items.py           # 图形项
│   │   │   └── layouts.py         # 图形布局
│   │   ├── styles/                # 样式主题
│   │   │   ├── __init__.py
│   │   │   └── themes.py
│   │   ├── resources/             # 资源文件
│   │   └── main.py                # 前端应用入口
│   ├── config/                    # 配置文件
│   │   ├── __init__.py
│   │   ├── settings.py            # 应用设置
│   │   └── database.py            # 数据库配置
│   ├── migrations/                # 数据库迁移
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── shared/                    # 共享代码
│   │   └── __init__.py
│   ├── tests/                     # 测试代码
│   │   └── __init__.py
│   ├── requirements.txt           # Python依赖
│   ├── setup.py                   # 安装脚本
│   ├── .env.example              # 环境变量示例
│   └── README.md                  # 项目说明
├── scripts/                       # 脚本文件
│   ├── init_db.py                # 数据库初始化
│   ├── create_demo_data.py       # 创建演示数据
│   ├── start_system.py           # 系统启动
│   ├── test_integration.py       # 集成测试
│   ├── test_frontend.py          # 前端测试
│   └── test_backend.py           # 后端测试
├── docs/                          # 文档
│   ├── technical-architecture.md  # 技术架构
│   ├── user-guide.md             # 用户指南
│   ├── developer-guide.md        # 开发者指南
│   └── deployment-guide.md       # 部署指南
├── data/                          # 数据文件
│   └── selfmastery.db            # SQLite数据库
├── alembic.ini                   # Alembic配置
└── README.md                     # 项目根README
```

## 技术栈

### 后端技术

- **Web框架**: FastAPI 0.68+
- **ASGI服务器**: Uvicorn
- **ORM**: SQLAlchemy 1.4+
- **数据库**: SQLite (开发), PostgreSQL (生产)
- **认证**: JWT (JSON Web Tokens)
- **数据验证**: Pydantic
- **数据库迁移**: Alembic
- **测试框架**: pytest
- **API文档**: Swagger/OpenAPI

### 前端技术

- **GUI框架**: PyQt5
- **图形绘制**: QPainter, QGraphicsView
- **HTTP客户端**: requests
- **数据处理**: pandas (可选)
- **图表库**: matplotlib, plotly (可选)

### 开发工具

- **代码格式化**: Black
- **代码检查**: pylint, flake8
- **类型检查**: mypy
- **依赖管理**: pip, pip-tools
- **版本控制**: Git
- **CI/CD**: GitHub Actions (可选)

## 后端开发

### FastAPI应用结构

#### 主应用文件 (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import auth, users
from backend.middleware.auth import AuthMiddleware

app = FastAPI(
    title="SelfMastery B2B API",
    description="业务系统管理API",
    version="1.0.0"
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])

@app.get("/")
async def root():
    return {"message": "SelfMastery B2B API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### 数据模型开发

#### 基础模型 (`models/base.py`)

```python
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

#### 用户模型 (`models/user.py`)

```python
from sqlalchemy import Column, String, Boolean
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="employee")
    is_active = Column(Boolean, default=True)
```

### Pydantic模式

#### 用户模式 (`schemas/user.py`)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "employee"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True
```

### 服务层开发

#### 基础服务 (`services/base_service.py`)

```python
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from backend.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
```

### API路由开发

#### 认证API (`api/auth.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.schemas.user import UserCreate, UserResponse
from backend.services.auth_service import AuthService
from backend.config.database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService()
    return auth_service.register_user(db, user)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_service = AuthService()
    return auth_service.authenticate_user(db, form_data.username, form_data.password)

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    auth_service = AuthService()
    return auth_service.get_current_user(db, token)
```

### 中间件开发

#### 认证中间件 (`middleware/auth.py`)

```python
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.config.settings import settings

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self, secret_key: str = settings.SECRET_KEY):
        self.secret_key = secret_key
        self.algorithm = "HS256"
    
    def verify_token(self, credentials: HTTPAuthorizationCredentials):
        try:
            payload = jwt.decode(credentials.credentials, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            return username
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
```

## 前端开发

### PyQt5应用结构

#### 主窗口 (`ui/main_window.py`)

```python
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMenuBar, QStatusBar
from PyQt5.QtCore import Qt
from frontend.widgets.system_canvas import SystemCanvas
from frontend.widgets.navigation_tree import NavigationTree
from frontend.services.auth_manager import AuthManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.init_ui()
        self.setup_menu()
        self.setup_status_bar()
    
    def init_ui(self):
        self.setWindowTitle("SelfMastery B2B业务系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加组件
        self.navigation_tree = NavigationTree()
        self.system_canvas = SystemCanvas()
        
        layout.addWidget(self.navigation_tree)
        layout.addWidget(self.system_canvas)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        file_menu.addAction('新建系统', self.new_system)
        file_menu.addAction('打开系统', self.open_system)
        file_menu.addAction('保存', self.save_system)
        file_menu.addSeparator()
        file_menu.addAction('退出', self.close)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        edit_menu.addAction('撤销', self.undo)
        edit_menu.addAction('重做', self.redo)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        view_menu.addAction('放大', self.zoom_in)
        view_menu.addAction('缩小', self.zoom_out)
        view_menu.addAction('适应窗口', self.fit_to_window)
    
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
```

### 自定义组件开发

#### 系统画布 (`widgets/system_canvas.py`)

```python
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush
from frontend.graphics.items import SystemItem, ProcessItem

class SystemCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
    def add_system_item(self, system_data):
        item = SystemItem(system_data)
        self.scene.addItem(item)
        return item
    
    def add_process_item(self, process_data):
        item = ProcessItem(process_data)
        self.scene.addItem(item)
        return item
    
    def clear_canvas(self):
        self.scene.clear()
    
    def zoom_in(self):
        self.scale(1.2, 1.2)
    
    def zoom_out(self):
        self.scale(0.8, 0.8)
    
    def fit_to_window(self):
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
```

### 服务层开发

#### API客户端 (`services/api_client.py`)

```python
import requests
from typing import Dict, Any, Optional
from frontend.services.auth_manager import AuthManager

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.auth_manager = AuthManager()
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        token = self.auth_manager.get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = requests.put(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = requests.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
```

## 数据库设计

### 数据库配置

#### 数据库连接 (`config/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite特定配置
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 数据库迁移

#### Alembic配置

```python
# migrations/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from backend.models.base import Base
from backend.config.settings import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

#### 创建迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "Add user table"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## API文档

### Swagger文档

FastAPI自动生成API文档，访问地址：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### API端点

#### 认证相关

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

#### 用户管理

- `GET /api/users/` - 获取用户列表
- `GET /api/users/{user_id}` - 获取用户详情
- `PUT /api/users/{user_id}` - 更新用户信息
- `DELETE /api/users/{user_id}` - 删除用户

#### 业务系统

- `GET /api/systems/` - 获取业务系统列表
- `POST /api/systems/` - 创建业务系统
- `GET /api/systems/{system_id}` - 获取系统详情
- `PUT /api/systems/{system_id}` - 更新系统信息
- `DELETE /api/systems/{system_id}` - 删除系统

## 测试指南

### 单元测试

#### 测试配置 (`tests/conftest.py`)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.base import Base
from backend.config.database import get_db
from backend.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

#### 模型测试 (`tests/test_models.py`)

```python
import pytest
from backend.models.user import User

def test_create_user(db):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "hashed_password",
        "full_name": "Test User"
    }
    user = User(**user_data)
    db.add(user)
    db.commit()
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
```

#### API测试 (`tests/test_api.py`)

```python
import pytest
from fastapi.testclient import TestClient

def test_register_user(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"

def test_login_user(client):
    # 先注册用户
    user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123"
    }
    client.post("/api/auth/register", json=user_data)
    
    # 测试登录
    login_data = {
        "username": "loginuser",
        "password": "password123"
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
```

### 集成测试

运行集成测试脚本：

```bash
python scripts/test_integration.py
python scripts/test_backend.py
python scripts/test_frontend.py
```

### 测试覆盖率

```bash
# 安装coverage
pip install coverage

# 运行测试并生成覆盖率报告
coverage run -m pytest
coverage report
coverage html  # 生成HTML报告
```

## 部署指南

### 开发环境部署

```bash
# 启动后端服务
cd selfmastery
python backend/main.py

# 启动前端应用
python frontend/main.py
```

### 生产环境部署

#### 使用Docker

创建`Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

创建`docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/selfmastery
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=selfmastery
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 使用systemd

创建服务文件`/etc/systemd/system/selfmastery.service`：

```ini
[Unit]
Description=SelfMastery B2B System
After=network.target

[Service]
Type=simple
User=selfmastery
WorkingDirectory=/opt/selfmastery
Environment=PATH=/