"""
Web API 应用
支持单图和多子图画布渲染
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Any, Dict, List
import logging

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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(title="Chart Class Web API", version="0.2.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"status": "ok", "message": "Chart Class Web API", "version": "0.2.0"}


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


# 启动命令
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
