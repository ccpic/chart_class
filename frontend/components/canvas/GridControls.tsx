'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';

export default function GridControls() {
  const { canvas, updateCanvas } = useCanvasStore();
  
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
          onChange={(e) => updateCanvas({ title: e.target.value })}
          placeholder="可选"
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>
      
      <div className="space-y-2">
        <label className="text-xs text-gray-600">Y轴总标题</label>
        <input
          type="text"
          value={canvas.ytitle || ''}
          onChange={(e) => updateCanvas({ ytitle: e.target.value })}
          placeholder="可选"
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>

      {/* 字体大小 */}
      <div className="space-y-2">
        <label className="text-xs text-gray-600">全局字体大小</label>
        <input
          type="number"
          min={8}
          max={24}
          step={1}
          value={canvas.fontsize || 14}
          onChange={(e) => updateCanvas({ fontsize: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>
      
      {/* 图例设置 */}
      <div className="space-y-3 pt-3 border-t">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="showLegend"
            checked={canvas.showLegend}
            onCheckedChange={(checked) => updateCanvas({ showLegend: !!checked })}
          />
          <Label htmlFor="showLegend" className="text-xs cursor-pointer">
            显示画布总图例
          </Label>
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
      
      {/* 导出设置 */}
      <div className="space-y-3 pt-3 border-t">
        <div className="space-y-2">
          <label className="text-xs text-gray-600">图片 DPI</label>
          <input
            type="number"
            min={72}
            max={600}
            step={50}
            value={canvas.dpi || 400}
            onChange={(e) => updateCanvas({ dpi: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
          />
          <p className="text-xs text-gray-400">更高的 DPI 获得更清晰的图片</p>
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="transparent"
            checked={canvas.transparent ?? true}
            onCheckedChange={(checked) => updateCanvas({ transparent: !!checked })}
          />
          <div className="flex-1">
            <Label htmlFor="transparent" className="text-xs cursor-pointer">
              透明背景
            </Label>
            <p className="text-xs text-gray-400">保存图片时使用透明背景</p>
          </div>
        </div>
      </div>
      
      {/* 其他设置 */}
      <div className="space-y-3 pt-3 border-t">
        <h3 className="text-sm font-semibold text-gray-700">坐标轴共享</h3>
        
        <div className="flex items-center space-x-2">
          <Checkbox
            id="sharex"
            checked={canvas.sharex ?? false}
            onCheckedChange={(checked) => updateCanvas({ sharex: !!checked })}
          />
          <Label htmlFor="sharex" className="text-xs cursor-pointer">
            共享 X 轴 (sharex)
          </Label>
        </div>
        <p className="text-xs text-gray-400 pl-6">多子图共享 X 轴刻度和范围</p>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="sharey"
            checked={canvas.sharey ?? false}
            onCheckedChange={(checked) => updateCanvas({ sharey: !!checked })}
          />
          <Label htmlFor="sharey" className="text-xs cursor-pointer">
            共享 Y 轴 (sharey)
          </Label>
        </div>
        <p className="text-xs text-gray-400 pl-6">多子图共享 Y 轴刻度和范围</p>
      </div>
      
      <div className="space-y-3 pt-3 border-t">
        <h3 className="text-sm font-semibold text-gray-700">其他选项</h3>
        
        <div className="flex items-center space-x-2">
          <Checkbox
            id="labelOuter"
            checked={canvas.labelOuter}
            onCheckedChange={(checked) => updateCanvas({ labelOuter: !!checked })}
          />
          <Label htmlFor="labelOuter" className="text-xs cursor-pointer">
            Label Outer
          </Label>
        </div>
        <p className="text-xs text-gray-400 pl-6">仅显示外围刻度标签</p>
      </div>
    </div>
  );
}
