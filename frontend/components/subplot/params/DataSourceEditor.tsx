import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface DataSourceEditorProps {
  subplot: any; // TODO: 添加具体类型
  onUpdate: (updates: Record<string, any>) => void;
}

export function DataSourceEditor({ subplot, onUpdate }: DataSourceEditorProps) {
  // TODO: 从后端获取可用字段列表
  const availableFields = [
    '销售额',
    '利润',
    '数量',
    '折扣',
    '日期',
    '类别',
    '地区',
  ];

  return (
    <div className="space-y-4">
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
        <p className="text-xs text-amber-800">
          ⚠️ 数据源编辑器开发中...
        </p>
        <p className="text-xs text-amber-700 mt-1">
          当前版本暂时保留原有数据绑定方式
        </p>
      </div>

      {/* X 轴字段 */}
      <div className="space-y-1.5">
        <Label htmlFor="field-x" className="text-xs font-medium text-gray-700">
          X 轴字段
        </Label>
        <Select
          disabled
          defaultValue="placeholder"
        >
          <SelectTrigger id="field-x" className="h-8 text-sm">
            <SelectValue placeholder="选择字段" />
          </SelectTrigger>
          <SelectContent>
            {availableFields.map((field) => (
              <SelectItem key={field} value={field}>
                {field}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Y 轴字段 */}
      <div className="space-y-1.5">
        <Label htmlFor="field-y" className="text-xs font-medium text-gray-700">
          Y 轴字段
        </Label>
        <Select
          disabled
          defaultValue="placeholder"
        >
          <SelectTrigger id="field-y" className="h-8 text-sm">
            <SelectValue placeholder="选择字段" />
          </SelectTrigger>
          <SelectContent>
            {availableFields.map((field) => (
              <SelectItem key={field} value={field}>
                {field}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 颜色映射字段（可选）*/}
      <div className="space-y-1.5">
        <Label htmlFor="field-hue" className="text-xs font-medium text-gray-700">
          颜色映射（可选）
        </Label>
        <Select
          disabled
          defaultValue="none"
        >
          <SelectTrigger id="field-hue" className="h-8 text-sm">
            <SelectValue placeholder="无" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">无</SelectItem>
            {availableFields.map((field) => (
              <SelectItem key={field} value={field}>
                {field}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="pt-2 border-t">
        <p className="text-xs text-gray-500">
          提示：数据源功能需要配合后端 API 完善
        </p>
      </div>
    </div>
  );
}
