'use client';

import { PlotSpecificParamsRouter } from './PlotSpecificParamsRouter';
import type { SubplotConfig } from '@/types/canvas';
import { BarChart3 } from 'lucide-react';
import { getChartTypeName } from '@/constants/chartTypes';

interface PlotSpecificParamsTabProps {
  subplot: SubplotConfig | null;
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
