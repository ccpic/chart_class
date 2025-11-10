'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { HelpCircle } from 'lucide-react';

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
            <label className="text-sm font-medium">透明度</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={subplot.params.alpha ?? 0.6}
              onChange={(e) => updateParam('alpha', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-gray-600 text-right">
              {(subplot.params.alpha ?? 0.6).toFixed(1)}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="random_color"
              checked={subplot.params.random_color ?? false}
              onChange={(e) => updateParam('random_color', e.target.checked)}
              className="rounded"
            />
            <label htmlFor="random_color" className="text-sm">随机颜色</label>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">边框颜色</label>
            <Input
              type="text"
              value={subplot.params.edgecolor || 'black'}
              onChange={(e) => updateParam('edgecolor', e.target.value)}
              placeholder="black, white, #RRGGBB"
            />
            <p className="text-xs text-gray-500">
              支持颜色名称或十六进制值
            </p>
          </div>
        </TabsContent>

        {/* Tab 3: 坐标轴 */}
        <TabsContent value="axis" className="space-y-4 mt-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">X 轴范围</label>
            <div className="flex items-center space-x-2">
              <Input
                type="number"
                placeholder="最小值"
                value={subplot.params.xlim?.[0] ?? ''}
                onChange={(e) => {
                  const xlim = subplot.params.xlim || [null, null];
                  updateParam('xlim', [e.target.value ? parseFloat(e.target.value) : null, xlim[1]]);
                }}
              />
              <span className="text-sm">-</span>
              <Input
                type="number"
                placeholder="最大值"
                value={subplot.params.xlim?.[1] ?? ''}
                onChange={(e) => {
                  const xlim = subplot.params.xlim || [null, null];
                  updateParam('xlim', [xlim[0], e.target.value ? parseFloat(e.target.value) : null]);
                }}
              />
            </div>
            <p className="text-xs text-gray-500">
              留空则自动计算
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Y 轴范围</label>
            <div className="flex items-center space-x-2">
              <Input
                type="number"
                placeholder="最小值"
                value={subplot.params.ylim?.[0] ?? ''}
                onChange={(e) => {
                  const ylim = subplot.params.ylim || [null, null];
                  updateParam('ylim', [e.target.value ? parseFloat(e.target.value) : null, ylim[1]]);
                }}
              />
              <span className="text-sm">-</span>
              <Input
                type="number"
                placeholder="最大值"
                value={subplot.params.ylim?.[1] ?? ''}
                onChange={(e) => {
                  const ylim = subplot.params.ylim || [null, null];
                  updateParam('ylim', [ylim[0], e.target.value ? parseFloat(e.target.value) : null]);
                }}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">X 轴格式化</label>
            <Input
              type="text"
              value={subplot.params.x_fmt || '{:,.0f}'}
              onChange={(e) => updateParam('x_fmt', e.target.value)}
              placeholder="{:,.0f}"
            />
            <p className="text-xs text-gray-500">
              Python 格式化字符串
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Y 轴格式化</label>
            <Input
              type="text"
              value={subplot.params.y_fmt || '{:,.0f}'}
              onChange={(e) => updateParam('y_fmt', e.target.value)}
              placeholder="{:,.0f}"
            />
          </div>

          {/* X 均值线设置 */}
          <div className="p-3 bg-blue-50 rounded-md space-y-3 mt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">X 轴参考线（垂直）</p>
              <input
                type="checkbox"
                id="enable_x_avg"
                checked={(subplot.params.x_avg !== undefined && subplot.params.x_avg !== null)}
                onChange={(e) => {
                  if (e.target.checked) {
                    updateParam('x_avg', 0);
                  } else {
                    updateParam('x_avg', null);
                  }
                }}
                className="rounded"
              />
            </div>
            
            {(subplot.params.x_avg !== undefined && subplot.params.x_avg !== null) && (
              <div className="space-y-2">
                <label className="text-sm">参考线位置（X 值）</label>
                <Input
                  type="number"
                  value={typeof subplot.params.x_avg === 'number' ? subplot.params.x_avg : ''}
                  onChange={(e) => updateParam('x_avg', e.target.value ? parseFloat(e.target.value) : 0)}
                  placeholder="输入 X 轴数值"
                />
                <p className="text-xs text-gray-500">
                  留空或填 0 表示自动使用均值
                </p>
              </div>
            )}
          </div>

          {/* Y 均值线设置 */}
          <div className="p-3 bg-green-50 rounded-md space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Y 轴参考线（水平）</p>
              <input
                type="checkbox"
                id="enable_y_avg"
                checked={(subplot.params.y_avg !== undefined && subplot.params.y_avg !== null)}
                onChange={(e) => {
                  if (e.target.checked) {
                    updateParam('y_avg', 0);
                  } else {
                    updateParam('y_avg', null);
                  }
                }}
                className="rounded"
              />
            </div>
            
            {(subplot.params.y_avg !== undefined && subplot.params.y_avg !== null) && (
              <div className="space-y-2">
                <label className="text-sm">参考线位置（Y 值）</label>
                <Input
                  type="number"
                  value={typeof subplot.params.y_avg === 'number' ? subplot.params.y_avg : ''}
                  onChange={(e) => updateParam('y_avg', e.target.value ? parseFloat(e.target.value) : 0)}
                  placeholder="输入 Y 轴数值"
                />
                <p className="text-xs text-gray-500">
                  留空或填 0 表示自动使用均值
                </p>
              </div>
            )}
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

              <div className="space-y-2">
                <label className="text-sm">颜色</label>
                <Input
                  type="text"
                  value={subplot.params.avg_color || 'gray'}
                  onChange={(e) => updateParam('avg_color', e.target.value)}
                  placeholder="gray, red, #RRGGBB"
                />
              </div>
            </div>
          )}
        </TabsContent>

        {/* Tab 4: 气泡和标签 */}
        <TabsContent value="bubble" className="space-y-4 mt-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">气泡缩放系数</label>
            <input
              type="range"
              min="0.1"
              max="10"
              step="0.1"
              value={subplot.params.bubble_scale ?? 1}
              onChange={(e) => updateParam('bubble_scale', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-gray-600 text-right">
              {(subplot.params.bubble_scale ?? 1).toFixed(1)}
            </div>
            <p className="text-xs text-gray-500">
              控制气泡整体大小
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium">标签显示数量</label>
              <div className="group relative">
                <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                  显示前 N 个最大的气泡标签，0 为不显示
                </div>
              </div>
            </div>
            <input
              type="range"
              min="0"
              max={rowCount || 20}
              step="1"
              value={subplot.params.label_limit ?? 0}
              onChange={(e) => updateParam('label_limit', parseInt(e.target.value))}
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
            <label className="text-sm font-medium">标签格式化</label>
            <Input
              type="text"
              value={subplot.params.label_formatter || '{index}'}
              onChange={(e) => updateParam('label_formatter', e.target.value)}
              placeholder="{index}, {x}, {y}, {z}"
            />
            <p className="text-xs text-gray-500">
              支持: {'{index}'} (行索引), {'{x}'}, {'{y}'}, {'{z}'}
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium">按 Y 值标注前 N 个</label>
              <div className="group relative">
                <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                  按 Y 值排序后标注前 N 个，0 表示不限制
                </div>
              </div>
            </div>
            <input
              type="range"
              min="0"
              max={rowCount || 20}
              step="1"
              value={subplot.params.label_topy ?? 0}
              onChange={(e) => updateParam('label_topy', parseInt(e.target.value))}
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
        </TabsContent>

        {/* Tab 5: 高级统计 */}
        <TabsContent value="stats" className="space-y-4 mt-4">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="show_reg"
              checked={subplot.params.show_reg ?? false}
              onChange={(e) => updateParam('show_reg', e.target.checked)}
              className="rounded"
            />
            <label htmlFor="show_reg" className="text-sm">显示回归线（线性拟合）</label>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="show_hist"
              checked={subplot.params.show_hist ?? false}
              onChange={(e) => updateParam('show_hist', e.target.checked)}
              className="rounded"
            />
            <label htmlFor="show_hist" className="text-sm">显示分布直方图（边缘分布）</label>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="corr"
              checked={(subplot.params.corr !== undefined && subplot.params.corr !== null && subplot.params.corr !== false)}
              onChange={(e) => updateParam('corr', e.target.checked ? true : null)}
              className="rounded"
            />
            <label htmlFor="corr" className="text-sm">显示相关系数（Pearson）</label>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
