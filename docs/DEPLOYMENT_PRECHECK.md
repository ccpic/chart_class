## 部署前代码审查报告

### 1. Backend 配置 (`backend-config`)
- **JWT 秘钥硬编码**：`web_api/auth.py` 直接给出 `SECRET_KEY = os.getenv(..., "your-secret-key-change-in-production")`。若未显式设置环境变量，生产环境会共享同一个弱秘钥，意味着任意人都能伪造合法 Token。
- **数据库初始化与存储**：`web_api/main.py` 在模块导入时调用 `init_db()`，默认 SQLite 文件位于 `/app/data/chart_class.db`，依赖容器卷挂载。多进程/多容器部署会共享同一 SQLite 文件，缺少锁与迁移机制，风险包括文件锁争用和数据损坏。
- **缺少运行级别配置**：日志、CORS、监听端口都写死在代码里，尚未通过环境变量暴露；`uvicorn` 以单进程启动，无法通过 Dockerfile 或 compose 覆盖。

> 改进要点：强制从环境变量读取 `JWT_SECRET_KEY`，并在启动时拒绝默认值；将数据库 URL、日志级别、CORS 列表改为环境配置；若将来需要多副本，迁移至 PostgreSQL 等外部数据库，并用 Alembic 维护 schema。

### 2. 状态持久化 (`state-persistence`)
- **图表保存未持久化**：`web_api/routers/charts.py` 使用 `_charts_storage` 内存字典保存用户图表，容器重启或多实例时完全丢失，同时缺乏锁，写并发会互相覆盖。
- **颜色管理为 JSON 文件写放大器**：`chart/color/color_manager.py`/`web_api/routers/colors.py` 为每个用户写 `data/colors/<user>/color_dict.json`。`ColorManager` 在每次写操作都直接 `json.dump`，无文件锁、无版本校验。多个请求在 Docker 中并行运行会导致文件损坏；同时这些 JSON 依旧挂在容器本地卷上，备份策略缺失。
- **全局 ColorManager**：`web_api/main.py` 和 `web_bridge/adapters/chart_adapter.py` 在模块级创建 `ColorManager()`，这会把默认颜色保存在单个 JSON 里，对用户隔离和热更新都有副作用。

> 改进要点：在部署前明确“图表保存功能仅为内存缓存”，或改成真正的数据库表；颜色数据写入前需要文件锁或直接存入同一数据库；移除全局单例，按请求加载用户上下文。

### 3. Docker 运行环境 (`docker-runtime`)
- **数据卷路径硬写**：`docker-compose.yml` 使用 `../data:/app/data`，在 Windows Server 上运行 compose（若当前目录不是 docker/）极易报路径无效。更安全做法是让 `.env` 提供绝对路径或使用命名 volume。
- **健康检查依赖内部 localhost**：`backend` 健康检查用 `urllib.request.urlopen('http://localhost:8001/')`。如果日后需要把应用挂在反向代理后或修改端口，该脚本需要同步更新，否则 compose 会判定容器不健康。

> 改进要点：把数据卷等都改成可配置项，并在 README 中给出 Windows Server 的示例命令；考虑构建阶段就复制 `app/`，运行阶段只挂载数据目录，避免把整个 repo 挂进生产容器。

### 4. 前端环境变量 (`frontend-env`)
- **API Base URL 硬编码为 localhost**：`frontend/lib/api.ts`、`frontend/lib/api/client.ts`、`frontend/store/authStore.ts` 都在构建时注入 `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"`。在 Docker compose 中，这个环境变量被设置为 `http://localhost:8001`，最终下发到浏览器，导致终端用户的浏览器向其本机 `localhost:8001` 发送请求，生产环境必然失效。
- **缺少服务器侧代理**：没有 Nginx/Caddy 之类的入口把前端与后端统一在同一域名路径下（例如 `/api`）。若直接暴露两个容器，需要在 `.env` 中手动填写公网地址，且必须处理 HTTPS / CORS。
- **Token 存储策略**：Zustand store 把 JWT 直接写入 localStorage，未配置 `sameSite`/`secure`。如需后台管理功能，应评估 XSS 面带来的令牌泄露风险。

> 改进要点：将 `NEXT_PUBLIC_API_URL` 设置为实际域名（例如 `https://chart.example.com/api`），或在 Next.js 应用内部通过 `/api` 路由做代理；把 URL 写入 `.env.production` 并在 docker-compose.prod.yml 中引入；验证 CORS 与 HTTPS 配置。

### 5. 综合部署风险 (`deployment-risks`)
| 等级 | 风险 | 影响 | 建议 |
| --- | --- | --- | --- |
| 高 | 前端 API 指向 `localhost` | 所有浏览器请求失败 | 在构建/运行阶段注入正确的公网 API URL，或改为相对路径并加反向代理 |
| 高 | 图表存储只在内存 | 容器重启即丢数据，无法水平扩展 | 上线前明确定义持久化方案（数据库/文件），至少提供“实验性质”警告 |
| 高 | JWT 秘钥默认值 | Token 可伪造，导致账户被接管 | 通过环境变量强制设置随机秘钥，并在启动脚本中校验 |
| 中 | 颜色 JSON 并发写 | 可能写花用户颜色库，且难于备份 | 切换到数据库或加文件锁/版本号 |
| 中 | pip 源硬编码清华 | 非大陆网络下构建失败 | 允许通过 `ARG PIP_INDEX_URL` 覆盖，默认使用官方源 |
| 中 | 数据卷路径依赖本地目录结构 | Windows Server 下一旦切换目录便启动失败 | 使用绝对路径或 Docker 命名卷，文档中示例清晰指出 |
| 低 | 健康检查 URL 写死 | 修改端口或路径后 compose 健康检查失效 | 让 healthcheck 读取容器内环境变量或使用 `CMD curl -f http://127.0.0.1:${PORT:-8001}/health` |

> 在完成上述整改前，不建议直接把当前镜像部署到 Windows Server 2022。尤其是 API Base URL、秘钥、数据持久化这三点，若不修复将导致“可用性=0”或“安全=0”。


