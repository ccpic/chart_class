'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // 自动重定向到多子图画布页面
    router.replace('/canvas');
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <p className="text-gray-600">正在跳转到画布编辑器...</p>
      </div>
    </div>
  );
}
