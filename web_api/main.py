"""
Chart Class Web API
统一的 Web API 服务，包括：
- 图表渲染 API（单图/多子图画布）
- 颜色管理 API（CRUD 操作）
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import logging
import os

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

# 导入颜色管理
from chart.color.color_manager import ColorManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Chart Class Web API",
    description="图表渲染 + 颜色管理统一 API",
    version="0.3.0",
)

# CORS 配置（支持环境变量）
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局颜色管理器
color_manager = ColorManager()


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
        },
        "docs": "/docs",
    }


# ============ 新端点：多子图渲染 ============


@app.post("/api/render/canvas")
async def render_canvas(request: RenderRequestModel):
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

        # 调用桥接层渲染
        adapter = get_adapter()
        canvas_dict = request.canvas.dict()
        subplots_list = [s.dict() for s in request.subplots]

        image_bytes = adapter.render_canvas(canvas_dict, subplots_list)

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
async def render_subplot(subplot: SubplotConfigModel):
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

        image_bytes = adapter.render_canvas(canvas_config, [subplot_config])

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


# ============ 颜色管理 API ============


class ColorCreateRequest(BaseModel):
    """创建颜色请求"""

    name: str
    color: str
    named_color: Optional[str] = None  # 可选的 matplotlib 命名颜色
    overwrite: bool = False


class ColorUpdateRequest(BaseModel):
    """更新颜色请求"""

    color: Optional[str] = None
    named_color: Optional[str] = None  # 可选的 matplotlib 命名颜色


class ColorResponse(BaseModel):
    """颜色响应"""

    name: str
    color: str  # 永远是 HEX 值
    named_color: Optional[str] = None  # 可选的 matplotlib 命名颜色


class MessageResponse(BaseModel):
    """通用消息响应"""

    message: str
    success: bool


@app.get("/api/colors", response_model=List[ColorResponse])
def list_colors(
    search: Optional[str] = Query(None, description="搜索关键词"),
):
    """
    获取所有颜色映射

    - **search**: 搜索关键词（可选）
    """
    mappings = color_manager.list_all(search=search)
    return [
        ColorResponse(name=m.name, color=m.color, named_color=m.named_color)
        for m in mappings
    ]


@app.get("/api/colors/meta/stats")
def get_color_stats():
    """获取统计信息"""
    all_colors = color_manager.to_dict()

    return {
        "total_colors": len(all_colors),
    }


@app.get("/api/colors/{name}", response_model=ColorResponse)
def get_color(name: str):
    """
    获取指定颜色映射

    - **name**: 颜色名称
    """
    mapping = color_manager.get(name)
    if not mapping:
        raise HTTPException(status_code=404, detail=f"颜色 '{name}' 不存在")

    return ColorResponse(
        name=mapping.name, color=mapping.color, named_color=mapping.named_color
    )


@app.post("/api/colors", response_model=MessageResponse)
def create_color(request: ColorCreateRequest):
    """
    添加新颜色映射

    - **name**: 颜色名称（必填）
    - **color**: 颜色值（必填）
    - **named_color**: 可选的 matplotlib 命名颜色（可选）
    - **overwrite**: 是否覆盖已存在的（默认 false）
    """
    success = color_manager.add(
        name=request.name,
        color=request.color,
        named_color=request.named_color,
        overwrite=request.overwrite,
    )

    if not success:
        raise HTTPException(
            status_code=409,
            detail=f"颜色 '{request.name}' 已存在，请设置 overwrite=true 覆盖",
        )

    return MessageResponse(message=f"成功添加颜色 '{request.name}'", success=True)


@app.put("/api/colors/{name}", response_model=MessageResponse)
def update_color(name: str, request: ColorUpdateRequest):
    """
    更新颜色映射

    - **name**: 颜色名称（路径参数）
    - **color**: 新颜色值（可选）
    - **named_color**: 新的命名颜色（可选，null 表示清除）
    """
    # 获取当前映射
    current = color_manager.get(name)
    if not current:
        raise HTTPException(status_code=404, detail=f"颜色 '{name}' 不存在")

    # 准备更新参数
    update_params = {}
    if request.color is not None:
        update_params["color"] = request.color

    # 处理 named_color：如果请求中包含该字段（即使是 null），都应该更新
    # Pydantic 会将 JSON 的 null 转为 Python 的 None
    if "named_color" in request.model_dump(exclude_unset=True):
        # 如果是 null，清空命名颜色；否则设置新值
        update_params["named_color"] = request.named_color or ""

    success = color_manager.update(name=name, **update_params)

    if not success:
        raise HTTPException(status_code=500, detail=f"更新颜色 '{name}' 失败")

    return MessageResponse(message=f"成功更新颜色 '{name}'", success=True)


@app.delete("/api/colors/{name}", response_model=MessageResponse)
def delete_color(name: str):
    """
    删除颜色映射

    - **name**: 颜色名称
    """
    success = color_manager.delete(name)

    if not success:
        raise HTTPException(status_code=404, detail=f"颜色 '{name}' 不存在")

    return MessageResponse(message=f"成功删除颜色 '{name}'", success=True)


@app.post("/api/colors/export/typescript", response_model=MessageResponse)
def export_typescript(output_path: str = "frontend/lib/colors/schemes.ts"):
    """
    导出为 TypeScript 文件

    - **output_path**: 输出文件路径（默认 frontend/lib/colors/schemes.ts）
    """
    try:
        color_manager.export_to_typescript(output_path)
        return MessageResponse(message=f"成功导出到 {output_path}", success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 启动服务 ============
if __name__ == "__main__":
    import uvicorn

    print("🚀 启动 Chart Class Web API 服务...")
    print("📊 图表渲染 API: http://localhost:8001/api/render/*")
    print("🎨 颜色管理 API: http://localhost:8001/api/colors/*")
    print("📚 API 文档: http://localhost:8001/docs")
    print("")

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
