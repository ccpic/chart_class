/**
 * 画布和子图相关的 TypeScript 类型定义
 * 对应后端的 Pydantic 模型
 */

export type ChartType = "bar" | "line" | "pie" | "area" | "scatter";

export interface ChartData {
  columns: string[];
  index?: string[];
  data: any[][];
}

export interface SubplotConfig {
  subplotId: string;
  axIndex: number;
  chartType: ChartType;
  data: ChartData;
  params: Record<string, any>;
}

export interface CanvasConfig {
  width: number;
  height: number;
  rows: number;
  cols: number;
  wspace: number;
  hspace: number;

  // 画布级别样式
  title?: string;
  titleFontsize?: number;
  ytitle?: string;
  ytitleFontsize?: number;

  // 图例配置
  showLegend: boolean;
  legendLoc: string;
  legendNcol: number;
  bboxToAnchor: [number, number];

  // 其他设置
  labelOuter: boolean;

  style?: Record<string, any>;
}

export interface RenderRequest {
  canvas: CanvasConfig;
  subplots: SubplotConfig[];
}
