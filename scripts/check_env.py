#!/usr/bin/env python3
"""
启动前环境检查脚本
用于验证生产环境的关键配置
"""

import os
import sys
from pathlib import Path


def check_jwt_secret():
    """检查 JWT 秘钥配置"""
    secret_key = os.getenv("JWT_SECRET_KEY")
    environment = (
        os.getenv("ENVIRONMENT")
        or os.getenv("NODE_ENV")
        or os.getenv("FLASK_ENV")
        or "development"
    ).lower()
    
    # 检查是否在 Docker 中
    if os.path.exists("/.dockerenv"):
        environment = "production"
    
    if not secret_key:
        if environment in ("production", "prod"):
            print("❌ 错误: JWT_SECRET_KEY 环境变量未设置！", file=sys.stderr)
            print("\n生产环境必须设置一个强随机秘钥（至少 32 字符）", file=sys.stderr)
            print("\n生成方法：", file=sys.stderr)
            print("  - Linux/Mac: openssl rand -hex 32", file=sys.stderr)
            print("  - Windows: python -c \"import secrets; print(secrets.token_hex(32))\"", file=sys.stderr)
            print("  - Python: python -c \"import secrets; print(secrets.token_urlsafe(32))\"", file=sys.stderr)
            return False
        else:
            print("⚠️  警告: JWT_SECRET_KEY 未设置，将使用开发环境默认值（不安全）")
            return True
    
    # 检查秘钥强度
    if len(secret_key) < 32:
        if environment in ("production", "prod"):
            print(f"❌ 错误: JWT_SECRET_KEY 强度不足（长度: {len(secret_key)}）", file=sys.stderr)
            print("要求：至少 32 字符", file=sys.stderr)
            return False
        else:
            print(f"⚠️  警告: JWT_SECRET_KEY 强度不足（长度: {len(secret_key)}），建议至少 32 字符")
            return True
    
    # 检查是否是默认值
    forbidden_values = [
        "your-secret-key-change-in-production",
        "dev-secret-key-change-in-production-not-secure",
        "secret",
        "password",
        "123456",
    ]
    if secret_key.lower() in [v.lower() for v in forbidden_values]:
        if environment in ("production", "prod"):
            print(f"❌ 错误: JWT_SECRET_KEY 使用了禁止的默认值", file=sys.stderr)
            return False
        else:
            print(f"⚠️  警告: JWT_SECRET_KEY 使用了不安全的默认值")
            return True
    
    print(f"✅ JWT_SECRET_KEY 已配置（长度: {len(secret_key)}）")
    return True


def check_api_url():
    """检查前端 API URL 配置"""
    api_url = os.getenv("NEXT_PUBLIC_API_URL")
    environment = (
        os.getenv("ENVIRONMENT")
        or os.getenv("NODE_ENV")
        or "development"
    ).lower()
    
    if not api_url:
        if environment in ("production", "prod"):
            print("❌ 错误: NEXT_PUBLIC_API_URL 环境变量未设置！", file=sys.stderr)
            print("生产环境必须设置前端 API URL（不能是 localhost）", file=sys.stderr)
            return False
        else:
            print("⚠️  警告: NEXT_PUBLIC_API_URL 未设置，将使用默认值 http://localhost:8001")
            return True
    
    # 检查是否是 localhost（生产环境不允许）
    if environment in ("production", "prod") and "localhost" in api_url.lower():
        print("❌ 错误: 生产环境不能使用 localhost 作为 API URL", file=sys.stderr)
        print(f"当前值: {api_url}", file=sys.stderr)
        print("请设置为实际可访问的地址（例如: https://your-domain.com/api）", file=sys.stderr)
        return False
    
    print(f"✅ NEXT_PUBLIC_API_URL 已配置: {api_url}")
    return True


def main():
    """主函数"""
    print("🔍 检查环境配置...\n")
    
    checks = [
        ("JWT 秘钥", check_jwt_secret),
        ("前端 API URL", check_api_url),
    ]
    
    failed = []
    for name, check_func in checks:
        print(f"检查 {name}...")
        if not check_func():
            failed.append(name)
        print()
    
    if failed:
        print(f"❌ 检查失败: {', '.join(failed)}", file=sys.stderr)
        print("\n请修复上述问题后重试", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ 所有检查通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()

