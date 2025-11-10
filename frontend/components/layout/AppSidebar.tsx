'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutGrid,
  BarChart3,
  LineChart,
  PieChart,
  AreaChart,
  ScatterChart,
  Settings,
  HelpCircle,
  ChevronRight,
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
} from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';

import { useCanvasStore } from '@/store/canvasStore';
import SubplotItem from '@/components/sidebar/SubplotItem';
import SampleDataButton from '@/components/canvas/SampleDataButton';
import CanvasToolbar from '@/components/canvas/CanvasToolbar';

/**
 * 全局侧边栏组件
 * 参考 shadcn/ui sidebar-07 设计
 * 特性：可折叠到图标，展示画布和子图层级结构
 */
export default function AppSidebar() {
  const pathname = usePathname();
  const { canvas, subplots } = useCanvasStore();

  return (
    <Sidebar collapsible="icon">
      {/* 顶部：应用标题和 Logo */}
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/canvas">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-black text-white">
                  <LayoutGrid className="size-4" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-semibold">Chart Class</span>
                  <span className="text-xs text-muted-foreground">
                    可视化工具
                  </span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      {/* 主内容：画布和子图 */}
      <SidebarContent>
        {/* 画布信息 */}
        <SidebarGroup>
          <SidebarGroupLabel>画布</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={pathname === '/canvas'}>
                  <Link href="/canvas">
                    <LayoutGrid className="size-4" />
                    <span>{canvas.title || '主画布'}</span>
                    <div className="ml-auto flex items-center gap-1 text-xs text-muted-foreground">
                      <span>{canvas.rows}×{canvas.cols}</span>
                      <ChevronRight className="size-3" />
                    </div>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* 子图列表 */}
        <SidebarGroup>
          <SidebarGroupLabel>
            子图 ({subplots.length})
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {subplots.length > 0 ? (
                subplots.map((subplot) => (
                  <SubplotItem
                    key={subplot.subplotId}
                    subplot={subplot}
                    isActive={pathname === `/subplot/${subplot.subplotId}`}
                  />
                ))
              ) : (
                <div className="px-2 py-4 text-center text-sm text-muted-foreground">
                  暂无子图
                  <div className="mt-1 text-xs">
                    点击画布网格添加
                  </div>
                </div>
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* 底部：工具栏 + 操作区 */}
      <SidebarFooter>
        {/* 工具栏：示例数据 + 保存/加载/重置 */}
        <div className="px-2 py-3 space-y-3">
          <div className="flex flex-col gap-2">
            <SampleDataButton />
          </div>
          <Separator />
          <CanvasToolbar />
        </div>
        
        <Separator />
        
        {/* 设置和帮助 */}
        <SidebarMenu>
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
