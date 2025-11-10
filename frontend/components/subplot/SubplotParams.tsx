'use client';

import { SubplotConfig } from '@/types/canvas';
import { Info, BarChart3 } from 'lucide-react';
import ParamsEditor from './ParamsEditor';

// 图表类型映射
const CHART_TYPE_LABELS: Record<string, string> = {
  bar: '柱状图',
  line: '折线图',
  pie: '饼图',
  area: '面积图',
  scatter: '散点图',
  bubble: '气泡图',
};

interface Props {
  subplot: SubplotConfig;
}

/**
 * 子图参数面板（右侧）
 * 显示图表类型和参数编辑器
 */
export default function SubplotParams({ subplot }: Props) {
  return (
    <div className="h-full overflow-y-auto p-4 space-y-6">
      {/* 参数编辑 */}
    <ParamsEditor subplot={subplot} />
    </div>
  );
}
