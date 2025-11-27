import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // 获取认证状态（从 localStorage 读取，但 middleware 在服务端运行，无法直接访问）
  // 所以这里只做路径检查，实际的认证检查在客户端组件中完成
  
  const { pathname } = request.nextUrl;
  
  // 登录页面不需要保护
  if (pathname.startsWith("/login")) {
    return NextResponse.next();
  }
  
  // 其他页面在客户端组件中检查认证状态
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * 匹配所有路径，除了：
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};

