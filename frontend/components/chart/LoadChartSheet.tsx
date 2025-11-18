'use client';

import React, { useEffect, useState } from 'react';
import { useChartStore } from '@/store/chartStore';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { SidebarMenuButton } from '@/components/ui/sidebar';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { FolderOpen, Trash2, Download, Search } from 'lucide-react';
import { chartDB } from '@/lib/db/chartDB';
import { saveAs } from 'file-saver';
import { Input } from '@/components/ui/input';

interface LoadChartDialogProps {
  trigger?: React.ReactNode;
}

function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  return date.toLocaleDateString('zh-CN');
}

export default function LoadChartDialog({ trigger }: LoadChartDialogProps) {
  const [open, setOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [chartToDelete, setChartToDelete] = useState<{ id: string; name: string } | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const charts = useChartStore((s) => s.charts);
  const loadCharts = useChartStore((s) => s.loadCharts);
  const loadChart = useChartStore((s) => s.loadChart);
  const deleteChart = useChartStore((s) => s.deleteChart);
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      loadCharts();
    }
  }, [open, loadCharts]);

  // 按更新时间排序（新到旧）并筛选
  const filteredAndSortedCharts = charts
    .filter((chart) =>
      chart.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => b.updatedAt - a.updatedAt);

  const handleLoad = async (id: string) => {
    try {
      await loadChart(id);
      setOpen(false);
      router.push('/canvas?tab=grid'); // 加载后跳转到网格布局tab
      toast({
        title: '加载成功',
        description: '图表已加载到画布',
      });
    } catch (error) {
      console.error('Load failed:', error);
      toast({
        title: '加载失败',
        description: (error as Error).message || '未知错误',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id: string, name: string) => {
    setChartToDelete({ id, name });
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!chartToDelete) return;
    
    try {
      await deleteChart(chartToDelete.id);
      toast({
        title: '删除成功',
        description: `图表 "${chartToDelete.name}" 已删除`,
      });
    } catch (error) {
      console.error('Delete failed:', error);
      toast({
        title: '删除失败',
        description: (error as Error).message || '未知错误',
        variant: 'destructive',
      });
    } finally {
      setDeleteDialogOpen(false);
      setChartToDelete(null);
    }
  };

  const handleExport = async (id: string, name: string) => {
    try {
      const blob = await chartDB.exportChart(id);
      saveAs(blob, `${name.replace(/\s+/g, '_')}-${Date.now()}.savedchart`);
      toast({
        title: '导出成功',
        description: `图表 "${name}" 已导出`,
      });
    } catch (error) {
      console.error('Export failed:', error);
      toast({
        title: '导出失败',
        description: (error as Error).message || '未知错误',
        variant: 'destructive',
      });
    }
  };

  return (
    <>
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          {trigger || (
            <SidebarMenuButton>
              <FolderOpen className="size-4" />
              <span>加载存档图表</span>
            </SidebarMenuButton>
          )}
        </SheetTrigger>
        <SheetContent className="w-full sm:max-w-2xl overflow-y-auto">
          <SheetHeader>
            <SheetTitle>加载图表</SheetTitle>
            <SheetDescription>
              从本地数据库加载已保存的图表
            </SheetDescription>
          </SheetHeader>

          {/* 搜索框 */}
          <div className="mt-6 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="搜索图表名称..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          <div className="mt-4">
            {charts.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                <FolderOpen className="h-12 w-12 mb-2 opacity-50" />
                <p>暂无保存的图表</p>
              </div>
            ) : filteredAndSortedCharts.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                <Search className="h-12 w-12 mb-2 opacity-50" />
                <p>未找到匹配的图表</p>
                <p className="text-xs mt-1">尝试使用其他关键词搜索</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredAndSortedCharts.map((chart) => (
                  <div
                    key={chart.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-sm">{chart.name}</h3>
                        {chart.description && (
                          <p className="text-xs text-gray-600 mt-1">{chart.description}</p>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>{chart.subplots?.length || 0} 个子图</span>
                          <span>{formatTime(chart.updatedAt)}</span>
                        </div>
                      </div>
                      <div className="flex gap-1 ml-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleLoad(chart.id)}
                          title="加载"
                        >
                          <FolderOpen className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleExport(chart.id, chart.name)}
                          title="导出"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive hover:text-destructive"
                          onClick={() => handleDelete(chart.id, chart.name)}
                          title="删除"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </SheetContent>
      </Sheet>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除图表</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除图表 &quot;{chartToDelete?.name}&quot; 吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              确认删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
