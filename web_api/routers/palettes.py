"""
调色板管理 API（独立于颜色映射）
支持用户隔离的调色板管理
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from web_api.database import get_db, User
from web_api.middleware import get_current_active_user
from web_api.palette_db_manager import PaletteDBManager

router = APIRouter()


# ============ 数据模型 ============


class PaletteResponse(BaseModel):
    """调色板响应"""

    id: int
    name: str
    is_default: bool
    colors: List[str]  # 颜色值列表（HEX 或命名颜色）
    color_count: int
    created_at: str
    updated_at: str


class PaletteListResponse(BaseModel):
    """调色板列表项"""

    id: int
    name: str
    is_default: bool
    color_count: int
    created_at: str
    updated_at: str


class PaletteUpdateRequest(BaseModel):
    """调色板更新请求"""

    colors: List[str]  # 颜色值列表（HEX 或命名颜色）


class PaletteCreateRequest(BaseModel):
    """创建调色板请求"""

    name: str
    colors: List[str]  # 颜色值列表（HEX 或命名颜色）


class MessageResponse(BaseModel):
    """通用消息响应"""

    message: str
    success: bool


def get_user_palette_manager(db: Session, user_id: int) -> PaletteDBManager:
    """获取用户的调色板管理器"""
    return PaletteDBManager(db, user_id)


@router.get("/palettes", response_model=List[PaletteListResponse])
async def list_palettes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有调色板"""
    palette_manager = get_user_palette_manager(db, current_user.id)
    palettes = palette_manager.list_palettes()

    return [
        PaletteListResponse(
            id=p["id"],
            name=p["name"],
            is_default=p["is_default"],
            color_count=p["color_count"],
            created_at=p["created_at"],
            updated_at=p["updated_at"],
        )
        for p in palettes
    ]


@router.get("/palettes/default", response_model=List[str])
async def get_default_palette(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的默认调色板"""
    palette_manager = get_user_palette_manager(db, current_user.id)
    return palette_manager.get_default_palette()


@router.put("/palettes/default", response_model=MessageResponse)
async def update_default_palette(
    request: PaletteUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新当前用户的默认调色板"""
    palette_manager = get_user_palette_manager(db, current_user.id)
    success = palette_manager.set_default_palette(request.colors)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新默认调色板失败",
        )

    return MessageResponse(message="默认调色板已更新", success=True)


@router.get("/palettes/{name}", response_model=PaletteResponse)
async def get_palette(
    name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取指定调色板"""
    palette_manager = get_user_palette_manager(db, current_user.id)
    palette = palette_manager.get_palette(name)

    if not palette:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"调色板 '{name}' 不存在",
        )

    return PaletteResponse(**palette)


@router.post("/palettes", response_model=PaletteResponse)
async def create_palette(
    request: PaletteCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建新调色板"""
    palette_manager = get_user_palette_manager(db, current_user.id)
    success = palette_manager.create_palette(request.name, request.colors)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"调色板 '{request.name}' 已存在",
        )

    # 返回创建的调色板
    palette = palette_manager.get_palette(request.name)
    if not palette:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建调色板失败",
        )

    return PaletteResponse(**palette)


@router.put("/palettes/{name}", response_model=MessageResponse)
async def update_palette(
    name: str,
    request: PaletteUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新指定调色板"""
    palette_manager = get_user_palette_manager(db, current_user.id)
    success = palette_manager.update_palette(name, request.colors)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"调色板 '{name}' 不存在",
        )

    return MessageResponse(message=f"调色板 '{name}' 已更新", success=True)


@router.delete("/palettes/{name}", response_model=MessageResponse)
async def delete_palette(
    name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除调色板（不能删除默认调色板）"""
    palette_manager = get_user_palette_manager(db, current_user.id)
    success = palette_manager.delete_palette(name)

    if not success:
        # 检查是否是默认调色板
        palette = palette_manager.get_palette(name)
        if palette and palette.get("is_default"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除默认调色板",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"调色板 '{name}' 不存在",
        )

    return MessageResponse(message=f"调色板 '{name}' 已删除", success=True)

