'use client';

import { useState } from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { TitleSection, GridSection, AxisSection, TicksSection, LegendSection } from './sections';
import type { PlotStyle } from '@/types/plotStyle';
import { Type, Grid3X3, Ruler, Hash, Tag } from 'lucide-react';

interface BaseStyleEditorProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
}

/**
 * 通用样式编辑器
 * 用于右侧边栏，提供标题、网格、坐标轴、刻度、图例的配置
 */
export function BaseStyleEditor({ style, onChange }: BaseStyleEditorProps) {
  // 默认展开标题分组
  const [openSections, setOpenSections] = useState<string[]>(['title']);

  return (
    <div className="space-y-2">
      <Accordion 
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
