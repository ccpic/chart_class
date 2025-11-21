'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 面积图参数编辑器
 * 对应后端 PlotArea 类的参数
 */
export default function AreaParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  const stacked = params.stacked ?? true;
  const showLabel = params.show_label || [];
  const endpointLabelOnly = params.endpoint_label_only ?? false;
  const linewidth = params.linewidth ?? 2;
  const alpha = params.alpha ?? 1;

  // 获取数据框的列名用于选择显示标签的系列
  const columnOptions = subplot.data.columns || [];

  // 添加/移除系列到 show_label 列表
  const toggleShowLabel = (column: string) => {
    const currentLabels = Array.isArray(showLabel) ? showLabel : [];
    if (currentLabels.includes(column)) {
      updateParam('show_label', currentLabels.filter((c: string) => c !== column));
    } else {
      updateParam('show_label', [...currentLabels, column]);
    }
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签设置</TabsTrigger>
        </TabsList>

        {/* Tab 1: 基础设置 */}
        <TabsContent value="basic" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">图表类型</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="stacked"
                checked={stacked}
                onCheckedChange={(checked) => updateParam('stacked', checked)}
              />
              <Label htmlFor="stacked" className="text-sm cursor-pointer">
                堆积面积图 (stacked)
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              {stacked ? '各系列堆叠显示，标签显示在面积中心' : '各系列并列显示，标签显示在数据点位置'}
            </p>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">样式设置</h4>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="alpha" className="text-sm">
                  透明度 (alpha)
                </Label>
                <span className="text-xs text-gray-500">{alpha.toFixed(2)}</span>
              </div>
              <Slider
                id="alpha"
                min={0}
                max={1}
                step={0.05}
                value={[alpha]}
                onValueChange={(value) => updateParam('alpha', value[0])}
                className="w-full"
              />
              <p className="text-xs text-gray-500">
                控制填充区域的透明度，1 为完全不透明，0 为完全透明
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="linewidth" className="text-sm">
                线宽 (linewidth)
              </Label>
              <Input
                id="linewidth"
                type="number"
                min={0.5}
                max={10}
                step={0.5}
                value={linewidth}
                onChange={(e) => updateParam('linewidth', parseFloat(e.target.value) || 2)}
                className="h-8 text-sm"
              />
              <p className="text-xs text-gray-500">
                面积边界线的宽度，默认值: 2
              </p>
            </div>
          </div>

          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-xs text-blue-700">
              💡 提示：堆积模式下，系列按列顺序从下往上叠加
            </p>
          </div>
        </TabsContent>

        {/* Tab 2: 标签设置 */}
        <TabsContent value="label" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">数据标签</h4>
            
            <div className="space-y-2">
              <Label className="text-sm">
                显示标签的系列 (show_label)
              </Label>
              <div className="space-y-2">
                {columnOptions.length > 0 ? (
                  columnOptions.map((column: string) => (
                    <div key={column} className="flex items-center space-x-2">
                      <Checkbox
                        id={`show-label-${column}`}
                        checked={Array.isArray(showLabel) && showLabel.includes(column)}
                        onCheckedChange={() => toggleShowLabel(column)}
                      />
                      <Label htmlFor={`show-label-${column}`} className="text-sm cursor-pointer flex-1">
                        {column}
                      </Label>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-gray-500">暂无可用列</p>
                )}
              </div>
              <p className="text-xs text-gray-500">
                选择要显示数据标签的系列
              </p>
            </div>

            {Array.isArray(showLabel) && showLabel.length > 0 && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-xs font-medium text-blue-800 mb-2">
                  已选择 {showLabel.length} 个系列显示标签:
                </p>
                <div className="flex flex-wrap gap-1">
                  {showLabel.map((col: string) => (
                    <span
                      key={col}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                    >
                      {col}
                      <button
                        onClick={() => toggleShowLabel(col)}
                        className="hover:bg-blue-200 rounded-full p-0.5"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">标签显示选项</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="endpoint_label_only"
                checked={endpointLabelOnly}
                onCheckedChange={(checked) => updateParam('endpoint_label_only', checked)}
              />
              <Label htmlFor="endpoint_label_only" className="text-sm cursor-pointer">
                仅显示首尾节点标签 (endpoint_label_only)
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              {endpointLabelOnly ? '只在第一个和最后一个数据点显示标签' : '在所有数据点显示标签'}
            </p>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">标签位置说明</h4>
            
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-md space-y-2">
              <div className="flex items-start gap-2">
                <span className="text-xs font-medium text-gray-700 mt-0.5">堆积模式:</span>
                <p className="text-xs text-gray-600 flex-1">
                  标签显示在面积区域的中心位置（上下边界的中间）
                </p>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-xs font-medium text-gray-700 mt-0.5">并列模式:</span>
                <p className="text-xs text-gray-600 flex-1">
                  标签显示在数据点的实际 Y 值位置
                </p>
              </div>
            </div>
          </div>

          <div className="p-3 bg-amber-50 border border-amber-200 rounded-md">
            <p className="text-xs text-amber-700">
              💡 提示：标签使用白色文字，并带有与面积颜色相同的背景框
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
