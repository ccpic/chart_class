'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';

export default function GridControls() {
  const { canvas, updateCanvas, reset } = useCanvasStore();
  
  const handleRowsChange = (value: number) => {
    if (value >= 1 && value <= 6) {
      updateCanvas({ rows: value });
    }
  };
  
  const handleColsChange = (value: number) => {
    if (value >= 1 && value <= 6) {
      updateCanvas({ cols: value });
    }
  };
  
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">画布设置</h3>
      
      {/* 网格尺寸 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-xs text-gray-600">行数</label>
          <input
            type="number"
            min={1}
            max={6}
            value={canvas.rows}
            onChange={(e) => handleRowsChange(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-xs text-gray-600">列数</label>
          <input
            type="number"
            min={1}
            max={6}
            value={canvas.cols}
            onChange={(e) => handleColsChange(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-xs text-gray-600">宽度 (英寸)</label>
          <input
            type="number"
            min={5}
            max={30}
            step={1}
            value={canvas.width}
            onChange={(e) => updateCanvas({ width: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-xs text-gray-600">高度 (英寸)</label>
          <input
            type="number"
            min={3}
            max={20}
            step={1}
            value={canvas.height}
            onChange={(e) => updateCanvas({ height: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
          />
        </div>
      </div>
      
      {/* 间距设置 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-xs text-gray-600">水平间距</label>
          <input
            type="number"
            min={0}
            max={1}
            step={0.05}
            value={canvas.wspace}
            onChange={(e) => updateCanvas({ wspace: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-xs text-gray-600">垂直间距</label>
          <input
            type="number"
            min={0}
            max={1}
            step={0.05}
            value={canvas.hspace}
            onChange={(e) => updateCanvas({ hspace: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
          />
        </div>
      </div>
      
      {/* 画布标题 */}
      <div className="space-y-2">
        <label className="text-xs text-gray-600">画布总标题</label>
        <input
          type="text"
          value={canvas.title || ''}
          onChange={(e) => updateCanvas({ title: e.target.value || undefined })}
          placeholder="可选"
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>
      
      <div className="space-y-2">
        <label className="text-xs text-gray-600">Y轴总标题</label>
        <input
          type="text"
          value={canvas.ytitle || ''}
          onChange={(e) => updateCanvas({ ytitle: e.target.value || undefined })}
          placeholder="可选"
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>
      
      {/* 图例设置 */}
      <div className="space-y-3 pt-3 border-t">
        <div className="flex items-center justify-between">
          <label className="text-xs text-gray-600">显示画布总图例</label>
          <input
            type="checkbox"
            checked={canvas.showLegend}
            onChange={(e) => updateCanvas({ showLegend: e.target.checked })}
            className="rounded"
          />
        </div>
        
        {canvas.showLegend && (
          <>
            <div className="space-y-1">
              <label className="text-xs text-gray-600">图例位置</label>
              <select
                value={canvas.legendLoc}
                onChange={(e) => updateCanvas({ legendLoc: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="center left">右侧居中</option>
                <option value="lower center">底部居中</option>
                <option value="upper center">顶部居中</option>
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-xs text-gray-600">图例列数</label>
              <input
                type="number"
                min={1}
                max={5}
                value={canvas.legendNcol}
                onChange={(e) => updateCanvas({ legendNcol: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>
          </>
        )}
      </div>
      
      {/* 其他设置 */}
      <div className="pt-3 border-t">
        <div className="flex items-center justify-between">
          <div>
            <label className="text-xs text-gray-600">Label Outer</label>
            <p className="text-xs text-gray-400">仅显示外围刻度标签</p>
          </div>
          <input
            type="checkbox"
            checked={canvas.labelOuter}
            onChange={(e) => updateCanvas({ labelOuter: e.target.checked })}
            className="rounded"
          />
        </div>
      </div>
      
      <button
        onClick={reset}
        className="w-full px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
      >
        重置画布
      </button>
    </div>
  );
}
