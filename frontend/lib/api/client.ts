/**
 * API 客户端工具
 * 统一处理 API 请求，自动添加 JWT Token
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export interface ApiError {
  detail: string;
  status: number;
}

/**
 * 获取认证头
 */
function getAuthHeaders(): HeadersInit {
  let token: string | null = null;

  if (typeof window !== "undefined") {
    try {
      // 从 localStorage 读取 auth-storage（Zustand persist 格式）
      const authStorage = localStorage.getItem("auth-storage");
      if (authStorage) {
        const parsed = JSON.parse(authStorage);
        // Zustand persist 的格式是 { state: { token: ..., user: ..., isAuthenticated: ... } }
        token = parsed?.state?.token || null;
      }
    } catch (error) {
      console.error("Failed to get token from localStorage:", error);
    }
  }

  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * 处理 API 响应
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      // 如果响应不是 JSON，使用默认错误信息
    }

    const error: ApiError = {
      detail: errorDetail,
      status: response.status,
    };

    throw error;
  }

  // 如果响应为空，返回空对象
  const contentType = response.headers.get("content-type");
  if (!contentType || !contentType.includes("application/json")) {
    return {} as T;
  }

  return response.json();
}

/**
 * GET 请求
 */
export async function apiGet<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return handleResponse<T>(response);
}

/**
 * POST 请求
 */
export async function apiPost<T>(endpoint: string, data?: any): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: data ? JSON.stringify(data) : undefined,
  });

  return handleResponse<T>(response);
}

/**
 * PUT 请求
 */
export async function apiPut<T>(endpoint: string, data?: any): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: data ? JSON.stringify(data) : undefined,
  });

  return handleResponse<T>(response);
}

/**
 * DELETE 请求
 */
export async function apiDelete<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  return handleResponse<T>(response);
}
