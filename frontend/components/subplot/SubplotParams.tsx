'use client';

import { SubplotConfig } from '@/types/canvas';
import { Info, BarChart3 } from 'lucide-react';
import ParamsEditor from './ParamsEditor';
import { BaseStyleEditor } from './params/BaseStyleEditor';
import type { PlotStyle } from '@/types/plotStyle';
import { useCanvasStore } from '@/store/canvasStore';

// 图表类型映射
const CHART_TYPE_LABELS: Record<string, string> = {
  bar: '柱状图',
  line: '折线图',
  pie: '饼图',
  area: '面积图',
  scatter: '散点图',
  bubble: '气泡图',
  hist: '直方图',
  table: '高级表格',
};

interface Props {
  subplot: SubplotConfig;
}

/**
 * 子图参数面板（右侧）
 * 显示通用样式参数编辑器
 */
export default function SubplotParams({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  // 更新样式参数
  const handleStyleChange = (updates: Partial<PlotStyle>) => {
    updateSubplot(subplot.subplotId, {
      params: {
        ...subplot.params,
        style: {
          ...subplot.params.style,
          ...updates,
        },
      },
    });
  };

  return (
    <div className="h-full overflow-y-auto p-4 space-y-6">
      {/* 通用样式编辑器 */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-3">通用样式</h2>
        <BaseStyleEditor 
          style={subplot.params.style || {}} 
          onChange={handleStyleChange}
        />
      </div>

      {/* 分隔线 */}
      <div className="border-t pt-4">
        <p className="text-xs text-gray-500 mb-2">
          提示：图表特有参数请在中间区域的「图表参数」Tab中设置
        </p>
      </div>
    </div>
  );
}
