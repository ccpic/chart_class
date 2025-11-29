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
import { Textarea } from '@/components/ui/textarea';
import ColorPicker from '@/components/color/ColorPicker';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 瀑布图参数编辑器
 * 对应后端 PlotWaterfall 类的参数
 */
export default function WaterfallParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  const sizeColumn = params.size ?? null;
  const showConnector = params.show_connector ?? true;
  const showLabel = params.show_label ?? true;
  const labelFormatter = params.label_formatter ?? '{abs}';
  const labelPos = params.label_pos ?? 'top';
  const positiveColor = params.positive_color ?? 'green';
  const negativeColor = params.negative_color ?? 'red';
  const barWidth = params.bar_width ?? 0.8;

  // 连接线样式
  const connectorStyle = params.connector_style || {};
  const connectorColor = connectorStyle.color ?? 'gray';
  const connectorLinestyle = connectorStyle.linestyle ?? '--';
  const connectorLinewidth = connectorStyle.linewidth ?? 1;
  const connectorAlpha = connectorStyle.alpha ?? 0.7;

  // 获取数据框的列名用于字段选择
  const columnOptions = subplot.data.columns || [];

  // 如果有数据且 sizeColumn 为 null，默认选择第一列
  useEffect(() => {
    if (columnOptions.length > 0 && sizeColumn === null) {
      updateParam('size', columnOptions[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [columnOptions.length]);

  const updateConnectorStyle = (key: string, value: any) => {
    updateParam('connector_style', { ...connectorStyle, [key]: value });
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签选项</TabsTrigger>
          <TabsTrigger value="connector" className="text-xs">连接线设置</TabsTrigger>
        </TabsList>

        {/* Tab 1: 基础设置 */}
        <TabsContent value="basic" className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="sizeColumn" className="text-sm font-medium">
              数据列 (size)
            </Label>
            {columnOptions.length > 0 ? (
              <Select
                value={sizeColumn || columnOptions[0]}
                onValueChange={(value) => updateParam('size', value)}
              >
                <SelectTrigger id="sizeColumn">
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
              指定用于瀑布图的数据列，如不指定则默认使用第1列
            </p>
          </div>

          <div className="space-y-2 pt-3 border-t">
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

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">颜色设置</h4>
            
            <div className="space-y-2">
              <Label htmlFor="positive_color" className="text-sm">
                正值颜色 (positive_color)
              </Label>
              <ColorPicker
                value={positiveColor}
                onChange={(newColor) => updateParam('positive_color', newColor)}
              />
              <p className="text-xs text-gray-500">
                中间柱子正值时的颜色（默认绿色）
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="negative_color" className="text-sm">
                负值颜色 (negative_color)
              </Label>
              <ColorPicker
                value={negativeColor}
                onChange={(newColor) => updateParam('negative_color', newColor)}
              />
              <p className="text-xs text-gray-500">
                中间柱子负值时的颜色（默认红色）
              </p>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              注意：第一个和最后一个柱子使用调色板的第一个颜色
            </p>
          </div>
        </TabsContent>

        {/* Tab 2: 标签选项 */}
        <TabsContent value="label" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">数据标签</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_label_waterfall"
                checked={showLabel}
                onCheckedChange={(checked) => updateParam('show_label', checked)}
              />
              <Label htmlFor="show_label_waterfall" className="text-sm cursor-pointer">
                显示数据标签
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              显示每个柱子的数值标签
            </p>
          </div>

          {showLabel && (
            <>
              <div className="space-y-2 pl-6">
                <Label htmlFor="label_formatter_waterfall" className="text-sm font-medium">
                  标签格式化 <span className="text-gray-400">(Shift+Enter换行)</span>
                </Label>
                <Textarea
                  id="label_formatter_waterfall"
                  value={labelFormatter}
                  onChange={(e) => updateParam('label_formatter', e.target.value)}
                  placeholder="{abs}, {diff}, {index}"
                  className="min-h-[32px] text-sm resize-y"
                  rows={1}
                />
                <p className="text-xs text-gray-500">
                  支持: {'{abs}'} (绝对值), {'{diff}'} (差值), {'{index}'} (索引)
                </p>
              </div>

              <div className="space-y-2 pl-6">
                <Label htmlFor="label_pos_waterfall" className="text-sm font-medium">
                  标签位置 (label_pos)
                </Label>
                <Select
                  value={labelPos}
                  onValueChange={(value: 'top' | 'center' | 'bottom') => updateParam('label_pos', value)}
                >
                  <SelectTrigger id="label_pos_waterfall">
                    <SelectValue placeholder="选择标签位置" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="top">顶部 (top)</SelectItem>
                    <SelectItem value="center">居中 (center)</SelectItem>
                    <SelectItem value="bottom">底部 (bottom)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-gray-500">
                  标签相对于柱子的位置
                </p>
              </div>
            </>
          )}
        </TabsContent>

        {/* Tab 3: 连接线设置 */}
        <TabsContent value="connector" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">连接线</h4>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_connector_waterfall"
                checked={showConnector}
                onCheckedChange={(checked) => updateParam('show_connector', checked)}
              />
              <Label htmlFor="show_connector_waterfall" className="text-sm cursor-pointer">
                显示连接线
              </Label>
            </div>
            <p className="text-xs text-gray-500">
              在相邻柱子之间绘制连接线
            </p>
          </div>

          {showConnector && (
            <>
              <div className="space-y-3 pt-3 border-t">
                <h4 className="text-sm font-semibold text-gray-800">连接线样式</h4>
                
                <div className="space-y-2">
                  <Label htmlFor="connector_color" className="text-xs">
                    连接线颜色
                  </Label>
                  <ColorPicker
                    value={connectorColor}
                    onChange={(newColor) => updateConnectorStyle('color', newColor)}
                    showColorValue={false}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="connector_linestyle" className="text-xs">
                    线型 (linestyle)
                  </Label>
                  <Select
                    value={connectorLinestyle}
                    onValueChange={(value) => updateConnectorStyle('linestyle', value)}
                  >
                    <SelectTrigger id="connector_linestyle">
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

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="connector_linewidth" className="text-xs">
                      线宽
                    </Label>
                    <span className="text-xs text-gray-500">{connectorLinewidth.toFixed(1)}</span>
                  </div>
                  <Slider
                    id="connector_linewidth"
                    min={0.5}
                    max={5}
                    step={0.1}
                    value={[connectorLinewidth]}
                    onValueChange={(value) => updateConnectorStyle('linewidth', value[0])}
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="connector_alpha" className="text-xs">
                      透明度
                    </Label>
                    <span className="text-xs text-gray-500">{(connectorAlpha * 100).toFixed(0)}%</span>
                  </div>
                  <Slider
                    id="connector_alpha"
                    min={0}
                    max={1}
                    step={0.05}
                    value={[connectorAlpha]}
                    onValueChange={(value) => updateConnectorStyle('alpha', value[0])}
                    className="w-full"
                  />
                </div>
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

