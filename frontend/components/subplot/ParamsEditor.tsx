'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import BubbleParamsEditor from './params/BubbleParamsEditor';

interface Props {
  subplot: SubplotConfig;
}

// 柱状图参数
function BarParams({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };
  
  return (
    <div className="space-y-3">
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="stacked"
          checked={subplot.params.stacked ?? true}
          onChange={(e) => updateParam('stacked', e.target.checked)}
          className="rounded"
        />
        <label htmlFor="stacked" className="text-sm">堆叠显示</label>
      </div>
      
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="show_label"
          checked={subplot.params.show_label ?? true}
          onChange={(e) => updateParam('show_label', e.target.checked)}
          className="rounded"
        />
        <label htmlFor="show_label" className="text-sm">显示数值标签</label>
      </div>
      
      <div className="space-y-1">
        <label className="text-sm">标签格式化</label>
        <input
          type="text"
          value={subplot.params.label_formatter ?? '{abs}'}
          onChange={(e) => updateParam('label_formatter', e.target.value)}
          className="w-full px-2 py-1 border rounded text-sm"
          placeholder="{abs}, {share}, {gr}"
        />
        <div className="text-xs text-gray-500">
          支持占位符: {'{abs}'} (绝对值), {'{share}'} (占比), {'{gr}'} (增长率)
        </div>
      </div>
    </div>
  );
}

// 折线图参数
function LineParams({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };
  
  return (
    <div className="space-y-3">
      <div className="space-y-1">
        <label className="text-sm">标记样式</label>
        <select
          value={subplot.params.marker ?? 'o'}
          onChange={(e) => updateParam('marker', e.target.value)}
          className="w-full px-2 py-1 border rounded text-sm"
        >
          <option value="o">圆形 (o)</option>
          <option value="s">方形 (s)</option>
          <option value="^">三角形 (^)</option>
          <option value="D">菱形 (D)</option>
          <option value="">无标记</option>
        </select>
      </div>
      
      <div className="space-y-1">
        <label className="text-sm">线宽</label>
        <input
          type="number"
          value={subplot.params.linewidth ?? 2}
          onChange={(e) => updateParam('linewidth', parseFloat(e.target.value))}
          min="0.5"
          max="5"
          step="0.5"
          className="w-full px-2 py-1 border rounded text-sm"
        />
      </div>
      
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="show_label_line"
          checked={subplot.params.show_label ?? false}
          onChange={(e) => updateParam('show_label', e.target.checked)}
          className="rounded"
        />
        <label htmlFor="show_label_line" className="text-sm">显示数值标签</label>
      </div>
    </div>
  );
}

// 饼图参数
function PieParams({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };
  
  return (
    <div className="space-y-3">
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="show_label_pie"
          checked={subplot.params.show_label ?? true}
          onChange={(e) => updateParam('show_label', e.target.checked)}
          className="rounded"
        />
        <label htmlFor="show_label_pie" className="text-sm">显示标签</label>
      </div>
      
      <div className="space-y-1">
        <label className="text-sm">起始角度</label>
        <input
          type="number"
          value={subplot.params.startangle ?? 90}
          onChange={(e) => updateParam('startangle', parseInt(e.target.value))}
          min="0"
          max="360"
          className="w-full px-2 py-1 border rounded text-sm"
        />
      </div>
      
      <div className="space-y-1">
        <label className="text-sm">突出显示（索引，逗号分隔）</label>
        <input
          type="text"
          value={subplot.params.explode?.join(',') ?? ''}
          onChange={(e) => {
            const values = e.target.value
              .split(',')
              .map((v) => parseFloat(v.trim()))
              .filter((v) => !isNaN(v));
            updateParam('explode', values.length > 0 ? values : undefined);
          }}
          className="w-full px-2 py-1 border rounded text-sm"
          placeholder="0.1, 0, 0, 0"
        />
      </div>
    </div>
  );
}

// 面积图参数
function AreaParams({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };
  
  return (
    <div className="space-y-3">
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="stacked_area"
          checked={subplot.params.stacked ?? true}
          onChange={(e) => updateParam('stacked', e.target.checked)}
          className="rounded"
        />
        <label htmlFor="stacked_area" className="text-sm">堆叠显示</label>
      </div>
      
      <div className="space-y-1">
        <label className="text-sm">透明度</label>
        <input
          type="number"
          value={subplot.params.alpha ?? 0.6}
          onChange={(e) => updateParam('alpha', parseFloat(e.target.value))}
          min="0"
          max="1"
          step="0.1"
          className="w-full px-2 py-1 border rounded text-sm"
        />
      </div>
    </div>
  );
}

// 散点图参数
function ScatterParams({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };
  
  return (
    <div className="space-y-3">
      <div className="space-y-1">
        <label className="text-sm">点大小</label>
        <input
          type="number"
          value={subplot.params.s ?? 50}
          onChange={(e) => updateParam('s', parseInt(e.target.value))}
          min="10"
          max="200"
          step="10"
          className="w-full px-2 py-1 border rounded text-sm"
        />
      </div>
      
      <div className="space-y-1">
        <label className="text-sm">标记样式</label>
        <select
          value={subplot.params.marker ?? 'o'}
          onChange={(e) => updateParam('marker', e.target.value)}
          className="w-full px-2 py-1 border rounded text-sm"
        >
          <option value="o">圆形 (o)</option>
          <option value="s">方形 (s)</option>
          <option value="^">三角形 (^)</option>
          <option value="D">菱形 (D)</option>
          <option value="*">星形 (*)</option>
        </select>
      </div>
      
      <div className="space-y-1">
        <label className="text-sm">透明度</label>
        <input
          type="number"
          value={subplot.params.alpha ?? 0.6}
          onChange={(e) => updateParam('alpha', parseFloat(e.target.value))}
          min="0"
          max="1"
          step="0.1"
          className="w-full px-2 py-1 border rounded text-sm"
        />
      </div>
    </div>
  );
}

export default function ParamsEditor({ subplot }: Props) {
  const renderParams = () => {
    switch (subplot.chartType) {
      case 'bar':
        return <BarParams subplot={subplot} />;
      case 'line':
        return <LineParams subplot={subplot} />;
      case 'pie':
        return <PieParams subplot={subplot} />;
      case 'area':
        return <AreaParams subplot={subplot} />;
      case 'scatter':
        return <ScatterParams subplot={subplot} />;
      case 'bubble':
        return <BubbleParamsEditor subplot={subplot} />;
      default:
        return <div className="text-sm text-gray-500">暂无可配置参数</div>;
    }
  };
  
  return (
    <div className="space-y-2">
      <label className="text-sm font-semibold">图表参数</label>
      {renderParams()}
    </div>
  );
}
