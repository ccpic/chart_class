"use client";

import { usePathname } from "next/navigation";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import AppSidebar from "@/components/layout/AppSidebar";

interface ConditionalLayoutProps {
  children: React.ReactNode;
}

/**
 * 条件布局组件
 * 登录页面不显示侧边栏，占据全屏
 * 其他页面显示侧边栏
 */
export default function ConditionalLayout({ children }: ConditionalLayoutProps) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login" || pathname === "/admin/login";

  if (isLoginPage) {
    // 登录页面：全屏布局，不显示侧边栏
    return <>{children}</>;
  }

  // 其他页面：显示侧边栏
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="flex h-screen overflow-hidden">
        {children}
      </SidebarInset>
    </SidebarProvider>
  );
}

