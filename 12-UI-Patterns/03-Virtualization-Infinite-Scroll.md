# Virtualization & Infinite Scroll Patterns

## Introduction to Virtualization

Virtualization is a technique for efficiently rendering large datasets by only rendering the items that are currently visible in the viewport. This dramatically improves performance when dealing with thousands or millions of items.

### Why Virtualization Matters

1. **Performance**: Render only visible items instead of all items
2. **Memory Efficiency**: Reduce DOM nodes and memory usage
3. **Smooth Scrolling**: Maintain 60fps even with large datasets
4. **User Experience**: Instant loading regardless of dataset size

## Basic Virtual Scrolling Implementation

```jsx
{% raw %}
import React, { useState, useEffect, useRef, useMemo } from 'react'

const VirtualList = ({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 5,
}) => {
  const [scrollTop, setScrollTop] = useState(0)
  const containerRef = useRef()

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    )
    return { startIndex, endIndex }
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan])

  // Generate visible items
  const visibleItems = useMemo(() => {
    const { startIndex, endIndex } = visibleRange
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index,
    }))
  }, [items, visibleRange])

  const handleScroll = (e) => {
    setScrollTop(e.currentTarget.scrollTop)
  }

  const totalHeight = items.length * itemHeight
  const offsetY = visibleRange.startIndex * itemHeight

  return (
    <div
      ref={containerRef}
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map(({ item, index }) => (
            <div
              key={index}
              style={{ height: itemHeight }}
            >
              {renderItem(item, index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Usage
const BasicVirtualListExample = () => {
  const items = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
    value: Math.random(),
  }))

  return (
    <VirtualList
      items={items}
      itemHeight={50}
      containerHeight={400}
      renderItem={(item) => (
        <div style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
          <strong>{item.name}</strong> - {item.value.toFixed(3)}
        </div>
      )}
    />
  )
}
{% endraw %}
```

## Advanced Virtual Scrolling with Dynamic Heights

```jsx
import React, { useState, useEffect, useRef, useCallback } from 'react'

const DynamicVirtualList = ({
  items,
  estimatedItemHeight = 50,
  containerHeight,
  renderItem,
  getItemKey,
  overscan = 5,
}) => {
  const [scrollTop, setScrollTop] = useState(0)
  const [heights, setHeights] = useState(new Map())
  const containerRef = useRef()
  const itemsRef = useRef(new Map())

  // Measure item heights after render
  const measureHeights = useCallback(() => {
    const newHeights = new Map()
    itemsRef.current.forEach((element, index) => {
      if (element) {
        newHeights.set(index, element.getBoundingClientRect().height)
      }
    })
    setHeights(prev => new Map([...prev, ...newHeights]))
  }, [])

  useEffect(() => {
    measureHeights()
  })

  // Calculate positions and visible range
  const { visibleRange, totalHeight, offsetMap } = useMemo(() => {
    const positions = new Map()
    const offsets = new Map()
    let totalHeight = 0

    items.forEach((_, index) => {
      offsets.set(index, totalHeight)
      const height = heights.get(index) || estimatedItemHeight
      positions.set(index, { top: totalHeight, height })
      totalHeight += height
    })

    // Find visible range
    let startIndex = 0
    let endIndex = items.length - 1

    for (let i = 0; i < items.length; i++) {
      const position = positions.get(i)
      if (position.top + position.height >= scrollTop) {
        startIndex = Math.max(0, i - overscan)
        break
      }
    }

    for (let i = startIndex; i < items.length; i++) {
      const position = positions.get(i)
      if (position.top > scrollTop + containerHeight) {
        endIndex = Math.min(items.length - 1, i + overscan)
        break
      }
    }

    return {
      visibleRange: { startIndex, endIndex },
      totalHeight,
      offsetMap: offsets,
    }
  }, [scrollTop, heights, items.length, containerHeight, estimatedItemHeight, overscan])

  const visibleItems = useMemo(() => {
    const { startIndex, endIndex } = visibleRange
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index,
    }))
  }, [items, visibleRange])

  const handleScroll = (e) => {
    setScrollTop(e.currentTarget.scrollTop)
  }

  const setItemRef = (index) => (element) => {
    if (element) {
      itemsRef.current.set(index, element)
    } else {
      itemsRef.current.delete(index)
    }
  }

  return (
    <div
      ref={containerRef}
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index }) => (
          <div
            key={getItemKey ? getItemKey(item, index) : index}
            ref={setItemRef(index)}
            style={{
              position: 'absolute',
              top: offsetMap.get(index) || 0,
              left: 0,
              right: 0,
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  )
}
```

## Infinite Scroll Implementation

```jsx
{% raw %}
import React, { useState, useEffect, useCallback, useRef } from 'react'

const useInfiniteScroll = ({
  fetchMore,
  hasNextPage,
  threshold = 200,
  enabled = true,
}) => {
  const [loading, setLoading] = useState(false)
  const observerRef = useRef()
  const loadingRef = useRef()

  const loadMore = useCallback(async () => {
    if (loading || !hasNextPage || !enabled) return

    setLoading(true)
    try {
      await fetchMore()
    } finally {
      setLoading(false)
    }
  }, [loading, hasNextPage, fetchMore, enabled])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const target = entries[0]
        if (target.isIntersecting) {
          loadMore()
        }
      },
      { threshold: 0.1 }
    )

    if (loadingRef.current) {
      observer.observe(loadingRef.current)
    }

    observerRef.current = observer
    return () => observer.disconnect()
  }, [loadMore])

  return { loading, loadingRef }
}

const InfiniteScrollList = ({
  initialItems = [],
  fetchItems,
  renderItem,
  loadingComponent = <div>Loading...</div>,
  endComponent = <div>No more items</div>,
  errorComponent = <div>Error loading items</div>,
}) => {
  const [items, setItems] = useState(initialItems)
  const [hasNextPage, setHasNextPage] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)

  const fetchMore = useCallback(async () => {
    try {
      setError(null)
      const newItems = await fetchItems(page)
      
      if (newItems.length === 0) {
        setHasNextPage(false)
      } else {
        setItems(prev => [...prev, ...newItems])
        setPage(prev => prev + 1)
      }
    } catch (err) {
      setError(err)
    }
  }, [fetchItems, page])

  const { loading, loadingRef } = useInfiniteScroll({
    fetchMore,
    hasNextPage,
  })

  // Load initial items
  useEffect(() => {
    if (items.length === 0) {
      fetchMore()
    }
  }, [])

  if (error) {
    return errorComponent
  }

  return (
    <div className="infinite-scroll-list">
      {items.map((item, index) => renderItem(item, index))}
      
      {hasNextPage && (
        <div ref={loadingRef} className="loading-trigger">
          {loading && loadingComponent}
        </div>
      )}
      
      {!hasNextPage && !loading && endComponent}
    </div>
  )
}

// Usage
const InfiniteScrollExample = () => {
  const fetchItems = async (page) => {
    const response = await fetch(`/api/items?page=${page}&limit=20`)
    const data = await response.json()
    return data.items
  }

  return (
    <InfiniteScrollList
      fetchItems={fetchItems}
      renderItem={(item, index) => (
        <div key={item.id} className="item">
          <h3>{item.title}</h3>
          <p>{item.description}</p>
        </div>
      )}
      loadingComponent={<div className="spinner">Loading more...</div>}
      endComponent={<div className="end">You've reached the end!</div>}
    />
  )
}
{% endraw %}
```

## Virtualized Grid Implementation

```jsx
{% raw %}
const VirtualGrid = ({
  items,
  columns,
  rowHeight,
  columnWidth,
  containerWidth,
  containerHeight,
  renderItem,
  gap = 0,
}) => {
  const [scrollTop, setScrollTop] = useState(0)
  const [scrollLeft, setScrollLeft] = useState(0)

  const totalRows = Math.ceil(items.length / columns)
  const totalHeight = totalRows * (rowHeight + gap) - gap
  const totalWidth = columns * (columnWidth + gap) - gap

  // Calculate visible range
  const visibleRowStart = Math.max(0, Math.floor(scrollTop / (rowHeight + gap)) - 1)
  const visibleRowEnd = Math.min(
    totalRows - 1,
    Math.ceil((scrollTop + containerHeight) / (rowHeight + gap)) + 1
  )

  const visibleColStart = Math.max(0, Math.floor(scrollLeft / (columnWidth + gap)) - 1)
  const visibleColEnd = Math.min(
    columns - 1,
    Math.ceil((scrollLeft + containerWidth) / (columnWidth + gap)) + 1
  )

  const visibleItems = []
  for (let row = visibleRowStart; row <= visibleRowEnd; row++) {
    for (let col = visibleColStart; col <= visibleColEnd; col++) {
      const index = row * columns + col
      if (index < items.length) {
        visibleItems.push({
          item: items[index],
          index,
          row,
          col,
          x: col * (columnWidth + gap),
          y: row * (rowHeight + gap),
        })
      }
    }
  }

  const handleScroll = (e) => {
    setScrollTop(e.currentTarget.scrollTop)
    setScrollLeft(e.currentTarget.scrollLeft)
  }

  return (
    <div
      style={{
        width: containerWidth,
        height: containerHeight,
        overflow: 'auto',
      }}
      onScroll={handleScroll}
    >
      <div
        style={{
          width: totalWidth,
          height: totalHeight,
          position: 'relative',
        }}
      >
        {visibleItems.map(({ item, index, x, y }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              left: x,
              top: y,
              width: columnWidth,
              height: rowHeight,
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  )
}

// Usage
const VirtualGridExample = () => {
  const items = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
    color: `hsl(${(i * 137.5) % 360}, 70%, 50%)`,
  }))

  return (
    <VirtualGrid
      items={items}
      columns={5}
      rowHeight={120}
      columnWidth={150}
      containerWidth={800}
      containerHeight={400}
      gap={10}
      renderItem={(item) => (
        <div
          style={{
            background: item.color,
            borderRadius: '8px',
            padding: '10px',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            fontWeight: 'bold',
          }}
        >
          {item.name}
        </div>
      )}
    />
  )
}
{% endraw %}
```

## Horizontal Virtual Scrolling

```jsx
{% raw %}
const HorizontalVirtualList = ({
  items,
  itemWidth,
  containerWidth,
  containerHeight,
  renderItem,
  overscan = 3,
}) => {
  const [scrollLeft, setScrollLeft] = useState(0)

  const visibleStart = Math.max(0, Math.floor(scrollLeft / itemWidth) - overscan)
  const visibleEnd = Math.min(
    items.length - 1,
    Math.ceil((scrollLeft + containerWidth) / itemWidth) + overscan
  )

  const visibleItems = items.slice(visibleStart, visibleEnd + 1).map((item, index) => ({
    item,
    index: visibleStart + index,
  }))

  const totalWidth = items.length * itemWidth
  const offsetX = visibleStart * itemWidth

  const handleScroll = (e) => {
    setScrollLeft(e.currentTarget.scrollLeft)
  }

  return (
    <div
      style={{
        width: containerWidth,
        height: containerHeight,
        overflowX: 'auto',
        overflowY: 'hidden',
      }}
      onScroll={handleScroll}
    >
      <div style={{ width: totalWidth, height: '100%', position: 'relative' }}>
        <div
          style={{
            transform: `translateX(${offsetX}px)`,
            height: '100%',
            display: 'flex',
          }}
        >
          {visibleItems.map(({ item, index }) => (
            <div
              key={index}
              style={{
                width: itemWidth,
                height: '100%',
                flexShrink: 0,
              }}
            >
              {renderItem(item, index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
{% endraw %}
```

## Bidirectional Infinite Scroll

```jsx
const useBidirectionalInfiniteScroll = ({
  fetchOlder,
  fetchNewer,
  threshold = 200,
}) => {
  const [loading, setLoading] = useState({ older: false, newer: false })
  const [hasMore, setHasMore] = useState({ older: true, newer: true })
  const topSentinelRef = useRef()
  const bottomSentinelRef = useRef()

  const loadOlder = useCallback(async () => {
    if (loading.older || !hasMore.older) return

    setLoading(prev => ({ ...prev, older: true }))
    try {
      const items = await fetchOlder()
      if (items.length === 0) {
        setHasMore(prev => ({ ...prev, older: false }))
      }
    } finally {
      setLoading(prev => ({ ...prev, older: false }))
    }
  }, [loading.older, hasMore.older, fetchOlder])

  const loadNewer = useCallback(async () => {
    if (loading.newer || !hasMore.newer) return

    setLoading(prev => ({ ...prev, newer: true }))
    try {
      const items = await fetchNewer()
      if (items.length === 0) {
        setHasMore(prev => ({ ...prev, newer: false }))
      }
    } finally {
      setLoading(prev => ({ ...prev, newer: false }))
    }
  }, [loading.newer, hasMore.newer, fetchNewer])

  useEffect(() => {
    const topObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadOlder()
        }
      },
      { threshold: 0.1 }
    )

    const bottomObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadNewer()
        }
      },
      { threshold: 0.1 }
    )

    if (topSentinelRef.current) {
      topObserver.observe(topSentinelRef.current)
    }

    if (bottomSentinelRef.current) {
      bottomObserver.observe(bottomSentinelRef.current)
    }

    return () => {
      topObserver.disconnect()
      bottomObserver.disconnect()
    }
  }, [loadOlder, loadNewer])

  return {
    loading,
    hasMore,
    topSentinelRef,
    bottomSentinelRef,
  }
}

const BidirectionalInfiniteList = ({
  initialItems = [],
  fetchOlder,
  fetchNewer,
  renderItem,
  keyExtractor,
}) => {
  const [items, setItems] = useState(initialItems)
  const containerRef = useRef()

  const handleFetchOlder = useCallback(async () => {
    const oldItems = await fetchOlder(items[0]?.id)
    setItems(prev => [...oldItems, ...prev])
    return oldItems
  }, [fetchOlder, items])

  const handleFetchNewer = useCallback(async () => {
    const newItems = await fetchNewer(items[items.length - 1]?.id)
    setItems(prev => [...prev, ...newItems])
    return newItems
  }, [fetchNewer, items])

  const {
    loading,
    hasMore,
    topSentinelRef,
    bottomSentinelRef,
  } = useBidirectionalInfiniteScroll({
    fetchOlder: handleFetchOlder,
    fetchNewer: handleFetchNewer,
  })

  return (
    <div ref={containerRef} className="bidirectional-infinite-list">
      {hasMore.older && (
        <div ref={topSentinelRef} className="sentinel">
          {loading.older && <div>Loading older items...</div>}
        </div>
      )}

      {items.map((item, index) => (
        <div key={keyExtractor(item, index)}>
          {renderItem(item, index)}
        </div>
      ))}

      {hasMore.newer && (
        <div ref={bottomSentinelRef} className="sentinel">
          {loading.newer && <div>Loading newer items...</div>}
        </div>
      )}
    </div>
  )
}
```

## Performance Optimizations

### 1. Memoization and React.memo

```jsx
const VirtualItem = React.memo(({ item, style, onSelect }) => (
  <div style={style} onClick={() => onSelect(item)}>
    <h3>{item.title}</h3>
    <p>{item.description}</p>
  </div>
))

// Prevent unnecessary re-renders
const MemoizedVirtualList = React.memo(VirtualList, (prevProps, nextProps) => {
  return (
    prevProps.items.length === nextProps.items.length &&
    prevProps.itemHeight === nextProps.itemHeight &&
    prevProps.containerHeight === nextProps.containerHeight
  )
})
```

### 2. Throttling and Debouncing

```jsx
import { throttle, debounce } from 'lodash'

const useThrottledScroll = (callback, delay = 16) => {
  const throttledCallback = useCallback(
    throttle(callback, delay),
    [callback, delay]
  )

  useEffect(() => {
    return () => {
      throttledCallback.cancel()
    }
  }, [throttledCallback])

  return throttledCallback
}

const OptimizedVirtualList = (props) => {
  const [scrollTop, setScrollTop] = useState(0)
  
  const handleScroll = useThrottledScroll((e) => {
    setScrollTop(e.currentTarget.scrollTop)
  }, 16)

  return (
    <div onScroll={handleScroll}>
      {/* Virtual list content */}
    </div>
  )
}
```

### 3. Intersection Observer Optimization

```jsx
const useIntersectionObserver = (callback, options = {}) => {
  const targetRef = useRef()
  const observerRef = useRef()

  useEffect(() => {
    const observer = new IntersectionObserver(callback, {
      threshold: 0.1,
      rootMargin: '50px',
      ...options,
    })

    if (targetRef.current) {
      observer.observe(targetRef.current)
    }

    observerRef.current = observer
    return () => observer.disconnect()
  }, [callback, options])

  return targetRef
}
```

## Testing Virtualization

```jsx
{% raw %}
import { render, screen, fireEvent } from '@testing-library/react'
import { act } from '@testing-library/react-hooks'

describe('VirtualList', () => {
  const mockItems = Array.from({ length: 100 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
  }))

  test('renders only visible items', () => {
    render(
      <VirtualList
        items={mockItems}
        itemHeight={50}
        containerHeight={200}
        renderItem={(item) => <div>{item.name}</div>}
      />
    )

    // Should render approximately 4-5 visible items + overscan
    expect(screen.getAllByText(/Item \d+/)).toHaveLength(9) // 4 visible + 5 overscan
  })

  test('updates visible items on scroll', () => {
    const { container } = render(
      <VirtualList
        items={mockItems}
        itemHeight={50}
        containerHeight={200}
        renderItem={(item) => <div data-testid={`item-${item.id}`}>{item.name}</div>}
      />
    )

    const scrollContainer = container.firstChild

    act(() => {
      fireEvent.scroll(scrollContainer, { target: { scrollTop: 250 } })
    })

    // Should now show items starting from index 5
    expect(screen.getByTestId('item-5')).toBeInTheDocument()
    expect(screen.queryByTestId('item-0')).not.toBeInTheDocument()
  })
})

describe('InfiniteScroll', () => {
  test('loads more items when scrolled to bottom', async () => {
    const mockFetchItems = jest.fn()
      .mockResolvedValueOnce([{ id: 1, name: 'Item 1' }])
      .mockResolvedValueOnce([{ id: 2, name: 'Item 2' }])

    render(
      <InfiniteScrollList
        fetchItems={mockFetchItems}
        renderItem={(item) => <div>{item.name}</div>}
      />
    )

    // Wait for initial load
    await screen.findByText('Item 1')

    // Simulate intersection
    const trigger = document.querySelector('.loading-trigger')
    fireEvent(trigger, new Event('intersect'))

    await screen.findByText('Item 2')
    expect(mockFetchItems).toHaveBeenCalledTimes(2)
  })
})
{% endraw %}
```

## Accessibility Considerations

```jsx
{% raw %}
const AccessibleVirtualList = ({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  ariaLabel,
  announceItems = true,
}) => {
  const [scrollTop, setScrollTop] = useState(0)
  const [focusedIndex, setFocusedIndex] = useState(0)
  const containerRef = useRef()

  // Announce visible range to screen readers
  const { startIndex, endIndex } = getVisibleRange(scrollTop, itemHeight, containerHeight, items.length)
  
  useEffect(() => {
    if (announceItems) {
      const message = `Showing items ${startIndex + 1} to ${endIndex + 1} of ${items.length}`
      // Announce to screen reader (implementation depends on your a11y library)
      announceToScreenReader(message)
    }
  }, [startIndex, endIndex, items.length, announceItems])

  const handleKeyDown = (e) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setFocusedIndex(Math.min(focusedIndex + 1, items.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setFocusedIndex(Math.max(focusedIndex - 1, 0))
        break
      case 'Home':
        e.preventDefault()
        setFocusedIndex(0)
        break
      case 'End':
        e.preventDefault()
        setFocusedIndex(items.length - 1)
        break
    }
  }

  return (
    <div
      ref={containerRef}
      role="listbox"
      aria-label={ariaLabel}
      aria-rowcount={items.length}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      style={{ height: containerHeight, overflow: 'auto' }}
    >
      {/* Virtual list implementation */}
      <div
        role="option"
        aria-posinset={focusedIndex + 1}
        aria-setsize={items.length}
        aria-selected={true}
      >
        {/* Focused item */}
      </div>
    </div>
  )
}
{% endraw %}
```

## Conclusion

Virtualization and infinite scroll are essential patterns for handling large datasets efficiently. Key takeaways:

**Virtualization Benefits:**
- Dramatically improves performance with large datasets
- Reduces memory usage and DOM complexity
- Maintains smooth scrolling experience
- Scales to millions of items

**Implementation Strategies:**
- Choose between fixed-height and dynamic-height virtualization
- Implement proper overscan for smooth scrolling
- Use Intersection Observer for efficient scroll detection
- Optimize with memoization and throttling

**Best Practices:**
- Always consider accessibility requirements
- Implement proper error handling and loading states
- Test with real-world data sizes and network conditions
- Monitor performance metrics and optimize bottlenecks
- Consider using established libraries like react-window or react-virtualized for complex scenarios

These patterns are crucial for building performant applications that handle large amounts of data while maintaining excellent user experience.