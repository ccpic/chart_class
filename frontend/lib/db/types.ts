import { CanvasConfig, SubplotConfig } from "@/types/canvas";

export interface SavedChart {
  id: string;
  name: string;
  thumbnail?: string;
  createdAt: number;
  updatedAt: number;
  tags?: string[];
  canvas: CanvasConfig;
  subplots: SubplotConfig[];
  version: string;
  /** 列表接口返回的子图数量（不包含完整 subplots 数据时使用） */
  subplotCount?: number;
}
