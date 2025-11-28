"""
数据库版本的图表管理器

功能:
- 增删改查图表（使用数据库）
- 支持用户隔离
- 支持标签筛选
- 解决内存存储问题（数据持久化）
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import json
import uuid

from web_api.database import SavedChart


class ChartDBManager:
    """
    数据库版本的图表管理器
    
    功能:
    - 增删改查图表（使用数据库）
    - 支持用户隔离
    - 支持标签筛选
    - 解决内存存储问题（数据持久化）
    """

    def __init__(self, db: Session, user_id: int):
        """
        初始化图表管理器
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        """
        self.db = db
        self.user_id = user_id

    def create(
        self,
        name: str,
        canvas: Dict[str, Any],
        subplots: List[Dict[str, Any]],
        tags: Optional[List[str]] = None,
        version: str = "1.0",
        chart_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建新图表
        
        Args:
            name: 图表名称
            canvas: 画布配置
            subplots: 子图列表
            tags: 标签列表
            version: 版本号
            chart_id: 图表ID（如果提供，否则自动生成UUID）
            
        Returns:
            创建的图表数据
        """
        if chart_id is None:
            chart_id = str(uuid.uuid4())
        
        now = datetime.utcnow()
        
        chart = SavedChart(
            id=chart_id,
            user_id=self.user_id,
            name=name,
            tags=json.dumps(tags or [], ensure_ascii=False),
            canvas=json.dumps(canvas, ensure_ascii=False),
            subplots=json.dumps(subplots, ensure_ascii=False),
            version=version,
            created_at=now,
            updated_at=now,
        )
        
        self.db.add(chart)
        
        try:
            self.db.commit()
            self.db.refresh(chart)
            return self._chart_to_dict(chart)
        except Exception as e:
            self.db.rollback()
            raise e

    def update(
        self,
        chart_id: str,
        name: Optional[str] = None,
        canvas: Optional[Dict[str, Any]] = None,
        subplots: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        version: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        更新图表
        
        Args:
            chart_id: 图表ID
            name: 图表名称
            canvas: 画布配置
            subplots: 子图列表
            tags: 标签列表
            version: 版本号
            
        Returns:
            更新后的图表数据，如果不存在则返回 None
        """
        chart = (
            self.db.query(SavedChart)
            .filter(
                and_(SavedChart.user_id == self.user_id, SavedChart.id == chart_id)
            )
            .first()
        )
        
        if not chart:
            return None
        
        if name is not None:
            chart.name = name
        if canvas is not None:
            chart.canvas = json.dumps(canvas, ensure_ascii=False)
        if subplots is not None:
            chart.subplots = json.dumps(subplots, ensure_ascii=False)
        if tags is not None:
            chart.tags = json.dumps(tags, ensure_ascii=False)
        if version is not None:
            chart.version = version
        
        chart.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(chart)
            return self._chart_to_dict(chart)
        except Exception as e:
            self.db.rollback()
            raise e

    def get(self, chart_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定图表
        
        Args:
            chart_id: 图表ID
            
        Returns:
            图表数据，如果不存在则返回 None
        """
        chart = (
            self.db.query(SavedChart)
            .filter(
                and_(SavedChart.user_id == self.user_id, SavedChart.id == chart_id)
            )
            .first()
        )
        
        if not chart:
            return None
        
        return self._chart_to_dict(chart)

    def list_all(
        self,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        列出所有图表（支持标签筛选）
        
        Args:
            tags: 标签列表（AND逻辑：必须包含所有指定tag）
            
        Returns:
            图表列表（按更新时间倒序）
        """
        query = self.db.query(SavedChart).filter(
            SavedChart.user_id == self.user_id
        )
        
        charts = query.order_by(SavedChart.updated_at.desc()).all()
        
        results = []
        for chart in charts:
            chart_dict = self._chart_to_dict(chart)
            
            # 如果指定了tags筛选，检查图表是否包含所有指定的tag
            if tags:
                chart_tags = chart_dict.get("tags") or []
                if not all(tag in chart_tags for tag in tags):
                    continue  # 跳过不包含所有指定tag的图表
            
            results.append(chart_dict)
        
        return results

    def get_all_tags(self) -> List[str]:
        """
        获取当前用户所有图表的唯一tag列表
        
        Returns:
            排序后的tag列表
        """
        charts = (
            self.db.query(SavedChart)
            .filter(SavedChart.user_id == self.user_id)
            .all()
        )
        
        all_tags = set()
        for chart in charts:
            try:
                tags = json.loads(chart.tags) if chart.tags else []
                all_tags.update(tags)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return sorted(list(all_tags))

    def delete(self, chart_id: str) -> bool:
        """
        删除图表
        
        Args:
            chart_id: 图表ID
            
        Returns:
            是否成功删除
        """
        chart = (
            self.db.query(SavedChart)
            .filter(
                and_(SavedChart.user_id == self.user_id, SavedChart.id == chart_id)
            )
            .first()
        )
        
        if not chart:
            return False
        
        self.db.delete(chart)
        
        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def _chart_to_dict(self, chart: SavedChart) -> Dict[str, Any]:
        """
        将数据库模型转换为字典
        
        Args:
            chart: 图表模型
            
        Returns:
            图表字典
        """
        try:
            tags = json.loads(chart.tags) if chart.tags else []
        except (json.JSONDecodeError, TypeError):
            tags = []
        
        try:
            canvas = json.loads(chart.canvas)
        except (json.JSONDecodeError, TypeError):
            canvas = {}
        
        try:
            subplots = json.loads(chart.subplots)
        except (json.JSONDecodeError, TypeError):
            subplots = []
        
        return {
            "id": chart.id,
            "name": chart.name,
            "tags": tags,
            "canvas": canvas,
            "subplots": subplots,
            "version": chart.version,
            "created_at": chart.created_at,
            "updated_at": chart.updated_at,
        }

