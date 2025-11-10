'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig, ChartType } from '@/types/canvas';

const CHART_TYPES: { value: ChartType; label: string; icon: string }[] = [
  { value: 'bar', label: '柱状图', icon: '📊' },
  { value: 'line', label: '折线图', icon: '📈' },
  { value: 'pie', label: '饼图', icon: '🥧' },
  { value: 'area', label: '面积图', icon: '📉' },
  { value: 'scatter', label: '散点图', icon: '⚫' },
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
            <div className="text-lg mb-1">{type.icon}</div>
            <div className="text-xs">{type.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
