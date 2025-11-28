"""
数据库版本的调色板管理器
独立管理颜色调色板，与颜色映射完全分离
调色板直接存储颜色值（HEX 或命名颜色），不依赖颜色映射
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import json

from web_api.database import ColorPalette
from chart.color.color_manager import DEFAULT_PALETTE


class PaletteDBManager:
    """
    数据库版本的调色板管理器
    
    功能:
    - 管理调色板（直接存储颜色值，如 HEX 或命名颜色）
    - 支持用户隔离
    - 支持多个调色板（默认调色板 + 自定义调色板）
    - 与颜色映射完全分离，独立管理颜色
    - 解决并发写问题（数据库事务保证）
    """

    def __init__(self, db: Session, user_id: int):
        """
        初始化调色板管理器
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        """
        self.db = db
        self.user_id = user_id
        self._ensure_default_palette()

    def _ensure_default_palette(self):
        """确保用户拥有默认调色板（使用默认颜色值）"""
        default_palette = (
            self.db.query(ColorPalette)
            .filter(
                and_(
                    ColorPalette.user_id == self.user_id,
                    ColorPalette.is_default == True,
                )
            )
            .first()
        )

        if not default_palette:
            # 创建默认调色板（直接使用颜色值，不依赖颜色映射）
            # DEFAULT_PALETTE 中的值既是名称也是颜色值（matplotlib 命名颜色）
            colors_json = json.dumps(DEFAULT_PALETTE, ensure_ascii=False)
            default_palette = ColorPalette(
                user_id=self.user_id,
                name="默认",
                is_default=True,
                colors=colors_json,
            )
            self.db.add(default_palette)
            self.db.commit()

    def get_default_palette(self) -> List[str]:
        """
        获取默认调色板
        
        Returns:
            颜色值列表（HEX 或命名颜色）
        """
        default_palette = (
            self.db.query(ColorPalette)
            .filter(
                and_(
                    ColorPalette.user_id == self.user_id,
                    ColorPalette.is_default == True,
                )
            )
            .first()
        )

        if not default_palette:
            return list(DEFAULT_PALETTE)

        try:
            colors = json.loads(default_palette.colors)
            return colors if isinstance(colors, list) else list(DEFAULT_PALETTE)
        except (json.JSONDecodeError, TypeError):
            return list(DEFAULT_PALETTE)

    def set_default_palette(self, colors: List[str]) -> bool:
        """
        设置默认调色板
        
        Args:
            colors: 颜色值列表（HEX 或命名颜色）
            
        Returns:
            bool: 是否成功
        """
        default_palette = (
            self.db.query(ColorPalette)
            .filter(
                and_(
                    ColorPalette.user_id == self.user_id,
                    ColorPalette.is_default == True,
                )
            )
            .first()
        )

        if not default_palette:
            # 创建默认调色板
            colors_json = json.dumps(colors, ensure_ascii=False)
            default_palette = ColorPalette(
                user_id=self.user_id,
                name="默认",
                is_default=True,
                colors=colors_json,
            )
            self.db.add(default_palette)
        else:
            # 更新现有调色板
            default_palette.colors = json.dumps(colors, ensure_ascii=False)
            default_palette.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def create_palette(self, name: str, colors: List[str]) -> bool:
        """
        创建新调色板
        
        Args:
            name: 调色板名称
            colors: 颜色值列表（HEX 或命名颜色）
            
        Returns:
            bool: 是否成功
        """
        # 检查名称是否已存在
        existing = (
            self.db.query(ColorPalette)
            .filter(
                and_(ColorPalette.user_id == self.user_id, ColorPalette.name == name)
            )
            .first()
        )

        if existing:
            return False

        colors_json = json.dumps(colors, ensure_ascii=False)
        palette = ColorPalette(
            user_id=self.user_id,
            name=name,
            is_default=False,
            colors=colors_json,
        )

        self.db.add(palette)

        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def list_palettes(self) -> List[Dict[str, Any]]:
        """
        列出所有调色板
        
        Returns:
            调色板列表
        """
        palettes = (
            self.db.query(ColorPalette)
            .filter(ColorPalette.user_id == self.user_id)
            .order_by(ColorPalette.is_default.desc(), ColorPalette.created_at.asc())
            .all()
        )

        results = []
        for palette in palettes:
            try:
                colors = json.loads(palette.colors)
            except (json.JSONDecodeError, TypeError):
                colors = []

            results.append(
                {
                    "id": palette.id,
                    "name": palette.name,
                    "is_default": palette.is_default,
                    "colors": colors,
                    "color_count": len(colors),
                    "created_at": palette.created_at.isoformat(),
                    "updated_at": palette.updated_at.isoformat(),
                }
            )

        return results

    def get_palette(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定调色板
        
        Args:
            name: 调色板名称
            
        Returns:
            调色板信息或 None
        """
        palette = (
            self.db.query(ColorPalette)
            .filter(
                and_(ColorPalette.user_id == self.user_id, ColorPalette.name == name)
            )
            .first()
        )

        if not palette:
            return None

        try:
            colors = json.loads(palette.colors)
        except (json.JSONDecodeError, TypeError):
            colors = []

        return {
            "id": palette.id,
            "name": palette.name,
            "is_default": palette.is_default,
            "colors": colors,
            "color_count": len(colors),
            "created_at": palette.created_at.isoformat(),
            "updated_at": palette.updated_at.isoformat(),
        }

    def update_palette(self, name: str, colors: List[str]) -> bool:
        """
        更新调色板
        
        Args:
            name: 调色板名称
            colors: 新的颜色值列表（HEX 或命名颜色）
            
        Returns:
            bool: 是否成功
        """
        palette = (
            self.db.query(ColorPalette)
            .filter(
                and_(ColorPalette.user_id == self.user_id, ColorPalette.name == name)
            )
            .first()
        )

        if not palette:
            return False

        palette.colors = json.dumps(colors, ensure_ascii=False)
        palette.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_palette(self, name: str) -> bool:
        """
        删除调色板（不能删除默认调色板）
        
        Args:
            name: 调色板名称
            
        Returns:
            bool: 是否成功
        """
        palette = (
            self.db.query(ColorPalette)
            .filter(
                and_(ColorPalette.user_id == self.user_id, ColorPalette.name == name)
            )
            .first()
        )

        if not palette:
            return False

        # 不能删除默认调色板
        if palette.is_default:
            return False

        self.db.delete(palette)

        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

