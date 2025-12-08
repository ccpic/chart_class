'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCanvasStore } from '@/store/canvasStore';
import { ChartType } from '@/types/canvas';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  BarChart3,
  BarChart2,
  LineChart,
  PieChart,
  AreaChart,
  Droplets,
  Table2,
  Trash2,
  Box,
  Filter,
  TrendingUp,
  Map,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import DeleteSubplotDialog from './DeleteSubplotDialog';
import { CHART_TYPE_LABELS } from '@/constants/chartTypes';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { getChartTypeName } from '@/constants/chartTypes';

// 图表类型图标映射
const CHART_TYPE_ICONS: Record<ChartType, React.ReactNode> = {
  bar: <BarChart3 className="h-4 w-4" />,
  barh: <BarChart2 className="h-4 w-4 rotate-90" />,
  line: <LineChart className="h-4 w-4" />,
  pie: <PieChart className="h-4 w-4" />,
  area: <AreaChart className="h-4 w-4" />,
  bubble: <Droplets className="h-4 w-4" />,
  hist: <BarChart3 className="h-4 w-4" />,
  boxdot: <Box className="h-4 w-4" />,
  funnel: <Filter className="h-4 w-4" />,
  waterfall: <TrendingUp className="h-4 w-4" />,
  table: <Table2 className="h-4 w-4" />,
  map: <Map className="h-4 w-4" />,
};

export default function GridPreview() {
  const router = useRouter();
  const { canvas, subplots, addSubplot, cloneSubplotConfig, getSubplotByAxIndex, updateSubplot, updateCanvas, deleteSubplot } = useCanvasStore();
  const [pendingChartTypes, setPendingChartTypes] = useState<Record<number, ChartType>>({});
  const [pendingCloneSource, setPendingCloneSource] = useState<Record<number, string>>({});
  
  const { rows, cols } = canvas;
  const totalCells = rows * cols;
  
  // 生成网格单元格
  const cells = Array.from({ length: totalCells }, (_, i) => i);
  
  // 初始化宽高比例数组（如果未设置）
  const widthRatios = canvas.widthRatios || Array(cols).fill(1);
  const heightRatios = canvas.heightRatios || Array(rows).fill(1);
  
  const handleChartTypeSelect = (axIndex: number, chartType: ChartType) => {
    const subplot = getSubplotByAxIndex(axIndex);
    
    if (subplot) {
      // 更新已有子图的类型
      updateSubplot(subplot.subplotId, { chartType });
    } else {
      // 保存待创建子图的类型
      setPendingChartTypes(prev => ({ ...prev, [axIndex]: chartType }));
    }
  };
  
  // 更新列宽比例
  const handleWidthRatioChange = (colIndex: number, value: number) => {
    const newRatios = [...widthRatios];
    newRatios[colIndex] = value;
    updateCanvas({ widthRatios: newRatios });
  };
  
  // 更新行高比例
  const handleHeightRatioChange = (rowIndex: number, value: number) => {
    const newRatios = [...heightRatios];
    newRatios[rowIndex] = value;
    updateCanvas({ heightRatios: newRatios });
  };
  
  const handleCreateSubplot = (axIndex: number) => {
    const chartType = pendingChartTypes[axIndex] || 'bar';
    addSubplot(axIndex, chartType);
    
    // 清除待定类型
    setPendingChartTypes(prev => {
      const newState = { ...prev };
      delete newState[axIndex];
      return newState;
    });
    
    // 跳转到子图编辑页面
    const newSubplot = getSubplotByAxIndex(axIndex);
    if (newSubplot) {
      router.push(`/subplot/${newSubplot.subplotId}`);
    }
  };
  
  const handleEditSubplot = (subplotId: string) => {
    router.push(`/subplot/${subplotId}`);
  };
  
  const handleDeleteSubplot = (subplotId: string, axIndex: number) => {
    deleteSubplot(subplotId);
    // 清除该位置的待定类型
    setPendingChartTypes(prev => {
      const newState = { ...prev };
      delete newState[axIndex];
      return newState;
    });
  };

  const handleCloneSourceSelect = (axIndex: number, sourceSubplotId: string) => {
    setPendingCloneSource(prev => ({ ...prev, [axIndex]: sourceSubplotId }));
  };

  const handleConfirmClone = (axIndex: number) => {
    const sourceSubplotId = pendingCloneSource[axIndex];
    if (!sourceSubplotId) return;

    cloneSubplotConfig(sourceSubplotId, axIndex);
    
    // 清除待定克隆源
    setPendingCloneSource(prev => {
      const newState = { ...prev };
      delete newState[axIndex];
      return newState;
    });
    
    // 跳转到新创建的子图编辑页面
    const newSubplot = getSubplotByAxIndex(axIndex);
    if (newSubplot) {
      router.push(`/subplot/${newSubplot.subplotId}`);
    }
  };
  
  return (
    <div className="h-full flex flex-col gap-4">
      <div className="flex items-center justify-between flex-shrink-0">
        <h3 className="text-sm font-semibold">网格布局 ({rows}×{cols})</h3>
        <div className="text-xs text-gray-500">
          已用 {subplots.length}/{totalCells} 个单元格
        </div>
      </div>
      
      {/* 列宽比例设置 */}
      {cols > 1 && (
        <div className="flex items-center gap-2 flex-shrink-0 bg-gray-50 border border-gray-200 p-3 rounded-lg">
          <span className="text-xs font-medium text-gray-700 whitespace-nowrap">列宽比例:</span>
          {widthRatios.map((ratio, colIndex) => (
            <div key={colIndex} className="flex items-center gap-1">
              <label className="text-xs text-gray-600">列{colIndex + 1}</label>
              <input
                type="number"
                min="0.1"
                max="10"
                step="0.1"
                value={ratio}
                onChange={(e) => handleWidthRatioChange(colIndex, parseFloat(e.target.value) || 1)}
                className="w-16 px-2 py-1 text-xs border rounded"
              />
            </div>
          ))}
          <span className="text-xs text-gray-500 ml-2">
            (数值越大，该列越宽)
          </span>
        </div>
      )}
      
      {/* 行高比例设置 */}
      {rows > 1 && (
        <div className="flex items-center gap-2 flex-shrink-0 bg-gray-50 border border-gray-200 p-3 rounded-lg">
          <span className="text-xs font-medium text-gray-700 whitespace-nowrap">行高比例:</span>
          {heightRatios.map((ratio, rowIndex) => (
            <div key={rowIndex} className="flex items-center gap-1">
              <label className="text-xs text-gray-600">行{rowIndex + 1}</label>
              <input
                type="number"
                min="0.1"
                max="10"
                step="0.1"
                value={ratio}
                onChange={(e) => handleHeightRatioChange(rowIndex, parseFloat(e.target.value) || 1)}
                className="w-16 px-2 py-1 text-xs border rounded"
              />
            </div>
          ))}
          <span className="text-xs text-gray-500 ml-2">
            (数值越大，该行越高)
          </span>
        </div>
      )}
      
      <div 
        className="grid gap-3 bg-gray-50 p-4 rounded-lg flex-1 min-h-0"
        style={{
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gridTemplateRows: `repeat(${rows}, 1fr)`,
        }}
      >
        {cells.map((axIndex) => {
          const subplot = getSubplotByAxIndex(axIndex);
          const pendingType = pendingChartTypes[axIndex];
          
          return (
            <div
              key={axIndex}
              className={`
                border-2 rounded-lg p-3 transition-all
                flex flex-col gap-2
                min-h-0
                ${subplot 
                  ? 'bg-white border-gray-400' 
                  : 'bg-gray-100 border-dashed border-gray-300'
                }
              `}
            >
              {/* 图表类型选择器 */}
              <div className="space-y-1 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                <label className="text-xs font-medium text-gray-600">
                  {subplot ? '图表类型' : '选择图表类型'}
                </label>
                <Select
                  value={subplot?.chartType || pendingType || ''}
                  onValueChange={(value: string) => handleChartTypeSelect(axIndex, value as ChartType)}
                >
                  <SelectTrigger className="h-9 text-sm">
                    <SelectValue placeholder="请选择..." />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(CHART_TYPE_LABELS).map(([type, label]) => (
                      <SelectItem key={type} value={type} className="text-sm">
                        <div className="flex items-center gap-2">
                          {CHART_TYPE_ICONS[type as ChartType]}
                          <span>{label}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* 单元格信息 */}
              <div className="flex-1 flex flex-col items-center justify-center min-h-0">
                {subplot ? (
                  <>
                    <div className="text-xs text-gray-500 mb-1">
                      位置 {axIndex + 1}
                    </div>
                    {subplot.data.columns.length > 0 && (
                      <div className="text-xs text-green-600">
                        ✓ 已配置数据
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-xs text-gray-400">
                    位置 {axIndex + 1}
                  </div>
                )}
              </div>
              
              {/* 克隆选项 - 所有单元格都显示（如果有其他子图且不是自己） */}
              {subplots.length > 0 && subplots.some(sp => sp.subplotId !== subplot?.subplotId) && (
                <div className="space-y-1.5 border-t pt-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                  <label className="text-xs font-medium text-gray-600">
                    {subplot ? '克隆其他子图（覆盖当前配置）' : '或克隆已有子图'}
                  </label>
                  <Select
                    value={pendingCloneSource[axIndex] || ''}
                    onValueChange={(value) => handleCloneSourceSelect(axIndex, value)}
                  >
                    <SelectTrigger className="h-9 text-sm">
                      <SelectValue placeholder="选择要克隆的子图..." />
                    </SelectTrigger>
                    <SelectContent>
                      {subplots
                        .filter(sp => sp.subplotId !== subplot?.subplotId) // 排除自己
                        .map((sp) => (
                          <SelectItem key={sp.subplotId} value={sp.subplotId} className="text-sm">
                            <div className="flex items-center gap-2">
                              {CHART_TYPE_ICONS[sp.chartType]}
                              <span>
                                位置 {sp.axIndex + 1} - {getChartTypeName(sp.chartType)}
                                {sp.data.columns.length > 0 && ' (已配置)'}
                              </span>
                            </div>
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* 操作按钮 */}
              {subplot ? (
                <div className="flex gap-2 flex-shrink-0">
                  {pendingCloneSource[axIndex] ? (
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <button
                          className="flex-1 px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded transition-colors border border-blue-600"
                        >
                          克隆并覆盖
                        </button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>确认克隆并覆盖</AlertDialogTitle>
                          <AlertDialogDescription>
                            {(() => {
                              const sourceSubplot = subplots.find(s => s.subplotId === pendingCloneSource[axIndex]);
                              if (!sourceSubplot) return '';
                              return `确定要用位置 ${sourceSubplot.axIndex + 1} 的 ${getChartTypeName(sourceSubplot.chartType)} 子图的所有配置（包括数据、参数等）覆盖当前位置 ${axIndex + 1} 的子图吗？此操作将替换当前子图的所有配置，无法撤销。`;
                            })()}
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel
                            onClick={() => {
                              setPendingCloneSource(prev => {
                                const newState = { ...prev };
                                delete newState[axIndex];
                                return newState;
                              });
                            }}
                          >
                            取消
                          </AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleConfirmClone(axIndex)}>
                            确认覆盖
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  ) : (
                    <button
                      onClick={() => handleEditSubplot(subplot.subplotId)}
                      className="flex-1 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded transition-colors"
                    >
                      编辑子图
                    </button>
                  )}
                  <DeleteSubplotDialog
                    subplot={subplot}
                    trigger={
                      <Button
                        variant="outline"
                        size="sm"
                        className="px-3 py-1.5 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200 hover:border-red-300"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    }
                    onConfirm={handleDeleteSubplot}
                  />
                </div>
              ) : (
                <div className="space-y-2 flex-shrink-0">
                  {/* 创建/克隆按钮 */}
                  {pendingCloneSource[axIndex] ? (
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <button
                          className="w-full px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded transition-colors flex-shrink-0 border border-blue-600"
                        >
                          克隆子图
                        </button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>确认克隆子图</AlertDialogTitle>
                          <AlertDialogDescription>
                            {(() => {
                              const sourceSubplot = subplots.find(s => s.subplotId === pendingCloneSource[axIndex]);
                              if (!sourceSubplot) return '';
                              return `确定要将位置 ${sourceSubplot.axIndex + 1} 的 ${getChartTypeName(sourceSubplot.chartType)} 子图的所有配置（包括数据、参数等）克隆到位置 ${axIndex + 1} 吗？`;
                            })()}
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel
                            onClick={() => {
                              setPendingCloneSource(prev => {
                                const newState = { ...prev };
                                delete newState[axIndex];
                                return newState;
                              });
                            }}
                          >
                            取消
                          </AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleConfirmClone(axIndex)}>
                            确认克隆
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  ) : (
                    <button
                      onClick={() => handleCreateSubplot(axIndex)}
                      disabled={!pendingType}
                      className={`
                        w-full px-3 py-1.5 text-sm font-medium rounded transition-colors flex-shrink-0 border
                        ${pendingType
                          ? 'text-white bg-gray-800 hover:bg-gray-900 border-gray-800'
                          : 'text-gray-400 bg-gray-200 border-gray-200 cursor-not-allowed'
                        }
                      `}
                    >
                      {pendingType ? '创建子图' : '先选择类型'}
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
