/**
 * Canvas 画布状态管理
 * 使用 Zustand 实现简洁的全局状态管理
 * 使用 persist 中间件自动持久化到 localStorage
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
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
  cloneSubplotConfig: (sourceSubplotId: string, targetAxIndex: number) => void;
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

export const useCanvasStore = create<CanvasStore>()(
  persist(
    (set, get) => ({
      canvas: { ...defaultCanvas },
      subplots: [],
      selectedSubplotId: null,
      currentSubplotId: null,
      renderedImage: null,
      renderError: null,
      selectedPaletteName: null, // 默认使用默认调色板

  updateCanvas: (config) =>
    set((state) => {
      const newCanvas = { ...state.canvas, ...config };
      
      // 如果 rows 或 cols 改变了，自动调整 widthRatios 和 heightRatios 数组长度
      if ('rows' in config || 'cols' in config) {
        const newRows = config.rows ?? newCanvas.rows;
        const newCols = config.cols ?? newCanvas.cols;
        
        // 调整 heightRatios 数组长度以匹配新的行数
        if ('rows' in config) {
          const currentHeightRatios = newCanvas.heightRatios || Array(newCanvas.rows).fill(1);
          if (currentHeightRatios.length !== newRows) {
            if (currentHeightRatios.length > newRows) {
              // 如果新行数更少，截断数组
              newCanvas.heightRatios = currentHeightRatios.slice(0, newRows);
            } else {
              // 如果新行数更多，用默认值 1 填充
              newCanvas.heightRatios = [
                ...currentHeightRatios,
                ...Array(newRows - currentHeightRatios.length).fill(1),
              ];
            }
          }
        }
        
        // 调整 widthRatios 数组长度以匹配新的列数
        if ('cols' in config) {
          const currentWidthRatios = newCanvas.widthRatios || Array(newCanvas.cols).fill(1);
          if (currentWidthRatios.length !== newCols) {
            if (currentWidthRatios.length > newCols) {
              // 如果新列数更少，截断数组
              newCanvas.widthRatios = currentWidthRatios.slice(0, newCols);
            } else {
              // 如果新列数更多，用默认值 1 填充
              newCanvas.widthRatios = [
                ...currentWidthRatios,
                ...Array(newCols - currentWidthRatios.length).fill(1),
              ];
            }
          }
        }
      }
      
      return { canvas: newCanvas };
    }),

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

  cloneSubplotConfig: (sourceSubplotId, targetAxIndex) => {
    const state = get();
    const sourceSubplot = state.subplots.find((s) => s.subplotId === sourceSubplotId);
    if (!sourceSubplot) return;

    // 检查目标位置是否已有子图
    const existingSubplot = state.subplots.find((s) => s.axIndex === targetAxIndex);
    
    if (existingSubplot) {
      // 如果目标位置已有子图，覆盖其配置
      const clonedConfig: Partial<SubplotConfig> = {
        chartType: sourceSubplot.chartType,
        data: {
          columns: [...sourceSubplot.data.columns],
          index: sourceSubplot.data.index ? [...sourceSubplot.data.index] : undefined,
          index_name: sourceSubplot.data.index_name,
          data: sourceSubplot.data.data.map(row => [...row]),
        },
        params: JSON.parse(JSON.stringify(sourceSubplot.params)), // 深拷贝 params
      };
      
      set((state) => ({
        subplots: state.subplots.map((s) =>
          s.subplotId === existingSubplot.subplotId
            ? { ...s, ...clonedConfig }
            : s
        ),
        selectedSubplotId: existingSubplot.subplotId,
      }));
    } else {
      // 如果目标位置没有子图，创建新的子图
      const clonedSubplot: SubplotConfig = {
        subplotId: `subplot-${Date.now()}`,
        axIndex: targetAxIndex,
        chartType: sourceSubplot.chartType,
        data: {
          columns: [...sourceSubplot.data.columns],
          index: sourceSubplot.data.index ? [...sourceSubplot.data.index] : undefined,
          index_name: sourceSubplot.data.index_name,
          data: sourceSubplot.data.data.map(row => [...row]),
        },
        params: JSON.parse(JSON.stringify(sourceSubplot.params)), // 深拷贝 params
      };

      set((state) => ({
        subplots: [...state.subplots, clonedSubplot],
        selectedSubplotId: clonedSubplot.subplotId,
      }));
    }
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
  },
    }),
    {
      name: "chart-class-canvas", // localStorage key
      // 只持久化需要的数据，不持久化渲染结果等临时状态
      partialize: (state) => ({
        canvas: state.canvas,
        subplots: state.subplots,
        selectedSubplotId: state.selectedSubplotId,
        currentSubplotId: state.currentSubplotId,
        selectedPaletteName: state.selectedPaletteName,
        // 不持久化 renderedImage, renderError 等临时状态
      }),
    }
  )
);
