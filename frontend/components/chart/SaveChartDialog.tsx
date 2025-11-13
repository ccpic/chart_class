'use client';

import React, { useState } from 'react';
import { useChartStore } from '@/store/chartStore';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { SidebarMenuButton } from '@/components/ui/sidebar';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Save } from 'lucide-react';

interface SaveChartDialogProps {
  trigger?: React.ReactNode;
}

export default function SaveChartDialog({ trigger }: SaveChartDialogProps) {
  const [inputDialogOpen, setInputDialogOpen] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  
  const { currentChartId, currentChart, saveCurrentAsChart, updateCurrentChart, saveAs } = useChartStore();
  const { toast } = useToast();

  // 点击保存按钮的入口
  const handleSaveClick = () => {
    if (currentChartId && currentChart) {
      // 已保存图表：显示确认对话框（覆盖/另存为/取消）
      setConfirmDialogOpen(true);
    } else {
      // 未保存图表：显示输入对话框
      setInputDialogOpen(true);
    }
  };

  // 确认覆盖（更新现有图表）
  const handleOverwrite = async () => {
    setSaving(true);
    try {
      await updateCurrentChart();
      toast({
        title: '已更新',
        description: `图表 "${currentChart?.name}" 已更新`,
      });
      setConfirmDialogOpen(false);
    } catch (error) {
      console.error('Update failed:', error);
      toast({
        title: '保存失败',
        description: (error as Error).message || '未知错误',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  // 选择另存为
  const handleSaveAsChoice = () => {
    setConfirmDialogOpen(false);
    // 预填充当前图表名称
    setName(currentChart?.name || '');
    setDescription(currentChart?.description || '');
    setInputDialogOpen(true);
  };

  // 保存新图表或另存为
  const handleSaveWithInput = async () => {
    if (!name.trim()) {
      toast({
        title: '错误',
        description: '请输入图表名称',
        variant: 'destructive',
      });
      return;
    }

    setSaving(true);
    try {
      if (currentChartId && currentChart) {
        // 另存为
        await saveAs(name.trim(), description.trim() || undefined);
        toast({
          title: '保存成功',
          description: `图表 "${name}" 已另存为新图表`,
        });
      } else {
        // 首次保存
        await saveCurrentAsChart(name.trim(), description.trim() || undefined);
        toast({
          title: '保存成功',
          description: `图表 "${name}" 已保存`,
        });
      }
      setInputDialogOpen(false);
      setName('');
      setDescription('');
    } catch (error) {
      console.error('Save failed:', error);
      toast({
        title: '保存失败',
        description: (error as Error).message || '未知错误',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const triggerElement = trigger || (
    <SidebarMenuButton onClick={handleSaveClick}>
      <Save className="size-4" />
      <span>保存当前图表</span>
    </SidebarMenuButton>
  );

  return (
    <>
      {/* 触发按钮 */}
      {!trigger && triggerElement}
      {trigger && <div onClick={handleSaveClick}>{trigger}</div>}

      {/* 确认对话框：覆盖/另存为/取消 */}
      <AlertDialog open={confirmDialogOpen} onOpenChange={setConfirmDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>保存图表</AlertDialogTitle>
            <AlertDialogDescription>
              当前图表 &quot;{currentChart?.name}&quot; 已存在，请选择保存方式：
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-col sm:flex-row gap-2">
            <AlertDialogCancel>取消</AlertDialogCancel>
            <Button variant="outline" onClick={handleSaveAsChoice} disabled={saving}>
              另存为
            </Button>
            <AlertDialogAction onClick={handleOverwrite} disabled={saving}>
              {saving ? '更新中...' : '覆盖'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* 输入对话框：输入标题和描述 */}
      <Dialog open={inputDialogOpen} onOpenChange={setInputDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {currentChartId ? '另存为新图表' : '保存图表'}
            </DialogTitle>
            <DialogDescription>
              {currentChartId 
                ? '将当前图表另存为新图表'
                : '保存当前画布和所有子图的配置到本地数据库'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">图表名称 *</Label>
              <Input
                id="name"
                placeholder="例如：销售分析图表"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSaveWithInput();
                  }
                }}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">描述（可选）</Label>
              <Textarea
                id="description"
                placeholder="添加一些备注信息..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setInputDialogOpen(false)} disabled={saving}>
              取消
            </Button>
            <Button onClick={handleSaveWithInput} disabled={saving}>
              {saving ? '保存中...' : '保存'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
