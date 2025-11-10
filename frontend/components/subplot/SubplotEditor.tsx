'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import ChartTypeSelector from './ChartTypeSelector';
import DataEditor from './DataEditor';
import ParamsEditor from './ParamsEditor';
import { BarChart3 } from 'lucide-react';

export default function SubplotEditor() {
  const { selectedSubplotId, subplots, deleteSubplot } = useCanvasStore();
  
  const currentSubplot = subplots.find(s => s.subplotId === selectedSubplotId);
  
  if (!currentSubplot) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="text-center">
          <BarChart3 className="h-12 w-12 mx-auto mb-2 text-gray-300" />
          <p className="text-sm">选择或添加一个子图开始编辑</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6 h-full overflow-y-auto">
      {/* 头部 */}
      <div className="flex items-center justify-between pb-3 border-b">
        <div>
          <h2 className="text-lg font-semibold">子图编辑器</h2>
          <p className="text-xs text-gray-500">
            位置: 第 {currentSubplot.axIndex + 1} 个单元格
          </p>
        </div>
        <button
          onClick={() => deleteSubplot(currentSubplot.subplotId)}
          className="px-3 py-1 text-sm text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
        >
          删除
        </button>
      </div>
      
      {/* 图表类型选择 */}
      <ChartTypeSelector subplot={currentSubplot} />
      
      {/* 数据编辑 */}
      <DataEditor subplot={currentSubplot} />
      
      {/* 参数编辑 */}
      <ParamsEditor subplot={currentSubplot} />
    </div>
  );
}
