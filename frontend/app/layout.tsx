import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from '@/components/ui/toaster'
import AuthGuard from '@/components/auth/AuthGuard'
import ConditionalLayout from '@/components/layout/ConditionalLayout'

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

