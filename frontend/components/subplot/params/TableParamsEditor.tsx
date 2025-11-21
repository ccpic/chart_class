'use client';

import React, { useState, useEffect } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Table2, Trash2, Plus } from 'lucide-react';
import NumberFormatEditor from '@/components/ui/number-format-editor';
import ColorPicker from '@/components/color/ColorPicker';

interface Props {
  subplot: SubplotConfig;
}

interface ColumnDefinition {
  name: string;
  title?: string;
  group?: string;  // 列分组标识
  width?: number;
  border?: string;
  formatter?: string;  // 向后兼容：简单格式字符串
  // 新增：增强的格式化配置
  formatter_config?: {
    fmt: string;          // 格式字符串，如 '{:,.0f}'
    unit?: '亿' | '百万' | '万' | '千' | null;  // 单位转换
    empty_zero?: boolean; // 零值显示为空，默认 true
    empty_nan?: boolean;  // NaN 显示为空，默认 true
  };
  textprops?: {
    ha?: string;
    weight?: string;
    style?: string;
    bbox?: {
      boxstyle?: string;  // 'round', 'square', 'circle' 等
      pad?: number;        // 内边距，默认0.3
      facecolor?: string;  // 背景色
      edgecolor?: string;  // 边框色
      linewidth?: number;  // 边框宽度
      alpha?: number;      // 透明度
    };
  };
  plot_fn?: string;  // 单元格内绘图函数类型：'bar', 'percentile_bars', 'progress_donut' 等
  plot_kw?: {
    color?: string;
    annotate?: boolean;
    height?: number;
    lw?: number;
    xlim?: [number, number];  // X轴范围 [min, max]
    formatter?: string;
    textprops?: {
      fontsize?: number;
      ha?: string;
      weight?: string;
      style?: string;
    };
  };
  // 背景颜色映射配置
  cmap_config?: {
    mode: 'numeric' | 'categorical';  // 数值映射或分类映射
    // 数值映射参数
    numeric?: {
      cmap: string;        // matplotlib colormap名称
      num_stds?: number;   // 标准差倍数，默认2.5
      vmin?: number;       // 可选最小值
      vmax?: number;       // 可选最大值
    };
    // 分类映射参数
    categorical?: {
      [value: string]: string;  // 值 → 颜色映射，如 {"自营": "#FF0000", "招商": "#0000FF"}
    };
  };
  // 文字颜色映射配置
  text_cmap_config?: {
    mode: 'numeric' | 'categorical' | 'negative_red';
    numeric?: {
      cmap: string;
      num_stds?: number;
      vmin?: number;
      vmax?: number;
    };
    categorical?: {
      [value: string]: string;
    };
  };
}

/**
 * 高级表格参数编辑器
 * 提供列定义功能，动态根据数据列生成配置
 */
export default function TableParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();

  // 获取数据框的列名
  const columnNames = subplot.data.columns || [];
  // 获取索引列名称，优先使用 index_name，否则使用默认值 "index"
  const indexName = subplot.data.index_name || 'index';
  const allColumns = [indexName, ...columnNames];

  // 检查列是否包含有效数据（非空、非null、非undefined）
  const isColumnEmpty = (columnName: string): boolean => {
    const data = subplot.data.data;
    const columns = subplot.data.columns || [];
    
    if (!data || !Array.isArray(data) || data.length === 0) return true;
    
    // 找到列的索引
    const colIndex = columns.indexOf(columnName);
    if (colIndex === -1) return true;
    
    // 检查该列是否有任何有效值
    const hasValidData = data.some(row => {
      const value = row[colIndex];
      return value !== null && value !== undefined && value !== '';
    });
    
    return !hasValidData;
  };

  // 计算每列的最小值和最大值
  const getColumnRange = (columnName: string): [number, number] => {
    const data = subplot.data.data;
    const columns = subplot.data.columns || [];
    
    if (!data || !Array.isArray(data) || data.length === 0) return [0, 1];
    
    // 找到列的索引
    const colIndex = columns.indexOf(columnName);
    if (colIndex === -1) return [0, 1];
    
    // 提取该列的所有值
    const numbers = data
      .map(row => row[colIndex])
      .map(v => typeof v === 'number' ? v : parseFloat(v))
      .filter(v => !isNaN(v));
    
    if (numbers.length === 0) return [0, 1];
    
    const min = Math.min(...numbers);
    const max = Math.max(...numbers);
    
    // 如果最小值和最大值相同，返回一个合理的范围
    if (min === max) return [Math.max(0, min - 1), max + 1];
    
    return [min, max];
  };

  // 获取cmap数值配置（向后兼容）
  const getCmapNumericConfig = (cmapConfig: any) => {
    if (!cmapConfig) return null;
    if (cmapConfig.numeric) return cmapConfig.numeric;
    // 向后兼容旧格式
    if (cmapConfig.cmap) {
      return {
        cmap: cmapConfig.cmap,
        num_stds: cmapConfig.num_stds,
        vmin: cmapConfig.vmin,
        vmax: cmapConfig.vmax
      };
    }
    return null;
  };

  // 获取cmap分类配置
  const getCmapCategoricalConfig = (cmapConfig: any) => {
    if (!cmapConfig) return {};
    return cmapConfig.categorical || {};
  };

  // 更新cmap配置
  const updateCmapConfig = (index: number, mode: 'numeric' | 'categorical', updates: any) => {
    const colDef = columnDefs[index];
    if (!colDef) return;

    if (mode === 'numeric') {
      updateColumnDef(index, {
        cmap_config: {
          mode: 'numeric',
          numeric: { ...getCmapNumericConfig(colDef.cmap_config), ...updates }
        }
      });
    } else {
      updateColumnDef(index, {
        cmap_config: {
          mode: 'categorical',
          categorical: { ...getCmapCategoricalConfig(colDef.cmap_config), ...updates }
        }
      });
    }
  };

  // 更新text_cmap配置
  const updateTextCmapConfig = (index: number, mode: 'numeric' | 'categorical', updates: any) => {
    const colDef = columnDefs[index];
    if (!colDef) return;

    if (mode === 'numeric') {
      updateColumnDef(index, {
        text_cmap_config: {
          mode: 'numeric',
          numeric: { ...getCmapNumericConfig(colDef.text_cmap_config), ...updates }
        }
      });
    } else {
      updateColumnDef(index, {
        text_cmap_config: {
          mode: 'categorical',
          categorical: { ...getCmapCategoricalConfig(colDef.text_cmap_config), ...updates }
        }
      });
    }
  };

  // 初始化列定义
  const [columnDefs, setColumnDefs] = useState<ColumnDefinition[]>(() => {
    const saved = subplot.params.col_defs;
    if (saved && Array.isArray(saved)) {
      return saved;
    }
    // 默认为所有列创建定义，但排除空列（数据列）
    return allColumns
      .filter((col, idx) => {
        // 保留索引列（第一列）
        if (idx === 0) return true;
        // 过滤掉空的数据列
        return !isColumnEmpty(col);
      })
      .map((col, idx) => ({
        name: col,
        title: col,
        width: 1,
        border: undefined,
        // 索引列（第一列）不设置formatter_config
        // 数据列使用默认的 formatter_config
        formatter_config: idx === 0 ? undefined : {
          fmt: '{:,.0f}',
          unit: null,
          empty_zero: true,
          empty_nan: true,
        },
        textprops: {},
      }));
  });

  // 当数据列变化时更新列定义
  useEffect(() => {
    const currentNames = columnDefs.map(d => d.name);
    const newCols = allColumns.filter(col => {
      // 已存在的列不需要添加
      if (currentNames.includes(col)) return false;
      // 索引列始终添加
      if (col === indexName) return true;
      // 空数据列不添加
      return !isColumnEmpty(col);
    });
    
    if (newCols.length > 0) {
      setColumnDefs(prev => {
        // 再次检查，避免并发更新导致的重复
        const prevNames = prev.map(d => d.name);
        const actualNewCols = newCols.filter(col => !prevNames.includes(col));
        
        if (actualNewCols.length === 0) return prev;
        
        return [
          ...prev,
          ...actualNewCols.map((col) => ({
            name: col,
            title: col,
            width: 1,
            border: undefined,
            // 新增的列：如果是索引列则不设置formatter_config
            formatter_config: col === indexName ? undefined : {
              fmt: '{:,.0f}',
              unit: null,
              empty_zero: true,
              empty_nan: true,
            },
            textprops: {},
          }))
        ];
      });
    }
  }, [columnNames.length]); // 只监听列数变化，避免无限循环

  // 更新列定义
  const updateColumnDef = (index: number, updates: Partial<ColumnDefinition>) => {
    const newDefs = [...columnDefs];
    const currentDef = newDefs[index];
    
    // 如果更新了formatter且存在plot_fn，同步formatter到plot_kw
    if (updates.formatter !== undefined && currentDef.plot_fn) {
      updates = {
        ...updates,
        plot_kw: {
          ...currentDef.plot_kw,
          formatter: updates.formatter
        }
      };
    }
    
    // 如果更新了formatter_config且存在plot_fn，同步到plot_kw.formatter
    // 注意：后端会自动使用列定义的formatter_config（包括unit），但前端需要确保plot_kw.formatter存在
    if (updates.formatter_config !== undefined && currentDef.plot_fn) {
      const fmtValue = updates.formatter_config.fmt || currentDef.formatter_config?.fmt || currentDef.formatter || '{:,.0f}';
      updates = {
        ...updates,
        plot_kw: {
          ...currentDef.plot_kw,
          formatter: fmtValue
        }
      };
    }
    
    newDefs[index] = { ...currentDef, ...updates };
    
    // 去重：确保没有重复的列名
    const uniqueDefs = newDefs.filter((def, idx, self) => 
      idx === self.findIndex(d => d.name === def.name)
    );
    
    setColumnDefs(uniqueDefs);
    updateParam('col_defs', uniqueDefs);
  };

  // 删除列定义
  const removeColumnDef = (index: number) => {
    const newDefs = columnDefs.filter((_, i) => i !== index);
    setColumnDefs(newDefs);
    updateParam('col_defs', newDefs);
  };

  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="columns" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="columns" className="text-xs gap-1">
            <Table2 className="h-3 w-3" />
            列定义
          </TabsTrigger>
          <TabsTrigger value="table" className="text-xs">表格样式</TabsTrigger>
        </TabsList>

        {/* Tab 1: 列定义 */}
        <TabsContent value="columns" className="space-y-4 mt-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">
              共 {columnDefs.filter((colDef, index, self) => 
                index === self.findIndex(c => c.name === colDef.name)
              ).length} 列
            </p>
          </div>

          <Accordion type="multiple" className="w-full">
            {columnDefs
              // 去重：如果有重复的列名，只保留第一个出现的
              .map((colDef, originalIndex) => ({ colDef, originalIndex }))
              .filter(({ colDef }, index, self) => 
                index === self.findIndex(item => item.colDef.name === colDef.name)
              )
              .map(({ colDef, originalIndex: index }) => (
              <AccordionItem key={colDef.name} value={colDef.name}>
                <AccordionTrigger className="text-sm hover:no-underline">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{colDef.title || colDef.name}</span>
                    <span className="text-xs text-gray-500">({colDef.name})</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 p-4 bg-gray-50 rounded-md">
                    {/* 基础设置 */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-semibold text-gray-700">基础设置</h4>
                      
                      {/* 分组和显示标题 */}
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1.5">
                          <Label htmlFor={`group-${index}`} className="text-xs">
                            分组
                          </Label>
                          <Input
                            id={`group-${index}`}
                            value={colDef.group || ''}
                            onChange={(e) => updateColumnDef(index, { group: e.target.value || undefined })}
                            placeholder="可选"
                            className="h-8 text-sm"
                          />
                        </div>

                        <div className="space-y-1.5">
                          <Label htmlFor={`title-${index}`} className="text-xs">
                            显示标题 <span className="text-gray-400">(Shift+Enter换行)</span>
                          </Label>
                          <Textarea
                            id={`title-${index}`}
                            value={colDef.title || ''}
                            onChange={(e) => updateColumnDef(index, { title: e.target.value })}
                            placeholder={colDef.name}
                            className="min-h-[32px] text-sm resize-y"
                            rows={1}
                          />
                        </div>
                      </div>

                      {/* 列宽度 */}
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1.5">
                          <Label htmlFor={`width-${index}`} className="text-xs">
                            列宽比例
                          </Label>
                          <Input
                            id={`width-${index}`}
                            type="number"
                            min="0.1"
                            max="10"
                            step="0.1"
                            value={colDef.width || 1}
                            onChange={(e) => updateColumnDef(index, { width: parseFloat(e.target.value) || 1 })}
                            className="h-8 text-sm"
                          />
                        </div>

                        {/* 边框 */}
                        <div className="space-y-1.5">
                          <Label htmlFor={`border-${index}`} className="text-xs">
                            边框位置
                          </Label>
                          <Select
                            value={colDef.border || 'none'}
                            onValueChange={(value) => updateColumnDef(index, { border: value === 'none' ? undefined : value })}
                          >
                            <SelectTrigger id={`border-${index}`} className="h-8 text-sm">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="none">无边框</SelectItem>
                              <SelectItem value="left">左边框</SelectItem>
                              <SelectItem value="right">右边框</SelectItem>
                              <SelectItem value="both">两侧边框</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>

                    {/* 文本样式 */}
                    <div className="space-y-3 pt-3 border-t">
                      <h4 className="text-xs font-semibold text-gray-700">文本样式</h4>
                      
                      <div className="grid grid-cols-3 gap-2">
                        {/* 水平对齐 */}
                        <div className="space-y-1.5">
                          <Label htmlFor={`ha-${index}`} className="text-xs">
                            对齐
                          </Label>
                          <Select
                            value={colDef.textprops?.ha || 'left'}
                            onValueChange={(value) => updateColumnDef(index, { 
                              textprops: { ...colDef.textprops, ha: value }
                            })}
                          >
                            <SelectTrigger id={`ha-${index}`} className="h-8 text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="left">左对齐</SelectItem>
                              <SelectItem value="center">居中</SelectItem>
                              <SelectItem value="right">右对齐</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        {/* 字重 */}
                        <div className="space-y-1.5">
                          <Label htmlFor={`weight-${index}`} className="text-xs">
                            字重
                          </Label>
                          <Select
                            value={colDef.textprops?.weight || 'normal'}
                            onValueChange={(value) => updateColumnDef(index, { 
                              textprops: { ...colDef.textprops, weight: value }
                            })}
                          >
                            <SelectTrigger id={`weight-${index}`} className="h-8 text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="normal">常规</SelectItem>
                              <SelectItem value="bold">加粗</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        {/* 字体样式 */}
                        <div className="space-y-1.5">
                          <Label htmlFor={`style-${index}`} className="text-xs">
                            样式
                          </Label>
                          <Select
                            value={colDef.textprops?.style || 'normal'}
                            onValueChange={(value) => updateColumnDef(index, { 
                              textprops: { ...colDef.textprops, style: value }
                            })}
                          >
                            <SelectTrigger id={`style-${index}`} className="h-8 text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="normal">正常</SelectItem>
                              <SelectItem value="italic">斜体</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      {/* 文本框样式 (bbox) */}
                      <div className="space-y-2 pt-2">
                        <div className="flex items-center justify-between">
                          <Label className="text-xs font-medium">文本框 (bbox)</Label>
                          <Checkbox
                            id={`enable-bbox-${index}`}
                            checked={!!colDef.textprops?.bbox}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                updateColumnDef(index, {
                                  textprops: {
                                    ...colDef.textprops,
                                    bbox: {
                                      boxstyle: 'round',
                                      pad: 0.3,
                                      facecolor: undefined,  // 默认无背景色
                                      edgecolor: undefined,  // 默认无边框色
                                      linewidth: 1,
                                      alpha: 0.8
                                    }
                                  }
                                });
                              } else {
                                const { bbox, ...restTextprops } = colDef.textprops || {};
                                updateColumnDef(index, { textprops: restTextprops });
                              }
                            }}
                          />
                        </div>

                        {colDef.textprops?.bbox && (
                          <div className="grid grid-cols-2 gap-2 pl-2 border-l-2 border-gray-200">
                            {/* 框样式 */}
                            <div className="space-y-1.5">
                              <Label htmlFor={`bbox-style-${index}`} className="text-xs">
                                框样式
                              </Label>
                              <Select
                                value={colDef.textprops.bbox.boxstyle || 'round'}
                                onValueChange={(value) => updateColumnDef(index, {
                                  textprops: {
                                    ...colDef.textprops,
                                    bbox: { ...colDef.textprops!.bbox, boxstyle: value }
                                  }
                                })}
                              >
                                <SelectTrigger id={`bbox-style-${index}`} className="h-8 text-sm">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="round">圆角</SelectItem>
                                  <SelectItem value="square">方角</SelectItem>
                                  <SelectItem value="circle">圆形</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>

                            {/* 内边距 */}
                            <div className="space-y-1.5">
                              <Label htmlFor={`bbox-pad-${index}`} className="text-xs">
                                内边距
                              </Label>
                              <Input
                                id={`bbox-pad-${index}`}
                                type="number"
                                min="0"
                                max="1"
                                step="0.05"
                                value={colDef.textprops.bbox.pad ?? 0.3}
                                onChange={(e) => updateColumnDef(index, {
                                  textprops: {
                                    ...colDef.textprops,
                                    bbox: { ...colDef.textprops!.bbox, pad: parseFloat(e.target.value) || 0.3 }
                                  }
                                })}
                                className="h-8 text-sm"
                              />
                            </div>

                            {/* 背景色 */}
                            <div className="space-y-1.5">
                              <div className="flex items-center justify-between mb-1">
                                <Label className="text-xs">背景色</Label>
                                <Checkbox
                                  id={`bbox-facecolor-enable-${index}`}
                                  checked={!!colDef.textprops.bbox.facecolor}
                                  onCheckedChange={(checked) => {
                                    updateColumnDef(index, {
                                      textprops: {
                                        ...colDef.textprops,
                                        bbox: { 
                                          ...colDef.textprops!.bbox, 
                                          facecolor: checked ? '#FFFF00' : undefined 
                                        }
                                      }
                                    });
                                  }}
                                />
                              </div>
                              {colDef.textprops.bbox.facecolor && (
                                <ColorPicker
                                  value={colDef.textprops.bbox.facecolor}
                                  onChange={(color) => updateColumnDef(index, {
                                    textprops: {
                                      ...colDef.textprops,
                                      bbox: { ...colDef.textprops!.bbox, facecolor: color }
                                    }
                                  })}
                                  showColorValue={false}
                                />
                              )}
                            </div>

                            {/* 边框色 */}
                            <div className="space-y-1.5">
                              <div className="flex items-center justify-between mb-1">
                                <Label className="text-xs">边框色</Label>
                                <Checkbox
                                  id={`bbox-edgecolor-enable-${index}`}
                                  checked={!!colDef.textprops.bbox.edgecolor}
                                  onCheckedChange={(checked) => {
                                    updateColumnDef(index, {
                                      textprops: {
                                        ...colDef.textprops,
                                        bbox: { 
                                          ...colDef.textprops!.bbox, 
                                          edgecolor: checked ? '#000000' : undefined 
                                        }
                                      }
                                    });
                                  }}
                                />
                              </div>
                              {colDef.textprops.bbox.edgecolor && (
                                <ColorPicker
                                  value={colDef.textprops.bbox.edgecolor}
                                  onChange={(color) => updateColumnDef(index, {
                                    textprops: {
                                      ...colDef.textprops,
                                      bbox: { ...colDef.textprops!.bbox, edgecolor: color }
                                    }
                                  })}
                                  showColorValue={false}
                                />
                              )}
                            </div>

                            {/* 边框宽度 */}
                            <div className="space-y-1.5">
                              <Label htmlFor={`bbox-lw-${index}`} className="text-xs">
                                边框宽度
                              </Label>
                              <Input
                                id={`bbox-lw-${index}`}
                                type="number"
                                min="0"
                                max="5"
                                step="0.5"
                                value={colDef.textprops.bbox.linewidth ?? 1}
                                onChange={(e) => updateColumnDef(index, {
                                  textprops: {
                                    ...colDef.textprops,
                                    bbox: {
                                      ...colDef.textprops!.bbox,
                                      linewidth: parseFloat(e.target.value) || 1
                                    }
                                  }
                                })}
                                className="h-8 text-sm"
                              />
                            </div>

                            {/* 透明度 */}
                            <div className="space-y-1.5">
                              <Label htmlFor={`bbox-alpha-${index}`} className="text-xs">
                                透明度
                              </Label>
                              <Input
                                id={`bbox-alpha-${index}`}
                                type="number"
                                min="0"
                                max="1"
                                step="0.1"
                                value={colDef.textprops.bbox.alpha ?? 0.8}
                                onChange={(e) => updateColumnDef(index, {
                                  textprops: {
                                    ...colDef.textprops,
                                    bbox: {
                                      ...colDef.textprops!.bbox,
                                      alpha: parseFloat(e.target.value) || 0.8
                                    }
                                  }
                                })}
                                className="h-8 text-sm"
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* 数值格式化 */}
                    <div className="space-y-3 pt-3 border-t">
                      <h4 className="text-xs font-semibold text-gray-700">数值格式化</h4>
                      
                      {/* 格式字符串 */}
                      <div className="space-y-1.5">
                        <Label className="text-xs">格式模板</Label>
                        <NumberFormatEditor
                          value={colDef.formatter_config?.fmt || colDef.formatter || '{:,.0f}'}
                          onChange={(format) => updateColumnDef(index, { 
                            formatter_config: {
                              ...colDef.formatter_config,
                              fmt: format,
                              unit: colDef.formatter_config?.unit ?? null,
                              empty_zero: colDef.formatter_config?.empty_zero ?? true,
                              empty_nan: colDef.formatter_config?.empty_nan ?? true,
                            }
                          })}
                          label=""
                          showHelp={true}
                        />
                      </div>

                      {/* 单位转换 */}
                      <div className="space-y-1.5">
                        <Label className="text-xs">单位转换</Label>
                        <Select
                          value={colDef.formatter_config?.unit || 'none'}
                          onValueChange={(value) => {
                            const unit = value === 'none' ? null : value as '亿' | '百万' | '万' | '千';
                            updateColumnDef(index, {
                              formatter_config: {
                                fmt: colDef.formatter_config?.fmt || colDef.formatter || '{:,.0f}',
                                unit,
                                empty_zero: colDef.formatter_config?.empty_zero ?? true,
                                empty_nan: colDef.formatter_config?.empty_nan ?? true,
                              }
                            });
                          }}
                        >
                          <SelectTrigger className="h-8 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="none">无</SelectItem>
                            <SelectItem value="亿">亿</SelectItem>
                            <SelectItem value="百万">百万</SelectItem>
                            <SelectItem value="万">万</SelectItem>
                            <SelectItem value="千">千</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      {/* 空值处理 */}
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id={`empty-zero-${index}`}
                            checked={colDef.formatter_config?.empty_zero ?? true}
                            onCheckedChange={(checked) => {
                              updateColumnDef(index, {
                                formatter_config: {
                                  fmt: colDef.formatter_config?.fmt || colDef.formatter || '{:,.0f}',
                                  unit: colDef.formatter_config?.unit ?? null,
                                  empty_zero: !!checked,
                                  empty_nan: colDef.formatter_config?.empty_nan ?? true,
                                }
                              });
                            }}
                          />
                          <Label htmlFor={`empty-zero-${index}`} className="text-xs cursor-pointer">
                            零值显示为空
                          </Label>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id={`empty-nan-${index}`}
                            checked={colDef.formatter_config?.empty_nan ?? true}
                            onCheckedChange={(checked) => {
                              updateColumnDef(index, {
                                formatter_config: {
                                  fmt: colDef.formatter_config?.fmt || colDef.formatter || '{:,.0f}',
                                  unit: colDef.formatter_config?.unit ?? null,
                                  empty_zero: colDef.formatter_config?.empty_zero ?? true,
                                  empty_nan: !!checked,
                                }
                              });
                            }}
                          />
                          <Label htmlFor={`empty-nan-${index}`} className="text-xs cursor-pointer">
                            空值显示为空
                          </Label>
                        </div>
                      </div>
                    </div>

                    {/* 背景色映射 */}
                    <div className="space-y-3 pt-3 border-t">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-semibold text-gray-700">背景色映射 (cmap)</h4>
                        <Checkbox
                          id={`enable-cmap-${index}`}
                          checked={!!colDef.cmap_config}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              updateColumnDef(index, {
                                cmap_config: { mode: 'numeric', numeric: { cmap: 'PiYG', num_stds: 2.5 } }
                              });
                            } else {
                              updateColumnDef(index, {
                                cmap_config: undefined
                              });
                            }
                          }}
                        />
                      </div>

                      {colDef.cmap_config && (
                        <div className="space-y-3 pl-2 border-l-2 border-gray-200">
                          {/* 模式选择 */}
                          <div className="space-y-1.5">
                            <Label className="text-xs">映射模式</Label>
                            <Select
                              value={colDef.cmap_config?.mode || 'numeric'}
                              onValueChange={(value: 'numeric' | 'categorical') => {
                                if (value === 'numeric') {
                                  updateColumnDef(index, {
                                    cmap_config: { mode: 'numeric', numeric: { cmap: 'PiYG', num_stds: 2.5 } }
                                  });
                                } else {
                                  updateColumnDef(index, {
                                    cmap_config: { mode: 'categorical', categorical: {} }
                                  });
                                }
                              }}
                            >
                              <SelectTrigger className="h-8 text-sm">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="numeric">数值映射</SelectItem>
                                <SelectItem value="categorical">分类映射</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>                              {/* 数值映射配置 */}
                            {colDef.cmap_config?.mode === 'numeric' && (
                              <div className="grid grid-cols-2 gap-2 pl-2 border-l border-gray-200">
                                {/* Colormap选择 */}
                                <div className="col-span-2 space-y-1.5">
                                  <Label htmlFor={`cmap-${index}`} className="text-xs">
                                    Colormap
                                  </Label>
                                  <Select
                                    value={getCmapNumericConfig(colDef.cmap_config)?.cmap || 'PiYG'}
                                    onValueChange={(value) => updateCmapConfig(index, 'numeric', { cmap: value })}
                                  >
                                    <SelectTrigger id={`cmap-${index}`} className="h-8 text-sm">
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="PiYG">PiYG (粉绿)</SelectItem>
                                      <SelectItem value="RdYlGn">RdYlGn (红黄绿)</SelectItem>
                                      <SelectItem value="RdBu">RdBu (红蓝)</SelectItem>
                                      <SelectItem value="viridis">Viridis (紫黄)</SelectItem>
                                      <SelectItem value="viridis_r">Viridis_r (黄紫)</SelectItem>
                                      <SelectItem value="plasma">Plasma (紫橙)</SelectItem>
                                      <SelectItem value="inferno">Inferno (黑红黄)</SelectItem>
                                      <SelectItem value="coolwarm">Coolwarm (蓝红)</SelectItem>
                                      <SelectItem value="Spectral">Spectral (光谱)</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>

                                {/* 标准差倍数 */}
                                <div className="space-y-1.5">
                                  <Label htmlFor={`cmap-stds-${index}`} className="text-xs">
                                    标准差倍数
                                  </Label>
                                  <Input
                                    id={`cmap-stds-${index}`}
                                    type="number"
                                    min="0.5"
                                    max="5"
                                    step="0.5"
                                    value={getCmapNumericConfig(colDef.cmap_config)?.num_stds ?? 2.5}
                                    onChange={(e) => updateCmapConfig(index, 'numeric', { num_stds: parseFloat(e.target.value) || 2.5 })}
                                    className="h-8 text-sm"
                                  />
                                </div>

                                {/* 空位 */}
                                <div></div>

                                {/* vmin */}
                                <div className="space-y-1.5">
                                  <Label htmlFor={`cmap-vmin-${index}`} className="text-xs">
                                    最小值 (可选)
                                  </Label>
                                  <Input
                                    id={`cmap-vmin-${index}`}
                                    type="number"
                                    step="0.1"
                                    placeholder="自动"
                                    value={getCmapNumericConfig(colDef.cmap_config)?.vmin ?? ''}
                                    onChange={(e) => updateCmapConfig(index, 'numeric', { vmin: e.target.value ? parseFloat(e.target.value) : undefined })}
                                    className="h-8 text-sm"
                                  />
                                </div>

                                {/* vmax */}
                                <div className="space-y-1.5">
                                  <Label htmlFor={`cmap-vmax-${index}`} className="text-xs">
                                    最大值 (可选)
                                  </Label>
                                  <Input
                                    id={`cmap-vmax-${index}`}
                                    type="number"
                                    step="0.1"
                                    placeholder="自动"
                                    value={getCmapNumericConfig(colDef.cmap_config)?.vmax ?? ''}
                                    onChange={(e) => updateCmapConfig(index, 'numeric', { vmax: e.target.value ? parseFloat(e.target.value) : undefined })}
                                    className="h-8 text-sm"
                                  />
                                </div>
                              </div>
                            )}

                            {/* 分类映射配置 */}
                            {colDef.cmap_config?.mode === 'categorical' && (
                              <div className="space-y-2 pl-2 border-l border-gray-200">
                                <div className="flex items-center justify-between">
                                  <Label className="text-xs">值-颜色映射</Label>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="h-6 px-2 text-xs"
                                    onClick={() => {
                                      const current = getCmapCategoricalConfig(colDef.cmap_config);
                                      const newKey = `值${Object.keys(current).length + 1}`;
                                      updateCmapConfig(index, 'categorical', { [newKey]: '#000000' });
                                    }}
                                  >
                                    + 添加
                                  </Button>
                                </div>
                                
                                {Object.entries(getCmapCategoricalConfig(colDef.cmap_config) || {}).map(([value, color], mapIndex) => (
                                  <div key={mapIndex} className="flex items-center gap-2">
                                    <Input
                                      value={value}
                                      onChange={(e) => {
                                        const current = getCmapCategoricalConfig(colDef.cmap_config);
                                        const newMap = { ...current };
                                        delete newMap[value];
                                        newMap[e.target.value] = color as string;
                                        updateColumnDef(index, {
                                          cmap_config: { mode: 'categorical', categorical: newMap }
                                        });
                                      }}
                                      placeholder="值"
                                      className="h-8 text-sm flex-1"
                                    />
                                    <ColorPicker
                                      value={color as string}
                                      onChange={(newColor) => updateCmapConfig(index, 'categorical', { [value]: newColor })}
                                    />
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      className="h-8 w-8 p-0"
                                      onClick={() => {
                                        const current = getCmapCategoricalConfig(colDef.cmap_config);
                                        const newMap = { ...current };
                                        delete newMap[value];
                                        updateColumnDef(index, {
                                          cmap_config: { mode: 'categorical', categorical: newMap }
                                        });
                                      }}
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  </div>
                                ))}
                              </div>
                            )}
                        </div>
                      )}
                    </div>

                    {/* 文字色映射 */}
                    <div className="space-y-3 pt-3 border-t">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-semibold text-gray-700">文字色映射 (text_cmap)</h4>
                        <Checkbox
                          id={`enable-text-cmap-${index}`}
                          checked={!!colDef.text_cmap_config}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              // 默认使用负值标红模式
                              updateColumnDef(index, {
                                text_cmap_config: { mode: 'negative_red' }
                              });
                            } else {
                              updateColumnDef(index, {
                                text_cmap_config: undefined
                              });
                            }
                          }}
                        />
                      </div>

                      {colDef.text_cmap_config && (
                        <div className="space-y-3 pl-2 border-l-2 border-gray-200">
                          {/* 模式选择 */}
                          <div className="space-y-1.5">
                            <Label className="text-xs">映射模式</Label>
                              <Select
                                value={colDef.text_cmap_config?.mode || 'numeric'}
                                onValueChange={(value: 'numeric' | 'categorical' | 'negative_red') => {
                                  if (value === 'numeric') {
                                    updateColumnDef(index, {
                                      text_cmap_config: { mode: 'numeric', numeric: { cmap: 'RdYlGn', num_stds: 2.5 } }
                                    });
                                  } else if (value === 'categorical') {
                                    updateColumnDef(index, {
                                      text_cmap_config: { mode: 'categorical', categorical: {} }
                                    });
                                  } else if (value === 'negative_red') {
                                    updateColumnDef(index, {
                                      text_cmap_config: { mode: 'negative_red' }
                                    });
                                  }
                                }}
                              >
                                <SelectTrigger className="h-8 text-sm">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="numeric">数值映射</SelectItem>
                                  <SelectItem value="categorical">分类映射</SelectItem>
                                  <SelectItem value="negative_red">负值标红</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>

                            {/* 数值映射配置 */}
                            {colDef.text_cmap_config?.mode === 'numeric' && (
                              <div className="grid grid-cols-2 gap-2 pl-2 border-l border-gray-200">
                                {/* Colormap选择 */}
                                <div className="col-span-2 space-y-1.5">
                                  <Label htmlFor={`text-cmap-${index}`} className="text-xs">
                                    Colormap
                                  </Label>
                                  <Select
                                    value={getCmapNumericConfig(colDef.text_cmap_config)?.cmap || 'RdYlGn'}
                                    onValueChange={(value) => updateTextCmapConfig(index, 'numeric', { cmap: value })}
                                  >
                                    <SelectTrigger id={`text-cmap-${index}`} className="h-8 text-sm">
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="PiYG">PiYG (粉绿)</SelectItem>
                                      <SelectItem value="RdYlGn">RdYlGn (红黄绿)</SelectItem>
                                      <SelectItem value="RdBu">RdBu (红蓝)</SelectItem>
                                      <SelectItem value="viridis">Viridis (紫黄)</SelectItem>
                                      <SelectItem value="viridis_r">Viridis_r (黄紫)</SelectItem>
                                      <SelectItem value="plasma">Plasma (紫橙)</SelectItem>
                                      <SelectItem value="inferno">Inferno (黑红黄)</SelectItem>
                                      <SelectItem value="coolwarm">Coolwarm (蓝红)</SelectItem>
                                      <SelectItem value="Spectral">Spectral (光谱)</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>

                                {/* 标准差倍数 */}
                                <div className="space-y-1.5">
                                  <Label htmlFor={`text-cmap-stds-${index}`} className="text-xs">
                                    标准差倍数
                                  </Label>
                                  <Input
                                    id={`text-cmap-stds-${index}`}
                                    type="number"
                                    min="0.5"
                                    max="5"
                                    step="0.5"
                                    value={getCmapNumericConfig(colDef.text_cmap_config)?.num_stds ?? 2.5}
                                    onChange={(e) => updateTextCmapConfig(index, 'numeric', { num_stds: parseFloat(e.target.value) || 2.5 })}
                                    className="h-8 text-sm"
                                  />
                                </div>

                                {/* 空位 */}
                                <div></div>

                                {/* vmin */}
                                <div className="space-y-1.5">
                                  <Label htmlFor={`text-cmap-vmin-${index}`} className="text-xs">
                                    最小值 (可选)
                                  </Label>
                                  <Input
                                    id={`text-cmap-vmin-${index}`}
                                    type="number"
                                    step="0.1"
                                    placeholder="自动"
                                    value={getCmapNumericConfig(colDef.text_cmap_config)?.vmin ?? ''}
                                    onChange={(e) => updateTextCmapConfig(index, 'numeric', { vmin: e.target.value ? parseFloat(e.target.value) : undefined })}
                                    className="h-8 text-sm"
                                  />
                                </div>

                                {/* vmax */}
                                <div className="space-y-1.5">
                                  <Label htmlFor={`text-cmap-vmax-${index}`} className="text-xs">
                                    最大值 (可选)
                                  </Label>
                                  <Input
                                    id={`text-cmap-vmax-${index}`}
                                    type="number"
                                    step="0.1"
                                    placeholder="自动"
                                    value={getCmapNumericConfig(colDef.text_cmap_config)?.vmax ?? ''}
                                    onChange={(e) => updateTextCmapConfig(index, 'numeric', { vmax: e.target.value ? parseFloat(e.target.value) : undefined })}
                                    className="h-8 text-sm"
                                  />
                                </div>
                              </div>
                            )}

                            {/* 分类映射配置 */}
                            {colDef.text_cmap_config?.mode === 'categorical' && (
                              <div className="space-y-2 pl-2 border-l border-gray-200">
                                <div className="flex items-center justify-between">
                                  <Label className="text-xs">值-颜色映射</Label>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="h-6 px-2 text-xs"
                                    onClick={() => {
                                      const current = getCmapCategoricalConfig(colDef.text_cmap_config);
                                      const newKey = `值${Object.keys(current).length + 1}`;
                                      updateTextCmapConfig(index, 'categorical', { [newKey]: '#000000' });
                                    }}
                                  >
                                    + 添加
                                  </Button>
                                </div>
                                
                                {Object.entries(getCmapCategoricalConfig(colDef.text_cmap_config) || {}).map(([value, color], mapIndex) => (
                                  <div key={mapIndex} className="flex items-center gap-2">
                                    <Input
                                      value={value}
                                      onChange={(e) => {
                                        const current = getCmapCategoricalConfig(colDef.text_cmap_config);
                                        const newMap = { ...current };
                                        delete newMap[value];
                                        newMap[e.target.value] = color as string;
                                        updateColumnDef(index, {
                                          text_cmap_config: { mode: 'categorical', categorical: newMap }
                                        });
                                      }}
                                      placeholder="值"
                                      className="h-8 text-sm flex-1"
                                    />
                                    <ColorPicker
                                      value={color as string}
                                      onChange={(newColor) => updateTextCmapConfig(index, 'categorical', { [value]: newColor })}
                                    />
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      className="h-8 w-8 p-0"
                                      onClick={() => {
                                        const current = getCmapCategoricalConfig(colDef.text_cmap_config);
                                        const newMap = { ...current };
                                        delete newMap[value];
                                        updateColumnDef(index, {
                                          text_cmap_config: { mode: 'categorical', categorical: newMap }
                                        });
                                      }}
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* 负值标红配置 */}
                            {colDef.text_cmap_config?.mode === 'negative_red' && (
                              <div className="pl-2 border-l border-gray-200">
                                <p className="text-xs text-gray-500">
                                  负数值将显示为红色，非负数值显示为默认颜色（黑色）
                                </p>
                              </div>
                            )}
                        </div>
                      )}
                    </div>

                    {/* 单元格图表 */}
                    <div className="space-y-3 pt-3 border-t">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-semibold text-gray-700">单元格图表</h4>
                        <Checkbox
                          id={`enable-plot-${index}`}
                          checked={!!colDef.plot_fn}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              const [min, max] = getColumnRange(colDef.name);
                              updateColumnDef(index, { 
                                plot_fn: 'bar',
                                plot_kw: {
                                  color: 'lightblue',
                                  annotate: true,
                                  height: 1,
                                  lw: 0.5,
                                  xlim: [min, max],
                                  formatter: colDef.formatter_config?.fmt || colDef.formatter || '{:,.0f}',
                                  textprops: { fontsize: 10 }
                                }
                              });
                            } else {
                              updateColumnDef(index, { plot_fn: undefined, plot_kw: undefined });
                            }
                          }}
                        />
                      </div>

                      {colDef.plot_fn && (
                        <div className="space-y-3 pl-2 border-l-2 border-gray-200">
                          {/* 图表类型 */}
                          <div className="space-y-1.5">
                            <Label htmlFor={`plot-type-${index}`} className="text-xs">
                              图表类型
                            </Label>
                            <Select
                              value={colDef.plot_fn || 'bar'}
                              onValueChange={(value) => updateColumnDef(index, { plot_fn: value })}
                            >
                              <SelectTrigger id={`plot-type-${index}`} className="h-8 text-sm">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="bar">条形图 (bar)</SelectItem>
                                <SelectItem value="percentile_bars">百分比条 (percentile_bars)</SelectItem>
                                <SelectItem value="progress_donut">进度环 (progress_donut)</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>

                          {/* 颜色 */}
                          <div className="space-y-1.5">
                            <ColorPicker
                              value={colDef.plot_kw?.color || 'lightblue'}
                              onChange={(color) => updateColumnDef(index, { 
                                plot_kw: { ...colDef.plot_kw, color }
                              })}
                              label="颜色"
                              showColorValue={true}
                            />
                          </div>

                          {/* X轴范围 (xlim) */}
                          <div className="space-y-1.5">
                            <Label className="text-xs">X轴范围 (xlim)</Label>
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <Input
                                  type="number"
                                  placeholder="最小值"
                                  step="0.1"
                                  value={colDef.plot_kw?.xlim?.[0] ?? getColumnRange(colDef.name)[0]}
                                  onChange={(e) => {
                                    const min = parseFloat(e.target.value) || 0;
                                    const max = colDef.plot_kw?.xlim?.[1] ?? getColumnRange(colDef.name)[1];
                                    updateColumnDef(index, { 
                                      plot_kw: { ...colDef.plot_kw, xlim: [min, max] }
                                    });
                                  }}
                                  className="h-8 text-sm"
                                />
                              </div>
                              <div>
                                <Input
                                  type="number"
                                  placeholder="最大值"
                                  step="0.1"
                                  value={colDef.plot_kw?.xlim?.[1] ?? getColumnRange(colDef.name)[1]}
                                  onChange={(e) => {
                                    const min = colDef.plot_kw?.xlim?.[0] ?? getColumnRange(colDef.name)[0];
                                    const max = parseFloat(e.target.value) || 1;
                                    updateColumnDef(index, { 
                                      plot_kw: { ...colDef.plot_kw, xlim: [min, max] }
                                    });
                                  }}
                                  className="h-8 text-sm"
                                />
                              </div>
                            </div>
                            <p className="text-xs text-gray-500">
                              条形图的横轴范围（自动基于数据范围）
                            </p>
                          </div>

                          {/* 显示标注和标注字号 */}
                          <div className="grid grid-cols-2 gap-2">
                            <div className="space-y-1.5">
                              <Label className="text-xs">显示标注</Label>
                              <div className="flex items-center h-8">
                                <Checkbox
                                  id={`plot-annotate-${index}`}
                                  checked={colDef.plot_kw?.annotate !== false}
                                  onCheckedChange={(checked) => updateColumnDef(index, { 
                                    plot_kw: { ...colDef.plot_kw, annotate: checked as boolean }
                                  })}
                                />
                              </div>
                            </div>

                            <div className="space-y-1.5">
                              <Label htmlFor={`plot-fontsize-${index}`} className="text-xs">
                                标注字号
                              </Label>
                              <Input
                                id={`plot-fontsize-${index}`}
                                type="number"
                                min="4"
                                max="20"
                                step="1"
                                value={colDef.plot_kw?.textprops?.fontsize || 10}
                                onChange={(e) => updateColumnDef(index, { 
                                  plot_kw: { 
                                    ...colDef.plot_kw, 
                                    textprops: { 
                                      ...colDef.plot_kw?.textprops, 
                                      fontsize: parseInt(e.target.value) || 10 
                                    }
                                  }
                                })}
                                className="h-8 text-sm"
                              />
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* 删除按钮 */}
                    <div className="pt-3 border-t">
                      <Button
                        onClick={() => removeColumnDef(index)}
                        variant="outline"
                        size="sm"
                        className="w-full gap-2 text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                        移除此列定义
                      </Button>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </TabsContent>

        {/* Tab 2: 表格样式 */}
        <TabsContent value="table" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">索引列设置</h4>
            
            {/* 索引列名称 */}
            <div className="space-y-1.5">
              <Label htmlFor="index-name" className="text-xs">
                索引列名称
              </Label>
              <Input
                id="index-name"
                value={subplot.data.index_name || 'index'}
                onChange={(e) => {
                  const newIndexName = e.target.value || 'index';
                  updateSubplot(subplot.subplotId, {
                    data: { ...subplot.data, index_name: newIndexName }
                  });
                }}
                placeholder="index"
                className="h-8 text-sm"
              />
              <p className="text-xs text-gray-500">
                设置后，在"列定义"中使用此名称配置索引列样式
              </p>
            </div>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">全局样式</h4>
            
            {/* 行分隔线 */}
            <div className="flex items-center gap-2">
              <Checkbox
                id="row-dividers"
                checked={subplot.params.row_dividers !== false}
                onCheckedChange={(checked) => updateParam('row_dividers', checked)}
              />
              <Label htmlFor="row-dividers" className="text-sm cursor-pointer">
                显示行分隔线
              </Label>
            </div>

            {/* 底部分隔线 */}
            <div className="flex items-center gap-2">
              <Checkbox
                id="footer-divider"
                checked={subplot.params.footer_divider !== false}
                onCheckedChange={(checked) => updateParam('footer_divider', checked)}
              />
              <Label htmlFor="footer-divider" className="text-sm cursor-pointer">
                显示底部分隔线
              </Label>
            </div>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">字体大小</h4>
            
            <div className="space-y-1.5">
              <Label htmlFor="fontsize" className="text-xs">
                表格字体大小
              </Label>
              <Input
                id="fontsize"
                type="number"
                min="6"
                max="24"
                value={subplot.params.fontsize || 10}
                onChange={(e) => updateParam('fontsize', parseInt(e.target.value) || 10)}
                className="h-8 text-sm"
              />
            </div>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">单元格绘制控制</h4>

            <p className="text-xs text-gray-500">可以选择跳过某些行的单元格内图表绘制（这些行仍会应用 formatter）。</p>

            {/* 排除行选择：基于 data.index 列表渲染多选 */}
            <div className="space-y-2 pt-2">
              { (!subplot.data.index || subplot.data.index.length === 0) ? (
                <p className="text-xs text-gray-500">当前数据没有索引信息，无法选择要排除的行。</p>
              ) : (
                <div className="space-y-2">
                  <div className="grid grid-cols-2 gap-2 max-h-40 overflow-auto border rounded-md p-2">
                    {subplot.data.index.map((idx: any, i: number) => {
                      // 将索引值转换为字符串（支持数字或字符串索引）
                      const idxStr = String(idx);
                      const selected: string[] = subplot.params.exclude_plot_rows || [];
                      const checked = selected.includes(idxStr);
                      return (
                        <div key={i} className="flex items-center gap-2">
                          <Checkbox
                            id={`exclude-row-${i}`}
                            checked={checked}
                            onCheckedChange={(c) => {
                              const prev: string[] = subplot.params.exclude_plot_rows || [];
                              let next: string[] = [];
                              if (c) {
                                next = Array.from(new Set([...prev, idxStr]));
                              } else {
                                next = prev.filter(x => x !== idxStr);
                              }
                              updateParam('exclude_plot_rows', next.length > 0 ? next : undefined);
                            }}
                          />
                          <Label htmlFor={`exclude-row-${i}`} className="text-xs cursor-pointer truncate">
                            {idxStr}
                          </Label>
                        </div>
                      );
                    })}
                  </div>
                  <p className="text-xs text-gray-500">
                    已选择 {(subplot.params.exclude_plot_rows || []).length} 行
                  </p>
                </div>
              ) }
            </div>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">指定行颜色</h4>
            
            <p className="text-xs text-gray-500">为特定行设置背景色和字体色（例如：总计行、合计行）</p>

            {/* 行背景色配置 */}
            <div className="space-y-2 pt-2">
              <Label className="text-xs font-medium">行背景色 (row_facecolors)</Label>
              <div className="space-y-2">
                {Object.entries(subplot.params.row_facecolors || {}).map(([rowName, color], idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <Input
                      value={rowName}
                      onChange={(e) => {
                        const newRowName = e.target.value;
                        const colors = { ...(subplot.params.row_facecolors || {}) };
                        delete colors[rowName];
                        // 允许空值，仅在用户删除该行时才移除配置
                        colors[newRowName] = color as string;
                        updateParam('row_facecolors', colors);
                      }}
                      placeholder="行名称（如：总计）"
                      className="h-8 text-xs flex-1"
                    />
                    <ColorPicker
                      value={(color as string) || '#C0C0C0'}
                      onChange={(newColor) => {
                        const colors = { ...(subplot.params.row_facecolors || {}), [rowName]: newColor };
                        updateParam('row_facecolors', colors);
                      }}
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const colors = { ...(subplot.params.row_facecolors || {}) };
                        delete colors[rowName];
                        updateParam('row_facecolors', Object.keys(colors).length > 0 ? colors : undefined);
                      }}
                      className="h-8 w-8 p-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const existing = subplot.params.row_facecolors || {};
                    // 生成唯一的键名
                    let newKey = '新行';
                    let counter = 1;
                    while (existing[newKey]) {
                      newKey = `新行${counter}`;
                      counter++;
                    }
                    const colors = { ...existing, [newKey]: 'silver' };
                    updateParam('row_facecolors', colors);
                  }}
                  className="h-8 text-xs"
                >
                  <Plus className="h-4 w-4 mr-1" /> 添加行背景色
                </Button>
              </div>
            </div>

            {/* 行字体色配置 */}
            <div className="space-y-2 pt-2">
              <Label className="text-xs font-medium">行字体色 (row_fontcolors)</Label>
              <div className="space-y-2">
                {Object.entries(subplot.params.row_fontcolors || {}).map(([rowName, color], idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <Input
                      value={rowName}
                      onChange={(e) => {
                        const newRowName = e.target.value;
                        const colors = { ...(subplot.params.row_fontcolors || {}) };
                        delete colors[rowName];
                        // 允许空值，仅在用户删除该行时才移除配置
                        colors[newRowName] = color as string;
                        updateParam('row_fontcolors', colors);
                      }}
                      placeholder="行名称（如：总计）"
                      className="h-8 text-xs flex-1"
                    />
                    <ColorPicker
                      value={(color as string) || '#000000'}
                      onChange={(newColor) => {
                        const colors = { ...(subplot.params.row_fontcolors || {}), [rowName]: newColor };
                        updateParam('row_fontcolors', colors);
                      }}
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const colors = { ...(subplot.params.row_fontcolors || {}) };
                        delete colors[rowName];
                        updateParam('row_fontcolors', Object.keys(colors).length > 0 ? colors : undefined);
                      }}
                      className="h-8 w-8 p-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const existing = subplot.params.row_fontcolors || {};
                    // 生成唯一的键名
                    let newKey = '新行';
                    let counter = 1;
                    while (existing[newKey]) {
                      newKey = `新行${counter}`;
                      counter++;
                    }
                    const colors = { ...existing, [newKey]: 'black' };
                    updateParam('row_fontcolors', colors);
                  }}
                  className="h-8 text-xs"
                >
                  <Plus className="h-4 w-4 mr-1" /> 添加行字体色
                </Button>
              </div>
            </div>
          </div>

          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md mt-4">
            <p className="text-xs text-blue-700">
              💡 提示：更多高级功能（如颜色映射、子图绘制）正在开发中
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
