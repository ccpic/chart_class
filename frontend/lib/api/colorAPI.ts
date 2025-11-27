/**
 * 颜色管理 API 客户端
 * 提供前端调用后端颜色管理接口的方法
 * 使用统一的 API 客户端，自动添加 JWT Token
 */

import { apiGet, apiPost, apiPut, apiDelete } from "./client";

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
  /**
   * 获取所有颜色映射
   * @param search - 搜索关键词（可选）
   */
  async listColors(params?: { search?: string }): Promise<ColorMapping[]> {
    const query = new URLSearchParams();
    if (params?.search) query.append("search", params.search);

    const queryString = query.toString();
    const endpoint = `/api/colors${queryString ? `?${queryString}` : ""}`;

    return apiGet<ColorMapping[]>(endpoint);
  }

  /**
   * 获取指定颜色映射
   * @param name - 颜色名称
   */
  async getColor(name: string): Promise<ColorMapping> {
    return apiGet<ColorMapping>(`/api/colors/${encodeURIComponent(name)}`);
  }

  /**
   * 添加新颜色映射
   * @param color - 颜色配置
   */
  async createColor(color: ColorCreateRequest): Promise<MessageResponse> {
    return apiPost<MessageResponse>("/api/colors", color);
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
    return apiPut<MessageResponse>(
      `/api/colors/${encodeURIComponent(name)}`,
      updates
    );
  }

  /**
   * 删除颜色映射
   * @param name - 颜色名称
   */
  async deleteColor(name: string): Promise<MessageResponse> {
    return apiDelete<MessageResponse>(
      `/api/colors/${encodeURIComponent(name)}`
    );
  }

  /**
   * 获取统计信息
   */
  async getStats(): Promise<ColorStats> {
    return apiGet<ColorStats>("/api/colors/meta/stats");
  }

  /**
   * 获取全局调色板顺序
   */
  async getPalette(): Promise<string[]> {
    return apiGet<string[]>("/api/colors/palette");
  }

  /**
   * 更新调色板顺序
   */
  async updatePalette(palette: string[]): Promise<MessageResponse> {
    return apiPut<MessageResponse>("/api/colors/palette", { palette });
  }
}

// 单例实例
export const colorAPI = new ColorAPIClient();

// React Hook (可选)
export function useColorAPI() {
  return colorAPI;
}
