'use client';

import React, { useRef } from 'react';
import { chartDB } from '@/lib/db/chartDB';
import { useChartStore } from '@/store/chartStore';
import { useToast } from '@/hooks/use-toast';
import { SidebarMenuButton } from '@/components/ui/sidebar';
import { Upload } from 'lucide-react';

export default function ChartImport() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const loadCharts = useChartStore((s) => s.loadCharts);
  const { toast } = useToast();

  const handleFile = async (file?: File) => {
    if (!file) return;
    try {
      await chartDB.importChart(file);
      await loadCharts();
      toast({
        title: '导入成功',
        description: `图表已导入到本地数据库`,
      });
    } catch (e) {
      console.error('import failed', e);
      toast({
        title: '导入失败',
        description: (e as Error).message || '未知错误',
        variant: 'destructive',
      });
    }
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".savedchart,application/json"
        onChange={(e) => handleFile(e.target.files?.[0])}
        className="hidden"
      />
      <SidebarMenuButton onClick={() => fileInputRef.current?.click()}>
        <Upload className="size-4" />
        <span>导入图表文件</span>
      </SidebarMenuButton>
    </>
  );
}

