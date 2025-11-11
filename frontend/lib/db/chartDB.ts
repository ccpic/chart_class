import { openDB, IDBPDatabase } from "idb";
import { SavedChart } from "./types";

const DB_NAME = "chart-class-charts";
const DB_VERSION = 1;
const STORE_NAME = "charts";

export class ChartDatabase {
  private db: IDBPDatabase | null = null;

  async init() {
    if (this.db) return this.db;
    this.db = await openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const store = db.createObjectStore(STORE_NAME, { keyPath: "id" });
          store.createIndex("by-name", "name");
          store.createIndex("by-createdAt", "createdAt");
          store.createIndex("by-updatedAt", "updatedAt");
          store.createIndex("by-tags", "tags", { multiEntry: true });
        }
      },
    });
    return this.db;
  }

  private async ensureDB() {
    if (!this.db) await this.init();
    return this.db!;
  }

  async saveChart(chart: SavedChart) {
    const db = await this.ensureDB();
    chart.updatedAt = Date.now();
    await db.put(STORE_NAME, chart);
  }

  async getChart(id: string): Promise<SavedChart | null> {
    const db = await this.ensureDB();
    return (await db.get(STORE_NAME, id)) as SavedChart | null;
  }

  async getAllCharts(): Promise<SavedChart[]> {
    const db = await this.ensureDB();
    return (await db.getAll(STORE_NAME)) as SavedChart[];
  }

  async deleteChart(id: string): Promise<void> {
    const db = await this.ensureDB();
    await db.delete(STORE_NAME, id);
  }

  async searchCharts(query: string): Promise<SavedChart[]> {
    const all = await this.getAllCharts();
    const q = query.trim().toLowerCase();
    if (!q) return all;
    return all.filter(
      (c) =>
        (c.name || "").toLowerCase().includes(q) ||
        (c.description || "").toLowerCase().includes(q)
    );
  }

  async exportChart(id: string): Promise<Blob> {
    const chart = await this.getChart(id);
    if (!chart) throw new Error("Chart not found");
    const json = JSON.stringify(chart, null, 2);
    return new Blob([json], { type: "application/json" });
  }

  async importChart(file: File): Promise<SavedChart> {
    const text = await file.text();
    const parsed = JSON.parse(text);
    // basic validation
    if (!parsed || !parsed.canvas || !Array.isArray(parsed.subplots)) {
      throw new Error("Invalid chart file");
    }
    // normalize id and timestamps
    const chart: SavedChart = {
      ...parsed,
      id:
        parsed.id && typeof parsed.id === "string"
          ? parsed.id
          : crypto.randomUUID(),
      createdAt: parsed.createdAt || Date.now(),
      updatedAt: Date.now(),
      version: parsed.version || "1.0",
    } as SavedChart;

    await this.saveChart(chart);
    return chart;
  }

  async clearAll() {
    const db = await this.ensureDB();
    const tx = db.transaction(STORE_NAME, "readwrite");
    await tx.store.clear();
    await tx.done;
  }
}

export const chartDB = new ChartDatabase();
