# Chart Class Web API 部署检查清单

本文档提供 Windows 服务部署（NSSM + Apache 2.4）的完整检查清单。

## 前置要求

### 1. 系统要求
- [ ] Windows Server 或 Windows 10/11
- [ ] Python 3.11+ 已安装
- [ ] Apache 2.4 已安装并运行
- [ ] NSSM 已下载并添加到 PATH

### 2. 软件安装

#### NSSM 安装
- [ ] 下载 NSSM：https://nssm.cc/download
- [ ] 解压到系统 PATH 目录（如 `C:\Windows\System32`）或项目目录
- [ ] 验证安装：在命令行运行 `nssm version`

#### Apache 2.4 安装
- [ ] Apache 2.4 已安装
- [ ] Apache 服务已启动
- [ ] 验证安装：访问 `http://localhost` 查看 Apache 默认页面

## 部署步骤

### 步骤 1: Python 环境准备

- [ ] 进入项目目录：`cd D:\PyProjects\chart_class2`
- [ ] 激活虚拟环境：`.venv\Scripts\activate`
- [ ] 安装依赖：`pip install -r requirements.txt`
- [ ] 测试运行：`python web_api/main.py`
  - 应该能看到服务启动信息
  - 按 Ctrl+C 停止测试

### 步骤 2: 环境变量配置

- [ ] 创建或更新 `.env` 文件（可选，NSSM 脚本会设置环境变量）
  ```env
  UVICORN_WORKERS=4
  THREAD_POOL_SIZE=4
  UVICORN_PORT=8001
  UVICORN_HOST=127.0.0.1
  ```

### 步骤 3: NSSM 服务注册

- [ ] 以管理员身份运行 `deploy/start_service.bat`
- [ ] 检查服务状态：`nssm status ChartClassAPI`
  - 应该显示 "SERVICE_RUNNING"
- [ ] 查看日志：`type logs\service_stdout.log`
  - 应该能看到服务启动信息
  - 确认没有错误信息

### 步骤 4: 本地服务测试

- [ ] 测试健康检查端点：
  ```powershell
  curl http://127.0.0.1:8001/
  ```
  - 应该返回 JSON 响应

- [ ] 测试 API 端点：
  ```powershell
  curl http://127.0.0.1:8001/api/chart-types
  ```
  - 应该返回图表类型列表

### 步骤 5: Apache 配置

- [ ] 复制 `deploy/apache_vhost.conf` 到 Apache 配置目录：
  ```powershell
  copy deploy\apache_vhost.conf C:\Apache24\conf\extra\chart_class_vhost.conf
  ```

- [ ] 编辑配置文件，修改以下内容：
  - [ ] `ServerName` 和 `ServerAlias` 为您的域名
  - [ ] SSL 证书路径（如果使用 HTTPS）

- [ ] 在 `httpd.conf` 中添加：
  ```apache
  Include conf/extra/chart_class_vhost.conf
  ```

- [ ] 确保以下模块已启用（在 `httpd.conf` 中取消注释）：
  - [ ] `LoadModule proxy_module modules/mod_proxy.so`
  - [ ] `LoadModule proxy_http_module modules/mod_proxy_http.so`
  - [ ] `LoadModule rewrite_module modules/mod_rewrite.so`
  - [ ] `LoadModule headers_module modules/mod_headers.so`
  - [ ] `LoadModule ssl_module modules/mod_ssl.so`（如果使用 HTTPS）

- [ ] 测试 Apache 配置：
  ```powershell
  C:\Apache24\bin\httpd.exe -t
  ```
  - 应该显示 "Syntax OK"

- [ ] 重启 Apache：
  ```powershell
  C:\Apache24\bin\httpd.exe -k restart
  ```

### 步骤 6: 防火墙配置

- [ ] 确保 Windows 防火墙允许 Apache 端口：
  - HTTP: 端口 80
  - HTTPS: 端口 443
- [ ] 后端端口（8001）只需本地访问，无需开放

### 步骤 7: 通过 Apache 测试

- [ ] 测试健康检查端点：
  ```powershell
  curl http://your-domain.com/api/chart-types
  ```
  - 应该返回图表类型列表

- [ ] 如果使用 HTTPS：
  ```powershell
  curl https://your-domain.com/api/chart-types
  ```

## 故障排查

### 服务无法启动

1. **检查日志**
   ```powershell
   type logs\service_stderr.log
   ```

2. **检查服务状态**
   ```powershell
   nssm status ChartClassAPI
   ```

3. **手动测试**
   ```powershell
   .venv\Scripts\python.exe web_api\main.py
   ```

### Apache 代理失败

1. **检查 Apache 错误日志**
   ```powershell
   type C:\Apache24\logs\error.log
   ```

2. **检查后端服务是否运行**
   ```powershell
   curl http://127.0.0.1:8001/
   ```

3. **检查 Apache 模块是否加载**
   ```powershell
   C:\Apache24\bin\httpd.exe -M | findstr proxy
   ```

### 性能问题

1. **检查 workers 数量**
   - 查看服务日志确认 workers 数量
   - 根据 CPU 核心数调整 `UVICORN_WORKERS`

2. **监控资源使用**
   - 任务管理器查看 CPU 和内存使用
   - 检查是否有内存泄漏

## 维护操作

### 重启服务
```powershell
nssm restart ChartClassAPI
```

### 停止服务
```powershell
nssm stop ChartClassAPI
```

### 启动服务
```powershell
nssm start ChartClassAPI
```

### 查看服务状态
```powershell
nssm status ChartClassAPI
```

### 更新服务配置
1. 停止服务
2. 修改 `deploy/start_service.bat` 中的环境变量
3. 重新运行 `deploy/start_service.bat`

### 卸载服务
```powershell
deploy\stop_service.bat
```

## 性能优化建议

1. **Workers 数量**
   - 建议设置为 CPU 核心数
   - 例如：4 核 CPU 设置为 4 workers

2. **线程池大小**
   - 建议设置为 workers 数量
   - 例如：4 workers 设置为 4 线程

3. **数据库优化**
   - 如果写入并发高，考虑迁移到 PostgreSQL
   - 当前 SQLite 适合低到中等并发场景

4. **Apache 配置**
   - 根据实际负载调整 `ProxyTimeout`
   - 考虑启用 Apache 的压缩模块

## 安全建议

1. **HTTPS 配置**
   - 生产环境必须使用 HTTPS
   - 使用有效的 SSL 证书

2. **防火墙规则**
   - 只开放必要的端口
   - 后端端口（8001）不对外开放

3. **JWT 密钥**
   - 生产环境必须设置强 JWT 密钥（至少 32 字符）
   - 通过环境变量设置：`JWT_SECRET_KEY`

4. **日志安全**
   - 定期清理日志文件
   - 避免在日志中记录敏感信息

## 联系支持

如果遇到问题，请检查：
1. 服务日志：`logs\service_stdout.log` 和 `logs\service_stderr.log`
2. Apache 日志：`C:\Apache24\logs\error.log`
3. 系统事件查看器：Windows 日志 > 应用程序

