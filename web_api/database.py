"""
数据库模型和初始化
使用 SQLAlchemy ORM 管理用户数据
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, UniqueConstraint, Text
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
    """颜色映射模型（已移除调色板相关字段）"""
    __tablename__ = "color_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID，支持用户隔离
    name = Column(String(100), nullable=False)  # 颜色名称
    color = Column(String(20), nullable=False)  # HEX 颜色值
    named_color = Column(String(50), nullable=True)  # matplotlib 命名颜色
    category = Column(String(50), nullable=True)  # 分类
    description = Column(String(255), nullable=True)  # 描述
    aliases = Column(String(500), nullable=True)  # 别名列表（JSON 字符串）
    # 注意：palette_order 已移除，调色板功能独立到 ColorPalette 表
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 唯一约束：同一用户不能有重复的颜色名称
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_color_name"),
    )

    def __repr__(self):
        return f"<ColorMapping(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class ColorPalette(Base):
    """调色板模型（独立管理颜色值，与颜色映射完全分离）"""
    __tablename__ = "color_palettes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID，支持用户隔离
    name = Column(String(100), nullable=False)  # 调色板名称（如"默认"、"主题1"）
    is_default = Column(Boolean, default=False, nullable=False)  # 是否默认调色板
    colors = Column(String(2000), nullable=False)  # 颜色值列表（JSON 字符串，存储 HEX 或命名颜色）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 唯一约束：同一用户不能有重复的调色板名称
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_palette_name"),
    )

    def __repr__(self):
        return f"<ColorPalette(id={self.id}, user_id={self.user_id}, name='{self.name}', is_default={self.is_default})>"


class SavedChart(Base):
    """保存的图表模型（用户隔离）"""
    __tablename__ = "saved_charts"

    id = Column(String(36), primary_key=True, index=True)  # UUID 字符串
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID，支持用户隔离
    name = Column(String(200), nullable=False)  # 图表名称
    tags = Column(String(1000), nullable=True)  # 标签列表（JSON 字符串）
    canvas = Column(Text, nullable=False)  # 画布配置（JSON 字符串）
    subplots = Column(Text, nullable=False)  # 子图列表（JSON 字符串）
    version = Column(String(20), default="1.0", nullable=False)  # 数据格式版本
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 唯一约束：同一用户不能有重复的图表ID（虽然ID是UUID，但为了数据完整性）
    __table_args__ = (
        UniqueConstraint("user_id", "id", name="uq_user_chart_id"),
    )

    def __repr__(self):
        return f"<SavedChart(id='{self.id}', user_id={self.user_id}, name='{self.name}')>"


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

