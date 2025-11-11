import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { PlotStyle } from '@/types/plotStyle';

interface LegendSectionProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
}

// 常用图例位置选项
const LEGEND_LOCATIONS = [
  { value: 'best', label: '最佳位置（自动）' },
  { value: 'upper right', label: '右上' },
  { value: 'upper left', label: '左上' },
  { value: 'lower left', label: '左下' },
  { value: 'lower right', label: '右下' },
  { value: 'right', label: '右侧' },
  { value: 'center left', label: '中左（默认）' },
  { value: 'center right', label: '中右' },
  { value: 'lower center', label: '下中' },
  { value: 'upper center', label: '上中' },
  { value: 'center', label: '正中' },
];

export function LegendSection({ style, onChange }: LegendSectionProps) {
  const bboxX = style.legend_bbox_to_anchor?.[0] ?? 1;
  const bboxY = style.legend_bbox_to_anchor?.[1] ?? 0.5;

  const updateBbox = (index: 0 | 1, value: string) => {
    const newBbox: [number, number] = [...(style.legend_bbox_to_anchor || [1, 0.5])];
    newBbox[index] = value === '' ? (index === 0 ? 1 : 0.5) : parseFloat(value);
    onChange({ legend_bbox_to_anchor: newBbox });
  };

  return (
    <div className="space-y-4">
      {/* 显示图例开关 */}
      <div className="flex items-center gap-2">
        <Checkbox
          id="show-legend"
          checked={style.show_legend !== false} // 默认为 true
          onCheckedChange={(checked: boolean) =>
            onChange({ show_legend: checked })
          }
        />
        <Label
          htmlFor="show-legend"
          className="text-sm font-medium text-gray-700 cursor-pointer"
        >
          显示图例
        </Label>
      </div>

      {style.show_legend !== false && (
        <div className="space-y-3 ml-0">
          {/* 图例位置和列数 - 4:1 布局 */}
          <div className="space-y-1.5">
            <div className="grid grid-cols-5 gap-2 items-end">
              <div className="col-span-4 space-y-1.5">
                <Label htmlFor="legend-loc" className="text-xs font-medium text-gray-700">
                  图例位置
                </Label>
                <Select
                  value={style.legend_loc || 'center left'}
                  onValueChange={(value) => onChange({ legend_loc: value })}
                >
                  <SelectTrigger id="legend-loc" className="h-8 text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {LEGEND_LOCATIONS.map((loc) => (
                      <SelectItem key={loc.value} value={loc.value}>
                        {loc.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="col-span-1 space-y-1.5">
                <Label htmlFor="legend-ncol" className="text-xs font-medium text-gray-700">
                  列数
                </Label>
                <Input
                  id="legend-ncol"
                  type="number"
                  value={style.legend_ncol || 1}
                  onChange={(e) =>
                    onChange({ legend_ncol: Number(e.target.value) })
                  }
                  min={1}
                  max={10}
                  className="h-8 text-sm"
                />
              </div>
            </div>
          </div>

          {/* 边界框位置（高级）*/}
          <div className="space-y-1.5 pt-2 border-t">
            <Label className="text-xs font-medium text-gray-700">
              边界框位置（高级）
            </Label>
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1">
                <Label htmlFor="bbox-x" className="text-xs text-gray-600">
                  X 坐标
                </Label>
                <Input
                  id="bbox-x"
                  type="number"
                  value={bboxX}
                  onChange={(e) => updateBbox(0, e.target.value)}
                  step={0.1}
                  className="h-8 text-sm"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="bbox-y" className="text-xs text-gray-600">
                  Y 坐标
                </Label>
                <Input
                  id="bbox-y"
                  type="number"
                  value={bboxY}
                  onChange={(e) => updateBbox(1, e.target.value)}
                  step={0.1}
                  className="h-8 text-sm"
                />
              </div>
            </div>
            <p className="text-xs text-gray-500">
              相对于图表的归一化坐标（0-1）
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
