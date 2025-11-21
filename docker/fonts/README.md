# 微软雅黑字体安装说明

## 方法 1：复制字体文件到容器（推荐）

1. **从 Windows 系统复制字体文件**
   - 打开 `C:\Windows\Fonts\`
   - 找到 `msyh.ttc`（微软雅黑）文件
   - 复制到 `docker/fonts/` 目录

2. **取消 Dockerfile 中的注释**
   编辑 `docker/Dockerfile.backend`，取消这一行的注释：
   ```dockerfile
   COPY docker/fonts/msyh.ttc /usr/share/fonts/truetype/msyh/msyh.ttc
   ```

3. **重新构建镜像**
   ```bash
   cd docker
   docker-compose build backend
   ```

## 方法 2：通过 Volume 挂载（开发环境）

在 `docker-compose.yml` 中添加字体挂载：

```yaml
services:
  backend:
    volumes:
      - ../data:/app/data
      - ./fonts:/usr/share/fonts/truetype/msyh:ro  # 添加字体挂载
```

然后将 `msyh.ttc` 放在 `docker/fonts/` 目录下。

## 方法 3：在容器运行时安装

如果容器已经在运行，可以：

```bash
# 进入容器
docker-compose exec backend bash

# 创建字体目录
mkdir -p /usr/share/fonts/truetype/msyh

# 从宿主机复制字体文件（需要先挂载）
# 或者使用 docker cp 命令从宿主机复制
```

## 验证字体安装

构建完成后，验证字体是否可用：

```bash
# 进入容器
docker-compose exec backend bash

# 检查字体
fc-list | grep -i "microsoft\|msyh\|微软"

# 或者检查字体文件
ls -la /usr/share/fonts/truetype/msyh/
```

## 注意事项

- 微软雅黑是商业字体，请确保您有使用权限
- 如果无法使用微软雅黑，代码会自动回退到系统默认字体
- 字体文件大小约 15-20MB

