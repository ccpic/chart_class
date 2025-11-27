# 部署关键问题修复说明

## 修复内容

本次修复解决了部署前检查中发现的两个高风险问题：

### 1. JWT 秘钥强制环境变量 ✅

**问题**：`web_api/auth.py` 使用硬编码默认值，生产环境存在安全风险。

**修复**：
- 修改 `web_api/auth.py`，强制要求 `JWT_SECRET_KEY` 环境变量
- 如果未设置，服务启动时会抛出异常，防止使用默认值

**影响**：生产环境部署时必须设置 `JWT_SECRET_KEY`，否则服务无法启动。

### 2. 前端 API URL 配置 ✅

**问题**：前端 API URL 硬编码为 `localhost`，生产环境浏览器无法访问。

**修复**：
- 更新 `docker/Dockerfile.frontend`，支持构建时传递 `NEXT_PUBLIC_API_URL`
- 更新 `docker/docker-compose.yml` 和 `docker-compose.prod.yml`，在构建时传递 API URL
- 更新 `docker/env.example`，添加清晰的配置说明

**影响**：生产环境部署时必须在 `.env` 文件中设置正确的 `NEXT_PUBLIC_API_URL`。

## 部署步骤

### 1. 准备环境变量文件

在 `docker/` 目录下创建 `.env` 文件：

```bash
cd docker
cp env.example .env
```

编辑 `.env` 文件，设置以下**必须**的变量：

```bash
# JWT 秘钥（必须设置）
# 生成方法：openssl rand -hex 32
JWT_SECRET_KEY=your-generated-secret-key-here

# 前端 API 地址（必须设置为实际可访问的地址）
# 不能使用 localhost（除非仅本地访问）
# 示例：
#   - 使用域名：https://your-domain.com/api
#   - 使用 IP：http://your-server-ip:8001
NEXT_PUBLIC_API_URL=http://your-server-ip:8001

# CORS 允许的来源（生产环境必须设置实际域名）
CORS_ORIGINS=http://your-frontend-domain:3000
```

### 2. 生成 JWT 秘钥

在 Windows PowerShell 中：

```powershell
# 方法1：使用 OpenSSL（如果已安装）
openssl rand -hex 32

# 方法2：使用 Python
python -c "import secrets; print(secrets.token_hex(32))"
```

将生成的秘钥复制到 `.env` 文件的 `JWT_SECRET_KEY` 中。

### 3. 构建并启动

```powershell
# 在 docker/ 目录下
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 4. 验证部署

1. **检查后端服务**：
   ```powershell
   curl http://localhost:8001/
   ```
   应该返回 JSON 响应。

2. **检查前端服务**：
   打开浏览器访问 `http://your-server-ip:3000`
   
3. **检查 API 连接**：
   打开浏览器开发者工具（F12），查看 Network 标签
   - 前端应该能成功请求后端 API
   - 如果看到 `localhost:8001` 的请求失败，说明 `NEXT_PUBLIC_API_URL` 配置错误

## 常见问题

### Q: 后端启动失败，提示 "JWT_SECRET_KEY 环境变量未设置"

**A**: 检查 `.env` 文件中是否设置了 `JWT_SECRET_KEY`，并确保 docker-compose 正确读取了 `.env` 文件。

### Q: 前端无法访问后端 API

**A**: 
1. 检查 `.env` 文件中的 `NEXT_PUBLIC_API_URL` 是否正确
2. 确保该 URL 可以从浏览器访问（不能是 `localhost`，除非仅本地访问）
3. 重新构建前端镜像：`docker-compose build frontend`

### Q: 为什么前端需要重新构建？

**A**: Next.js 的 `NEXT_PUBLIC_*` 环境变量在构建时注入到代码中，运行时无法修改。因此修改 `NEXT_PUBLIC_API_URL` 后必须重新构建前端镜像。

### Q: 如何更新 API URL？

**A**: 
1. 修改 `.env` 文件中的 `NEXT_PUBLIC_API_URL`
2. 重新构建前端：`docker-compose build frontend`
3. 重启服务：`docker-compose up -d`

## 安全建议

1. **JWT 秘钥**：
   - 使用强随机字符串（至少 32 字节）
   - 不要将 `.env` 文件提交到 Git
   - 定期轮换秘钥（需要所有用户重新登录）

2. **API URL**：
   - 生产环境使用 HTTPS
   - 配置反向代理（Nginx/Caddy）统一域名
   - 设置正确的 CORS 策略

3. **环境变量**：
   - 使用 `.env` 文件管理敏感配置
   - 确保 `.env` 文件权限正确（仅所有者可读）
   - 在 Windows Server 上考虑使用 Windows 环境变量或密钥管理服务

## 后续优化建议

参考 `docs/DEPLOYMENT_PRECHECK.md` 中的其他问题：
- 图表存储持久化（中优先级）
- 颜色 JSON 并发写保护（中优先级）
- 数据卷路径优化（中优先级）

