'use client';

import React, { useEffect } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import NumberFormatEditor from '@/components/ui/number-format-editor';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 柱状图参数编辑器
 * 对应后端 PlotBar 类的参数
 */
export default function BarParamsEditor({ subplot }: Props) {
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
  const showTotalBar = params.show_total_bar ?? false;
  const showTotalLabel = params.show_total_label ?? false;
  const showGrText = params.show_gr_text ?? false;
  const showGrLine = params.show_gr_line ?? false;
  const showAvgLine = params.show_avg_line ?? false;
  const labelThreshold = params.label_threshold ?? 0.02;
  const periodChange = params.period_change ?? 1;
  const barWidth = params.bar_width ?? 0.8;
  const fmtAbs = params.fmt_abs ?? '{:,.0f}';
  const fmtShare = params.fmt_share ?? '{:.1%}';
  const fmtGr = params.fmt_gr ?? '{:+.1%}';

  // 获取数据行数，用于设置 period_change 的最大值
  const dataRowCount = subplot.data?.data?.length || 1;
  const maxPeriodChange = Math.max(1, dataRowCount - 1);
  
  // 确保 periodChange 不超过最大值（用于显示）
  const validPeriodChange = Math.min(periodChange, maxPeriodChange);
  
  // 如果当前值超过最大值，自动调整
  useEffect(() => {
    if (periodChange > maxPeriodChange && maxPeriodChange > 0) {
      updateParam('period_change', maxPeriodChange);
    }
  }, [dataRowCount, maxPeriodChange]);

  return (
    <div className="space-y-4">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签选项</TabsTrigger>
          <TabsTrigger value="growth" className="text-xs">增长率</TabsTrigger>
          <TabsTrigger value="advanced" className="text-xs">高级功能</TabsTrigger>
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
                堆积柱状图
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              {stacked ? '各系列堆叠显示' : '各系列并列显示'}
            </p>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">柱宽设置</h4>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="bar_width" className="text-sm">
                  柱宽 (bar_width)
                </Label>
                <span className="text-xs text-gray-500">{barWidth.toFixed(1)}</span>
              </div>
              <Slider
                id="bar_width"
                min={0.1}
                max={1.0}
                step={0.1}
                value={[barWidth]}
                onValueChange={(value) => updateParam('bar_width', value[0])}
                className="w-full"
              />
              <p className="text-xs text-gray-500">
                控制柱状图的宽度（0.1-1.0，默认0.8）
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
                    placeholder="{abs}, {share}, {gr}, {index}, {col}"
                    className="min-h-[32px] text-sm resize-y"
                    rows={1}
                  />
                  <p className="text-xs text-gray-500">
                    支持: {'{abs}'} (绝对值), {'{share}'} (占比), {'{gr}'} (增长率), {'{index}'} (索引), {'{col}'} (列名)
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
              </>
            )}
          </div>

          <div className="space-y-3 pt-3 border-t">
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

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">总计标签</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_total_label"
                checked={showTotalLabel}
                onCheckedChange={(checked) => updateParam('show_total_label', checked)}
              />
              <Label htmlFor="show_total_label" className="text-sm cursor-pointer">
                显示堆积总计值
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              在柱状图顶端显示堆积之和
            </p>
          </div>
        </TabsContent>

        {/* Tab 3: 增长率 */}
        <TabsContent value="growth" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">增长率显示</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_gr_text"
                checked={showGrText}
                onCheckedChange={(checked) => updateParam('show_gr_text', checked)}
              />
              <Label htmlFor="show_gr_text" className="text-sm cursor-pointer">
                显示增长率数字
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              在柱间显示各系列的增长率数字
            </p>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_gr_line"
                checked={showGrLine}
                onCheckedChange={(checked) => updateParam('show_gr_line', checked)}
              />
              <Label htmlFor="show_gr_line" className="text-sm cursor-pointer">
                显示增长率折线图
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              使用次坐标轴绘制增长率折线图
            </p>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">增长率设置</h4>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="period_change" className="text-sm">
                  同比期数 (period_change)
                </Label>
                <span className="text-xs text-gray-500">{validPeriodChange}</span>
              </div>
              <Slider
                id="period_change"
                min={1}
                max={maxPeriodChange}
                step={1}
                value={[validPeriodChange]}
                onValueChange={(value) => updateParam('period_change', value[0])}
                className="w-full"
              />
              <p className="text-xs text-gray-500">
                计算增长率时对比的期数（1=同比上期，4=同比去年同期，最大{maxPeriodChange}）
              </p>
            </div>
          </div>
        </TabsContent>

        {/* Tab 4: 高级功能 */}
        <TabsContent value="advanced" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">辅助线</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_avg_line"
                checked={showAvgLine}
                onCheckedChange={(checked) => updateParam('show_avg_line', checked)}
              />
              <Label htmlFor="show_avg_line" className="text-sm cursor-pointer">
                显示平均线
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              显示平均值参考线（仅单列数据时有效）
            </p>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_total_bar"
                checked={showTotalBar}
                onCheckedChange={(checked) => updateParam('show_total_bar', checked)}
              />
              <Label htmlFor="show_total_bar" className="text-sm cursor-pointer">
                显示总体表现外框
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              在柱状图外显示总体表现的虚线框
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
