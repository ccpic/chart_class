'use client';

import { useState } from 'react';
import DataInput from '@/components/DataInput';
import ParamControls from '@/components/ParamControls';
import ChartPreview from '@/components/ChartPreview';
import { renderChart } from '@/lib/api';

export default function Home() {
  // 状态管理
  const [chartData, setChartData] = useState<any>(null);
  const [params, setParams] = useState({
    stacked: true,
    show_label: true,
    label_formatter: '{abs}'
  });
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 渲染图表
  const handleRender = async () => {
    if (!chartData) {
      setError('请先输入数据');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // 构造完整的参数对象，包含 chart_type
      const fullParams = {
        chart_type: 'bar',
        ...params
      };
      const blob = await renderChart(chartData, fullParams);
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
    } catch (err: any) {
      setError(err.message || '渲染失败');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧：数据输入 */}
      <aside className="w-80 bg-white border-r p-4 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">数据输入</h2>
        <DataInput onChange={setChartData} />
      </aside>

      {/* 中间：预览区 */}
      <main className="flex-1 p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Chart Class - MVP</h1>
          <button
            onClick={handleRender}
            disabled={isLoading || !chartData}
            className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 disabled:bg-gray-300"
          >
            {isLoading ? '渲染中...' : '渲染图表'}
          </button>
        </div>
        
        <ChartPreview 
          imageUrl={previewUrl} 
          isLoading={isLoading}
          error={error}
        />
      </main>

      {/* 右侧：参数控制 */}
      <aside className="w-80 bg-white border-l p-4 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">参数设置</h2>
        <ParamControls params={params} onChange={setParams} />
      </aside>
    </div>
  );
}
