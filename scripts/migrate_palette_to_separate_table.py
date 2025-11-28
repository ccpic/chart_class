"""
将调色板数据从 ColorMapping.palette_order 迁移到独立的 ColorPalette 表

迁移逻辑：
1. 从 ColorMapping 表中读取所有用户的 palette_order 数据
2. 为每个用户创建默认调色板（ColorPalette）
3. 将 palette_order 不为 NULL 的颜色名称按顺序写入调色板
4. 删除 ColorMapping 表中的 palette_order 列（需要手动执行 SQL，因为 SQLAlchemy 不支持直接删除列）
"""

import sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# 确保可以导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_api.database import get_db_sync, User, ColorMapping, ColorPalette, engine, Base
import json


def migrate_palette_data():
    """迁移调色板数据"""
    db = get_db_sync()

    try:
        # 检查 ColorPalette 表是否存在，如果不存在则创建
        Base.metadata.create_all(bind=engine, tables=[ColorPalette.__table__])
        print("✅ ColorPalette 表已创建或已存在")

        # 获取所有用户
        users = db.query(User).all()
        print(f"找到 {len(users)} 个用户")

        for user in users:
            user_id = user.id
            print(f"\n--- 迁移用户 {user.username} (ID: {user_id}) 的调色板数据 ---")

            # 检查是否已有默认调色板
            existing_palette = (
                db.query(ColorPalette)
                .filter(
                    ColorPalette.user_id == user_id,
                    ColorPalette.is_default == True,
                )
                .first()
            )

            if existing_palette:
                print(f"  用户 {user.username} 已有默认调色板，跳过迁移")
                continue

            # 查询该用户所有有 palette_order 的颜色映射
            color_mappings = (
                db.query(ColorMapping)
                .filter(
                    ColorMapping.user_id == user_id,
                    ColorMapping.palette_order.isnot(None),
                )
                .order_by(ColorMapping.palette_order.asc())
                .all()
            )

            if not color_mappings:
                print(f"  用户 {user.username} 没有调色板数据（palette_order 为 NULL），创建空默认调色板")
                # 创建空默认调色板
                default_palette = ColorPalette(
                    user_id=user_id,
                    name="默认",
                    is_default=True,
                    color_names=json.dumps([], ensure_ascii=False),
                )
                db.add(default_palette)
                db.commit()
                continue

            # 提取颜色名称列表（按 palette_order 排序）
            color_names = [mapping.name for mapping in color_mappings]
            print(f"  找到 {len(color_names)} 个调色板颜色: {color_names}")

            # 创建默认调色板
            color_names_json = json.dumps(color_names, ensure_ascii=False)
            default_palette = ColorPalette(
                user_id=user_id,
                name="默认",
                is_default=True,
                color_names=color_names_json,
            )
            db.add(default_palette)
            db.commit()

            print(f"  ✅ 用户 {user.username} 的调色板数据迁移完成")

        print("\n✅ 所有用户调色板数据迁移完成")

        # 提示：需要手动删除 palette_order 列
        print("\n⚠️  注意：迁移完成后，需要手动删除 ColorMapping 表中的 palette_order 列")
        print("   可以使用以下 SQL 命令（SQLite 不支持直接删除列，需要重建表）：")
        print("   或者使用 SQLite 工具手动删除该列")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 迁移失败: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(migrate_palette_data())

