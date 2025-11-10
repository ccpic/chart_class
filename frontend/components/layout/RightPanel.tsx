'use client';

import React from 'react';

interface RightPanelProps {
  children: React.ReactNode;
}

/**
 * 右侧参数面板容器
 * 固定宽度 400px，用于显示配置参数
 */
export default function RightPanel({ children }: RightPanelProps) {
  return (
    <div className="w-[400px] border-l bg-white overflow-y-auto">
      {children}
    </div>
  );
}
