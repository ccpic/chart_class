#!/usr/bin/env python3
"""
创建超级管理员脚本
用法: python scripts/create_superadmin.py --username admin --password admin123
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web_api.database import init_db, get_db_sync, User, UserRole
from web_api.auth import get_password_hash


def create_superadmin(username: str, password: str, email: str = None):
    """创建超级管理员账户"""
    # 初始化数据库
    init_db()
    
    # 获取数据库会话
    db = get_db_sync()
    
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ 错误: 用户名 '{username}' 已存在")
            return False
        
        # 检查邮箱是否已存在（如果提供）
        if email:
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                print(f"❌ 错误: 邮箱 '{email}' 已被使用")
                return False
        
        # 创建超级管理员
        hashed_password = get_password_hash(password)
        superadmin = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=UserRole.SUPERADMIN.value,
            is_active=True,
        )
        
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        
        print(f"✅ 成功创建超级管理员账户:")
        print(f"   - 用户名: {username}")
        if email:
            print(f"   - 邮箱: {email}")
        print(f"   - 角色: {superadmin.role}")
        print(f"   - ID: {superadmin.id}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建失败: {str(e)}")
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="创建超级管理员账户")
    parser.add_argument("--username", required=True, help="用户名")
    parser.add_argument("--password", required=True, help="密码")
    parser.add_argument("--email", help="邮箱（可选）")
    
    args = parser.parse_args()
    
    # 验证密码强度（简单检查）
    if len(args.password) < 6:
        print("⚠️  警告: 密码长度建议至少 6 个字符")
    
    # 创建超级管理员
    success = create_superadmin(args.username, args.password, args.email)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

