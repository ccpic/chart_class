import { create } from "zustand";
import { chartDB } from "@/lib/db/chartDB";
import { useCanvasStore } from "./canvasStore";
import { SavedChart } from "@/lib/db/types";

interface ChartStore {
  charts: SavedChart[];
  currentChart: SavedChart | null;
  currentChartId: string | null; // 当前关联的图表ID
  isLoading: boolean;

  loadCharts: () => Promise<void>;
  saveCurrentAsChart: (name: string, tags?: string[]) => Promise<void>;
  updateCurrentChart: () => Promise<void>; // 更新当前图表
  saveAs: (name: string, tags?: string[]) => Promise<void>; // 另存为新图表
  loadChart: (id: string) => Promise<void>;
  deleteChart: (id: string) => Promise<void>;
  clearCurrentChartId: () => void; // 清除当前图表ID（新建时）
  getAllTags: () => Promise<string[]>; // 获取所有唯一tag列表
  filterChartsByTags: (tags: string[]) => Promise<SavedChart[]>; // 按tag筛选图表
}

export const useChartStore = create<ChartStore>((set, get) => ({
  charts: [],
  currentChart: null,
  currentChartId: null,
  isLoading: false,

  loadCharts: async () => {
    set({ isLoading: true });
    try {
      const charts = await chartDB.getAllCharts();
      set({ charts, isLoading: false });
    } catch (error) {
      console.error("Failed to load charts:", error);
      set({ isLoading: false });
    }
  },

  saveCurrentAsChart: async (name, tags) => {
    const canvasState = useCanvasStore.getState();
    const now = Date.now();
    const chart: SavedChart = {
      id: crypto.randomUUID(),
      name,
      tags: tags || [],
      createdAt: now,
      updatedAt: now,
      canvas: canvasState.canvas,
      subplots: canvasState.subplots,
      version: "1.0",
    } as SavedChart;

    await chartDB.saveChart(chart);
    set({ currentChartId: chart.id, currentChart: chart });
    await get().loadCharts();
  },

  updateCurrentChart: async () => {
    const { currentChartId, currentChart } = get();
    if (!currentChartId || !currentChart) {
      throw new Error("没有关联的图表可以更新");
    }

    const canvasState = useCanvasStore.getState();
    const updatedChart: SavedChart = {
      ...currentChart,
      updatedAt: Date.now(),
      canvas: canvasState.canvas,
      subplots: canvasState.subplots,
    };

    const savedChart = await chartDB.saveChart(updatedChart);
    // 如果降级为创建新图表，更新 currentChartId
    set({
      currentChart: savedChart,
      currentChartId: savedChart.id,
    });
    await get().loadCharts();
  },

  saveAs: async (name, tags) => {
    const canvasState = useCanvasStore.getState();
    const now = Date.now();
    const chart: SavedChart = {
      id: crypto.randomUUID(),
      name,
      tags: tags || [],
      createdAt: now,
      updatedAt: now,
      canvas: canvasState.canvas,
      subplots: canvasState.subplots,
      version: "1.0",
    } as SavedChart;

    await chartDB.saveChart(chart);
    set({ currentChartId: chart.id, currentChart: chart });
    await get().loadCharts();
  },

  loadChart: async (id) => {
    const chart = await chartDB.getChart(id);
    if (chart) {
      const canvasStore = useCanvasStore.getState();
      canvasStore.loadFromSavedChart(chart.canvas, chart.subplots);
      set({ currentChart: chart, currentChartId: id });
    }
  },

  deleteChart: async (id) => {
    await chartDB.deleteChart(id);
    const { currentChartId } = get();
    if (currentChartId === id) {
      set({ currentChartId: null, currentChart: null });
    }
    await get().loadCharts();
  },

  clearCurrentChartId: () => {
    set({ currentChartId: null, currentChart: null });
  },

  getAllTags: async () => {
    return await chartDB.getAllTags();
  },

  filterChartsByTags: async (tags) => {
    return await chartDB.filterChartsByTags(tags);
  },
}));
