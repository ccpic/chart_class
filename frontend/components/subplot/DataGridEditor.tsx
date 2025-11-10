'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Trash2, Info, ArrowDownLeft } from 'lucide-react';

interface DataGridEditorProps {
  data: {
    columns: string[];
    index?: string[];
    data: any[][];
  };
  onChange: (data: { columns: string[]; index: string[]; data: any[][] }) => void;
}

/**
 * Excel 风格的数据网格编辑器
 * 支持添加/删除行列、编辑单元格、编辑行索引
 */
export default function DataGridEditor({ data, onChange }: DataGridEditorProps) {
  // 辅助函数：智能解析数字（处理货币符号、千位符、百分号等）
  const safeParseNumber = (value: string): string | number => {
    if (!value || value.trim() === '') return value;
    
    const trimmed = value.trim();
    
    // 检查是否包含百分号
    const hasPercent = trimmed.includes('%');
    
    // 清理字符串：
    // 1. 去除货币符号：$, ¥, €, £, ₹ 等
    // 2. 去除千位符：,
    // 3. 去除加号：+
    // 4. 去除百分号：%
    let cleaned = trimmed
      .replace(/[$¥€£₹]/g, '')  // 去除常见货币符号
      .replace(/,/g, '')          // 去除千位符
      .replace(/\+/g, '')         // 去除加号
      .replace(/%/g, '');         // 去除百分号
    
    cleaned = cleaned.trim();
    
    // 如果清理后为空，返回原值
    if (cleaned === '') return value;
    
    // 检查清理后是否为纯数字（包括小数点、负号、科学计数法）
    const isPureNumber = /^-?\d*\.?\d+([eE][+-]?\d+)?$/.test(cleaned);
    
    if (!isPureNumber) {
      // 不是数字，保持原样
      return value;
    }
    
    // 转换为数字
    const numValue = parseFloat(cleaned);
    
    if (isNaN(numValue)) {
      return value; // 转换失败，保持原样
    }
    
    // 如果原值包含百分号，除以 100
    if (hasPercent) {
      return numValue / 100;
    }
    
    return numValue;
  };

  // 初始化默认数据：20 行 5 列
  const initializeDefaultData = () => {
    if (data.columns && data.columns.length > 0) {
      return {
        columns: data.columns,
        index: data.index || data.data.map((_, i) => `行${i + 1}`),
        rows: data.data
      };
    }
    // 默认 20 行 5 列
    return {
      columns: Array.from({ length: 5 }, (_, i) => `列${i + 1}`),
      index: Array.from({ length: 20 }, (_, i) => `行${i + 1}`),
      rows: Array.from({ length: 20 }, () => Array(5).fill(''))
    };
  };

  const defaultData = initializeDefaultData();
  const [columns, setColumns] = useState<string[]>(defaultData.columns);
  const [index, setIndex] = useState<string[]>(defaultData.index);
  const [rows, setRows] = useState<any[][]>(defaultData.rows);
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number; type: 'data' | 'rowIndex' | 'colName' | 'corner' } | null>(null);

  // 当外部数据变化时同步到本地状态
  useEffect(() => {
    // 如果有数据，使用传入的数据
    if (data.columns && data.columns.length > 0) {
      setColumns(data.columns);
      setIndex(data.index || data.data.map((_, i) => `行${i + 1}`));
      setRows(data.data);
    } else if (data.columns && data.columns.length === 0) {
      // 如果明确清空了数据（columns 为空数组），重置为默认空白表格
      setColumns(Array.from({ length: 5 }, (_, i) => `列${i + 1}`));
      setIndex(Array.from({ length: 20 }, (_, i) => `行${i + 1}`));
      setRows(Array.from({ length: 20 }, () => Array(5).fill('')));
    }
  }, [data]);

  // 同步到父组件
  const syncToParent = (newColumns: string[], newIndex: string[], newRows: any[][]) => {
    onChange({ columns: newColumns, index: newIndex, data: newRows });
  };

  // 添加列
  const addColumn = () => {
    const newColumns = [...columns, `列${columns.length + 1}`];
    const newRows = rows.map(row => [...row, '']);
    setColumns(newColumns);
    setRows(newRows);
    syncToParent(newColumns, index, newRows);
  };

  // 删除列
  const deleteColumn = (colIndex: number) => {
    if (columns.length <= 1) return; // 至少保留一列
    const newColumns = columns.filter((_, i) => i !== colIndex);
    const newRows = rows.map(row => row.filter((_, i) => i !== colIndex));
    setColumns(newColumns);
    setRows(newRows);
    syncToParent(newColumns, index, newRows);
  };

  // 添加行
  const addRow = () => {
    const newRow = new Array(columns.length).fill('');
    const newRows = [...rows, newRow];
    const newIndex = [...index, `行${index.length + 1}`];
    setRows(newRows);
    setIndex(newIndex);
    syncToParent(columns, newIndex, newRows);
  };

  // 删除行
  const deleteRow = (rowIndex: number) => {
    if (rows.length <= 1) return; // 至少保留一行
    const newRows = rows.filter((_, i) => i !== rowIndex);
    const newIndex = index.filter((_, i) => i !== rowIndex);
    setRows(newRows);
    setIndex(newIndex);
    syncToParent(columns, newIndex, newRows);
  };

  // 更新列名
  const updateColumnName = (colIndex: number, value: string) => {
    const newColumns = [...columns];
    newColumns[colIndex] = value;
    setColumns(newColumns);
    syncToParent(newColumns, index, rows);
  };

  // 更新行索引
  const updateRowIndex = (rowIndex: number, value: string) => {
    const newIndex = [...index];
    newIndex[rowIndex] = value;
    setIndex(newIndex);
    syncToParent(columns, newIndex, rows);
  };

  // 更新单元格值
  const updateCell = (rowIndex: number, colIndex: number, value: string) => {
    const newRows = [...rows];
    if (!newRows[rowIndex]) newRows[rowIndex] = [];
    
    // 使用安全的数字转换
    newRows[rowIndex][colIndex] = safeParseNumber(value);
    
    setRows(newRows);
    syncToParent(columns, index, newRows);
  };

  // 键盘导航
  const handleKeyDown = (e: React.KeyboardEvent, rowIndex: number, colIndex: number, cellType: 'data' | 'rowIndex' | 'colName' | 'corner') => {
    if (!selectedCell) return;

    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault();
        if (cellType === 'data' && rowIndex > 0) {
          setSelectedCell({ row: rowIndex - 1, col: colIndex, type: 'data' });
        }
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (cellType === 'data' && rowIndex < rows.length - 1) {
          setSelectedCell({ row: rowIndex + 1, col: colIndex, type: 'data' });
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        if (cellType === 'data' && colIndex > 0) {
          setSelectedCell({ row: rowIndex, col: colIndex - 1, type: 'data' });
        }
        break;
      case 'ArrowRight':
        e.preventDefault();
        if (cellType === 'data' && colIndex < columns.length - 1) {
          setSelectedCell({ row: rowIndex, col: colIndex + 1, type: 'data' });
        }
        break;
      case 'Enter':
        e.preventDefault();
        if (cellType === 'data' && rowIndex < rows.length - 1) {
          setSelectedCell({ row: rowIndex + 1, col: colIndex, type: 'data' });
        }
        break;
    }
  };

  // 处理粘贴事件（支持从 Excel 复制）
  const handlePaste = (e: React.ClipboardEvent, startRow: number, startCol: number, cellType: 'data' | 'rowIndex' | 'colName' | 'corner') => {
    e.preventDefault();
    
    const pastedText = e.clipboardData.getData('text');
    if (!pastedText) return;

    // 解析粘贴的数据（Excel 使用制表符分隔列，换行符分隔行）
    const pastedRows = pastedText.split('\n').map(row => 
      row.split('\t').map(cell => cell.trim())
    );

    // 移除最后的空行（如果有）
    if (pastedRows[pastedRows.length - 1].every(cell => cell === '')) {
      pastedRows.pop();
    }

    // 根据粘贴位置类型处理
    if (cellType === 'corner') {
      // 左上角粘贴：第一行 → 列名，第一列 → 行索引，其余 → 数据
      handleCornerPaste(pastedRows);
    } else if (cellType === 'colName') {
      // 列名粘贴：只更新列名
      handleColumnNamePaste(pastedRows, startCol);
    } else if (cellType === 'rowIndex') {
      // 行索引粘贴：只更新行索引
      handleRowIndexPaste(pastedRows, startRow);
    } else {
      // 数据区域粘贴
      handleDataPaste(pastedRows, startRow, startCol);
    }
  };

  // 左上角粘贴处理
  const handleCornerPaste = (pastedRows: string[][]) => {
    if (pastedRows.length === 0) return;

    // 第一行作为列名（跳过第一个单元格）
    const newColumns = pastedRows[0].slice(1);
    
    // 第一列作为行索引（跳过第一个单元格）
    const newIndex = pastedRows.slice(1).map(row => row[0] || '');
    
    // 其余作为数据
    const newRows = pastedRows.slice(1).map(row => {
      const dataRow = row.slice(1);
      return dataRow.map(cell => safeParseNumber(cell));
    });

    // 确保数据行数与索引行数匹配
    while (newRows.length < newIndex.length) {
      newRows.push(new Array(newColumns.length).fill(''));
    }

    setColumns(newColumns.length > 0 ? newColumns : ['列1']);
    setIndex(newIndex.length > 0 ? newIndex : ['行1']);
    setRows(newRows);
    syncToParent(
      newColumns.length > 0 ? newColumns : ['列1'],
      newIndex.length > 0 ? newIndex : ['行1'],
      newRows
    );
  };

  // 列名粘贴处理
  const handleColumnNamePaste = (pastedRows: string[][], startCol: number) => {
    // 如果粘贴的是多行数据，转为数据区域粘贴（从第一行数据开始）
    if (pastedRows.length > 1) {
      console.log('检测到多行粘贴，转为数据区域粘贴');
      handleDataPaste(pastedRows, 0, startCol);
      return;
    }

    // 只取第一行作为列名
    const pastedCols = pastedRows[0] || [];
    const newColumns = [...columns];

    // 扩展列数（如果需要）
    const neededCols = startCol + pastedCols.length;
    while (newColumns.length < neededCols) {
      newColumns.push(`列${newColumns.length + 1}`);
    }

    // 填充列名
    pastedCols.forEach((col, i) => {
      newColumns[startCol + i] = col;
    });

    // 扩展数据行的列数
    const newRows = rows.map(row => {
      const newRow = [...row];
      while (newRow.length < neededCols) {
        newRow.push('');
      }
      return newRow;
    });

    setColumns(newColumns);
    setRows(newRows);
    syncToParent(newColumns, index, newRows);
  };

  // 行索引粘贴处理
  const handleRowIndexPaste = (pastedRows: string[][], startRow: number) => {
    // 如果粘贴的是多列数据（不只是一列索引），转为数据区域粘贴
    const maxCols = Math.max(...pastedRows.map(row => row.length));
    if (maxCols > 1) {
      console.log('检测到多列粘贴，转为数据区域粘贴');
      handleDataPaste(pastedRows, startRow, 0);
      return;
    }

    // 取第一列作为行索引
    const pastedIndex = pastedRows.map(row => row[0] || '');
    const newIndex = [...index];
    const newRows = [...rows];

    // 扩展行数（如果需要）
    const neededRows = startRow + pastedIndex.length;
    while (newIndex.length < neededRows) {
      newIndex.push(`行${newIndex.length + 1}`);
      newRows.push(new Array(columns.length).fill(''));
    }

    // 填充行索引
    pastedIndex.forEach((idx, i) => {
      newIndex[startRow + i] = idx;
    });

    setIndex(newIndex);
    setRows(newRows);
    syncToParent(columns, newIndex, newRows);
  };

  // 数据区域粘贴处理
  const handleDataPaste = (pastedRows: string[][], startRow: number, startCol: number) => {
    const newRows = [...rows];
    const pasteHeight = pastedRows.length;
    const pasteWidth = Math.max(...pastedRows.map(row => row.length));

    // 如果粘贴区域超出当前表格，自动扩展
    const neededRows = startRow + pasteHeight;
    const neededCols = startCol + pasteWidth;

    // 扩展行
    if (neededRows > newRows.length) {
      const additionalRows = neededRows - newRows.length;
      for (let i = 0; i < additionalRows; i++) {
        newRows.push(new Array(columns.length).fill(''));
      }
    }

    // 扩展列
    let newColumns = [...columns];
    if (neededCols > columns.length) {
      const additionalCols = neededCols - columns.length;
      for (let i = 0; i < additionalCols; i++) {
        newColumns.push(`列${newColumns.length + 1}`);
      }
      // 为现有行添加新列
      newRows.forEach(row => {
        while (row.length < neededCols) {
          row.push('');
        }
      });
    }

    // 扩展行索引
    let newIndex = [...index];
    if (neededRows > newIndex.length) {
      const additionalIndex = neededRows - newIndex.length;
      for (let i = 0; i < additionalIndex; i++) {
        newIndex.push(`行${newIndex.length + 1}`);
      }
    }

    // 填充粘贴的数据
    pastedRows.forEach((pastedRow, i) => {
      const targetRow = startRow + i;
      pastedRow.forEach((cell, j) => {
        const targetCol = startCol + j;
        if (targetRow < newRows.length && targetCol < neededCols) {
          // 使用安全的数字转换
          newRows[targetRow][targetCol] = safeParseNumber(cell);
        }
      });
    });

    // 更新状态
    setColumns(newColumns);
    setIndex(newIndex);
    setRows(newRows);
    syncToParent(newColumns, newIndex, newRows);

    // 选中粘贴区域的右下角
    setSelectedCell({ 
      row: Math.min(startRow + pasteHeight - 1, newRows.length - 1), 
      col: Math.min(startCol + pasteWidth - 1, neededCols - 1),
      type: 'data'
    });
  };

  return (
    <div className="space-y-4">
      {/* 工具栏 */}
      <div className="flex items-center gap-2 pb-2 border-b">
        <Button onClick={addColumn} size="sm" variant="outline" className="gap-2">
          <Plus className="h-3 w-3" />
          添加列
        </Button>
        <Button onClick={addRow} size="sm" variant="outline" className="gap-2">
          <Plus className="h-3 w-3" />
          添加行
        </Button>
        <div className="ml-auto text-xs text-gray-600">
          {columns.length} 列 × {rows.length} 行
        </div>
      </div>

      {/* 表格容器 */}
      <div className="border rounded-lg overflow-auto max-h-[500px]">
        <table className="w-full border-collapse">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              {/* 左上角交汇单元格 */}
              <th 
                className={`w-32 border-b border-r p-2 text-xs font-semibold text-gray-400 cursor-pointer hover:bg-blue-100 ${
                  selectedCell?.type === 'corner' ? 'bg-blue-200 ring-2 ring-blue-500' : 'bg-gray-100'
                }`}
                onClick={() => setSelectedCell({ row: 0, col: 0, type: 'corner' })}
                onPaste={(e) => handlePaste(e, 0, 0, 'corner')}
                tabIndex={0}
                title="点击选中，粘贴包含行列索引的完整表格"
              >
                <ArrowDownLeft className="h-4 w-4 mx-auto text-gray-400" />
              </th>
              {columns.map((col, colIndex) => (
                <th key={colIndex} className="border-b border-r bg-gray-50 p-0">
                  <div className="flex items-center gap-1">
                    <Input
                      value={col}
                      onChange={(e) => updateColumnName(colIndex, e.target.value)}
                      onFocus={() => setSelectedCell({ row: 0, col: colIndex, type: 'colName' })}
                      onPaste={(e) => handlePaste(e, 0, colIndex, 'colName')}
                      className={`border-0 h-8 text-xs font-semibold text-center focus-visible:ring-1 bg-transparent ${
                        selectedCell?.type === 'colName' && selectedCell?.col === colIndex 
                          ? 'bg-blue-100 ring-2 ring-blue-500' 
                          : ''
                      }`}
                      placeholder={`列${colIndex + 1}`}
                    />
                    <button
                      onClick={() => deleteColumn(colIndex)}
                      className="p-1 hover:bg-red-100 rounded text-red-600"
                      title="删除列"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-blue-50/50">
                <td className="border-r border-b bg-gray-50 p-0">
                  <div className="flex items-center gap-1">
                    <Input
                      value={index[rowIndex] || `行${rowIndex + 1}`}
                      onChange={(e) => updateRowIndex(rowIndex, e.target.value)}
                      onFocus={() => setSelectedCell({ row: rowIndex, col: 0, type: 'rowIndex' })}
                      onPaste={(e) => handlePaste(e, rowIndex, 0, 'rowIndex')}
                      className={`border-0 h-9 text-xs font-medium focus-visible:ring-1 bg-transparent ${
                        selectedCell?.type === 'rowIndex' && selectedCell?.row === rowIndex 
                          ? 'bg-blue-100 ring-2 ring-blue-500' 
                          : ''
                      }`}
                      placeholder={`行${rowIndex + 1}`}
                    />
                    <button
                      onClick={() => deleteRow(rowIndex)}
                      className="p-1 hover:bg-red-100 rounded text-red-600 mr-1"
                      title="删除行"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </td>
                {columns.map((_, colIndex) => (
                  <td key={colIndex} className="border-r border-b p-0">
                    <Input
                      value={row[colIndex] ?? ''}
                      onChange={(e) => updateCell(rowIndex, colIndex, e.target.value)}
                      onFocus={() => setSelectedCell({ row: rowIndex, col: colIndex, type: 'data' })}
                      onKeyDown={(e) => handleKeyDown(e, rowIndex, colIndex, 'data')}
                      onPaste={(e) => handlePaste(e, rowIndex, colIndex, 'data')}
                      className={`
                        border-0 h-9 text-sm focus-visible:ring-2 focus-visible:ring-blue-500 rounded-none
                        ${selectedCell?.row === rowIndex && selectedCell?.col === colIndex && selectedCell?.type === 'data'
                          ? 'bg-blue-50 ring-2 ring-blue-500' 
                          : 'bg-transparent'}
                      `}
                      placeholder="..."
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 提示信息 */}
      <div className="text-xs text-gray-500 space-y-1">
        <p className="flex items-center gap-1 font-medium">
          <Info className="h-3 w-3" />
          提示：
        </p>
        <ul className="list-disc list-inside space-y-0.5 ml-2">
          <li><strong>左上角单元格</strong>：点击选中，粘贴包含行列索引的完整 Excel 表格（第一行→列名，第一列→行索引）</li>
          <li><strong>列名区域</strong>：点击任意列名粘贴一行列名</li>
          <li><strong>行索引区域</strong>：点击任意行索引粘贴一列行索引</li>
          <li><strong>数据区域</strong>：点击单元格粘贴数据矩阵，自动扩展表格</li>
          <li><strong>智能数字解析</strong>：自动去除货币符号（$¥€£）、千位符（,）、加号（+），百分号（%）自动转换（50% → 0.5）</li>
        </ul>
      </div>
    </div>
  );
}
