/**
 * 图表样式参数类型定义
 * 对应后端 chart/plots/base.py::Plot.Style
 */

/**
 * 网格配置
 */
export interface GridConfig {
  axis?: "both" | "x" | "y";
  linestyle?: string;
  alpha?: number;
}

/**
 * 图表通用样式参数
 */
export interface PlotStyle {
  // ===== 标题 =====
  title?: string;
  title_fontsize?: number;
  title_y?: number; // 标题垂直位置 (0.0-1.2, 默认1.0)
  title_loc?: "left" | "center" | "right";

  // ===== 网格 =====
  major_grid?: GridConfig | null;
  minor_grid?: GridConfig | null;

  // ===== 坐标轴 =====
  xlabel?: string;
  ylabel?: string;
  xlabel_fontsize?: number | null;
  ylabel_fontsize?: number | null;
  xlim?: [number | null, number | null] | null;
  ylim?: [number | null, number | null] | null;
  hide_top_right_spines?: boolean;

  // ===== 刻度 =====
  all_xticks?: boolean;
  xticklabel_fontsize?: number | null;
  yticklabel_fontsize?: number | null;
  xticklabel_rotation?: number | null;
  yticklabel_rotation?: number | null;
  remove_xticks?: boolean;
  remove_yticks?: boolean;
  xticks_interval?: number | null;
  yticks_interval?: number | null;

  // ===== 图例 =====
  show_legend?: boolean;
  legend_loc?: string;
  legend_ncol?: number;
  legend_bbox_to_anchor?: [number, number] | null;

  // ===== 其他通用参数 =====
  fontsize?: number;
  fmt?: string;
  color_dict?: Record<string, string>;
  focus?: string[];
  hue?: string;
}

/**
 * 气泡图特有参数
 */
export interface BubbleSpecificParams {
  // 基础参数
  bubble_scale?: number;
  alpha?: number;
  edgecolor?: string | { hex: string; name?: string };

  // 统计参数
  show_reg?: boolean;
  corr?: boolean;
  show_hist?: boolean;

  // 参考线参数
  x_avg?: boolean;
  y_avg?: boolean;
  avg_color?: string | { hex: string; name?: string };
  avg_width?: number;

  // 标签参数
  limit_label?: number | null;

  // 数值格式化
  x_fmt?: string;
  y_fmt?: string;
}

/**
 * 完整的子图参数（样式 + 特有参数）
 */
export interface SubplotParams {
  style: PlotStyle;
  specific?: BubbleSpecificParams; // 根据图表类型，可以是 BubbleSpecificParams | BarSpecificParams | ...
}
