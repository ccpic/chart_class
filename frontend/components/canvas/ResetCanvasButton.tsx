'use client';

import { Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useCanvasStore } from '@/store/canvasStore';
import { useChartStore } from '@/store/chartStore';
import { SidebarMenuButton } from '@/components/ui/sidebar';
import { useToast } from '@/hooks/use-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

/**
 * 重置画布按钮组件
 * 提供重置画布和子图的功能，带有确认对话框
 */
export default function ResetCanvasButton() {
  const reset = useCanvasStore((state) => state.reset);
  const clearCurrentChartId = useChartStore((state) => state.clearCurrentChartId);
  const { toast } = useToast();
  const router = useRouter();

  const handleReset = () => {
    reset();
    clearCurrentChartId(); // 清除当前图表关联
    // 重置后跳转到画布页面
    router.push('/canvas');
    toast({
      title: '重置成功',
      description: '所有画布和子图配置已清空',
    });
  };

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <SidebarMenuButton>
          <Trash2 className="size-4" />
          <span>重置画布</span>
        </SidebarMenuButton>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>确认重置画布</AlertDialogTitle>
          <AlertDialogDescription>
            此操作将清空所有画布和子图配置，无法撤销。确定要继续吗？
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>取消</AlertDialogCancel>
          <AlertDialogAction onClick={handleReset}>
            确认重置
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
