"""
数据库配置模块
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置设置"""
    
    # 数据库类型配置
    DB_TYPE: str = "sqlite"  # sqlite 或 postgresql
    
    # SQLite配置
    DB_PATH: str = "data/selfmastery.db"
    
    # PostgreSQL配置（可选）
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "selfmastery"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "selfmastery_db"
    
    # 连接池配置
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # 是否启用SQL日志
    DB_ECHO: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量
    
    @property
    def database_url(self) -> str:
        """同步数据库连接URL"""
        if self.DB_TYPE == "sqlite":
            # 确保数据目录存在
            db_path = Path(self.DB_PATH)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{self.DB_PATH}"
        else:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def async_database_url(self) -> str:
        """异步数据库连接URL"""
        if self.DB_TYPE == "sqlite":
            db_path = Path(self.DB_PATH)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{self.DB_PATH}"
        else:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# 全局数据库设置实例
db_settings = DatabaseSettings()

# SQLite性能优化配置
def _sqlite_pragma_on_connect(dbapi_conn, connection_record):
    """SQLite连接时的性能优化配置"""
    if db_settings.DB_TYPE == "sqlite":
        dbapi_conn.execute("PRAGMA journal_mode=WAL")
        dbapi_conn.execute("PRAGMA synchronous=NORMAL")
        dbapi_conn.execute("PRAGMA cache_size=10000")
        dbapi_conn.execute("PRAGMA temp_store=MEMORY")
        dbapi_conn.execute("PRAGMA mmap_size=268435456")
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

# 创建数据库引擎
if db_settings.DB_TYPE == "sqlite":
    engine = create_engine(
        db_settings.database_url,
        echo=db_settings.DB_ECHO,
        connect_args={"check_same_thread": False}
    )
    event.listen(engine, "connect", _sqlite_pragma_on_connect)
else:
    engine = create_engine(
        db_settings.database_url,
        pool_size=db_settings.DB_POOL_SIZE,
        max_overflow=db_settings.DB_MAX_OVERFLOW,
        pool_timeout=db_settings.DB_POOL_TIMEOUT,
        pool_recycle=db_settings.DB_POOL_RECYCLE,
        echo=db_settings.DB_ECHO,
    )

# 创建异步数据库引擎
if db_settings.DB_TYPE == "sqlite":
    async_engine = create_async_engine(
        db_settings.async_database_url,
        echo=db_settings.DB_ECHO,
        connect_args={"check_same_thread": False}
    )
else:
    async_engine = create_async_engine(
        db_settings.async_database_url,
        pool_size=db_settings.DB_POOL_SIZE,
        max_overflow=db_settings.DB_MAX_OVERFLOW,
        pool_timeout=db_settings.DB_POOL_TIMEOUT,
        pool_recycle=db_settings.DB_POOL_RECYCLE,
        echo=db_settings.DB_ECHO,
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """获取数据库会话（同步）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """获取数据库会话（异步）"""
    async with AsyncSessionLocal() as session:
        yield session


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)


async def init_async_db():
    """异步初始化数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)