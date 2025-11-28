#!/usr/bin/env python3
"""
将 JSON 格式的颜色数据迁移到数据库
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web_api.database import get_db_sync, ColorMapping, User
from chart.color.color_manager import DEFAULT_PALETTE


def migrate_user_colors(user_id: int, json_path: Path, db) -> int:
    """
    迁移单个用户的颜色数据
    
    Args:
        user_id: 用户ID
        json_path: JSON 文件路径
        db: 数据库会话
        
    Returns:
        迁移的颜色数量
    """
    if not json_path.exists():
        print(f"  跳过：文件不存在 {json_path}")
        return 0

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  错误：无法读取文件 {json_path}: {e}")
        return 0

    if not isinstance(data, dict):
        print(f"  跳过：无效的数据格式 {json_path}")
        return 0

    # 获取调色板顺序
    palette = data.get("__palette__", DEFAULT_PALETTE)
    palette_order_map = {name: idx + 1 for idx, name in enumerate(palette)}

    migrated_count = 0

    for name, value in data.items():
        if name == "__palette__":
            continue

        # 检查是否已存在
        existing = (
            db.query(ColorMapping)
            .filter(
                ColorMapping.user_id == user_id,
                ColorMapping.name == name,
            )
            .first()
        )

        if existing:
            print(f"  跳过：颜色 '{name}' 已存在")
            continue

        # 解析颜色数据
        if isinstance(value, str):
            # 简单格式：{"name": "color"}
            color = value
            named_color = value if value in DEFAULT_PALETTE else None
            category = None
            description = None
            aliases = None
        elif isinstance(value, dict):
            # 完整格式：{"name": {"name": ..., "color": ..., ...}}
            color = value.get("color", name)
            named_color = value.get("named_color")
            category = value.get("category")
            description = value.get("description")
            aliases = value.get("aliases")
        else:
            print(f"  跳过：无效的颜色数据 '{name}': {value}")
            continue

        # 创建数据库记录
        color_mapping = ColorMapping(
            user_id=user_id,
            name=name,
            color=color,
            named_color=named_color,
            category=category,
            description=description,
            aliases=json.dumps(aliases, ensure_ascii=False) if aliases else None,
            palette_order=palette_order_map.get(name),
        )

        db.add(color_mapping)
        migrated_count += 1

    try:
        db.commit()
        print(f"  ✅ 成功迁移 {migrated_count} 个颜色")
        return migrated_count
    except Exception as e:
        db.rollback()
        print(f"  ❌ 迁移失败: {e}")
        return 0


def main():
    """主函数"""
    print("🔄 开始迁移颜色数据到数据库...\n")

    # 获取数据目录
    data_dir = project_root / "data" / "colors"
    if not data_dir.exists():
        print(f"❌ 颜色数据目录不存在: {data_dir}")
        print("   如果没有现有数据，可以跳过迁移")
        return

    db = get_db_sync()
    total_migrated = 0

    # 遍历所有用户目录
    for user_dir in data_dir.iterdir():
        if not user_dir.is_dir():
            continue

        try:
            user_id = int(user_dir.name)
        except ValueError:
            print(f"⚠️  跳过无效的用户目录: {user_dir.name}")
            continue

        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"⚠️  跳过：用户 ID {user_id} 不存在")
            continue

        json_path = user_dir / "color_dict.json"
        print(f"📦 迁移用户 {user_id} ({user.username})...")

        migrated = migrate_user_colors(user_id, json_path, db)
        total_migrated += migrated

    db.close()

    print(f"\n✅ 迁移完成！共迁移 {total_migrated} 个颜色")
    print("\n💡 提示：迁移完成后，可以删除 data/colors/ 目录（可选）")


if __name__ == "__main__":
    main()

