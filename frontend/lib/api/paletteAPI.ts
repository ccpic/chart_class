/**
 * 调色板管理 API 客户端
 * 提供前端调用后端调色板管理接口的方法
 * 使用统一的 API 客户端，自动添加 JWT Token
 */

import { apiGet, apiPost, apiPut, apiDelete } from "./client";

export interface Palette {
  id: number;
  name: string;
  is_default: boolean;
  colors: string[]; // 颜色值列表（HEX 或命名颜色）
  color_count: number;
  created_at: string;
  updated_at: string;
}

export interface PaletteListItem {
  id: number;
  name: string;
  is_default: boolean;
  color_count: number;
  created_at: string;
  updated_at: string;
}

export interface PaletteUpdateRequest {
  colors: string[]; // 颜色值列表（HEX 或命名颜色）
}

export interface PaletteCreateRequest {
  name: string;
  colors: string[]; // 颜色值列表（HEX 或命名颜色）
}

export interface MessageResponse {
  message: string;
  success: boolean;
}

class PaletteAPIClient {
  /**
   * 获取所有调色板（列表视图）
   */
  async listPalettes(): Promise<PaletteListItem[]> {
    return apiGet<PaletteListItem[]>("/api/palettes");
  }

  /**
   * 获取默认调色板（颜色值列表）
   */
  async getDefaultPalette(): Promise<string[]> {
    return apiGet<string[]>("/api/palettes/default");
  }

  /**
   * 更新默认调色板
   * @param colors - 颜色值列表（HEX 或命名颜色，按顺序）
   */
  async updateDefaultPalette(
    colors: string[]
  ): Promise<MessageResponse> {
    return apiPut<MessageResponse>("/api/palettes/default", {
      colors: colors,
    });
  }

  /**
   * 获取指定调色板
   * @param name - 调色板名称
   */
  async getPalette(name: string): Promise<Palette> {
    return apiGet<Palette>(`/api/palettes/${encodeURIComponent(name)}`);
  }

  /**
   * 创建新调色板
   * @param palette - 调色板配置
   */
  async createPalette(
    palette: PaletteCreateRequest
  ): Promise<Palette> {
    return apiPost<Palette>("/api/palettes", palette);
  }

  /**
   * 更新调色板
   * @param name - 调色板名称
   * @param updates - 更新内容（包含颜色值列表）
   */
  async updatePalette(
    name: string,
    updates: PaletteUpdateRequest
  ): Promise<MessageResponse> {
    return apiPut<MessageResponse>(
      `/api/palettes/${encodeURIComponent(name)}`,
      updates
    );
  }

  /**
   * 删除调色板（不能删除默认调色板）
   * @param name - 调色板名称
   */
  async deletePalette(name: string): Promise<MessageResponse> {
    return apiDelete<MessageResponse>(
      `/api/palettes/${encodeURIComponent(name)}`
    );
  }
}

// 单例实例
export const paletteAPI = new PaletteAPIClient();

// React Hook (可选)
export function usePaletteAPI() {
  return paletteAPI;
}

