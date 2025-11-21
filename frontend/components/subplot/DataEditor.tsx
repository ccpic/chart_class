'use client';

import React, { useState } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig, ChartData } from '@/types/canvas';
import { AlertCircle } from 'lucide-react';

interface Props {
  subplot: SubplotConfig;
}

// 示例数据模板（使用 DataFrame 格式）
const EXAMPLE_DATA: Record<string, ChartData> = {
  bar: {
    columns: ['销量', '目标'],
    index: ['产品A', '产品B', '产品C', '产品D'],
    data: [
      [120, 100],
      [90, 100],
      [150, 100],
      [80, 100],
    ],
  },
  line: {
    columns: ['营收', '成本'],
    index: ['1月', '2月', '3月', '4月', '5月', '6月'],
    data: [
      [50, 30],
      [60, 35],
      [55, 32],
      [70, 40],
      [85, 45],
      [90, 48],
    ],
  },
  pie: {
    columns: ['占比'],
    index: ['类别A', '类别B', '类别C', '类别D'],
    data: [[35], [25], [20], [20]],
  },
  area: {
    columns: ['区域1', '区域2'],
    index: ['Q1', 'Q2', 'Q3', 'Q4'],
    data: [
      [10, 15],
      [20, 25],
      [15, 20],
      [25, 30],
    ],
  },
  boxdot: {
    columns: ['类别', '数值'],
    index: ['样本1', '样本2', '样本3', '样本4', '样本5', '样本6', '样本7', '样本8'],
    data: [
      ['A', 25],
      ['A', 30],
      ['A', 28],
      ['B', 35],
      ['B', 40],
      ['B', 38],
      ['C', 20],
      ['C', 22],
    ],
  },
};

export default function DataEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  const [jsonText, setJsonText] = useState(
    JSON.stringify(subplot.data, null, 2)
  );
  const [error, setError] = useState<string | null>(null);

  const handleJsonChange = (value: string) => {
    setJsonText(value);
    setError(null);

    try {
      const parsed = JSON.parse(value) as ChartData;
      
      // 验证数据结构（DataFrame 格式）
      if (!parsed.columns || !Array.isArray(parsed.columns)) {
        throw new Error('缺少 columns 字段或格式错误');
      }
      if (!parsed.data || !Array.isArray(parsed.data)) {
        throw new Error('缺少 data 字段或格式错误');
      }
      // 验证每行数据长度与列数一致
      for (const row of parsed.data) {
        if (!Array.isArray(row) || row.length !== parsed.columns.length) {
          throw new Error('data 中每行的长度必须与 columns 长度一致');
        }
      }

      updateSubplot(subplot.subplotId, { data: parsed });
    } catch (err) {
      setError(err instanceof Error ? err.message : '数据格式错误');
    }
  };

  const loadExample = () => {
    const exampleData = EXAMPLE_DATA[subplot.chartType];
    const formatted = JSON.stringify(exampleData, null, 2);
    setJsonText(formatted);
    handleJsonChange(formatted);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold">数据配置</label>
        <button
          onClick={loadExample}
          className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded"
        >
          加载示例数据
        </button>
      </div>
      
      <textarea
        value={jsonText}
        onChange={(e) => handleJsonChange(e.target.value)}
        className={`
          w-full h-64 px-3 py-2 border rounded-md font-mono text-xs
          ${error ? 'border-red-500' : 'border-gray-300'}
          focus:outline-none focus:ring-2 focus:ring-black
        `}
        placeholder='{"columns": ["系列1", "系列2"], "index": ["A", "B"], "data": [[1, 2], [3, 4]]}'
      />
      
      {error && (
        <div className="text-xs text-red-500 bg-red-50 px-2 py-1 rounded flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </div>
      )}
      
      <div className="text-xs text-gray-500">
        <details>
          <summary className="cursor-pointer">数据格式说明</summary>
          <pre className="mt-2 p-2 bg-gray-50 rounded text-xs overflow-auto">
{`{
  "columns": ["系列1", "系列2"],
  "index": ["行1", "行2", "行3"],
  "data": [
    [值1, 值2],
    [值3, 值4],
    [值5, 值6]
  ]
}`}
          </pre>
        </details>
      </div>
    </div>
  );
}
