export type ChartTypeKey =
  | 'bar'
  | 'barh'
  | 'line'
  | 'pie'
  | 'area'
  | 'bubble'
  | 'hist'
  | 'boxdot'
  | 'funnel'
  | 'waterfall'
  | 'table'
  | 'map'
  | string;

/**
 * 图表类型英文 key 到中文名称的全局映射
 */
export const CHART_TYPE_LABELS: Record<ChartTypeKey, string> = {
  bar: '柱状图',
  barh: '条形图',
  line: '折线图',
  pie: '饼图',
  area: '面积图',
  bubble: '气泡图',
  hist: '直方图',
  boxdot: '箱型图',
  funnel: '漏斗图',
  waterfall: '瀑布图',
  table: '高级表格',
  map: '热力地图',
};

/**
 * 获取图表类型的中文名称，未映射时回退为原始 key
 */
export function getChartTypeName(kind: string): string {
  return CHART_TYPE_LABELS[kind] || kind;
}


