'use client';

import { useMemo } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutGrid,
  BarChart3,
  LineChart,
  PieChart,
  AreaChart,
  Circle,
  Flame,
  TreePine,
  Grid3x3,
  Triangle,
  Box,
  Target,
  Cloud,
  AlertCircle,
  Trash2,
} from 'lucide-react';

import { TreeView } from '@/components/tree-view';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useCanvasStore } from '@/store/canvasStore';
import DeleteSubplotDialog from './DeleteSubplotDialog';

// 图表类型的中文名称
const chartTypeNames: Record<string, string> = {
  bar: '柱状图',
  line: '折线图',
  pie: '饼图',
  area: '面积图',
  bubble: '气泡图',
  hist: '直方图',
  heatmap: '热力图',
  treemap: '树状图',
  waffle: '华夫饼图',
  funnel: '漏斗图',
  venn2: '韦恩图(2)',
  venn3: '韦恩图(3)',
  boxdot: '箱型图',
  stripdot: '算珠图',
  word_cloud: '词云',
  table: '高级表格',
};

// 图表类型对应的 Lucide 图标
const chartTypeIcons: Record<string, React.ComponentType<any>> = {
  bar: BarChart3,
  line: LineChart,
  pie: PieChart,
  area: AreaChart,
  bubble: Circle,
  hist: BarChart3,
  heatmap: Flame,
  treemap: TreePine,
  waffle: Grid3x3,
  funnel: Triangle,
  venn2: Circle,
  venn3: Circle,
  boxdot: Box,
  stripdot: Target,
  word_cloud: Cloud,
};

interface CanvasTreeViewProps {
  /**
   * 是否自动展开所有节点
   * @default true
   */
  expandAll?: boolean;
  
  /**
   * 额外的 className
   */
  className?: string;
}

/**
 * 画布和子图树形结构组件
 * 
 * 功能：
 * - 以树形结构展示画布和子图的层级关系
 * - 画布作为根节点，显示标题和网格尺寸
 * - 子图作为子节点，显示图表类型、中文名称和位置索引
 * - 支持点击导航到对应页面
 * - 根据当前路径自动高亮选中的节点
 * 
 * @example
 * ```tsx
 * <CanvasTreeView expandAll={true} className="p-2" />
 * ```
 */
export default function CanvasTreeView({
  expandAll = true,
  className = 'p-2',
}: CanvasTreeViewProps) {
  const pathname = usePathname();
  const router = useRouter();
  const canvas = useCanvasStore((state) => state.canvas);
  const subplots = useCanvasStore((state) => state.subplots);
  const isDataComplete = useCanvasStore((state) => state.isDataComplete);
  const deleteSubplot = useCanvasStore((state) => state.deleteSubplot);
  const { toast } = useToast();

  // 删除子图的处理函数
  const handleDeleteSubplot = (subplotId: string, axIndex: number) => {
    deleteSubplot(subplotId);
    // 如果当前在该子图页面，跳转到画布页面
    if (pathname.includes(subplotId)) {
      router.push('/canvas');
    }
    toast({
      title: '删除成功',
      description: `子图 ${axIndex + 1} 已删除`,
    });
  };

  // 构建树形数据结构
  const treeData = useMemo(() => {
    return [
      {
        id: 'canvas',
        name: `${canvas.title || '主画布'} (${canvas.rows}×${canvas.cols})`,
        icon: LayoutGrid,
        children: subplots.length > 0 
          ? subplots.map((subplot) => {
              const hasData = isDataComplete(subplot.subplotId);
              // 未配置数据的子图使用警告图标，已配置的使用对应图表图标
              const IconComponent = hasData 
                ? (chartTypeIcons[subplot.chartType] || BarChart3)
                : AlertCircle;
              
              return {
                id: subplot.subplotId,
                name: `${chartTypeNames[subplot.chartType] || subplot.chartType} [${subplot.axIndex}]`,
                icon: IconComponent,
                onClick: () => router.push(`/subplot/${subplot.subplotId}`),
                // 添加删除按钮
                actions: (
                  <DeleteSubplotDialog
                    subplot={subplot}
                    trigger={
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </Button>
                    }
                    onConfirm={handleDeleteSubplot}
                  />
                ),
              };
            })
          : undefined, // 没有子图时不显示 children
        onClick: () => router.push('/canvas'),
      },
    ];
  }, [canvas.title, canvas.rows, canvas.cols, subplots, router, isDataComplete, handleDeleteSubplot]);

  // 根据当前路径确定选中的项目
  const selectedItemId = useMemo(() => {
    if (pathname === '/canvas') {
      return 'canvas';
    }
    const match = pathname.match(/\/subplot\/(.+)/);
    return match ? match[1] : undefined;
  }, [pathname]);

  return (
    <TreeView
      key={selectedItemId} // 使用 key 强制重新渲染以同步选中状态
      data={treeData}
      initialSelectedItemId={selectedItemId}
      expandAll={expandAll}
      className={className}
    />
  );
}
