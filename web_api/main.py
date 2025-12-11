"""
Chart Class Web API
统一的 Web API 服务，包括：
- 图表渲染 API（单图/多子图画布）
- 颜色管理 API（CRUD 操作）
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Tuple
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio

# 导入桥接层
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from web_bridge.adapters.chart_adapter import get_adapter
from web_api.models import (
    RenderRequestModel,
    ChartType,
    CanvasConfigModel,
    SubplotConfigModel,
)

# 导入用户权限模块
from web_api.database import init_db, User, get_db
from web_api.routers import users, charts, colors, palettes
from web_api.middleware import get_current_active_user
from web_api.routers.colors import get_user_color_manager
from web_api.palette_db_manager import PaletteDBManager
from sqlalchemy.orm import Session

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 启动前检查：验证关键配置
def _startup_checks():
    """启动前检查关键配置"""
    import os
    
    # 获取环境
    env = os.getenv("ENVIRONMENT") or os.getenv("NODE_ENV") or os.getenv("FLASK_ENV")
    if env:
        env = env.lower()
    elif os.path.exists("/.dockerenv"):
        env = "production"
    else:
        env = "development"
    
    logger.info(f"环境: {env}")
    
    # 检查 JWT 秘钥（导入时会自动验证，这里只是记录状态）
    from web_api.auth import SECRET_KEY
    if env in ("production", "prod"):
        if not SECRET_KEY or len(SECRET_KEY) < 32:
            logger.error("❌ 生产环境 JWT_SECRET_KEY 未设置或强度不足！")
            raise ValueError("生产环境必须设置强 JWT 秘钥（至少 32 字符）")
        logger.info("✅ JWT 秘钥已配置（长度: %d）", len(SECRET_KEY))
    else:
        if SECRET_KEY and len(SECRET_KEY) >= 32:
            logger.info("✅ JWT 秘钥已配置（长度: %d）", len(SECRET_KEY))
        else:
            logger.warning("⚠️  开发环境使用默认 JWT 秘钥，生产环境请设置 JWT_SECRET_KEY")
    
    # 检查数据库
    try:
        init_db()
        logger.info("✅ 数据库初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise

# 执行启动检查
_startup_checks()

# 创建线程池用于处理 CPU 密集型任务（图表渲染）
THREAD_POOL_SIZE = int(os.getenv("THREAD_POOL_SIZE", "4"))
_executor = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)
logger.info(f"线程池已创建，大小: {THREAD_POOL_SIZE}")

# 创建应用
app = FastAPI(
    title="Chart Class Web API",
    description="图表渲染 + 颜色管理 + 用户权限统一 API",
    version="0.4.0",
)

# CORS 配置（支持环境变量）
cors_origins_env = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173"
)
cors_origins = [
    origin.strip() for origin in cors_origins_env.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注意：颜色管理已迁移到数据库，使用 get_user_color_manager(db, user_id) 获取用户颜色管理器

# 集成路由
app.include_router(users.router, prefix="/api/auth", tags=["认证"])
app.include_router(charts.router, prefix="/api", tags=["图表管理"])
app.include_router(colors.router, prefix="/api", tags=["颜色管理"])
app.include_router(palettes.router, prefix="/api", tags=["调色板管理"])


# 数据模型
class ChartDataModel(BaseModel):
    """图表数据模型"""

    columns: List[str]
    index: List[str]
    data: List[List[Any]]


class ChartParamsModel(BaseModel):
    """图表参数模型"""

    stacked: bool = True
    show_label: bool = True
    label_formatter: str = "{abs}"


class RenderRequest(BaseModel):
    """渲染请求"""

    data: ChartDataModel
    params: ChartParamsModel


# ============ API 端点 ============


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "message": "Chart Class Web API",
        "version": "0.3.0",
        "services": {
            "chart_rendering": "/api/render/*",
            "color_management": "/api/colors/*",
            "palette_management": "/api/palettes/*",
            "user_auth": "/api/auth/*",
            "chart_management": "/api/charts/*",
        },
        "docs": "/docs",
    }


# ============ 新端点：多子图渲染 ============


def _build_user_color_config(
    user_id: int,
    db: Session,
    palette_name: Optional[str] = None,
) -> Tuple[Optional[Dict[str, str]], Optional[List[str]]]:
    """
    根据用户ID构建颜色字典和调色板
    优先使用命名颜色，其次使用 HEX
    
    注意：
    - 颜色映射：用于图表中通过名称引用颜色
    - 调色板：完全独立，直接存储颜色值（HEX 或命名颜色），不依赖颜色映射
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        palette_name: 调色板名称，如果为 None 或 "默认"，则使用默认调色板
    """
    try:
        # 获取颜色映射（用于图表中通过名称引用颜色）
        color_manager = get_user_color_manager(db, user_id)
        user_colors = color_manager.list_all()
        
        color_dict = None
        if user_colors:
            color_dict = {
                mapping.name: (mapping.named_color if mapping.named_color else mapping.color)
                for mapping in user_colors
            }
        
        # 获取调色板（直接使用颜色值，不依赖颜色映射）
        palette_manager = PaletteDBManager(db, user_id)
        if palette_name and palette_name != "默认":
            # 获取指定调色板
            palette_data = palette_manager.get_palette(palette_name)
            if palette_data:
                palette_colors = palette_data.get("colors", [])
            else:
                # 如果指定的调色板不存在，回退到默认调色板
                logger.warning(f"调色板 '{palette_name}' 不存在，使用默认调色板")
                palette_colors = palette_manager.get_default_palette()
        else:
            # 使用默认调色板
            palette_colors = palette_manager.get_default_palette()
        
        return color_dict, (palette_colors if palette_colors else None)
    except Exception as exc:
        logger.warning(f"加载用户颜色失败 user_id={user_id}: {exc}")
        return None, None


@app.post("/api/render/canvas")
async def render_canvas(
    request: RenderRequestModel,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    渲染多子图画布

    Request Body:
    {
      "canvas": {
        "width": 15,
        "height": 12,
        "rows": 2,
        "cols": 2,
        "title": "画布总标题",
        "ytitle": "Y轴总标题",
        "show_legend": true,
        "label_outer": true,
        ...
      },
      "subplots": [
        {
          "subplot_id": "subplot-1",
          "ax_index": 0,
          "chart_type": "bar",
          "data": {...},
          "params": {...}
        },
        ...
      ]
    }
    """
    try:
        logger.info(
            f"收到画布渲染请求: {request.canvas.rows}x{request.canvas.cols} 网格, {len(request.subplots)} 个子图"
        )

        # 验证子图数量
        total_grids = request.canvas.rows * request.canvas.cols
        if len(request.subplots) > total_grids:
            raise HTTPException(
                status_code=400,
                detail=f"子图数量 ({len(request.subplots)}) 超过网格容量 ({total_grids})",
            )

        # 验证 ax_index 范围
        for subplot in request.subplots:
            if subplot.ax_index >= total_grids:
                raise HTTPException(
                    status_code=400,
                    detail=f"子图索引 {subplot.ax_index} 超出范围 (0-{total_grids-1})",
                )

        # 调用桥接层渲染（使用线程池避免阻塞事件循环）
        adapter = get_adapter()
        canvas_dict = request.canvas.dict()
        subplots_list = [s.dict() for s in request.subplots]

        # 从请求中获取调色板名称
        palette_name = request.palette_name
        color_dict, palette_colors = _build_user_color_config(current_user.id, db, palette_name=palette_name)

        # 将 CPU 密集型的渲染任务放到线程池中执行
        loop = asyncio.get_event_loop()
        image_bytes = await loop.run_in_executor(
            _executor,
            adapter.render_canvas,
            canvas_dict,
            subplots_list,
            color_dict,
            palette_colors,
        )

        logger.info(f"画布渲染成功，图片大小: {len(image_bytes)} bytes")

        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={"Cache-Control": "no-cache"},
        )

    except ValueError as e:
        logger.error(f"画布渲染失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"画布渲染失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"渲染失败: {str(e)}")


@app.post("/api/render/subplot")
async def render_subplot(
    subplot: SubplotConfigModel,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    渲染单个子图（独立预览）

    Request Body:
    {
      "subplot_id": "subplot-1",
      "ax_index": 0,
      "chart_type": "bar",
      "data": {
        "columns": ["品牌A", "品牌B"],
        "data": [[100, 200], [300, 400]]
      },
      "params": {
        "stacked": true,
        "show_label": true
      }
    }

    返回单个子图的 PNG 图片，使用 1x1 画布
    """
    try:
        logger.info(
            f"收到子图渲染请求: ID={subplot.subplot_id}, Type={subplot.chart_type}"
        )

        # 创建一个 1x1 画布来渲染单个子图
        adapter = get_adapter()

        # 构造单子图画布配置
        canvas_config = {
            "width": 12,
            "height": 8,
            "rows": 1,
            "cols": 1,
            "wspace": 0.1,
            "hspace": 0.1,
            "show_legend": False,
            "label_outer": False,
        }

        # 将子图索引设为 0（单图）
        subplot_config = subplot.dict()
        subplot_config["ax_index"] = 0

        # 从请求中获取调色板名称
        palette_name = subplot.palette_name
        color_dict, palette_colors = _build_user_color_config(current_user.id, db, palette_name=palette_name)

        # 将 CPU 密集型的渲染任务放到线程池中执行
        loop = asyncio.get_event_loop()
        image_bytes = await loop.run_in_executor(
            _executor,
            adapter.render_canvas,
            canvas_config,
            [subplot_config],
            color_dict,
            palette_colors,
        )

        logger.info(f"子图渲染成功，图片大小: {len(image_bytes)} bytes")

        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={"Cache-Control": "no-cache"},
        )

    except ValueError as e:
        logger.error(f"子图渲染失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"子图渲染失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"渲染失败: {str(e)}")


# ============ 工具端点 ============


@app.get("/api/chart-types")
async def get_chart_types():
    """获取支持的图表类型列表"""
    adapter = get_adapter()
    return {"chart_types": adapter.get_supported_chart_types()}


@app.get("/api/chart-types/{chart_type}/defaults")
async def get_default_params(chart_type: str):
    """获取指定图表类型的默认参数"""
    adapter = get_adapter()
    defaults = adapter.get_default_params(chart_type)
    if not defaults:
        raise HTTPException(status_code=404, detail=f"未知的图表类型: {chart_type}")
    return defaults


# ============ 保留原有的单图端点（向后兼容）============


@app.post("/api/render")
async def render_chart(request: RenderRequest):
    """
    单图渲染（MVP 兼容端点）

    保留此端点以确保 MVP 前端仍能工作

    示例请求：
    ```json
    {
        "data": {
            "columns": ["品牌A", "品牌B"],
            "index": ["2024-01", "2024-02"],
            "data": [[1000, 800], [1200, 900]]
        },
        "params": {
            "stacked": true,
            "show_label": true,
            "label_formatter": "{abs}"
        }
    }
    ```
    """
    try:
        logger.info("收到渲染请求")

        # 调用适配器
        adapter = get_adapter()
        image_bytes = adapter.render_bar_chart(
            data_json=request.data.dict(), params=request.params.dict()
        )

        logger.info(f"渲染成功，图片大小: {len(image_bytes)} bytes")

        # 返回图片
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={"Cache-Control": "no-cache"},
        )

    except Exception as e:
        logger.error(f"渲染失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============ 颜色管理 API（向后兼容，已迁移到 routers/colors.py） ============
# 注意：这些端点已废弃，新代码应使用 /api/colors/*（需要认证）
# 保留这些端点以确保向后兼容，但建议迁移到新的用户隔离 API


# ============ 启动服务 ============
if __name__ == "__main__":
    import uvicorn
    import multiprocessing

    # 从环境变量获取配置
    workers = int(os.getenv("UVICORN_WORKERS", "1"))
    port = int(os.getenv("UVICORN_PORT", "8001"))
    host = os.getenv("UVICORN_HOST", "0.0.0.0")  # 开发模式默认监听所有接口
    reload = os.getenv("UVICORN_RELOAD", "true").lower() == "true"
    
    # 服务模式（通过 NSSM）只监听本地地址
    if os.getenv("UVICORN_HOST"):
        host = os.getenv("UVICORN_HOST")
    elif not reload:
        # 生产环境默认监听本地
        host = "127.0.0.1"

    print("🚀 启动 Chart Class Web API 服务...")
    print(f"📊 图表渲染 API: http://{host}:{port}/api/render/*")
    print(f"🎨 颜色管理 API: http://{host}:{port}/api/colors/*")
    print(f"📚 API 文档: http://{host}:{port}/docs")
    print(f"⚙️  Workers: {workers if not reload else 1} (reload={reload})")
    print(f"🧵 线程池大小: {THREAD_POOL_SIZE}")
    print("")

    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers if not reload else 1,  # reload 模式不支持多 workers
        reload=reload,
        log_level="info"
    )
