'use client';

import Link from 'next/link';
import {
  LayoutGrid,
  Settings,
  HelpCircle,
} from 'lucide-react';

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarSeparator,
} from '@/components/ui/sidebar';

import { useCanvasStore } from '@/store/canvasStore';
import CanvasTreeView from '@/components/canvas/CanvasTreeView';
import ResetCanvasButton from '@/components/canvas/ResetCanvasButton';
import SaveChartDialog from '@/components/chart/SaveChartDialog';
import LoadChartSheet from '@/components/chart/LoadChartSheet';
import ChartImport from '@/components/chart/ChartImport';
import ColorManagerSheet from '@/components/color/ColorManagerSheet';

/**
 * 全局侧边栏组件
 * 使用 TreeView 展示画布和子图的层级结构
 */
export default function AppSidebar() {
  const subplots = useCanvasStore((state) => state.subplots);

  return (
    <Sidebar collapsible="icon">
      {/* 顶部：应用标题和 Logo */}
      <SidebarHeader className="group-data-[collapsible=icon]:items-center">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/canvas">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-black text-white">
                  <LayoutGrid className="size-4" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="text-lg font-semibold">Chart Class</span>
                  <span className="text-xs text-muted-foreground">
                    可视化工具
                  </span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      {/* 主内容：画布和子图树形结构 */}
      <SidebarContent className="group-data-[collapsible=icon]:items-center">
        <SidebarGroup>
          <SidebarGroupLabel className="group-data-[collapsible=icon]:text-center">
            画布结构 ({subplots.length} 个子图)
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <CanvasTreeView expandAll={true} className="p-2" />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* 底部：图表管理、重置按钮、设置和帮助 */}
      <SidebarFooter className="group-data-[collapsible=icon]:items-center">
        <SidebarMenu>
          <SidebarMenuItem>
            <ResetCanvasButton />
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SaveChartDialog />
          </SidebarMenuItem>
          <SidebarMenuItem>
            <LoadChartSheet />
          </SidebarMenuItem>
          <SidebarMenuItem>
            <ChartImport />
          </SidebarMenuItem>
          <SidebarSeparator />
          <SidebarMenuItem>
            <ColorManagerSheet />
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/settings">
                <Settings className="size-4" />
                <span>设置</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <a
                href="https://github.com/ccpic/chart_class"
                target="_blank"
                rel="noopener noreferrer"
              >
                <HelpCircle className="size-4" />
                <span>帮助文档</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      {/* 折叠触发器（鼠标悬停在边缘展开）*/}
      <SidebarRail />
    </Sidebar>
  );
}
