"""
颜色管理 API（支持用户隔离）
每个用户有独立的颜色字典文件
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import json

from web_api.database import get_db, User
from web_api.middleware import get_current_active_user
from chart.color.color_manager import ColorManager, DEFAULT_PALETTE

router = APIRouter()

DEFAULT_COLOR_VALUE_MAP = {name: name for name in DEFAULT_PALETTE}


def ensure_default_palette(cm: ColorManager) -> None:
    """确保用户初次使用时拥有默认调色板颜色."""
    for name, color in DEFAULT_COLOR_VALUE_MAP.items():
        if cm.get(name) is None:
            cm.add(name=name, color=color, named_color=name, overwrite=False)


# ============ 数据模型 ============


class ColorCreateRequest(BaseModel):
    """创建颜色请求"""

    name: str
    color: str
    named_color: Optional[str] = None
    overwrite: bool = False


class ColorUpdateRequest(BaseModel):
    """更新颜色请求"""

    color: Optional[str] = None
    named_color: Optional[str] = None


class ColorResponse(BaseModel):
    """颜色响应"""

    name: str
    color: str
    named_color: Optional[str] = None


class MessageResponse(BaseModel):
    """通用消息响应"""

    message: str
    success: bool


class PaletteUpdateRequest(BaseModel):
    """调色板更新请求"""

    palette: List[str]


def get_user_color_manager(user_id: int) -> ColorManager:
    """获取用户的颜色管理器"""
    # 每个用户有独立的颜色文件
    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "colors"
    user_color_dir = DATA_DIR / str(user_id)
    user_color_dir.mkdir(parents=True, exist_ok=True)
    color_json_path = user_color_dir / "color_dict.json"

    return ColorManager(json_path=str(color_json_path))


@router.get("/colors", response_model=List[ColorResponse])
async def list_colors(
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户的所有颜色映射"""
    color_manager = get_user_color_manager(current_user.id)
    ensure_default_palette(color_manager)
    mappings = color_manager.list_all(search=search)
    return [
        ColorResponse(name=m.name, color=m.color, named_color=m.named_color)
        for m in mappings
    ]


@router.get("/colors/meta/stats")
async def get_color_stats(
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户的颜色统计信息"""
    color_manager = get_user_color_manager(current_user.id)
    ensure_default_palette(color_manager)
    all_colors = color_manager.to_dict()
    return {
        "total_colors": len(all_colors),
    }


@router.get("/colors/palette", response_model=List[str])
async def get_color_palette(current_user: User = Depends(get_current_active_user)):
    """获取当前用户的调色板顺序"""
    color_manager = get_user_color_manager(current_user.id)
    return color_manager.get_palette()


@router.put("/colors/palette", response_model=MessageResponse)
async def update_color_palette(
    request: PaletteUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """更新当前用户的调色板顺序"""
    color_manager = get_user_color_manager(current_user.id)
    color_manager.set_palette(request.palette)
    return MessageResponse(message="调色板已更新", success=True)


@router.get("/colors/{name}", response_model=ColorResponse)
async def get_color(
    name: str,
    current_user: User = Depends(get_current_active_user),
):
    """获取指定颜色映射"""
    color_manager = get_user_color_manager(current_user.id)
    ensure_default_palette(color_manager)
    mapping = color_manager.get(name)
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"颜色 '{name}' 不存在",
        )
    return ColorResponse(
        name=mapping.name, color=mapping.color, named_color=mapping.named_color
    )


@router.post("/colors", response_model=MessageResponse)
async def create_color(
    request: ColorCreateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """添加新颜色映射"""
    color_manager = get_user_color_manager(current_user.id)
    success = color_manager.add(
        name=request.name,
        color=request.color,
        named_color=request.named_color,
        overwrite=request.overwrite,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"颜色 '{request.name}' 已存在，请设置 overwrite=true 覆盖",
        )

    return MessageResponse(message=f"成功添加颜色 '{request.name}'", success=True)


@router.put("/colors/{name}", response_model=MessageResponse)
async def update_color(
    name: str,
    request: ColorUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """更新颜色映射"""
    color_manager = get_user_color_manager(current_user.id)
    current = color_manager.get(name)
    if not current:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"颜色 '{name}' 不存在",
        )

    update_params = {}
    if request.color is not None:
        update_params["color"] = request.color

    if "named_color" in request.model_dump(exclude_unset=True):
        update_params["named_color"] = request.named_color or ""

    success = color_manager.update(name=name, **update_params)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新颜色 '{name}' 失败",
        )

    return MessageResponse(message=f"成功更新颜色 '{name}'", success=True)


@router.delete("/colors/{name}", response_model=MessageResponse)
async def delete_color(
    name: str,
    current_user: User = Depends(get_current_active_user),
):
    """删除颜色映射"""
    color_manager = get_user_color_manager(current_user.id)
    success = color_manager.delete(name)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"颜色 '{name}' 不存在",
        )

    return MessageResponse(message=f"成功删除颜色 '{name}'", success=True)
