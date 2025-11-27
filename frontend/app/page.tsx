'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    // AuthGuard 会处理认证检查，这里只需要重定向
    if (isAuthenticated) {
      router.replace('/canvas');
    } else {
      router.replace('/login');
    }
  }, [router, isAuthenticated]);

  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <p className="text-gray-600">正在跳转...</p>
      </div>
    </div>
  );
}
