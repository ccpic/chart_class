'use client';

import React from 'react';
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
import { SubplotConfig } from '@/types/canvas';
import { getChartTypeName } from '@/constants/chartTypes';

interface DeleteSubplotDialogProps {
  /** 子图配置 */
  subplot: SubplotConfig;
  /** 删除按钮的触发元素 */
  trigger: React.ReactNode;
  /** 删除确认后的回调函数 */
  onConfirm: (subplotId: string, axIndex: number) => void;
  /** 是否显示图表类型信息 */
  showChartType?: boolean;
}

/**
 * 删除子图确认对话框组件
 * 
 * 可复用的删除子图确认对话框，用于统一删除确认的UI和逻辑
 * 
 * @example
 * ```tsx
 * <DeleteSubplotDialog
 *   subplot={subplot}
 *   trigger={<Button>删除</Button>}
 *   onConfirm={(subplotId, axIndex) => deleteSubplot(subplotId)}
 * />
 * ```
 */
export default function DeleteSubplotDialog({
  subplot,
  trigger,
  onConfirm,
  showChartType = true,
}: DeleteSubplotDialogProps) {
  const handleConfirm = () => {
    onConfirm(subplot.subplotId, subplot.axIndex);
  };

  const chartTypeName = getChartTypeName(subplot.chartType);
  const description = showChartType
    ? `此操作将删除子图 ${subplot.axIndex + 1} (${chartTypeName}) 及其所有数据和配置，无法撤销。确定要继续吗？`
    : `此操作将删除子图 ${subplot.axIndex + 1} 及其所有数据和配置，无法撤销。确定要继续吗？`;

  return (
    <div onClick={(e) => e.stopPropagation()}>
      <AlertDialog>
        <AlertDialogTrigger asChild onClick={(e) => e.stopPropagation()}>
          {trigger}
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除子图</AlertDialogTitle>
            <AlertDialogDescription>
              {description}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirm}>
              确认删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

