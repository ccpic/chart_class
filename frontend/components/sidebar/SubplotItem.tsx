'use client';

import Link from 'next/link';
import {
  BarChart3,
  LineChart,
  PieChart,
  AreaChart,
  ScatterChart,
  Droplets,
  Circle,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

import {
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuBadge,
} from '@/components/ui/sidebar';

import { SubplotConfig } from '@/types/canvas';

interface Props {
  subplot: SubplotConfig;
  isActive: boolean;
}

/**
 * 根据图表类型返回对应图标
 */
function getChartIcon(type: string) {
  const iconClass = 'size-4';
  switch (type) {
    case 'bar':
      return <BarChart3 className={iconClass} />;
    case 'line':
      return <LineChart className={iconClass} />;
    case 'pie':
      return <PieChart className={iconClass} />;
    case 'area':
      return <AreaChart className={iconClass} />;
    case 'scatter':
      return <ScatterChart className={iconClass} />;
    case 'bubble':
      return <Droplets className={iconClass} />;
    default:
      return <Circle className={iconClass} />;
  }
}

/**
 * 检查子图数据是否完整
 */
function isDataComplete(subplot: SubplotConfig): boolean {
  return (
    subplot.data.columns &&
    subplot.data.columns.length > 0 &&
    subplot.data.data &&
    subplot.data.data.length > 0
  );
}

/**
 * 子图列表项组件
 * 显示图表类型图标、位置、数据状态
 */
export default function SubplotItem({ subplot, isActive }: Props) {
  const hasData = isDataComplete(subplot);

  return (
    <SidebarMenuItem>
      <SidebarMenuButton asChild isActive={isActive}>
        <Link href={`/subplot/${subplot.subplotId}`}>
          {getChartIcon(subplot.chartType)}
          <span>子图 {subplot.axIndex + 1}</span>

          {/* 状态徽章 */}
          <SidebarMenuBadge>
            {hasData ? (
              <CheckCircle2 className="size-3 text-green-600" />
            ) : (
              <AlertCircle className="size-3 text-yellow-600" />
            )}
          </SidebarMenuBadge>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
