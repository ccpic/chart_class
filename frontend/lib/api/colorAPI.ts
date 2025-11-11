/**
 * 颜色管理 API 客户端
 * 提供前端调用后端颜色管理接口的方法
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_COLOR_API_URL || "http://localhost:8000";

export interface ColorMapping {
  name: string;
  color: string; // 永远是 HEX 值
  named_color?: string; // 可选的 matplotlib 命名颜色
}

export interface ColorCreateRequest {
  name: string;
  color: string;
  named_color?: string;
  overwrite?: boolean;
}

export interface ColorUpdateRequest {
  color?: string;
  named_color?: string | null; // 支持更新命名颜色，null 表示清除
}

export interface MessageResponse {
  message: string;
  success: boolean;
}

export interface ColorStats {
  total_colors: number;
}

class ColorAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API 请求失败 [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * 获取所有颜色映射
   * @param search - 搜索关键词（可选）
   */
  async listColors(params?: { search?: string }): Promise<ColorMapping[]> {
    const query = new URLSearchParams();
    if (params?.search) query.append("search", params.search);

    const queryString = query.toString();
    const endpoint = `/api/colors${queryString ? `?${queryString}` : ""}`;

    return this.request<ColorMapping[]>(endpoint);
  }

  /**
   * 获取指定颜色映射
   * @param name - 颜色名称
   */
  async getColor(name: string): Promise<ColorMapping> {
    return this.request<ColorMapping>(
      `/api/colors/${encodeURIComponent(name)}`
    );
  }

  /**
   * 添加新颜色映射
   * @param color - 颜色配置
   */
  async createColor(color: ColorCreateRequest): Promise<MessageResponse> {
    return this.request<MessageResponse>("/api/colors", {
      method: "POST",
      body: JSON.stringify(color),
    });
  }

  /**
   * 更新颜色映射
   * @param name - 颜色名称
   * @param updates - 更新内容
   */
  async updateColor(
    name: string,
    updates: ColorUpdateRequest
  ): Promise<MessageResponse> {
    return this.request<MessageResponse>(
      `/api/colors/${encodeURIComponent(name)}`,
      {
        method: "PUT",
        body: JSON.stringify(updates),
      }
    );
  }

  /**
   * 删除颜色映射
   * @param name - 颜色名称
   */
  async deleteColor(name: string): Promise<MessageResponse> {
    return this.request<MessageResponse>(
      `/api/colors/${encodeURIComponent(name)}`,
      {
        method: "DELETE",
      }
    );
  }

  /**
   * 获取统计信息
   */
  async getStats(): Promise<ColorStats> {
    return this.request<ColorStats>("/api/colors/meta/stats");
  }

  /**
   * 导出为 TypeScript 文件
   * @param outputPath - 输出路径
   */
  async exportToTypeScript(outputPath?: string): Promise<MessageResponse> {
    const query = outputPath
      ? `?output_path=${encodeURIComponent(outputPath)}`
      : "";
    return this.request<MessageResponse>(
      `/api/colors/export/typescript${query}`,
      {
        method: "POST",
      }
    );
  }
}

// 单例实例
export const colorAPI = new ColorAPIClient();

// React Hook (可选)
export function useColorAPI() {
  return colorAPI;
}
