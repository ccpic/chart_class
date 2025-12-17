"use client"

import * as React from "react"
import { Check, RotateCcw } from "lucide-react"
import { cn } from "@/lib/utils"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

// 常用 matplotlib colormaps 及其颜色值（RGB 0-255）
// 这些是简化版本，用于前端预览
const COLORMAP_DATA: Record<string, string[]> = {
  // Perceptually Uniform Sequential
  viridis: ["#440154", "#482777", "#3F4A8A", "#31678E", "#26838F", "#1F9D8A", "#2CB085", "#56C667", "#86D549", "#C2DF23", "#FEE825"],
  plasma: ["#0D0887", "#46039F", "#7201A8", "#9C179E", "#BD3786", "#D8576B", "#ED7953", "#FB9F3A", "#FDCA26", "#F0F921"],
  inferno: ["#000004", "#1B0C42", "#4B0A77", "#781C6D", "#A52C60", "#CF4446", "#ED6925", "#FB9A06", "#F7D03C", "#FCFFA4"],
  magma: ["#000004", "#1B0C42", "#4B0A77", "#781C6D", "#A52C60", "#CF4446", "#ED6925", "#FB9A06", "#F7D03C", "#FCFFA4"],
  cividis: ["#00204D", "#003570", "#1B4B7A", "#3D5F7F", "#5B7284", "#76858A", "#8F9890", "#A8AB97", "#C0BDA0", "#D9CFAB", "#F2E5B4"],
  
  // Sequential
  Blues: ["#F7FBFF", "#DEEBF7", "#C6DBEF", "#9ECAE1", "#6BAED6", "#4292C6", "#2171B5", "#08519C", "#08306B"],
  Greens: ["#F7FCF5", "#E5F5E0", "#C7E9C0", "#A1D99B", "#74C476", "#41AB5D", "#238B45", "#006D2C", "#00441B"],
  Oranges: ["#FFF5EB", "#FEE6CE", "#FDD0A2", "#FDAE6B", "#FD8D3C", "#F16913", "#D94801", "#A63603", "#7F2704"],
  Reds: ["#FFF5F0", "#FEE0D2", "#FCBBA1", "#FC9272", "#FB6A4A", "#EF3B2C", "#CB181D", "#A50F15", "#67000D"],
  Purples: ["#FCFBFD", "#EFEDF5", "#DADAEB", "#BCBDDC", "#9E9AC8", "#807DBA", "#6A51A3", "#54278F", "#3F007D"],
  Greys: ["#FFFFFF", "#F0F0F0", "#D9D9D9", "#BDBDBD", "#969696", "#737373", "#525252", "#252525", "#000000"],
  
  // Diverging
  PiYG: ["#C51B7D", "#DE77AE", "#F1B6DA", "#FDE0EF", "#F7F7F7", "#E6F5D0", "#B8E186", "#7FBC41", "#4D9221"],
  PRGn: ["#762A83", "#9970AB", "#C2A5CF", "#E7D4E8", "#F7F7F7", "#D9F0D3", "#A6DBA0", "#5AAE61", "#1B7837"],
  BrBG: ["#8C510A", "#BF812D", "#DFC27D", "#F6E8C3", "#F5F5F5", "#C7EAE5", "#80CDC1", "#35978F", "#01665E"],
  PuOr: ["#B35806", "#E08214", "#FDB863", "#FEE0B6", "#F7F7F7", "#D8DAEB", "#B2ABD2", "#8073AC", "#542788"],
  RdBu: ["#B2182B", "#D6604D", "#F4A582", "#FDDBC7", "#F7F7F7", "#D1E5F0", "#92C5DE", "#4393C3", "#2166AC"],
  RdYlGn: ["#A50026", "#D73027", "#F46D43", "#FDAE61", "#FEE08B", "#FFFFBF", "#E6F598", "#ABDDA4", "#66C2A5", "#3288BD", "#313695"],
  RdYlBu: ["#A50026", "#D73027", "#F46D43", "#FDAE61", "#FEE08B", "#FFFFCC", "#E0F3F8", "#ABD9E9", "#74ADD1", "#4575B4", "#313695"],
  Spectral: ["#9E0142", "#D53E4F", "#F46D43", "#FDAE61", "#FEE08B", "#FFFFBF", "#E6F598", "#ABDDA4", "#66C2A5", "#3288BD", "#5E4FA2"],
  
  // Cyclic
  hsv: ["#FF0000", "#FF7F00", "#FFFF00", "#7FFF00", "#00FF00", "#00FF7F", "#00FFFF", "#007FFF", "#0000FF", "#7F00FF", "#FF00FF", "#FF007F"],
  twilight: ["#E8E8E8", "#D0D0D0", "#B8B8B8", "#A0A0A0", "#888888", "#707070", "#585858", "#404040", "#282828", "#101010", "#000000"],
  
  // Other
  coolwarm: ["#3B4CC0", "#5C7AD1", "#7FA5D8", "#A3C9DD", "#C8DCE0", "#E8D4C8", "#E8B99F", "#E89C75", "#E67E4A", "#D55E1F"],
  cool: ["#00FFFF", "#00CCFF", "#0099FF", "#0066FF", "#0033FF", "#0000FF"],
  hot: ["#000000", "#330000", "#660000", "#990000", "#CC0000", "#FF0000", "#FF3300", "#FF6600", "#FF9900", "#FFCC00", "#FFFF00", "#FFFFCC"],
  jet: ["#000080", "#0000FF", "#0080FF", "#00FFFF", "#80FF80", "#FFFF00", "#FF8000", "#FF0000", "#800000"],
  rainbow: ["#FF0000", "#FF7F00", "#FFFF00", "#7FFF00", "#00FF00", "#00FF7F", "#00FFFF", "#007FFF", "#0000FF", "#7F00FF", "#FF00FF"],
  terrain: ["#00A600", "#63C600", "#E6E600", "#EAB64E", "#E6D200", "#E6B400", "#E69100", "#E67800", "#E64500", "#E60000"],
  ocean: ["#000000", "#000033", "#000066", "#000099", "#0000CC", "#0000FF", "#0033FF", "#0066FF", "#0099FF", "#00CCFF", "#00FFFF"],
  gist_earth: ["#000000", "#0000FF", "#00FFFF", "#00FF00", "#FFFF00", "#FF0000", "#FF00FF"],
  gist_heat: ["#000000", "#330000", "#660000", "#990000", "#CC0000", "#FF0000", "#FF3300", "#FF6600", "#FF9900", "#FFCC00", "#FFFF00"],
  gist_ncar: ["#000080", "#0000FF", "#00FFFF", "#00FF00", "#FFFF00", "#FF0000", "#FF00FF", "#800080"],
  gist_rainbow: ["#FF0000", "#FF7F00", "#FFFF00", "#7FFF00", "#00FF00", "#00FF7F", "#00FFFF", "#007FFF", "#0000FF", "#7F00FF", "#FF00FF"],
  gist_stern: ["#000000", "#000033", "#000066", "#000099", "#0000CC", "#0000FF", "#0033FF", "#0066FF", "#0099FF", "#00CCFF", "#00FFFF"],
  nipy_spectral: ["#000000", "#0000FF", "#00FFFF", "#00FF00", "#FFFF00", "#FF0000", "#FF00FF", "#800080"],
  seismic: ["#000080", "#0000FF", "#00FFFF", "#FFFFFF", "#FFFF00", "#FF0000", "#800000"],
  terrain_cmap: ["#00A600", "#63C600", "#E6E600", "#EAB64E", "#E6D200", "#E6B400", "#E69100", "#E67800", "#E64500", "#E60000"],
}

// 所有可用的 colormap 名称（按类别排序）
const COLORMAP_NAMES = [
  // Perceptually Uniform Sequential
  "viridis", "plasma", "inferno", "magma", "cividis",
  // Sequential
  "Blues", "Greens", "Oranges", "Reds", "Purples", "Greys",
  // Diverging
  "PiYG", "PRGn", "BrBG", "PuOr", "RdBu", "RdYlGn", "RdYlBu", "Spectral",
  // Cyclic
  "hsv", "twilight",
  // Other
  "coolwarm", "cool", "hot", "jet", "rainbow", "terrain", "ocean",
  "gist_earth", "gist_heat", "gist_ncar", "gist_rainbow", "gist_stern",
  "nipy_spectral", "seismic", "terrain_cmap",
] as const

export type ColormapName = typeof COLORMAP_NAMES[number]

interface CmapPickerProps {
  value?: string // 当前选中的 cmap 名称（可能包含 _r 后缀）
  onChange?: (value: string) => void // 返回完整的 cmap 名称（可能包含 _r）
  className?: string
  label?: string
  showPreview?: boolean // 是否显示预览
  showReverse?: boolean // 是否显示反向选项
}

/**
 * 解析 cmap 名称，分离基础名称和反向标志
 */
function parseCmapName(cmapName: string): { name: ColormapName; reversed: boolean } {
  if (cmapName.endsWith("_r")) {
    const baseName = cmapName.slice(0, -2) as ColormapName
    if (COLORMAP_NAMES.includes(baseName)) {
      return { name: baseName, reversed: true }
    }
  }
  return { name: cmapName as ColormapName, reversed: false }
}

/**
 * 生成渐变色预览的 CSS gradient
 */
function generateGradient(colors: string[], reversed: boolean = false): string {
  const colorList = reversed ? [...colors].reverse() : colors
  const stops = colorList.map((color, index) => {
    const percent = (index / (colorList.length - 1)) * 100
    return `${color} ${percent}%`
  }).join(", ")
  return `linear-gradient(to right, ${stops})`
}

/**
 * 获取 colormap 的渐变色
 */
function getCmapColors(cmapName: ColormapName): string[] {
  return COLORMAP_DATA[cmapName] || COLORMAP_DATA.viridis
}

export function CmapPicker({
  value = "PiYG",
  onChange,
  className,
  label = "颜色映射",
  showPreview = true,
  showReverse = true,
}: CmapPickerProps) {
  const { name: currentName, reversed: currentReversed } = parseCmapName(value)
  const [selectedName, setSelectedName] = React.useState<ColormapName>(currentName)
  const [reversed, setReversed] = React.useState<boolean>(currentReversed)

  // 当外部 value 变化时，更新内部状态
  React.useEffect(() => {
    const parsed = parseCmapName(value)
    setSelectedName(parsed.name)
    setReversed(parsed.reversed)
  }, [value])

  // 当选择变化时，通知外部
  const handleNameChange = (newName: ColormapName) => {
    setSelectedName(newName)
    const finalName = reversed ? `${newName}_r` : newName
    onChange?.(finalName)
  }

  const handleReverseChange = (checked: boolean) => {
    setReversed(checked)
    const finalName = checked ? `${selectedName}_r` : selectedName
    onChange?.(finalName)
  }

  const colors = getCmapColors(selectedName)
  const gradient = generateGradient(colors, reversed)

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <Label className="text-sm font-medium">{label}</Label>
      )}
      
      <div className="space-y-2">
        <Select value={selectedName} onValueChange={handleNameChange}>
          <SelectTrigger>
            <SelectValue placeholder="选择颜色映射" />
          </SelectTrigger>
          <SelectContent className="max-h-[300px]">
            {COLORMAP_NAMES.map((cmapName) => (
              <SelectItem key={cmapName} value={cmapName}>
                <div className="flex items-center gap-2">
                  {showPreview && (
                    <div
                      className="w-8 h-4 rounded border border-border"
                      style={{
                        background: generateGradient(getCmapColors(cmapName)),
                      }}
                    />
                  )}
                  <span>{cmapName}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {showPreview && (
          <div className="space-y-1">
            <div
              className="w-full h-8 rounded border border-border"
              style={{ background: gradient }}
            />
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>预览</span>
              <span>{reversed ? `${selectedName}_r` : selectedName}</span>
            </div>
          </div>
        )}

        {showReverse && (
          <div className="flex items-center space-x-2">
            <Checkbox
              id="reverse-cmap"
              checked={reversed}
              onCheckedChange={handleReverseChange}
            />
            <Label
              htmlFor="reverse-cmap"
              className="text-sm font-normal cursor-pointer flex items-center gap-1"
            >
              <RotateCcw className="h-3 w-3" />
              反向颜色映射
            </Label>
          </div>
        )}
      </div>
    </div>
  )
}

