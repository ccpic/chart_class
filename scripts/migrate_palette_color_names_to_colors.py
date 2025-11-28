"""
数据库迁移脚本：将 color_palettes 表的 color_names 列重命名为 colors

SQLite 不支持直接重命名列，需要：
1. 创建新表（带 colors 列）
2. 复制数据
3. 删除旧表
4. 重命名新表
"""

import sys
import sqlite3
from pathlib import Path
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError

# 确保可以导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_api.database import engine, Base, ColorPalette, get_db_sync, DB_PATH


def migrate_palette_column_name():
    """迁移 color_palettes 表的列名从 color_names 到 colors"""
    db = get_db_sync()
    
    try:
        # 检查表是否存在
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'color_palettes' not in tables:
            print("✅ color_palettes 表不存在，将在首次使用时自动创建")
            return 0
        
        # 检查列是否存在
        columns = [col['name'] for col in inspector.get_columns('color_palettes')]
        
        if 'colors' in columns:
            print("✅ color_palettes.colors 列已存在，无需迁移")
            return 0
        
        if 'color_names' not in columns:
            print("⚠️  color_palettes.color_names 列不存在，将创建新表")
            # 删除旧表并重新创建
            db.execute(text("DROP TABLE IF EXISTS color_palettes"))
            Base.metadata.create_all(bind=engine, tables=[ColorPalette.__table__])
            print("✅ 已重新创建 color_palettes 表（带 colors 列）")
            return 0
        
        print("🔄 开始迁移 color_palettes 表...")
        print("   将 color_names 列重命名为 colors")
        
        # 获取现有数据
        result = db.execute(text("SELECT id, user_id, name, is_default, color_names, created_at, updated_at FROM color_palettes"))
        rows = result.fetchall()
        
        print(f"   找到 {len(rows)} 条调色板记录")
        
        # 删除可能存在的临时表
        db.execute(text("DROP TABLE IF EXISTS color_palettes_new"))
        
        # 创建新表（带 colors 列）
        db.execute(text("""
            CREATE TABLE color_palettes_new (
                id INTEGER NOT NULL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                is_default BOOLEAN NOT NULL,
                colors VARCHAR(2000) NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                CONSTRAINT uq_user_palette_name UNIQUE (user_id, name)
            )
        """))
        
        # 创建索引（如果不存在）
        try:
            db.execute(text("CREATE INDEX ix_color_palettes_user_id ON color_palettes_new (user_id)"))
        except OperationalError as e:
            if "already exists" not in str(e).lower():
                raise
        
        # 使用 SQLite 原始连接复制数据
        db.close()  # 关闭 SQLAlchemy 会话
        
        # 使用原始 SQLite 连接
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # 复制数据（将 color_names 的值复制到 colors）
        cursor.execute("SELECT id, user_id, name, is_default, color_names, created_at, updated_at FROM color_palettes")
        rows = cursor.fetchall()
        
        for row in rows:
            # 确保布尔值转换为整数（SQLite 使用 0/1）
            is_default = 1 if row[3] else 0
            cursor.execute("""
                INSERT INTO color_palettes_new 
                (id, user_id, name, is_default, colors, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row[0],  # id
                row[1],  # user_id
                row[2],  # name
                is_default,   # is_default (转换为 0/1)
                row[4],  # color_names -> colors
                row[5],  # created_at
                row[6],  # updated_at
            ))
        
        conn.commit()
        conn.close()
        
        # 重新打开 SQLAlchemy 会话
        db = get_db_sync()
        
        # 删除旧表并重命名新表（使用原始 SQLite 连接）
        db.close()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE color_palettes")
        cursor.execute("ALTER TABLE color_palettes_new RENAME TO color_palettes")
        
        conn.commit()
        conn.close()
        
        # 重新打开 SQLAlchemy 会话
        db = get_db_sync()
        
        print(f"✅ 成功迁移 {len(rows)} 条记录")
        print("✅ color_palettes 表迁移完成")
        
        return 0
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(migrate_palette_column_name())

