'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig, ChartType } from '@/types/canvas';
import {
  BarChart3,
  LineChart,
  PieChart,
  AreaChart,
  Table2,
  BarChart4,
  Box,
} from 'lucide-react';

const CHART_TYPES: { value: ChartType; label: string; icon: React.ReactNode }[] = [
  { value: 'bar', label: '柱状图', icon: <BarChart3 className="h-5 w-5" /> },
  { value: 'line', label: '折线图', icon: <LineChart className="h-5 w-5" /> },
  { value: 'pie', label: '饼图', icon: <PieChart className="h-5 w-5" /> },
  { value: 'area', label: '面积图', icon: <AreaChart className="h-5 w-5" /> },
  { value: 'hist', label: '直方图', icon: <BarChart4 className="h-5 w-5" /> },
  { value: 'boxdot', label: '箱型图', icon: <Box className="h-5 w-5" /> },
  { value: 'table', label: '高级表格', icon: <Table2 className="h-5 w-5" /> },
];

interface Props {
  subplot: SubplotConfig;
}

export default function ChartTypeSelector({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const handleTypeChange = (chartType: ChartType) => {
    updateSubplot(subplot.subplotId, { chartType });
  };
  
  return (
    <div className="space-y-2">
      <label className="text-sm font-semibold">图表类型</label>
      <div className="grid grid-cols-3 gap-2">
        {CHART_TYPES.map((type) => (
          <button
            key={type.value}
            onClick={() => handleTypeChange(type.value)}
            className={`
              px-3 py-2 text-sm rounded-md border-2 transition-all
              ${subplot.chartType === type.value
                ? 'border-black bg-black text-white'
                : 'border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <div className="mb-1 flex justify-center">{type.icon}</div>
            <div className="text-xs">{type.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
