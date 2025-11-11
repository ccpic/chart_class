import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { PlotStyle } from '@/types/plotStyle';

interface AxisSectionProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
}

export function AxisSection({ style, onChange }: AxisSectionProps) {
  const xMin = style.xlim?.[0] ?? '';
  const xMax = style.xlim?.[1] ?? '';
  const yMin = style.ylim?.[0] ?? '';
  const yMax = style.ylim?.[1] ?? '';

  const updateXLim = (index: 0 | 1, value: string) => {
    const newLim: [number | null, number | null] = [...(style.xlim || [null, null])];
    newLim[index] = value === '' ? null : parseFloat(value);
    onChange({ xlim: newLim });
  };

  const updateYLim = (index: 0 | 1, value: string) => {
    const newLim: [number | null, number | null] = [...(style.ylim || [null, null])];
    newLim[index] = value === '' ? null : parseFloat(value);
    onChange({ ylim: newLim });
  };

  return (
    <div className="space-y-4">
      {/* X 轴设置 */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-800">X 轴</h4>

        {/* X 轴标题和字体 - 4:1 布局 */}
        <div className="space-y-1.5">
          <div className="grid grid-cols-5 gap-2 items-end">
            <div className="col-span-4 space-y-1.5">
              <Label htmlFor="xlabel" className="text-xs font-medium text-gray-700">
                轴标题
              </Label>
              <Input
                id="xlabel"
                value={style.xlabel || ''}
                onChange={(e) => onChange({ xlabel: e.target.value })}
                placeholder="X 轴标题"
                className="h-8 text-sm"
              />
            </div>
            <div className="col-span-1 space-y-1.5">
              <Label htmlFor="xlabel-fontsize" className="text-xs font-medium text-gray-700">
                字号
              </Label>
              <Input
                id="xlabel-fontsize"
                type="number"
                value={style.xlabel_fontsize || 14}
                onChange={(e) => onChange({ xlabel_fontsize: Number(e.target.value) })}
                min={8}
                max={24}
                className="h-8 text-sm"
              />
            </div>
          </div>
        </div>

        {/* X 轴范围 */}
        <div className="space-y-1.5">
          <Label className="text-xs font-medium text-gray-700">轴范围</Label>
          <div className="grid grid-cols-2 gap-2">
            <Input
              type="number"
              value={xMin}
              onChange={(e) => updateXLim(0, e.target.value)}
              placeholder="最小值"
              className="h-8 text-sm"
            />
            <Input
              type="number"
              value={xMax}
              onChange={(e) => updateXLim(1, e.target.value)}
              placeholder="最大值"
              className="h-8 text-sm"
            />
          </div>
          <p className="text-xs text-gray-500">留空为自动</p>
        </div>
      </div>

      {/* Y 轴设置 */}
      <div className="space-y-3 pt-3 border-t">
        <h4 className="text-sm font-semibold text-gray-800">Y 轴</h4>

        {/* Y 轴标题和字体 - 4:1 布局 */}
        <div className="space-y-1.5">
          <div className="grid grid-cols-5 gap-2 items-end">
            <div className="col-span-4 space-y-1.5">
              <Label htmlFor="ylabel" className="text-xs font-medium text-gray-700">
                轴标题
              </Label>
              <Input
                id="ylabel"
                value={style.ylabel || ''}
                onChange={(e) => onChange({ ylabel: e.target.value })}
                placeholder="Y 轴标题"
                className="h-8 text-sm"
              />
            </div>
            <div className="col-span-1 space-y-1.5">
              <Label htmlFor="ylabel-fontsize" className="text-xs font-medium text-gray-700">
                字号
              </Label>
              <Input
                id="ylabel-fontsize"
                type="number"
                value={style.ylabel_fontsize || 14}
                onChange={(e) => onChange({ ylabel_fontsize: Number(e.target.value) })}
                min={8}
                max={24}
                className="h-8 text-sm"
              />
            </div>
          </div>
        </div>

        {/* Y 轴范围 */}
        <div className="space-y-1.5">
          <Label className="text-xs font-medium text-gray-700">轴范围</Label>
          <div className="grid grid-cols-2 gap-2">
            <Input
              type="number"
              value={yMin}
              onChange={(e) => updateYLim(0, e.target.value)}
              placeholder="最小值"
              className="h-8 text-sm"
            />
            <Input
              type="number"
              value={yMax}
              onChange={(e) => updateYLim(1, e.target.value)}
              placeholder="最大值"
              className="h-8 text-sm"
            />
          </div>
          <p className="text-xs text-gray-500">留空为自动</p>
        </div>
      </div>

      {/* 边框设置 */}
      <div className="pt-3 border-t">
        <div className="flex items-center gap-2">
          <Checkbox
            id="hide-spines"
            checked={style.hide_top_right_spines || false}
            onCheckedChange={(checked) =>
              onChange({ hide_top_right_spines: checked as boolean })
            }
          />
          <Label
            htmlFor="hide-spines"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            隐藏上边框和右边框
          </Label>
        </div>
        <p className="text-xs text-gray-500 ml-6 mt-1">
          常用于学术图表，保持左下双轴
        </p>
      </div>
    </div>
  );
}
