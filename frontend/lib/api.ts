const API_BASE = "http://localhost:8000";

export async function renderChart(data: any, params: any): Promise<Blob> {
  console.log("发送数据到 API:", { data, params });

  const response = await fetch(`${API_BASE}/api/render`, {
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
