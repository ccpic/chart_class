'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Trash2, Info, ArrowDownLeft } from 'lucide-react';
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from '@/components/ui/context-menu';

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

  // 初始化默认数据：10 行 2 列
  const initializeDefaultData = () => {
    if (data.columns && data.columns.length > 0) {
      return {
        columns: data.columns,
        index: data.index || data.data.map((_, i) => `行${i + 1}`),
        rows: data.data
      };
    }
    // 默认 10 行 2 列
    return {
      columns: Array.from({ length: 2 }, (_, i) => `列${i + 1}`),
      index: Array.from({ length: 10 }, (_, i) => `行${i + 1}`),
      rows: Array.from({ length: 10 }, () => Array(2).fill(''))
    };
  };

  const defaultData = initializeDefaultData();
  const [columns, setColumns] = useState<string[]>(defaultData.columns);
  const [index, setIndex] = useState<string[]>(defaultData.index);
  const [rows, setRows] = useState<any[][]>(defaultData.rows);
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number; type: 'data' | 'rowIndex' | 'colName' | 'corner' } | null>(null);
  const [selectedCells, setSelectedCells] = useState<Set<string>>(new Set());
  const [isSelecting, setIsSelecting] = useState(false);
  const [selectionStart, setSelectionStart] = useState<{ row: number; col: number } | null>(null);

  // 当外部数据变化时同步到本地状态
  useEffect(() => {
    // 如果有数据，使用传入的数据
    if (data.columns && data.columns.length > 0) {
      setColumns(data.columns);
      setIndex(data.index || data.data.map((_, i) => `行${i + 1}`));
      setRows(data.data);
    } else if (data.columns && data.columns.length === 0) {
      // 如果明确清空了数据（columns 为空数组），重置为默认空白表格
      setColumns(Array.from({ length: 2 }, (_, i) => `列${i + 1}`));
      setIndex(Array.from({ length: 10 }, (_, i) => `行${i + 1}`));
      setRows(Array.from({ length: 10 }, () => Array(2).fill('')));
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

  // 在指定列右侧插入空列
  const insertColumnAfter = (colIndex: number) => {
    const newColumns = [
      ...columns.slice(0, colIndex + 1),
      `列${columns.length + 1}`,
      ...columns.slice(colIndex + 1)
    ];
    const newRows = rows.map(row => [
      ...row.slice(0, colIndex + 1),
      '',
      ...row.slice(colIndex + 1)
    ]);
    setColumns(newColumns);
    setRows(newRows);
    syncToParent(newColumns, index, newRows);
  };

  // 在指定列左侧插入空列
  const insertColumnBefore = (colIndex: number) => {
    const newColumns = [
      ...columns.slice(0, colIndex),
      `列${columns.length + 1}`,
      ...columns.slice(colIndex)
    ];
    const newRows = rows.map(row => [
      ...row.slice(0, colIndex),
      '',
      ...row.slice(colIndex)
    ]);
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
    
    // 如果包含换行符，保持为字符串；否则尝试数字转换
    if (value.includes('\n')) {
      newRows[rowIndex][colIndex] = value;
    } else {
      // 使用安全的数字转换
      newRows[rowIndex][colIndex] = safeParseNumber(value);
    }
    
    setRows(newRows);
    syncToParent(columns, index, newRows);
  };

  // 批量选择相关函数
  const getCellKey = (row: number, col: number) => `${row}-${col}`;

  const handleCellMouseDown = (rowIndex: number, colIndex: number) => {
    setIsSelecting(true);
    setSelectionStart({ row: rowIndex, col: colIndex });
    setSelectedCells(new Set([getCellKey(rowIndex, colIndex)]));
  };

  const handleCellMouseEnter = (rowIndex: number, colIndex: number) => {
    if (!isSelecting || !selectionStart) return;
    
    const minRow = Math.min(selectionStart.row, rowIndex);
    const maxRow = Math.max(selectionStart.row, rowIndex);
    const minCol = Math.min(selectionStart.col, colIndex);
    const maxCol = Math.max(selectionStart.col, colIndex);
    
    const newSelection = new Set<string>();
    for (let r = minRow; r <= maxRow; r++) {
      for (let c = minCol; c <= maxCol; c++) {
        newSelection.add(getCellKey(r, c));
      }
    }
    setSelectedCells(newSelection);
  };

  const handleCellMouseUp = () => {
    setIsSelecting(false);
  };

  // 删除选中的单元格内容
  const deleteSelectedCells = () => {
    if (selectedCells.size === 0) return;
    
    const newRows = [...rows];
    selectedCells.forEach(key => {
      const [rowStr, colStr] = key.split('-');
      const row = parseInt(rowStr);
      const col = parseInt(colStr);
      if (newRows[row] && col < newRows[row].length) {
        newRows[row][col] = '';
      }
    });
    
    setRows(newRows);
    syncToParent(columns, index, newRows);
    setSelectedCells(new Set());
  };

  // 监听全局鼠标释放事件
  useEffect(() => {
    const handleGlobalMouseUp = () => setIsSelecting(false);
    document.addEventListener('mouseup', handleGlobalMouseUp);
    return () => document.removeEventListener('mouseup', handleGlobalMouseUp);
  }, []);

  // 复制选中的单元格
  const copySelectedCells = async () => {
    if (selectedCells.size === 0) return;
    
    // 找出选中区域的边界
    const selectedArray = Array.from(selectedCells).map(key => {
      const [rowStr, colStr] = key.split('-');
      return { row: parseInt(rowStr), col: parseInt(colStr) };
    });
    
    const minRow = Math.min(...selectedArray.map(cell => cell.row));
    const maxRow = Math.max(...selectedArray.map(cell => cell.row));
    const minCol = Math.min(...selectedArray.map(cell => cell.col));
    const maxCol = Math.max(...selectedArray.map(cell => cell.col));
    
    // 构建二维数组（包含所有行列，即使未选中）
    const copyData: string[][] = [];
    for (let r = minRow; r <= maxRow; r++) {
      const rowData: string[] = [];
      for (let c = minCol; c <= maxCol; c++) {
        if (selectedCells.has(getCellKey(r, c))) {
          // 选中的单元格：复制其值
          const cellValue = rows[r]?.[c] ?? '';
          const displayValue = typeof cellValue === 'string' ? cellValue : String(cellValue);
          rowData.push(displayValue);
        } else {
          // 未选中的单元格：保持空白
          rowData.push('');
        }
      }
      copyData.push(rowData);
    }
    
    // 转换为 Excel 格式（制表符分隔列，换行符分隔行）
    const tsvText = copyData.map(row => row.join('\t')).join('\n');
    
    // 复制到剪贴板
    try {
      await navigator.clipboard.writeText(tsvText);
      console.log('✅ 已复制到剪贴板:', copyData);
    } catch (err) {
      console.error('❌ 复制失败:', err);
      // 降级方案：使用 document.execCommand (已废弃但兼容性好)
      const textarea = document.createElement('textarea');
      textarea.value = tsvText;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        console.log('✅ 使用降级方案复制成功');
      } catch (e) {
        console.error('❌ 降级方案也失败:', e);
      }
      document.body.removeChild(textarea);
    }
  };

  // 监听键盘事件（Delete/Backspace 删除，Ctrl+C 复制）
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 检查当前焦点是否在输入框内（Textarea 或 Input）
      const activeElement = document.activeElement;
      const isInputFocused = activeElement && (
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.tagName === 'INPUT'
      );

      // 只有当焦点不在输入框内，且有选中单元格时，才执行批量删除
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedCells.size > 0 && !isInputFocused) {
        e.preventDefault();
        deleteSelectedCells();
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'c' && selectedCells.size > 0) {
        e.preventDefault();
        copySelectedCells();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedCells, rows]);

  // 自动调整 Textarea 高度
  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>, rowIndex: number, colIndex: number) => {
    const textarea = e.target;
    // 重置高度以获取正确的 scrollHeight
    textarea.style.height = 'auto';
    // 设置新高度，但不超过最大高度
    const newHeight = Math.min(textarea.scrollHeight, 200);
    textarea.style.height = `${newHeight}px`;
    // 更新单元格值
    updateCell(rowIndex, colIndex, textarea.value);
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

    console.log(`📋 粘贴事件 - 位置类型: ${cellType}, 起始位置: (${startRow}, ${startCol})`);

    // 解析粘贴的数据（Excel 使用制表符分隔列，换行符分隔行）
    const pastedRows = pastedText.split('\n').map(row => 
      row.split('\t').map(cell => cell.trim())
    );

    // 移除最后的空行（如果有）
    if (pastedRows.length > 0 && pastedRows[pastedRows.length - 1].every(cell => cell === '')) {
      pastedRows.pop();
    }

    console.log('📊 解析后的数据:', pastedRows);

    // 根据粘贴位置类型处理
    if (cellType === 'corner') {
      // 左上角粘贴：第一行 → 列名，第一列 → 行索引，其余 → 数据
      console.log('🔷 识别为左上角粘贴');
      handleCornerPaste(pastedRows);
    } else if (cellType === 'colName') {
      // 列名粘贴：只更新列名
      console.log('📊 识别为列名粘贴');
      handleColumnNamePaste(pastedRows, startCol);
    } else if (cellType === 'rowIndex') {
      // 行索引粘贴：只更新行索引
      console.log('📋 识别为行索引粘贴');
      handleRowIndexPaste(pastedRows, startRow);
    } else {
      // 数据区域粘贴
      console.log('📈 识别为数据区域粘贴');
      handleDataPaste(pastedRows, startRow, startCol);
    }
  };

  // 左上角粘贴处理
  const handleCornerPaste = (pastedRows: string[][]) => {
    console.log('🔷 左上角粘贴 - 原始数据:', pastedRows);
    
    if (pastedRows.length === 0) {
      console.warn('粘贴数据为空');
      return;
    }

    // 如果只有一行一列，当作普通数据处理
    if (pastedRows.length === 1 && pastedRows[0].length === 1) {
      console.log('只有一个单元格，忽略');
      return;
    }

    // 第一行作为列名（跳过第一个单元格，因为 [0][0] 是左上角交汇处）
    const newColumns = pastedRows[0].slice(1).filter(col => col !== '');
    console.log('📊 解析列名:', newColumns);
    
    // 第一列作为行索引（跳过第一行，因为 [0][0] 是左上角交汇处）
    const newIndex = pastedRows.slice(1).map(row => row[0] || '').filter(idx => idx !== '');
    console.log('📋 解析行索引:', newIndex);
    
    // 其余作为数据（跳过第一行和第一列）
    const newRows = pastedRows.slice(1).map(row => {
      const dataRow = row.slice(1);
      return dataRow.map(cell => safeParseNumber(cell));
    });
    console.log('📈 解析数据矩阵:', newRows);

    // 验证数据完整性
    if (newColumns.length === 0) {
      console.warn('没有有效的列名，使用默认列名');
      newColumns.push('列1');
    }

    if (newIndex.length === 0) {
      console.warn('没有有效的行索引，使用默认行索引');
      newIndex.push('行1');
    }

    // 确保数据行数与索引行数匹配
    while (newRows.length < newIndex.length) {
      newRows.push(new Array(newColumns.length).fill(''));
    }

    // 确保每行的列数匹配
    newRows.forEach(row => {
      while (row.length < newColumns.length) {
        row.push('');
      }
    });

    console.log('✅ 最终结果:', { columns: newColumns, index: newIndex, rows: newRows });

    setColumns(newColumns);
    setIndex(newIndex);
    setRows(newRows);
    syncToParent(newColumns, newIndex, newRows);
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
        {selectedCells.size > 0 && (
          <>
            <Button 
              onClick={copySelectedCells} 
              size="sm" 
              variant="outline" 
              className="gap-2"
            >
              复制选中 ({selectedCells.size})
            </Button>
            <Button 
              onClick={deleteSelectedCells} 
              size="sm" 
              variant="destructive" 
              className="gap-2"
            >
              <Trash2 className="h-3 w-3" />
              删除选中
            </Button>
          </>
        )}
        <div className="ml-auto text-xs text-gray-600">
          {columns.length} 列 × {rows.length} 行
          {selectedCells.size > 0 && ` | 已选中 ${selectedCells.size} 个单元格`}
        </div>
      </div>

      {/* 表格容器 */}
      <div className="border rounded-lg overflow-auto max-h-[500px]">
        <table className="w-full border-collapse">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              {/* 左上角交汇单元格 */}
              <th className="w-32 border-b border-r p-0 bg-gray-100 relative">
                <Input
                  value=""
                  readOnly
                  onFocus={() => setSelectedCell({ row: 0, col: 0, type: 'corner' })}
                  onPaste={(e) => {
                    console.log('🔷 左上角粘贴事件触发');
                    handlePaste(e, 0, 0, 'corner');
                  }}
                  className={`border-0 h-8 text-xs font-semibold text-center focus-visible:ring-2 bg-transparent cursor-pointer ${
                    selectedCell?.type === 'corner' 
                      ? 'bg-blue-200 ring-2 ring-blue-500' 
                      : 'hover:bg-blue-100'
                  }`}
                  title="点击选中，粘贴包含行列索引的完整表格"
                  placeholder=""
                />
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <ArrowDownLeft className="h-4 w-4 text-gray-400" />
                </div>
              </th>
              {columns.map((col, colIndex) => (
                <th key={colIndex} className="border-b border-r bg-gray-50 p-0">
                  <ContextMenu>
                    <ContextMenuTrigger asChild>
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
                    </ContextMenuTrigger>
                    <ContextMenuContent className="w-48">
                      <ContextMenuItem
                        onClick={() => insertColumnBefore(colIndex)}
                        className="cursor-pointer"
                      >
                        <Plus className="mr-2 h-4 w-4" />
                        在左侧插入列
                      </ContextMenuItem>
                      <ContextMenuItem
                        onClick={() => insertColumnAfter(colIndex)}
                        className="cursor-pointer"
                      >
                        <Plus className="mr-2 h-4 w-4" />
                        在右侧插入列
                      </ContextMenuItem>
                      <ContextMenuItem
                        onClick={() => deleteColumn(colIndex)}
                        className="cursor-pointer text-red-600"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        删除此列
                      </ContextMenuItem>
                    </ContextMenuContent>
                  </ContextMenu>
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
                {columns.map((_, colIndex) => {
                  const cellValue = row[colIndex] ?? '';
                  const displayValue = typeof cellValue === 'string' ? cellValue : String(cellValue);
                  // 计算行数（根据换行符数量）
                  const lineCount = displayValue.split('\n').length;
                  const estimatedRows = Math.max(1, Math.min(lineCount, 8)); // 最多显示 8 行
                  return (
                    <td key={colIndex} className="border-r border-b p-0 align-top">
                      <Textarea
                        value={displayValue}
                        onChange={(e) => handleTextareaChange(e, rowIndex, colIndex)}
                        onFocus={(e) => {
                          setSelectedCell({ row: rowIndex, col: colIndex, type: 'data' });
                          // 聚焦时自动调整高度
                          const textarea = e.target;
                          textarea.style.height = 'auto';
                          const newHeight = Math.min(textarea.scrollHeight, 200);
                          textarea.style.height = `${newHeight}px`;
                        }}
                        onMouseDown={() => handleCellMouseDown(rowIndex, colIndex)}
                        onMouseEnter={() => handleCellMouseEnter(rowIndex, colIndex)}
                        onMouseUp={handleCellMouseUp}
                        onKeyDown={(e) => {
                          // 在 Textarea 中，Enter 键用于换行
                          // Tab 键用于移动到下一个单元格
                          if (e.key === 'Tab') {
                            e.preventDefault();
                            if (e.shiftKey) {
                              // Shift+Tab 移动到上一个单元格
                              if (colIndex > 0) {
                                setSelectedCell({ row: rowIndex, col: colIndex - 1, type: 'data' });
                              } else if (rowIndex > 0) {
                                setSelectedCell({ row: rowIndex - 1, col: columns.length - 1, type: 'data' });
                              }
                            } else {
                              // Tab 移动到下一个单元格
                              if (colIndex < columns.length - 1) {
                                setSelectedCell({ row: rowIndex, col: colIndex + 1, type: 'data' });
                              } else if (rowIndex < rows.length - 1) {
                                setSelectedCell({ row: rowIndex + 1, col: 0, type: 'data' });
                              }
                            }
                          } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                            // 方向键用于导航（当光标在文本开头或结尾时）
                            const textarea = e.target as HTMLTextAreaElement;
                            const cursorPos = textarea.selectionStart;
                            const textLength = textarea.value.length;
                            
                            if (e.key === 'ArrowUp' && cursorPos === 0) {
                              e.preventDefault();
                              if (rowIndex > 0) {
                                setSelectedCell({ row: rowIndex - 1, col: colIndex, type: 'data' });
                              }
                            } else if (e.key === 'ArrowDown' && cursorPos === textLength) {
                              e.preventDefault();
                              if (rowIndex < rows.length - 1) {
                                setSelectedCell({ row: rowIndex + 1, col: colIndex, type: 'data' });
                              }
                            } else if (e.key === 'ArrowLeft' && cursorPos === 0) {
                              e.preventDefault();
                              if (colIndex > 0) {
                                setSelectedCell({ row: rowIndex, col: colIndex - 1, type: 'data' });
                              }
                            } else if (e.key === 'ArrowRight' && cursorPos === textLength) {
                              e.preventDefault();
                              if (colIndex < columns.length - 1) {
                                setSelectedCell({ row: rowIndex, col: colIndex + 1, type: 'data' });
                              }
                            }
                          }
                        }}
                        onPaste={(e) => handlePaste(e, rowIndex, colIndex, 'data')}
                        className={`
                          border-0 text-sm focus-visible:ring-2 focus-visible:ring-blue-500 rounded-none resize-none
                          px-2 py-1 leading-tight
                          ${selectedCells.has(getCellKey(rowIndex, colIndex))
                            ? 'bg-blue-100 ring-2 ring-blue-400' 
                            : selectedCell?.row === rowIndex && selectedCell?.col === colIndex && selectedCell?.type === 'data'
                            ? 'bg-blue-50 ring-2 ring-blue-500' 
                            : 'bg-transparent'}
                        `}
                        placeholder="..."
                        rows={estimatedRows}
                        style={{
                          minHeight: '36px',
                          maxHeight: '200px',
                          overflowY: 'auto',
                          lineHeight: '1.4',
                        }}
                      />
                    </td>
                  );
                })}
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
          <li><strong>列名区域</strong>：点击任意列名粘贴一行列名，右键菜单可插入/删除列</li>
          <li><strong>行索引区域</strong>：点击任意行索引粘贴一列行索引</li>
          <li><strong>数据区域</strong>：点击单元格粘贴数据矩阵，自动扩展表格</li>
          <li><strong>文本换行</strong>：数据单元格支持多行文本，按 Enter 键换行，单元格高度自动调整</li>
          <li><strong>批量选择</strong>：鼠标拖拽选择多个单元格，按 Delete/Backspace 键批量删除，按 Ctrl+C 复制为 Excel 格式</li>
          <li><strong>智能数字解析</strong>：自动去除货币符号（$¥€£）、千位符（,）、加号（+），百分号（%）自动转换（50% → 0.5）</li>
          <li><strong>键盘导航</strong>：Tab 键移动到下一个单元格，Shift+Tab 移动到上一个单元格，方向键在文本边界时切换单元格</li>
        </ul>
      </div>
    </div>
  );
}
