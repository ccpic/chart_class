'use client';

import { useState } from 'react';
import { Loader2, AlertCircle, BarChart3 } from 'lucide-react';
import { SubplotConfig } from '@/types/canvas';
import { renderSubplot } from '@/lib/api';
import { Button } from '@/components/ui/button';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 子图预览标签页
 * 显示单个子图的渲染效果
 */
export default function SubplotPreview({ subplot }: Props) {
  const [isRendering, setIsRendering] = useState(false);
  const [renderedImage, setRenderedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const hasData =
    subplot.data.columns &&
    subplot.data.columns.length > 0 &&
    subplot.data.data &&
    subplot.data.data.length > 0;

  const handleRender = async () => {
    setIsRendering(true);
    setError(null);

    try {
      const blob = await renderSubplot(subplot);
      const imageUrl = URL.createObjectURL(blob);
      setRenderedImage(imageUrl);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '渲染失败';
      setError(errorMessage);
      console.error('Subplot render error:', err);
    } finally {
      setIsRendering(false);
    }
  };

  return (
    <div className="space-y-4 pt-4">
      {/* 渲染按钮 */}
      <Button
        onClick={handleRender}
        disabled={isRendering || !hasData}
        className="w-full"
      >
        {isRendering && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {isRendering ? '渲染中...' : '渲染预览'}
      </Button>

      {/* 错误提示 */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600 flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            {error}
          </p>
        </div>
      )}

      {/* 空状态或渲染结果 */}
      {!renderedImage && !error && (
        <div className="flex items-center justify-center h-[400px] bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <div className="text-center">
            <BarChart3 className="h-16 w-16 mx-auto mb-3 text-gray-400" />
            <p className="text-gray-700 font-medium mb-1">
              {hasData ? '点击上方按钮预览图表' : '请先在"数据编辑"标签页配置数据'}
            </p>
            <p className="text-sm text-gray-500">
              图表类型：{subplot.chartType}
            </p>
          </div>
        </div>
      )}

      {/* 渲染结果 */}
      {renderedImage && (
        <div className="border rounded-lg overflow-hidden bg-white">
          <img
            src={renderedImage}
            alt={`Subplot ${subplot.axIndex + 1} Preview`}
            className="w-full h-auto"
          />
        </div>
      )}
    </div>
  );
}
