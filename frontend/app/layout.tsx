import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Chart Class - MVP',
  description: 'Web visualization tool for Chart Class library',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}
