"""
数据库模型和初始化
使用 SQLAlchemy ORM 管理用户数据
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Optional

# 数据库路径
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "chart_class.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要这个参数
    echo=False,  # 设置为 True 可以查看 SQL 语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


class UserRole(str, Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class ColorMapping(Base):
    """颜色映射模型"""
    __tablename__ = "color_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID，支持用户隔离
    name = Column(String(100), nullable=False)  # 颜色名称
    color = Column(String(20), nullable=False)  # HEX 颜色值
    named_color = Column(String(50), nullable=True)  # matplotlib 命名颜色
    category = Column(String(50), nullable=True)  # 分类
    description = Column(String(255), nullable=True)  # 描述
    aliases = Column(String(500), nullable=True)  # 别名列表（JSON 字符串）
    palette_order = Column(Integer, nullable=True)  # 调色板顺序（NULL 表示不在调色板中）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 唯一约束：同一用户不能有重复的颜色名称
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_color_name"),
    )

    def __repr__(self):
        return f"<ColorMapping(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print(f"数据库已初始化: {DB_PATH}")


def get_db() -> Session:
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync() -> Session:
    """同步获取数据库会话（用于脚本）"""
    return SessionLocal()

