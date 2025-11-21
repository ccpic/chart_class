'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import ColorPicker from '@/components/color/ColorPicker';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 直方图参数编辑器
 * 对应后端 PlotHist 类的参数
 */
export default function HistParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  const bins = params.bins ?? 10;
  const tiles = params.tiles ?? 10;
  const showKde = params.show_kde ?? true;
  const showMetrics = params.show_metrics ?? true;
  const showTiles = params.show_tiles ?? false;

  return (
    <div className="space-y-4">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="display" className="text-xs">显示选项</TabsTrigger>
          <TabsTrigger value="color" className="text-xs">颜色方案</TabsTrigger>
        </TabsList>

        {/* Tab 1: 基础设置 */}
        <TabsContent value="basic" className="space-y-4 mt-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="bins" className="text-sm font-medium">
                柱数量 (bins)
              </Label>
              <span className="text-xs text-gray-500">{bins}</span>
            </div>
            <Slider
              id="bins"
              min={5}
              max={50}
              step={1}
              value={[bins]}
              onValueChange={(value) => updateParam('bins', value[0])}
              className="w-full"
            />
            <p className="text-xs text-gray-500">直方图柱的个数</p>
          </div>

        </TabsContent>

        {/* Tab 2: 显示选项 */}
        <TabsContent value="display" className="space-y-4 mt-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="show_kde"
              checked={showKde}
              onCheckedChange={(checked) => updateParam('show_kde', checked)}
            />
            <Label htmlFor="show_kde" className="text-sm cursor-pointer">
              显示核密度估计曲线 (KDE)
            </Label>
          </div>
          <p className="text-xs text-gray-500 pl-6">
            在直方图上叠加显示核密度估计曲线
          </p>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="show_metrics"
              checked={showMetrics}
              onCheckedChange={(checked) => updateParam('show_metrics', checked)}
            />
            <Label htmlFor="show_metrics" className="text-sm cursor-pointer">
              显示统计指标
            </Label>
          </div>
          <p className="text-xs text-gray-500 pl-6">
            显示均值和中位数线及标签
          </p>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_tiles"
                checked={showTiles}
                onCheckedChange={(checked) => updateParam('show_tiles', checked)}
              />
              <Label htmlFor="show_tiles" className="text-sm cursor-pointer">
                显示等分线
              </Label>
            </div>
            <p className="text-xs text-gray-500 pl-6">
              显示将数据等分的百分位线（如十分位线）
            </p>

            {showTiles && (
              <div className="space-y-2 pl-6 pt-2 border-t">
                <div className="flex items-center justify-between">
                  <Label htmlFor="tiles" className="text-sm font-medium">
                    等分线数量 (tiles)
                  </Label>
                  <span className="text-xs text-gray-500">{tiles}</span>
                </div>
                <Slider
                  id="tiles"
                  min={2}
                  max={20}
                  step={1}
                  value={[tiles]}
                  onValueChange={(value) => updateParam('tiles', value[0])}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">等分线的个数</p>
              </div>
            )}
          </div>
        </TabsContent>

        {/* Tab 3: 颜色方案 */}
        <TabsContent value="color" className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label className="text-sm font-medium">直方图颜色</Label>
            <ColorPicker
              value={params.color_hist || 'grey'}
              onChange={(color) => updateParam('color_hist', color)}
            />
            <p className="text-xs text-gray-500">直方图柱的填充颜色</p>
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium">KDE 曲线颜色</Label>
            <ColorPicker
              value={params.color_kde || 'darkorange'}
              onChange={(color) => updateParam('color_kde', color)}
            />
            <p className="text-xs text-gray-500">核密度估计曲线的颜色</p>
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium">均值线颜色</Label>
            <ColorPicker
              value={params.color_mean || 'purple'}
              onChange={(color) => updateParam('color_mean', color)}
            />
            <p className="text-xs text-gray-500">平均数标记线的颜色</p>
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium">中位数线颜色</Label>
            <ColorPicker
              value={params.color_median || 'crimson'}
              onChange={(color) => updateParam('color_median', color)}
            />
            <p className="text-xs text-gray-500">中位数标记线的颜色</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
