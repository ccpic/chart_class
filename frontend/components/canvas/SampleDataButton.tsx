'use client';

import { Lightbulb } from 'lucide-react';
import { useCanvasStore } from '@/store/canvasStore';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

/**
 * 示例数据生成器
 * 快速生成示例画布用于测试
 */
export default function SampleDataButton() {
  const { updateCanvas, addSubplot, updateSubplot, clearAllSubplots } = useCanvasStore();
  const { toast } = useToast();

  const generateSampleData = () => {
    // 清空现有子图
    clearAllSubplots();

    // 设置 2x2 画布
    updateCanvas({ rows: 2, cols: 2 });

    // 生成4个示例子图
    const sampleSubplots = [
      {
        axIndex: 0,
        chartType: 'bar' as const,
        data: {
          columns: ['品牌A', '品牌B', '品牌C'],
          index: ['Q1', 'Q2', 'Q3'],
          data: [
            [100, 200, 150],
            [180, 220, 190],
            [150, 180, 170]
          ]
        },
        params: { stacked: true, show_label: true }
      },
      {
        axIndex: 1,
        chartType: 'line' as const,
        data: {
          columns: ['产品X', '产品Y'],
          index: ['2024-01', '2024-02', '2024-03', '2024-04'],
          data: [
            [50, 80],
            [70, 95],
            [85, 110],
            [95, 120]
          ]
        },
        params: {}
      },
      {
        axIndex: 2,
        chartType: 'pie' as const,
        data: {
          columns: ['类别A', '类别B', '类别C', '类别D'],
          index: ['总计'],
          data: [[300, 200, 150, 100]]
        },
        params: {}
      },
      {
        axIndex: 3,
        chartType: 'area' as const,
        data: {
          columns: ['指标1', '指标2'],
          index: ['周一', '周二', '周三', '周四'],
          data: [
            [40, 60],
            [55, 75],
            [70, 90],
            [80, 100]
          ]
        },
        params: {}
      }
    ];

    // 延迟添加以确保状态更新
    setTimeout(() => {
      sampleSubplots.forEach(subplot => {
        addSubplot(subplot.axIndex, subplot.chartType);
      });
      
      // 再次延迟更新数据
      setTimeout(() => {
        const state = useCanvasStore.getState();
        state.subplots.forEach((sp, index) => {
          if (index < sampleSubplots.length) {
            updateSubplot(sp.subplotId, {
              data: sampleSubplots[index].data,
              params: sampleSubplots[index].params
            });
          }
        });
        toast({
          title: '示例数据已生成',
          description: '包含 4 个子图（柱状图、折线图、饼图、面积图）',
        });
      }, 100);
    }, 50);
  };

  return (
    <Button
      onClick={generateSampleData}
      variant="default"
      size="sm"
      className="w-full justify-start gap-2 bg-blue-600 hover:bg-blue-700"
    >
      <Lightbulb className="h-4 w-4" />
      <span>生成示例数据</span>
    </Button>
  );
}
