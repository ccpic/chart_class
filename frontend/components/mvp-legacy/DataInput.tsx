'use client';

import { useState } from 'react';

const EXAMPLE_DATA = {
  columns: ["品牌A", "品牌B", "品牌C"],
  index: ["2024-01", "2024-02", "2024-03"],
  data: [
    [1000, 800, 600],
    [1200, 900, 700],
    [1100, 1000, 800]
  ]
};

interface Props {
  onChange: (data: any) => void;
}

export default function DataInput({ onChange }: Props) {
  const [jsonText, setJsonText] = useState(
    JSON.stringify(EXAMPLE_DATA, null, 2)
  );
  const [error, setError] = useState<string | null>(null);

  const handleChange = (text: string) => {
    setJsonText(text);
    setError(null);

    try {
      const parsed = JSON.parse(text);
      onChange(parsed);
    } catch (err) {
      setError('JSON 格式错误');
      onChange(null);
    }
  };

  const loadExample = () => {
    const text = JSON.stringify(EXAMPLE_DATA, null, 2);
    setJsonText(text);
    handleChange(text);
  };

  return (
    <div className="space-y-3">
      <button
        onClick={loadExample}
        className="w-full px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50"
      >
        加载示例数据
      </button>

      <textarea
        value={jsonText}
        onChange={(e) => handleChange(e.target.value)}
        className="w-full h-96 p-3 border border-gray-300 rounded font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-black"
        placeholder='{"columns": [...], "data": [...]}'
      />

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      <div className="text-xs text-gray-500 space-y-1">
        <p>格式示例：</p>
        <pre className="bg-gray-100 p-2 rounded overflow-x-auto">
{`{
  "columns": ["列1", "列2"],
  "index": ["行1", "行2"],
  "data": [[100, 200], [300, 400]]
}`}
        </pre>
      </div>
    </div>
  );
}
