import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import type { PlotStyle, GridConfig } from '@/types/plotStyle';

interface GridSectionProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
}

export function GridSection({ style, onChange }: GridSectionProps) {
  // 修复：undefined 和 null 都应该被视为未启用
  const majorEnabled = !!style.major_grid;
  const minorEnabled = !!style.minor_grid;

  const toggleMajorGrid = (checked: boolean) => {
    onChange({
      major_grid: checked
        ? { axis: 'both', linestyle: '-', alpha: 0.3 }
        : null,
    });
  };

  const toggleMinorGrid = (checked: boolean) => {
    onChange({
      minor_grid: checked
        ? { axis: 'both' }
        : null,
    });
  };

  const updateMajorGrid = (updates: Partial<GridConfig>) => {
    onChange({
      major_grid: { ...style.major_grid, ...updates } as GridConfig,
    });
  };

  const updateMinorGrid = (updates: Partial<GridConfig>) => {
    onChange({
      minor_grid: { ...style.minor_grid, ...updates } as GridConfig,
    });
  };

  return (
    <div className="space-y-4">
      {/* 主网格线 */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Checkbox
            id="major-grid"
            checked={majorEnabled}
            onCheckedChange={toggleMajorGrid}
          />
          <Label
            htmlFor="major-grid"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            主网格线
          </Label>
        </div>

        {majorEnabled && (
          <div className="ml-6 space-y-3 border-l-2 border-gray-200 pl-3">
            {/* 网格方向和线型 - 1:1 布局 */}
            <div className="space-y-1.5">
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1.5">
                  <Label htmlFor="major-grid-axis" className="text-xs text-gray-600">
                    网格方向
                  </Label>
                  <Select
                    value={style.major_grid?.axis || 'both'}
                    onValueChange={(value: 'both' | 'x' | 'y') =>
                      updateMajorGrid({ axis: value })
                    }
                  >
                    <SelectTrigger id="major-grid-axis" className="h-8 text-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="both">双向</SelectItem>
                      <SelectItem value="x">横向</SelectItem>
                      <SelectItem value="y">纵向</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="major-grid-style" className="text-xs text-gray-600">
                    线型
                  </Label>
                  <Select
                    value={style.major_grid?.linestyle || '-'}
                    onValueChange={(value) => updateMajorGrid({ linestyle: value })}
                  >
                    <SelectTrigger id="major-grid-style" className="h-8 text-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="-">实线</SelectItem>
                      <SelectItem value="--">虚线</SelectItem>
                      <SelectItem value=":">点线</SelectItem>
                      <SelectItem value="-.">点划线</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 次网格线 */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Checkbox
            id="minor-grid"
            checked={minorEnabled}
            onCheckedChange={toggleMinorGrid}
          />
          <Label
            htmlFor="minor-grid"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            次网格线
          </Label>
        </div>

        {minorEnabled && (
          <div className="ml-6 space-y-3 border-l-2 border-gray-200 pl-3">
            {/* 网格方向 */}
            <div className="space-y-1.5">
              <Label htmlFor="minor-grid-axis" className="text-xs text-gray-600">
                网格方向
              </Label>
              <Select
                value={style.minor_grid?.axis || 'both'}
                onValueChange={(value: 'both' | 'x' | 'y') =>
                  updateMinorGrid({ axis: value })
                }
              >
                <SelectTrigger id="minor-grid-axis" className="h-8 text-sm">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="both">横纵双向</SelectItem>
                  <SelectItem value="x">仅横向（X轴）</SelectItem>
                  <SelectItem value="y">仅纵向（Y轴）</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <p className="text-xs text-gray-500">
              次网格线样式由 matplotlib 自动设置
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
