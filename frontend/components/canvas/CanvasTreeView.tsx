'use client';

import { useMemo } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutGrid,
  BarChart3,
  BarChart2,
  LineChart,
  PieChart,
  AreaChart,
  Droplets,
  Table2,
  Box,
  Filter,
  TrendingUp,
  AlertCircle,
  Trash2,
  Map,
} from 'lucide-react';

import { TreeView } from '@/components/tree-view';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useCanvasStore } from '@/store/canvasStore';
import { getChartTypeName } from '@/constants/chartTypes';
import DeleteSubplotDialog from './DeleteSubplotDialog';

// 包装组件：为 barh 图标添加旋转样式
const BarhIcon = (props: any) => {
  return <BarChart2 {...props} className={`${props.className || ''} rotate-90`} />;
};

// 图表类型对应的 Lucide 图标（与 GridPreview 保持一致）
const chartTypeIcons: Record<string, React.ComponentType<any>> = {
  bar: BarChart3,
  barh: BarhIcon, // 使用包装组件以支持旋转
  line: LineChart,
  pie: PieChart,
  area: AreaChart,
  bubble: Droplets,
  hist: BarChart3,
  boxdot: Box,
  funnel: Filter,
  waterfall: TrendingUp,
  table: Table2,
  map: Map,
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
                name: `${getChartTypeName(subplot.chartType)} [${subplot.axIndex}]`,
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
