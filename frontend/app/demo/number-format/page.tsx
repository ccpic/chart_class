'use client';

import React, { useState } from 'react';
import NumberFormatEditor from '@/components/ui/number-format-editor';

/**
 * NumberFormatEditor 组件测试页面
 * 
 * 展示各种使用场景和配置
 */
export default function NumberFormatEditorDemo() {
  const [format1, setFormat1] = useState('{:,.0f}');
  const [format2, setFormat2] = useState('{:+,.2f}');
  const [format3, setFormat3] = useState('{:.1%}');
  const [format4, setFormat4] = useState('{:+.2%}');

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">NumberFormatEditor 组件演示</h1>
          <p className="text-gray-600">
            可视化 Python 数值格式化字符串编辑器
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 space-y-8">
          <div>
            <h2 className="text-xl font-semibold mb-4">基础示例</h2>
            
            <div className="space-y-6">
              {/* 示例 1: 默认格式 - 千位符，0位小数 */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  示例 1: 整数格式（默认）
                </h3>
                <NumberFormatEditor
                  label="整数格式"
                  value={format1}
                  onChange={setFormat1}
                />
                <div className="mt-4 p-3 bg-blue-50 rounded text-sm">
                  <p className="text-gray-700">
                    <strong>用途：</strong>显示整数，如人口、数量等
                  </p>
                  <p className="text-gray-600 mt-1">
                    <strong>格式：</strong><code className="bg-white px-1 rounded">{format1}</code>
                  </p>
                </div>
              </div>

              {/* 示例 2: 带加号和小数 */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  示例 2: 带符号的小数
                </h3>
                <NumberFormatEditor
                  label="带符号小数"
                  value={format2}
                  onChange={setFormat2}
                />
                <div className="mt-4 p-3 bg-green-50 rounded text-sm">
                  <p className="text-gray-700">
                    <strong>用途：</strong>显示增长率、变化量等需要正负号的数据
                  </p>
                  <p className="text-gray-600 mt-1">
                    <strong>格式：</strong><code className="bg-white px-1 rounded">{format2}</code>
                  </p>
                </div>
              </div>

              {/* 示例 3: 百分比 */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  示例 3: 百分比格式
                </h3>
                <NumberFormatEditor
                  label="百分比格式"
                  value={format3}
                  onChange={setFormat3}
                />
                <div className="mt-4 p-3 bg-purple-50 rounded text-sm">
                  <p className="text-gray-700">
                    <strong>用途：</strong>显示占比、增长率等百分比数据
                  </p>
                  <p className="text-gray-600 mt-1">
                    <strong>格式：</strong><code className="bg-white px-1 rounded">{format3}</code>
                  </p>
                </div>
              </div>

              {/* 示例 4: 带符号的百分比 */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  示例 4: 带符号的百分比
                </h3>
                <NumberFormatEditor
                  label="带符号百分比"
                  value={format4}
                  onChange={setFormat4}
                />
                <div className="mt-4 p-3 bg-orange-50 rounded text-sm">
                  <p className="text-gray-700">
                    <strong>用途：</strong>显示同比/环比增长率，需要显示正负号
                  </p>
                  <p className="text-gray-600 mt-1">
                    <strong>格式：</strong><code className="bg-white px-1 rounded">{format4}</code>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t">
            <h2 className="text-xl font-semibold mb-4">应用场景</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded">
                <h3 className="font-medium mb-2">图表坐标轴</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• X 轴数值格式化</li>
                  <li>• Y 轴数值格式化</li>
                  <li>• 双轴图表格式化</li>
                </ul>
              </div>
              <div className="p-4 bg-gray-50 rounded">
                <h3 className="font-medium mb-2">数据标签</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• 柱状图标签</li>
                  <li>• 折线图数据点</li>
                  <li>• 气泡图标注</li>
                </ul>
              </div>
              <div className="p-4 bg-gray-50 rounded">
                <h3 className="font-medium mb-2">统计信息</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• 汇总统计值</li>
                  <li>• 百分比占比</li>
                  <li>• 增长率显示</li>
                </ul>
              </div>
              <div className="p-4 bg-gray-50 rounded">
                <h3 className="font-medium mb-2">表格数据</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• 数据表格式化</li>
                  <li>• 汇总行格式化</li>
                  <li>• 对比列格式化</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t">
            <h2 className="text-xl font-semibold mb-4">格式参考</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left">格式字符串</th>
                    <th className="px-4 py-2 text-left">配置</th>
                    <th className="px-4 py-2 text-left">示例输出</th>
                    <th className="px-4 py-2 text-left">常用场景</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  <tr>
                    <td className="px-4 py-2 font-mono">{'{:,.0f}'}</td>
                    <td className="px-4 py-2">千位符，0位小数</td>
                    <td className="px-4 py-2 font-mono">1,235</td>
                    <td className="px-4 py-2">整数数据</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-mono">{'{:,.2f}'}</td>
                    <td className="px-4 py-2">千位符，2位小数</td>
                    <td className="px-4 py-2 font-mono">1,234.57</td>
                    <td className="px-4 py-2">金额、价格</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-mono">{'{:+,.1f}'}</td>
                    <td className="px-4 py-2">加号，千位符，1位小数</td>
                    <td className="px-4 py-2 font-mono">+1,234.6</td>
                    <td className="px-4 py-2">增量、变化</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-mono">{'{:.1%}'}</td>
                    <td className="px-4 py-2">百分比，1位小数</td>
                    <td className="px-4 py-2 font-mono">12.3%</td>
                    <td className="px-4 py-2">占比、比率</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-mono">{'{:+.2%}'}</td>
                    <td className="px-4 py-2">加号，百分比，2位小数</td>
                    <td className="px-4 py-2 font-mono">+12.35%</td>
                    <td className="px-4 py-2">增长率</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-mono">{'{:.0f}'}</td>
                    <td className="px-4 py-2">无千位符，0位小数</td>
                    <td className="px-4 py-2 font-mono">1235</td>
                    <td className="px-4 py-2">简单整数</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-900 mb-2">💡 使用提示</h3>
          <ul className="text-sm text-yellow-800 space-y-1">
            <li>• 悬停在帮助图标（ⓘ）上可查看详细说明</li>
            <li>• 底部实时显示格式字符串和示例输出</li>
            <li>• 小数位数范围为 0-10</li>
            <li>• 百分比模式下，数值会自动乘以 100</li>
            <li>• 格式字符串直接用于 Python matplotlib 图表</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
