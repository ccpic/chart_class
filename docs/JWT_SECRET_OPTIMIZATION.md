# JWT 秘钥配置优化说明

## 优化内容

本次优化改进了 JWT 秘钥的验证和检查机制，确保生产环境的安全性。

## 主要改进

### 1. 秘钥强度验证 ✅

**位置**: `web_api/auth.py`

- 添加 `_validate_secret_key()` 函数，验证秘钥强度
- 生产环境要求：
  - 至少 32 字符
  - 不能是明显的默认值（如 "secret", "password" 等）
- 开发环境允许使用默认值，但会显示警告

### 2. 环境自动检测 ✅

**位置**: `web_api/auth.py`

- 添加 `_get_environment()` 函数，自动检测运行环境
- 检测顺序：
  1. `ENVIRONMENT` 环境变量
  2. `NODE_ENV` 环境变量
  3. `FLASK_ENV` 环境变量
  4. 检查是否在 Docker 容器中（`/.dockerenv` 文件）
  5. 默认为 `development`

### 3. 启动时校验 ✅

**位置**: `web_api/main.py`

- 添加 `_startup_checks()` 函数，在服务启动前验证配置
- 检查项：
  - JWT 秘钥是否存在和强度
  - 数据库初始化
- 记录详细的日志信息

### 4. 启动前检查脚本 ✅

**位置**: `scripts/check_env.py`

- 独立的 Python 脚本，可在 Docker 启动前运行
- 检查项：
  - JWT 秘钥配置和强度
  - 前端 API URL 配置（生产环境不能使用 localhost）
- 提供清晰的错误提示和修复建议

### 5. Docker 启动脚本集成 ✅

**位置**: `docker/docker-start.bat`

- 在启动 Docker 服务前自动运行环境检查
- 如果检查失败，阻止启动并显示错误信息

## 使用方法

### 开发环境

开发环境可以使用默认值，但会显示警告：

```bash
# 直接启动，使用默认秘钥
python web_api/main.py
```

### 生产环境

生产环境必须设置环境变量：

**方法 1: 环境变量**
```bash
# Linux/Mac
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export ENVIRONMENT=production

# Windows PowerShell
$env:JWT_SECRET_KEY = "your-generated-secret-key"
$env:ENVIRONMENT = "production"
```

**方法 2: .env 文件（Docker）**
```bash
# docker/.env
JWT_SECRET_KEY=your-generated-secret-key-here
ENVIRONMENT=production
```

**方法 3: 生成秘钥**
```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# 或
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 手动运行检查脚本

```bash
# 在项目根目录
python scripts/check_env.py
```

## 验证流程

### 启动时自动验证

1. **导入模块时** (`web_api/auth.py`):
   - 检查环境变量
   - 验证秘钥强度
   - 生产环境未设置或强度不足时抛出异常

2. **服务启动时** (`web_api/main.py`):
   - 执行 `_startup_checks()`
   - 记录配置状态到日志
   - 验证数据库连接

3. **Docker 启动前** (`docker/docker-start.bat`):
   - 运行 `scripts/check_env.py`
   - 检查失败时阻止启动

## 错误处理

### 生产环境未设置秘钥

```
❌ JWT_SECRET_KEY 环境变量未设置！
生产环境必须设置一个强随机秘钥（至少 32 字符）。
生成方法：
  - Linux/Mac: openssl rand -hex 32
  - Windows: python -c "import secrets; print(secrets.token_hex(32))"
  - Python: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 秘钥强度不足

```
❌ JWT_SECRET_KEY 强度不足！
当前秘钥长度: 16 字符
要求：至少 32 字符，且不能是默认值
生成方法：python -c "import secrets; print(secrets.token_hex(32))"
```

### 使用了禁止的默认值

```
❌ JWT_SECRET_KEY 使用了禁止的默认值
```

## 安全建议

1. **秘钥生成**：
   - 使用强随机生成器（`secrets` 模块）
   - 至少 32 字符
   - 包含字母、数字和特殊字符

2. **秘钥管理**：
   - 不要将秘钥提交到 Git
   - 使用环境变量或密钥管理服务
   - 定期轮换秘钥（需要所有用户重新登录）

3. **环境隔离**：
   - 开发、测试、生产环境使用不同的秘钥
   - 使用 `.env` 文件管理不同环境的配置

4. **日志安全**：
   - 不要在日志中输出完整的秘钥
   - 只记录秘钥长度和配置状态

## 测试

### 测试开发环境默认值

```bash
# 不设置环境变量，应该使用默认值并显示警告
python web_api/main.py
```

### 测试生产环境验证

```bash
# 设置生产环境但未设置秘钥，应该失败
export ENVIRONMENT=production
python web_api/main.py
```

### 测试秘钥强度验证

```bash
# 设置弱秘钥，应该显示警告（开发环境）或失败（生产环境）
export JWT_SECRET_KEY=weak
python web_api/main.py
```

## 相关文件

- `web_api/auth.py` - JWT 配置和验证逻辑
- `web_api/main.py` - 启动时检查
- `scripts/check_env.py` - 独立检查脚本
- `docker/docker-start.bat` - Docker 启动脚本
- `docker/env.example` - 环境变量示例

