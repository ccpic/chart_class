'use client';

import BubbleParamsEditor from './BubbleParamsEditor';
import TableParamsEditor from './TableParamsEditor';
import HistParamsEditor from './HistParamsEditor';
import BarParamsEditor from './BarParamsEditor';
import BarhParamsEditor from './BarhParamsEditor';
import LineParamsEditor from './LineParamsEditor';
import AreaParamsEditor from './AreaParamsEditor';
import PieParamsEditor from './PieParamsEditor';
import BoxdotParamsEditor from './BoxdotParamsEditor';
import FunnelParamsEditor from './FunnelParamsEditor';
import WaterfallParamsEditor from './WaterfallParamsEditor';
import MapParamsEditor from './MapParamsEditor';
import type { SubplotConfig } from '@/types/canvas';
import { getChartTypeName } from '@/constants/chartTypes';

interface PlotSpecificParamsRouterProps {
  subplot: SubplotConfig;
}

/**
 * 根据图表类型路由到对应的参数编辑组件
 */
export function PlotSpecificParamsRouter({ subplot }: PlotSpecificParamsRouterProps) {
  const chartName = getChartTypeName(subplot.chartType);

  // 气泡图
  if (subplot.chartType === 'bubble') {
    return <BubbleParamsEditor subplot={subplot} />;
  }

  // 高级表格
  if (subplot.chartType === 'table') {
    return <TableParamsEditor subplot={subplot} />;
  }

  // 直方图
  if (subplot.chartType === 'hist') {
    return <HistParamsEditor subplot={subplot} />;
  }

  // 柱状图
  if (subplot.chartType === 'bar') {
    return <BarParamsEditor subplot={subplot} />;
  }

  // 条形图（横向柱状图）
  if (subplot.chartType === 'barh') {
    return <BarhParamsEditor subplot={subplot} />;
  }

  // 折线图
  if (subplot.chartType === 'line') {
    return <LineParamsEditor subplot={subplot} />;
  }

  // 面积图
  if (subplot.chartType === 'area') {
    return <AreaParamsEditor subplot={subplot} />;
  }

  // 饼图
  if (subplot.chartType === 'pie') {
    return <PieParamsEditor subplot={subplot} />;
  }

  // 箱型图
  if (subplot.chartType === 'boxdot') {
    return <BoxdotParamsEditor subplot={subplot} />;
  }

  // 漏斗图
  if (subplot.chartType === 'funnel') {
    return <FunnelParamsEditor subplot={subplot} />;
  }

  // 瀑布图
  if (subplot.chartType === 'waterfall') {
    return <WaterfallParamsEditor subplot={subplot} />;
  }

  // 热力地图
  if (subplot.chartType === 'map') {
    return <MapParamsEditor subplot={subplot} />;
  }

  // 其他图表类型显示开发中提示
  return (
    <div className="flex items-center justify-center h-32">
      <div className="text-center">
        <div className="text-4xl mb-2">🚧</div>
        <p className="text-sm font-medium text-gray-700">
          {chartName} 参数编辑器开发中
        </p>
        <p className="text-xs text-gray-500 mt-1">
          即将推出，敬请期待
        </p>
      </div>
    </div>
  );
}
