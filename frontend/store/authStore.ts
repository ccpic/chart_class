/**
 * 用户认证状态管理
 * 使用 Zustand 管理用户登录状态和 JWT Token
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: number;
  username: string;
  email?: string;
  role: string;
}

interface AuthStore {
  // 状态
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // 操作
  login: (username: string, password: string) => Promise<void>;
  register: (
    username: string,
    password: string,
    email?: string
  ) => Promise<void>;
  logout: () => void;
  fetchUserInfo: () => Promise<void>;
  setToken: (token: string) => void;
  clearAuth: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "登录失败");
          }

          const data = await response.json();

          // 确保数据格式正确
          if (!data.access_token) {
            throw new Error("登录响应格式错误：缺少 access_token");
          }

          if (!data.user) {
            throw new Error("登录响应格式错误：缺少 user");
          }

          set({
            token: data.access_token,
            user: data.user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (username: string, password: string, email?: string) => {
        set({ isLoading: true });
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password, email }),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "注册失败");
          }

          const data = await response.json();
          set({
            token: data.access_token,
            user: data.user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      fetchUserInfo: async () => {
        const { token } = get();
        if (!token) {
          return;
        }

        set({ isLoading: true });
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            // Token 可能已过期
            if (response.status === 401) {
              get().clearAuth();
            }
            throw new Error("获取用户信息失败");
          }

          const user = await response.json();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          // 如果获取失败，清除认证状态
          get().clearAuth();
        }
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
        // 设置 token 后自动获取用户信息
        get().fetchUserInfo();
      },

      clearAuth: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },
    }),
    {
      name: "auth-storage", // localStorage key
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
