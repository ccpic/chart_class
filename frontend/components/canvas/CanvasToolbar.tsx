'use client';

import { Save, Upload, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useCanvasStore } from '@/store/canvasStore';
import { Button } from '@/components/ui/button';
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
 * 工具栏组件
 * 提供保存、加载、重置等操作
 */
export default function CanvasToolbar() {
  const { saveToLocalStorage, loadFromLocalStorage, reset } = useCanvasStore();
  const { toast } = useToast();
  const router = useRouter();

  const handleSave = () => {
    saveToLocalStorage();
    toast({
      title: '保存成功',
      description: '画布配置已保存到本地存储',
    });
  };

  const handleLoad = () => {
    loadFromLocalStorage();
    toast({
      title: '加载成功',
      description: '画布配置已从本地存储加载',
    });
  };

  const handleReset = () => {
    reset();
    // 重置后跳转到画布页面
    router.push('/canvas');
    toast({
      title: '重置成功',
      description: '所有画布和子图配置已清空',
    });
  };

  return (
    <div className="flex flex-col gap-2">
      <Button
        onClick={handleSave}
        variant="outline"
        size="sm"
        className="w-full justify-start gap-2"
      >
        <Save className="h-4 w-4" />
        <span>保存配置</span>
      </Button>

      <Button
        onClick={handleLoad}
        variant="outline"
        size="sm"
        className="w-full justify-start gap-2"
      >
        <Upload className="h-4 w-4" />
        <span>加载配置</span>
      </Button>

      <AlertDialog>
        <AlertDialogTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className="w-full justify-start gap-2"
          >
            <Trash2 className="h-4 w-4" />
            <span>重置画布</span>
          </Button>
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
    </div>
  );
}
