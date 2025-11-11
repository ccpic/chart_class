import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { PlotStyle } from '@/types/plotStyle';

interface TitleSectionProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
}

export function TitleSection({ style, onChange }: TitleSectionProps) {
  return (
    <div className="space-y-3">
      {/* 标题文本和字体大小 - 4:1 布局 */}
      <div className="space-y-1.5">
        <div className="grid grid-cols-5 gap-2 items-end">
          <div className="col-span-4 space-y-1.5">
            <Label htmlFor="title" className="text-xs font-medium text-gray-700">
              标题文本
            </Label>
            <Input
              id="title"
              value={style.title || ''}
              onChange={(e) => onChange({ title: e.target.value })}
              placeholder="输入图表标题"
              className="h-8 text-sm"
            />
          </div>
          <div className="col-span-1 space-y-1.5">
            <Label htmlFor="title-fontsize" className="text-xs font-medium text-gray-700">
              字号
            </Label>
            <Input
              id="title-fontsize"
              type="number"
              value={style.title_fontsize || 14}
              onChange={(e) => onChange({ title_fontsize: Number(e.target.value) })}
              min={8}
              max={48}
              className="h-8 text-sm"
            />
          </div>
        </div>
        <p className="text-xs text-gray-500">
          推荐字号：12-24
        </p>
      </div>
    </div>
  );
}
