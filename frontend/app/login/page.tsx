"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function LoginPage() {
  const router = useRouter();
  const { login, register, isLoading, isAuthenticated } = useAuthStore();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);

  // 如果已登录，重定向到画布页面
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/canvas");
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      if (isLoginMode) {
        await login(username, password);
      } else {
        await register(username, password, email || undefined);
      }
      // 登录/注册成功后，authStore 会自动更新状态
      router.push("/canvas");
    } catch (err: any) {
      setError(err.message || "操作失败，请重试");
    }
  };

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{isLoginMode ? "登录" : "注册"}</CardTitle>
          <CardDescription>
            {isLoginMode
              ? "请输入您的用户名和密码"
              : "创建新账户"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">用户名</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={isLoading}
                placeholder="请输入用户名"
              />
            </div>

            {!isLoginMode && (
              <div className="space-y-2">
                <Label htmlFor="email">邮箱（可选）</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  placeholder="请输入邮箱"
                />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="password">密码</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                placeholder="请输入密码"
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading
                ? "处理中..."
                : isLoginMode
                ? "登录"
                : "注册"}
            </Button>
          </form>

          <div className="mt-4 text-center text-sm">
            {isLoginMode ? (
              <span>
                还没有账户？{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsLoginMode(false);
                    setError(null);
                  }}
                  className="text-blue-600 hover:underline"
                >
                  立即注册
                </button>
              </span>
            ) : (
              <span>
                已有账户？{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsLoginMode(true);
                    setError(null);
                  }}
                  className="text-blue-600 hover:underline"
                >
                  立即登录
                </button>
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

