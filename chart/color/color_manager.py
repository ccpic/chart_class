"""
颜色管理 API
提供增删改查接口，支持前后端使用
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json
from pathlib import Path

# 数据文件路径（项目根目录的 data 文件夹）
DATA_DIR = Path(__file__).parent.parent.parent / "data"
COLOR_JSON_PATH = DATA_DIR / "color_dict.json"

DEFAULT_PALETTE = [
    "teal",
    "crimson",
    "navy",
    "darkorange",
    "darkgreen",
    "olivedrab",
    "purple",
    "pink",
    "deepskyblue",
    "saddlebrown",
    "tomato",
    "cornflowerblue",
    "magenta",
]

DEFAULT_COLOR_MAP: Dict[str, str] = {name: name for name in DEFAULT_PALETTE}


@dataclass
class ColorMapping:
    """颜色映射数据类 - 包含名称、颜色值和可选的命名颜色"""

    name: str
    color: str  # 永远是 HEX 值
    named_color: str | None = None  # 可选的 matplotlib 命名颜色
    category: str | None = None
    description: str | None = None
    aliases: list[str] | None = None

    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        result: Dict[str, Any] = {"name": self.name, "color": self.color}
        if self.named_color:
            result["named_color"] = self.named_color
        if self.category:
            result["category"] = self.category
        if self.description:
            result["description"] = self.description
        if self.aliases:
            result["aliases"] = self.aliases
        return result


class ColorManager:
    """
    颜色管理器

    功能:
    - 增删改查颜色映射
    - 持久化到 JSON
    - 支持分类和别名
    - 验证颜色值
    """

    def __init__(self, json_path: Optional[str] = None):
        """
        初始化颜色管理器

        Args:
            json_path: JSON 文件路径，默认使用 data/color_dict.json
        """
        self.json_path: Path = Path(json_path) if json_path else COLOR_JSON_PATH
        self._colors: dict[str, ColorMapping] = {}
        self.palette: list[str] = list(DEFAULT_PALETTE)
        self._load_from_json()
        changed = self._ensure_default_colors()
        self._sync_palette_with_colors()
        if changed:
            self._save_to_json()

    def _load_from_json(self):
        """从 JSON 文件加载颜色"""
        if not self.json_path.exists():
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 兼容两种格式
            if isinstance(data, dict):
                for name, value in data.items():
                    if name == "__palette__":
                        if isinstance(value, list):
                            cleaned = [
                                str(item)
                                for item in value
                                if isinstance(item, str) and item
                            ]
                            if cleaned:
                                self.palette = cleaned
                        continue
                    if isinstance(value, str):
                        # 简单映射: {"name": "color"}
                        self._colors[name] = ColorMapping(name=name, color=value)
                    elif isinstance(value, dict):
                        # 完整对象: {"name": {"name": ..., "color": ..., ...}}
                        # 确保 name 字段存在
                        if "name" not in value:
                            value["name"] = name
                        self._colors[name] = ColorMapping(**value)
        except Exception as e:
            print(f"警告: 加载颜色文件失败 - {e}")

    def _ensure_default_colors(self) -> bool:
        """
        确保默认调色板中的颜色在当前颜色集合中存在。
        如缺失则自动创建，返回是否发生修改。
        """
        changed = False
        for name in DEFAULT_PALETTE:
            if name not in self._colors:
                color_value = DEFAULT_COLOR_MAP.get(name, name)
                self._colors[name] = ColorMapping(
                    name=name,
                    color=color_value,
                    named_color=name,
                )
                changed = True
        return changed

    def _save_to_json(self):
        """保存到 JSON 文件"""
        self.json_path.parent.mkdir(parents=True, exist_ok=True)

        # 导出为完整格式（保存所有字段）
        full_dict: dict[str, Any] = {
            name: mapping.to_dict() for name, mapping in self._colors.items()
        }
        full_dict["__palette__"] = self.palette

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(full_dict, f, ensure_ascii=False, indent=2)

    def _sync_palette_with_colors(self):
        """确保调色板与当前颜色集合保持同步"""
        existing_names = list(self._colors.keys())
        filtered = [name for name in self.palette if name in self._colors]
        for name in existing_names:
            if name not in filtered:
                filtered.append(name)
        if not filtered:
            filtered = existing_names or list(DEFAULT_PALETTE)
        self.palette = filtered

    # ===== CRUD 操作 =====

    def add(
        self,
        name: str,
        color: str,
        named_color: str | None = None,
        overwrite: bool = False,
        category: str | None = None,
        description: str | None = None,
        aliases: list[str] | None = None,
    ) -> bool:
        """
        添加颜色映射

        Args:
            name: 颜色名称
            color: 颜色值（支持 hex, rgb, 命名颜色）
            named_color: 可选的 matplotlib 命名颜色
            overwrite: 是否覆盖已存在的

        Returns:
            bool: 是否成功添加
        """
        if name in self._colors and not overwrite:
            return False

        self._colors[name] = ColorMapping(
            name=name,
            color=color,
            named_color=named_color,
            category=category,
            description=description,
            aliases=aliases,
        )
        if name not in self.palette:
            self.palette.append(name)
        self._save_to_json()
        return True

    def get(self, name: str) -> ColorMapping | None:
        """
        获取颜色映射

        Args:
            name: 颜色名称

        Returns:
            ColorMapping 或 None
        """
        return self._colors.get(name)

    def get_color(self, name: str, default: str = "#808080") -> str:
        """
        获取颜色值（快捷方法）

        Args:
            name: 颜色名称
            default: 默认颜色

        Returns:
            颜色字符串
        """
        mapping = self._colors.get(name)
        return mapping.color if mapping else default

    def update(
        self,
        name: str,
        color: str | None = None,
        named_color: str | None = None,
        category: str | None = None,
        description: str | None = None,
        aliases: list[str] | None = None,
    ) -> bool:
        """
        更新颜色映射

        Args:
            name: 颜色名称
            color: 新颜色值（None 表示不更新）
            named_color: 新的命名颜色（None 表示不更新，空字符串表示清除）

        Returns:
            bool: 是否成功更新
        """
        if name not in self._colors:
            return False

        mapping = self._colors[name]
        if color is not None:
            mapping.color = color
        # 对于 named_color，需要区分"未提供"和"清除"
        # 前端传递 undefined 会变成 None（不在请求中），传递 null 也会变成 None
        # 这里我们假设：如果参数存在但为 None，表示清除；如果参数不存在，不更新
        # 但 Python 无法区分这两种情况，需要在 API 层处理
        if named_color is not None:
            if named_color == "":
                mapping.named_color = None  # 清除
            else:
                mapping.named_color = named_color

        if category is not None:
            mapping.category = category or None
        if description is not None:
            mapping.description = description or None
        if aliases is not None:
            mapping.aliases = aliases or None

        self._save_to_json()
        return True

    def delete(self, name: str) -> bool:
        """
        删除颜色映射

        Args:
            name: 颜色名称

        Returns:
            bool: 是否成功删除
        """
        if name not in self._colors:
            return False

        del self._colors[name]
        if name in self.palette:
            self.palette.remove(name)
        self._sync_palette_with_colors()
        self._save_to_json()
        return True

    def list_all(self, search: str | None = None) -> list[ColorMapping]:
        """
        列出所有颜色映射

        Args:
            search: 搜索关键词（匹配名称）

        Returns:
            颜色映射列表
        """
        results = list(self._colors.values())

        if search:
            search_lower = search.lower()
            results = [m for m in results if search_lower in m.name.lower()]

        order_map = {name: idx for idx, name in enumerate(self.palette)}
        results.sort(key=lambda mapping: order_map.get(mapping.name, len(order_map)))

        return results

    def to_dict(self) -> Dict[str, str]:
        """
        导出为简单字典（name -> color）

        Returns:
            Dict[str, str]: 颜色字典
        """
        return {name: mapping.color for name, mapping in self._colors.items()}

    def get_palette(self) -> List[str]:
        """获取调色板顺序"""
        self._sync_palette_with_colors()
        return list(self.palette)

    def set_palette(self, palette: List[str]):
        """设置调色板顺序"""
        cleaned: List[str] = []
        seen = set()
        for name in palette:
            if name in self._colors and name not in seen:
                cleaned.append(name)
                seen.add(name)
        for name in self._colors:
            if name not in seen:
                cleaned.append(name)
        if not cleaned:
            cleaned = list(self._colors.keys()) or list(DEFAULT_PALETTE)
        self.palette = cleaned
        self._save_to_json()

    def export_to_typescript(self, output_path: str | Path):
        """
        导出为 TypeScript 文件

        Args:
            output_path: 输出文件路径
        """
        # 按分类组织
        by_category = {}
        uncategorized = {}

        for name, mapping in self._colors.items():
            if mapping.category:
                if mapping.category not in by_category:
                    by_category[mapping.category] = {}
                by_category[mapping.category][name] = mapping.color
            else:
                uncategorized[name] = mapping.color

        # 生成 TypeScript 代码
        ts_content = """/**
 * 颜色映射配置（自动生成）
 * 请勿手动编辑，使用 ColorManager API 修改
 */

export interface ColorMapping {
  name: string;
  color: string;
  category?: string;
  description?: string;
  aliases?: string[];
}

"""

        # 分类颜色
        if by_category:
            ts_content += "// 按分类组织的颜色\n"
            ts_content += "export const COLOR_CATEGORIES = {\n"
            for category, colors in sorted(by_category.items()):
                ts_content += f"  {category}: {{\n"
                for name, color in sorted(colors.items()):
                    safe_name = name.replace('"', '\\"')
                    ts_content += f'    "{safe_name}": "{color}",\n'
                ts_content += "  },\n"
            ts_content += "} as const;\n\n"

        # 扁平化字典
        all_colors = self.to_dict()
        ts_content += "// 扁平化颜色字典\n"
        ts_content += "export const COLOR_DICT: Record<string, string> = {\n"
        for name, color in sorted(all_colors.items()):
            safe_name = name.replace('"', '\\"')
            ts_content += f'  "{safe_name}": "{color}",\n'
        ts_content += "} as const;\n\n"

        # 辅助函数
        ts_content += """
/**
 * 获取颜色值
 * @param name - 颜色名称
 * @param defaultColor - 默认颜色
 * @returns 颜色字符串
 */
export function getColor(name: string, defaultColor: string = "#808080"): string {
  return COLOR_DICT[name] || defaultColor;
}

/**
 * 获取分类下的所有颜色
 * @param category - 分类名称
 * @returns 颜色字典
 */
export function getColorsByCategory(category: keyof typeof COLOR_CATEGORIES): Record<string, string> {
  return COLOR_CATEGORIES[category] || {};
}
"""

        # 写入文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ts_content)


# ===== 全局实例 =====
_global_manager: Optional[ColorManager] = None


def get_color_manager() -> ColorManager:
    """获取全局颜色管理器实例"""
    global _global_manager
    if _global_manager is None:
        _global_manager = ColorManager()
    return _global_manager


# ===== 便捷函数 =====


def add_color(name: str, color: str, **kwargs) -> bool:
    """添加颜色（便捷函数）"""
    return get_color_manager().add(name, color, **kwargs)


def get_color(name: str, default: str = "#808080") -> str:
    """获取颜色（便捷函数）"""
    return get_color_manager().get_color(name, default)


def update_color(name: str, **kwargs) -> bool:
    """更新颜色（便捷函数）"""
    return get_color_manager().update(name, **kwargs)


def delete_color(name: str) -> bool:
    """删除颜色（便捷函数）"""
    return get_color_manager().delete(name)


def list_colors(**kwargs) -> List[ColorMapping]:
    """列出颜色（便捷函数）"""
    return get_color_manager().list_all(**kwargs)
