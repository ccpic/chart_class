'use client';

import { useState, useEffect, useMemo } from 'react';
import { colorAPI, ColorMapping } from '@/lib/api/colorAPI';
import { paletteAPI, PaletteListItem } from '@/lib/api/paletteAPI';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SidebarMenuButton } from '@/components/ui/sidebar';
import ColorPicker from '@/components/color/ColorPicker';
import ColorPalette from '@/components/color/ColorPalette';
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
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from '@/components/ui/tabs';
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
import { Palette, Plus, Search, Trash2, Edit2 } from 'lucide-react';
import { useCanvasStore } from '@/store/canvasStore';

// 注意：调色板现在直接存储颜色值，不再依赖颜色映射
// 此函数已废弃，保留仅用于兼容

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
  const [paletteList, setPaletteList] = useState<PaletteListItem[]>([]);
  const [currentPaletteName, setCurrentPaletteName] = useState<string>('默认');
  const [isCreatingPalette, setIsCreatingPalette] = useState(false);
  const [newPaletteName, setNewPaletteName] = useState('');
  const [paletteToDelete, setPaletteToDelete] = useState<string | null>(null);
  const [deletePaletteConfirmOpen, setDeletePaletteConfirmOpen] = useState(false);

  const [isAdding, setIsAdding] = useState(false);
  const [newColorName, setNewColorName] = useState('');
  const [newColorValue, setNewColorValue] = useState('#000000');

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [colorToDelete, setColorToDelete] = useState<string | null>(null);

  const { toast } = useToast();
  const { setSelectedPalette } = useCanvasStore();

  const loadColorData = async () => {
    setIsLoading(true);
    try {
      const [colorData, paletteListData] = await Promise.all([
        colorAPI.listColors(),
        paletteAPI.listPalettes(),
      ]);
      setColors(colorData);
      setPaletteList(paletteListData);
      
      // 加载当前选中的调色板
      await loadCurrentPalette();
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

  const loadCurrentPalette = async () => {
    try {
      // 如果当前调色板是默认调色板，使用 getDefaultPalette
      if (currentPaletteName === '默认') {
        const defaultPalette = await paletteAPI.getDefaultPalette();
        setPalette(defaultPalette);
      } else {
        // 否则获取指定调色板
        const paletteData = await paletteAPI.getPalette(currentPaletteName);
        setPalette(paletteData.colors);
      }
    } catch (error) {
      toast({
        title: '加载调色板失败',
        description: error instanceof Error ? error.message : '无法加载调色板',
        variant: 'destructive',
      });
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadColorData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && currentPaletteName && paletteList.length > 0) {
      loadCurrentPalette();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPaletteName]);

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

  // 注意：调色板现在直接存储颜色值，不再从颜色映射中选择
  // availablePaletteCandidates 已不再需要

  const handlePaletteChange = (newColors: string[]) => {
    setPalette(newColors);
  };

  const handleSavePalette = async () => {
    setIsPaletteSaving(true);
    try {
      if (currentPaletteName === '默认') {
        await paletteAPI.updateDefaultPalette(palette);
      } else {
        await paletteAPI.updatePalette(currentPaletteName, { colors: palette });
      }
      toast({
        title: '已更新调色板',
        description: `调色板 "${currentPaletteName}" 已保存`,
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

  const handleCreatePalette = async () => {
    if (!newPaletteName.trim()) {
      toast({
        title: '验证失败',
        description: '调色板名称不能为空',
        variant: 'destructive',
      });
      return;
    }

    try {
      await paletteAPI.createPalette({
        name: newPaletteName.trim(),
        colors: palette.length > 0 ? palette : ['#808080'],
      });
      toast({
        title: '创建成功',
        description: `调色板 "${newPaletteName}" 已创建`,
      });
      setIsCreatingPalette(false);
      setNewPaletteName('');
      await loadColorData();
      const createdPaletteName = newPaletteName.trim();
      setCurrentPaletteName(createdPaletteName);
      // 同步更新到 canvasStore，应用到当前画布
      setSelectedPalette(createdPaletteName);
    } catch (error) {
      toast({
        title: '创建失败',
        description: error instanceof Error ? error.message : '创建调色板时出错',
        variant: 'destructive',
      });
    }
  };

  const handleDeletePalette = async (name: string) => {
    try {
      await paletteAPI.deletePalette(name);
      toast({
        title: '删除成功',
        description: `调色板 "${name}" 已删除`,
      });
      // 如果删除的是当前调色板，切换到默认调色板
      if (name === currentPaletteName) {
        setCurrentPaletteName('默认');
        // 同步更新到 canvasStore
        setSelectedPalette(null);
      }
      await loadColorData();
    } catch (error) {
      toast({
        title: '删除失败',
        description: error instanceof Error ? error.message : '删除调色板时出错',
        variant: 'destructive',
      });
    }
  };

  const confirmDeletePalette = (name: string) => {
    setPaletteToDelete(name);
    setDeletePaletteConfirmOpen(true);
  };

  const handleUseCurrentOrder = () => {
    // 使用当前颜色映射的颜色值作为调色板
    setPalette(colors.map((color) => color.named_color || color.color));
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
          <SheetTitle>颜色管理</SheetTitle>
          <SheetDescription>
            管理颜色映射和调色板，共 {colors.length} 个颜色
          </SheetDescription>
        </SheetHeader>

        <Tabs defaultValue="colors" className="mt-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="colors">颜色映射</TabsTrigger>
            <TabsTrigger value="palette">调色板</TabsTrigger>
          </TabsList>

          <TabsContent value="colors" className="space-y-4 mt-4">
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
          </TabsContent>

          <TabsContent value="palette" className="space-y-4 mt-4">
            {/* 调色板列表 */}
            <div className="space-y-2 p-4 border rounded bg-muted/30">
              <div className="flex items-center justify-between">
                <p className="font-medium text-sm flex items-center gap-2">
                  <Palette className="h-4 w-4" />
                  调色板方案
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setIsCreatingPalette(true)}
                  disabled={isCreatingPalette}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  新建调色板
                </Button>
              </div>

              {isCreatingPalette ? (
                <div className="flex gap-2 p-2 border rounded bg-background">
                  <Input
                    placeholder="输入调色板名称..."
                    value={newPaletteName}
                    onChange={(e) => setNewPaletteName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleCreatePalette();
                      } else if (e.key === 'Escape') {
                        setIsCreatingPalette(false);
                        setNewPaletteName('');
                      }
                    }}
                    autoFocus
                  />
                  <Button size="sm" onClick={handleCreatePalette} disabled={!newPaletteName.trim()}>
                    创建
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setIsCreatingPalette(false);
                      setNewPaletteName('');
                    }}
                  >
                    取消
                  </Button>
                </div>
              ) : null}

              <div className="space-y-1 max-h-48 overflow-y-auto">
                {paletteList.map((p) => (
                  <div
                    key={p.id}
                    className={`
                      flex items-center justify-between p-2 rounded border cursor-pointer
                      ${currentPaletteName === p.name ? 'bg-primary/10 border-primary' : 'hover:bg-accent'}
                    `}
                    onClick={() => {
                      setCurrentPaletteName(p.name);
                      // 同步更新到 canvasStore，应用到当前画布
                      setSelectedPalette(p.name === '默认' ? null : p.name);
                    }}
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <Palette className="h-4 w-4 flex-shrink-0" />
                      <span className="font-medium text-sm truncate">{p.name}</span>
                      {p.is_default && (
                        <span className="text-xs text-muted-foreground">(默认)</span>
                      )}
                      <span className="text-xs text-muted-foreground">
                        {p.color_count} 个颜色
                      </span>
                    </div>
                    {!p.is_default && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          confirmDeletePalette(p.name);
                        }}
                        title="删除调色板"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* 当前调色板编辑 */}
            <div className="space-y-4 p-4 border rounded bg-muted/30">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-sm flex items-center gap-2">
                    <Edit2 className="h-4 w-4" />
                    {currentPaletteName === '默认' ? '默认调色板' : `调色板: ${currentPaletteName}`}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    点击颜色方块可编辑颜色，调整颜色循环顺序，渲染时按此顺序分配颜色
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

              <div className="py-2">
                <ColorPalette
                  colors={palette}
                  onChange={handlePaletteChange}
                  allowAdd={true}
                  allowRemove={true}
                  disabled={isPaletteSaving}
                  size="md"
                  defaultColor="#808080"
                />
              </div>

              {palette.length === 0 && (
                <p className="text-xs text-muted-foreground text-center py-4">
                  当前调色板为空，点击 + 按钮添加颜色
                </p>
              )}
            </div>
          </TabsContent>
        </Tabs>
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

      <AlertDialog open={deletePaletteConfirmOpen} onOpenChange={setDeletePaletteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除调色板</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除调色板 <strong>"{paletteToDelete}"</strong> 吗？
              此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (paletteToDelete) {
                  handleDeletePalette(paletteToDelete);
                  setDeletePaletteConfirmOpen(false);
                  setPaletteToDelete(null);
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
