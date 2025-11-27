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
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Trash2 } from 'lucide-react';
import NumberFormatEditor from '@/components/ui/number-format-editor';
import ColorPicker from '@/components/color/ColorPicker';

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
  const connections = params.connections ?? [];

  // 获取数据行数，用于设置 period_change 的最大值
  const dataRowCount = subplot.data?.data?.length || 1;
  const maxPeriodChange = Math.max(1, dataRowCount - 1);
  
  // 获取数据索引，用于连接线的 x1, x2 选择
  const dataIndex = subplot.data?.index || [];
  
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
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签选项</TabsTrigger>
          <TabsTrigger value="growth" className="text-xs">增长率</TabsTrigger>
          <TabsTrigger value="connection" className="text-xs">连接线</TabsTrigger>
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

        {/* Tab 4: 连接线 */}
        <TabsContent value="connection" className="space-y-4 mt-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-gray-800">连接线设置</h4>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  const newConnections = [
                    ...connections,
                    {
                      x1: 0,
                      x2: 1,
                      text: '',
                      offset: undefined,
                      color: 'black',
                      linewidth: 1,
                      linestyle: '--',
                      arrow: undefined,
                    },
                  ];
                  updateParam('connections', newConnections);
                }}
                className="gap-2"
              >
                <Plus className="h-3 w-3" />
                添加连接线
              </Button>
            </div>
            <p className="text-xs text-gray-500">
              在柱状图中连接两个柱子并显示注释文本
            </p>

            {connections.length === 0 ? (
              <div className="text-center py-8 text-sm text-gray-400">
                暂无连接线，点击上方按钮添加
              </div>
            ) : (
              <div className="space-y-4">
                {connections.map((conn: any, index: number) => (
                  <div
                    key={index}
                    className="border rounded-lg p-4 space-y-3 bg-gray-50"
                  >
                    <div className="flex items-center justify-between">
                      <h5 className="text-sm font-medium text-gray-700">
                        连接线 {index + 1}
                      </h5>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          const newConnections = connections.filter(
                            (_: any, i: number) => i !== index
                          );
                          updateParam('connections', newConnections);
                        }}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-2">
                        <Label htmlFor={`conn-x1-${index}`} className="text-xs">
                          起始柱子 (x1)
                        </Label>
                        <Select
                          value={String(conn.x1 ?? 0)}
                          onValueChange={(value) => {
                            const newConnections = [...connections];
                            newConnections[index] = {
                              ...newConnections[index],
                              x1: parseInt(value),
                            };
                            updateParam('connections', newConnections);
                          }}
                        >
                          <SelectTrigger id={`conn-x1-${index}`}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {dataIndex.map((idx: string, i: number) => (
                              <SelectItem key={i} value={String(i)}>
                                {i}: {idx}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor={`conn-x2-${index}`} className="text-xs">
                          结束柱子 (x2)
                        </Label>
                        <Select
                          value={String(conn.x2 ?? 1)}
                          onValueChange={(value) => {
                            const newConnections = [...connections];
                            newConnections[index] = {
                              ...newConnections[index],
                              x2: parseInt(value),
                            };
                            updateParam('connections', newConnections);
                          }}
                        >
                          <SelectTrigger id={`conn-x2-${index}`}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {dataIndex.map((idx: string, i: number) => (
                              <SelectItem key={i} value={String(i)}>
                                {i}: {idx}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-2">
                        <Label htmlFor={`conn-color-${index}`} className="text-xs">
                          颜色
                        </Label>
                        <ColorPicker
                          value={conn.color || '#000000'}
                          onChange={(color) => {
                            const newConnections = [...connections];
                            newConnections[index] = {
                              ...newConnections[index],
                              color: color,
                            };
                            updateParam('connections', newConnections);
                          }}
                          showColorValue={false}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor={`conn-linestyle-${index}`} className="text-xs">
                          线条样式
                        </Label>
                        <Select
                          value={conn.linestyle || '--'}
                          onValueChange={(value) => {
                            const newConnections = [...connections];
                            newConnections[index] = {
                              ...newConnections[index],
                              linestyle: value,
                            };
                            updateParam('connections', newConnections);
                          }}
                        >
                          <SelectTrigger id={`conn-linestyle-${index}`}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="-">实线 (-)</SelectItem>
                            <SelectItem value="--">虚线 (--)</SelectItem>
                            <SelectItem value="-.">点划线 (-.)</SelectItem>
                            <SelectItem value=":">点线 (:)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label htmlFor={`conn-linewidth-${index}`} className="text-xs">
                            线条宽度
                          </Label>
                          <span className="text-xs text-gray-500">
                            {conn.linewidth || 1}
                          </span>
                        </div>
                        <Slider
                          id={`conn-linewidth-${index}`}
                          min={0.5}
                          max={5}
                          step={0.5}
                          value={[conn.linewidth || 1]}
                          onValueChange={(value) => {
                            const newConnections = [...connections];
                            newConnections[index] = {
                              ...newConnections[index],
                              linewidth: value[0],
                            };
                            updateParam('connections', newConnections);
                          }}
                          className="w-full"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor={`conn-arrow-${index}`} className="text-xs">
                          箭头
                        </Label>
                        <Select
                          value={conn.arrow !== undefined ? String(conn.arrow) : 'none'}
                          onValueChange={(value) => {
                            const newConnections = [...connections];
                            newConnections[index] = {
                              ...newConnections[index],
                              arrow: value === 'none' ? undefined : parseInt(value),
                            };
                            updateParam('connections', newConnections);
                          }}
                        >
                          <SelectTrigger id={`conn-arrow-${index}`}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="none">无箭头</SelectItem>
                            <SelectItem value="1">在起始点 (x1)</SelectItem>
                            <SelectItem value="2">在结束点 (x2)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label htmlFor={`conn-offset-${index}`} className="text-xs">
                          垂直偏移量 (可选)
                        </Label>
                        <span className="text-xs text-gray-500">
                          {conn.offset !== undefined ? conn.offset.toFixed(2) : '自动'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Checkbox
                          id={`conn-offset-enabled-${index}`}
                          checked={conn.offset !== undefined}
                          onCheckedChange={(checked) => {
                            const newConnections = [...connections];
                            newConnections[index] = {
                              ...newConnections[index],
                              offset: checked ? 0.1 : undefined,
                            };
                            updateParam('connections', newConnections);
                          }}
                        />
                        <Label
                          htmlFor={`conn-offset-enabled-${index}`}
                          className="text-xs cursor-pointer"
                        >
                          自定义偏移量
                        </Label>
                        {conn.offset !== undefined && (
                          <Slider
                            min={0}
                            max={1}
                            step={0.05}
                            value={[conn.offset]}
                            onValueChange={(value) => {
                              const newConnections = [...connections];
                              newConnections[index] = {
                                ...newConnections[index],
                                offset: value[0],
                              };
                              updateParam('connections', newConnections);
                            }}
                            className="flex-1"
                          />
                        )}
                      </div>
                      <p className="text-xs text-gray-500">
                        连接线距离最高点的垂直偏移量，留空则自动计算
                      </p>
                    </div>

                    <div className="space-y-3 pt-3 border-t">
                      <h6 className="text-xs font-semibold text-gray-700">注释文本与样式</h6>

                      <div className="grid grid-cols-[1fr_120px] gap-3">
                        <div className="space-y-2">
                          <Label htmlFor={`conn-text-${index}`} className="text-xs">
                            注释文本
                          </Label>
                          <Textarea
                            id={`conn-text-${index}`}
                            value={conn.text || ''}
                            onChange={(e) => {
                              const newConnections = [...connections];
                              newConnections[index] = {
                                ...newConnections[index],
                                text: e.target.value,
                              };
                              updateParam('connections', newConnections);
                            }}
                            onKeyDown={(e) => {
                              // Shift+Enter 换行，Enter 不换行（阻止默认行为）
                              if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                              }
                            }}
                            placeholder="输入注释文本（Shift+Enter 换行）"
                            className="text-sm min-h-[60px] resize-none"
                            rows={2}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor={`conn-text-size-${index}`} className="text-xs">
                            字体大小
                          </Label>
                          <Input
                            id={`conn-text-size-${index}`}
                            type="number"
                            min={8}
                            max={72}
                            step={1}
                            value={conn.text_size ?? 12}
                            onChange={(e) => {
                              const newConnections = [...connections];
                              newConnections[index] = {
                                ...newConnections[index],
                                text_size: e.target.value ? parseFloat(e.target.value) : undefined,
                              };
                              updateParam('connections', newConnections);
                            }}
                            placeholder="12"
                            className="text-sm"
                          />
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div className="space-y-2">
                          <Label htmlFor={`conn-text-color-${index}`} className="text-xs">
                            文本颜色
                          </Label>
                          <ColorPicker
                            value={conn.text_color || conn.color || '#000000'}
                            onChange={(color) => {
                              const newConnections = [...connections];
                              newConnections[index] = {
                                ...newConnections[index],
                                text_color: color,
                              };
                              updateParam('connections', newConnections);
                            }}
                            showColorValue={false}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor={`conn-text-weight-${index}`} className="text-xs">
                            字体加粗
                          </Label>
                          <Select
                            value={conn.text_weight || 'normal'}
                            onValueChange={(value) => {
                              const newConnections = [...connections];
                              newConnections[index] = {
                                ...newConnections[index],
                                text_weight: value === 'normal' ? undefined : value,
                              };
                              updateParam('connections', newConnections);
                            }}
                          >
                            <SelectTrigger id={`conn-text-weight-${index}`}>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="normal">正常</SelectItem>
                              <SelectItem value="bold">加粗</SelectItem>
                              <SelectItem value="semibold">半粗</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div className="space-y-3 pt-2">
                        <h6 className="text-xs font-medium text-gray-600">文本框样式</h6>
                        
                        {/* 第一行：文本框形状和文本垂直偏移量 */}
                        <div className="grid grid-cols-2 gap-3">
                          <div className="space-y-2">
                            <Label htmlFor={`conn-bbox-boxstyle-${index}`} className="text-xs">
                              文本框形状
                            </Label>
                            <Select
                              value={conn.bbox_boxstyle || 'square'}
                              onValueChange={(value) => {
                                const newConnections = [...connections];
                                newConnections[index] = {
                                  ...newConnections[index],
                                  bbox_boxstyle: value === 'square' ? undefined : value,
                                };
                                updateParam('connections', newConnections);
                              }}
                            >
                              <SelectTrigger id={`conn-bbox-boxstyle-${index}`}>
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
                          </div>

                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <Label htmlFor={`conn-text-offset-${index}`} className="text-xs">
                                文本垂直偏移量
                              </Label>
                              <span className="text-xs text-gray-500">
                                {conn.text_offset !== undefined ? conn.text_offset.toFixed(2) : '0.00'}
                              </span>
                            </div>
                            <Slider
                              id={`conn-text-offset-${index}`}
                              min={-0.5}
                              max={0.5}
                              step={0.01}
                              value={[conn.text_offset ?? 0]}
                              onValueChange={(value) => {
                                const newConnections = [...connections];
                                newConnections[index] = {
                                  ...newConnections[index],
                                  text_offset: value[0],
                                };
                                updateParam('connections', newConnections);
                              }}
                              className="w-full"
                            />
                          </div>
                        </div>

                        {/* 第二行：背景颜色和边框颜色 */}
                        <div className="grid grid-cols-2 gap-3">
                          <div className="space-y-2">
                            <Label htmlFor={`conn-bbox-facecolor-${index}`} className="text-xs">
                              背景颜色
                            </Label>
                            <ColorPicker
                              value={conn.bbox_facecolor || '#FFFFFF'}
                              onChange={(color) => {
                                const newConnections = [...connections];
                                newConnections[index] = {
                                  ...newConnections[index],
                                  bbox_facecolor: color,
                                };
                                updateParam('connections', newConnections);
                              }}
                              showColorValue={false}
                            />
                          </div>

                          <div className="space-y-2">
                            <Label htmlFor={`conn-bbox-edgecolor-${index}`} className="text-xs">
                              边框颜色
                            </Label>
                            <ColorPicker
                              value={conn.bbox_edgecolor || '#000000'}
                              onChange={(color) => {
                                const newConnections = [...connections];
                                newConnections[index] = {
                                  ...newConnections[index],
                                  bbox_edgecolor: color,
                                };
                                updateParam('connections', newConnections);
                              }}
                              showColorValue={false}
                            />
                          </div>
                        </div>

                        {/* 第三行：背景透明度和边框宽度 */}
                        <div className="grid grid-cols-2 gap-3">
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <Label htmlFor={`conn-bbox-alpha-${index}`} className="text-xs">
                                背景透明度
                              </Label>
                              <span className="text-xs text-gray-500">
                                {((conn.bbox_alpha ?? 0.5) * 100).toFixed(0)}%
                              </span>
                            </div>
                            <Slider
                              id={`conn-bbox-alpha-${index}`}
                              min={0}
                              max={1}
                              step={0.05}
                              value={[conn.bbox_alpha ?? 0.5]}
                              onValueChange={(value) => {
                                const newConnections = [...connections];
                                newConnections[index] = {
                                  ...newConnections[index],
                                  bbox_alpha: value[0],
                                };
                                updateParam('connections', newConnections);
                              }}
                              className="w-full"
                            />
                          </div>

                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <Label htmlFor={`conn-bbox-linewidth-${index}`} className="text-xs">
                                边框宽度
                              </Label>
                              <span className="text-xs text-gray-500">
                                {conn.bbox_linewidth ?? 1}
                              </span>
                            </div>
                            <Slider
                              id={`conn-bbox-linewidth-${index}`}
                              min={0}
                              max={3}
                              step={0.1}
                              value={[conn.bbox_linewidth ?? 1]}
                              onValueChange={(value) => {
                                const newConnections = [...connections];
                                newConnections[index] = {
                                  ...newConnections[index],
                                  bbox_linewidth: value[0],
                                };
                                updateParam('connections', newConnections);
                              }}
                              className="w-full"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* Tab 5: 高级功能 */}
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
