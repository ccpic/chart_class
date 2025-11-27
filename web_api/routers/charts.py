"""
图表管理 API
支持用户隔离的图表保存和加载
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from web_api.database import get_db, User
from web_api.middleware import get_current_active_user

router = APIRouter()


# ============ 数据模型 ============


class ChartData(BaseModel):
    """图表数据"""

    columns: List[str]
    index: Optional[List[str]] = None
    data: List[List[Any]]


class SavedChartRequest(BaseModel):
    """保存图表请求"""

    name: str
    tags: Optional[List[str]] = None
    canvas: Dict[str, Any]
    subplots: List[Dict[str, Any]]
    version: str = "1.0"


class SavedChartResponse(BaseModel):
    """保存的图表响应"""

    id: str
    name: str
    tags: Optional[List[str]]
    canvas: Dict[str, Any]
    subplots: List[Dict[str, Any]]
    version: str
    created_at: datetime
    updated_at: datetime


class ChartListResponse(BaseModel):
    """图表列表项"""

    id: str
    name: str
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


# ============ 简单的内存存储（后续可改为数据库） ============
# 注意：这是临时实现，生产环境应该使用数据库

_charts_storage: Dict[int, Dict[str, Dict[str, Any]]] = (
    {}
)  # {user_id: {chart_id: chart_data}}


def _get_user_charts(user_id: int) -> Dict[str, Dict[str, Any]]:
    """获取用户的图表存储"""
    if user_id not in _charts_storage:
        _charts_storage[user_id] = {}
    return _charts_storage[user_id]


@router.post("/charts", response_model=SavedChartResponse)
async def save_chart(
    chart_data: SavedChartRequest,
    current_user: User = Depends(get_current_active_user),
):
    """保存图表"""
    import uuid

    user_charts = _get_user_charts(current_user.id)

    # 创建新图表
    chart_id = str(uuid.uuid4())
    now = datetime.utcnow()

    saved_chart = {
        "id": chart_id,
        "name": chart_data.name,
        "tags": chart_data.tags or [],
        "canvas": chart_data.canvas,
        "subplots": chart_data.subplots,
        "version": chart_data.version,
        "created_at": now,
        "updated_at": now,
    }

    user_charts[chart_id] = saved_chart

    return SavedChartResponse(**saved_chart)


@router.put("/charts/{chart_id}", response_model=SavedChartResponse)
async def update_chart(
    chart_id: str,
    chart_data: SavedChartRequest,
    current_user: User = Depends(get_current_active_user),
):
    """更新图表"""
    user_charts = _get_user_charts(current_user.id)

    if chart_id not in user_charts:
        # 添加调试信息
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"图表不存在: chart_id={chart_id}, user_id={current_user.id}, "
            f"用户图表数量={len(user_charts)}, 图表IDs={list(user_charts.keys())[:5]}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"图表不存在: chart_id={chart_id}",
        )

    # 更新图表
    existing_chart = user_charts[chart_id]
    existing_chart.update(
        {
            "name": chart_data.name,
            "tags": chart_data.tags or [],
            "canvas": chart_data.canvas,
            "subplots": chart_data.subplots,
            "version": chart_data.version,
            "updated_at": datetime.utcnow(),
        }
    )

    return SavedChartResponse(**existing_chart)


@router.get("/charts", response_model=List[ChartListResponse])
async def list_charts(
    tags: Optional[List[str]] = Query(
        None, description="按tag筛选（AND逻辑：必须包含所有指定tag）"
    ),
    current_user: User = Depends(get_current_active_user),
):
    """获取图表列表"""
    user_charts = _get_user_charts(current_user.id)

    charts = []
    for chart_id, chart_data in user_charts.items():
        chart_tags = chart_data.get("tags") or []

        # 如果指定了tags筛选，检查图表是否包含所有指定的tag
        if tags:
            if not all(tag in chart_tags for tag in tags):
                continue  # 跳过不包含所有指定tag的图表

        charts.append(
            ChartListResponse(
                id=chart_data["id"],
                name=chart_data["name"],
                tags=chart_tags,
                created_at=chart_data["created_at"],
                updated_at=chart_data["updated_at"],
            )
        )

    # 按更新时间倒序排序
    charts.sort(key=lambda x: x.updated_at, reverse=True)

    return charts


@router.get("/charts/tags", response_model=List[str])
async def get_all_tags(
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户所有图表的唯一tag列表"""
    user_charts = _get_user_charts(current_user.id)

    all_tags: Set[str] = set()
    for chart_id, chart_data in user_charts.items():
        chart_tags = chart_data.get("tags") or []
        all_tags.update(chart_tags)

    # 返回排序后的tag列表
    return sorted(list(all_tags))


@router.get("/charts/{chart_id}", response_model=SavedChartResponse)
async def get_chart(
    chart_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """获取图表详情"""
    user_charts = _get_user_charts(current_user.id)

    if chart_id not in user_charts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图表不存在",
        )

    return SavedChartResponse(**user_charts[chart_id])


@router.delete("/charts/{chart_id}")
async def delete_chart(
    chart_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """删除图表"""
    user_charts = _get_user_charts(current_user.id)

    if chart_id not in user_charts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图表不存在",
        )

    del user_charts[chart_id]

    return {"message": "图表已删除"}
