'use client';

import React from 'react';

interface MainContentProps {
  children: React.ReactNode;
}

/**
 * 主内容区容器
 * 用于画布页面和子图页面的中间栏
 */
export default function MainContent({ children }: MainContentProps) {
  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      {children}
    </div>
  );
}
