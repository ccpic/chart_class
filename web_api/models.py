"""
Web API 数据模型
定义所有 API 请求/响应的 Pydantic 模型
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class ChartType(str, Enum):
    """支持的图表类型"""

    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    BUBBLE = "bubble"


class ChartDataModel(BaseModel):
    """图表数据"""

    columns: List[str] = Field(..., description="列名列表")
    index: Optional[List[str]] = Field(None, description="索引列表")
    data: List[List[Any]] = Field(..., description="数据矩阵")


class SubplotConfigModel(BaseModel):
    """单个子图配置"""

    subplot_id: str = Field(..., description="子图唯一ID")
    ax_index: int = Field(..., description="子图位置索引")
    chart_type: ChartType = Field(..., description="图表类型")
    data: ChartDataModel = Field(..., description="数据")
    params: Dict[str, Any] = Field(default_factory=dict, description="图表参数")


class CanvasConfigModel(BaseModel):
    """画布配置"""

    width: float = Field(15, description="画布宽度")
    height: float = Field(6, description="画布高度")
    rows: int = Field(1, ge=1, le=6, description="网格行数")
    cols: int = Field(1, ge=1, le=6, description="网格列数")
    wspace: float = Field(0.1, description="子图水平间距")
    hspace: float = Field(0.1, description="子图垂直间距")

    # 子图宽高比例
    width_ratios: Optional[List[float]] = Field(None, description="子图宽度比例列表")
    height_ratios: Optional[List[float]] = Field(None, description="子图高度比例列表")

    # 画布级别样式
    title: Optional[str] = Field(None, description="画布总标题")
    title_fontsize: Optional[float] = Field(None, description="总标题字体大小")
    ytitle: Optional[str] = Field(None, description="Y轴总标题")
    ytitle_fontsize: Optional[float] = Field(None, description="Y轴总标题字体大小")
    fontsize: Optional[int] = Field(14, description="全局字体大小")

    # 图例配置
    show_legend: bool = Field(False, description="是否显示画布总图例")
    legend_loc: str = Field("center left", description="图例位置")
    legend_ncol: int = Field(1, description="图例列数")
    bbox_to_anchor: Optional[Tuple[float, float]] = Field(
        (1, 0.5), description="图例相对位置"
    )

    # 其他设置
    label_outer: bool = Field(False, description="仅显示外围刻度标签")
    dpi: int = Field(400, description="图片保存 DPI")
    transparent: bool = Field(True, description="是否使用透明背景")

    style: Optional[Dict[str, Any]] = Field(None, description="其他全局样式")


class RenderRequestModel(BaseModel):
    """完整渲染请求"""

    canvas: CanvasConfigModel = Field(..., description="画布配置")
    subplots: List[SubplotConfigModel] = Field(..., description="子图列表")
