/**
 * Canvas 画布状态管理
 * 使用 Zustand 实现简洁的全局状态管理
 */

import { create } from "zustand";
import { CanvasConfig, SubplotConfig, ChartType } from "@/types/canvas";

interface CanvasStore {
  // 状态
  canvas: CanvasConfig;
  subplots: SubplotConfig[];
  selectedSubplotId: string | null;
  currentSubplotId: string | null; // 当前正在编辑的子图（用于路由同步）
  renderedImage: string | null; // 画布渲染结果
  renderError: string | null; // 渲染错误信息
  selectedPaletteName: string | null; // 当前选定的调色板名称（null 表示使用默认调色板）

  // Canvas Actions
  updateCanvas: (config: Partial<CanvasConfig>) => void;
  setSelectedPalette: (paletteName: string | null) => void; // 设置选定的调色板

  // Subplot Actions
  addSubplot: (axIndex: number, chartType?: ChartType) => void;
  updateSubplot: (subplotId: string, updates: Partial<SubplotConfig>) => void;
  updateSubplotData: (
    subplotId: string,
    data: { columns: string[]; data: any[][] }
  ) => void;
  deleteSubplot: (subplotId: string) => void;
  selectSubplot: (subplotId: string | null) => void;
  setCurrentSubplot: (subplotId: string | null) => void;

  // 渲染结果管理
  setRenderedImage: (imageUrl: string | null) => void;
  setRenderError: (error: string | null) => void;
  clearRenderResult: () => void;

  // 批量操作
  clearAllSubplots: () => void;
  duplicateSubplot: (subplotId: string, newAxIndex: number) => void;

  // 工具方法
  getSubplotByAxIndex: (axIndex: number) => SubplotConfig | undefined;
  getSubplotById: (subplotId: string) => SubplotConfig | undefined;
  getEmptyGridCells: () => number[];
  isDataComplete: (subplotId: string) => boolean;
  canRender: () => boolean;

  // 本地存储（可选）
  saveToLocalStorage: () => void;
  loadFromLocalStorage: () => void;

  // 从保存的图表加载
  loadFromSavedChart: (canvas: CanvasConfig, subplots: SubplotConfig[]) => void;

  // 重置
  reset: () => void;
}

const defaultCanvas: CanvasConfig = {
  width: 15,
  height: 6,
  rows: 1,
  cols: 1,
  wspace: 0.1,
  hspace: 0.1,
  fontsize: 14,
  showLegend: false,
  legendLoc: "center left",
  legendNcol: 1,
  bboxToAnchor: [1, 0.5],
  sharex: false,
  sharey: false,
  labelOuter: false,
  dpi: 400,
  transparent: true,
};

export const useCanvasStore = create<CanvasStore>((set, get) => ({
  canvas: { ...defaultCanvas },
  subplots: [],
  selectedSubplotId: null,
  currentSubplotId: null,
  renderedImage: null,
  renderError: null,
  selectedPaletteName: null, // 默认使用默认调色板

  updateCanvas: (config) =>
    set((state) => ({
      canvas: { ...state.canvas, ...config },
    })),

  setSelectedPalette: (paletteName) =>
    set({ selectedPaletteName: paletteName }),

  setRenderedImage: (imageUrl) =>
    set({ renderedImage: imageUrl, renderError: null }),

  setRenderError: (error) => set({ renderError: error, renderedImage: null }),

  clearRenderResult: () => set({ renderedImage: null, renderError: null }),

  addSubplot: (axIndex, chartType = "bar") => {
    // 根据图表类型设置默认参数
    let defaultParams = {};
    if (chartType === "bubble") {
      defaultParams = {
        alpha: 0.6,
        bubble_scale: 1,
        edgecolor: "black",
        random_color: false,
        show_reg: false,
        show_hist: false,
        corr: null,
        label_limit: 0,
        label_formatter: "{index}",
        x_avg: null,
        y_avg: null,
        avg_linestyle: "--",
        avg_linewidth: 1,
        avg_color: "gray",
      };
    } else if (chartType === "barh") {
      defaultParams = {
        stacked: true,
        show_label: true,
        label_formatter: "{abs}",
        label_threshold: 0.02,
        label_pos: "smart",
        bar_height: 0.8,
        fmt_abs: "{:,.0f}",
        fmt_share: "{:.1%}",
        fmt_gr: "{:+.1%}",
      };
    } else if (chartType === "funnel") {
      defaultParams = {
        size: null,
        height: 0.7,
        color: "navy",
        show_label: true,
        label_ha: "center",
        bbox: {
          boxstyle: "round,pad=0.5",
          facecolor: "grey",
          edgecolor: "black",
          linewidth: 1,
          alpha: 0.5,
        },
      };
    } else if (chartType === "waterfall") {
      defaultParams = {
        size: null,
        show_connector: true,
        connector_style: {
          color: "gray",
          linestyle: "--",
          linewidth: 1,
          alpha: 0.7,
        },
        show_label: true,
        label_formatter: "{abs}",
        label_pos: "top",
        positive_color: "green",
        negative_color: "red",
        bar_width: 0.8,
      };
    }

    const newSubplot: SubplotConfig = {
      subplotId: `subplot-${Date.now()}`,
      axIndex,
      chartType,
      data: {
        columns: [],
        data: [],
      },
      params: defaultParams,
    };
    set((state) => ({
      subplots: [...state.subplots, newSubplot],
      selectedSubplotId: newSubplot.subplotId,
    }));
  },

  updateSubplot: (subplotId, updates) =>
    set((state) => ({
      subplots: state.subplots.map((subplot) =>
        subplot.subplotId === subplotId ? { ...subplot, ...updates } : subplot
      ),
    })),

  updateSubplotData: (subplotId, data) =>
    set((state) => ({
      subplots: state.subplots.map((subplot) =>
        subplot.subplotId === subplotId ? { ...subplot, data } : subplot
      ),
    })),

  deleteSubplot: (subplotId) =>
    set((state) => ({
      subplots: state.subplots.filter((s) => s.subplotId !== subplotId),
      selectedSubplotId:
        state.selectedSubplotId === subplotId ? null : state.selectedSubplotId,
      currentSubplotId:
        state.currentSubplotId === subplotId ? null : state.currentSubplotId,
    })),

  selectSubplot: (subplotId) => set({ selectedSubplotId: subplotId }),

  setCurrentSubplot: (subplotId) => set({ currentSubplotId: subplotId }),

  clearAllSubplots: () =>
    set({
      subplots: [],
      selectedSubplotId: null,
      currentSubplotId: null,
    }),

  duplicateSubplot: (subplotId, newAxIndex) => {
    const state = get();
    const original = state.subplots.find((s) => s.subplotId === subplotId);
    if (!original) return;

    const duplicated: SubplotConfig = {
      ...original,
      subplotId: `subplot-${Date.now()}`,
      axIndex: newAxIndex,
    };
    set((state) => ({
      subplots: [...state.subplots, duplicated],
    }));
  },

  getSubplotByAxIndex: (axIndex) => {
    const state = get();
    return state.subplots.find((s) => s.axIndex === axIndex);
  },

  getSubplotById: (subplotId) => {
    const state = get();
    return state.subplots.find((s) => s.subplotId === subplotId);
  },

  getEmptyGridCells: () => {
    const state = get();
    const total = state.canvas.rows * state.canvas.cols;
    const occupied = state.subplots.map((s) => s.axIndex);
    const empty: number[] = [];
    for (let i = 0; i < total; i++) {
      if (!occupied.includes(i)) {
        empty.push(i);
      }
    }
    return empty;
  },

  isDataComplete: (subplotId) => {
    const state = get();
    const subplot = state.subplots.find((s) => s.subplotId === subplotId);
    if (!subplot) return false;
    return subplot.data.columns.length > 0 && subplot.data.data.length > 0;
  },

  canRender: () => {
    const state = get();
    return (
      state.subplots.length > 0 &&
      state.subplots.every(
        (s) => s.data.columns.length > 0 && s.data.data.length > 0
      )
    );
  },

  saveToLocalStorage: () => {
    const state = get();
    try {
      localStorage.setItem(
        "chart-class-canvas",
        JSON.stringify({
          canvas: state.canvas,
          subplots: state.subplots,
        })
      );
    } catch (error) {
      console.error("Failed to save to localStorage:", error);
    }
  },

  loadFromLocalStorage: () => {
    try {
      const saved = localStorage.getItem("chart-class-canvas");
      if (saved) {
        const { canvas, subplots } = JSON.parse(saved);
        set({ canvas, subplots });
      }
    } catch (error) {
      console.error("Failed to load from localStorage:", error);
    }
  },

  loadFromSavedChart: (canvas, subplots) => {
    set({
      canvas,
      subplots,
      selectedSubplotId: null,
      currentSubplotId: null,
      renderedImage: null,
      renderError: null,
    });
  },

  reset: () => {
    set({
      canvas: { ...defaultCanvas },
      subplots: [],
      selectedSubplotId: null,
      currentSubplotId: null,
      selectedPaletteName: null,
    });
    // 同时清除本地存储
    try {
      localStorage.removeItem("chart-class-canvas");
    } catch (error) {
      console.error("Failed to clear localStorage:", error);
    }
  },
}));
