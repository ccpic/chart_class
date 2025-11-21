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
 * 饼图参数编辑器
 * 对应后端 PlotPie 类的参数
 */
export default function PieParamsEditor({ subplot }: Props) {
  const { updateSubplot, canvas } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  const size = params.size ?? null;
  const labelFormatter = params.label_formatter ?? '{abs}';
  const donut = params.donut ?? false;
  const donutTitle = params.donut_title ?? '';
  const pctDistance = params.pct_distance ?? 0.8;
  const startAngle = params.start_angle ?? 90;
  const counterClock = params.counter_clock ?? false;
  const lineWidth = params.line_width ?? 1;
  const edgecolor = params.edgecolor ?? 'white';
  const labelFontsize = params.label_fontsize ?? canvas?.fontsize ?? 14;
  const circleDistance = params.circle_distance ?? 0.7;
  const fmtAbs = params.fmt_abs ?? '';
  const fmtShare = params.fmt_share ?? '';

  // 获取数据框的列名用于字段选择
  const columnOptions = subplot.data.columns || [];

  // 如果有数据且 size 为 null，默认选择第一列
  useEffect(() => {
    if (columnOptions.length > 0 && size === null) {
      updateParam('size', columnOptions[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [columnOptions.length]); // 只在列数变化时检查，避免无限循环

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
              指定用于饼图大小的数据列，如不指定则默认使用第1列
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="donut"
                checked={donut}
                onCheckedChange={(checked) => updateParam('donut', checked)}
              />
              <Label htmlFor="donut" className="text-sm cursor-pointer">
                甜甜圈图 (donut)
              </Label>
            </div>
            <p className="text-xs text-gray-500 pl-6">
              {donut ? '显示为甜甜圈图（中间有空白）' : '显示为标准饼图'}
            </p>
          </div>

          {donut && (
            <>
              <div className="space-y-2">
                <Label htmlFor="donut_title" className="text-sm font-medium">
                  甜甜圈中心文字 (donut_title)
                </Label>
                <Input
                  id="donut_title"
                  value={donutTitle}
                  onChange={(e) => updateParam('donut_title', e.target.value || null)}
                  placeholder="可选，甜甜圈图中间显示的文字"
                  className="text-sm"
                />
                <p className="text-xs text-gray-500">
                  甜甜圈图中心显示的文字内容
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="circle_distance" className="text-sm font-medium">
                  中心圆半径 (circle_distance)
                </Label>
                <div className="flex items-center gap-4">
                  <Slider
                    id="circle_distance"
                    min={0.1}
                    max={0.9}
                    step={0.05}
                    value={[circleDistance]}
                    onValueChange={(values) => updateParam('circle_distance', values[0])}
                    className="flex-1"
                  />
                  <Input
                    type="number"
                    min={0.1}
                    max={0.9}
                    step={0.05}
                    value={circleDistance}
                    onChange={(e) => updateParam('circle_distance', parseFloat(e.target.value) || 0.7)}
                    className="w-20 text-sm"
                  />
                </div>
                <p className="text-xs text-gray-500">
                  控制甜甜圈中心空白圆的大小，范围 0.1-0.9，默认 0.7
                </p>
              </div>
            </>
          )}

          <div className="space-y-2">
            <Label htmlFor="start_angle" className="text-sm font-medium">
              起始角度 (start_angle)
            </Label>
            <Input
              id="start_angle"
              type="number"
              min={0}
              max={360}
              step={1}
              value={startAngle}
              onChange={(e) => updateParam('start_angle', parseInt(e.target.value) || 90)}
              className="text-sm"
            />
            <p className="text-xs text-gray-500">
              饼图第一片扇叶从哪个角度开始，范围 0-360 度，默认 90 度（从顶部开始）
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="counter_clock"
                checked={counterClock}
                onCheckedChange={(checked) => updateParam('counter_clock', checked)}
              />
              <Label htmlFor="counter_clock" className="text-sm cursor-pointer">
                逆时针方向 (counter_clock)
              </Label>
            </div>
            <p className="text-xs text-gray-500 pl-6">
              {counterClock ? '扇叶按逆时针方向排列' : '扇叶按顺时针方向排列'}
            </p>
          </div>
        </TabsContent>

        {/* Tab 2: 标签选项 */}
        <TabsContent value="label" className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="label_formatter" className="text-sm font-medium">
              标签格式化 (label_formatter)
            </Label>
            <Input
              id="label_formatter"
              value={labelFormatter}
              onChange={(e) => updateParam('label_formatter', e.target.value || '{abs}')}
              placeholder="{abs}"
              className="text-sm"
            />
            <p className="text-xs text-gray-500">
              标签格式化字符串，支持占位符：{'{abs}'} (绝对值), {'{share}'} (占比), {'{index}'} (索引名称)
            </p>
            <p className="text-xs text-gray-400">
              示例：&quot;{'{abs}'}&quot; 或 &quot;{'{share}'}&quot; 或 &quot;{'{abs}'}\n{'{share}'}&quot; (双行显示)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="label_fontsize" className="text-sm font-medium">
              标签字体大小 (label_fontsize)
            </Label>
            <Input
              id="label_fontsize"
              type="number"
              min={8}
              max={24}
              step={1}
              value={labelFontsize}
              onChange={(e) => updateParam('label_fontsize', parseInt(e.target.value) || 14)}
              className="text-sm"
            />
            <p className="text-xs text-gray-500">
              标签文字的字体大小，范围 8-24，默认使用全局字体大小
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="pct_distance" className="text-sm font-medium">
              标签距离 (pct_distance)
            </Label>
            <div className="flex items-center gap-4">
              <Slider
                id="pct_distance"
                min={0.1}
                max={1.5}
                step={0.05}
                value={[pctDistance]}
                onValueChange={(values) => updateParam('pct_distance', values[0])}
                className="flex-1"
              />
              <Input
                type="number"
                min={0.1}
                max={1.5}
                step={0.05}
                value={pctDistance}
                onChange={(e) => updateParam('pct_distance', parseFloat(e.target.value) || 0.8)}
                className="w-20 text-sm"
              />
            </div>
            <p className="text-xs text-gray-500">
              标签距离饼图中心的距离，范围 0.1-1.5，默认 0.8
            </p>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">自定义格式化（可选）</h4>
            
            <div className="space-y-2">
              <Label htmlFor="fmt_abs" className="text-sm font-medium">
                绝对值格式化 (fmt_abs)
              </Label>
              <Input
                id="fmt_abs"
                value={fmtAbs}
                onChange={(e) => updateParam('fmt_abs', e.target.value || null)}
                placeholder={'例如: {:,.0f}'}
                className="text-sm"
              />
              <p className="text-xs text-gray-500">
                自定义绝对值显示格式，如 &quot;{'{:,.0f}'}&quot; 表示千分位分隔的整数
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="fmt_share" className="text-sm font-medium">
                占比格式化 (fmt_share)
              </Label>
              <Input
                id="fmt_share"
                value={fmtShare}
                onChange={(e) => updateParam('fmt_share', e.target.value || null)}
                placeholder={'例如: {:.1%}'}
                className="text-sm"
              />
              <p className="text-xs text-gray-500">
                自定义占比显示格式，如 &quot;{'{:.1%}'}&quot; 表示保留1位小数的百分比
              </p>
            </div>
          </div>
        </TabsContent>

        {/* Tab 3: 样式设置 */}
        <TabsContent value="style" className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="line_width" className="text-sm font-medium">
              边框宽度 (line_width)
            </Label>
            <div className="flex items-center gap-4">
              <Slider
                id="line_width"
                min={0}
                max={5}
                step={0.1}
                value={[lineWidth]}
                onValueChange={(values) => updateParam('line_width', values[0])}
                className="flex-1"
              />
              <Input
                type="number"
                min={0}
                max={5}
                step={0.1}
                value={lineWidth}
                onChange={(e) => updateParam('line_width', parseFloat(e.target.value) || 1)}
                className="w-20 text-sm"
              />
            </div>
            <p className="text-xs text-gray-500">
              扇叶边框的宽度，范围 0-5，默认 1
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="edgecolor" className="text-sm font-medium">
              边框颜色 (edgecolor)
            </Label>
            <ColorPicker
              value={edgecolor}
              onChange={(color) => updateParam('edgecolor', color)}
            />
            <p className="text-xs text-gray-500">
              扇叶边框的颜色，默认白色
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
