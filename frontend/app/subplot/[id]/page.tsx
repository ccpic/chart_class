'use client';

import { useParams, useRouter } from 'next/navigation';
import { Trash2 } from 'lucide-react';
import { useCanvasStore } from '@/store/canvasStore';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import MainContent from '@/components/layout/MainContent';
import RightPanel from '@/components/layout/RightPanel';
import SubplotTabs from '@/components/subplot/SubplotTabs';
import SubplotParams from '@/components/subplot/SubplotParams';
import DeleteSubplotDialog from '@/components/canvas/DeleteSubplotDialog';

export default function SubplotPage() {
  const params = useParams();
  const router = useRouter();
  const subplotId = params.id as string;
  const { toast } = useToast();
  
  const { subplots, deleteSubplot } = useCanvasStore();
  const subplot = subplots.find((s) => s.subplotId === subplotId);

  const handleDelete = (subplotId: string, axIndex: number) => {
    deleteSubplot(subplotId);
    router.push('/canvas');
    toast({
      title: '删除成功',
      description: `子图 ${axIndex + 1} 已删除`,
    });
  };

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
        <div className="min-h-full flex flex-col">
          {/* 标题栏 */}
          <div className="px-6 py-4 border-b bg-white flex-shrink-0 sticky top-0 z-10">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-bold">
                  子图 {subplot.axIndex + 1}
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  图表类型：{subplot.chartType} | 位置：第 {subplot.axIndex + 1} 个网格
                </p>
              </div>
              
              {/* 删除按钮 */}
              <DeleteSubplotDialog
                subplot={subplot}
                trigger={
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-2 text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span>删除子图</span>
                  </Button>
                }
                onConfirm={handleDelete}
                showChartType={false}
              />
            </div>
          </div>

          {/* Tabs 区域 - 顶天立地 */}
          <div className="flex-1 min-h-0">
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
