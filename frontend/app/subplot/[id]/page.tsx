'use client';

import { useParams } from 'next/navigation';
import { useCanvasStore } from '@/store/canvasStore';
import MainContent from '@/components/layout/MainContent';
import RightPanel from '@/components/layout/RightPanel';
import SubplotTabs from '@/components/subplot/SubplotTabs';
import SubplotParams from '@/components/subplot/SubplotParams';

export default function SubplotPage() {
  const params = useParams();
  const subplotId = params.id as string;
  
  const { subplots } = useCanvasStore();
  const subplot = subplots.find((s) => s.subplotId === subplotId);

  if (!subplot) {
    return (
      <div className="flex h-full w-full">
        <MainContent>
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-lg text-gray-600 mb-4">❌ 子图不存在</p>
              <p className="text-sm text-gray-500">ID: {subplotId}</p>
            </div>
          </div>
        </MainContent>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full">
      {/* 中心内容区：Tabs（预览 + 数据编辑） */}
      <MainContent>
        <div className="h-full flex flex-col">
          {/* 标题栏 */}
          <div className="px-6 py-4 border-b bg-white flex-shrink-0">
            <h1 className="text-2xl font-bold">
              子图 {subplot.axIndex + 1}
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              图表类型：{subplot.chartType} | 位置：第 {subplot.axIndex + 1} 个网格
            </p>
          </div>

          {/* Tabs 区域 - 顶天立地 */}
          <div className="flex-1 overflow-hidden">
            <SubplotTabs subplot={subplot} />
          </div>
        </div>
      </MainContent>

      {/* 右侧参数面板 */}
      <RightPanel>
        <SubplotParams subplot={subplot} />
      </RightPanel>
    </div>
  );
}
