'use client';

import { useState, useEffect } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table2, FileJson, Info, AlertCircle, Save, RotateCcw } from 'lucide-react';
import DataGridEditor from './DataGridEditor';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 子图数据编辑标签页
 * 提供 Excel 表格和 JSON 两种编辑方式
 */
export default function SubplotDataTab({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  // 本地编辑状态
  const [jsonText, setJsonText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<'grid' | 'json'>('grid');

  // 初始化时加载数据
  useEffect(() => {
    setJsonText(JSON.stringify(subplot.data, null, 2));
  }, [subplot.subplotId]);

  // 当从 JSON 切换到 Grid 时，同步数据
  useEffect(() => {
    if (currentView === 'grid') {
      setJsonText(JSON.stringify(subplot.data, null, 2));
    }
  }, [currentView, subplot.data]);

  // DataGrid 数据变化处理
  const handleGridChange = (newData: { columns: string[]; index: string[]; data: any[][] }) => {
    updateSubplot(subplot.subplotId, { data: newData });
    setJsonText(JSON.stringify(newData, null, 2));
    setError(null);
  };

  // JSON 保存处理
  const handleJsonSave = () => {
    try {
      const parsedData = JSON.parse(jsonText);
      
      // 验证数据格式
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

      // 更新到 store
      updateSubplot(subplot.subplotId, { data: parsedData });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '数据格式错误');
    }
  };

  const handleJsonReset = () => {
    setJsonText(JSON.stringify(subplot.data, null, 2));
    setError(null);
  };

  return (
    <div className="h-full flex flex-col">
      <Tabs defaultValue="grid" className="flex-1 flex flex-col" onValueChange={(v) => setCurrentView(v as 'grid' | 'json')}>
        {/* Tab 头部 */}
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="grid" className="gap-2">
            <Table2 className="h-4 w-4" />
            表格编辑
          </TabsTrigger>
          <TabsTrigger value="json" className="gap-2">
            <FileJson className="h-4 w-4" />
            JSON 编辑
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: 表格编辑器 */}
        <TabsContent value="grid" className="flex-1 overflow-auto mt-4">
          <DataGridEditor 
            data={subplot.data} 
            onChange={handleGridChange}
          />
        </TabsContent>

        {/* Tab 2: JSON 编辑器 */}
        <TabsContent value="json" className="flex-1 overflow-auto mt-4">
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
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  {error}
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
