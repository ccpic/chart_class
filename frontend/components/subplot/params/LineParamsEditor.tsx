'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 折线图参数编辑器
 * 对应后端 PlotLine 类的参数
 */
export default function LineParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  const showLabel = params.show_label || [];
  const endpointLabelOnly = params.endpoint_label_only ?? false;
  const adjustLabels = params.adjust_labels ?? true;
  const linewidth = params.linewidth ?? 2;
  const linestyle = params.linestyle || '-';
  const marker = params.marker || 'o';
  const markersize = params.markersize ?? 5;
  const lineColor = params.line_color || null;

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
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="style" className="text-xs">样式选项</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签设置</TabsTrigger>
        </TabsList>

        {/* Tab 1: 基础设置 */}
        <TabsContent value="basic" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">线条样式</h4>
            
            <div className="space-y-2">
              <Label htmlFor="linestyle" className="text-sm">
                线型 (linestyle)
              </Label>
              <Select
                value={linestyle}
                onValueChange={(value) => updateParam('linestyle', value)}
              >
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="-">实线 (-)</SelectItem>
                  <SelectItem value="--">虚线 (--)</SelectItem>
                  <SelectItem value=":">点线 (:)</SelectItem>
                  <SelectItem value="-.">点划线 (-.)</SelectItem>
                </SelectContent>
              </Select>
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
                默认值: 2，范围: 0.5-10
              </p>
            </div>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">标记点样式</h4>
            
            <div className="space-y-2">
              <Label htmlFor="marker" className="text-sm">
                标记形状 (marker)
              </Label>
              <Select
                value={marker || 'none'}
                onValueChange={(value) => updateParam('marker', value === 'none' ? '' : value)}
              >
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="o">圆形 (o)</SelectItem>
                  <SelectItem value="s">方形 (s)</SelectItem>
                  <SelectItem value="^">三角形 (^)</SelectItem>
                  <SelectItem value="D">菱形 (D)</SelectItem>
                  <SelectItem value="*">星形 (*)</SelectItem>
                  <SelectItem value="+">加号 (+)</SelectItem>
                  <SelectItem value="x">叉号 (x)</SelectItem>
                  <SelectItem value="none">无标记</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="markersize" className="text-sm">
                标记大小 (markersize)
              </Label>
              <Input
                id="markersize"
                type="number"
                min={1}
                max={20}
                step={1}
                value={markersize}
                onChange={(e) => updateParam('markersize', parseInt(e.target.value) || 5)}
                className="h-8 text-sm"
              />
              <p className="text-xs text-gray-500">
                默认值: 5，范围: 1-20
              </p>
            </div>
          </div>
        </TabsContent>

        {/* Tab 2: 样式选项 */}
        <TabsContent value="style" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">颜色设置</h4>
            
            <div className="space-y-2">
              <Label htmlFor="line_color" className="text-sm">
                统一线条颜色 (line_color)
              </Label>
              <div className="flex gap-2">
                <Input
                  id="line_color"
                  type="text"
                  value={lineColor || ''}
                  onChange={(e) => updateParam('line_color', e.target.value || null)}
                  placeholder="例: #1f77b4 或 blue"
                  className="h-8 text-sm flex-1"
                />
                <Input
                  type="color"
                  value={lineColor || '#1f77b4'}
                  onChange={(e) => updateParam('line_color', e.target.value)}
                  className="h-8 w-16"
                />
              </div>
              <p className="text-xs text-gray-500">
                留空则使用默认颜色方案（按列自动分配颜色）
              </p>
            </div>

            {lineColor && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => updateParam('line_color', null)}
                className="text-xs"
              >
                清除颜色设置
              </Button>
            )}
          </div>
        </TabsContent>

        {/* Tab 3: 标签设置 */}
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
              {endpointLabelOnly ? '只在折线的第一个和最后一个点显示标签' : '在所有数据点显示标签'}
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
