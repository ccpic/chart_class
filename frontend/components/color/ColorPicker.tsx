'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Check, X } from 'lucide-react';

// Matplotlib 基础命名颜色
const MATPLOTLIB_COLORS = {
  '基础颜色': {
    'blue': '#0000FF',
    'green': '#008000',
    'red': '#FF0000',
    'cyan': '#00FFFF',
    'magenta': '#FF00FF',
    'yellow': '#FFFF00',
    'black': '#000000',
    'white': '#FFFFFF',
  },
  'Tableau 调色板': {
    'tab:blue': '#1f77b4',
    'tab:orange': '#ff7f0e',
    'tab:green': '#2ca02c',
    'tab:red': '#d62728',
    'tab:purple': '#9467bd',
    'tab:brown': '#8c564b',
    'tab:pink': '#e377c2',
    'tab:gray': '#7f7f7f',
    'tab:olive': '#bcbd22',
    'tab:cyan': '#17becf',
  },
  'CSS 颜色': {
    'aliceblue': '#F0F8FF',
    'antiquewhite': '#FAEBD7',
    'aqua': '#00FFFF',
    'aquamarine': '#7FFFD4',
    'azure': '#F0FFFF',
    'beige': '#F5F5DC',
    'bisque': '#FFE4C4',
    'blanchedalmond': '#FFEBCD',
    'blueviolet': '#8A2BE2',
    'brown': '#A52A2A',
    'burlywood': '#DEB887',
    'cadetblue': '#5F9EA0',
    'chartreuse': '#7FFF00',
    'chocolate': '#D2691E',
    'coral': '#FF7F50',
    'cornflowerblue': '#6495ED',
    'cornsilk': '#FFF8DC',
    'crimson': '#DC143C',
    'darkblue': '#00008B',
    'darkcyan': '#008B8B',
    'darkgoldenrod': '#B8860B',
    'darkgray': '#A9A9A9',
    'darkgreen': '#006400',
    'darkkhaki': '#BDB76B',
    'darkmagenta': '#8B008B',
    'darkolivegreen': '#556B2F',
    'darkorange': '#FF8C00',
    'darkorchid': '#9932CC',
    'darkred': '#8B0000',
    'darksalmon': '#E9967A',
    'darkseagreen': '#8FBC8F',
    'darkslateblue': '#483D8B',
    'darkslategray': '#2F4F4F',
    'darkturquoise': '#00CED1',
    'darkviolet': '#9400D3',
    'deeppink': '#FF1493',
    'deepskyblue': '#00BFFF',
    'dimgray': '#696969',
    'dodgerblue': '#1E90FF',
    'firebrick': '#B22222',
    'floralwhite': '#FFFAF0',
    'forestgreen': '#228B22',
    'fuchsia': '#FF00FF',
    'gainsboro': '#DCDCDC',
    'ghostwhite': '#F8F8FF',
    'gold': '#FFD700',
    'goldenrod': '#DAA520',
    'gray': '#808080',
    'greenyellow': '#ADFF2F',
    'honeydew': '#F0FFF0',
    'hotpink': '#FF69B4',
    'indianred': '#CD5C5C',
    'indigo': '#4B0082',
    'ivory': '#FFFFF0',
    'khaki': '#F0E68C',
    'lavender': '#E6E6FA',
    'lavenderblush': '#FFF0F5',
    'lawngreen': '#7CFC00',
    'lemonchiffon': '#FFFACD',
    'lightblue': '#ADD8E6',
    'lightcoral': '#F08080',
    'lightcyan': '#E0FFFF',
    'lightgoldenrodyellow': '#FAFAD2',
    'lightgray': '#D3D3D3',
    'lightgreen': '#90EE90',
    'lightpink': '#FFB6C1',
    'lightsalmon': '#FFA07A',
    'lightseagreen': '#20B2AA',
    'lightskyblue': '#87CEFA',
    'lightslategray': '#778899',
    'lightsteelblue': '#B0C4DE',
    'lightyellow': '#FFFFE0',
    'lime': '#00FF00',
    'limegreen': '#32CD32',
    'linen': '#FAF0E6',
    'maroon': '#800000',
    'mediumaquamarine': '#66CDAA',
    'mediumblue': '#0000CD',
    'mediumorchid': '#BA55D3',
    'mediumpurple': '#9370DB',
    'mediumseagreen': '#3CB371',
    'mediumslateblue': '#7B68EE',
    'mediumspringgreen': '#00FA9A',
    'mediumturquoise': '#48D1CC',
    'mediumvioletred': '#C71585',
    'midnightblue': '#191970',
    'mintcream': '#F5FFFA',
    'mistyrose': '#FFE4E1',
    'moccasin': '#FFE4B5',
    'navajowhite': '#FFDEAD',
    'navy': '#000080',
    'oldlace': '#FDF5E6',
    'olive': '#808000',
    'olivedrab': '#6B8E23',
    'orange': '#FFA500',
    'orangered': '#FF4500',
    'orchid': '#DA70D6',
    'palegoldenrod': '#EEE8AA',
    'palegreen': '#98FB98',
    'paleturquoise': '#AFEEEE',
    'palevioletred': '#DB7093',
    'papayawhip': '#FFEFD5',
    'peachpuff': '#FFDAB9',
    'peru': '#CD853F',
    'pink': '#FFC0CB',
    'plum': '#DDA0DD',
    'powderblue': '#B0E0E6',
    'purple': '#800080',
    'rebeccapurple': '#663399',
    'rosybrown': '#BC8F8F',
    'royalblue': '#4169E1',
    'saddlebrown': '#8B4513',
    'salmon': '#FA8072',
    'sandybrown': '#F4A460',
    'seagreen': '#2E8B57',
    'seashell': '#FFF5EE',
    'sienna': '#A0522D',
    'silver': '#C0C0C0',
    'skyblue': '#87CEEB',
    'slateblue': '#6A5ACD',
    'slategray': '#708090',
    'snow': '#FFFAFA',
    'springgreen': '#00FF7F',
    'steelblue': '#4682B4',
    'tan': '#D2B48C',
    'teal': '#008080',
    'thistle': '#D8BFD8',
    'tomato': '#FF6347',
    'turquoise': '#40E0D0',
    'violet': '#EE82EE',
    'wheat': '#F5DEB3',
    'whitesmoke': '#F5F5F5',
    'yellowgreen': '#9ACD32',
  },
};

// 创建颜色名称到 HEX 的扁平映射
const COLOR_NAME_MAP: Record<string, string> = Object.values(MATPLOTLIB_COLORS).reduce(
  (acc, colors) => ({ ...acc, ...colors }),
  {}
);

// 创建 HEX 到颜色名称的反向映射（用于识别命名颜色）
const HEX_TO_NAME_MAP: Record<string, string> = Object.entries(COLOR_NAME_MAP).reduce(
  (acc, [name, hex]) => ({ ...acc, [hex.toUpperCase()]: name }),
  {}
);

// 根据颜色名称或 HEX 值获取 HEX
const getHexFromColorNameOrHex = (input: string): string | null => {
  const trimmed = input.trim().toLowerCase();
  
  // 如果已经是有效的 HEX 格式，直接返回
  if (/^#[0-9A-F]{6}$/i.test(trimmed)) {
    return trimmed.toUpperCase();
  }
  
  // 查找命名颜色
  const hex = COLOR_NAME_MAP[trimmed];
  return hex ? hex.toUpperCase() : null;
};

// 根据 HEX 值查找对应的命名颜色
const getNamedColorFromHex = (hex: string): string | undefined => {
  return HEX_TO_NAME_MAP[hex.toUpperCase()];
};

/**
 * 将 HEX 颜色转换为 HSL
 * 用于颜色相似度排序
 */
const hexToHSL = (hex: string): { h: number; s: number; l: number } => {
  // 移除 # 并转换为 RGB
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const diff = max - min;
  
  let h = 0;
  let s = 0;
  const l = (max + min) / 2;

  if (diff !== 0) {
    s = l > 0.5 ? diff / (2 - max - min) : diff / (max + min);

    switch (max) {
      case r:
        h = ((g - b) / diff + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / diff + 2) / 6;
        break;
      case b:
        h = ((r - g) / diff + 4) / 6;
        break;
    }
  }

  return {
    h: h * 360,      // 色相 (0-360)
    s: s * 100,      // 饱和度 (0-100)
    l: l * 100,      // 亮度 (0-100)
  };
};

/**
 * 智能颜色排序算法
 * 按照色相 → 饱和度 → 亮度的优先级排序
 * 使颜色按照色轮顺序排列，相似颜色聚集在一起
 */
const sortColorsBySimilarity = (colors: [string, string][]): [string, string][] => {
  return colors.sort((a, b) => {
    const hslA = hexToHSL(a[1]);
    const hslB = hexToHSL(b[1]);

    // 优先级1: 按色相排序（红→橙→黄→绿→青→蓝→紫）
    if (Math.abs(hslA.h - hslB.h) > 1) {
      return hslA.h - hslB.h;
    }

    // 优先级2: 色相相近时，按饱和度排序（灰色在前，鲜艳在后）
    if (Math.abs(hslA.s - hslB.s) > 1) {
      return hslA.s - hslB.s;
    }

    // 优先级3: 色相和饱和度都相近时，按亮度排序（暗→亮）
    return hslA.l - hslB.l;
  });
};

interface ColorPickerProps {
  value: string;
  namedColor?: string; // 外部传入的命名颜色（如果有）
  onChange: (color: string, namedColor?: string) => void; // 返回 HEX 值和可选的命名颜色
  label?: string;
  disabled?: boolean;
  showColorValue?: boolean; // 是否显示颜色值文本，默认为 true
}

/**
 * 高级颜色选择器组件
 * 
 * 功能：
 * - 调色板选择
 * - RGB/HEX 输入
 * - Matplotlib 命名颜色选择
 * - 实时预览
 */
export default function ColorPicker({
  value,
  namedColor: externalNamedColor,
  onChange,
  label,
  disabled = false,
  showColorValue = true,
}: ColorPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [currentColor, setCurrentColor] = useState(value);
  const [currentNamedColor, setCurrentNamedColor] = useState<string | undefined>(externalNamedColor); // 追踪命名颜色
  const [hexInput, setHexInput] = useState(value);
  const [rgbInput, setRgbInput] = useState({ r: 0, g: 0, b: 0 });
  const [searchTerm, setSearchTerm] = useState('');

  // 同步外部值变化
  useEffect(() => {
    setCurrentColor(value);
    setHexInput(value);
    updateRgbFromHex(value);
    // 同步外部命名颜色，如果没有则尝试从HEX值查找
    if (externalNamedColor) {
      setCurrentNamedColor(externalNamedColor);
    } else {
      const named = getNamedColorFromHex(value);
      setCurrentNamedColor(named);
    }
  }, [value, externalNamedColor]);

  // HEX 转 RGB
  const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16),
        }
      : null;
  };

  // RGB 转 HEX
  const rgbToHex = (r: number, g: number, b: number): string => {
    return (
      '#' +
      [r, g, b]
        .map((x) => {
          const hex = Math.max(0, Math.min(255, x)).toString(16);
          return hex.length === 1 ? '0' + hex : hex;
        })
        .join('')
        .toUpperCase()
    );
  };

  // 更新 RGB 值从 HEX
  const updateRgbFromHex = (hex: string) => {
    const rgb = hexToRgb(hex);
    if (rgb) {
      setRgbInput(rgb);
    }
  };

  // 应用颜色并通知外部
  const applyColor = (color: string, namedColor?: string) => {
    setCurrentColor(color);
    setHexInput(color);
    updateRgbFromHex(color);
    setCurrentNamedColor(namedColor);
    onChange(color, namedColor);
  };

  // 处理颜色选择
  const handleColorSelect = (color: string, namedColor?: string) => {
    applyColor(color, namedColor);
  };

  // 处理 HEX 输入（支持颜色名称）
  const handleHexChange = (input: string) => {
    const trimmedInput = input.trim().toLowerCase();
    
    // 检查是否为命名颜色
    if (COLOR_NAME_MAP[trimmedInput]) {
      const hex = COLOR_NAME_MAP[trimmedInput].toUpperCase();
      applyColor(hex, trimmedInput);
      return;
    }
    
    // 尝试将输入转换为 HEX
    const hex = getHexFromColorNameOrHex(input);
    if (hex) {
      const named = getNamedColorFromHex(hex);
      applyColor(hex, named);
    } else {
      // 如果不是有效格式，仍然更新输入框（允许用户输入）
      setHexInput(input);
    }
  };

  // 处理 RGB 输入
  const handleRgbChange = (channel: 'r' | 'g' | 'b', value: string) => {
    const numValue = parseInt(value) || 0;
    const newRgb = { ...rgbInput, [channel]: numValue };
    setRgbInput(newRgb);
    const hex = rgbToHex(newRgb.r, newRgb.g, newRgb.b);
    applyColor(hex, undefined);
  };

  // 弹窗关闭时应用颜色
  const handleOpenChange = (open: boolean) => {
    if (!open && currentColor !== value) {
      // 关闭时应用颜色，传递命名颜色（如果有）
      onChange(currentColor, currentNamedColor);
    } else if (!open) {
      // 关闭但没有改变，重置为原值
      setCurrentColor(value);
      setHexInput(value);
      updateRgbFromHex(value);
      setCurrentNamedColor(undefined);
    }
    setIsOpen(open);
  };

  // 过滤并智能排序命名颜色（按色相→饱和度→亮度排序）
  const filteredAndSortedColors = (() => {
    // 将所有颜色扁平化为 [name, hex] 数组
    const allColors = Object.values(MATPLOTLIB_COLORS).flatMap(colors =>
      Object.entries(colors)
    );
    
    // 过滤
    const filtered = allColors.filter(([name]) =>
      name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    // 按颜色相似度智能排序（HSL 色彩空间）
    return sortColorsBySimilarity(filtered);
  })();

  return (
    <div className="space-y-2">
      {label && <Label>{label}</Label>}
      <Popover open={isOpen} onOpenChange={handleOpenChange}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            disabled={disabled}
            className="w-full justify-start gap-2 h-10"
          >
            <div
              className="w-6 h-6 rounded border border-gray-300"
              style={{ backgroundColor: currentColor }}
            />
            {showColorValue && (
              <span className="flex-1 text-left text-sm">
                {currentNamedColor || currentColor}
              </span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-96 p-0" align="start">
          <div className="p-4 space-y-4 relative">
            {/* 关闭按钮 */}
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-2 h-6 w-6 rounded-full"
              onClick={() => handleOpenChange(false)}
            >
              <X className="h-4 w-4" />
            </Button>

            {/* 当前颜色预览 */}
            <div className="flex items-center gap-3">
              <div
                className="w-20 h-20 rounded border-2 border-gray-300 shadow-sm"
                style={{ backgroundColor: currentColor }}
              />
              <div className="flex-1">
                <div className="text-sm font-medium">当前颜色</div>
                <div className="text-xs text-muted-foreground font-mono">
                  {currentColor}
                </div>
                <div className="text-xs text-muted-foreground">
                  RGB({rgbInput.r}, {rgbInput.g}, {rgbInput.b})
                </div>
              </div>
            </div>

            {/* 标签页 */}
            <Tabs defaultValue="named" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="picker">调色板</TabsTrigger>
                <TabsTrigger value="input">输入</TabsTrigger>
                <TabsTrigger value="named">命名颜色</TabsTrigger>
              </TabsList>

              {/* 调色板 */}
              <TabsContent value="picker" className="space-y-3">
                <div className="space-y-2">
                  <Label>浏览器颜色选择器</Label>
                  <Input
                    type="color"
                    value={currentColor}
                    onChange={(e) => {
                      const newColor = e.target.value.toUpperCase();
                      const namedColor = getNamedColorFromHex(newColor);
                      handleColorSelect(newColor, namedColor);
                    }}
                    className="w-full h-40 cursor-pointer"
                  />
                </div>
              </TabsContent>

              {/* 输入 */}
              <TabsContent value="input" className="space-y-3">
                {/* HEX 输入 */}
                <div className="space-y-2">
                  <Label htmlFor="hex">HEX / 颜色名称</Label>
                  <Input
                    id="hex"
                    value={hexInput}
                    onChange={(e) => handleHexChange(e.target.value)}
                    placeholder="#000000 或 red, blue, tab:blue..."
                    className="font-mono"
                  />
                  <p className="text-xs text-muted-foreground">
                    支持 HEX 值或 matplotlib 颜色名称
                  </p>
                </div>

                {/* RGB 输入 */}
                <div className="space-y-2">
                  <Label>RGB</Label>
                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <Label htmlFor="r" className="text-xs">
                        R
                      </Label>
                      <Input
                        id="r"
                        type="number"
                        min="0"
                        max="255"
                        value={rgbInput.r}
                        onChange={(e) => handleRgbChange('r', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="g" className="text-xs">
                        G
                      </Label>
                      <Input
                        id="g"
                        type="number"
                        min="0"
                        max="255"
                        value={rgbInput.g}
                        onChange={(e) => handleRgbChange('g', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="b" className="text-xs">
                        B
                      </Label>
                      <Input
                        id="b"
                        type="number"
                        min="0"
                        max="255"
                        value={rgbInput.b}
                        onChange={(e) => handleRgbChange('b', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </TabsContent>

              {/* 命名颜色 */}
              <TabsContent value="named" className="space-y-3">
                {/* 搜索 */}
                <Input
                  placeholder="搜索颜色名称..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />

                {/* 颜色列表 - 固定容器，无横向滚动 */}
                <div 
                  className="h-64 w-full overflow-y-auto overflow-x-hidden rounded-md border p-2"
                  style={{ overscrollBehavior: 'contain' }}
                  onWheel={(e) => {
                    e.stopPropagation();
                  }}
                >
                  {/* 使用固定列数的网格，避免横向滚动 */}
                  <div className="grid grid-cols-16 gap-0.5">
                    {filteredAndSortedColors.map(([name, hex], index) => {
                      // 计算 tooltip 显示位置
                      const colsPerRow = 16;
                      const row = Math.floor(index / colsPerRow);
                      const col = index % colsPerRow;
                      
                      // 根据位置智能调整 tooltip 方向
                      let tooltipPosition = '';
                      let arrowPosition = '';
                      
                      // 前3行：tooltip 显示在下方
                      if (row < 3) {
                        tooltipPosition = 'top-full mt-1';
                        arrowPosition = 'bottom-full border-b-gray-900';
                      } 
                      // 其他行：tooltip 显示在上方
                      else {
                        tooltipPosition = 'bottom-full mb-1';
                        arrowPosition = 'top-full border-t-gray-900';
                      }
                      
                      // 左右对齐调整
                      let horizontalAlign = 'left-1/2 -translate-x-1/2'; // 默认居中
                      if (col < 3) {
                        // 最左侧：tooltip 左对齐
                        horizontalAlign = 'left-0';
                      } else if (col >= colsPerRow - 3) {
                        // 最右侧：tooltip 右对齐
                        horizontalAlign = 'right-0';
                      }
                      
                      return (
                        <button
                          key={name}
                          onClick={() => handleColorSelect(hex, name)}
                          className="relative group w-5 h-5 rounded-sm border border-gray-200 hover:scale-150 hover:z-50 hover:shadow-lg transition-all"
                          style={{ backgroundColor: hex }}
                        >
                          {currentColor && currentColor.toUpperCase() === hex.toUpperCase() && (
                            <div className="absolute inset-0 flex items-center justify-center">
                              <Check className="w-3 h-3 text-white drop-shadow-lg" />
                            </div>
                          )}
                          {/* Hover 提示 - 智能定位 */}
                          <div 
                            className={`absolute ${tooltipPosition} ${horizontalAlign} hidden group-hover:block bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50 pointer-events-none shadow-xl`}
                          >
                            {name} - {hex}
                            {/* 小三角箭头 */}
                            <div 
                              className={`absolute ${col < 3 ? 'left-2' : col >= colsPerRow - 3 ? 'right-2' : 'left-1/2 -translate-x-1/2'} border-4 border-transparent ${arrowPosition}`}
                            ></div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}
