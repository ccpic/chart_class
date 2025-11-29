'use client';

import React, { useEffect } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import ColorPicker from '@/components/color/ColorPicker';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 漏斗图参数编辑器
 * 对应后端 PlotFunnel 类的参数
 */
export default function FunnelParamsEditor({ subplot }: Props) {
  const { updateSubplot, canvas } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  const size = params.size ?? null;
  const height = params.height ?? 0.7;
  const color = params.color ?? 'navy';
  const showLabel = params.show_label ?? true;
  const labelHa = params.label_ha ?? 'center';
  
  // bbox 相关参数
  const bbox = params.bbox || {};
  const bboxBoxstyle = bbox.boxstyle || 'round,pad=0.5';
  const bboxFacecolor = bbox.facecolor || 'grey';
  const bboxEdgecolor = bbox.edgecolor || 'black';
  const bboxLinewidth = bbox.linewidth ?? 1;
  const bboxAlpha = bbox.alpha ?? 0.5;

  // 获取数据框的列名用于字段选择
  const columnOptions = subplot.data.columns || [];

  // 如果有数据且 size 为 null，默认选择第一列
  useEffect(() => {
    if (columnOptions.length > 0 && size === null) {
      updateParam('size', columnOptions[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [columnOptions.length]);

  // 更新 bbox 参数
  const updateBbox = (key: string, value: any) => {
    const newBbox = { ...bbox, [key]: value };
    updateParam('bbox', newBbox);
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签选项</TabsTrigger>
          <TabsTrigger value="style" className="text-xs">样式设置</TabsTrigger>
        </TabsList>

        {/* Tab 1: 基础设置 */}
        <TabsContent value="basic" className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="size" className="text-sm font-medium">
              数据列 (size)
            </Label>
            {columnOptions.length > 0 ? (
              <Select
                value={size || columnOptions[0]}
                onValueChange={(value) => updateParam('size', value)}
              >
                <SelectTrigger id="size">
                  <SelectValue placeholder="选择数据列" />
                </SelectTrigger>
                <SelectContent>
                  {columnOptions.map((col) => (
                    <SelectItem key={col} value={col}>
                      {col}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <div className="h-10 px-3 py-2 text-sm border border-gray-200 rounded-md bg-gray-50 text-gray-500 flex items-center">
                暂无数据列
              </div>
            )}
            <p className="text-xs text-gray-500">
              指定用于漏斗图大小的数据列，如不指定则默认使用第1列
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="height" className="text-sm">
                漏斗高度 (height)
              </Label>
              <span className="text-xs text-gray-500">{height.toFixed(2)}</span>
            </div>
            <Slider
              id="height"
              min={0.1}
              max={1.5}
              step={0.1}
              value={[height]}
              onValueChange={(value) => updateParam('height', value[0])}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              控制漏斗每个阶段的高度（0.1-1.5，默认0.7）
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="color" className="text-sm font-medium">
              漏斗颜色 (color)
            </Label>
            <ColorPicker
              value={color}
              onChange={(newColor) => updateParam('color', newColor)}
              showColorValue={true}
            />
            <p className="text-xs text-gray-500">
              漏斗图的填充颜色（默认：navy）
            </p>
          </div>
        </TabsContent>

        {/* Tab 2: 标签选项 */}
        <TabsContent value="label" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">标签显示</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_label"
                checked={showLabel}
                onCheckedChange={(checked) => updateParam('show_label', checked)}
              />
              <Label htmlFor="show_label" className="text-sm cursor-pointer">
                显示标签
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              是否在漏斗图左侧显示阶段标签
            </p>
          </div>

          {showLabel && (
            <div className="space-y-3 pt-3 border-t">
              <h4 className="text-sm font-semibold text-gray-800">标签对齐</h4>
              
              <div className="space-y-2">
                <Label htmlFor="label_ha" className="text-sm font-medium">
                  标签水平对齐 (label_ha)
                </Label>
                <Select
                  value={labelHa}
                  onValueChange={(value) => updateParam('label_ha', value)}
                >
                  <SelectTrigger id="label_ha">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="left">左对齐</SelectItem>
                    <SelectItem value="center">居中</SelectItem>
                    <SelectItem value="right">右对齐</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-gray-500">
                  标签文本的水平对齐方式
                </p>
              </div>
            </div>
          )}
        </TabsContent>

        {/* Tab 3: 样式设置 */}
        <TabsContent value="style" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">标签背景框样式</h4>
            
            <div className="space-y-2">
              <Label htmlFor="bbox_boxstyle" className="text-sm font-medium">
                背景框形状 (boxstyle)
              </Label>
              <Select
                value={bboxBoxstyle}
                onValueChange={(value) => updateBbox('boxstyle', value)}
              >
                <SelectTrigger id="bbox_boxstyle">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="square">方形</SelectItem>
                  <SelectItem value="round">圆角</SelectItem>
                  <SelectItem value="round,pad=0.5">圆角（大内边距）</SelectItem>
                  <SelectItem value="circle">圆形</SelectItem>
                  <SelectItem value="sawtooth">锯齿</SelectItem>
                  <SelectItem value="larrow">左箭头</SelectItem>
                  <SelectItem value="rarrow">右箭头</SelectItem>
                  <SelectItem value="darrow">双箭头</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">
                标签背景框的形状样式
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="bbox_facecolor" className="text-sm font-medium">
                  背景颜色
                </Label>
                <ColorPicker
                  value={bboxFacecolor}
                  onChange={(newColor) => updateBbox('facecolor', newColor)}
                  showColorValue={false}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="bbox_edgecolor" className="text-sm font-medium">
                  边框颜色
                </Label>
                <ColorPicker
                  value={bboxEdgecolor}
                  onChange={(newColor) => updateBbox('edgecolor', newColor)}
                  showColorValue={false}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="bbox_linewidth" className="text-sm">
                    边框宽度
                  </Label>
                  <span className="text-xs text-gray-500">{bboxLinewidth}</span>
                </div>
                <Slider
                  id="bbox_linewidth"
                  min={0}
                  max={5}
                  step={0.5}
                  value={[bboxLinewidth]}
                  onValueChange={(value) => updateBbox('linewidth', value[0])}
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="bbox_alpha" className="text-sm">
                    背景透明度
                  </Label>
                  <span className="text-xs text-gray-500">
                    {(bboxAlpha * 100).toFixed(0)}%
                  </span>
                </div>
                <Slider
                  id="bbox_alpha"
                  min={0}
                  max={1}
                  step={0.05}
                  value={[bboxAlpha]}
                  onValueChange={(value) => updateBbox('alpha', value[0])}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

