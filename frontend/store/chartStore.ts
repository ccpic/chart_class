import { create } from "zustand";
import { chartDB } from "@/lib/db/chartDB";
import { useCanvasStore } from "./canvasStore";
import { SavedChart } from "@/lib/db/types";

interface ChartStore {
  charts: SavedChart[];
  currentChart: SavedChart | null;
  isLoading: boolean;

  loadCharts: () => Promise<void>;
  saveCurrentAsChart: (name: string, description?: string) => Promise<void>;
  loadChart: (id: string) => Promise<void>;
  deleteChart: (id: string) => Promise<void>;
}

export const useChartStore = create<ChartStore>((set, get) => ({
  charts: [],
  currentChart: null,
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

  saveCurrentAsChart: async (name, description) => {
    const canvasState = useCanvasStore.getState();
    const now = Date.now();
    const chart: SavedChart = {
      id: crypto.randomUUID(),
      name,
      description,
      createdAt: now,
      updatedAt: now,
      canvas: canvasState.canvas,
      subplots: canvasState.subplots,
      version: "1.0",
    } as SavedChart;

    await chartDB.saveChart(chart);
    await get().loadCharts();
  },

  loadChart: async (id) => {
    const chart = await chartDB.getChart(id);
    if (chart) {
      const canvasStore = useCanvasStore.getState();
      canvasStore.loadFromSavedChart(chart.canvas, chart.subplots);
      set({ currentChart: chart });
    }
  },

  deleteChart: async (id) => {
    await chartDB.deleteChart(id);
    await get().loadCharts();
  },
}));
