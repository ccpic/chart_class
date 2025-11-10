'use client';

import GridControls from '@/components/canvas/GridControls';
import GridPreview from '@/components/canvas/GridPreview';

/**
 * Canvas 参数面板
 * 包含网格控制和预览
 */
export default function CanvasParams() {
  return (
    <div className="h-full overflow-y-auto p-4">
      <h2 className="text-lg font-semibold mb-4">画布设置</h2>
      
      <GridControls />
      
      <div className="mt-6 pt-6 border-t">
        <h3 className="text-sm font-semibold mb-2">网格预览</h3>
        <GridPreview />
      </div>
    </div>
  );
}
