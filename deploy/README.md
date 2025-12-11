# Chart Class Web API 部署指南

本目录包含 Windows 服务部署（NSSM + Apache 2.4）所需的所有文件。

## 文件说明

- `start_service.bat` - NSSM 服务安装脚本
- `stop_service.bat` - NSSM 服务卸载脚本
- `apache_vhost.conf` - Apache 2.4 反向代理配置文件
- `DEPLOYMENT_CHECKLIST.md` - 详细的部署检查清单

## 快速开始

### 1. 安装 NSSM 服务

以管理员身份运行：
```batch
deploy\start_service.bat
```

### 2. 配置 Apache

1. 复制 `apache_vhost.conf` 到 Apache 配置目录
2. 修改配置文件中的域名和 SSL 证书路径
3. 在 `httpd.conf` 中引入配置文件
4. 重启 Apache

详细步骤请参考 `DEPLOYMENT_CHECKLIST.md`。

## 环境变量配置

服务通过 NSSM 脚本设置环境变量，主要配置项：

- `UVICORN_WORKERS=4` - Worker 进程数量
- `THREAD_POOL_SIZE=4` - 线程池大小
- `UVICORN_PORT=8001` - 服务端口
- `UVICORN_HOST=127.0.0.1` - 监听地址（仅本地）

如需修改，请编辑 `start_service.bat` 中的环境变量设置。

## 服务管理

### 查看服务状态
```batch
nssm status ChartClassAPI
```

### 重启服务
```batch
nssm restart ChartClassAPI
```

### 停止服务
```batch
nssm stop ChartClassAPI
```

### 卸载服务
```batch
deploy\stop_service.bat
```

## 日志位置

- 服务标准输出：`logs\service_stdout.log`
- 服务错误输出：`logs\service_stderr.log`
- Apache 访问日志：`C:\Apache24\logs\chart_class_access.log`
- Apache 错误日志：`C:\Apache24\logs\chart_class_error.log`

## 性能优化

### Workers 数量
建议设置为 CPU 核心数。例如：
- 4 核 CPU → 4 workers
- 8 核 CPU → 8 workers

### 线程池大小
建议设置为 workers 数量，确保每个 worker 有一个线程处理 CPU 密集型任务。

### 修改配置
1. 停止服务：`nssm stop ChartClassAPI`
2. 编辑 `start_service.bat` 中的环境变量
3. 重新运行：`deploy\start_service.bat`

## 故障排查

如果遇到问题，请：

1. 检查服务日志：`type logs\service_stderr.log`
2. 检查服务状态：`nssm status ChartClassAPI`
3. 测试本地服务：`curl http://127.0.0.1:8001/`
4. 检查 Apache 日志：`type C:\Apache24\logs\error.log`

更多故障排查信息请参考 `DEPLOYMENT_CHECKLIST.md`。

