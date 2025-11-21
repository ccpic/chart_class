# Docker 问题排查指南

## ERR_CONNECTION_REFUSED 问题排查

### 1. 检查容器状态

```bash
cd docker
docker-compose ps
```

应该看到两个容器都在运行：
- `chart-class-backend` - 状态应该是 `Up`
- `chart-class-frontend` - 状态应该是 `Up`

### 2. 查看后端容器日志

```bash
docker-compose logs backend
```

或者实时查看：
```bash
docker-compose logs -f backend
```

常见问题：
- 端口被占用
- 依赖安装失败
- 代码错误导致启动失败

### 3. 检查后端是否正常响应

```bash
# 在容器外部测试
curl http://localhost:8001/

# 或者在容器内部测试
docker-compose exec backend curl http://localhost:8001/
```

### 4. 检查端口映射

```bash
# 查看端口映射
docker-compose ps
# 或者
docker port chart-class-backend
```

应该显示：`8001/tcp -> 0.0.0.0:8001`

### 5. 检查网络连接

```bash
# 查看容器网络
docker network ls
docker network inspect chart_class2_default
```

### 6. 重启服务

```bash
cd docker
docker-compose down
docker-compose up -d --build
```

### 7. 检查环境变量

确保前端的环境变量正确设置：

```bash
docker-compose exec frontend env | grep NEXT_PUBLIC_API_URL
```

应该显示：`NEXT_PUBLIC_API_URL=http://localhost:8001`

### 8. 常见解决方案

#### 问题：后端容器启动失败

```bash
# 查看详细错误
docker-compose logs backend

# 重新构建
docker-compose build --no-cache backend
docker-compose up -d backend
```

#### 问题：端口冲突

```bash
# 检查端口占用（Windows）
netstat -ano | findstr :8001

# 检查端口占用（Linux/Mac）
lsof -i :8001

# 如果被占用，修改 docker-compose.yml 中的端口
```

#### 问题：前端无法连接后端

确保：
1. 后端容器正常运行
2. 端口映射正确（8001:8001）
3. 前端环境变量 `NEXT_PUBLIC_API_URL` 设置为 `http://localhost:8001`
4. CORS 配置允许前端来源

### 9. 进入容器调试

```bash
# 进入后端容器
docker-compose exec backend bash

# 检查进程
ps aux | grep uvicorn

# 检查端口监听
netstat -tlnp | grep 8001
# 或者
ss -tlnp | grep 8001

# 手动启动服务测试
uvicorn web_api.main:app --host 0.0.0.0 --port 8001
```

### 10. 完全重置

如果以上都不行，完全重置：

```bash
cd docker
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```




