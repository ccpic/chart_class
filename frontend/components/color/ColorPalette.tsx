'use client';

import { useState } from 'react';
import ColorPicker from './ColorPicker';
import { Button } from '@/components/ui/button';
import { Plus, Trash2 } from 'lucide-react';

interface ColorPaletteProps {
  /**
   * 颜色值列表（HEX 或命名颜色）
   */
  colors: string[];
  /**
   * 颜色变化回调
   */
  onChange: (colors: string[]) => void;
  /**
   * 是否允许添加颜色
   */
  allowAdd?: boolean;
  /**
   * 是否允许删除颜色
   */
  allowRemove?: boolean;
  /**
   * 是否禁用
   */
  disabled?: boolean;
  /**
   * 颜色方块大小
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * 默认新颜色值
   */
  defaultColor?: string;
}

/**
 * 颜色调色板组件
 * 使用 ColorPicker 的最小模式形成一排颜色选择器
 */
export default function ColorPalette({
  colors,
  onChange,
  allowAdd = true,
  allowRemove = true,
  disabled = false,
  size = 'md',
  defaultColor = '#808080',
}: ColorPaletteProps) {
  const handleColorChange = (index: number, newColor: string) => {
    const newColors = [...colors];
    newColors[index] = newColor;
    onChange(newColors);
  };

  const handleAddColor = () => {
    onChange([...colors, defaultColor]);
  };

  const handleRemoveColor = (index: number) => {
    const newColors = colors.filter((_, i) => i !== index);
    onChange(newColors);
  };

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {colors.map((color, index) => (
        <div key={index} className="relative group">
          <ColorPicker
            value={color}
            onChange={(newColor) => handleColorChange(index, newColor)}
            compact={true}
            size={size}
            disabled={disabled}
          />
          {allowRemove && !disabled && (
            <button
              onClick={() => handleRemoveColor(index)}
              className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-destructive text-destructive-foreground opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center shadow-md hover:bg-destructive/90 z-10"
              title="删除颜色"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          )}
        </div>
      ))}
      {allowAdd && !disabled && (
        <Button
          variant="outline"
          size="icon"
          onClick={handleAddColor}
          className={`${size === 'sm' ? 'w-6 h-6' : size === 'md' ? 'w-8 h-8' : 'w-10 h-10'} rounded border-2 border-dashed`}
          title="添加颜色"
        >
          <Plus className={`${size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5'}`} />
        </Button>
      )}
    </div>
  );
}

