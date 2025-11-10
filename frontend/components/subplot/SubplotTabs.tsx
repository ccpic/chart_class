'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SubplotConfig } from '@/types/canvas';
import { Eye, Table2, FileJson, Loader2, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCanvasStore } from '@/store/canvasStore';
import { renderSubplot } from '@/lib/api';
import Image from 'next/image';
import { Textarea } from '@/components/ui/textarea';
import { AlertCircle, BarChart3, Info, Save, RotateCcw } from 'lucide-react';
import DataGridEditor from './DataGridEditor';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 子图编辑 Tabs - 重构版
 * 三个并列 tabs：渲染预览、表格编辑、JSON 编辑
 */
export default function SubplotTabs({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  // 渲染相关状态
  const [isRendering, setIsRendering] = useState(false);
  const [renderedImage, setRenderedImage] = useState<string | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);

  // JSON 编辑相关状态
  const [jsonText, setJsonText] = useState(JSON.stringify(subplot.data, null, 2));
  const [jsonError, setJsonError] = useState<string | null>(null);

  const hasData =
    subplot.data.columns &&
    subplot.data.columns.length > 0 &&
    subplot.data.data &&
    subplot.data.data.length > 0;

  // 渲染子图
  const handleRender = async () => {
    setIsRendering(true);
    setRenderError(null);

    try {
      const blob = await renderSubplot(subplot);
      const imageUrl = URL.createObjectURL(blob);
      setRenderedImage(imageUrl);
    } catch (err) {
      setRenderError(err instanceof Error ? err.message : '渲染失败');
    } finally {
      setIsRendering(false);
    }
  };

  // 清空数据
  const handleClearData = () => {
    const emptyData = {
      columns: [],
      index: [],
      data: []
    };
    updateSubplot(subplot.subplotId, { data: emptyData });
    setJsonText(JSON.stringify(emptyData, null, 2));
    setRenderedImage(null);
    setRenderError(null);
    setJsonError(null);
  };

  // 表格数据变化
  const handleGridChange = (newData: { columns: string[]; index: string[]; data: any[][] }) => {
    updateSubplot(subplot.subplotId, { data: newData });
    setJsonText(JSON.stringify(newData, null, 2));
    setJsonError(null);
  };

  // JSON 保存
  const handleJsonSave = () => {
    try {
      const parsedData = JSON.parse(jsonText);
      
      if (!parsedData.columns || !Array.isArray(parsedData.columns)) {
        throw new Error('缺少 columns 字段或格式错误');
      }
      if (!parsedData.data || !Array.isArray(parsedData.data)) {
        throw new Error('缺少 data 字段或格式错误');
      }

      // 如果没有 index，生成默认值
      if (!parsedData.index) {
        parsedData.index = parsedData.data.map((_: any, i: number) => `行${i + 1}`);
      }

      updateSubplot(subplot.subplotId, { data: parsedData });
      setJsonError(null);
    } catch (err) {
      setJsonError(err instanceof Error ? err.message : '数据格式错误');
    }
  };

  // JSON 重置
  const handleJsonReset = () => {
    setJsonText(JSON.stringify(subplot.data, null, 2));
    setJsonError(null);
  };

  return (
    <div className="h-full flex flex-col">
      {/* 顶部操作栏 */}
      <div className="px-6 pt-4 pb-3 border-b bg-white flex items-center gap-3 flex-shrink-0">
        <Button
          onClick={handleRender}
          disabled={!hasData || isRendering}
          className="gap-2"
        >
          {isRendering ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              渲染中...
            </>
          ) : (
            <>
              <Eye className="h-4 w-4" />
              渲染预览
            </>
          )}
        </Button>

        <Button
          onClick={handleClearData}
          variant="outline"
          className="gap-2"
        >
          <Trash2 className="h-4 w-4" />
          清空数据
        </Button>

        <div className="ml-auto text-sm text-gray-600">
          {hasData 
            ? `${subplot.data.columns.length} 列 × ${subplot.data.data.length} 行`
            : '未配置数据'}
        </div>
      </div>

      {/* Tabs 区域 */}
      <Tabs defaultValue="preview" className="flex-1 flex flex-col">
        <TabsList className="mx-6 mt-4 flex-shrink-0">
          <TabsTrigger value="preview" className="gap-2">
            <Eye className="h-4 w-4" />
            渲染预览
          </TabsTrigger>
          <TabsTrigger value="grid" className="gap-2">
            <Table2 className="h-4 w-4" />
            表格编辑
          </TabsTrigger>
          <TabsTrigger value="json" className="gap-2">
            <FileJson className="h-4 w-4" />
            JSON 编辑
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: 渲染预览 */}
        <TabsContent value="preview" className="flex-1 overflow-auto mt-0 px-6 pb-6 pt-4">
          <div className="space-y-4">
            {/* 错误提示 */}
            {renderError && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  {renderError}
                </p>
              </div>
            )}

            {/* 渲染结果或空状态 */}
            {renderedImage ? (
              <div className="bg-white rounded-lg border overflow-hidden">
                <Image
                  src={renderedImage}
                  alt="Subplot Preview"
                  width={800}
                  height={600}
                  className="w-full h-auto"
                  unoptimized
                />
              </div>
            ) : (
              <div className="flex items-center justify-center h-[400px] bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <div className="text-center">
                  <BarChart3 className="h-16 w-16 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-700 font-medium mb-1">
                    {hasData ? '点击上方"渲染预览"按钮查看图表' : '请先配置数据'}
                  </p>
                  <p className="text-sm text-gray-500">
                    图表类型：{subplot.chartType}
                  </p>
                </div>
              </div>
            )}
          </div>
        </TabsContent>

        {/* Tab 2: 表格编辑 */}
        <TabsContent value="grid" className="flex-1 overflow-auto mt-0 px-6 pb-6 pt-4">
          <DataGridEditor 
            data={subplot.data} 
            onChange={handleGridChange}
          />
        </TabsContent>

        {/* Tab 3: JSON 编辑 */}
        <TabsContent value="json" className="flex-1 overflow-auto mt-0 px-6 pb-6 pt-4">
          <div className="space-y-4">
            {/* 说明文字 */}
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-700 flex items-center gap-2">
                <Info className="h-4 w-4" />
                编辑 JSON 数据，格式：<code className="mx-1 px-1 bg-blue-100 rounded">
                  &#123;"columns": [...], "index": [...], "data": [...]&#125;
                </code>
              </p>
            </div>

            {/* JSON 编辑器 */}
            <Textarea
              value={jsonText}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJsonText(e.target.value)}
              placeholder='{"columns": ["A", "B"], "index": ["行1", "行2"], "data": [[1, 2], [3, 4]]}'
              className="font-mono text-sm min-h-[400px]"
            />

            {/* 错误提示 */}
            {jsonError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  {jsonError}
                </p>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex gap-2">
              <Button onClick={handleJsonSave} className="flex-1 gap-2">
                <Save className="h-4 w-4" />
                保存数据
              </Button>
              <Button onClick={handleJsonReset} variant="outline" className="flex-1 gap-2">
                <RotateCcw className="h-4 w-4" />
                重置
              </Button>
            </div>

            {/* 数据统计 */}
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
              <p className="text-xs text-gray-600">
                当前数据：
                {subplot.data.columns?.length || 0} 列 ×{' '}
                {subplot.data.data?.length || 0} 行
              </p>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

