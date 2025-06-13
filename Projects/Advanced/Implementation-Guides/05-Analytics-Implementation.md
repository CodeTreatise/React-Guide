# 📊 Real-time Analytics Dashboard - Implementation Guide

> **Project**: Interactive Data Visualization Platform  
> **Difficulty**: Advanced  
> **Duration**: 4-6 weeks  
> **Focus**: Data visualization, real-time updates, performance optimization

## 🎯 Project Overview

Build a comprehensive analytics dashboard with real-time data visualization, interactive charts, and performance monitoring. This project emphasizes data processing, visualization libraries, and real-time communication.

## 🚀 Quick Start (30 minutes)

```bash
# Create project with Vite for better performance
npm create vite@latest analytics-dashboard -- --template react-ts
cd analytics-dashboard

# Install visualization and data processing libraries
npm install recharts d3 @visx/visx @tanstack/react-table
npm install framer-motion react-spring @react-spring/web

# Install real-time and data fetching
npm install socket.io-client @tanstack/react-query
npm install axios date-fns lodash @types/lodash

# Install UI and styling
npm install @headlessui/react @heroicons/react
npm install tailwindcss autoprefixer postcss @tailwindcss/forms
npm install clsx tailwind-merge

# Install development tools
npm install --save-dev @types/d3 eslint-plugin-react-hooks
npm install --save-dev vite-plugin-eslint @vitejs/plugin-react

# Setup Tailwind CSS
npx tailwindcss init -p

# Start development server
npm run dev
```

## 🏗️ Architecture Overview

### Data Flow Architecture
```
📊 Data Sources → 🔄 Real-time Processors → 📈 Visualization Components
     ↓                     ↓                        ↓
📡 APIs/WebSocket  →  🏪 State Management  →  🎨 Interactive Charts
```

### Tech Stack Decision Matrix

| Tool | Purpose | Why Chosen | Alternative |
|------|---------|------------|-------------|
| **Recharts** | Primary Charting | React-native, simple API | Chart.js, Victory |
| **D3** | Complex Visualizations | Maximum flexibility, animations | Observable Plot |
| **VISX** | Advanced Graphics | React + D3 integration | Nivo |
| **React Table** | Data Tables | Powerful, headless | AG Grid |
| **Socket.io** | Real-time Data | Reliable WebSocket handling | Native WebSocket |
| **Framer Motion** | Animations | Smooth, performant animations | React Spring |
| **TanStack Query** | Data Management | Caching, background updates | SWR |

### Folder Structure
```
src/
├── components/
│   ├── charts/
│   │   ├── LineChart/
│   │   ├── BarChart/
│   │   ├── PieChart/
│   │   └── HeatMap/
│   ├── dashboard/
│   │   ├── DashboardGrid/
│   │   ├── MetricCard/
│   │   └── FilterPanel/
│   ├── tables/
│   │   ├── DataTable/
│   │   └── VirtualizedTable/
│   └── ui/
├── hooks/
│   ├── useRealTimeData.ts
│   ├── useChartData.ts
│   └── useWebSocket.ts
├── services/
│   ├── analyticsAPI.ts
│   ├── websocket.ts
│   └── dataProcessing.ts
├── utils/
│   ├── chartHelpers.ts
│   ├── dataTransforms.ts
│   └── formatters.ts
├── types/
│   ├── analytics.ts
│   └── charts.ts
└── stores/
    ├── dashboardStore.ts
    └── filtersStore.ts
```

## 📋 Implementation Roadmap

### Phase 1: Foundation & Core Charts (Week 1)
- [ ] Project setup with Vite and TypeScript
- [ ] Basic dashboard layout and routing
- [ ] Core chart components (Line, Bar, Pie)
- [ ] Mock data service and API integration
- [ ] Responsive design implementation

### Phase 2: Advanced Visualizations (Week 2)
- [ ] Heat maps and scatter plots
- [ ] Interactive charts with zoom/pan
- [ ] Custom D3 visualizations
- [ ] Chart composition and layouts
- [ ] Animation and transition effects

### Phase 3: Real-time Features (Week 3)
- [ ] WebSocket integration for live data
- [ ] Real-time chart updates
- [ ] Performance optimization for streaming
- [ ] Data aggregation and processing
- [ ] Alert system for threshold monitoring

### Phase 4: Dashboard Features (Week 4)
- [ ] Drag-and-drop dashboard builder
- [ ] Advanced filtering and search
- [ ] Data export functionality
- [ ] Custom date range selection
- [ ] Dashboard sharing and persistence

### Phase 5: Performance & Production (Weeks 5-6)
- [ ] Virtual scrolling for large datasets
- [ ] Chart performance optimization
- [ ] Memory leak prevention
- [ ] Error boundary implementation
- [ ] Deployment and monitoring

## 💻 Core Implementation Examples

### Real-time Data Hook
```typescript
// src/hooks/useRealTimeData.ts
import { useState, useEffect, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { analyticsAPI } from '../services/analyticsAPI';
import { useWebSocket } from './useWebSocket';

interface UseRealTimeDataOptions {
  endpoint: string;
  refreshInterval?: number;
  enableRealTime?: boolean;
  aggregation?: 'sum' | 'avg' | 'count';
  timeWindow?: number; // minutes
}

export const useRealTimeData = <T>({
  endpoint,
  refreshInterval = 30000,
  enableRealTime = true,
  aggregation = 'sum',
  timeWindow = 5
}: UseRealTimeDataOptions) => {
  const queryClient = useQueryClient();
  const [liveData, setLiveData] = useState<T[]>([]);
  const bufferRef = useRef<T[]>([]);
  
  // WebSocket connection for real-time updates
  const { socket, isConnected } = useWebSocket();
  
  // Base query for initial data
  const query = useQuery({
    queryKey: ['analytics', endpoint],
    queryFn: () => analyticsAPI.getData<T>(endpoint),
    refetchInterval: enableRealTime ? refreshInterval : false,
    staleTime: 5000,
  });

  // Handle real-time updates
  useEffect(() => {
    if (!socket || !enableRealTime) return;

    const handleUpdate = (newData: T) => {
      // Add to buffer for batch processing
      bufferRef.current.push(newData);
      
      // Process buffer every second
      const interval = setInterval(() => {
        if (bufferRef.current.length > 0) {
          const updates = [...bufferRef.current];
          bufferRef.current = [];
          
          // Apply aggregation logic
          const processedData = aggregateData(updates, aggregation, timeWindow);
          
          setLiveData(prev => {
            const updated = [...prev, ...processedData];
            // Keep only last N minutes of data
            const cutoff = Date.now() - (timeWindow * 60 * 1000);
            return updated.filter(item => 
              new Date(item.timestamp).getTime() > cutoff
            );
          });
          
          // Update React Query cache
          queryClient.setQueryData(['analytics', endpoint], (old: T[]) => {
            return old ? [...old, ...processedData] : processedData;
          });
        }
      }, 1000);

      return () => clearInterval(interval);
    };

    socket.on(`${endpoint}_update`, handleUpdate);
    
    return () => {
      socket.off(`${endpoint}_update`, handleUpdate);
    };
  }, [socket, enableRealTime, endpoint, aggregation, timeWindow]);

  const aggregateData = (data: T[], type: string, window: number): T[] => {
    // Group data by time windows
    const windowSize = window * 60 * 1000; // Convert to milliseconds
    const groups = new Map<number, T[]>();
    
    data.forEach(item => {
      const windowStart = Math.floor(
        new Date(item.timestamp).getTime() / windowSize
      ) * windowSize;
      
      if (!groups.has(windowStart)) {
        groups.set(windowStart, []);
      }
      groups.get(windowStart)!.push(item);
    });
    
    // Apply aggregation
    return Array.from(groups.entries()).map(([windowStart, items]) => {
      switch (type) {
        case 'sum':
          return {
            ...items[0],
            value: items.reduce((sum, item) => sum + item.value, 0),
            timestamp: new Date(windowStart).toISOString()
          };
        case 'avg':
          return {
            ...items[0],
            value: items.reduce((sum, item) => sum + item.value, 0) / items.length,
            timestamp: new Date(windowStart).toISOString()
          };
        case 'count':
          return {
            ...items[0],
            value: items.length,
            timestamp: new Date(windowStart).toISOString()
          };
        default:
          return items[0];
      }
    });
  };

  return {
    data: query.data || [],
    liveData,
    isLoading: query.isLoading,
    error: query.error,
    isConnected,
    refetch: query.refetch
  };
};
```

### Interactive Line Chart Component
```typescript
// src/components/charts/InteractiveLineChart.tsx
import React, { useState, useMemo, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Brush,
  ReferenceLine
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { format, parseISO } from 'date-fns';

interface DataPoint {
  timestamp: string;
  value: number;
  category?: string;
  [key: string]: any;
}

interface InteractiveLineChartProps {
  data: DataPoint[];
  height?: number;
  showBrush?: boolean;
  showAnimation?: boolean;
  thresholds?: { value: number; label: string; color: string }[];
  onDataPointClick?: (point: DataPoint) => void;
  colorScheme?: string[];
}

export const InteractiveLineChart: React.FC<InteractiveLineChartProps> = ({
  data,
  height = 400,
  showBrush = true,
  showAnimation = true,
  thresholds = [],
  onDataPointClick,
  colorScheme = ['#8884d8', '#82ca9d', '#ffc658']
}) => {
  const [selectedRange, setSelectedRange] = useState<[number, number] | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<DataPoint | null>(null);
  const [isZoomed, setIsZoomed] = useState(false);

  // Process and transform data
  const processedData = useMemo(() => {
    return data.map((point, index) => ({
      ...point,
      index,
      formattedTime: format(parseISO(point.timestamp), 'MMM dd, HH:mm'),
      shortTime: format(parseISO(point.timestamp), 'HH:mm')
    }));
  }, [data]);

  // Apply zoom filter if range is selected
  const displayData = useMemo(() => {
    if (!selectedRange) return processedData;
    
    const [startIndex, endIndex] = selectedRange;
    return processedData.slice(startIndex, endIndex + 1);
  }, [processedData, selectedRange]);

  // Calculate statistics
  const stats = useMemo(() => {
    if (displayData.length === 0) return null;
    
    const values = displayData.map(d => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    
    return {
      min: min.toFixed(2),
      max: max.toFixed(2),
      avg: avg.toFixed(2),
      count: displayData.length
    };
  }, [displayData]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    setHoveredPoint(data);

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg"
      >
        <p className="font-medium text-gray-900">{data.formattedTime}</p>
        <p className="text-lg font-bold text-blue-600">
          {payload[0].value.toLocaleString()}
        </p>
        {data.category && (
          <p className="text-sm text-gray-600">Category: {data.category}</p>
        )}
      </motion.div>
    );
  };

  // Handle brush change (zoom)
  const handleBrushChange = useCallback((range: any) => {
    if (range && range.startIndex !== undefined && range.endIndex !== undefined) {
      setSelectedRange([range.startIndex, range.endIndex]);
      setIsZoomed(true);
    }
  }, []);

  // Reset zoom
  const resetZoom = useCallback(() => {
    setSelectedRange(null);
    setIsZoomed(false);
  }, []);

  // Handle point click
  const handlePointClick = useCallback((data: any) => {
    if (onDataPointClick) {
      onDataPointClick(data.payload);
    }
  }, [onDataPointClick]);

  return (
    <div className="w-full">
      {/* Chart Header with Stats */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex space-x-4">
          {stats && (
            <>
              <div className="text-sm">
                <span className="text-gray-500">Min:</span>
                <span className="ml-1 font-medium">{stats.min}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-500">Max:</span>
                <span className="ml-1 font-medium">{stats.max}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-500">Avg:</span>
                <span className="ml-1 font-medium">{stats.avg}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-500">Points:</span>
                <span className="ml-1 font-medium">{stats.count}</span>
              </div>
            </>
          )}
        </div>
        
        {isZoomed && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={resetZoom}
            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            Reset Zoom
          </motion.button>
        )}
      </div>

      {/* Main Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={displayData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          
          <XAxis
            dataKey="shortTime"
            tick={{ fontSize: 12 }}
            tickLine={{ stroke: '#ccc' }}
          />
          
          <YAxis
            tick={{ fontSize: 12 }}
            tickLine={{ stroke: '#ccc' }}
            tickFormatter={(value) => value.toLocaleString()}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          {/* Threshold Reference Lines */}
          {thresholds.map((threshold, index) => (
            <ReferenceLine
              key={index}
              y={threshold.value}
              stroke={threshold.color}
              strokeDasharray="5 5"
              label={{
                value: threshold.label,
                position: 'topRight',
                style: { fontSize: 12, fill: threshold.color }
              }}
            />
          ))}
          
          <Line
            type="monotone"
            dataKey="value"
            stroke={colorScheme[0]}
            strokeWidth={2}
            dot={{ r: 3, strokeWidth: 0 }}
            activeDot={{ 
              r: 6, 
              stroke: colorScheme[0], 
              strokeWidth: 2,
              onClick: handlePointClick
            }}
            {...(showAnimation && {
              animationDuration: 1000,
              animationBegin: 0
            })}
          />
          
          {/* Brush for zooming */}
          {showBrush && (
            <Brush
              dataKey="shortTime"
              height={30}
              stroke={colorScheme[0]}
              onChange={handleBrushChange}
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      {/* Hover Details */}
      <AnimatePresence>
        {hoveredPoint && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="mt-4 p-3 bg-gray-50 rounded border-l-4 border-blue-500"
          >
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Timestamp:</span>
                <p className="font-medium">{hoveredPoint.formattedTime}</p>
              </div>
              <div>
                <span className="text-gray-500">Value:</span>
                <p className="font-medium text-lg">{hoveredPoint.value.toLocaleString()}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
```

### Dashboard Grid Component
```typescript
// src/components/dashboard/DashboardGrid.tsx
import React, { useState, useCallback } from 'react';
import { motion, Reorder } from 'framer-motion';
import { PlusIcon, XMarkIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import { InteractiveLineChart } from '../charts/InteractiveLineChart';
import { BarChart } from '../charts/BarChart';
import { PieChart } from '../charts/PieChart';
import { MetricCard } from './MetricCard';

interface DashboardWidget {
  id: string;
  type: 'line-chart' | 'bar-chart' | 'pie-chart' | 'metric' | 'table';
  title: string;
  data: any[];
  config: {
    size: 'small' | 'medium' | 'large';
    refreshInterval?: number;
    [key: string]: any;
  };
}

interface DashboardGridProps {
  widgets: DashboardWidget[];
  onWidgetUpdate: (widgets: DashboardWidget[]) => void;
  onAddWidget: () => void;
  editable?: boolean;
}

export const DashboardGrid: React.FC<DashboardGridProps> = ({
  widgets,
  onWidgetUpdate,
  onAddWidget,
  editable = false
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);

  // Handle widget reordering
  const handleReorder = useCallback((newOrder: DashboardWidget[]) => {
    onWidgetUpdate(newOrder);
  }, [onWidgetUpdate]);

  // Remove widget
  const removeWidget = useCallback((widgetId: string) => {
    const updatedWidgets = widgets.filter(w => w.id !== widgetId);
    onWidgetUpdate(updatedWidgets);
  }, [widgets, onWidgetUpdate]);

  // Get grid size class based on widget size
  const getSizeClass = (size: string) => {
    switch (size) {
      case 'small': return 'col-span-1 row-span-1';
      case 'medium': return 'col-span-2 row-span-1';
      case 'large': return 'col-span-2 row-span-2';
      default: return 'col-span-1 row-span-1';
    }
  };

  // Render widget content based on type
  const renderWidgetContent = (widget: DashboardWidget) => {
    switch (widget.type) {
      case 'line-chart':
        return (
          <InteractiveLineChart
            data={widget.data}
            height={widget.config.size === 'large' ? 300 : 200}
            showBrush={widget.config.size === 'large'}
            {...widget.config}
          />
        );
      
      case 'bar-chart':
        return (
          <BarChart
            data={widget.data}
            height={widget.config.size === 'large' ? 300 : 200}
            {...widget.config}
          />
        );
      
      case 'pie-chart':
        return (
          <PieChart
            data={widget.data}
            height={widget.config.size === 'large' ? 300 : 200}
            {...widget.config}
          />
        );
      
      case 'metric':
        return (
          <MetricCard
            title={widget.title}
            value={widget.data[0]?.value || 0}
            change={widget.data[0]?.change}
            trend={widget.data[0]?.trend}
            {...widget.config}
          />
        );
      
      default:
        return <div>Unsupported widget type</div>;
    }
  };

  return (
    <div className="w-full">
      {/* Dashboard Controls */}
      {editable && (
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <div className="flex space-x-3">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className={`px-4 py-2 rounded-md transition-colors ${
                isEditing
                  ? 'bg-red-100 text-red-700 hover:bg-red-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Cog6ToothIcon className="w-4 h-4 inline mr-2" />
              {isEditing ? 'Exit Edit' : 'Edit Mode'}
            </button>
            <button
              onClick={onAddWidget}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <PlusIcon className="w-4 h-4 inline mr-2" />
              Add Widget
            </button>
          </div>
        </div>
      )}

      {/* Dashboard Grid */}
      <Reorder.Group
        axis="y"
        values={widgets}
        onReorder={handleReorder}
        className="grid grid-cols-4 gap-6 auto-rows-min"
      >
        {widgets.map((widget) => (
          <Reorder.Item
            key={widget.id}
            value={widget}
            className={`${getSizeClass(widget.config.size)} ${
              isEditing ? 'cursor-grab active:cursor-grabbing' : ''
            }`}
          >
            <motion.div
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className={`bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow ${
                selectedWidget === widget.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => setSelectedWidget(widget.id)}
            >
              {/* Widget Header */}
              <div className="flex justify-between items-center p-4 border-b">
                <h3 className="font-semibold text-gray-900">{widget.title}</h3>
                {isEditing && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeWidget(widget.id);
                    }}
                    className="text-red-500 hover:text-red-700 transition-colors"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Widget Content */}
              <div className="p-4">
                {renderWidgetContent(widget)}
              </div>

              {/* Real-time Indicator */}
              {widget.config.refreshInterval && (
                <div className="absolute top-2 right-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                </div>
              )}
            </motion.div>
          </Reorder.Item>
        ))}
      </Reorder.Group>

      {/* Empty State */}
      {widgets.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <PlusIcon className="w-12 h-12 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No widgets yet</h3>
          <p className="text-gray-600 mb-4">Get started by adding your first widget</p>
          <button
            onClick={onAddWidget}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Add Widget
          </button>
        </motion.div>
      )}
    </div>
  );
};
```

### Performance-Optimized Data Table
```typescript
// src/components/tables/VirtualizedTable.tsx
import React, { useMemo, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  ColumnDef,
  flexRender,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline';

interface VirtualizedTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  height?: number;
  onRowClick?: (row: T) => void;
  globalFilter?: string;
  onGlobalFilterChange?: (value: string) => void;
}

export const VirtualizedTable = <T extends Record<string, any>>({
  data,
  columns,
  height = 400,
  onRowClick,
  globalFilter = '',
  onGlobalFilterChange
}: VirtualizedTableProps<T>) => {
  const [sorting, setSorting] = useState([]);

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  // Get the visible rows
  const { rows } = table.getRowModel();

  // Create a parent ref for the virtualizer
  const parentRef = React.useRef<HTMLDivElement>(null);

  // Create the virtualizer
  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Row height
    overscan: 10,
  });

  // Get virtual items
  const virtualItems = virtualizer.getVirtualItems();

  return (
    <div className="w-full">
      {/* Global Filter */}
      {onGlobalFilterChange && (
        <div className="mb-4">
          <input
            type="text"
            value={globalFilter}
            onChange={(e) => onGlobalFilterChange(e.target.value)}
            placeholder="Search all columns..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      {/* Table Container */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        {/* Table Header */}
        <div className="bg-gray-50 border-b border-gray-200">
          {table.getHeaderGroups().map(headerGroup => (
            <div key={headerGroup.id} className="flex">
              {headerGroup.headers.map(header => (
                <div
                  key={header.id}
                  className="flex-1 min-w-0 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  style={{ width: header.getSize() }}
                >
                  {header.isPlaceholder ? null : (
                    <div
                      className={`flex items-center space-x-1 ${
                        header.column.getCanSort() ? 'cursor-pointer select-none' : ''
                      }`}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      <span>
                        {flexRender(header.column.columnDef.header, header.getContext())}
                      </span>
                      {header.column.getCanSort() && (
                        <span className="flex flex-col">
                          <ChevronUpIcon
                            className={`w-3 h-3 ${
                              header.column.getIsSorted() === 'asc'
                                ? 'text-gray-900'
                                : 'text-gray-400'
                            }`}
                          />
                          <ChevronDownIcon
                            className={`w-3 h-3 -mt-1 ${
                              header.column.getIsSorted() === 'desc'
                                ? 'text-gray-900'
                                : 'text-gray-400'
                            }`}
                          />
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* Virtual Table Body */}
        <div
          ref={parentRef}
          className="overflow-auto"
          style={{ height: `${height}px` }}
        >
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            {virtualItems.map(virtualRow => {
              const row = rows[virtualRow.index];
              return (
                <div
                  key={row.id}
                  className={`absolute top-0 left-0 w-full flex hover:bg-gray-50 ${
                    onRowClick ? 'cursor-pointer' : ''
                  }`}
                  style={{
                    height: `${virtualRow.size}px`,
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                  onClick={() => onRowClick?.(row.original)}
                >
                  {row.getVisibleCells().map(cell => (
                    <div
                      key={cell.id}
                      className="flex-1 min-w-0 px-4 py-3 text-sm text-gray-900 border-b border-gray-200"
                      style={{ width: cell.column.getSize() }}
                    >
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        </div>

        {/* Table Footer with Stats */}
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
          <div className="flex justify-between items-center text-sm text-gray-700">
            <span>
              Showing {virtualItems.length} of {rows.length} rows
              {globalFilter && ` (filtered from ${data.length} total)`}
            </span>
            <span>
              {data.length.toLocaleString()} total records
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Usage example with column definitions
export const useAnalyticsTableColumns = (): ColumnDef<any>[] => {
  return useMemo(() => [
    {
      accessorKey: 'timestamp',
      header: 'Time',
      cell: ({ getValue }) => {
        const date = new Date(getValue() as string);
        return format(date, 'MMM dd, HH:mm:ss');
      },
      size: 150,
    },
    {
      accessorKey: 'event',
      header: 'Event',
      size: 200,
    },
    {
      accessorKey: 'user',
      header: 'User',
      cell: ({ getValue }) => {
        const user = getValue() as { name: string; email: string };
        return (
          <div>
            <div className="font-medium">{user.name}</div>
            <div className="text-gray-500 text-xs">{user.email}</div>
          </div>
        );
      },
      size: 200,
    },
    {
      accessorKey: 'value',
      header: 'Value',
      cell: ({ getValue }) => {
        const value = getValue() as number;
        return (
          <span className="font-mono">
            {value.toLocaleString()}
          </span>
        );
      },
      size: 100,
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ getValue }) => {
        const status = getValue() as 'success' | 'error' | 'pending';
        const colors = {
          success: 'bg-green-100 text-green-800',
          error: 'bg-red-100 text-red-800',
          pending: 'bg-yellow-100 text-yellow-800',
        };
        return (
          <span className={`px-2 py-1 text-xs rounded-full ${colors[status]}`}>
            {status}
          </span>
        );
      },
      size: 100,
    },
  ], []);
};
```

## 🗄️ Database Schema & Mock Data

```typescript
// src/services/mockData.ts
export const generateMockAnalyticsData = (days: number = 30) => {
  const data = [];
  const now = new Date();
  
  for (let i = days * 24 * 60; i >= 0; i -= 5) { // Every 5 minutes
    const timestamp = new Date(now.getTime() - (i * 60 * 1000));
    
    data.push({
      timestamp: timestamp.toISOString(),
      pageViews: Math.floor(Math.random() * 1000) + 100,
      uniqueVisitors: Math.floor(Math.random() * 500) + 50,
      bounceRate: Math.random() * 0.6 + 0.2, // 20-80%
      avgSessionDuration: Math.floor(Math.random() * 300) + 60, // 1-6 minutes
      conversions: Math.floor(Math.random() * 50),
      revenue: Math.floor(Math.random() * 10000) + 1000,
    });
  }
  
  return data;
};

export const generateRealtimeEvents = () => {
  const events = [
    'page_view', 'button_click', 'form_submit', 'purchase', 'signup', 'download'
  ];
  
  const locations = [
    'homepage', 'product_page', 'checkout', 'dashboard', 'settings', 'contact'
  ];
  
  return {
    id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date().toISOString(),
    event: events[Math.floor(Math.random() * events.length)],
    location: locations[Math.floor(Math.random() * locations.length)],
    user: {
      id: `user_${Math.floor(Math.random() * 10000)}`,
      name: `User ${Math.floor(Math.random() * 1000)}`,
      email: `user${Math.floor(Math.random() * 1000)}@example.com`,
    },
    value: Math.floor(Math.random() * 1000),
    metadata: {
      browser: ['Chrome', 'Firefox', 'Safari', 'Edge'][Math.floor(Math.random() * 4)],
      device: ['desktop', 'mobile', 'tablet'][Math.floor(Math.random() * 3)],
      country: ['US', 'UK', 'CA', 'DE', 'FR'][Math.floor(Math.random() * 5)],
    }
  };
};
```

## 🚀 Deployment Options

### 1. Vercel with API Routes
```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "buildCommand": "npm run build"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/analytics/(.*)",
      "dest": "/api/analytics/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_WS_URL": "wss://your-websocket-server.com"
  }
}
```

### 2. Docker Deployment
```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📊 Performance Optimization

### Monitoring Performance
```typescript
// src/utils/performanceMonitor.ts
class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();
  
  startTiming(label: string): () => void {
    const start = performance.now();
    
    return () => {
      const end = performance.now();
      const duration = end - start;
      
      if (!this.metrics.has(label)) {
        this.metrics.set(label, []);
      }
      
      this.metrics.get(label)!.push(duration);
      
      // Log slow operations
      if (duration > 100) {
        console.warn(`Slow operation detected: ${label} took ${duration.toFixed(2)}ms`);
      }
    };
  }
  
  getStats(label: string) {
    const values = this.metrics.get(label) || [];
    if (values.length === 0) return null;
    
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    return { avg, min, max, count: values.length };
  }
  
  // Monitor chart rendering performance
  monitorChartRender = (chartType: string) => {
    return this.startTiming(`chart_render_${chartType}`);
  };
  
  // Monitor data processing
  monitorDataProcessing = (operation: string) => {
    return this.startTiming(`data_processing_${operation}`);
  };
}

export const performanceMonitor = new PerformanceMonitor();
```

## ✅ Success Criteria

### Performance Targets
- [ ] **Chart Rendering**: < 100ms for datasets up to 10k points
- [ ] **Real-time Updates**: < 50ms latency for WebSocket messages
- [ ] **Data Processing**: < 200ms for aggregations
- [ ] **Memory Usage**: < 100MB for typical dashboard
- [ ] **Bundle Size**: < 500KB gzipped

### Feature Completeness
- [ ] **Interactive Charts**: Zoom, pan, tooltip, click handlers
- [ ] **Real-time Data**: WebSocket integration with <1s updates
- [ ] **Dashboard Builder**: Drag-drop widget management
- [ ] **Data Export**: CSV, JSON, PNG export functionality
- [ ] **Responsive Design**: Mobile and tablet optimized

### Data Visualization Quality
- [ ] **Chart Types**: Line, bar, pie, scatter, heatmap support
- [ ] **Accessibility**: WCAG AA compliance, keyboard navigation
- [ ] **Color Schemes**: Colorblind-friendly palettes
- [ ] **Animation**: Smooth, performant transitions
- [ ] **Customization**: Configurable themes and layouts

## 📚 Additional Resources

### Visualization Libraries
- [Recharts Documentation](https://recharts.org/en-US/)
- [D3.js Tutorials](https://d3js.org/)
- [VISX Examples](https://airbnb.io/visx/)
- [Observable Plot](https://observablehq.com/plot/)

### Performance & Animation
- [Framer Motion Guide](https://www.framer.com/motion/)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Web Vitals](https://web.dev/vitals/)

---

**Previous**: [Collaborative Implementation Guide](./04-Collaborative-Implementation.md)  
**Complete**: All Advanced Project Implementation Guides ✅
