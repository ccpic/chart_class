"""
数据库版本的颜色管理器
使用 SQLite 数据库存储颜色映射，解决并发写问题
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import json

from web_api.database import ColorMapping
from chart.color.color_manager import ColorMapping as ColorMappingData


class ColorDBManager:
    """
    数据库版本的颜色管理器
    
    功能:
    - 增删改查颜色映射（使用数据库）
    - 支持用户隔离
    - 解决并发写问题（数据库事务保证）
    
    注意：调色板功能已独立到 PaletteDBManager
    """

    def __init__(self, db: Session, user_id: int):
        """
        初始化颜色管理器
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        注意：颜色映射完全由用户控制，不自动创建任何默认颜色。
        默认调色板由 PaletteDBManager 管理，与颜色映射完全分离。
        """
        self.db = db
        self.user_id = user_id
        # 不再自动创建默认颜色映射，颜色映射完全由用户管理

    def add(
        self,
        name: str,
        color: str,
        named_color: Optional[str] = None,
        overwrite: bool = False,
        category: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[List[str]] = None,
    ) -> bool:
        """
        添加颜色映射
        
        Args:
            name: 颜色名称
            color: 颜色值（HEX）
            named_color: matplotlib 命名颜色
            overwrite: 是否覆盖已存在的
            category: 分类
            description: 描述
            aliases: 别名列表
            
        Returns:
            bool: 是否成功添加
        """
        existing = (
            self.db.query(ColorMapping)
            .filter(
                and_(ColorMapping.user_id == self.user_id, ColorMapping.name == name)
            )
            .first()
        )

        if existing and not overwrite:
            return False

        aliases_json = json.dumps(aliases, ensure_ascii=False) if aliases else None

        if existing:
            # 更新现有记录
            existing.color = color
            existing.named_color = named_color
            existing.category = category
            existing.description = description
            existing.aliases = aliases_json
            existing.updated_at = datetime.utcnow()
        else:
            # 创建新记录（不设置调色板顺序）
            color_mapping = ColorMapping(
                user_id=self.user_id,
                name=name,
                color=color,
                named_color=named_color,
                category=category,
                description=description,
                aliases=aliases_json,
            )
            self.db.add(color_mapping)

        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def get(self, name: str) -> Optional[ColorMappingData]:
        """
        获取颜色映射
        
        Args:
            name: 颜色名称
            
        Returns:
            ColorMappingData 或 None
        """
        mapping = (
            self.db.query(ColorMapping)
            .filter(
                and_(ColorMapping.user_id == self.user_id, ColorMapping.name == name)
            )
            .first()
        )

        if not mapping:
            return None

        aliases = (
            json.loads(mapping.aliases) if mapping.aliases else None
        )

        return ColorMappingData(
            name=mapping.name,
            color=mapping.color,
            named_color=mapping.named_color,
            category=mapping.category,
            description=mapping.description,
            aliases=aliases,
        )

    def get_color(self, name: str, default: str = "#808080") -> str:
        """
        获取颜色值（快捷方法）
        
        Args:
            name: 颜色名称
            default: 默认颜色
            
        Returns:
            颜色字符串
        """
        mapping = self.get(name)
        return mapping.color if mapping else default

    def update(
        self,
        name: str,
        color: Optional[str] = None,
        named_color: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[List[str]] = None,
    ) -> bool:
        """
        更新颜色映射
        
        Args:
            name: 颜色名称
            color: 新颜色值（None 表示不更新）
            named_color: 新的命名颜色（None 表示不更新，空字符串表示清除）
            category: 分类
            description: 描述
            aliases: 别名列表
            
        Returns:
            bool: 是否成功更新
        """
        mapping = (
            self.db.query(ColorMapping)
            .filter(
                and_(ColorMapping.user_id == self.user_id, ColorMapping.name == name)
            )
            .first()
        )

        if not mapping:
            return False

        if color is not None:
            mapping.color = color
        if named_color is not None:
            mapping.named_color = named_color if named_color else None
        if category is not None:
            mapping.category = category if category else None
        if description is not None:
            mapping.description = description if description else None
        if aliases is not None:
            mapping.aliases = (
                json.dumps(aliases, ensure_ascii=False) if aliases else None
            )

        mapping.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, name: str) -> bool:
        """
        删除颜色映射
        
        Args:
            name: 颜色名称
            
        Returns:
            bool: 是否成功删除
        """
        mapping = (
            self.db.query(ColorMapping)
            .filter(
                and_(ColorMapping.user_id == self.user_id, ColorMapping.name == name)
            )
            .first()
        )

        if not mapping:
            return False

        self.db.delete(mapping)

        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def list_all(self, search: Optional[str] = None) -> List[ColorMappingData]:
        """
        列出所有颜色映射
        
        Args:
            search: 搜索关键词（匹配名称）
            
        Returns:
            颜色映射列表
        """
        query = self.db.query(ColorMapping).filter(
            ColorMapping.user_id == self.user_id
        )

        if search:
            query = query.filter(ColorMapping.name.contains(search))

        mappings = query.all()

        results = []
        for mapping in mappings:
            aliases = (
                json.loads(mapping.aliases) if mapping.aliases else None
            )
            results.append(
                ColorMappingData(
                    name=mapping.name,
                    color=mapping.color,
                    named_color=mapping.named_color,
                    category=mapping.category,
                    description=mapping.description,
                    aliases=aliases,
                )
            )

        # 按名称排序（不再按调色板顺序，调色板由 PaletteDBManager 管理）
        results.sort(key=lambda m: m.name)

        return results

    def to_dict(self) -> Dict[str, str]:
        """
        导出为简单字典（name -> color）
        
        Returns:
            Dict[str, str]: 颜色字典
        """
        mappings = self.list_all()
        return {mapping.name: mapping.color for mapping in mappings}

