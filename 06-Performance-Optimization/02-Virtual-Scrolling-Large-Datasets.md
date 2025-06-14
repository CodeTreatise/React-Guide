# Virtual Scrolling & Large Dataset Management

## Table of Contents
1. [Introduction to Virtual Scrolling](#introduction-to-virtual-scrolling)
2. [Building Custom Virtual Scrolling](#building-custom-virtual-scrolling)
3. [React Window Integration](#react-window-integration)
4. [Infinite Scrolling Patterns](#infinite-scrolling-patterns)
5. [Large Dataset Optimization](#large-dataset-optimization)
6. [Data Pagination & Virtualization](#data-pagination--virtualization)
7. [Performance Monitoring](#performance-monitoring)
8. [Real-World Implementation](#real-world-implementation)

## Introduction to Virtual Scrolling

Virtual scrolling is a technique that renders only the visible portion of a large dataset, dramatically improving performance when dealing with thousands or millions of items.

### Why Virtual Scrolling Matters

```jsx
// ❌ BAD: Rendering all items at once
function BadLargeList({ items }) {
  return (
    <div style={{ height: '400px', overflow: 'auto' }}>
      {items.map(item => (
        <div key={item.id} style={{ height: '50px', padding: '10px' }}>
          {item.name} - {item.description}
        </div>
      ))}
    </div>
  );
}

// ✅ GOOD: Virtual scrolling approach
function VirtualizedLargeList({ items }) {
  const [startIndex, setStartIndex] = useState(0);
  const [endIndex, setEndIndex] = useState(10);
  
  const visibleItems = items.slice(startIndex, endIndex);
  
  return (
    <VirtualScrollContainer
      items={items}
      itemHeight={50}
      containerHeight={400}
      renderItem={({ item, index }) => (
        <div key={item.id}>
          {item.name} - {item.description}
        </div>
      )}
    />
  );
}
```

### Virtual Scrolling Benefits

```jsx
// Performance comparison hook
function usePerformanceComparison() {
  const [stats, setStats] = useState({
    renderTime: 0,
    memoryUsage: 0,
    domNodes: 0
  });
  
  const measurePerformance = useCallback((operation) => {
    const startTime = performance.now();
    const startMemory = performance.memory?.usedJSHeapSize || 0;
    const startNodes = document.querySelectorAll('*').length;
    
    // Execute operation
    const result = operation();
    
    // Measure results
    Promise.resolve(result).then(() => {
      const endTime = performance.now();
      const endMemory = performance.memory?.usedJSHeapSize || 0;
      const endNodes = document.querySelectorAll('*').length;
      
      setStats({
        renderTime: endTime - startTime,
        memoryUsage: endMemory - startMemory,
        domNodes: endNodes - startNodes
      });
    });
    
    return result;
  }, []);
  
  return { stats, measurePerformance };
}
```

## Building Custom Virtual Scrolling

### Basic Virtual Scroll Hook

```jsx
function useVirtualScrolling({
  items,
  itemHeight,
  containerHeight,
  overscan = 5
}) {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef(null);
  
  // Calculate visible range
  const startIndex = Math.max(
    0,
    Math.floor(scrollTop / itemHeight) - overscan
  );
  const endIndex = Math.min(
    items.length,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );
  
  // Visible items
  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex).map((item, index) => ({
      item,
      index: startIndex + index
    }));
  }, [items, startIndex, endIndex]);
  
  // Total height for scrollbar
  const totalHeight = items.length * itemHeight;
  
  // Offset for positioning
  const offsetY = startIndex * itemHeight;
  
  // Scroll handler
  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);
  
  // Scroll to index
  const scrollToIndex = useCallback((index) => {
    if (scrollElementRef.current) {
      scrollElementRef.current.scrollTop = index * itemHeight;
    }
  }, [itemHeight]);
  
  return {
    scrollElementRef,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    scrollToIndex,
    startIndex,
    endIndex
  };
}
```

### Enhanced Virtual List Component

```jsx
{% raw %}
{% raw %}
function VirtualList({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 5,
  onScroll,
  scrollToAlignment = 'auto'
}) {
  const {
    scrollElementRef,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    scrollToIndex,
    startIndex,
    endIndex
  } = useVirtualScrolling({
    items,
    itemHeight,
    containerHeight,
    overscan
  });
  
  // Enhanced scroll handler
  const enhancedScrollHandler = useCallback((e) => {
    handleScroll(e);
    onScroll?.(e, { startIndex, endIndex });
  }, [handleScroll, onScroll, startIndex, endIndex]);
  
  // Smooth scrolling to index
  const smoothScrollToIndex = useCallback((index, alignment = scrollToAlignment) => {
    if (!scrollElementRef.current) return;
    
    const targetScrollTop = calculateScrollTop(index, alignment);
    
    scrollElementRef.current.scrollTo({
      top: targetScrollTop,
      behavior: 'smooth'
    });
  }, [scrollToAlignment]);
  
  const calculateScrollTop = useCallback((index, alignment) => {
    const itemTop = index * itemHeight;
    const itemBottom = itemTop + itemHeight;
    const currentScrollTop = scrollElementRef.current?.scrollTop || 0;
    const currentScrollBottom = currentScrollTop + containerHeight;
    
    switch (alignment) {
      case 'start':
        return itemTop;
      case 'end':
        return itemBottom - containerHeight;
      case 'center':
        return itemTop - (containerHeight - itemHeight) / 2;
      case 'auto':
      default:
        if (itemTop < currentScrollTop) {
          return itemTop;
        } else if (itemBottom > currentScrollBottom) {
          return itemBottom - containerHeight;
        }
        return currentScrollTop;
    }
  }, [itemHeight, containerHeight]);
  
  // Keyboard navigation
  const handleKeyDown = useCallback((e) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (endIndex < items.length) {
          smoothScrollToIndex(Math.min(endIndex, items.length - 1));
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (startIndex > 0) {
          smoothScrollToIndex(Math.max(startIndex - 1, 0));
        }
        break;
      case 'PageDown':
        e.preventDefault();
        const pageSize = Math.floor(containerHeight / itemHeight);
        smoothScrollToIndex(Math.min(startIndex + pageSize, items.length - 1));
        break;
      case 'PageUp':
        e.preventDefault();
        const pageSizeUp = Math.floor(containerHeight / itemHeight);
        smoothScrollToIndex(Math.max(startIndex - pageSizeUp, 0));
        break;
      case 'Home':
        e.preventDefault();
        smoothScrollToIndex(0, 'start');
        break;
      case 'End':
        e.preventDefault();
        smoothScrollToIndex(items.length - 1, 'end');
        break;
    }
  }, [startIndex, endIndex, items.length, smoothScrollToIndex, containerHeight, itemHeight]);
  
  return (
    <div
      ref={scrollElementRef}
      style={{
        height: containerHeight,
        overflow: 'auto',
        outline: 'none'
      }}
      onScroll={enhancedScrollHandler}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map(({ item, index }) =>
            renderItem({ item, index, style: { height: itemHeight } })
          )}
        </div>
      </div>
    </div>
  );
}
{% endraw %}
{% endraw %}
```

### Variable Height Virtual Scrolling

```jsx
function useVariableHeightVirtualScrolling({
  items,
  estimatedItemHeight = 50,
  containerHeight,
  overscan = 5,
  getItemHeight
}) {
  const [scrollTop, setScrollTop] = useState(0);
  const itemHeightsRef = useRef(new Map());
  const itemPositionsRef = useRef(new Map());
  const scrollElementRef = useRef(null);
  
  // Measure item height
  const measureItemHeight = useCallback((index, element) => {
    if (element) {
      const height = element.getBoundingClientRect().height;
      itemHeightsRef.current.set(index, height);
      
      // Recalculate positions
      let position = 0;
      for (let i = 0; i <= index; i++) {
        itemPositionsRef.current.set(i, position);
        const itemHeight = itemHeightsRef.current.get(i) || 
                          getItemHeight?.(items[i], i) || 
                          estimatedItemHeight;
        position += itemHeight;
      }
    }
  }, [items, estimatedItemHeight, getItemHeight]);
  
  // Get item position
  const getItemPosition = useCallback((index) => {
    if (itemPositionsRef.current.has(index)) {
      return itemPositionsRef.current.get(index);
    }
    
    // Calculate estimated position
    return index * estimatedItemHeight;
  }, [estimatedItemHeight]);
  
  // Get item height
  const getItemHeightMemo = useCallback((index) => {
    return itemHeightsRef.current.get(index) || 
           getItemHeight?.(items[index], index) || 
           estimatedItemHeight;
  }, [items, estimatedItemHeight, getItemHeight]);
  
  // Calculate visible range
  const { startIndex, endIndex } = useMemo(() => {
    let start = 0;
    let end = items.length;
    
    // Binary search for start index
    let low = 0;
    let high = items.length - 1;
    
    while (low <= high) {
      const mid = Math.floor((low + high) / 2);
      const position = getItemPosition(mid);
      
      if (position < scrollTop) {
        low = mid + 1;
      } else {
        high = mid - 1;
      }
    }
    
    start = Math.max(0, low - overscan);
    
    // Find end index
    let currentPosition = getItemPosition(start);
    end = start;
    
    while (end < items.length && currentPosition < scrollTop + containerHeight) {
      currentPosition += getItemHeightMemo(end);
      end++;
    }
    
    end = Math.min(items.length, end + overscan);
    
    return { startIndex: start, endIndex: end };
  }, [scrollTop, items.length, containerHeight, overscan, getItemPosition, getItemHeightMemo]);
  
  // Visible items
  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex).map((item, index) => ({
      item,
      index: startIndex + index,
      position: getItemPosition(startIndex + index),
      height: getItemHeightMemo(startIndex + index)
    }));
  }, [items, startIndex, endIndex, getItemPosition, getItemHeightMemo]);
  
  // Total height
  const totalHeight = useMemo(() => {
    let height = 0;
    for (let i = 0; i < items.length; i++) {
      height += getItemHeightMemo(i);
    }
    return height;
  }, [items.length, getItemHeightMemo]);
  
  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);
  
  return {
    scrollElementRef,
    visibleItems,
    totalHeight,
    handleScroll,
    measureItemHeight,
    startIndex,
    endIndex
  };
}
```

## React Window Integration

### Using react-window for Lists

```jsx
import { FixedSizeList, VariableSizeList } from 'react-window';

// Fixed size list component
function FixedSizeVirtualList({ items, itemHeight = 50, height = 400 }) {
  const renderItem = useCallback(({ index, style }) => {
    const item = items[index];
    
    return (
      <div style={style}>
        <ItemComponent item={item} />
      </div>
    );
  }, [items]);
  
  return (
    <FixedSizeList
      height={height}
      itemCount={items.length}
      itemSize={itemHeight}
      itemData={items}
    >
      {renderItem}
    </FixedSizeList>
  );
}

// Variable size list with dynamic heights
function VariableSizeVirtualList({ items, getItemHeight, height = 400 }) {
  const listRef = useRef(null);
  const itemHeightCache = useRef(new Map());
  
  const getItemSize = useCallback((index) => {
    if (itemHeightCache.current.has(index)) {
      return itemHeightCache.current.get(index);
    }
    
    const height = getItemHeight(items[index], index);
    itemHeightCache.current.set(index, height);
    return height;
  }, [items, getItemHeight]);
  
  const renderItem = useCallback(({ index, style }) => {
    const item = items[index];
    
    return (
      <div style={style}>
        <ItemComponent 
          item={item} 
          onHeightChange={(height) => {
            itemHeightCache.current.set(index, height);
            listRef.current?.resetAfterIndex(index);
          }}
        />
      </div>
    );
  }, [items]);
  
  return (
    <VariableSizeList
      ref={listRef}
      height={height}
      itemCount={items.length}
      itemSize={getItemSize}
      itemData={items}
    >
      {renderItem}
    </VariableSizeList>
  );
}
```

### Grid Virtualization

```jsx
import { FixedSizeGrid } from 'react-window';

function VirtualizedGrid({ 
  items, 
  columnCount = 3, 
  rowHeight = 200, 
  columnWidth = 300,
  height = 600 
}) {
  const rowCount = Math.ceil(items.length / columnCount);
  
  const renderCell = useCallback(({ columnIndex, rowIndex, style }) => {
    const itemIndex = rowIndex * columnCount + columnIndex;
    const item = items[itemIndex];
    
    if (!item) {
      return <div style={style} />;
    }
    
    return (
      <div style={style}>
        <div style={{ padding: '10px' }}>
          <GridItemComponent item={item} />
        </div>
      </div>
    );
  }, [items, columnCount]);
  
  return (
    <FixedSizeGrid
      columnCount={columnCount}
      columnWidth={columnWidth}
      height={height}
      rowCount={rowCount}
      rowHeight={rowHeight}
      itemData={items}
    >
      {renderCell}
    </FixedSizeGrid>
  );
}
```

### Advanced Grid with Dynamic Content

```jsx
function AdvancedVirtualGrid({
  items,
  columnCount,
  getItemSize,
  height,
  onItemClick
}) {
  const [selectedItems, setSelectedItems] = useState(new Set());
  const gridRef = useRef(null);
  
  const handleItemClick = useCallback((item, index) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(item.id)) {
        newSet.delete(item.id);
      } else {
        newSet.add(item.id);
      }
      return newSet;
    });
    
    onItemClick?.(item, index);
  }, [onItemClick]);
  
  const renderCell = useCallback(({ columnIndex, rowIndex, style }) => {
    const itemIndex = rowIndex * columnCount + columnIndex;
    const item = items[itemIndex];
    
    if (!item) return <div style={style} />;
    
    const isSelected = selectedItems.has(item.id);
    
    return (
      <div
        style={{
          ...style,
          padding: '5px'
        }}
      >
        <div
          style={{
            height: '100%',
            padding: '10px',
            border: isSelected ? '2px solid #007bff' : '1px solid #ddd',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onClick={() => handleItemClick(item, itemIndex)}
        >
          <GridItemComponent item={item} isSelected={isSelected} />
        </div>
      </div>
    );
  }, [items, columnCount, selectedItems, handleItemClick]);
  
  return (
    <FixedSizeGrid
      ref={gridRef}
      columnCount={columnCount}
      columnWidth={getItemSize.width}
      height={height}
      rowCount={Math.ceil(items.length / columnCount)}
      rowHeight={getItemSize.height}
    >
      {renderCell}
    </FixedSizeGrid>
  );
}
```

## Infinite Scrolling Patterns

### Basic Infinite Scroll Hook

```jsx
function useInfiniteScroll({
  hasMore,
  loading,
  onLoadMore,
  threshold = 0.8
}) {
  const containerRef = useRef(null);
  const [isFetching, setIsFetching] = useState(false);
  
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const scrollPercentage = (scrollTop + clientHeight) / scrollHeight;
      
      if (scrollPercentage >= threshold && hasMore && !loading && !isFetching) {
        setIsFetching(true);
        onLoadMore();
      }
    };
    
    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [hasMore, loading, onLoadMore, threshold, isFetching]);
  
  useEffect(() => {
    if (!loading) {
      setIsFetching(false);
    }
  }, [loading]);
  
  return { containerRef, isFetching };
}
```

### Advanced Infinite Scroll with Intersection Observer

```jsx
function useIntersectionInfiniteScroll({
  hasMore,
  loading,
  onLoadMore,
  rootMargin = '100px'
}) {
  const loadingRef = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const target = entries[0];
        if (target.isIntersecting && hasMore && !loading) {
          onLoadMore();
        }
      },
      {
        rootMargin,
        threshold: 0.1
      }
    );
    
    const currentLoadingRef = loadingRef.current;
    if (currentLoadingRef) {
      observer.observe(currentLoadingRef);
    }
    
    return () => {
      if (currentLoadingRef) {
        observer.unobserve(currentLoadingRef);
      }
    };
  }, [hasMore, loading, onLoadMore, rootMargin]);
  
  return { loadingRef };
}
```

### Infinite Scroll with Virtual List

```jsx
{% raw %}
{% raw %}
function InfiniteVirtualList({
  items,
  hasMore,
  loading,
  onLoadMore,
  itemHeight = 60,
  containerHeight = 400,
  loadingComponent: LoadingComponent = DefaultLoadingComponent
}) {
  const { containerRef } = useInfiniteScroll({
    hasMore,
    loading,
    onLoadMore,
    threshold: 0.9
  });
  
  const {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  } = useVirtualScrolling({
    items,
    itemHeight,
    containerHeight
  });
  
  const combinedScrollHandler = useCallback((e) => {
    handleScroll(e);
  }, [handleScroll]);
  
  return (
    <div
      ref={containerRef}
      style={{
        height: containerHeight,
        overflow: 'auto'
      }}
      onScroll={combinedScrollHandler}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map(({ item, index }) => (
            <div key={item.id || index} style={{ height: itemHeight }}>
              <ListItemComponent item={item} />
            </div>
          ))}
        </div>
      </div>
      
      {loading && (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <LoadingComponent />
        </div>
      )}
      
      {!hasMore && items.length > 0 && (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          No more items to load
        </div>
      )}
    </div>
  );
}
{% endraw %}
{% endraw %}
```

### Bidirectional Infinite Scroll

```jsx
function useBidirectionalInfiniteScroll({
  onLoadMore,
  onLoadPrevious,
  hasMore,
  hasPrevious,
  loading,
  threshold = 100
}) {
  const containerRef = useRef(null);
  const [scrollPosition, setScrollPosition] = useState(0);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isLoadingPrevious, setIsLoadingPrevious] = useState(false);
  
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      
      // Load more at bottom
      if (
        scrollHeight - scrollTop - clientHeight < threshold &&
        hasMore &&
        !loading &&
        !isLoadingMore
      ) {
        setIsLoadingMore(true);
        onLoadMore().finally(() => setIsLoadingMore(false));
      }
      
      // Load previous at top
      if (
        scrollTop < threshold &&
        hasPrevious &&
        !loading &&
        !isLoadingPrevious
      ) {
        const previousScrollHeight = scrollHeight;
        setIsLoadingPrevious(true);
        
        onLoadPrevious().then(() => {
          // Maintain scroll position after prepending items
          const newScrollHeight = container.scrollHeight;
          container.scrollTop = scrollTop + (newScrollHeight - previousScrollHeight);
          setIsLoadingPrevious(false);
        });
      }
      
      setScrollPosition(scrollTop);
    };
    
    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [hasMore, hasPrevious, loading, onLoadMore, onLoadPrevious, threshold, isLoadingMore, isLoadingPrevious]);
  
  return {
    containerRef,
    scrollPosition,
    isLoadingMore,
    isLoadingPrevious
  };
}
```

## Large Dataset Optimization

### Data Chunking and Processing

```jsx
function useChunkedProcessing(data, chunkSize = 1000, processingDelay = 10) {
  const [processedData, setProcessedData] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const processChunk = useCallback(async (chunk, processor) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const processed = chunk.map(processor);
        resolve(processed);
      }, processingDelay);
    });
  }, [processingDelay]);
  
  const processData = useCallback(async (processor) => {
    setIsProcessing(true);
    setProgress(0);
    setProcessedData([]);
    
    const chunks = [];
    for (let i = 0; i < data.length; i += chunkSize) {
      chunks.push(data.slice(i, i + chunkSize));
    }
    
    const results = [];
    
    for (let i = 0; i < chunks.length; i++) {
      const processedChunk = await processChunk(chunks[i], processor);
      results.push(...processedChunk);
      
      setProcessedData([...results]);
      setProgress(((i + 1) / chunks.length) * 100);
    }
    
    setIsProcessing(false);
  }, [data, chunkSize, processChunk]);
  
  return {
    processedData,
    isProcessing,
    progress,
    processData
  };
}
```

### Memory-Efficient Data Handling

```jsx
function useMemoryEfficientData({
  pageSize = 100,
  cacheSize = 5,
  fetchData
}) {
  const [pages, setPages] = useState(new Map());
  const [loading, setLoading] = useState(new Set());
  const [errors, setErrors] = useState(new Map());
  const cacheOrder = useRef([]);
  
  const loadPage = useCallback(async (pageIndex) => {
    if (pages.has(pageIndex) || loading.has(pageIndex)) {
      return;
    }
    
    setLoading(prev => new Set(prev).add(pageIndex));
    setErrors(prev => {
      const newErrors = new Map(prev);
      newErrors.delete(pageIndex);
      return newErrors;
    });
    
    try {
      const pageData = await fetchData(pageIndex, pageSize);
      
      setPages(prev => {
        const newPages = new Map(prev);
        newPages.set(pageIndex, pageData);
        
        // Update cache order
        cacheOrder.current = cacheOrder.current.filter(p => p !== pageIndex);
        cacheOrder.current.push(pageIndex);
        
        // Remove oldest pages if cache is full
        while (cacheOrder.current.length > cacheSize) {
          const oldestPage = cacheOrder.current.shift();
          newPages.delete(oldestPage);
        }
        
        return newPages;
      });
    } catch (error) {
      setErrors(prev => {
        const newErrors = new Map(prev);
        newErrors.set(pageIndex, error);
        return newErrors;
      });
    } finally {
      setLoading(prev => {
        const newLoading = new Set(prev);
        newLoading.delete(pageIndex);
        return newLoading;
      });
    }
  }, [fetchData, pageSize, cacheSize]);
  
  const getItem = useCallback((index) => {
    const pageIndex = Math.floor(index / pageSize);
    const itemIndex = index % pageSize;
    
    if (!pages.has(pageIndex)) {
      loadPage(pageIndex);
      return null;
    }
    
    const page = pages.get(pageIndex);
    return page?.[itemIndex] || null;
  }, [pages, pageSize, loadPage]);
  
  const preloadPages = useCallback((startIndex, endIndex) => {
    const startPage = Math.floor(startIndex / pageSize);
    const endPage = Math.floor(endIndex / pageSize);
    
    for (let page = startPage; page <= endPage; page++) {
      if (!pages.has(page) && !loading.has(page)) {
        loadPage(page);
      }
    }
  }, [pageSize, pages, loading, loadPage]);
  
  return {
    getItem,
    loadPage,
    preloadPages,
    isLoading: (pageIndex) => loading.has(pageIndex),
    getError: (pageIndex) => errors.get(pageIndex),
    getCachedPages: () => Array.from(pages.keys())
  };
}
```

### Optimized Search and Filtering

```jsx
function useOptimizedSearch(data, searchFields = ['name']) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredData, setFilteredData] = useState(data);
  const [isSearching, setIsSearching] = useState(false);
  
  // Create search index
  const searchIndex = useMemo(() => {
    const index = new Map();
    
    data.forEach((item, itemIndex) => {
      searchFields.forEach(field => {
        const value = item[field]?.toString().toLowerCase() || '';
        
        // Create ngrams for fuzzy search
        for (let i = 0; i <= value.length - 2; i++) {
          const ngram = value.substr(i, 3);
          if (!index.has(ngram)) {
            index.set(ngram, new Set());
          }
          index.get(ngram).add(itemIndex);
        }
      });
    });
    
    return index;
  }, [data, searchFields]);
  
  // Debounced search
  const debouncedSearch = useMemo(
    () => debounce((term) => {
      setIsSearching(true);
      
      if (!term) {
        setFilteredData(data);
        setIsSearching(false);
        return;
      }
      
      // Use Web Workers for heavy search operations
      if (window.Worker && data.length > 10000) {
        const worker = new Worker('/search-worker.js');
        worker.postMessage({ data, term, searchFields });
        
        worker.onmessage = (e) => {
          setFilteredData(e.data);
          setIsSearching(false);
          worker.terminate();
        };
      } else {
        // Fallback to main thread search
        const results = performSearch(term);
        setFilteredData(results);
        setIsSearching(false);
      }
    }, 300),
    [data, searchFields, searchIndex]
  );
  
  const performSearch = useCallback((term) => {
    const lowerTerm = term.toLowerCase();
    const candidateIndices = new Set();
    
    // Use ngram index for initial filtering
    for (let i = 0; i <= lowerTerm.length - 2; i++) {
      const ngram = lowerTerm.substr(i, 3);
      const indices = searchIndex.get(ngram);
      if (indices) {
        indices.forEach(idx => candidateIndices.add(idx));
      }
    }
    
    // Filter candidates with exact matching
    return Array.from(candidateIndices)
      .map(idx => data[idx])
      .filter(item => {
        return searchFields.some(field => {
          const value = item[field]?.toString().toLowerCase() || '';
          return value.includes(lowerTerm);
        });
      })
      .sort((a, b) => {
        // Score based on match position
        const aScore = getMatchScore(a, lowerTerm);
        const bScore = getMatchScore(b, lowerTerm);
        return bScore - aScore;
      });
  }, [data, searchFields, searchIndex]);
  
  const getMatchScore = useCallback((item, term) => {
    let score = 0;
    searchFields.forEach(field => {
      const value = item[field]?.toString().toLowerCase() || '';
      const index = value.indexOf(term);
      if (index !== -1) {
        // Higher score for matches at beginning
        score += (value.length - index) / value.length;
      }
    });
    return score;
  }, [searchFields]);
  
  useEffect(() => {
    debouncedSearch(searchTerm);
  }, [searchTerm, debouncedSearch]);
  
  return {
    searchTerm,
    setSearchTerm,
    filteredData,
    isSearching
  };
}
```

## Data Pagination & Virtualization

### Advanced Pagination Hook

```jsx
{% raw %}
{% raw %}
function useAdvancedPagination({
  totalItems,
  itemsPerPage = 20,
  initialPage = 1,
  prefetchPages = 2
}) {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [loadedPages, setLoadedPages] = useState(new Set([initialPage]));
  const [pageData, setPageData] = useState(new Map());
  const [loading, setLoading] = useState(new Set());
  
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  
  const loadPage = useCallback(async (page, fetchFunction) => {
    if (loadedPages.has(page) || loading.has(page) || page < 1 || page > totalPages) {
      return;
    }
    
    setLoading(prev => new Set(prev).add(page));
    
    try {
      const data = await fetchFunction(page, itemsPerPage);
      
      setPageData(prev => new Map(prev).set(page, data));
      setLoadedPages(prev => new Set(prev).add(page));
    } catch (error) {
      console.error(`Failed to load page ${page}:`, error);
    } finally {
      setLoading(prev => {
        const newLoading = new Set(prev);
        newLoading.delete(page);
        return newLoading;
      });
    }
  }, [loadedPages, loading, totalPages, itemsPerPage]);
  
  const prefetchAdjacentPages = useCallback((page, fetchFunction) => {
    for (let i = Math.max(1, page - prefetchPages); i <= Math.min(totalPages, page + prefetchPages); i++) {
      if (i !== page) {
        loadPage(i, fetchFunction);
      }
    }
  }, [loadPage, prefetchPages, totalPages]);
  
  const goToPage = useCallback((page, fetchFunction) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      loadPage(page, fetchFunction);
      prefetchAdjacentPages(page, fetchFunction);
    }
  }, [totalPages, loadPage, prefetchAdjacentPages]);
  
  const nextPage = useCallback((fetchFunction) => {
    if (currentPage < totalPages) {
      goToPage(currentPage + 1, fetchFunction);
    }
  }, [currentPage, totalPages, goToPage]);
  
  const previousPage = useCallback((fetchFunction) => {
    if (currentPage > 1) {
      goToPage(currentPage - 1, fetchFunction);
    }
  }, [currentPage, goToPage]);
  
  return {
    currentPage,
    totalPages,
    pageData: pageData.get(currentPage) || [],
    isLoading: loading.has(currentPage),
    loadedPages,
    goToPage,
    nextPage,
    previousPage,
    hasNextPage: currentPage < totalPages,
    hasPreviousPage: currentPage > 1,
    getPageData: (page) => pageData.get(page) || []
  };
}
{% endraw %}
{% endraw %}
```

### Virtual Pagination Component

```jsx
{% raw %}
{% raw %}
function VirtualPaginatedList({
  totalItems,
  itemsPerPage = 20,
  itemHeight = 60,
  containerHeight = 400,
  fetchData,
  renderItem,
  loadingComponent: LoadingComponent = DefaultLoadingComponent
}) {
  const {
    currentPage,
    totalPages,
    pageData,
    isLoading,
    goToPage,
    nextPage,
    previousPage,
    hasNextPage,
    hasPreviousPage
  } = useAdvancedPagination({ totalItems, itemsPerPage });
  
  const {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    scrollToIndex
  } = useVirtualScrolling({
    items: pageData,
    itemHeight,
    containerHeight
  });
  
  // Load initial page
  useEffect(() => {
    goToPage(1, fetchData);
  }, [goToPage, fetchData]);
  
  // Handle page navigation
  const handlePageChange = useCallback((page) => {
    goToPage(page, fetchData);
    scrollToIndex(0); // Scroll to top when page changes
  }, [goToPage, fetchData, scrollToIndex]);
  
  return (
    <div>
      {/* Virtual List */}
      <div
        style={{
          height: containerHeight,
          overflow: 'auto',
          border: '1px solid #ddd',
          borderRadius: '4px'
        }}
        onScroll={handleScroll}
      >
        {isLoading ? (
          <div style={{ 
            height: containerHeight, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center' 
          }}>
            <LoadingComponent />
          </div>
        ) : (
          <div style={{ height: totalHeight, position: 'relative' }}>
            <div
              style={{
                transform: `translateY(${offsetY}px)`,
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0
              }}
            >
              {visibleItems.map(({ item, index }) =>
                renderItem({ item, index, style: { height: itemHeight } })
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Pagination Controls */}
      <div style={{ 
        marginTop: '10px', 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px'
      }}>
        <button 
          onClick={() => previousPage(fetchData)}
          disabled={!hasPreviousPage || isLoading}
        >
          Previous
        </button>
        
        <div style={{ display: 'flex', gap: '5px' }}>
          {/* Page numbers */}
          {Array.from({ length: Math.min(totalPages, 10) }, (_, i) => {
            const pageNumber = i + 1;
            return (
              <button
                key={pageNumber}
                onClick={() => handlePageChange(pageNumber)}
                disabled={isLoading}
                style={{
                  padding: '5px 10px',
                  background: pageNumber === currentPage ? '#007bff' : '#f8f9fa',
                  color: pageNumber === currentPage ? 'white' : 'black',
                  border: '1px solid #ddd',
                  borderRadius: '3px'
                }}
              >
                {pageNumber}
              </button>
            );
          })}
        </div>
        
        <button 
          onClick={() => nextPage(fetchData)}
          disabled={!hasNextPage || isLoading}
        >
          Next
        </button>
      </div>
      
      {/* Page Info */}
      <div style={{ textAlign: 'center', marginTop: '10px', color: '#666' }}>
        Page {currentPage} of {totalPages} ({totalItems} total items)
      </div>
    </div>
  );
}
{% endraw %}
{% endraw %}
```

## Performance Monitoring

### Virtual Scroll Performance Monitor

```jsx
function useVirtualScrollPerformance() {
  const [metrics, setMetrics] = useState({
    renderTime: 0,
    scrollEvents: 0,
    visibleItems: 0,
    totalItems: 0,
    fps: 0
  });
  
  const frameCount = useRef(0);
  const lastTime = useRef(performance.now());
  const scrollEventCount = useRef(0);
  
  const measureRenderTime = useCallback((operation) => {
    const startTime = performance.now();
    const result = operation();
    const endTime = performance.now();
    
    setMetrics(prev => ({
      ...prev,
      renderTime: endTime - startTime
    }));
    
    return result;
  }, []);
  
  const trackScrollEvent = useCallback(() => {
    scrollEventCount.current++;
    setMetrics(prev => ({
      ...prev,
      scrollEvents: scrollEventCount.current
    }));
  }, []);
  
  const updateVisibleItems = useCallback((visible, total) => {
    setMetrics(prev => ({
      ...prev,
      visibleItems: visible,
      totalItems: total
    }));
  }, []);
  
  // FPS monitoring
  useEffect(() => {
    const updateFPS = () => {
      frameCount.current++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime.current >= 1000) {
        const fps = Math.round((frameCount.current * 1000) / (currentTime - lastTime.current));
        
        setMetrics(prev => ({
          ...prev,
          fps
        }));
        
        frameCount.current = 0;
        lastTime.current = currentTime;
      }
      
      requestAnimationFrame(updateFPS);
    };
    
    const animationId = requestAnimationFrame(updateFPS);
    return () => cancelAnimationFrame(animationId);
  }, []);
  
  return {
    metrics,
    measureRenderTime,
    trackScrollEvent,
    updateVisibleItems
  };
}
```

### Memory Usage Monitor

```jsx
function useMemoryMonitor() {
  const [memoryUsage, setMemoryUsage] = useState({
    used: 0,
    total: 0,
    limit: 0
  });
  
  useEffect(() => {
    const updateMemoryUsage = () => {
      if (performance.memory) {
        setMemoryUsage({
          used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
          total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
          limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
        });
      }
    };
    
    updateMemoryUsage();
    const interval = setInterval(updateMemoryUsage, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return memoryUsage;
}
```

## Real-World Implementation

### Complete Virtual Table Example

```jsx
{% raw %}
{% raw %}
function VirtualTable({
  data,
  columns,
  rowHeight = 40,
  headerHeight = 50,
  containerHeight = 400,
  sortable = true,
  selectable = true
}) {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: null });
  const [selectedRows, setSelectedRows] = useState(new Set());
  const tableRef = useRef(null);
  
  // Sort data
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return data;
    
    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig]);
  
  const {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  } = useVirtualScrolling({
    items: sortedData,
    itemHeight: rowHeight,
    containerHeight: containerHeight - headerHeight
  });
  
  const handleSort = useCallback((columnKey) => {
    if (!sortable) return;
    
    setSortConfig(prev => ({
      key: columnKey,
      direction: prev.key === columnKey && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  }, [sortable]);
  
  const handleRowSelect = useCallback((rowId) => {
    if (!selectable) return;
    
    setSelectedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(rowId)) {
        newSet.delete(rowId);
      } else {
        newSet.add(rowId);
      }
      return newSet;
    });
  }, [selectable]);
  
  const handleSelectAll = useCallback(() => {
    if (!selectable) return;
    
    if (selectedRows.size === sortedData.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(sortedData.map(row => row.id)));
    }
  }, [selectable, selectedRows.size, sortedData]);
  
  return (
    <div style={{ border: '1px solid #ddd', borderRadius: '4px' }}>
      {/* Header */}
      <div 
        style={{
          height: headerHeight,
          display: 'flex',
          backgroundColor: '#f8f9fa',
          borderBottom: '1px solid #ddd'
        }}
      >
        {selectable && (
          <div style={{ width: '50px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <input
              type="checkbox"
              checked={selectedRows.size === sortedData.length && sortedData.length > 0}
              onChange={handleSelectAll}
            />
          </div>
        )}
        {columns.map((column) => (
          <div
            key={column.key}
            style={{
              flex: column.width || 1,
              padding: '10px',
              fontWeight: 'bold',
              cursor: sortable ? 'pointer' : 'default',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
            onClick={() => handleSort(column.key)}
          >
            {column.title}
            {sortable && sortConfig.key === column.key && (
              <span>{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
            )}
          </div>
        ))}
      </div>
      
      {/* Virtual Body */}
      <div
        ref={tableRef}
        style={{
          height: containerHeight - headerHeight,
          overflow: 'auto'
        }}
        onScroll={handleScroll}
      >
        <div style={{ height: totalHeight, position: 'relative' }}>
          <div
            style={{
              transform: `translateY(${offsetY}px)`,
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0
            }}
          >
            {visibleItems.map(({ item: row, index }) => (
              <div
                key={row.id}
                style={{
                  height: rowHeight,
                  display: 'flex',
                  borderBottom: '1px solid #eee',
                  backgroundColor: selectedRows.has(row.id) ? '#e3f2fd' : 'white'
                }}
              >
                {selectable && (
                  <div style={{ width: '50px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <input
                      type="checkbox"
                      checked={selectedRows.has(row.id)}
                      onChange={() => handleRowSelect(row.id)}
                    />
                  </div>
                )}
                {columns.map((column) => (
                  <div
                    key={column.key}
                    style={{
                      flex: column.width || 1,
                      padding: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#f8f9fa', 
        borderTop: '1px solid #ddd',
        fontSize: '14px',
        color: '#666'
      }}>
        {selectedRows.size > 0 && `${selectedRows.size} of `}
        {sortedData.length} rows
      </div>
    </div>
  );
}
{% endraw %}
{% endraw %}
```

### Usage Examples

```jsx
{% raw %}
{% raw %}
// Example usage
function App() {
  const [tableData, setTableData] = useState([]);
  
  const columns = [
    { key: 'id', title: 'ID', width: 80 },
    { key: 'name', title: 'Name', width: 200 },
    { key: 'email', title: 'Email', width: 250 },
    { 
      key: 'status', 
      title: 'Status',
      render: (value) => (
        <span style={{ 
          padding: '4px 8px',
          borderRadius: '12px',
          backgroundColor: value === 'active' ? '#4caf50' : '#f44336',
          color: 'white',
          fontSize: '12px'
        }}>
          {value}
        </span>
      )
    }
  ];
  
  useEffect(() => {
    // Generate large dataset
    const data = Array.from({ length: 10000 }, (_, i) => ({
      id: i + 1,
      name: `User ${i + 1}`,
      email: `user${i + 1}@example.com`,
      status: Math.random() > 0.5 ? 'active' : 'inactive'
    }));
    setTableData(data);
  }, []);
  
  return (
    <div style={{ padding: '20px' }}>
      <h2>Virtual Table with 10,000 rows</h2>
      <VirtualTable
        data={tableData}
        columns={columns}
        containerHeight={600}
        sortable={true}
        selectable={true}
      />
    </div>
  );
}
{% endraw %}
{% endraw %}
```

## Summary

Virtual scrolling and large dataset management are essential techniques for building performant React applications that handle massive amounts of data. Key takeaways:

### Best Practices:
1. **Use virtual scrolling** for lists with more than 100-200 items
2. **Implement proper caching** to avoid redundant data fetching
3. **Chunk large operations** to prevent blocking the main thread
4. **Monitor performance metrics** to identify bottlenecks
5. **Prefetch adjacent data** for smooth user experience

### Performance Considerations:
- Virtual scrolling reduces DOM nodes from thousands to dozens
- Memory usage stays constant regardless of dataset size
- Smooth 60fps scrolling even with millions of items
- Intelligent caching prevents unnecessary network requests

### When to Use:
- Large data tables (>1000 rows)
- Infinite feeds (social media, news)
- File browsers with many items
- Search results with extensive datasets
- Real-time data streams

These techniques ensure your React applications remain responsive and performant even when dealing with massive datasets, providing users with a smooth and enjoyable experience.
