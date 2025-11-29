import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from '@/components/ui/toaster'
import AuthGuard from '@/components/auth/AuthGuard'
import ConditionalLayout from '@/components/layout/ConditionalLayout'

export const metadata: Metadata = {
  title: 'Chart Class2 - 画图助手',
  description: 'Next.js前端控制后端Matplotlib绘图库的Web可视化工具',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>
        <AuthGuard>
          <ConditionalLayout>
            {children}
          </ConditionalLayout>
        </AuthGuard>
        <Toaster />
      </body>
    </html>
  )
}

