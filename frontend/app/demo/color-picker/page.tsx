'use client';

import React, { useState } from 'react';
import ColorPicker from '@/components/color/ColorPicker';

/**
 * ColorPicker 组件测试页面
 * 
 * 测试优化后的功能：
 * 1. 无横向/纵向滚动条溢出
 * 2. 智能 tooltip 定位（边缘和角落）
 * 3. 命名颜色选择和保存
 */
export default function ColorPickerDemo() {
  const [color1, setColor1] = useState('#FF5733');
  const [color2, setColor2] = useState('#800080');
  const [color3, setColor3] = useState('#1f77b4');
  const [lastSelectedName, setLastSelectedName] = useState<string>('');

  const handleColorChange = (color: string, namedColor?: string) => {
    setLastSelectedName(namedColor || '未命名');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">ColorPicker 优化测试</h1>
          <p className="text-gray-600">
            测试命名颜色面板的滚动条和 tooltip 显示优化
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">功能测试</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 测试 1: 完整颜色值显示 */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  测试 1: 显示颜色值
                </h3>
                <ColorPicker
                  label="带颜色值的选择器"
                  value={color1}
                  onChange={(color, name) => {
                    setColor1(color);
                    handleColorChange(color, name);
                  }}
                  showColorValue={true}
                />
                <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
                  <p><strong>当前值:</strong> {color1}</p>
                </div>
              </div>

              {/* 测试 2: 仅色块显示 */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  测试 2: 仅显示色块
                </h3>
                <ColorPicker
                  label="仅色块选择器"
                  value={color2}
                  onChange={(color, name) => {
                    setColor2(color);
                    handleColorChange(color, name);
                  }}
                  showColorValue={false}
                />
                <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
                  <p><strong>当前值:</strong> {color2}</p>
                  <p><strong>命名颜色:</strong> {lastSelectedName}</p>
                </div>
              </div>

              {/* 测试 3: Tableau 颜色 */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  测试 3: Tableau 调色板
                </h3>
                <ColorPicker
                  label="Tableau 色系"
                  value={color3}
                  onChange={(color, name) => {
                    setColor3(color);
                    handleColorChange(color, name);
                  }}
                />
                <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
                  <p><strong>当前值:</strong> {color3}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t">
            <h2 className="text-xl font-semibold mb-4">优化点说明</h2>
            <div className="space-y-3 text-sm">
              <div className="p-3 bg-blue-50 rounded">
                <h4 className="font-semibold text-blue-900 mb-1">✅ 滚动条优化</h4>
                <ul className="text-blue-800 space-y-1 ml-4 list-disc">
                  <li>固定 16 列网格布局，避免横向滚动</li>
                  <li>使用 <code className="bg-white px-1 rounded">overflow-y-auto overflow-x-hidden</code></li>
                  <li>色块大小固定为 20px (w-5 h-5)</li>
                </ul>
              </div>

              <div className="p-3 bg-green-50 rounded">
                <h4 className="font-semibold text-green-900 mb-1">✅ Tooltip 智能定位</h4>
                <ul className="text-green-800 space-y-1 ml-4 list-disc">
                  <li><strong>垂直方向:</strong> 前 3 行显示在下方，其他行显示在上方</li>
                  <li><strong>水平方向:</strong> 左侧 3 列左对齐，右侧 3 列右对齐，中间居中</li>
                  <li><strong>层级:</strong> 使用 <code className="bg-white px-1 rounded">z-50</code> 确保 tooltip 始终在最上层</li>
                  <li><strong>箭头:</strong> 根据对齐方式智能调整箭头位置</li>
                </ul>
              </div>

              <div className="p-3 bg-purple-50 rounded">
                <h4 className="font-semibold text-purple-900 mb-1">✅ 智能颜色排序</h4>
                <ul className="text-purple-800 space-y-1 ml-4 list-disc">
                  <li><strong>色相优先:</strong> 按照色轮顺序（红→橙→黄→绿→青→蓝→紫）</li>
                  <li><strong>饱和度次之:</strong> 同色系内，灰色在前，鲜艳在后</li>
                  <li><strong>亮度最后:</strong> 饱和度相同时，从暗到亮排列</li>
                  <li><strong>视觉效果:</strong> 颜色渐变自然，相似颜色聚集</li>
                </ul>
              </div>

              <div className="p-3 bg-orange-50 rounded">
                <h4 className="font-semibold text-orange-900 mb-1">✅ 交互优化</h4>
                <ul className="text-orange-800 space-y-1 ml-4 list-disc">
                  <li>鼠标悬停时色块放大 1.5 倍 (<code className="bg-white px-1 rounded">hover:scale-150</code>)</li>
                  <li>添加阴影增强视觉反馈</li>
                  <li>Tooltip 使用 <code className="bg-white px-1 rounded">pointer-events-none</code> 避免干扰点击</li>
                  <li>当前选中颜色显示 ✓ 标记</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t">
            <h2 className="text-xl font-semibold mb-4">测试建议</h2>
            <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
              <h4 className="font-semibold text-yellow-900 mb-2">🧪 如何测试</h4>
              <ol className="text-sm text-yellow-800 space-y-2 ml-4 list-decimal">
                <li>
                  <strong>滚动条测试:</strong> 
                  <ul className="ml-4 mt-1 space-y-1 list-disc">
                    <li>点击任意颜色选择器</li>
                    <li>切换到"命名颜色"标签页</li>
                    <li>验证只有纵向滚动条，无横向滚动条</li>
                    <li>滚动查看所有颜色（约 150+ 个）</li>
                  </ul>
                </li>
                <li>
                  <strong>Tooltip 定位测试:</strong>
                  <ul className="ml-4 mt-1 space-y-1 list-disc">
                    <li>将鼠标悬停在第一行（最上方）的色块 → tooltip 应显示在下方</li>
                    <li>将鼠标悬停在最左列的色块 → tooltip 应左对齐</li>
                    <li>将鼠标悬停在最右列的色块 → tooltip 应右对齐</li>
                    <li>将鼠标悬停在中间区域 → tooltip 应居中显示</li>
                    <li>滚动到底部，悬停色块 → tooltip 应显示在上方</li>
                  </ul>
                </li>
                <li>
                  <strong>命名颜色保存测试:</strong>
                  <ul className="ml-4 mt-1 space-y-1 list-disc">
                    <li>选择一个命名颜色（如 "purple"）</li>
                    <li>查看"测试 2"下方的"命名颜色"应显示颜色名称</li>
                    <li>选择调色板中的自定义颜色 → 命名颜色应显示"未命名"</li>
                  </ul>
                </li>
                <li>
                  <strong>搜索功能测试:</strong>
                  <ul className="ml-4 mt-1 space-y-1 list-disc">
                    <li>在搜索框输入 "blue" → 应只显示包含 blue 的颜色</li>
                    <li>清空搜索框 → 应恢复显示所有颜色</li>
                  </ul>
                </li>
              </ol>
            </div>
          </div>
        </div>

        <div className="bg-gray-100 border border-gray-300 rounded-lg p-4">
          <h3 className="font-semibold mb-2">💡 技术实现细节</h3>
          <div className="text-sm space-y-3">
            <div>
              <p className="font-semibold mb-1">网格布局</p>
              <code className="bg-white px-2 py-1 rounded block">grid grid-cols-16</code>
              <p className="text-xs text-gray-600 mt-1">16 列固定网格，每个色块 20×20px</p>
            </div>

            <div>
              <p className="font-semibold mb-1">滚动控制</p>
              <code className="bg-white px-2 py-1 rounded block">overflow-y-auto overflow-x-hidden</code>
              <p className="text-xs text-gray-600 mt-1">仅允许垂直滚动，禁用横向滚动</p>
            </div>

            <div>
              <p className="font-semibold mb-1">智能颜色排序算法 (HSL 色彩空间)</p>
              <pre className="bg-white p-3 rounded mt-1 text-xs overflow-x-auto">
{`// 将 HEX 转换为 HSL
const hexToHSL = (hex) => {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  
  // 计算色相 (Hue)、饱和度 (Saturation)、亮度 (Lightness)
  // ...
  
  return { h: 0-360, s: 0-100, l: 0-100 };
};

// 三级排序
colors.sort((a, b) => {
  const hslA = hexToHSL(a[1]);
  const hslB = hexToHSL(b[1]);
  
  // 1. 优先按色相排序 (色轮顺序)
  if (hslA.h !== hslB.h) return hslA.h - hslB.h;
  
  // 2. 色相相同，按饱和度 (灰→鲜艳)
  if (hslA.s !== hslB.s) return hslA.s - hslB.s;
  
  // 3. 最后按亮度 (暗→亮)
  return hslA.l - hslB.l;
});`}
              </pre>
              <p className="text-xs text-gray-600 mt-2">
                <strong>为什么用 HSL？</strong><br/>
                - 色相 (H): 表示颜色类型（红/绿/蓝等），按色轮顺序排列更自然<br/>
                - 饱和度 (S): 表示颜色鲜艳程度，同色系内从灰到鲜艳渐变<br/>
                - 亮度 (L): 表示明暗程度，最后按亮度排序使过渡更平滑
              </p>
            </div>

            <div>
              <p className="font-semibold mb-1">Tooltip 智能定位算法</p>
              <pre className="bg-white p-3 rounded mt-1 text-xs overflow-x-auto">
{`const row = Math.floor(index / 16);
const col = index % 16;

// 垂直定位
if (row < 3) tooltipPosition = 'top-full mt-1';    // 上方 3 行 → 下方显示
else tooltipPosition = 'bottom-full mb-1';          // 其他行 → 上方显示

// 水平对齐
if (col < 3) horizontalAlign = 'left-0';            // 左侧 3 列 → 左对齐
else if (col >= 13) horizontalAlign = 'right-0';    // 右侧 3 列 → 右对齐
else horizontalAlign = 'left-1/2 -translate-x-1/2'; // 中间 → 居中对齐`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
