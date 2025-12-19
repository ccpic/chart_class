'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Trash2, Map as MapIcon } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import ColorPicker from '@/components/color/ColorPicker';
import NumberFormatEditor from '@/components/ui/number-format-editor';
import { CmapPicker } from '@/components/ui/cmap-picker';
import LabelStyleEditor, { LabelStyle } from '@/components/ui/label-style-editor';

interface Props {
  subplot: SubplotConfig;
}

/**
 * 热力地图参数编辑器
 * 对应后端 PlotMap 类的参数
 */
export default function MapParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  };

  // 从 params 中获取当前值，如果没有则使用默认值
  const params = subplot.params || {};
  
  // 基础参数
  const level = params.level ?? 'province';
  const scope = params.scope ?? 'national';
  const regions = params.regions ?? [];
  const excludeRegions = params.exclude_regions ?? ['三沙市'];
  const valueColumn = params.value_column ?? '';
  const regionColumn = params.region_column ?? '';
  const provinceColumn = params.province_column ?? '';
  const cityColumn = params.city_column ?? '';
  const countyColumn = params.county_column ?? '';
  
  // 标签参数
  const labelColumn = params.label_column ?? '';
  const labelFormat = params.label_format ?? '{index}';
  const labelValueFormat = params.label_value_format ?? '{:,.0f}';
  const labelFontsize = params.label_fontsize ?? 8;
  const useAbbr = params.use_abbr ?? false;
  const labelStyle: LabelStyle = params.label_style ?? {};
  
  // 样式参数
  const colorMappingMode = params.color_mapping_mode ?? 'colormap'; // 'colormap' | 'categorical'
  const cmap = params.cmap ?? 'PiYG';
  const colorMapping = params.color_mapping ?? {}; // 分类映射的键值对 {value: color}
  const hatchMapping = params.hatch_mapping ?? {}; // 纹理映射的键值对 {value: {hatch: string, density: number, color: string}}
  
  // 使用数组来维护映射项的顺序，每个项有稳定的 ID
  // 数组项格式：{id: string, key: string}
  const [colorMappingOrder, setColorMappingOrder] = useState<Array<{id: string, key: string}>>([]);
  const [hatchMappingOrder, setHatchMappingOrder] = useState<Array<{id: string, key: string}>>([]);
  
  // ID 计数器（用于生成唯一 ID）
  const colorIdCounterRef = useRef(0);
  const hatchIdCounterRef = useRef(0);
  
  // 同步颜色映射的顺序（当映射变化时更新）
  // 只处理添加和删除，不处理键值改变（键值改变由 onChange 处理）
  useEffect(() => {
    const colorKeys = Object.keys(colorMapping || {});
    const currentKeys = new Set(colorMappingOrder.map(item => item.key));
    const newKeys = new Set(colorKeys);
    
    // 检查是否有新增或删除的项
    const hasNewItems = colorKeys.some(key => !currentKeys.has(key));
    const hasRemovedItems = colorMappingOrder.some(item => !newKeys.has(item.key));
    
    // 只有当有新增或删除时才更新
    if (hasNewItems || hasRemovedItems) {
      // 创建新的顺序数组
      const newOrder: Array<{id: string, key: string}> = [];
      
      // 首先，保留仍然存在的项（按原顺序）
      colorMappingOrder.forEach(item => {
        if (newKeys.has(item.key)) {
          newOrder.push(item);
        }
      });
      
      // 然后，添加新的项
      colorKeys.forEach(key => {
        if (!currentKeys.has(key)) {
          newOrder.push({
            id: `color_${++colorIdCounterRef.current}_${Date.now()}`,
            key: key
          });
        }
      });
      
      setColorMappingOrder(newOrder);
    }
  }, [colorMapping, colorMappingOrder]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // 同步纹理映射的顺序（当映射变化时更新）
  // 只处理添加和删除，不处理键值改变（键值改变由 onChange 处理）
  useEffect(() => {
    const hatchKeys = Object.keys(hatchMapping || {});
    const currentKeys = new Set(hatchMappingOrder.map(item => item.key));
    const newKeys = new Set(hatchKeys);
    
    // 检查是否有新增或删除的项
    const hasNewItems = hatchKeys.some(key => !currentKeys.has(key));
    const hasRemovedItems = hatchMappingOrder.some(item => !newKeys.has(item.key));
    
    // 只有当有新增或删除时才更新
    if (hasNewItems || hasRemovedItems) {
      // 创建新的顺序数组
      const newOrder: Array<{id: string, key: string}> = [];
      
      // 首先，保留仍然存在的项（按原顺序）
      hatchMappingOrder.forEach(item => {
        if (newKeys.has(item.key)) {
          newOrder.push(item);
        }
      });
      
      // 然后，添加新的项
      hatchKeys.forEach(key => {
        if (!currentKeys.has(key)) {
          newOrder.push({
            id: `hatch_${++hatchIdCounterRef.current}_${Date.now()}`,
            key: key
          });
        }
      });
      
      setHatchMappingOrder(newOrder);
    }
  }, [hatchMapping, hatchMappingOrder]); // eslint-disable-line react-hooks/exhaustive-deps
  const vmin = params.vmin;
  const vmax = params.vmax;
  const edgecolor = params.edgecolor ?? 'black';
  const linewidth = params.linewidth ?? 0.5;
  const nationalBorderWidth = params.national_border_width ?? null;
  const provinceBorderWidth = params.province_border_width ?? null;
  const cityBorderWidth = params.city_border_width ?? null;
  const showColorbar = params.show_colorbar ?? true;
  const dissolveUrban = params.dissolve_urban ?? false;

  // 新区域输入状态
  const [newRegion, setNewRegion] = useState('');
  const [newExcludeRegion, setNewExcludeRegion] = useState('');

  // 获取数据列名列表
  const columnOptions = subplot.data?.columns || [];

  // 常用省份列表
  const commonProvinces = [
    '北京', '上海', '广东', '浙江', '江苏', '山东', '四川', '河南',
    '湖北', '湖南', '河北', '福建', '云南', '贵州', '陕西', '重庆',
    '辽宁', '吉林', '黑龙江', '安徽', '江西', '广西', '海南', '内蒙古',
    '新疆', '西藏', '青海', '甘肃', '宁夏', '天津', '山西',
  ];

  // 常用城市列表（示例）
  const commonCities = [
    '昆明', '成都', '贵阳', '重庆', '西安', '兰州', '银川', '西宁',
    '乌鲁木齐', '拉萨', '呼和浩特', '石家庄', '太原', '济南', '郑州',
    '武汉', '长沙', '南昌', '合肥', '南京', '杭州', '福州', '广州',
    '南宁', '海口', '沈阳', '长春', '哈尔滨', '大连', '青岛', '厦门',
  ];


  return (
    <div className="space-y-4">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="basic" className="text-xs">基础设置</TabsTrigger>
          <TabsTrigger value="region" className="text-xs">区域范围</TabsTrigger>
          <TabsTrigger value="label" className="text-xs">标签设置</TabsTrigger>
          <TabsTrigger value="style" className="text-xs">样式设置</TabsTrigger>
        </TabsList>

        {/* Tab 1: 基础设置 */}
        <TabsContent value="basic" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">数据层级与范围</h4>
            
            <div className="space-y-2">
              <Label htmlFor="level" className="text-sm">
                数据粒度 (level)
              </Label>
              <Select
                value={level}
                onValueChange={(value) => updateParam('level', value)}
              >
                <SelectTrigger id="level">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="province">省级数据</SelectItem>
                  <SelectItem value="prefecture">地级市数据</SelectItem>
                  <SelectItem value="county">区县数据</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">
                {level === 'province' && '数据为省级统计数据'}
                {level === 'prefecture' && '数据为地级市/自治州统计数据'}
                {level === 'county' && '数据为区县级统计数据'}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="scope" className="text-sm">
                地图范围 (scope)
              </Label>
              <Select
                value={scope}
                onValueChange={(value) => updateParam('scope', value)}
              >
                <SelectTrigger id="scope">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="national">全国范围</SelectItem>
                  <SelectItem value="provinces">指定省份集合</SelectItem>
                  <SelectItem value="cities">指定地级市集合</SelectItem>
                  <SelectItem value="counties">指定区县集合</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">
                {scope === 'national' && '显示全国地图（自动排除三沙市避免变形）'}
                {scope === 'provinces' && '显示指定省份的地图（需在"区域范围"标签页指定）'}
                {scope === 'cities' && '显示指定地级市的地图（需在"区域范围"标签页指定）'}
                {scope === 'counties' && '显示指定区县的地图（需在"区域范围"标签页指定）'}
              </p>
            </div>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">数据列设置</h4>
            
            <div className="space-y-2">
              <Label htmlFor="value_column" className="text-sm">
                数值列 (value_column)
              </Label>
              {columnOptions.length > 0 ? (
                <Select
                  value={valueColumn || columnOptions[0] || ''}
                  onValueChange={(value) => updateParam('value_column', value || '')}
                >
                  <SelectTrigger id="value_column" className="text-sm">
                    <SelectValue placeholder="选择数值列" />
                  </SelectTrigger>
                  <SelectContent>
                    {columnOptions.map((col: string) => (
                      <SelectItem key={col} value={col}>
                        {col}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <div className="h-10 px-3 py-2 text-sm border border-gray-200 rounded-md bg-gray-50 text-gray-500 flex items-center">
                  暂无数据列
                </div>
              )}
              <p className="text-xs text-gray-500">
                用于地图着色的数值列名，如不指定则自动使用数据的第一列
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="region_column" className="text-sm">
                区域列 (region_column)
              </Label>
              {columnOptions.length > 0 ? (
                <Select
                  value={regionColumn || '__index__'}
                  onValueChange={(value) => {
                    const newValue = value === '__index__' ? '' : value;
                    updateParam('region_column', newValue);
                  }}
                >
                  <SelectTrigger id="region_column" className="text-sm">
                    <SelectValue placeholder="留空则使用索引" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__index__">（使用索引）</SelectItem>
                    {columnOptions.map((col: string) => (
                      <SelectItem key={col} value={col}>
                        {col}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <div className="h-10 px-3 py-2 text-sm border border-gray-200 rounded-md bg-gray-50 text-gray-500 flex items-center">
                  暂无数据列
                </div>
              )}
              <p className="text-xs text-gray-500">
                包含行政区划名称的列名，留空则使用数据索引
                {level === 'county' && '（区县层级建议使用省市区县列）'}
              </p>
            </div>

            {/* 区县层级的省市区县列设置 */}
            {level === 'county' && (
              <>
                <div className="space-y-2 pt-2 border-t">
                  <Label htmlFor="province_column" className="text-sm">
                    省级列 (province_column) <span className="text-red-500">*</span>
                  </Label>
                  {columnOptions.length > 0 ? (
                    <Select
                      value={provinceColumn || ''}
                      onValueChange={(value) => updateParam('province_column', value || '')}
                    >
                      <SelectTrigger id="province_column" className="text-sm">
                        <SelectValue placeholder="选择省级列" />
                      </SelectTrigger>
                      <SelectContent>
                        {columnOptions.map((col: string) => (
                          <SelectItem key={col} value={col}>
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <div className="h-10 px-3 py-2 text-sm border border-gray-200 rounded-md bg-gray-50 text-gray-500 flex items-center">
                      暂无数据列
                    </div>
                  )}
                  <p className="text-xs text-gray-500">
                    区县层级必须提供省级列，用于唯一标识区县（区县名有重复）
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="city_column" className="text-sm">
                    地级市列 (city_column) <span className="text-red-500">*</span>
                  </Label>
                  {columnOptions.length > 0 ? (
                    <Select
                      value={cityColumn || ''}
                      onValueChange={(value) => updateParam('city_column', value || '')}
                    >
                      <SelectTrigger id="city_column" className="text-sm">
                        <SelectValue placeholder="选择地级市列" />
                      </SelectTrigger>
                      <SelectContent>
                        {columnOptions.map((col: string) => (
                          <SelectItem key={col} value={col}>
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <div className="h-10 px-3 py-2 text-sm border border-gray-200 rounded-md bg-gray-50 text-gray-500 flex items-center">
                      暂无数据列
                    </div>
                  )}
                  <p className="text-xs text-gray-500">
                    区县层级必须提供地级市列，用于唯一标识区县
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="county_column" className="text-sm">
                    区县列 (county_column) <span className="text-red-500">*</span>
                  </Label>
                  {columnOptions.length > 0 ? (
                    <Select
                      value={countyColumn || ''}
                      onValueChange={(value) => updateParam('county_column', value || '')}
                    >
                      <SelectTrigger id="county_column" className="text-sm">
                        <SelectValue placeholder="选择区县列" />
                      </SelectTrigger>
                      <SelectContent>
                        {columnOptions.map((col: string) => (
                          <SelectItem key={col} value={col}>
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <div className="h-10 px-3 py-2 text-sm border border-gray-200 rounded-md bg-gray-50 text-gray-500 flex items-center">
                      暂无数据列
                    </div>
                  )}
                  <p className="text-xs text-gray-500">
                    区县层级必须提供区县列，如未指定则使用 region_column
                  </p>
                </div>

                <div className="mt-3 p-3 bg-blue-50 rounded-md border border-blue-200">
                  <p className="text-xs text-blue-800">
                    <strong>提示：</strong>由于中国区县名有重复（如多个"朝阳区"），
                    区县层级必须提供省市区县四级数据才能正确匹配。
                    特殊处理：东莞、中山、嘉峪关、儋州这4个地级市无下属区县，
                    会自动降级为地级市显示。
                  </p>
                </div>
              </>
            )}
          </div>
        </TabsContent>

        {/* Tab 2: 区域范围 */}
        <TabsContent value="region" className="space-y-4 mt-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-gray-800">
                指定区域列表 (regions)
              </h4>
              <span className="text-xs text-gray-500">
                {regions.length} 个区域
              </span>
            </div>
            
            {scope !== 'national' && (
              <>
                <p className="text-xs text-gray-500">
                  {scope === 'provinces' && '指定要显示的省份/自治区/直辖市'}
                  {scope === 'cities' && '指定要显示的地级市/自治州'}
                  {scope === 'counties' && '指定要显示的区县'}
                </p>

                {/* 快速选择常用区域 */}
                {scope === 'provinces' && (
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">快速添加省份</Label>
                    <div className="grid grid-cols-6 gap-1 p-2 bg-gray-50 rounded border">
                      {commonProvinces.map((province) => (
                        <Button
                          key={province}
                          size="sm"
                          variant={regions.includes(province) ? "default" : "outline"}
                          onClick={() => {
                            if (regions.includes(province)) {
                              updateParam('regions', regions.filter((r: string) => r !== province));
                            } else {
                              updateParam('regions', [...regions, province]);
                            }
                          }}
                          className="text-xs h-7 px-1"
                        >
                          {province}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {scope === 'cities' && (
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">快速添加城市</Label>
                    <div className="grid grid-cols-6 gap-1 p-2 bg-gray-50 rounded border">
                      {commonCities.map((city) => (
                        <Button
                          key={city}
                          size="sm"
                          variant={regions.includes(city) ? "default" : "outline"}
                          onClick={() => {
                            if (regions.includes(city)) {
                              updateParam('regions', regions.filter((r: string) => r !== city));
                            } else {
                              updateParam('regions', [...regions, city]);
                            }
                          }}
                          className="text-xs h-7 px-1"
                        >
                          {city}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* 手动添加区域 */}
                <div className="space-y-2">
                  <Label className="text-xs font-medium">手动添加区域</Label>
                  <div className="flex gap-2">
                    <Input
                      value={newRegion}
                      onChange={(e) => setNewRegion(e.target.value)}
                      placeholder="输入区域名称"
                      className="text-sm flex-1"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newRegion.trim()) {
                          if (!regions.includes(newRegion.trim())) {
                            updateParam('regions', [...regions, newRegion.trim()]);
                          }
                          setNewRegion('');
                        }
                      }}
                    />
                    <Button
                      size="sm"
                      onClick={() => {
                        if (newRegion.trim() && !regions.includes(newRegion.trim())) {
                          updateParam('regions', [...regions, newRegion.trim()]);
                          setNewRegion('');
                        }
                      }}
                      className="gap-2"
                    >
                      <Plus className="h-3 w-3" />
                      添加
                    </Button>
                  </div>
                </div>

                {/* 已选区域列表 */}
                {regions.length > 0 && (
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">已选区域</Label>
                    <div className="flex flex-wrap gap-2 p-2 bg-gray-50 rounded border max-h-32 overflow-y-auto">
                      {regions.map((region: string, index: number) => (
                        <div
                          key={index}
                          className="inline-flex items-center gap-1 px-2 py-1 bg-white border rounded text-xs"
                        >
                          <span>{region}</span>
                          <button
                            onClick={() => {
                              updateParam('regions', regions.filter((_: string, i: number) => i !== index));
                            }}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {scope === 'national' && (
              <div className="text-center py-8 text-sm text-gray-400">
                全国范围模式下不需要指定区域
              </div>
            )}
          </div>

          <div className="space-y-3 pt-3 border-t">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-gray-800">
                排除区域 (exclude_regions)
              </h4>
              <span className="text-xs text-gray-500">
                {excludeRegions.length} 个排除
              </span>
            </div>
            
            <p className="text-xs text-gray-500">
              指定要从地图中排除的区域（默认排除三沙市以避免地图变形）
            </p>

            {/* 手动添加排除区域 */}
            <div className="space-y-2">
              <div className="flex gap-2">
                <Input
                  value={newExcludeRegion}
                  onChange={(e) => setNewExcludeRegion(e.target.value)}
                  placeholder="输入要排除的区域"
                  className="text-sm flex-1"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && newExcludeRegion.trim()) {
                      if (!excludeRegions.includes(newExcludeRegion.trim())) {
                        updateParam('exclude_regions', [...excludeRegions, newExcludeRegion.trim()]);
                      }
                      setNewExcludeRegion('');
                    }
                  }}
                />
                <Button
                  size="sm"
                  onClick={() => {
                    if (newExcludeRegion.trim() && !excludeRegions.includes(newExcludeRegion.trim())) {
                      updateParam('exclude_regions', [...excludeRegions, newExcludeRegion.trim()]);
                      setNewExcludeRegion('');
                    }
                  }}
                  className="gap-2"
                >
                  <Plus className="h-3 w-3" />
                  添加
                </Button>
              </div>
            </div>

            {/* 已排除区域列表 */}
            {excludeRegions.length > 0 && (
              <div className="space-y-2">
                <Label className="text-xs font-medium">已排除区域</Label>
                <div className="flex flex-wrap gap-2 p-2 bg-gray-50 rounded border">
                  {excludeRegions.map((region: string, index: number) => (
                    <div
                      key={index}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-white border rounded text-xs"
                    >
                      <span>{region}</span>
                      <button
                        onClick={() => {
                          updateParam('exclude_regions', excludeRegions.filter((_: string, i: number) => i !== index));
                        }}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </TabsContent>

        {/* Tab 3: 标签设置 */}
        <TabsContent value="label" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">区域标签</h4>
            
            <div className="space-y-2">
              <Label htmlFor="label_column" className="text-sm">
                标签数据列 (label_column)
              </Label>
              <Select
                value={labelColumn || 'none'}
                onValueChange={(value) => {
                  const newValue = value === 'none' ? '' : value;
                  updateParam('label_column', newValue);
                  // 如果取消选择列，也清空 label_format
                  if (!newValue && labelFormat) {
                    updateParam('label_format', '');
                  }
                }}
              >
                <SelectTrigger id="label_column">
                  <SelectValue placeholder="选择数据列" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">不显示标签</SelectItem>
                  {subplot.data.columns && subplot.data.columns.map((col: string) => (
                    <SelectItem key={col} value={col}>
                      {col}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">
                选择用于标签的数据列。即使只显示区域名（{'{index}'}），也需要选择一个列
              </p>
            </div>

            {labelColumn && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="label_format" className="text-sm font-medium">
                    标签格式 (label_format)
                  </Label>
                  <Textarea
                    id="label_format"
                    value={labelFormat}
                    onChange={(e) => updateParam('label_format', e.target.value)}
                    placeholder="{index}"
                    className="min-h-[48px] text-sm resize-y font-mono"
                    rows={2}
                  />
                  <div className="text-xs text-gray-600 space-y-1 bg-blue-50 p-2 rounded border border-blue-200">
                    <p className="font-medium text-blue-800">💡 占位符说明：</p>
                    <ul className="space-y-0.5 ml-2">
                      <li><code className="bg-white px-1 rounded">{'{index}'}</code> - 区域名称（如"北京"、"上海"）</li>
                      <li><code className="bg-white px-1 rounded">{'{value}'}</code> - 所选标签列的数值</li>
                    </ul>
                    <p className="mt-1">示例：</p>
                    <ul className="space-y-0.5 ml-2">
                      <li><code className="bg-white px-1 rounded">{'{index}'}</code> → 只显示"北京"（区域名）</li>
                      <li><code className="bg-white px-1 rounded">{'{value}'}</code> → 只显示数值（如"36000"）</li>
                      <li><code className="bg-white px-1 rounded">{'{index}\\n{value}'}</code> → 两行：区域名 + 数值</li>
                    </ul>
                  </div>
                </div>

                <div className="space-y-2">
                  <NumberFormatEditor
                    value={labelValueFormat}
                    onChange={(format) => updateParam('label_value_format', format)}
                    label="数值格式化 (label_value_format)"
                    showHelp={true}
                  />
                  <p className="text-xs text-amber-700 bg-amber-50 p-2 rounded border border-amber-200">
                    💡 此格式仅影响标签中 {'{value}'} 占位符的显示
                  </p>
                </div>

            <div className="space-y-2 p-3 bg-gray-50 rounded border">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="use_abbr"
                  checked={useAbbr}
                  onCheckedChange={(checked) => updateParam('use_abbr', checked)}
                />
                <Label htmlFor="use_abbr" className="text-sm font-medium cursor-pointer">
                  使用区域简称 (use_abbr)
                </Label>
              </div>
              <p className="text-xs text-gray-600 pl-6">
                {useAbbr 
                  ? '✓ 已启用：{index} 将显示简称（"湖南省" → "湖南"，"琼中黎族苗族自治县" → "琼中县"）' 
                  : '○ 未启用：{index} 将显示完整区域名称'}
              </p>
            </div>

                <div className="space-y-2">
                  <LabelStyleEditor
                    value={labelStyle}
                    onChange={(style) => updateParam('label_style', style)}
                    label="标签样式"
                  />
                  <p className="text-xs text-gray-500">
                    控制标签的字体大小、颜色、样式和文本框外观
                  </p>
                </div>
              </>
            )}
          </div>
        </TabsContent>

        {/* Tab 4: 样式设置 */}
        <TabsContent value="style" className="space-y-4 mt-4">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-800">颜色映射</h4>
            
            {/* 颜色映射模式选择 */}
            <div className="space-y-2">
              <Label htmlFor="color_mapping_mode" className="text-sm">
                映射模式 (color_mapping_mode)
              </Label>
              <Select
                value={colorMappingMode}
                onValueChange={(value) => {
                  updateParam('color_mapping_mode', value);
                  // 如果切换到colormap模式，清空分类映射
                  if (value === 'colormap') {
                    updateParam('color_mapping', {});
                  }
                }}
              >
                <SelectTrigger id="color_mapping_mode">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="colormap">颜色渐变 (colormap)</SelectItem>
                  <SelectItem value="categorical">分类映射 (categorical)</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">
                {colorMappingMode === 'colormap' 
                  ? '使用颜色渐变方案，根据数值大小映射颜色'
                  : '使用手动指定的值-颜色映射对，匹配上的值显示对应颜色，否则不上色'}
              </p>
            </div>

            {/* Colormap 模式配置 */}
            {colorMappingMode === 'colormap' && (
              <>
                <div className="space-y-2 pl-2 border-l-2 border-gray-200">
                  <CmapPicker
                    value={cmap}
                    onChange={(value) => updateParam('cmap', value)}
                    label="颜色映射方案 (cmap)"
                    showPreview={true}
                    showReverse={true}
                  />
                  <p className="text-xs text-gray-500">
                    选择热力图的颜色渐变方案
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 pl-2 border-l-2 border-gray-200">
                  <div className="space-y-2">
                    <Label htmlFor="vmin" className="text-sm">
                      最小值 (vmin)
                    </Label>
                    <Input
                      id="vmin"
                      type="number"
                      value={vmin ?? ''}
                      onChange={(e) => updateParam('vmin', e.target.value ? parseFloat(e.target.value) : undefined)}
                      placeholder="自动"
                      className="text-sm"
                    />
                    <p className="text-xs text-gray-500">
                      颜色范围的最小值，留空则自动计算
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="vmax" className="text-sm">
                      最大值 (vmax)
                    </Label>
                    <Input
                      id="vmax"
                      type="number"
                      value={vmax ?? ''}
                      onChange={(e) => updateParam('vmax', e.target.value ? parseFloat(e.target.value) : undefined)}
                      placeholder="自动"
                      className="text-sm"
                    />
                    <p className="text-xs text-gray-500">
                      颜色范围的最大值，留空则自动计算
                    </p>
                  </div>
                </div>
              </>
            )}

            {/* Categorical 模式配置 */}
            {colorMappingMode === 'categorical' && (
              <div className="space-y-2 pl-2 border-l-2 border-gray-200">
                <div className="flex items-center justify-between">
                  <Label className="text-xs">值-颜色映射</Label>
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-6 px-2 text-xs"
                    onClick={() => {
                      const newKey = `值${Object.keys(colorMapping).length + 1}`;
                      // 简化格式：直接使用颜色字符串
                      updateParam('color_mapping', { ...colorMapping, [newKey]: '#000000' });
                    }}
                  >
                    <Plus className="h-3 w-3 mr-1" />
                    添加
                  </Button>
                </div>
                
                {colorMappingOrder.map((orderItem) => {
                  const value = orderItem.key;
                  const mapping = colorMapping[value];
                  if (mapping === undefined) return null; // 如果映射已被删除，跳过
                  
                  // 向后兼容：如果 mapping 是字符串，直接使用；如果是对象，提取 color
                  const color = typeof mapping === 'string' ? mapping : (mapping as any)?.color || '#000000';
                  
                  return (
                    <div key={orderItem.id} className="flex items-center gap-2">
                      <Input
                        value={value}
                        onChange={(e) => {
                          const newMap = { ...colorMapping };
                          const newValue = e.target.value;
                          // 如果新值和旧值不同，更新键名
                          if (newValue !== value) {
                            const oldMapping = newMap[value];
                            delete newMap[value];
                            // 即使新值为空，也保留映射项（使用空字符串作为键）
                            newMap[newValue] = oldMapping;
                            // 更新顺序数组中的键
                            setColorMappingOrder(prev => 
                              prev.map(item => item.id === orderItem.id ? { ...item, key: newValue } : item)
                            );
                          }
                          updateParam('color_mapping', newMap);
                        }}
                        placeholder="值"
                        className="h-8 text-sm flex-1"
                      />
                      <ColorPicker
                        value={color}
                        onChange={(newColor) => {
                          // 简化格式：直接使用颜色字符串，不再使用对象格式
                          updateParam('color_mapping', { 
                            ...colorMapping, 
                            [value]: newColor 
                          });
                        }}
                      />
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-8 w-8 p-0"
                        onClick={() => {
                          const newMap = { ...colorMapping };
                          delete newMap[value];
                          // 从顺序数组中移除该项
                          setColorMappingOrder(prev => prev.filter(item => item.id !== orderItem.id));
                          updateParam('color_mapping', newMap);
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  );
                })}
                
                {Object.keys(colorMapping || {}).length === 0 && (
                  <p className="text-xs text-gray-400 italic">
                    暂无映射规则，点击"添加"按钮创建值-颜色映射对
                  </p>
                )}
                
                <p className="text-xs text-gray-500 mt-2">
                  数值列的值如果匹配上映射中的键，则显示对应颜色；否则该区域不上色（透明）
                </p>
              </div>
            )}

            {/* 颜色条控件：仅在 colormap 模式下显示 */}
            {colorMappingMode === 'colormap' && (
              <>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="show_colorbar"
                    checked={showColorbar}
                    onCheckedChange={(checked) => updateParam('show_colorbar', checked)}
                  />
                  <Label htmlFor="show_colorbar" className="text-sm cursor-pointer">
                    显示颜色条 (show_colorbar)
                  </Label>
                </div>
                <p className="text-xs text-gray-500 pl-6">
                  在地图旁显示颜色图例条
                </p>
              </>
            )}
            
            {/* 分类映射模式下提示 */}
            {colorMappingMode === 'categorical' && (
              <p className="text-xs text-gray-400 italic pl-6">
                分类映射模式下不显示颜色条
              </p>
            )}
          </div>

          {/* 纹理映射配置 */}
          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">纹理映射</h4>
            <div className="space-y-2 pl-2 border-l-2 border-gray-200">
              <div className="flex items-center justify-between">
                <Label className="text-xs">值-纹理映射</Label>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-6 px-2 text-xs"
                  onClick={() => {
                    const newKey = `值${Object.keys(hatchMapping).length + 1}`;
                    updateParam('hatch_mapping', { 
                      ...hatchMapping, 
                      [newKey]: { hatch: '/', density: 5, color: '#000000' } 
                    });
                  }}
                >
                  <Plus className="h-3 w-3 mr-1" />
                  添加
                </Button>
              </div>
              
              {hatchMappingOrder.map((orderItem) => {
                const value = orderItem.key;
                const mapping = hatchMapping[value];
                if (mapping === undefined) return null; // 如果映射已被删除，跳过
                
                const hatch = (mapping as any)?.hatch || '/';
                const density = (mapping as any)?.density ?? 5;
                const color = (mapping as any)?.color || '#000000';
                
                return (
                  <div key={orderItem.id} className="flex items-center gap-2 flex-wrap">
                    <Input
                      value={value}
                      onChange={(e) => {
                        const newMap = { ...hatchMapping };
                        const newValue = e.target.value;
                        if (newValue !== value) {
                          const oldMapping = newMap[value];
                          delete newMap[value];
                          // 即使新值为空，也保留映射项（使用空字符串作为键）
                          newMap[newValue] = oldMapping;
                          // 更新顺序数组中的键
                          setHatchMappingOrder(prev => 
                            prev.map(item => item.id === orderItem.id ? { ...item, key: newValue } : item)
                          );
                        }
                        updateParam('hatch_mapping', newMap);
                      }}
                      placeholder="值"
                      className="h-8 text-sm flex-1 min-w-[100px]"
                    />
                    <Select
                      value={hatch}
                      onValueChange={(newHatch) => {
                        updateParam('hatch_mapping', { 
                          ...hatchMapping, 
                          [value]: { ...(mapping as any), hatch: newHatch } 
                        });
                      }}
                    >
                      <SelectTrigger className="h-8 w-20 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="/">/</SelectItem>
                        <SelectItem value="\\">\</SelectItem>
                        <SelectItem value="|">|</SelectItem>
                        <SelectItem value="-">-</SelectItem>
                        <SelectItem value="+">+</SelectItem>
                        <SelectItem value="x">x</SelectItem>
                        <SelectItem value="o">o</SelectItem>
                        <SelectItem value="O">O</SelectItem>
                        <SelectItem value=".">.</SelectItem>
                        <SelectItem value="*">*</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="flex items-center gap-1">
                      <Label className="text-xs whitespace-nowrap">密度:</Label>
                      <Input
                        type="number"
                        value={density}
                        onChange={(e) => {
                          const newDensity = parseInt(e.target.value) || 1;
                          updateParam('hatch_mapping', { 
                            ...hatchMapping, 
                            [value]: { ...(mapping as any), density: newDensity } 
                          });
                        }}
                        min={1}
                        max={20}
                        className="h-8 w-16 text-xs"
                      />
                    </div>
                    <ColorPicker
                      value={color}
                      onChange={(newColor) => {
                        updateParam('hatch_mapping', { 
                          ...hatchMapping, 
                          [value]: { ...(mapping as any), color: newColor } 
                        });
                      }}
                    />
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-8 w-8 p-0 flex-shrink-0"
                      onClick={() => {
                        const newMap = { ...hatchMapping };
                        delete newMap[value];
                        // 从顺序数组中移除该项
                        setHatchMappingOrder(prev => prev.filter(item => item.id !== orderItem.id));
                        updateParam('hatch_mapping', newMap);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                );
              })}
              
              {Object.keys(hatchMapping || {}).length === 0 && (
                <p className="text-xs text-gray-400 italic">
                  暂无映射规则，点击"添加"按钮创建值-纹理映射对
                </p>
              )}
              
              <p className="text-xs text-gray-500 mt-2">
                数值列的值如果匹配上映射中的键，则显示对应的纹理、密度和颜色
              </p>
            </div>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">边界样式</h4>
            
            <div className="space-y-2">
              <Label htmlFor="edgecolor" className="text-sm">
                边界颜色 (edgecolor)
              </Label>
              <ColorPicker
                value={edgecolor}
                onChange={(color) => updateParam('edgecolor', color)}
              />
              <p className="text-xs text-gray-500">
                行政区划边界的颜色
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="linewidth" className="text-sm">
                  基础边界线宽 (linewidth)
                </Label>
                <span className="text-xs text-gray-500">{linewidth.toFixed(1)}</span>
              </div>
              <Slider
                id="linewidth"
                min={0.1}
                max={3}
                step={0.1}
                value={[linewidth]}
                onValueChange={(value) => updateParam('linewidth', value[0])}
                className="w-full"
              />
              <p className="text-xs text-gray-500">
                控制区县等基础边界线条的粗细（0.1-3.0）
              </p>
            </div>

            <div className="space-y-3 pt-2 pl-3 border-l-2 border-gray-200">
              <p className="text-xs font-medium text-gray-700">分层级边界加粗</p>
              <p className="text-xs text-gray-500">留空则使用基础线宽</p>
              
              {/* 国界线宽 */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="national_border_width" className="text-xs">
                    国界线宽
                  </Label>
                  {nationalBorderWidth !== null && (
                    <span className="text-xs text-gray-500">{nationalBorderWidth.toFixed(1)}</span>
                  )}
                </div>
                <div className="flex gap-2 items-center">
                  <Slider
                    id="national_border_width"
                    min={0.1}
                    max={5}
                    step={0.1}
                    value={[nationalBorderWidth ?? linewidth]}
                    onValueChange={(value) => updateParam('national_border_width', value[0])}
                    className="flex-1"
                    disabled={nationalBorderWidth === null}
                  />
                  <Checkbox
                    checked={nationalBorderWidth !== null}
                    onCheckedChange={(checked) => {
                      updateParam('national_border_width', checked ? linewidth * 2 : null);
                    }}
                  />
                </div>
                <p className="text-xs text-gray-400">
                  全国地图外边界（仅全国范围时显示）
                </p>
              </div>

              {/* 省界线宽 */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="province_border_width" className="text-xs">
                    省界线宽
                  </Label>
                  {provinceBorderWidth !== null && (
                    <span className="text-xs text-gray-500">{provinceBorderWidth.toFixed(1)}</span>
                  )}
                </div>
                <div className="flex gap-2 items-center">
                  <Slider
                    id="province_border_width"
                    min={0.1}
                    max={5}
                    step={0.1}
                    value={[provinceBorderWidth ?? linewidth]}
                    onValueChange={(value) => updateParam('province_border_width', value[0])}
                    className="flex-1"
                    disabled={provinceBorderWidth === null}
                  />
                  <Checkbox
                    checked={provinceBorderWidth !== null}
                    onCheckedChange={(checked) => {
                      updateParam('province_border_width', checked ? linewidth * 2 : null);
                    }}
                  />
                </div>
                <p className="text-xs text-gray-400">
                  省级行政区边界
                </p>
              </div>

              {/* 市界线宽 */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="city_border_width" className="text-xs">
                    地级市边界线宽
                  </Label>
                  {cityBorderWidth !== null && (
                    <span className="text-xs text-gray-500">{cityBorderWidth.toFixed(1)}</span>
                  )}
                </div>
                <div className="flex gap-2 items-center">
                  <Slider
                    id="city_border_width"
                    min={0.1}
                    max={5}
                    step={0.1}
                    value={[cityBorderWidth ?? linewidth]}
                    onValueChange={(value) => updateParam('city_border_width', value[0])}
                    className="flex-1"
                    disabled={cityBorderWidth === null}
                  />
                  <Checkbox
                    checked={cityBorderWidth !== null}
                    onCheckedChange={(checked) => {
                      updateParam('city_border_width', checked ? linewidth * 2 : null);
                    }}
                  />
                </div>
                <p className="text-xs text-gray-400">
                  地级市行政区边界（地级市层级或区县层级时显示）
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-3 pt-3 border-t">
            <h4 className="text-sm font-semibold text-gray-800">高级选项</h4>
            
            {level === 'county' && scope === 'cities' && (
              <>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="dissolve_urban"
                    checked={dissolveUrban}
                    onCheckedChange={(checked) => updateParam('dissolve_urban', checked)}
                  />
                  <Label htmlFor="dissolve_urban" className="text-sm cursor-pointer">
                    合并市区轮廓 (dissolve_urban)
                  </Label>
                </div>
                <p className="text-xs text-gray-500 pl-6">
                  将市辖区合并为一个整体显示（仅在区县层级且显示指定城市时有效）
                </p>
              </>
            )}

            {(level !== 'county' || scope !== 'cities') && (
              <div className="text-xs text-gray-400 italic">
                当前配置下无可用高级选项
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* 配置预览 */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <MapIcon className="h-4 w-4 text-blue-600 mt-0.5" />
          <div className="flex-1 text-xs">
            <p className="font-medium text-blue-900 mb-1">当前配置</p>
            <p className="text-blue-700">
              {level === 'province' && '省级'}
              {level === 'prefecture' && '地级市'}
              {level === 'county' && '区县'}
              数据 · {' '}
              {scope === 'national' && '全国范围'}
              {scope === 'provinces' && `${regions.length}个省份`}
              {scope === 'cities' && `${regions.length}个城市`}
              {scope === 'counties' && `${regions.length}个区县`}
              {labelColumn && ` · 显示${useAbbr ? '简称' : '全称'}标签`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
