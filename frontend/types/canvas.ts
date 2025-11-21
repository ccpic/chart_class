/**
 * 画布和子图相关的 TypeScript 类型定义
 * 对应后端的 Pydantic 模型
 */

export type ChartType =
  | "bar"
  | "line"
  | "pie"
  | "area"
  | "bubble"
  | "table"
  | "hist" // 直方图
  | "boxdot"; // 箱型图

export interface ChartData {
  columns: string[];
  index?: string[];
  index_name?: string;
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

  // 子图宽高比例
  widthRatios?: number[];
  heightRatios?: number[];

  // 画布级别样式
  title?: string;
  titleFontsize?: number;
  ytitle?: string;
  ytitleFontsize?: number;
  fontsize?: number;

  // 图例配置
  showLegend: boolean;
  legendLoc: string;
  legendNcol: number;
  bboxToAnchor: [number, number];

  // 坐标轴共享
  sharex?: boolean;
  sharey?: boolean;

  // 其他设置
  labelOuter: boolean;
  dpi?: number;
  transparent?: boolean;

  style?: Record<string, any>;
}

export interface RenderRequest {
  canvas: CanvasConfig;
  subplots: SubplotConfig[];
}
