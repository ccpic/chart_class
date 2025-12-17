'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { HelpCircle, Plus, Trash2 } from 'lucide-react';
import ColorPicker from '@/components/color/ColorPicker';
import NumberFormatEditor from '@/components/ui/number-format-editor';
import { Button } from '@/components/ui/button';
import { CmapPicker } from '@/components/ui/cmap-picker';

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

  // 判断列是否为数值类型
  const isNumericColumn = (columnName: string): boolean => {
    if (!columnName || !subplot.data.data || subplot.data.data.length === 0) {
      return false;
    }
    
    const colIndex = subplot.data.columns.indexOf(columnName);
    if (colIndex === -1) return false;
    
    // 检查该列的所有值是否都可以转换为数字
    const values = subplot.data.data.map(row => row[colIndex]);
    const numericCount = values.filter(v => {
      if (v === null || v === undefined || v === '') return true; // 空值视为有效
      const num = typeof v === 'number' ? v : parseFloat(String(v));
      return !isNaN(num);
    }).length;
    
    // 如果超过80%的值是数字，则认为该列是数值类型
    return numericCount / values.length >= 0.8;
  };

  // 获取当前 hue 列
  const hueColumn = subplot.params.hue;
  const isHueNumeric = hueColumn ? isNumericColumn(hueColumn) : false;

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

          {/* 数值类型 hue 的 colormap 选择器 */}
          {isHueNumeric && (
            <div className="space-y-2">
              <CmapPicker
                value={subplot.params.cmap || 'PiYG'}
                onChange={(value) => updateParam('cmap', value)}
                label="颜色映射方案 (cmap)"
                showPreview={true}
                showReverse={true}
              />
              <p className="text-xs text-gray-500">
                当颜色字段为数值类型时，使用此颜色映射方案
              </p>
            </div>
          )}

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
            <Label htmlFor="label-formatter" className="text-sm font-medium">
              标签格式化 <span className="text-gray-400">(Shift+Enter换行)</span>
            </Label>
            <Textarea
              id="label-formatter"
              value={subplot.params.label_formatter || '{index}'}
              onChange={(e) => updateParam('label_formatter', e.target.value)}
              placeholder="{index}, {x}, {y}, {z}"
              className="min-h-[32px] text-sm resize-y"
              rows={1}
            />
            <p className="text-xs text-gray-500">
              支持: {'{index}'} (行索引), {'{x}'}, {'{y}'}, {'{z}'}
            </p>
          </div>

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

          {/* 极值标签控制：按 x/y/z 轴极值自动标注 */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Label className="text-sm font-medium">
                极值标签（按轴极值）
              </Label>
              <div className="group relative">
                <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-72 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                  为每个轴设置显示多少个极值标签，可选择按最大值或最小值排序选择前 N 个。
                  同一条记录可能同时是多个轴的极值，标签会重复出现。
                </div>
              </div>
            </div>
            
            {/* X 轴极值 */}
            <div className="space-y-2 p-3 bg-gray-50 rounded-md border border-gray-200">
              <div className="flex items-center justify-between">
                <Label className="text-sm font-medium">X 轴极值</Label>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-600">选择方式</span>
                  <Select
                    value={subplot.params.label_x_extreme_mode || 'max'}
                    onValueChange={(value: string) => updateParam('label_x_extreme_mode', value)}
                  >
                    <SelectTrigger className="h-7 w-24 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="max">最大值</SelectItem>
                      <SelectItem value="min">最小值</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Slider
                min={0}
                max={rowCount || 20}
                step={1}
                value={[subplot.params.label_x_extreme_count ?? 0]}
                onValueChange={([value]) => updateParam('label_x_extreme_count', value)}
                className="w-full"
              />
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-600">
                  {subplot.params.label_x_extreme_count ?? 0} 个标签
                </span>
                <span className="text-xs text-gray-500">
                  (最多 {rowCount || 20} 个)
                </span>
              </div>
            </div>

            {/* Y 轴极值 */}
            <div className="space-y-2 p-3 bg-gray-50 rounded-md border border-gray-200">
              <div className="flex items-center justify-between">
                <Label className="text-sm font-medium">Y 轴极值</Label>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-600">选择方式</span>
                  <Select
                    value={subplot.params.label_y_extreme_mode || 'max'}
                    onValueChange={(value: string) => updateParam('label_y_extreme_mode', value)}
                  >
                    <SelectTrigger className="h-7 w-24 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="max">最大值</SelectItem>
                      <SelectItem value="min">最小值</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Slider
                min={0}
                max={rowCount || 20}
                step={1}
                value={[subplot.params.label_y_extreme_count ?? 0]}
                onValueChange={([value]) => updateParam('label_y_extreme_count', value)}
                className="w-full"
              />
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-600">
                  {subplot.params.label_y_extreme_count ?? 0} 个标签
                </span>
                <span className="text-xs text-gray-500">
                  (最多 {rowCount || 20} 个)
                </span>
              </div>
            </div>

            {/* Z 轴极值 */}
            <div className="space-y-2 p-3 bg-gray-50 rounded-md border border-gray-200">
              <div className="flex items-center justify-between">
                <Label className="text-sm font-medium">Z 轴极值</Label>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-600">选择方式</span>
                  <Select
                    value={subplot.params.label_z_extreme_mode || 'max'}
                    onValueChange={(value: string) => updateParam('label_z_extreme_mode', value)}
                  >
                    <SelectTrigger className="h-7 w-24 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="max">最大值</SelectItem>
                      <SelectItem value="min">最小值</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Slider
                min={0}
                max={rowCount || 20}
                step={1}
                value={[subplot.params.label_z_extreme_count ?? 0]}
                onValueChange={([value]) => updateParam('label_z_extreme_count', value)}
                className="w-full"
              />
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-600">
                  {subplot.params.label_z_extreme_count ?? 0} 个标签
                </span>
                <span className="text-xs text-gray-500">
                  (最多 {rowCount || 20} 个)
                </span>
              </div>
            </div>
          </div>

          {/* 高亮标签：指定要高亮显示标签的项目 */}
          <div className="space-y-3 pt-3 border-t">
            <div className="flex items-center space-x-2">
              <Label className="text-sm font-medium">
                高亮标签
              </Label>
              <div className="group relative">
                <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-72 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                  指定要高亮显示标签的项目。如果输入的文本匹配项目的行索引（部分匹配），将强制显示标签并使用指定的颜色。
                </div>
              </div>
            </div>
            <div className="space-y-2">
              {Object.entries(subplot.params.label_highlight_items || {}).map(([pattern, color], idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <Textarea
                    value={pattern}
                    onChange={(e) => {
                      const newPattern = e.target.value;
                      const items = { ...(subplot.params.label_highlight_items || {}) };
                      delete items[pattern];
                      // 允许空值，仅在用户删除该项时才移除配置
                      items[newPattern] = color as string;
                      updateParam('label_highlight_items', items);
                    }}
                    placeholder="匹配文本（如：北京、总计）"
                    className="min-h-[32px] text-sm flex-1 min-w-[200px] resize-y"
                    rows={1}
                  />
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <ColorPicker
                      value={(color as string) || '#FF0000'}
                      onChange={(newColor) => {
                        const items = { ...(subplot.params.label_highlight_items || {}), [pattern]: newColor };
                        updateParam('label_highlight_items', items);
                      }}
                      variant="button"
                      showColorValue={true}
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const items = { ...(subplot.params.label_highlight_items || {}) };
                        delete items[pattern];
                        updateParam('label_highlight_items', Object.keys(items).length > 0 ? items : undefined);
                      }}
                      className="h-8 w-8 p-0 flex-shrink-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const existing = subplot.params.label_highlight_items || {};
                  // 生成唯一的键名
                  let newKey = '新项目';
                  let counter = 1;
                  while (existing[newKey]) {
                    newKey = `新项目${counter}`;
                    counter++;
                  }
                  const items = { ...existing, [newKey]: '#FF0000' };
                  updateParam('label_highlight_items', items);
                }}
                className="h-8 text-xs"
              >
                <Plus className="h-4 w-4 mr-1" /> 添加高亮项
              </Button>
            </div>
            <p className="text-xs text-gray-500">
              输入的文本会与行索引进行部分匹配，匹配成功的项目将强制显示标签并使用指定的颜色
            </p>
          </div>

          {((subplot.params.label_x_extreme_count ?? 0) > 0 || 
            (subplot.params.label_y_extreme_count ?? 0) > 0 || 
            (subplot.params.label_z_extreme_count ?? 0) > 0) && (
            <div className="space-y-3 pt-3 border-t">
              <h5 className="text-sm font-medium text-gray-700">标签调整选项</h5>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="label_draw_lines"
                  checked={subplot.params.label_draw_lines ?? true}
                  onCheckedChange={(checked) => updateParam('label_draw_lines', checked)}
                />
                <Label htmlFor="label_draw_lines" className="text-sm cursor-pointer">
                  绘制连接线 (label_draw_lines)
                </Label>
              </div>

              {(subplot.params.label_draw_lines ?? true) && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="label_linecolor" className="text-sm">
                      连接线颜色 (label_linecolor)
                    </Label>
                    <ColorPicker
                      label=""
                      value={subplot.params.label_linecolor || 'black'}
                      onChange={(color) => updateParam('label_linecolor', color || 'black')}
                      showColorValue={true}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="label_linewidth" className="text-sm">
                      连接线宽度 (label_linewidth): {(subplot.params.label_linewidth ?? 0.8).toFixed(1)}
                    </Label>
                    <Slider
                      id="label_linewidth"
                      min={0.1}
                      max={3}
                      step={0.1}
                      value={[subplot.params.label_linewidth ?? 0.8]}
                      onValueChange={([value]) => updateParam('label_linewidth', value)}
                      className="w-full"
                    />
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label htmlFor="label_max_distance" className="text-sm">
                  最大距离 (label_max_distance): {(subplot.params.label_max_distance ?? 0.1).toFixed(2)}
                </Label>
                <Slider
                  id="label_max_distance"
                  min={0.01}
                  max={0.5}
                  step={0.01}
                  value={[subplot.params.label_max_distance ?? 0.1]}
                  onValueChange={([value]) => updateParam('label_max_distance', value)}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">
                  限制标签离数据点的最大距离（相对于轴范围的比例）
                </p>
              </div>
            </div>
          )}
          
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
