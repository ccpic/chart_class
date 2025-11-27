'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  LayoutGrid,
  Users,
  User,
  LogOut,
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
import { useChartStore } from '@/store/chartStore';
import { useAuthStore } from '@/store/authStore';
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
  const router = useRouter();
  const subplots = useCanvasStore((state) => state.subplots);
  const { currentChart, currentChartId } = useChartStore();
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

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
          {/* 当前图表名称 */}
          <div className="px-2 py-2 border-b group-data-[collapsible=icon]:px-2">
            <div className="text-xs text-muted-foreground mb-1 group-data-[collapsible=icon]:text-center">
              当前图表
            </div>
            <div className="text-sm font-medium truncate group-data-[collapsible=icon]:text-center" title={currentChart?.name || '未保存图表'}>
              {currentChartId && currentChart ? currentChart.name : '未保存图表'}
            </div>
          </div>
          
          <SidebarGroupLabel className="group-data-[collapsible=icon]:text-center">
            画布结构 ({subplots.length} 个子图)
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <CanvasTreeView expandAll={true} className="p-2" />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* 底部：图表管理、重置按钮 */}
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
          <SidebarMenuItem>
            <ColorManagerSheet />
          </SidebarMenuItem>
          
          {/* 超级管理员显示用户管理链接 */}
          {isAuthenticated && user && (user.role === "superadmin" || user.role === "admin") && (
            <SidebarMenuItem>
              <SidebarMenuButton asChild>
                <Link href="/admin/users">
                  <Users className="size-4" />
                  <span>用户管理</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}

          {/* 当前用户信息 - 放在最底部 */}
          {isAuthenticated && user && (
            <>
              <SidebarSeparator />
              <SidebarMenuItem>
                <div className="px-2 py-2 group-data-[collapsible=icon]:px-2">
                  <div className="flex items-center gap-2 group-data-[collapsible=icon]:justify-center">
                    <User className="size-4 text-muted-foreground" />
                    <div className="flex-1 min-w-0 group-data-[collapsible=icon]:hidden">
                      <div className="text-xs text-muted-foreground mb-1">当前用户</div>
                      <span className="text-sm font-medium truncate">{user.username}</span>
                    </div>
                  </div>
                </div>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton onClick={handleLogout}>
                  <LogOut className="size-4" />
                  <span>退出登录</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </>
          )}
        </SidebarMenu>
      </SidebarFooter>

      {/* 折叠触发器（鼠标悬停在边缘展开）*/}
      <SidebarRail />
    </Sidebar>
  );
}
