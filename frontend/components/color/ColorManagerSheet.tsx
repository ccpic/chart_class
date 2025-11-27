'use client';

import { useState, useEffect, useMemo } from 'react';
import { colorAPI, ColorMapping } from '@/lib/api/colorAPI';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SidebarMenuButton } from '@/components/ui/sidebar';
import ColorPicker from '@/components/color/ColorPicker';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
import { Palette, Plus, Search, Trash2, ArrowUp, ArrowDown } from 'lucide-react';

const mergePaletteWithColors = (
  palette: string[],
  colors: ColorMapping[]
): string[] => {
  const colorNames = colors.map((color) => color.name);
  const cleaned: string[] = [];
  const seen = new Set<string>();

  palette.forEach((name) => {
    if (colorNames.includes(name) && !seen.has(name)) {
      cleaned.push(name);
      seen.add(name);
    }
  });

  colorNames.forEach((name) => {
    if (!seen.has(name)) {
      cleaned.push(name);
      seen.add(name);
    }
  });

  return cleaned;
};

/**
 * 颜色管理面板组件
 *
 * 功能：
 * - 查看所有颜色映射
 * - 管理调色板顺序
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
  const [palette, setPalette] = useState<string[]>([]);
  const [isPaletteSaving, setIsPaletteSaving] = useState(false);
  const [paletteSelectValue, setPaletteSelectValue] = useState('');

  const [isAdding, setIsAdding] = useState(false);
  const [newColorName, setNewColorName] = useState('');
  const [newColorValue, setNewColorValue] = useState('#000000');

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [colorToDelete, setColorToDelete] = useState<string | null>(null);

  const { toast } = useToast();

  const loadColorData = async () => {
    setIsLoading(true);
    try {
      const [colorData, paletteData] = await Promise.all([
        colorAPI.listColors(),
        colorAPI.getPalette(),
      ]);
      setColors(colorData);
      setPalette(mergePaletteWithColors(paletteData, colorData));
    } catch (error) {
      toast({
        title: '加载失败',
        description: error instanceof Error ? error.message : '无法加载颜色数据',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadColorData();
    }
  }, [isOpen]);

  const colorLookup = useMemo(() => {
    const map = new Map<string, ColorMapping>();
    colors.forEach((color) => map.set(color.name, color));
    return map;
  }, [colors]);

  const filteredColors = useMemo(() => {
    if (!searchTerm.trim()) {
      return colors;
    }
    const term = searchTerm.trim().toLowerCase();
    return colors.filter((color) => color.name.toLowerCase().includes(term));
  }, [colors, searchTerm]);

  const availablePaletteCandidates = useMemo(
    () => colors.filter((color) => !palette.includes(color.name)),
    [colors, palette]
  );

  const movePaletteItem = (index: number, offset: number) => {
    setPalette((prev) => {
      const next = [...prev];
      const target = index + offset;
      if (target < 0 || target >= next.length) {
        return prev;
      }
      const [item] = next.splice(index, 1);
      next.splice(target, 0, item);
      return next;
    });
  };

  const removePaletteItem = (name: string) => {
    setPalette((prev) => prev.filter((item) => item !== name));
  };

  const handleAddToPalette = () => {
    if (!paletteSelectValue) return;
    setPalette((prev) =>
      prev.includes(paletteSelectValue) ? prev : [...prev, paletteSelectValue]
    );
    setPaletteSelectValue('');
  };

  const handleSavePalette = async () => {
    setIsPaletteSaving(true);
    try {
      await colorAPI.updatePalette(palette);
      toast({
        title: '已更新调色板',
        description: '新的颜色顺序将在渲染时生效',
      });
      await loadColorData();
    } catch (error) {
      toast({
        title: '保存失败',
        description: error instanceof Error ? error.message : '更新调色板时出错',
        variant: 'destructive',
      });
    } finally {
      setIsPaletteSaving(false);
    }
  };

  const handleUseCurrentOrder = () => {
    setPalette(colors.map((color) => color.name));
  };

  const handleDelete = async (name: string) => {
    try {
      await colorAPI.deleteColor(name);
      toast({
        title: '删除成功',
        description: `已删除颜色 "${name}"`,
      });
      await loadColorData();
    } catch (error) {
      toast({
        title: '删除失败',
        description: error instanceof Error ? error.message : '删除颜色时出错',
        variant: 'destructive',
      });
    }
  };

  const confirmDelete = (name: string) => {
    setColorToDelete(name);
    setDeleteConfirmOpen(true);
  };

  const handleColorChange = async (
    name: string,
    newColor: string,
    namedColor?: string
  ) => {
    try {
      await colorAPI.updateColor(name, {
        color: newColor,
        named_color: namedColor ?? null,
      });
      toast({
        title: '更新成功',
        description: `已更新颜色 "${name}"`,
      });
      await loadColorData();
    } catch (error) {
      toast({
        title: '更新失败',
        description: error instanceof Error ? error.message : '更新颜色时出错',
        variant: 'destructive',
      });
    }
  };

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
      await loadColorData();
    } catch (error) {
      toast({
        title: '添加失败',
        description: error instanceof Error ? error.message : '添加颜色时出错',
        variant: 'destructive',
      });
    }
  };

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
            管理图表颜色映射和默认调色板，共 {colors.length} 个颜色
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-4 mt-6">
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

          <div className="space-y-2 p-4 border rounded bg-muted/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm flex items-center gap-2">
                  <Palette className="h-4 w-4" />
                  全局调色板
                </p>
                <p className="text-xs text-muted-foreground">
                  调整默认颜色循环顺序，渲染时按此顺序分配颜色
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleUseCurrentOrder}
                  disabled={isPaletteSaving || colors.length === 0}
                >
                  使用当前顺序
                </Button>
                <Button
                  size="sm"
                  onClick={handleSavePalette}
                  disabled={isPaletteSaving || palette.length === 0}
                >
                  {isPaletteSaving ? '保存中...' : '保存调色板'}
                </Button>
              </div>
            </div>

            {palette.length === 0 ? (
              <p className="text-xs text-muted-foreground">
                当前没有调色板，请添加颜色后保存顺序。
              </p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                {palette.map((name, index) => {
                  const color = colorLookup.get(name);
                  const swatch = color?.color || '#cccccc';
                  return (
                    <div
                      key={name}
                      className="flex items-center gap-2 px-3 py-2 border rounded bg-background"
                    >
                      <div
                        className="w-6 h-6 rounded border"
                        style={{ backgroundColor: swatch }}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{name}</p>
                        {color?.named_color && (
                          <p className="text-xs text-muted-foreground truncate">
                            {color.named_color}
                          </p>
                        )}
                      </div>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          disabled={index === 0}
                          onClick={() => movePaletteItem(index, -1)}
                        >
                          <ArrowUp className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          disabled={index === palette.length - 1}
                          onClick={() => movePaletteItem(index, 1)}
                        >
                          <ArrowDown className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-destructive"
                          onClick={() => removePaletteItem(name)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {availablePaletteCandidates.length > 0 && (
              <div className="flex gap-2">
                <Select
                  value={paletteSelectValue}
                  onValueChange={setPaletteSelectValue}
                >
                  <SelectTrigger className="flex-1">
                    <SelectValue placeholder="选择颜色添加到调色板" />
                  </SelectTrigger>
                  <SelectContent>
                    {availablePaletteCandidates.map((color) => (
                      <SelectItem key={color.name} value={color.name}>
                        {color.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button onClick={handleAddToPalette} disabled={!paletteSelectValue}>
                  添加
                </Button>
              </div>
            )}
          </div>

          {!isAdding ? (
            <Button
              className="w-full"
              variant="outline"
              onClick={() => setIsAdding(true)}
            >
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

          <div className="space-y-2">
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">加载中...</div>
            ) : filteredColors.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                没有找到颜色
              </div>
            ) : (
              filteredColors.map((color) => (
                <div
                  key={color.name}
                  className="flex items-center gap-3 p-3 border rounded hover:bg-accent"
                >
                  <div className="flex-shrink-0">
                    <ColorPicker
                      value={color.color}
                      namedColor={color.named_color || undefined}
                      onChange={(newColor, namedColor) =>
                        handleColorChange(color.name, newColor, namedColor)
                      }
                      showColorValue={false}
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{color.name}</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-2 flex-wrap">
                      {color.named_color && (
                        <span
                          className="font-medium"
                          style={{ color: color.color }}
                        >
                          {color.named_color}
                        </span>
                      )}
                      <span className="font-mono">{color.color}</span>
                    </div>
                  </div>

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
