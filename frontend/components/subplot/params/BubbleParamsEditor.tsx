'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { HelpCircle } from 'lucide-react';
import ColorPicker from '@/components/color/ColorPicker';
import NumberFormatEditor from '@/components/ui/number-format-editor';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 气泡图参数编辑器
 * 使用 Tabs 组织为5个分组：数据源、颜色方案、坐标轴、气泡和标签、高级统计
 */
export default function BubbleParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 获取数据框的列名用于字段选择
  const columnOptions = subplot.data.columns || [];
  // 获取数据行数
  const rowCount = subplot.data.index?.length || subplot.data.data?.length || 0;

  return (
    <div className="space-y-4">
      <Tabs defaultValue="data" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="data" className="text-xs">数据源</TabsTrigger>
          <TabsTrigger value="color" className="text-xs">颜色</TabsTrigger>
          <TabsTrigger value="axis" className="text-xs">坐标轴</TabsTrigger>
          <TabsTrigger value="bubble" className="text-xs">气泡标签</TabsTrigger>
          <TabsTrigger value="stats" className="text-xs">统计</TabsTrigger>
        </TabsList>

        {/* Tab 1: 数据源 */}
        <TabsContent value="data" className="space-y-4 mt-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">X 轴字段</label>
            <Select
              value={subplot.params.x || columnOptions[0] || ''}
              onValueChange={(value: string) => updateParam('x', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="选择 X 轴字段" />
              </SelectTrigger>
              <SelectContent>
                {columnOptions.map((col: string) => (
                  <SelectItem key={col} value={col}>
                    {col}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Y 轴字段</label>
            <Select
              value={subplot.params.y || columnOptions[1] || ''}
              onValueChange={(value: string) => updateParam('y', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="选择 Y 轴字段" />
              </SelectTrigger>
              <SelectContent>
                {columnOptions.map((col: string) => (
                  <SelectItem key={col} value={col}>
                    {col}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Z 轴字段（气泡大小）</label>
            <Select
              value={subplot.params.z || columnOptions[2] || ''}
              onValueChange={(value: string) => updateParam('z', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="选择气泡大小字段" />
              </SelectTrigger>
              <SelectContent>
                {columnOptions.map((col: string) => (
                  <SelectItem key={col} value={col}>
                    {col}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-gray-500">
              Z 字段值决定气泡大小
            </p>
          </div>
        </TabsContent>

        {/* Tab 2: 颜色方案 */}
        <TabsContent value="color" className="space-y-4 mt-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">颜色字段（Hue）</label>
            <Select
              value={subplot.params.hue || '__none__'}
              onValueChange={(value: string) => updateParam('hue', value === '__none__' ? undefined : value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="不使用颜色映射" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__none__">不使用颜色映射</SelectItem>
                {columnOptions.map((col: string) => (
                  <SelectItem key={col} value={col}>
                    {col}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-gray-500">
              选择字段后，气泡颜色将按该字段的值自动分配
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="alpha-slider" className="text-sm font-medium">
              透明度: {(subplot.params.alpha ?? 0.6).toFixed(1)}
            </Label>
            <Slider
              id="alpha-slider"
              min={0}
              max={1}
              step={0.1}
              value={[subplot.params.alpha ?? 0.6]}
              onValueChange={([value]) => updateParam('alpha', value)}
              className="w-full"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="random_color"
              checked={subplot.params.random_color ?? false}
              onCheckedChange={(checked) => updateParam('random_color', checked)}
            />
            <Label htmlFor="random_color" className="text-sm cursor-pointer">
              随机颜色
            </Label>
          </div>

          <ColorPicker
            label="气泡边框颜色"
            value={subplot.params.edgecolor || '#000000'}
            onChange={(color) => updateParam('edgecolor', color)}
          />
        </TabsContent>

        {/* Tab 3: 坐标轴 */}
        <TabsContent value="axis" className="space-y-4 mt-4">
          {/* X轴格式化和Y轴格式化 - 一行 */}
          <div className="grid grid-cols-2 gap-4">
            <NumberFormatEditor
              label="X 轴格式化"
              value={subplot.params.x_fmt || '{:,.0f}'}
              onChange={(fmt) => updateParam('x_fmt', fmt)}
            />

            <NumberFormatEditor
              label="Y 轴格式化"
              value={subplot.params.y_fmt || '{:,.0f}'}
              onChange={(fmt) => updateParam('y_fmt', fmt)}
            />
          </div>

          {/* X轴参考线和Y轴参考线 - 一行 */}
          <div className="grid grid-cols-2 gap-4">
            {/* X 均值线设置 */}
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-md space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="enable_x_avg" className="text-sm font-medium cursor-pointer">
                  X 轴参考线
                </Label>
                <Checkbox
                  id="enable_x_avg"
                  checked={(subplot.params.x_avg !== undefined && subplot.params.x_avg !== null)}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      updateParam('x_avg', 0);
                    } else {
                      updateParam('x_avg', null);
                    }
                  }}
                />
              </div>
              
              {(subplot.params.x_avg !== undefined && subplot.params.x_avg !== null) && (
                <div className="space-y-2">
                  <Label htmlFor="x_avg_input" className="text-sm">参考线位置</Label>
                  <Input
                    id="x_avg_input"
                    type="number"
                    value={typeof subplot.params.x_avg === 'number' ? subplot.params.x_avg : ''}
                    onChange={(e) => updateParam('x_avg', e.target.value ? parseFloat(e.target.value) : 0)}
                    placeholder="X 值"
                  />
                  <p className="text-xs text-gray-500">0=均值</p>
                </div>
              )}
            </div>

            {/* Y 均值线设置 */}
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-md space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="enable_y_avg" className="text-sm font-medium cursor-pointer">
                  Y 轴参考线
                </Label>
                <Checkbox
                  id="enable_y_avg"
                  checked={(subplot.params.y_avg !== undefined && subplot.params.y_avg !== null)}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      updateParam('y_avg', 0);
                    } else {
                      updateParam('y_avg', null);
                    }
                  }}
                />
              </div>
              
              {(subplot.params.y_avg !== undefined && subplot.params.y_avg !== null) && (
                <div className="space-y-2">
                  <Label htmlFor="y_avg_input" className="text-sm">参考线位置</Label>
                  <Input
                    id="y_avg_input"
                    type="number"
                    value={typeof subplot.params.y_avg === 'number' ? subplot.params.y_avg : ''}
                    onChange={(e) => updateParam('y_avg', e.target.value ? parseFloat(e.target.value) : 0)}
                    placeholder="Y 值"
                  />
                  <p className="text-xs text-gray-500">0=均值</p>
                </div>
              )}
            </div>
          </div>

          {/* 参考线样式 */}
          {((subplot.params.x_avg !== undefined && subplot.params.x_avg !== null) || 
            (subplot.params.y_avg !== undefined && subplot.params.y_avg !== null)) && (
            <div className="p-3 bg-gray-50 rounded-md space-y-3">
              <p className="text-sm font-medium">参考线样式</p>
              
              <div className="space-y-2">
                <label className="text-sm">线型</label>
                <Select
                  value={subplot.params.avg_linestyle || '--'}
                  onValueChange={(value: string) => updateParam('avg_linestyle', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="--">虚线 (--)</SelectItem>
                    <SelectItem value="-">实线 (-)</SelectItem>
                    <SelectItem value=":">点线 (:)</SelectItem>
                    <SelectItem value="-.">点划线 (-.)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm">线宽</label>
                <Input
                  type="number"
                  value={subplot.params.avg_linewidth ?? 1}
                  onChange={(e) => updateParam('avg_linewidth', parseFloat(e.target.value))}
                  min="0.5"
                  max="5"
                  step="0.5"
                />
              </div>

              <ColorPicker
                label="颜色"
                value={subplot.params.avg_color || '#808080'}
                onChange={(color) => updateParam('avg_color', color)}
              />
            </div>
          )}
        </TabsContent>

        {/* Tab 4: 气泡和标签 */}
        <TabsContent value="bubble" className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="bubble-scale-slider" className="text-sm font-medium">
              气泡缩放系数: {(subplot.params.bubble_scale ?? 1).toFixed(1)}
            </Label>
            <Slider
              id="bubble-scale-slider"
              min={0.1}
              max={10}
              step={0.1}
              value={[subplot.params.bubble_scale ?? 1]}
              onValueChange={([value]) => updateParam('bubble_scale', value)}
              className="w-full"
            />
            <p className="text-xs text-gray-500">控制气泡整体大小</p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Label htmlFor="label-limit-slider" className="text-sm font-medium">
                标签显示数量
              </Label>
              <div className="group relative">
                <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                  显示前 N 个气泡标签，0 为不显示
                </div>
              </div>
            </div>
            <Slider
              id="label-limit-slider"
              min={0}
              max={rowCount || 20}
              step={1}
              value={[subplot.params.label_limit ?? 0]}
              onValueChange={([value]) => updateParam('label_limit', value)}
              className="w-full"
            />
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">
                {subplot.params.label_limit ?? 0} 个标签
              </span>
              <span className="text-xs text-gray-500">
                (最多 {rowCount || 20} 个)
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Label htmlFor="label-topy-slider" className="text-sm font-medium">
                按 Y 值标注前 N 个
              </Label>
              <div className="group relative">
                <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                  按 Y 值排序后标注前 N 个，0 表示不限制
                </div>
              </div>
            </div>
            <Slider
              id="label-topy-slider"
              min={0}
              max={rowCount || 20}
              step={1}
              value={[subplot.params.label_topy ?? 0]}
              onValueChange={([value]) => updateParam('label_topy', value)}
              className="w-full"
            />
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">
                {subplot.params.label_topy ?? 0} 个标签
              </span>
              <span className="text-xs text-gray-500">
                (最多 {rowCount || 20} 个)
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="label-formatter" className="text-sm font-medium">
              标签格式化
            </Label>
            <Input
              id="label-formatter"
              type="text"
              value={subplot.params.label_formatter || '{index}'}
              onChange={(e) => updateParam('label_formatter', e.target.value)}
              placeholder="{index}, {x}, {y}, {z}"
            />
            <p className="text-xs text-gray-500">
              支持: {'{index}'} (行索引), {'{x}'}, {'{y}'}, {'{z}'}
            </p>
          </div>

          
        </TabsContent>

        {/* Tab 5: 高级统计 */}
        <TabsContent value="stats" className="space-y-4 mt-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="show_reg"
              checked={subplot.params.show_reg ?? false}
              onCheckedChange={(checked) => updateParam('show_reg', checked)}
            />
            <Label htmlFor="show_reg" className="text-sm cursor-pointer">
              显示回归线（线性拟合）
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="show_hist"
              checked={subplot.params.show_hist ?? false}
              onCheckedChange={(checked) => updateParam('show_hist', checked)}
            />
            <Label htmlFor="show_hist" className="text-sm cursor-pointer">
              显示分布直方图（边缘分布）
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="corr"
              checked={(subplot.params.corr !== undefined && subplot.params.corr !== null && subplot.params.corr !== false)}
              onCheckedChange={(checked) => updateParam('corr', checked ? true : null)}
            />
            <Label htmlFor="corr" className="text-sm cursor-pointer">
              显示相关系数（Pearson）
            </Label>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
