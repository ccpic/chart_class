import { CanvasConfig, SubplotConfig } from "@/types/canvas";

/**
 * API 工具库
 * 封装所有后端 API 调用
 */

// ========== 数据格式转换工具 ==========

/**
 * 将 camelCase 转换为 snake_case
 */
function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}

/**
 * 递归转换对象的键为 snake_case
 * 用于将前端的 camelCase 数据转换为后端期望的 snake_case
 */
function convertKeysToSnakeCase(obj: any): any {
  if (obj === null || obj === undefined) return obj;

  if (Array.isArray(obj)) {
    return obj.map(convertKeysToSnakeCase);
  }

  if (typeof obj === "object") {
    return Object.keys(obj).reduce((acc, key) => {
      const snakeKey = toSnakeCase(key);
      acc[snakeKey] = convertKeysToSnakeCase(obj[key]);
      return acc;
    }, {} as any);
  }

  return obj;
}

// ========== API 端点 ==========

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * 渲染整个画布（多子图）
 * @param canvas 画布配置
 * @param subplots 子图列表
 * @returns 图片 Blob
 */
export async function renderCanvas(
  canvas: CanvasConfig,
  subplots: SubplotConfig[]
): Promise<Blob> {
  const requestData = convertKeysToSnakeCase({ canvas, subplots });

  const response = await fetch(`${API_BASE_URL}/api/render/canvas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "渲染失败");
  }

  return response.blob();
}

/**
 * 渲染单个子图
 * @param subplot 子图配置
 * @returns 图片 Blob
 */
export async function renderSubplot(subplot: SubplotConfig): Promise<Blob> {
  // 直接发送完整的子图配置
  const requestData = convertKeysToSnakeCase(subplot);

  const response = await fetch(`${API_BASE_URL}/api/render/subplot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "渲染失败");
  }

  return response.blob();
}

/**
 * 获取支持的图表类型列表
 * @returns 图表类型数组
 */
export async function getChartTypes(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/chart-types`);

  if (!response.ok) {
    throw new Error("获取图表类型失败");
  }

  const data = await response.json();
  return data.chart_types || [];
}

/**
 * 获取指定图表类型的默认参数
 * @param chartType 图表类型
 * @returns 默认参数对象
 */
export async function getDefaultParams(
  chartType: string
): Promise<Record<string, any>> {
  const response = await fetch(
    `${API_BASE_URL}/api/chart-types/${chartType}/defaults`
  );

  if (!response.ok) {
    throw new Error(`获取 ${chartType} 默认参数失败`);
  }

  return response.json();
}

// ========== 旧版 API（向后兼容）==========

/**
 * @deprecated 使用 renderCanvas 代替
 */
export async function renderChart(data: any, params: any): Promise<Blob> {
  console.log("发送数据到 API:", { data, params });

  const response = await fetch(`${API_BASE_URL}/api/render`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ data, params }),
  });

  console.log("API 响应状态:", response.status);

  if (!response.ok) {
    let errorMsg = "渲染失败";
    try {
      const error = await response.json();
      errorMsg = error.detail || JSON.stringify(error);
    } catch (e) {
      errorMsg = `HTTP ${response.status}: ${response.statusText}`;
    }
    console.error("API 错误:", errorMsg);
    throw new Error(errorMsg);
  }

  return await response.blob();
}

// ========== 导出工具函数（供其他地方使用）==========
export { toSnakeCase, convertKeysToSnakeCase };
