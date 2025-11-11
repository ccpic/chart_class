import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import type { PlotStyle } from '@/types/plotStyle';

interface TicksSectionProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
}

export function TicksSection({ style, onChange }: TicksSectionProps) {
  return (
    <div className="space-y-4">
      {/* X 轴刻度 */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-800">X 轴刻度</h4>

        {/* 旋转角度和字体大小 - 4:1 布局 */}
        <div className="space-y-1.5">
          <div className="grid grid-cols-5 gap-2 items-end">
            <div className="col-span-4 space-y-1.5">
              <Label htmlFor="xtick-rotation" className="text-xs font-medium text-gray-700">
                旋转角度: {style.xticklabel_rotation || 0}°
              </Label>
              <Slider
                id="xtick-rotation"
                value={[style.xticklabel_rotation || 0]}
                onValueChange={([value]) => onChange({ xticklabel_rotation: value })}
                min={0}
                max={90}
                step={15}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>0°</span>
                <span>45°</span>
                <span>90°</span>
              </div>
            </div>
            <div className="col-span-1 space-y-1.5">
              <Label htmlFor="xtick-fontsize" className="text-xs font-medium text-gray-700">
                字号
              </Label>
              <Input
                id="xtick-fontsize"
                type="number"
                value={style.xticklabel_fontsize || 14}
                onChange={(e) =>
                  onChange({ xticklabel_fontsize: Number(e.target.value) })
                }
                min={6}
                max={20}
                className="h-8 text-sm"
              />
            </div>
          </div>
        </div>

        {/* 刻度间隔 */}
        <div className="space-y-1.5">
          <Label htmlFor="xtick-interval" className="text-xs font-medium text-gray-700">
            刻度间隔
          </Label>
          <Input
            id="xtick-interval"
            type="number"
            value={style.xticks_interval ?? ''}
            onChange={(e) =>
              onChange({
                xticks_interval: e.target.value === '' ? null : Number(e.target.value),
              })
            }
            placeholder="自动"
            className="h-8 text-sm"
          />
        </div>

        {/* 隐藏刻度 */}
        <div className="flex items-center gap-2">
          <Checkbox
            id="remove-xticks"
            checked={style.remove_xticks || false}
            onCheckedChange={(checked: boolean) =>
              onChange({ remove_xticks: checked })
            }
          />
          <Label
            htmlFor="remove-xticks"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            隐藏 X 轴刻度
          </Label>
        </div>
      </div>

      {/* Y 轴刻度 */}
      <div className="space-y-3 pt-3 border-t">
        <h4 className="text-sm font-semibold text-gray-800">Y 轴刻度</h4>

        {/* 旋转角度和字体大小 - 4:1 布局 */}
        <div className="space-y-1.5">
          <div className="grid grid-cols-5 gap-2 items-end">
            <div className="col-span-4 space-y-1.5">
              <Label htmlFor="ytick-rotation" className="text-xs font-medium text-gray-700">
                旋转角度: {style.yticklabel_rotation || 0}°
              </Label>
              <Slider
                id="ytick-rotation"
                value={[style.yticklabel_rotation || 0]}
                onValueChange={([value]) => onChange({ yticklabel_rotation: value })}
                min={0}
                max={90}
                step={15}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>0°</span>
                <span>45°</span>
                <span>90°</span>
              </div>
            </div>
            <div className="col-span-1 space-y-1.5">
              <Label htmlFor="ytick-fontsize" className="text-xs font-medium text-gray-700">
                字号
              </Label>
              <Input
                id="ytick-fontsize"
                type="number"
                value={style.yticklabel_fontsize || 14}
                onChange={(e) =>
                  onChange({ yticklabel_fontsize: Number(e.target.value) })
                }
                min={6}
                max={20}
                className="h-8 text-sm"
              />
            </div>
          </div>
        </div>

        {/* 刻度间隔 */}
        <div className="space-y-1.5">
          <Label htmlFor="ytick-interval" className="text-xs font-medium text-gray-700">
            刻度间隔
          </Label>
          <Input
            id="ytick-interval"
            type="number"
            value={style.yticks_interval ?? ''}
            onChange={(e) =>
              onChange({
                yticks_interval: e.target.value === '' ? null : Number(e.target.value),
              })
            }
            placeholder="自动"
            className="h-8 text-sm"
          />
        </div>

        {/* 隐藏刻度 */}
        <div className="flex items-center gap-2">
          <Checkbox
            id="remove-yticks"
            checked={style.remove_yticks || false}
            onCheckedChange={(checked: boolean) =>
              onChange({ remove_yticks: checked })
            }
          />
          <Label
            htmlFor="remove-yticks"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            隐藏 Y 轴刻度
          </Label>
        </div>
      </div>
    </div>
  );
}
