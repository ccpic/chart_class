'use client';

import { useState } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import MainContent from '@/components/layout/MainContent';
import RightPanel from '@/components/layout/RightPanel';
import GridControls from '@/components/canvas/GridControls';
import GridPreview from '@/components/canvas/GridPreview';
import RenderButton from '@/components/canvas/RenderButton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Download, Grid3x3, Eye, Info, AlertCircle, Palette } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function CanvasPage() {
  const { canvas, subplots } = useCanvasStore();
  const [renderedImage, setRenderedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('grid');

  const handleRenderComplete = (imageUrl: string) => {
    setRenderedImage(imageUrl);
    setError(null);
    // 自动跳转到渲染结果 tab
    setActiveTab('render');
  };

  const handleRenderError = (errorMessage: string) => {
    setError(errorMessage);
    setRenderedImage(null);
  };

  const handleDownload = () => {
    if (!renderedImage) return;
    
    const link = document.createElement('a');
    link.href = renderedImage;
    link.download = `canvas-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex h-full w-full">
      {/* 中心内容区：Tabs 布局 */}
      <MainContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-full w-full">
          {/* Tab 头部 */}
          <div className="border-b bg-white px-4 py-2 flex-shrink-0">
            <div className="flex items-center justify-between">
              <TabsList className="grid max-w-md grid-cols-2">
                <TabsTrigger value="grid" className="gap-2">
                  <Grid3x3 className="h-4 w-4" />
                  网格布局
                </TabsTrigger>
                <TabsTrigger value="render" className="gap-2">
                  <Eye className="h-4 w-4" />
                  渲染结果
                </TabsTrigger>
              </TabsList>
              
              {/* 渲染和下载按钮 */}
              <div className="flex items-center gap-2">
                <RenderButton
                  onRenderComplete={handleRenderComplete}
                  onRenderError={handleRenderError}
                />
                {renderedImage && (
                  <Button
                    onClick={handleDownload}
                    variant="outline"
                    size="sm"
                    className="gap-2"
                  >
                    <Download className="h-4 w-4" />
                    下载图片
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Tab 1: 网格布局 */}
          <TabsContent 
            value="grid" 
            className="m-0 p-6 flex-1 data-[state=active]:flex data-[state=active]:flex-col"
          >
            <div className="flex flex-col h-full gap-4">
              <div className="flex items-center justify-between flex-shrink-0">
                <div>
                  <h2 className="text-xl font-bold">网格预览</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {canvas.rows} × {canvas.cols} 网格 | {subplots.length} 个子图
                  </p>
                </div>
              </div>
              
              <div className="flex-1 min-h-0">
                <GridPreview />
              </div>
              
              {/* 数据状态提示 */}
              {subplots.length > 0 && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-md flex-shrink-0">
                  <p className="text-sm text-blue-700 flex items-center gap-2">
                    <Info className="h-4 w-4" />
                    数据状态：
                    {subplots.every(s => s.data.columns.length > 0 && s.data.data.length > 0)
                      ? ' 所有子图数据已配置完整 ✓'
                      : ` ${subplots.filter(s => s.data.columns.length > 0 && s.data.data.length > 0).length}/${subplots.length} 个子图已配置数据`}
                  </p>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Tab 2: 渲染结果 */}
          <TabsContent 
            value="render" 
            className="m-0 p-6 flex-1 data-[state=active]:flex data-[state=active]:flex-col"
          >
            <div className="flex flex-col h-full gap-4">
              <div className="flex items-center justify-between flex-shrink-0">
                <div>
                  <h2 className="text-xl font-bold">渲染结果</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    点击"渲染画布"生成图表
                  </p>
                </div>
              </div>

              {/* 错误提示 */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-md flex-shrink-0">
                  <p className="text-sm text-red-600 flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" />
                    {error}
                  </p>
                </div>
              )}

              {/* 渲染结果显示区 */}
              <div className="flex-1 bg-white rounded-lg border overflow-hidden">
                {!renderedImage && !error && (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <Palette className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-lg font-medium text-gray-700 mb-2">
                        准备好渲染画布了吗？
                      </p>
                      <p className="text-sm text-gray-500">
                        {subplots.length === 0
                          ? '请先在"网格布局"标签页添加子图'
                          : `当前已添加 ${subplots.length} 个子图，点击上方"渲染画布"按钮`}
                      </p>
                    </div>
                  </div>
                )}

                {renderedImage && (
                  <div className="w-full h-full flex items-center justify-center p-4">
                    <img
                      src={renderedImage}
                      alt="Rendered Canvas"
                      className="max-w-full max-h-full object-contain"
                    />
                  </div>
                )}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </MainContent>

      {/* 右侧参数面板：画布设置 */}
      <RightPanel>
        <div className="h-full overflow-y-auto p-4">
          <h2 className="text-lg font-semibold mb-4">画布设置</h2>
          <GridControls />
        </div>
      </RightPanel>
    </div>
  );
}
