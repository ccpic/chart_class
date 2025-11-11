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
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Save } from 'lucide-react';

interface SaveChartDialogProps {
  trigger?: React.ReactNode;
}

export default function SaveChartDialog({ trigger }: SaveChartDialogProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  
  const saveCurrentAsChart = useChartStore((s) => s.saveCurrentAsChart);
  const { toast } = useToast();

  const handleSave = async () => {
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
      await saveCurrentAsChart(name.trim(), description.trim() || undefined);
      toast({
        title: '保存成功',
        description: `图表 "${name}" 已保存`,
      });
      setOpen(false);
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

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <SidebarMenuButton>
            <Save className="size-4" />
            <span>保存当前图表</span>
          </SidebarMenuButton>
        )}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>保存图表</DialogTitle>
          <DialogDescription>
            保存当前画布和所有子图的配置到本地数据库
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
                  handleSave();
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
          <Button variant="outline" onClick={() => setOpen(false)} disabled={saving}>
            取消
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? '保存中...' : '保存'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
