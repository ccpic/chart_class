import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import type { PlotStyle } from '@/types/plotStyle';

interface BorderSectionProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
}

export function BorderSection({ style, onChange }: BorderSectionProps) {
  // 默认都显示（如果未设置，则默认为 true）
  const showTop = style.show_top_spine !== undefined ? style.show_top_spine : true;
  const showRight = style.show_right_spine !== undefined ? style.show_right_spine : true;
  const showBottom = style.show_bottom_spine !== undefined ? style.show_bottom_spine : true;
  const showLeft = style.show_left_spine !== undefined ? style.show_left_spine : true;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        {/* 上边框 */}
        <div className="flex items-center gap-2">
          <Checkbox
            id="show-top-spine"
            checked={showTop}
            onCheckedChange={(checked) =>
              onChange({ show_top_spine: checked as boolean })
            }
          />
          <Label
            htmlFor="show-top-spine"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            上边框
          </Label>
        </div>

        {/* 右边框 */}
        <div className="flex items-center gap-2">
          <Checkbox
            id="show-right-spine"
            checked={showRight}
            onCheckedChange={(checked) =>
              onChange({ show_right_spine: checked as boolean })
            }
          />
          <Label
            htmlFor="show-right-spine"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            右边框
          </Label>
        </div>

        {/* 下边框 */}
        <div className="flex items-center gap-2">
          <Checkbox
            id="show-bottom-spine"
            checked={showBottom}
            onCheckedChange={(checked) =>
              onChange({ show_bottom_spine: checked as boolean })
            }
          />
          <Label
            htmlFor="show-bottom-spine"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            下边框
          </Label>
        </div>

        {/* 左边框 */}
        <div className="flex items-center gap-2">
          <Checkbox
            id="show-left-spine"
            checked={showLeft}
            onCheckedChange={(checked) =>
              onChange({ show_left_spine: checked as boolean })
            }
          />
          <Label
            htmlFor="show-left-spine"
            className="text-sm font-medium text-gray-700 cursor-pointer"
          >
            左边框
          </Label>
        </div>
      </div>
      <p className="text-xs text-gray-500">
        控制图表四个边框的显示/隐藏
      </p>
    </div>
  );
}

