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
import NumberFormatEditor from '@/components/ui/number-format-editor';
import ColorPicker from '@/components/color/ColorPicker';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 条形图（横向柱状图）参数编辑器
 * 对应后端 PlotBarh 类的参数
 */
export default function BarhParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  const stacked = params.stacked ?? true;
  const showLabel = params.show_label ?? true;
  const labelFormatter = params.label_formatter ?? '{abs}';
  const labelThreshold = params.label_threshold ?? 0.02;
  const labelPos = params.label_pos ?? 'smart';
  const barHeight = params.bar_height ?? 0.8;
  const fmtAbs = params.fmt_abs ?? '{:,.0f}';
  const fmtShare = params.fmt_share ?? '{:.1%}';
  const fmtGr = params.fmt_gr ?? '{:+.1%}';
  const labelFontsize = params.label_fontsize ?? subplot.fontsize ?? 11;
  const labelColor = params.label_color ?? null;

  return (
    <div className="space-y-4">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签选项</TabsTrigger>
          <TabsTrigger value="format" className="text-xs">格式设置</TabsTrigger>
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
                堆积条形图
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              {stacked ? '各系列堆叠显示' : '各系列并列显示'}
            </p>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">条形高度设置</h4>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="bar_height" className="text-sm">
                  条形高度 (bar_height)
                </Label>
                <span className="text-xs text-gray-500">{barHeight.toFixed(1)}</span>
              </div>
              <Slider
                id="bar_height"
                min={0.1}
                max={1.0}
                step={0.1}
                value={[barHeight]}
                onValueChange={(value) => updateParam('bar_height', value[0])}
                className="w-full"
              />
              <p className="text-xs text-gray-500">
                控制条形图的高度（0.1-1.0，默认0.8）
              </p>
            </div>
          </div>
        </TabsContent>

        {/* Tab 2: 标签选项 */}
        <TabsContent value="label" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">数据标签</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_label"
                checked={showLabel}
                onCheckedChange={(checked) => updateParam('show_label', checked)}
              />
              <Label htmlFor="show_label" className="text-sm cursor-pointer">
                显示数据标签
              </Label>
            </div>

            {showLabel && (
              <>
                <div className="space-y-2 pl-6">
                  <Label htmlFor="label_formatter" className="text-sm font-medium">
                    标签格式化 <span className="text-gray-400">(Shift+Enter换行)</span>
                  </Label>
                  <Textarea
                    id="label_formatter"
                    value={labelFormatter}
                    onChange={(e) => updateParam('label_formatter', e.target.value)}
                    placeholder="{abs}, {share}, {index}, {col}, {share_total}"
                    className="min-h-[32px] text-sm resize-y"
                    rows={1}
                  />
                  <p className="text-xs text-gray-500">
                    支持: {'{abs}'} (绝对值), {'{share}'} (占比), {'{index}'} (索引), {'{col}'} (列名), {'{share_total}'} (总占比)
                  </p>
                </div>

                <div className="space-y-2 pl-6">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="label_threshold" className="text-sm">
                      标签显示阈值
                    </Label>
                    <span className="text-xs text-gray-500">{(labelThreshold * 100).toFixed(0)}%</span>
                  </div>
                  <Slider
                    id="label_threshold"
                    min={0}
                    max={0.2}
                    step={0.01}
                    value={[labelThreshold]}
                    onValueChange={(value) => updateParam('label_threshold', value[0])}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500">
                    系列占堆积之和的比例大于此值才显示标签
                  </p>
                </div>

                <div className="space-y-2 pl-6">
                  <Label htmlFor="label_pos" className="text-sm font-medium">
                    标签位置 (label_pos)
                  </Label>
                  <Select
                    value={labelPos}
                    onValueChange={(value) => updateParam('label_pos', value)}
                  >
                    <SelectTrigger id="label_pos">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="smart">智能定位</SelectItem>
                      <SelectItem value="center">居中</SelectItem>
                      <SelectItem value="outer">外侧</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-gray-500">
                    smart: 根据数据值自动判断位置；center: 标签居中显示；outer: 标签显示在条形外侧
                  </p>
                </div>
              </>
            )}
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">标签样式</h4>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="label_fontsize" className="text-sm font-medium">
                  标签字体大小
                </Label>
                <div className="mt-1.5">
                  <Input
                    id="label_fontsize"
                    type="number"
                    min="4"
                    max="24"
                    step="1"
                    value={labelFontsize}
                    onChange={(e) => updateParam('label_fontsize', parseInt(e.target.value) || 11)}
                    className="h-8 text-sm"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  控制标签文字的字体大小（4-24）
                </p>
              </div>

              <div>
                <ColorPicker
                  label="标签字体颜色"
                  value={labelColor || ''}
                  onChange={(color) => updateParam('label_color', color || null)}
                  showColorValue={true}
                />
                <p className="text-xs text-gray-500 mt-1">
                  如果留空，将根据背景自动选择颜色（白色或黑色）以确保可见性
                </p>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Tab 3: 格式设置 */}
        <TabsContent value="format" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">标签格式设置</h4>
            
            <div className="space-y-4">
              <div>
                <p className="text-xs text-gray-500 mb-2">
                  用于格式化 {'{abs}'} 占位符
                </p>
                <NumberFormatEditor
                  value={fmtAbs}
                  onChange={(format) => updateParam('fmt_abs', format)}
                  label="绝对值格式 (fmt_abs)"
                />
              </div>

              <div>
                <p className="text-xs text-gray-500 mb-2">
                  用于格式化 {'{share}'} 占位符（通常使用百分比格式）
                </p>
                <NumberFormatEditor
                  value={fmtShare}
                  onChange={(format) => updateParam('fmt_share', format)}
                  label="占比格式 (fmt_share)"
                />
              </div>

              <div>
                <p className="text-xs text-gray-500 mb-2">
                  用于格式化 {'{gr}'} 占位符（通常使用带正负号的百分比格式）
                </p>
                <NumberFormatEditor
                  value={fmtGr}
                  onChange={(format) => updateParam('fmt_gr', format)}
                  label="增长率格式 (fmt_gr)"
                />
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

