'use client';

import React, { useState, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TagSelectorProps {
  value: string[];
  onChange: (tags: string[]) => void;
  availableTags?: string[];
  placeholder?: string;
  className?: string;
}

/**
 * Tag选择器组件
 * - 使用Badge显示已选tag
 * - 输入新tag（按Enter或逗号）自动添加
 * - 点击Badge上的X按钮删除tag
 * - 显示已有tag列表，点击添加到选中列表
 * - 输入时过滤已有tag列表（模糊搜索）
 */
export default function TagSelector({
  value,
  onChange,
  availableTags = [],
  placeholder = '输入tag并按Enter添加...',
  className,
}: TagSelectorProps) {
  const [inputValue, setInputValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 过滤可用的tag（排除已选中的，并根据输入值过滤）
  const filteredAvailableTags = React.useMemo(() => {
    const trimmedInput = inputValue.trim().toLowerCase();
    return availableTags.filter(
      (tag) =>
        !value.includes(tag) &&
        (trimmedInput === '' || tag.toLowerCase().includes(trimmedInput))
    );
  }, [availableTags, value, inputValue]);

  // 决定是否显示建议列表：只有在聚焦且有输入内容且有匹配结果时才显示
  const shouldShowSuggestions = React.useMemo(() => {
    return isFocused && inputValue.trim().length > 0 && filteredAvailableTags.length > 0;
  }, [isFocused, inputValue, filteredAvailableTags.length]);

  // 处理输入框按键事件
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(inputValue.trim());
    } else if (e.key === 'Backspace' && inputValue === '' && value.length > 0) {
      // 如果输入框为空且按了退格键，删除最后一个tag
      removeTag(value[value.length - 1]);
    } else if (e.key === 'Escape') {
      setIsFocused(false);
      inputRef.current?.blur();
    } else if (e.key === 'ArrowDown' && shouldShowSuggestions) {
      // 可以添加键盘导航功能（可选）
      e.preventDefault();
      // TODO: 实现键盘导航
    }
  };

  // 添加tag
  const addTag = (tag: string) => {
    if (!tag || value.includes(tag)) return;
    
    const newTags = [...value, tag];
    onChange(newTags);
    setInputValue('');
    // 保持聚焦状态，方便继续输入
    inputRef.current?.focus();
  };

  // 删除tag
  const removeTag = (tag: string) => {
    const newTags = value.filter((t) => t !== tag);
    onChange(newTags);
  };

  // 从可用列表中添加tag
  const handleSelectAvailableTag = (tag: string) => {
    addTag(tag);
  };

  return (
    <div className={cn('space-y-2', className)} ref={containerRef}>
      {/* 已选tag显示区域 */}
      <div className="relative flex flex-wrap gap-2 min-h-[2.5rem] p-2 border rounded-md bg-background">
        {value.map((tag) => (
          <Badge
            key={tag}
            variant="secondary"
            className="flex items-center gap-1 px-2 py-1"
          >
            <span>{tag}</span>
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="ml-1 rounded-full hover:bg-destructive/20 focus:outline-none focus:ring-2 focus:ring-ring"
              aria-label={`删除tag ${tag}`}
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
        
        {/* 输入框 */}
        <Input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            // 输入内容变化时，自动显示/隐藏建议列表（由 shouldShowSuggestions 控制）
          }}
          onKeyDown={handleInputKeyDown}
          onFocus={() => {
            setIsFocused(true);
          }}
          onBlur={() => {
            // 延迟关闭，以便点击选项时能触发
            setTimeout(() => {
              setIsFocused(false);
            }, 200);
          }}
          placeholder={value.length === 0 ? placeholder : ''}
          className="flex-1 min-w-[120px] border-0 focus-visible:ring-0 focus-visible:ring-offset-0 h-auto py-1"
        />
        
        {/* 可用tag建议列表 */}
        {shouldShowSuggestions && (
          <div className="absolute top-full left-0 right-0 z-50 mt-1 border rounded-md bg-popover shadow-md max-h-[200px] overflow-y-auto">
            <div className="text-xs text-muted-foreground px-2 py-1.5 font-medium border-b">
              可用tag
            </div>
            {filteredAvailableTags.map((tag) => (
              <button
                key={tag}
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault(); // 防止输入框失去焦点
                  handleSelectAvailableTag(tag);
                }}
                className="w-full text-left px-2 py-1.5 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none"
              >
                <div className="flex items-center gap-2">
                  <Plus className="h-3 w-3" />
                  <span>{tag}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
      
      {/* 提示信息 */}
      {value.length === 0 && inputValue === '' && !isFocused && (
        <p className="text-xs text-muted-foreground">
          输入tag名称并按Enter或逗号添加，输入时会显示匹配的建议tag
        </p>
      )}
      {isFocused && inputValue.trim().length > 0 && filteredAvailableTags.length === 0 && (
        <p className="text-xs text-muted-foreground">
          没有匹配的tag，按Enter创建新tag: &quot;{inputValue.trim()}&quot;
        </p>
      )}
    </div>
  );
}

