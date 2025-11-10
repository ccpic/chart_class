"""
MVP 版本的 FastAPI 应用
单文件，仅一个渲染端点
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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(title="Chart Class Web API - MVP", version="0.1.0")

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
    return {"status": "ok", "message": "Chart Class Web API - MVP", "version": "0.1.0"}


@app.post("/api/render")
async def render_chart(request: RenderRequest):
    """
    渲染柱状图

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
