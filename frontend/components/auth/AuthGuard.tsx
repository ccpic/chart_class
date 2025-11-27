"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

/**
 * 认证保护组件
 * 如果 requireAuth 为 true，未登录用户将被重定向到登录页
 */
export default function AuthGuard({ children, requireAuth = true }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, token, fetchUserInfo } = useAuthStore();

  useEffect(() => {
    // 登录页面和管理员登录页面不需要认证
    if (pathname === "/login" || pathname === "/admin/login") {
      return;
    }

    if (requireAuth) {
      // 如果未认证，尝试从 localStorage 恢复 token
      if (!isAuthenticated) {
        const authStorage = localStorage.getItem("auth-storage");
        if (authStorage) {
          try {
            const parsed = JSON.parse(authStorage);
            if (parsed.state?.token) {
              // 有 token，尝试获取用户信息验证 token 是否有效
              fetchUserInfo()
                .then(() => {
                  // Token 有效，继续访问
                })
                .catch(() => {
                  // Token 无效，跳转到登录页
                  router.replace("/login");
                });
              return;
            }
          } catch {
            // 解析失败，清除无效数据
            localStorage.removeItem("auth-storage");
          }
        }
        // 未登录，跳转到登录页
        router.replace("/login");
      }
    }
  }, [isAuthenticated, token, pathname, router, requireAuth, fetchUserInfo]);

  // 如果是登录页面，直接渲染
  if (pathname === "/login" || pathname === "/admin/login") {
    return <>{children}</>;
  }

  // 如果需要认证但未认证，显示加载中
  if (requireAuth && !isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-gray-600">正在验证身份...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

