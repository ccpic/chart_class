'use client';

import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { HelpCircle } from 'lucide-react';

interface NumberFormatEditorProps {
  value: string;
  onChange: (format: string) => void;
  label?: string;
  showHelp?: boolean;
}

/**
 * 数值格式化编辑器
 * 
 * 提供可视化界面来配置 Python 格式化字符串
 * 格式模式: {:[+][,][.precision][%]}f
 * 
 * 示例:
 * - {:,.0f} → 1,234
 * - {:+,.2f} → +1,234.56
 * - {:.1%} → 12.3%
 */
export default function NumberFormatEditor({
  value,
  onChange,
  label = '数值格式',
  showHelp = true,
}: NumberFormatEditorProps) {
  const [showPlus, setShowPlus] = useState(false);
  const [showThousands, setShowThousands] = useState(false);
  const [showPercent, setShowPercent] = useState(false);
  const [decimals, setDecimals] = useState(0);

  // 解析格式字符串到控件状态
  useEffect(() => {
    const parseFormat = (fmt: string) => {
      // 匹配格式: {:+,.2f} 或 {:.1%} 等
      const match = fmt.match(/\{:([+])?(,)?\.(\d+)([f%])\}/);
      
      if (match) {
        setShowPlus(!!match[1]);
        setShowThousands(!!match[2]);
        setDecimals(parseInt(match[3], 10));
        setShowPercent(match[4] === '%');
      } else {
        // 默认值
        setShowPlus(false);
        setShowThousands(true);
        setDecimals(0);
        setShowPercent(false);
      }
    };

    parseFormat(value);
  }, [value]);

  // 根据控件状态生成格式字符串
  const buildFormat = (
    plus: boolean,
    thousands: boolean,
    percent: boolean,
    decimalPlaces: number
  ): string => {
    let fmt = '{:';
    
    if (plus) fmt += '+';
    if (thousands) fmt += ',';
    
    fmt += `.${decimalPlaces}`;
    fmt += percent ? '%' : 'f';
    fmt += '}';
    
    return fmt;
  };

  // 更新单个控件时重新生成格式字符串
  const updateFormat = (
    newPlus?: boolean,
    newThousands?: boolean,
    newPercent?: boolean,
    newDecimals?: number
  ) => {
    const fmt = buildFormat(
      newPlus ?? showPlus,
      newThousands ?? showThousands,
      newPercent ?? showPercent,
      newDecimals ?? decimals
    );
    onChange(fmt);
  };

  // 生成示例值
  const getExample = () => {
    const num = 1234.5678;
    try {
      // 模拟 Python 格式化（简化版）
      let result: string | number = num;
      
      if (showPercent) {
        result = num / 100; // 百分比模式下除以100
        result = result.toFixed(decimals);
        result = parseFloat(result);
        if (showThousands && result >= 1000) {
          result = result.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
          });
        } else {
          result = result.toFixed(decimals);
        }
        result = (showPlus && num > 0 ? '+' : '') + result + '%';
      } else {
        if (showThousands) {
          result = num.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
          });
        } else {
          result = num.toFixed(decimals);
        }
        if (showPlus && num > 0) {
          result = '+' + result;
        }
      }
      
      return result.toString();
    } catch {
      return '无效格式';
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Label className="text-sm font-medium">{label}</Label>
        {showHelp && (
          <div className="group relative">
            <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
            <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-80 p-3 bg-gray-900 text-white text-xs rounded shadow-lg z-50">
              <p className="font-semibold mb-1">Python 格式化字符串</p>
              <p className="mb-2">当前格式: <code className="bg-gray-800 px-1 rounded">{value}</code></p>
              <p className="mb-1">示例输出: <span className="font-mono">{getExample()}</span></p>
              <div className="mt-2 pt-2 border-t border-gray-700 text-[10px]">
                <p>• <strong>+号</strong>: 正数显示加号</p>
                <p>• <strong>千位符</strong>: 使用逗号分隔千位</p>
                <p>• <strong>百分号</strong>: 数值乘100后显示%</p>
                <p>• <strong>小数位</strong>: 保留的小数位数</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 gap-2 p-3 bg-gray-50 rounded-md border border-gray-200">
        {/* 显示+号 */}
        <div className="flex flex-col items-center gap-1.5">
          <Label htmlFor="show-plus" className="text-xs text-gray-600 whitespace-nowrap cursor-pointer">
            +号
          </Label>
          <Checkbox
            id="show-plus"
            checked={showPlus}
            onCheckedChange={(checked) => {
              const isChecked = checked === true;
              setShowPlus(isChecked);
              updateFormat(isChecked, undefined, undefined, undefined);
            }}
          />
        </div>

        {/* 千位符 */}
        <div className="flex flex-col items-center gap-1.5">
          <Label htmlFor="show-thousands" className="text-xs text-gray-600 whitespace-nowrap cursor-pointer">
            千位符
          </Label>
          <Checkbox
            id="show-thousands"
            checked={showThousands}
            onCheckedChange={(checked) => {
              const isChecked = checked === true;
              setShowThousands(isChecked);
              updateFormat(undefined, isChecked, undefined, undefined);
            }}
          />
        </div>

        {/* 百分号 */}
        <div className="flex flex-col items-center gap-1.5">
          <Label htmlFor="show-percent" className="text-xs text-gray-600 whitespace-nowrap cursor-pointer">
            百分号
          </Label>
          <Checkbox
            id="show-percent"
            checked={showPercent}
            onCheckedChange={(checked) => {
              const isChecked = checked === true;
              setShowPercent(isChecked);
              updateFormat(undefined, undefined, isChecked, undefined);
            }}
          />
        </div>

        {/* 小数位 */}
        <div className="flex flex-col items-center gap-1.5">
          <Label htmlFor="decimals-input" className="text-xs text-gray-600 whitespace-nowrap">
            小数位
          </Label>
          <Input
            id="decimals-input"
            type="number"
            min="0"
            max="10"
            value={decimals}
            onChange={(e) => {
              const val = parseInt(e.target.value, 10);
              if (!isNaN(val) && val >= 0 && val <= 10) {
                setDecimals(val);
                updateFormat(undefined, undefined, undefined, val);
              }
            }}
            className="w-14 h-8 text-center text-sm px-1"
          />
        </div>
      </div>

      {/* 格式字符串和预览 */}
      <div className="flex items-center gap-2 text-xs">
        <span className="text-gray-500">格式:</span>
        <code className="bg-gray-100 px-2 py-1 rounded font-mono text-gray-700">{value}</code>
        <span className="text-gray-400">→</span>
        <span className="text-gray-500">示例:</span>
        <span className="font-mono font-semibold text-gray-800">{getExample()}</span>
      </div>
    </div>
  );
}
