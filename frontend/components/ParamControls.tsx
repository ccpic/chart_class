'use client';

interface Params {
  stacked: boolean;
  show_label: boolean;
  label_formatter: string;
}

interface Props {
  params: Params;
  onChange: (params: Params) => void;
}

export default function ParamControls({ params, onChange }: Props) {
  const updateParam = (key: keyof Params, value: any) => {
    onChange({ ...params, [key]: value });
  };

  return (
    <div className="space-y-4">
      {/* 堆叠显示 */}
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">堆叠显示</label>
        <input
          type="checkbox"
          checked={params.stacked}
          onChange={(e) => updateParam('stacked', e.target.checked)}
          className="w-5 h-5"
        />
      </div>

      {/* 显示标签 */}
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">显示标签</label>
        <input
          type="checkbox"
          checked={params.show_label}
          onChange={(e) => updateParam('show_label', e.target.checked)}
          className="w-5 h-5"
        />
      </div>

      {/* 标签格式 */}
      <div className="space-y-2">
        <label className="text-sm font-medium">标签格式</label>
        <select
          value={params.label_formatter}
          onChange={(e) => updateParam('label_formatter', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black"
        >
          <option value="{abs}">绝对值</option>
          <option value="{share}">占比</option>
          <option value="{abs}\n{share}">双行显示</option>
        </select>
      </div>

      {/* 参数说明 */}
      <div className="mt-6 p-3 bg-gray-50 rounded text-xs text-gray-600 space-y-2">
        <p><strong>堆叠显示</strong>: 是否堆叠柱体</p>
        <p><strong>显示标签</strong>: 是否在柱体上显示数值</p>
        <p><strong>标签格式</strong>: 标签的显示格式</p>
      </div>
    </div>
  );
}
