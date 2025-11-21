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
import { Button } from '@/components/ui/button';
import { ArrowDown, ArrowUp, RotateCcw } from 'lucide-react';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 箱型图参数编辑器
 * 对应后端 PlotBoxdot 类的参数
 */
export default function BoxdotParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  const x = params.x ?? null;
  const y = params.y ?? null;
  const labelLimit = params.label_limit ?? 0;
  const labelThreshold = params.label_threshold ?? 0;
  const whisParam = params.whis ?? 'inf';
  const showStats = params.show_stats ?? true;
  const dotSize = params.dot_size ?? 8;
  const dotJitter = params.jitter ?? 0.2;
  const dotEdgeColor = params.dot_edgecolor ?? '#000000';
  const dotAlpha = params.dot_alpha ?? 0.5;
  const dotLineWidth = params.dot_linewidth ?? 1.0;

  // 获取数据框的列名用于字段选择
  const columnOptions = subplot.data.columns || [];
  const dataRows: any[][] = Array.isArray(subplot.data?.data) ? subplot.data.data : [];
  const dataCount = dataRows.length;
  const labelLimitMax = dataCount > 0 ? dataCount : 0;
  const effectiveX = x ?? columnOptions[0] ?? null;
  const selectedXIndex = effectiveX ? columnOptions.indexOf(effectiveX) : -1;

  const xCategories = React.useMemo(() => {
    if (selectedXIndex === -1) return [];
    const seen = new Set<string>();
    const categories: any[] = [];
    dataRows.forEach((row) => {
      const value = row?.[selectedXIndex];
      const key =
        typeof value === 'object'
          ? JSON.stringify(value)
          : String(value ?? '__NULL__');
      if (!seen.has(key)) {
        seen.add(key);
        categories.push(value);
      }
    });
    return categories;
  }, [dataRows, selectedXIndex]);

  const orderParam: any[] = Array.isArray(params.order) ? params.order : [];
  const resolvedOrder = React.useMemo(() => {
    if (!xCategories.length) return [];
    const sanitized = orderParam.filter((item) =>
      xCategories.some((cat) => cat === item)
    );
    const remaining = xCategories.filter(
      (cat) => !sanitized.some((item) => item === cat)
    );
    return [...sanitized, ...remaining];
  }, [orderParam, xCategories]);

  useEffect(() => {
    if (labelLimit > labelLimitMax) {
      updateParam('label_limit', labelLimitMax);
    }
  }, [labelLimit, labelLimitMax]);

  const whisDisplayValue =
    typeof whisParam === 'number' ? whisParam.toString() : (whisParam ?? 'inf').toString();

  const handleWhisChange = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed) {
      updateParam('whis', 'inf');
      return;
    }
    if (trimmed.toLowerCase() === 'inf' || trimmed === '∞') {
      updateParam('whis', 'inf');
      return;
    }
    const parsed = parseFloat(trimmed);
    if (!Number.isNaN(parsed) && parsed > 0) {
      updateParam('whis', parsed);
    } else {
      updateParam('whis', trimmed);
    }
  };

  const formatCategoryLabel = (value: any) => {
    if (value === null || value === undefined || value === '') {
      return '（空值）';
    }
    return String(value);
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签选项</TabsTrigger>
          <TabsTrigger value="scatter" className="text-xs">散点设置</TabsTrigger>
        </TabsList>

        {/* Tab 1: 基础设置 */}
        <TabsContent value="basic" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">数据源</h4>

            <div className="space-y-2">
              <Label htmlFor="x-column" className="text-sm">
                X 轴字段 (x)
              </Label>
              {columnOptions.length > 0 ? (
                <Select
                  value={x || columnOptions[0] || ''}
                  onValueChange={(value) => updateParam('x', value || null)}
                >
                  <SelectTrigger id="x-column" className="h-8 text-xs">
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
                指定 X 轴类别数据的字段名，如不指定则默认使用第1列
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="y-column" className="text-sm">
                Y 轴字段 (y)
              </Label>
              {columnOptions.length > 0 ? (
                <Select
                  value={y || (columnOptions.length > 1 ? columnOptions[1] : columnOptions[0]) || ''}
                  onValueChange={(value) => updateParam('y', value || null)}
                >
                  <SelectTrigger id="y-column" className="h-8 text-xs">
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
                指定 Y 轴数值数据的字段名，如不指定则默认使用第2列
              </p>
            </div>
          </div>

          {xCategories.length > 0 && (
            <div className="space-y-3 pt-3 border-t">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-gray-800">类别顺序 (order)</h4>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => updateParam('order', xCategories)}
                  disabled={!orderParam.length}
                  className="text-xs flex items-center gap-1"
                >
                  <RotateCcw className="h-4 w-4" />
                  重置
                </Button>
              </div>
              <p className="text-xs text-gray-500">
                根据需要调整箱型图中各类别的显示顺序。默认按照数据出现的顺序。
              </p>
              <div className="space-y-2">
                {resolvedOrder.map((category, idx) => (
                  <div
                    key={`${String(category)}-${idx}`}
                    className="flex items-center gap-2"
                  >
                    <div className="flex-1 px-3 py-2 border border-gray-200 rounded-md text-sm bg-white">
                      {formatCategoryLabel(category)}
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        type="button"
                        size="icon"
                        variant="outline"
                        disabled={idx === 0}
                        onClick={() => {
                          if (idx === 0) return;
                          const next = [...resolvedOrder];
                          [next[idx - 1], next[idx]] = [next[idx], next[idx - 1]];
                          updateParam('order', next);
                        }}
                      >
                        <ArrowUp className="h-4 w-4" />
                      </Button>
                      <Button
                        type="button"
                        size="icon"
                        variant="outline"
                        disabled={idx === resolvedOrder.length - 1}
                        onClick={() => {
                          if (idx === resolvedOrder.length - 1) return;
                          const next = [...resolvedOrder];
                          [next[idx], next[idx + 1]] = [next[idx + 1], next[idx]];
                          updateParam('order', next);
                        }}
                      >
                        <ArrowDown className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">统计显示</h4>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="show_stats"
                checked={showStats}
                onCheckedChange={(checked) => updateParam('show_stats', checked)}
              />
              <Label htmlFor="show_stats" className="text-sm cursor-pointer">
                显示统计值 (show_stats)
              </Label>
            </div>
            <p className="text-xs text-gray-500 pl-6">
              {showStats ? '显示最大值、最小值、中位数标签' : '不显示统计值标签'}
            </p>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">箱型图参数</h4>

            <div className="space-y-2">
              <Label htmlFor="whis" className="text-sm font-medium">
                箱型图须长度 (whis)
              </Label>
              <Input
                id="whis"
                type="text"
                value={whisDisplayValue}
                onChange={(e) => handleWhisChange(e.target.value)}
                placeholder="inf 或 1.5"
                className="w-full text-sm"
              />
              <p className="text-xs text-gray-500">
                控制箱型图须的长度。输入数字（如 1.5 表示 1.5×IQR）或 inf（包含所有异常值），默认 inf。
              </p>
            </div>
          </div>
        </TabsContent>

        {/* Tab 2: 标签选项 */}
        <TabsContent value="label" className="space-y-4 mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="label_limit" className="text-sm font-medium">
                标签数量限制 (label_limit)
              </Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="label_limit"
                  min={0}
                  max={labelLimitMax}
                  step={1}
                  value={[labelLimit]}
                  onValueChange={(values) => updateParam('label_limit', values[0])}
                  className="flex-1"
                />
                <Input
                  type="number"
                  min={0}
                  max={labelLimitMax}
                  step={1}
                  value={labelLimit}
                  onChange={(e) => updateParam('label_limit', parseInt(e.target.value, 10) || 0)}
                  className="w-20 text-sm"
                />
              </div>
              <p className="text-xs text-gray-500">
                展示数据点标签的数量，0 表示不显示标签，范围 0-{labelLimitMax}（当前数据量 {dataCount}），默认 0
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="label_threshold" className="text-sm font-medium">
                标签阈值 (label_threshold)
              </Label>
              <Input
                id="label_threshold"
                type="number"
                min={0}
                step={0.1}
                value={labelThreshold}
                onChange={(e) => updateParam('label_threshold', parseFloat(e.target.value) || 0)}
                className="w-full text-sm"
              />
              <p className="text-xs text-gray-500">
                对大于此 Y 轴值的数据点展示标签，支持小数，默认 0
              </p>
            </div>
          </div>
        </TabsContent>

        {/* Tab 3: 散点设置 */}
        <TabsContent value="scatter" className="space-y-4 mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="dot_size" className="text-sm font-medium">
                散点大小 (dot_size)
              </Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="dot_size"
                  min={1}
                  max={50}
                  step={1}
                  value={[dotSize]}
                  onValueChange={(values) => updateParam('dot_size', values[0])}
                  className="flex-1"
                />
                <Input
                  type="number"
                  min={1}
                  max={50}
                  step={1}
                  value={dotSize}
                  onChange={(e) => updateParam('dot_size', parseInt(e.target.value, 10) || 1)}
                  className="w-20 text-sm"
                />
              </div>
              <p className="text-xs text-gray-500">
                控制散点的大小，范围 1-50，默认 8
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dot_jitter" className="text-sm font-medium">
                散点横向抖动 (jitter)
              </Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="dot_jitter"
                  min={0}
                  max={1}
                  step={0.01}
                  value={[dotJitter]}
                  onValueChange={(values) => updateParam('jitter', values[0])}
                  className="flex-1"
                />
                <Input
                  type="number"
                  min={0}
                  max={1}
                  step={0.01}
                  value={dotJitter}
                  onChange={(e) => updateParam('jitter', parseFloat(e.target.value) || 0)}
                  className="w-20 text-sm"
                />
              </div>
              <p className="text-xs text-gray-500">
                控制散点的横向抖动范围（0-1），避免重叠，默认 0.2
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                散点边框颜色 (edgecolor)
              </Label>
              <ColorPicker
                value={dotEdgeColor}
                onChange={(color) => updateParam('dot_edgecolor', color)}
              />
              <p className="text-xs text-gray-500">
                选择散点边框颜色，默认黑色
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dot_alpha" className="text-sm font-medium">
                散点透明度 (alpha)
              </Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="dot_alpha"
                  min={0}
                  max={1}
                  step={0.05}
                  value={[dotAlpha]}
                  onValueChange={(values) => updateParam('dot_alpha', values[0])}
                  className="flex-1"
                />
                <Input
                  type="number"
                  min={0}
                  max={1}
                  step={0.05}
                  value={dotAlpha}
                  onChange={(e) => updateParam('dot_alpha', parseFloat(e.target.value) || 0)}
                  className="w-20 text-sm"
                />
              </div>
              <p className="text-xs text-gray-500">
                控制散点整体透明度（0-1），默认 0.5
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="dot_linewidth" className="text-sm font-medium">
              散点边框宽度 (linewidth)
            </Label>
            <div className="flex items-center gap-4">
              <Slider
                id="dot_linewidth"
                min={0}
                max={5}
                step={0.1}
                value={[dotLineWidth]}
                onValueChange={(values) => updateParam('dot_linewidth', values[0])}
                className="flex-1"
              />
              <Input
                type="number"
                min={0}
                max={5}
                step={0.1}
                value={dotLineWidth}
                onChange={(e) => updateParam('dot_linewidth', parseFloat(e.target.value) || 0)}
                className="w-20 text-sm"
              />
            </div>
            <p className="text-xs text-gray-500">
              控制散点边框线宽，范围 0-5，默认 1.0
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

