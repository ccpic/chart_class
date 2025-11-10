import type { Metadata } from 'next'
import './globals.css'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import AppSidebar from '@/components/layout/AppSidebar'
import { Toaster } from '@/components/ui/toaster'

export const metadata: Metadata = {
  title: 'Chart Class - 可视化工具',
  description: 'Web visualization tool for Chart Class library',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>
        <SidebarProvider>
          {/* 左侧：可折叠侧边栏 */}
          <AppSidebar />
          
          {/* 右侧：主内容区（水平布局容器） */}
          <SidebarInset className="flex h-screen overflow-hidden">
            {children}
          </SidebarInset>
        </SidebarProvider>
        <Toaster />
      </body>
    </html>
  )
}

