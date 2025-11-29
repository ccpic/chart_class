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
import type { SubplotConfig } from '@/types/canvas';

interface PlotSpecificParamsRouterProps {
  subplot: SubplotConfig;
}

/**
 * 图表类型到中文名称的映射
 */
function getChartTypeName(kind: string): string {
  const nameMap: Record<string, string> = {
    bubble: '气泡图',
    table: '高级表格',
    hist: '直方图',
    bar: '柱状图',
    barh: '条形图',
    line: '折线图',
    pie: '饼图',
    boxdot: '箱型图',
    funnel: '漏斗图',
    waterfall: '瀑布图',
    heatmap: '热力图',
    treemap: '矩形树图',
    waffle: '华夫饼图',
    venn: '韦恩图',
    wordcloud: '词云',
  };
  return nameMap[kind] || kind;
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
