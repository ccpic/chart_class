'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import ColorPicker from '@/components/color/ColorPicker';

export interface LabelStyle {
  fontsize?: number;
  color?: string;
  weight?: 'normal' | 'bold' | 'italic';
  bbox?: {
    enabled?: boolean;
    boxstyle?: string;
    facecolor?: string;
    show_border?: boolean;
    edgecolor?: string;
    linewidth?: number;
    alpha?: number;
  };
}

interface LabelStyleEditorProps {
  value: LabelStyle;
  onChange: (value: LabelStyle) => void;
  label?: string;
}

/**
 * 标签样式编辑器组件
 * 提供字体大小、颜色、样式和文本框（bbox）的完整控制
 */
export default function LabelStyleEditor({
  value,
  onChange,
  label,
}: LabelStyleEditorProps) {
  const updateValue = (updates: Partial<LabelStyle>) => {
    onChange({ ...value, ...updates });
  };

  const updateBbox = (updates: Partial<LabelStyle['bbox']>) => {
    const currentBbox = value.bbox || { enabled: false };
    const newBbox = { ...currentBbox, ...updates };
    onChange({
      ...value,
      bbox: newBbox,
    });
  };

  const bboxEnabled = value.bbox?.enabled ?? false;

  return (
    <div className="space-y-3">
      {label && (
        <Label className="text-sm font-medium text-gray-700">{label}</Label>
      )}
      
      {/* 第一行：字体大小、颜色、样式 */}
      <div className="grid grid-cols-3 gap-2 items-end">
        {/* 字体大小 */}
        <div className="space-y-1">
          <Label htmlFor="label-fontsize" className="text-xs text-gray-600">
            字体大小
          </Label>
          <Input
            id="label-fontsize"
            type="number"
            min="4"
            max="24"
            step="1"
            value={value.fontsize || 11}
            onChange={(e) =>
              updateValue({ fontsize: parseInt(e.target.value) || 11 })
            }
            className="h-8 text-sm"
          />
        </div>

        {/* 字体颜色 */}
        <div className="space-y-1">
          <Label className="text-xs text-gray-600">字体颜色</Label>
          <div className="flex items-center gap-2">
            {value.color ? (
              <>
                <ColorPicker
                  value={value.color}
                  onChange={(color) => updateValue({ color })}
                  compact={true}
                  variant="input"
                  showColorValue={false}
                />
                <button
                  type="button"
                  onClick={() => updateValue({ color: undefined })}
                  className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-100"
                  title="恢复为自动颜色（后端根据位置自动计算）"
                >
                  自动
                </button>
              </>
            ) : (
              <>
                <div className="h-8 w-8 rounded border-2 border-dashed border-gray-300 bg-gray-50 flex items-center justify-center cursor-pointer hover:border-gray-400 hover:bg-gray-100 transition-colors" title="当前为自动颜色（后端根据位置自动计算，通常为白色）">
                  <span className="text-xs text-gray-400">自动</span>
                </div>
                <ColorPicker
                  value="#000000"
                  onChange={(color) => updateValue({ color })}
                  compact={true}
                  variant="input"
                  showColorValue={false}
                />
              </>
            )}
          </div>
          {!value.color && (
            <p className="text-xs text-gray-500 mt-1">
              未设置时，后端会根据标签位置自动选择颜色（通常为白色）
            </p>
          )}
        </div>

        {/* 字体样式 */}
        <div className="space-y-1">
          <Label htmlFor="label-weight" className="text-xs text-gray-600">
            字体样式
          </Label>
          <Select
            value={value.weight || 'normal'}
            onValueChange={(val: 'normal' | 'bold' | 'italic') =>
              updateValue({ weight: val })
            }
          >
            <SelectTrigger id="label-weight" className="h-8 text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="normal">常规</SelectItem>
              <SelectItem value="bold">加粗</SelectItem>
              <SelectItem value="italic">斜体</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 第二行：文本框（bbox）控制 */}
      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="label-bbox-enabled"
            checked={bboxEnabled}
            onCheckedChange={(checked) => {
              const newEnabled = !!checked;
              if (newEnabled) {
                // 启用时，如果 bbox 不存在，创建默认配置
                const currentBbox = value.bbox || {};
                updateBbox({ 
                  enabled: true,
                  boxstyle: currentBbox.boxstyle || 'round',
                  facecolor: currentBbox.facecolor || '#FFFFFF',
                  show_border: currentBbox.show_border ?? true,
                  edgecolor: currentBbox.edgecolor || '#000000',
                  linewidth: currentBbox.linewidth ?? 1,
                  alpha: currentBbox.alpha ?? 0.7,
                });
              } else {
                // 禁用时，只设置 enabled 为 false
                updateBbox({ enabled: false });
              }
            }}
          />
          <Label
            htmlFor="label-bbox-enabled"
            className="text-xs cursor-pointer text-gray-700"
          >
            启用文本框
          </Label>
        </div>

        {/* 文本框详细设置（仅在启用时显示，紧凑布局） */}
        {bboxEnabled && (
          <div className="pl-6 space-y-2 border-l-2 border-gray-200">
            {/* 第一行：形状、背景颜色、背景透明度 */}
            <div className="grid grid-cols-3 gap-2">
              <div className="space-y-1">
                <Label htmlFor="label-bbox-boxstyle" className="text-xs text-gray-600">
                  形状
                </Label>
                <Select
                  value={value.bbox?.boxstyle || 'round'}
                  onValueChange={(val) => updateBbox({ boxstyle: val })}
                >
                  <SelectTrigger id="label-bbox-boxstyle" className="h-8 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="round">圆角</SelectItem>
                    <SelectItem value="square">方形</SelectItem>
                    <SelectItem value="round,pad=0.5">圆角（内边距）</SelectItem>
                    <SelectItem value="square,pad=0.5">方形（内边距）</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label className="text-xs text-gray-600">背景色</Label>
                <ColorPicker
                  value={value.bbox?.facecolor || '#FFFFFF'}
                  onChange={(color) => updateBbox({ facecolor: color })}
                  compact={true}
                  variant="input"
                  showColorValue={false}
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="label-bbox-alpha" className="text-xs text-gray-600">
                  背景透明度
                </Label>
                <Input
                  id="label-bbox-alpha"
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={value.bbox?.alpha ?? 0.7}
                  onChange={(e) =>
                    updateBbox({ alpha: parseFloat(e.target.value) || 0.7 })
                  }
                  className="h-8 text-sm"
                />
              </div>
            </div>

            {/* 显示边框 checkbox */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="label-bbox-show-border"
                checked={value.bbox?.show_border ?? true}
                onCheckedChange={(checked) =>
                  updateBbox({ show_border: !!checked })
                }
              />
              <Label
                htmlFor="label-bbox-show-border"
                className="text-xs cursor-pointer text-gray-700"
              >
                显示边框
              </Label>
            </div>

            {/* 边框设置（仅在显示边框时显示） */}
            {value.bbox?.show_border !== false && (
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <Label className="text-xs text-gray-600">边框色</Label>
                  <ColorPicker
                    value={value.bbox?.edgecolor || '#000000'}
                    onChange={(color) => updateBbox({ edgecolor: color })}
                    compact={true}
                    variant="input"
                    showColorValue={false}
                  />
                </div>

                <div className="space-y-1">
                  <Label htmlFor="label-bbox-linewidth" className="text-xs text-gray-600">
                    边框粗细
                  </Label>
                  <Input
                    id="label-bbox-linewidth"
                    type="number"
                    min="0"
                    max="5"
                    step="0.1"
                    value={value.bbox?.linewidth || 1}
                    onChange={(e) =>
                      updateBbox({ linewidth: parseFloat(e.target.value) || 1 })
                    }
                    className="h-8 text-sm"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

