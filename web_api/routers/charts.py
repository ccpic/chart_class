"""
图表管理 API
支持用户隔离的图表保存和加载（使用数据库持久化）
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from web_api.database import get_db, User
from web_api.middleware import get_current_active_user
from web_api.chart_db_manager import ChartDBManager

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


# ============ 数据库存储 ============
# 使用数据库持久化图表数据，支持用户隔离

def get_user_chart_manager(db: Session, user_id: int) -> ChartDBManager:
    """获取用户的图表管理器（数据库版本）"""
    return ChartDBManager(db, user_id)


@router.post("/charts", response_model=SavedChartResponse)
async def save_chart(
    chart_data: SavedChartRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """保存图表"""
    chart_manager = get_user_chart_manager(db, current_user.id)
    
    saved_chart = chart_manager.create(
        name=chart_data.name,
        canvas=chart_data.canvas,
        subplots=chart_data.subplots,
        tags=chart_data.tags,
        version=chart_data.version,
    )

    return SavedChartResponse(**saved_chart)


@router.put("/charts/{chart_id}", response_model=SavedChartResponse)
async def update_chart(
    chart_id: str,
    chart_data: SavedChartRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新图表"""
    chart_manager = get_user_chart_manager(db, current_user.id)
    
    updated_chart = chart_manager.update(
        chart_id=chart_id,
        name=chart_data.name,
        canvas=chart_data.canvas,
        subplots=chart_data.subplots,
        tags=chart_data.tags,
        version=chart_data.version,
    )
    
    if not updated_chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"图表不存在: chart_id={chart_id}",
        )

    return SavedChartResponse(**updated_chart)


@router.get("/charts", response_model=List[ChartListResponse])
async def list_charts(
    tags: Optional[List[str]] = Query(
        None, description="按tag筛选（AND逻辑：必须包含所有指定tag）"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取图表列表"""
    chart_manager = get_user_chart_manager(db, current_user.id)
    
    charts_data = chart_manager.list_all(tags=tags)
    
    charts = [
        ChartListResponse(
            id=chart["id"],
            name=chart["name"],
            tags=chart["tags"],
            created_at=chart["created_at"],
            updated_at=chart["updated_at"],
        )
        for chart in charts_data
    ]

    return charts


@router.get("/charts/tags", response_model=List[str])
async def get_all_tags(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前用户所有图表的唯一tag列表"""
    chart_manager = get_user_chart_manager(db, current_user.id)
    return chart_manager.get_all_tags()


@router.get("/charts/{chart_id}", response_model=SavedChartResponse)
async def get_chart(
    chart_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取图表详情"""
    chart_manager = get_user_chart_manager(db, current_user.id)
    
    chart = chart_manager.get(chart_id)
    
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图表不存在",
        )

    return SavedChartResponse(**chart)


@router.delete("/charts/{chart_id}")
async def delete_chart(
    chart_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除图表"""
    chart_manager = get_user_chart_manager(db, current_user.id)
    
    success = chart_manager.delete(chart_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图表不存在",
        )

    return {"message": "图表已删除"}
