'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig, ChartType } from '@/types/canvas';
import { getChartTypeName } from '@/constants/chartTypes';
import {
  BarChart3,
  LineChart,
  PieChart,
  AreaChart,
  Table2,
  BarChart4,
  Box,
  BarChart2,
  Filter,
  TrendingUp,
  Map,
} from 'lucide-react';

const CHART_TYPES: { value: ChartType; icon: React.ReactNode }[] = [
  { value: 'bar', icon: <BarChart3 className="h-5 w-5" /> },
  { value: 'barh', icon: <BarChart2 className="h-5 w-5 rotate-90" /> },
  { value: 'line', icon: <LineChart className="h-5 w-5" /> },
  { value: 'pie', icon: <PieChart className="h-5 w-5" /> },
  { value: 'area', icon: <AreaChart className="h-5 w-5" /> },
  { value: 'hist', icon: <BarChart4 className="h-5 w-5" /> },
  { value: 'boxdot', icon: <Box className="h-5 w-5" /> },
  { value: 'funnel', icon: <Filter className="h-5 w-5" /> },
  { value: 'waterfall', icon: <TrendingUp className="h-5 w-5" /> },
  { value: 'map', icon: <Map className="h-5 w-5" /> },
  { value: 'table', icon: <Table2 className="h-5 w-5" /> },
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
            <div className="text-xs">{getChartTypeName(type.value)}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
