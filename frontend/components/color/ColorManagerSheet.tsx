'use client';

import { useState, useEffect } from 'react';
import { colorAPI, ColorMapping } from '@/lib/api/colorAPI';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SidebarMenuButton } from '@/components/ui/sidebar';
import ColorPicker from '@/components/color/ColorPicker';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { Palette, Plus, Search, Trash2 } from 'lucide-react';

/**
 * 颜色管理面板组件
 * 
 * 功能：
 * - 查看所有颜色映射
 * - 搜索/筛选颜色
 * - 添加新颜色
 * - 直接修改颜色值
 * - 删除颜色
 */
export default function ColorManagerSheet() {
  const [colors, setColors] = useState<ColorMapping[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  
  // 添加新颜色状态
  const [isAdding, setIsAdding] = useState(false);
  const [newColorName, setNewColorName] = useState('');
  const [newColorValue, setNewColorValue] = useState('#000000');
  
  // 删除确认对话框
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [colorToDelete, setColorToDelete] = useState<string | null>(null);

  const { toast } = useToast();

  // 加载颜色列表
  const loadColors = async () => {
    setIsLoading(true);
    try {
      const data = await colorAPI.listColors({
        search: searchTerm || undefined,
      });
      setColors(data);
    } catch (error) {
      toast({
        title: '加载失败',
        description: error instanceof Error ? error.message : '无法加载颜色列表',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 删除颜色
  const handleDelete = async (name: string) => {
    try {
      await colorAPI.deleteColor(name);
      toast({
        title: '删除成功',
        description: `已删除颜色 "${name}"`,
      });
      loadColors();
    } catch (error) {
      toast({
        title: '删除失败',
        description: error instanceof Error ? error.message : '删除颜色时出错',
        variant: 'destructive',
      });
    }
  };

  // 打开删除确认对话框
  const confirmDelete = (name: string) => {
    setColorToDelete(name);
    setDeleteConfirmOpen(true);
  };

  // 更新颜色值
  const handleColorChange = async (name: string, newColor: string, namedColor?: string) => {
    try {
      await colorAPI.updateColor(name, { 
        color: newColor,
        named_color: namedColor ?? null, // undefined 转为 null，确保传递该字段
      });
      toast({
        title: '更新成功',
        description: `已更新颜色 "${name}"`,
      });
      loadColors();
    } catch (error) {
      toast({
        title: '更新失败',
        description: error instanceof Error ? error.message : '更新颜色时出错',
        variant: 'destructive',
      });
    }
  };

  // 添加新颜色
  const handleAddColor = async () => {
    if (!newColorName || !newColorValue) {
      toast({
        title: '验证失败',
        description: '颜色名称和颜色值不能为空',
        variant: 'destructive',
      });
      return;
    }

    try {
      await colorAPI.createColor({
        name: newColorName,
        color: newColorValue,
        overwrite: false,
      });
      toast({
        title: '添加成功',
        description: `已添加颜色 "${newColorName}"`,
      });
      setIsAdding(false);
      setNewColorName('');
      setNewColorValue('#000000');
      loadColors();
    } catch (error) {
      toast({
        title: '添加失败',
        description: error instanceof Error ? error.message : '添加颜色时出错',
        variant: 'destructive',
      });
    }
  };

  // Sheet 打开时加载数据
  useEffect(() => {
    if (isOpen) {
      loadColors();
    }
  }, [isOpen, searchTerm]);

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <SidebarMenuButton>
          <Palette className="size-4" />
          <span>颜色管理</span>
        </SidebarMenuButton>
      </SheetTrigger>
      <SheetContent side="right" className="w-full sm:max-w-xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>颜色映射管理</SheetTitle>
          <SheetDescription>
            管理图表颜色映射配置，共 {colors.length} 个颜色
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-4 mt-6">
          {/* 搜索和筛选 */}
          <div className="flex gap-2">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="搜索颜色名称..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
          </div>

          {/* 添加新颜色按钮/表单 */}
          {!isAdding ? (
            <Button className="w-full" variant="outline" onClick={() => setIsAdding(true)}>
              <Plus className="mr-2 h-4 w-4" />
              添加新颜色
            </Button>
          ) : (
            <div className="space-y-3 p-4 border rounded bg-muted/50">
              <div className="space-y-2">
                <Label htmlFor="newColorName">颜色名称 *</Label>
                <Input
                  id="newColorName"
                  value={newColorName}
                  onChange={(e) => setNewColorName(e.target.value)}
                  placeholder="例如：品牌红色"
                />
              </div>
              <ColorPicker 
                label="颜色值 *"
                value={newColorValue}
                onChange={setNewColorValue}
              />
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => {
                    setIsAdding(false);
                    setNewColorName('');
                    setNewColorValue('#000000');
                  }}
                >
                  取消
                </Button>
                <Button className="flex-1" onClick={handleAddColor}>
                  添加
                </Button>
              </div>
            </div>
          )}

          {/* 颜色列表 */}
          <div className="space-y-2">
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">
                加载中...
              </div>
            ) : colors.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                没有找到颜色
              </div>
            ) : (
              colors.map((color) => (
                <div
                  key={color.name}
                  className="flex items-center gap-3 p-3 border rounded hover:bg-accent"
                >
                  {/* 颜色选择器 */}
                  <div className="flex-shrink-0">
                    <ColorPicker 
                      value={color.color}
                      onChange={(newColor, namedColor) => handleColorChange(color.name, newColor, namedColor)}
                      showColorValue={false}
                    />
                  </div>

                  {/* 颜色信息 */}
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{color.name}</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-2">
                      <span>{color.color}</span>
                      {color.named_color && (
                        <span 
                          className="font-medium"
                          style={{ color: color.color }}
                        >
                          {color.named_color}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* 删除按钮 */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive flex-shrink-0"
                    onClick={() => confirmDelete(color.name)}
                    title="删除"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))
            )}
          </div>
        </div>
      </SheetContent>

      {/* 删除确认对话框 */}
      <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除颜色 <strong>"{colorToDelete}"</strong> 吗？
              此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (colorToDelete) {
                  handleDelete(colorToDelete);
                  setDeleteConfirmOpen(false);
                  setColorToDelete(null);
                }
              }}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Sheet>
  );
}
