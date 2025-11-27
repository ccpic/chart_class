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
}
