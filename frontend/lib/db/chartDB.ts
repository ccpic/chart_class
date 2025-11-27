import { SavedChart } from "./types";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api/client";

/**
 * 图表数据库（使用 API 而非 IndexedDB）
 * 所有操作都通过后端 API，支持用户隔离
 */
export class ChartDatabase {
  /**
   * 保存图表（新建或更新）
   */
  async saveChart(chart: SavedChart): Promise<SavedChart> {
    const chartData = {
      name: chart.name,
      tags: chart.tags || [],
      canvas: chart.canvas,
      subplots: chart.subplots,
      version: chart.version || "1.0",
    };

    let response: any;
    if (chart.id) {
      // 尝试更新现有图表
      try {
        response = await apiPut<any>(`/api/charts/${chart.id}`, chartData);
      } catch (error: any) {
        // 如果更新失败（404），降级为创建新图表
        if (error.status === 404) {
          console.warn(`图表 ${chart.id} 不存在，降级为创建新图表`);
          response = await apiPost<any>("/api/charts", chartData);
          // 清除旧的ID，使用新的ID
          chart.id = "";
        } else {
          throw error;
        }
      }
    } else {
      // 创建新图表
      response = await apiPost<any>("/api/charts", chartData);
    }

    // 更新 chart 对象
    chart.id = response.id;
    chart.createdAt = new Date(response.created_at).getTime();
    chart.updatedAt = new Date(response.updated_at).getTime();

    return chart;
  }

  /**
   * 获取单个图表
   */
  async getChart(id: string): Promise<SavedChart | null> {
    try {
      const response = await apiGet<SavedChart>(`/api/charts/${id}`);
      // 转换后端格式到前端格式
      return {
        id: response.id,
        name: response.name,
        tags: response.tags || [],
        canvas: response.canvas,
        subplots: response.subplots,
        version: response.version,
        createdAt: new Date(response.created_at).getTime(),
        updatedAt: new Date(response.updated_at).getTime(),
      };
    } catch (error: any) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  /**
   * 获取所有图表
   */
  async getAllCharts(): Promise<SavedChart[]> {
    try {
      const charts = await apiGet<
        Array<{
          id: string;
          name: string;
          tags?: string[];
          created_at: string;
          updated_at: string;
        }>
      >("/api/charts");

      // 只返回列表信息，不包含完整数据
      // 如果需要完整数据，需要调用 getChart
      return charts.map((chart) => ({
        id: chart.id,
        name: chart.name,
        tags: chart.tags || [],
        canvas: {} as any, // 占位符，实际使用时需要调用 getChart
        subplots: [], // 占位符
        version: "1.0",
        createdAt: new Date(chart.created_at).getTime(),
        updatedAt: new Date(chart.updated_at).getTime(),
      }));
    } catch (error) {
      console.error("获取图表列表失败:", error);
      return [];
    }
  }

  /**
   * 删除图表
   */
  async deleteChart(id: string): Promise<void> {
    await apiDelete(`/api/charts/${id}`);
  }

  /**
   * 搜索图表（按名称）
   */
  async searchCharts(query: string): Promise<SavedChart[]> {
    const all = await this.getAllCharts();
    const q = query.trim().toLowerCase();
    if (!q) return all;
    return all.filter((c) => (c.name || "").toLowerCase().includes(q));
  }

  /**
   * 获取所有唯一tag列表
   */
  async getAllTags(): Promise<string[]> {
    try {
      const tags = await apiGet<string[]>("/api/charts/tags");
      return tags;
    } catch (error) {
      console.error("获取tag列表失败:", error);
      return [];
    }
  }

  /**
   * 按tag筛选图表（AND逻辑：必须包含所有指定tag）
   */
  async filterChartsByTags(tags: string[]): Promise<SavedChart[]> {
    if (!tags || tags.length === 0) {
      return await this.getAllCharts();
    }

    try {
      // 构建查询参数：tags=tag1&tags=tag2&tags=tag3
      const queryParams = tags
        .map((tag) => `tags=${encodeURIComponent(tag)}`)
        .join("&");
      const charts = await apiGet<
        Array<{
          id: string;
          name: string;
          tags?: string[];
          created_at: string;
          updated_at: string;
        }>
      >(`/api/charts?${queryParams}`);

      return charts.map((chart) => ({
        id: chart.id,
        name: chart.name,
        tags: chart.tags || [],
        canvas: {} as any,
        subplots: [],
        version: "1.0",
        createdAt: new Date(chart.created_at).getTime(),
        updatedAt: new Date(chart.updated_at).getTime(),
      }));
    } catch (error) {
      console.error("按tag筛选图表失败:", error);
      return [];
    }
  }

  /**
   * 导出图表
   */
  async exportChart(id: string): Promise<Blob> {
    const chart = await this.getChart(id);
    if (!chart) throw new Error("Chart not found");
    const json = JSON.stringify(chart, null, 2);
    return new Blob([json], { type: "application/json" });
  }

  /**
   * 导入图表
   */
  async importChart(file: File): Promise<SavedChart> {
    const text = await file.text();
    const parsed = JSON.parse(text);

    // 基本验证
    if (!parsed || !parsed.canvas || !Array.isArray(parsed.subplots)) {
      throw new Error("Invalid chart file");
    }

    // 规范化数据
    const chart: SavedChart = {
      ...parsed,
      id: parsed.id && typeof parsed.id === "string" ? parsed.id : "",
      createdAt: parsed.createdAt || Date.now(),
      updatedAt: Date.now(),
      version: parsed.version || "1.0",
    } as SavedChart;

    // 保存到服务器
    await this.saveChart(chart);
    return chart;
  }

  /**
   * 清空所有图表（仅用于测试，实际可能不需要）
   */
  async clearAll(): Promise<void> {
    const charts = await this.getAllCharts();
    for (const chart of charts) {
      await this.deleteChart(chart.id);
    }
  }
}

export const chartDB = new ChartDatabase();
