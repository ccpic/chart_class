'use client';

import React from 'react';
import { useChartStore } from '@/store/chartStore';
import { chartDB } from '@/lib/db/chartDB';
import { Button } from '@/components/ui/button';
import { saveAs } from 'file-saver';

export default function ChartExport() {
  const charts = useChartStore((s) => s.charts);

  const handleExport = async (id: string) => {
    try {
      const blob = await chartDB.exportChart(id);
      const chart = charts.find((c) => c.id === id);
      const name = chart?.name || 'chart';
      saveAs(blob, `${name.replace(/\s+/g, '_')}-${Date.now()}.savedchart`);
    } catch (e) {
      console.error('export failed', e);
      alert('导出失败');
    }
  };

  return (
    <div className="space-y-2">
      {charts.map((c) => (
        <div key={c.id} className="flex items-center justify-between">
          <div>{c.name}</div>
          <Button size="sm" variant="outline" onClick={() => handleExport(c.id)}>
            导出
          </Button>
        </div>
      ))}
    </div>
  );
}
