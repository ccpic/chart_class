'use client';

import { useState } from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { TitleSection, GridSection, AxisSection, TicksSection, LegendSection, BorderSection } from './sections';
import type { PlotStyle } from '@/types/plotStyle';
import { Type, Grid3X3, Ruler, Hash, Tag, Square } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';

interface BaseStyleEditorProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
  hasSecondaryAxis?: boolean;
}

/**
 * 通用样式编辑器
 * 用于右侧边栏，提供标题、网格、坐标轴、刻度、图例的配置
 */
export function BaseStyleEditor({ style, onChange, hasSecondaryAxis }: BaseStyleEditorProps) {
  // 默认展开标题分组
  const [openSections, setOpenSections] = useState<string>('title');

  return (
    <div className="space-y-2">
      <Accordion 
        type="single"
        value={openSections} 
        onValueChange={setOpenSections}
        className="space-y-2"
      >
        {/* 标题 */}
        <AccordionItem value="title" className="border rounded-md overflow-hidden">
          <AccordionTrigger className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-sm font-medium">
            <div className="flex items-center gap-2">
              <Type className="h-4 w-4" />
              <span>标题</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 py-3 bg-white border-t">
            <TitleSection style={style} onChange={onChange} />
          </AccordionContent>
        </AccordionItem>

        {/* 网格 */}
        <AccordionItem value="grid" className="border rounded-md overflow-hidden">
          <AccordionTrigger className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-sm font-medium">
            <div className="flex items-center gap-2">
              <Grid3X3 className="h-4 w-4" />
              <span>网格线</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 py-3 bg-white border-t">
            <GridSection style={style} onChange={onChange} />
          </AccordionContent>
        </AccordionItem>

        {/* 坐标轴 */}
        <AccordionItem value="axis" className="border rounded-md overflow-hidden">
          <AccordionTrigger className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-sm font-medium">
            <div className="flex items-center gap-2">
              <Ruler className="h-4 w-4" />
              <span>坐标轴</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 py-3 bg-white border-t">
            <AxisSection style={style} onChange={onChange} />
          </AccordionContent>
        </AccordionItem>

        {/* 次坐标轴（仅当存在次轴时显示） */}
        {hasSecondaryAxis && (
          <AccordionItem value="secondaryAxis" className="border rounded-md overflow-hidden">
            <AccordionTrigger className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-sm font-medium">
              <div className="flex items-center gap-2">
                <Ruler className="h-4 w-4" />
                <span>次坐标轴 (Y2)</span>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-3 py-3 bg-white border-t">
              <SecondaryAxisSection style={style} onChange={onChange} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* 刻度 */}
        <AccordionItem value="ticks" className="border rounded-md overflow-hidden">
          <AccordionTrigger className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-sm font-medium">
            <div className="flex items-center gap-2">
              <Hash className="h-4 w-4" />
              <span>刻度</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 py-3 bg-white border-t">
            <TicksSection style={style} onChange={onChange} />
          </AccordionContent>
        </AccordionItem>

        {/* 边框 */}
        <AccordionItem value="border" className="border rounded-md overflow-hidden">
          <AccordionTrigger className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-sm font-medium">
            <div className="flex items-center gap-2">
              <Square className="h-4 w-4" />
              <span>边框</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 py-3 bg-white border-t">
            <BorderSection style={style} onChange={onChange} />
          </AccordionContent>
        </AccordionItem>

        {/* 图例 */}
        <AccordionItem value="legend" className="border rounded-md overflow-hidden">
          <AccordionTrigger className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-sm font-medium">
            <div className="flex items-center gap-2">
              <Tag className="h-4 w-4" />
              <span>图例</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 py-3 bg-white border-t">
            <LegendSection style={style} onChange={onChange} />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}

function SecondaryAxisSection({ style, onChange }: { style: PlotStyle; onChange: (updates: Partial<PlotStyle>) => void }) {
  const y2Min = style.y2lim?.[0] ?? '';
  const y2Max = style.y2lim?.[1] ?? '';

  const updateY2Lim = (index: 0 | 1, value: string) => {
    const newLim: [number | null, number | null] = [...(style.y2lim || [null, null])];
    newLim[index] = value === '' ? null : parseFloat(value);
    onChange({ y2lim: newLim });
  };

  return (
    <div className="space-y-3">
      {/* Y2 轴标题和字体 */}
      <div className="space-y-1.5">
        <div className="grid grid-cols-5 gap-2 items-end">
          <div className="col-span-4 space-y-1.5">
            <Label htmlFor="y2label" className="text-xs font-medium text-gray-700">
              次轴标题
            </Label>
            <Input
              id="y2label"
              value={style.y2label || ''}
              onChange={(e) => onChange({ y2label: e.target.value })}
              placeholder="Y2 轴标题"
              className="h-8 text-sm"
            />
          </div>
          <div className="col-span-1 space-y-1.5">
            <Label htmlFor="y2label-fontsize" className="text-xs font-medium text-gray-700">
              字号
            </Label>
            <Input
              id="y2label-fontsize"
              type="number"
              value={style.y2label_fontsize || 14}
              onChange={(e) => onChange({ y2label_fontsize: Number(e.target.value) })}
              min={8}
              max={24}
              className="h-8 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Y2 轴范围 */}
      <div className="space-y-1.5">
        <Label className="text-xs font-medium text-gray-700">轴范围</Label>
        <div className="grid grid-cols-2 gap-2">
          <Input
            type="number"
            value={y2Min}
            onChange={(e) => updateY2Lim(0, e.target.value)}
            placeholder="最小值"
            className="h-8 text-sm"
          />
          <Input
            type="number"
            value={y2Max}
            onChange={(e) => updateY2Lim(1, e.target.value)}
            placeholder="最大值"
            className="h-8 text-sm"
          />
        </div>
        <p className="text-xs text-gray-500">留空为自动</p>
      </div>

      {/* 隐藏整体 Y2 轴 */}
      <div className="flex items-center space-x-2 pt-2">
        <Checkbox
          id="hide_y2axis"
          checked={style.hide_y2axis ?? false}
          onCheckedChange={(checked) => onChange({ hide_y2axis: !!checked })}
        />
        <Label htmlFor="hide_y2axis" className="text-sm cursor-pointer">
          隐藏整体次坐标轴
        </Label>
      </div>
    </div>
  );
}
