'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { useCanvasStore } from '@/store/canvasStore';
import { renderCanvas } from '@/lib/api';
import { Button } from '@/components/ui/button';

interface Props {
  onRenderComplete: (imageUrl: string) => void;
  onRenderError: (error: string) => void;
}

/**
 * 渲染画布按钮
 * 处理渲染逻辑和状态
 */
export default function RenderButton({ onRenderComplete, onRenderError }: Props) {
  const { canvas, subplots } = useCanvasStore();
  const [isRendering, setIsRendering] = useState(false);

  // 检查是否可以渲染
  const canRender = subplots.length > 0 && subplots.every(
    (subplot) => subplot.data.columns.length > 0 && subplot.data.data.length > 0
  );

  const handleRender = async () => {
    setIsRendering(true);
    onRenderError(''); // 清空之前的错误

    try {
      // 验证数据完整性
      if (subplots.length === 0) {
        throw new Error('请先添加至少一个子图');
      }

      for (const subplot of subplots) {
        if (!subplot.data.columns || subplot.data.columns.length === 0) {
          throw new Error(`子图 ${subplot.axIndex + 1} 缺少数据列`);
        }
        if (!subplot.data.data || subplot.data.data.length === 0) {
          throw new Error(`子图 ${subplot.axIndex + 1} 缺少数据`);
        }
      }

      // 调用渲染 API
      const blob = await renderCanvas(canvas, subplots);
      const imageUrl = URL.createObjectURL(blob);
      onRenderComplete(imageUrl);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '渲染时发生错误';
      onRenderError(errorMessage);
      console.error('Render error:', err);
    } finally {
      setIsRendering(false);
    }
  };

  return (
    <Button
      onClick={handleRender}
      disabled={isRendering || !canRender}
      className="w-full"
    >
      {isRendering && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {isRendering ? '渲染中...' : '渲染画布'}
    </Button>
  );
}
