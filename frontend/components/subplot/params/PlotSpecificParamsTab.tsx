'use client';

import { PlotSpecificParamsRouter } from './PlotSpecificParamsRouter';
import type { SubplotConfig } from '@/types/canvas';
import { BarChart3 } from 'lucide-react';

interface PlotSpecificParamsTabProps {
  subplot: SubplotConfig | null;
}

/**
 * 图表类型到中文名称的映射
 */
function getChartTypeName(kind: string): string {
  const nameMap: Record<string, string> = {
    bubble: '气泡图',
    bar: '柱状图',
    line: '折线图',
    pie: '饼图',
    scatter: '散点图',
    heatmap: '热力图',
    treemap: '矩形树图',
    waffle: '华夫饼图',
    funnel: '漏斗图',
    venn: '韦恩图',
    wordcloud: '词云',
  };
  return nameMap[kind] || kind;
}

/**
 * 图表特有参数 Tab 页面
 * 显示在子图面板的第4个Tab中，包含数据源配置和图表特有参数
 */
export function PlotSpecificParamsTab({ subplot }: PlotSpecificParamsTabProps) {
  if (!subplot) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="text-center">
          <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            当前无选中子图
          </p>
          <p className="text-sm text-gray-500">
            请在"渲染预览"或其他Tab中查看图表内容
          </p>
        </div>
      </div>
    );
  }

  const chartName = getChartTypeName(subplot.chartType);

  return (
    <div className="h-full p-6">
      {/* 图表特有参数区域 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 max-h-full overflow-y-auto">
        <PlotSpecificParamsRouter subplot={subplot as any} />
      </div>
    </div>
  );
}
