# Accessibility & ARIA Patterns

## Table of Contents
1. [Accessibility Fundamentals](#accessibility-fundamentals)
2. [ARIA Roles and Properties](#aria-roles-and-properties)
3. [Focus Management](#focus-management)
4. [Keyboard Navigation](#keyboard-navigation)
5. [Screen Reader Support](#screen-reader-support)
6. [Accessible Form Patterns](#accessible-form-patterns)
7. [Complex Widget Accessibility](#complex-widget-accessibility)
8. [Testing Accessibility](#testing-accessibility)

---

## Accessibility Fundamentals

### Semantic HTML Foundation

```jsx
{% raw %}
{% raw %}
// Always start with semantic HTML
const AccessibleButton = ({ children, variant = 'primary', ...props }) => {
  return (
    <button 
      className={`btn btn--${variant}`}
      {...props}
    >
      {children}
    </button>
  )
}

// Proper heading hierarchy
const ArticleLayout = ({ title, subtitle, content, author }) => {
  return (
    <article>
      <header>
        <h1>{title}</h1>
        {subtitle && <h2>{subtitle}</h2>}
        <p>By <span className="author">{author}</span></p>
      </header>
      
      <main>
        {content}
      </main>
    </article>
  )
}

// Landmark roles for navigation
const PageLayout = ({ children }) => {
  return (
    <>
      <header role="banner">
        <nav role="navigation" aria-label="Main navigation">
          <NavMenu />
        </nav>
      </header>
      
      <main role="main">
        {children}
      </main>
      
      <aside role="complementary" aria-label="Related links">
        <Sidebar />
      </aside>
      
      <footer role="contentinfo">
        <FooterContent />
      </footer>
    </>
  )
}
{% endraw %}
{% endraw %}
```

### Color Contrast and Visual Accessibility

```jsx
import { useState, useEffect } from 'react'

// Hook for detecting user preferences
const useAccessibilityPreferences = () => {
  const [preferences, setPreferences] = useState({
    prefersReducedMotion: false,
    prefersHighContrast: false,
    prefersDarkMode: false,
  })
  
  useEffect(() => {
    const mediaQueries = {
      prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)'),
      prefersHighContrast: window.matchMedia('(prefers-contrast: high)'),
      prefersDarkMode: window.matchMedia('(prefers-color-scheme: dark)'),
    }
    
    const updatePreferences = () => {
      setPreferences({
        prefersReducedMotion: mediaQueries.prefersReducedMotion.matches,
        prefersHighContrast: mediaQueries.prefersHighContrast.matches,
        prefersDarkMode: mediaQueries.prefersDarkMode.matches,
      })
    }
    
    updatePreferences()
    
    Object.values(mediaQueries).forEach(mq => {
      mq.addEventListener('change', updatePreferences)
    })
    
    return () => {
      Object.values(mediaQueries).forEach(mq => {
        mq.removeEventListener('change', updatePreferences)
      })
    }
  }, [])
  
  return preferences
}

// Accessible color system
const ColorSystem = {
  // WCAG AA compliant color combinations
  primary: {
    background: '#0066cc',
    text: '#ffffff',
    contrast: 4.56, // AA compliant
  },
  secondary: {
    background: '#6c757d',
    text: '#ffffff',
    contrast: 4.54,
  },
  success: {
    background: '#28a745',
    text: '#ffffff',
    contrast: 4.52,
  },
  warning: {
    background: '#ffc107',
    text: '#212529',
    contrast: 4.58,
  },
  error: {
    background: '#dc3545',
    text: '#ffffff',
    contrast: 5.12,
  },
}

const AccessibleAlert = ({ type = 'info', children, ...props }) => {
  const colors = ColorSystem[type] || ColorSystem.primary
  const { prefersHighContrast } = useAccessibilityPreferences()
  
  const styles = {
    backgroundColor: colors.background,
    color: colors.text,
    padding: '12px 16px',
    borderRadius: '4px',
    border: prefersHighContrast ? '2px solid currentColor' : 'none',
  }
  
  return (
    <div
      role="alert"
      aria-live="polite"
      style={styles}
      {...props}
    >
      {children}
    </div>
  )
}
```

---

## ARIA Roles and Properties

### Essential ARIA Patterns

```jsx
{% raw %}
{% raw %}
// Accessible disclosure/dropdown
const DisclosurePattern = ({ trigger, children, id }) => {
  const [isOpen, setIsOpen] = useState(false)
  const triggerId = `${id}-trigger`
  const contentId = `${id}-content`
  
  return (
    <>
      <button
        id={triggerId}
        aria-expanded={isOpen}
        aria-controls={contentId}
        onClick={() => setIsOpen(!isOpen)}
        className="disclosure-trigger"
      >
        {trigger}
        <span aria-hidden="true">{isOpen ? '−' : '+'}</span>
      </button>
      
      <div
        id={contentId}
        role="region"
        aria-labelledby={triggerId}
        hidden={!isOpen}
        className="disclosure-content"
      >
        {children}
      </div>
    </>
  )
}

// Accessible modal dialog
const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children,
  initialFocus,
  returnFocus = true 
}) => {
  const modalRef = useRef()
  const previousActiveElement = useRef()
  
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement
      
      // Trap focus within modal
      const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
          onClose()
        }
        
        if (e.key === 'Tab') {
          trapFocus(e, modalRef.current)
        }
      }
      
      document.addEventListener('keydown', handleKeyDown)
      
      // Focus management
      if (initialFocus) {
        initialFocus.current?.focus()
      } else {
        modalRef.current?.focus()
      }
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden'
      
      return () => {
        document.removeEventListener('keydown', handleKeyDown)
        document.body.style.overflow = 'auto'
        
        if (returnFocus && previousActiveElement.current) {
          previousActiveElement.current.focus()
        }
      }
    }
  }, [isOpen, onClose, initialFocus, returnFocus])
  
  const trapFocus = (e, container) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]
    
    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        lastElement?.focus()
        e.preventDefault()
      }
    } else {
      if (document.activeElement === lastElement) {
        firstElement?.focus()
        e.preventDefault()
      }
    }
  }
  
  if (!isOpen) return null
  
  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose()
        }
      }}
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby="modal-description"
        className="modal-content"
        tabIndex={-1}
      >
        <header className="modal-header">
          <h2 id="modal-title">{title}</h2>
          <button
            onClick={onClose}
            aria-label="Close dialog"
            className="modal-close"
          >
            <span aria-hidden="true">×</span>
          </button>
        </header>
        
        <div id="modal-description" className="modal-body">
          {children}
        </div>
      </div>
    </div>
  )
}

// Accessible tooltip
const Tooltip = ({ children, content, id, placement = 'top' }) => {
  const [isVisible, setIsVisible] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const tooltipId = `${id}-tooltip`
  
  const showTooltip = () => setIsVisible(true)
  const hideTooltip = () => {
    if (!isFocused) {
      setIsVisible(false)
    }
  }
  
  return (
    <>
      <span
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={() => {
          setIsFocused(true)
          showTooltip()
        }}
        onBlur={() => {
          setIsFocused(false)
          hideTooltip()
        }}
        aria-describedby={isVisible ? tooltipId : undefined}
        tabIndex={0}
      >
        {children}
      </span>
      
      {isVisible && (
        <div
          id={tooltipId}
          role="tooltip"
          className={`tooltip tooltip--${placement}`}
          aria-hidden={!isVisible}
        >
          {content}
        </div>
      )}
    </>
  )
}
{% endraw %}
{% endraw %}
```

### ARIA Live Regions

```jsx
{% raw %}
{% raw %}
// Status announcements
const StatusAnnouncer = () => {
  const [message, setMessage] = useState('')
  const [priority, setPriority] = useState('polite')
  
  const announce = (text, isUrgent = false) => {
    setPriority(isUrgent ? 'assertive' : 'polite')
    setMessage(text)
    
    // Clear message after announcement
    setTimeout(() => setMessage(''), 1000)
  }
  
  // Expose announce function globally
  useEffect(() => {
    window.announceToScreenReader = announce
    
    return () => {
      delete window.announceToScreenReader
    }
  }, [])
  
  return (
    <div
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  )
}

// Loading states with proper announcements
const AsyncButton = ({ onClick, children, loadingText = 'Loading...' }) => {
  const [isLoading, setIsLoading] = useState(false)
  
  const handleClick = async () => {
    setIsLoading(true)
    
    try {
      await onClick()
      window.announceToScreenReader?.('Action completed successfully')
    } catch (error) {
      window.announceToScreenReader?.('Action failed. Please try again.', true)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      aria-describedby={isLoading ? 'loading-status' : undefined}
    >
      {isLoading ? (
        <>
          <span aria-hidden="true">⏳</span>
          {loadingText}
        </>
      ) : (
        children
      )}
      
      {isLoading && (
        <span id="loading-status" className="sr-only" aria-live="polite">
          Please wait, {loadingText}
        </span>
      )}
    </button>
  )
}

// Dynamic content updates
const DynamicList = ({ items }) => {
  const [previousCount, setPreviousCount] = useState(items.length)
  
  useEffect(() => {
    const currentCount = items.length
    const difference = currentCount - previousCount
    
    if (difference !== 0) {
      const action = difference > 0 ? 'added' : 'removed'
      const count = Math.abs(difference)
      const itemText = count === 1 ? 'item' : 'items'
      
      window.announceToScreenReader?.(
        `${count} ${itemText} ${action}. Total: ${currentCount} items.`
      )
    }
    
    setPreviousCount(currentCount)
  }, [items.length, previousCount])
  
  return (
    <ul aria-label={`List with ${items.length} items`}>
      {items.map((item, index) => (
        <li key={item.id} aria-setsize={items.length} aria-posinset={index + 1}>
          {item.content}
        </li>
      ))}
    </ul>
  )
}
{% endraw %}
{% endraw %}
```

---

## Focus Management

### Focus Trap Implementation

```jsx
const useFocusTrap = (isActive) => {
  const containerRef = useRef()
  
  useEffect(() => {
    if (!isActive || !containerRef.current) return
    
    const container = containerRef.current
    const focusableSelector = `
      button:not([disabled]),
      [href],
      input:not([disabled]),
      select:not([disabled]),
      textarea:not([disabled]),
      [tabindex]:not([tabindex="-1"]):not([disabled])
    `
    
    const getFocusableElements = () => {
      return container.querySelectorAll(focusableSelector)
    }
    
    const handleKeyDown = (e) => {
      if (e.key !== 'Tab') return
      
      const focusableElements = getFocusableElements()
      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]
      
      if (e.shiftKey) {
        if (document.activeElement === firstElement || !container.contains(document.activeElement)) {
          lastElement?.focus()
          e.preventDefault()
        }
      } else {
        if (document.activeElement === lastElement || !container.contains(document.activeElement)) {
          firstElement?.focus()
          e.preventDefault()
        }
      }
    }
    
    container.addEventListener('keydown', handleKeyDown)
    
    // Initial focus
    const firstFocusable = getFocusableElements()[0]
    firstFocusable?.focus()
    
    return () => {
      container.removeEventListener('keydown', handleKeyDown)
    }
  }, [isActive])
  
  return containerRef
}

// Focus restoration
const useFocusRestore = () => {
  const previousActiveElement = useRef()
  
  const saveFocus = () => {
    previousActiveElement.current = document.activeElement
  }
  
  const restoreFocus = () => {
    if (previousActiveElement.current && 
        document.contains(previousActiveElement.current)) {
      previousActiveElement.current.focus()
    }
  }
  
  return { saveFocus, restoreFocus }
}

// Skip links for keyboard navigation
const SkipLinks = () => {
  return (
    <nav className="skip-links" aria-label="Skip links">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#navigation" className="skip-link">
        Skip to navigation
      </a>
      <a href="#search" className="skip-link">
        Skip to search
      </a>
    </nav>
  )
}
```

### Roving Tabindex Pattern

```jsx
// Toolbar with roving tabindex
const Toolbar = ({ children, orientation = 'horizontal' }) => {
  const [activeIndex, setActiveIndex] = useState(0)
  const itemsRef = useRef([])
  
  const isVertical = orientation === 'vertical'
  const nextKey = isVertical ? 'ArrowDown' : 'ArrowRight'
  const prevKey = isVertical ? 'ArrowUp' : 'ArrowLeft'
  
  const handleKeyDown = (e) => {
    const currentIndex = activeIndex
    let newIndex = currentIndex
    
    switch (e.key) {
      case nextKey:
        newIndex = (currentIndex + 1) % itemsRef.current.length
        e.preventDefault()
        break
      case prevKey:
        newIndex = currentIndex === 0 ? itemsRef.current.length - 1 : currentIndex - 1
        e.preventDefault()
        break
      case 'Home':
        newIndex = 0
        e.preventDefault()
        break
      case 'End':
        newIndex = itemsRef.current.length - 1
        e.preventDefault()
        break
      default:
        return
    }
    
    setActiveIndex(newIndex)
    itemsRef.current[newIndex]?.focus()
  }
  
  return (
    <div
      role="toolbar"
      aria-orientation={orientation}
      onKeyDown={handleKeyDown}
      className="toolbar"
    >
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child, {
          ref: (el) => { itemsRef.current[index] = el },
          tabIndex: index === activeIndex ? 0 : -1,
          'aria-posinset': index + 1,
          'aria-setsize': React.Children.count(children),
        })
      )}
    </div>
  )
}

// Menu with keyboard navigation
const Menu = ({ trigger, children }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const menuRef = useRef()
  const itemsRef = useRef([])
  
  const handleTriggerKeyDown = (e) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
      case 'ArrowDown':
        e.preventDefault()
        setIsOpen(true)
        setActiveIndex(0)
        break
      case 'ArrowUp':
        e.preventDefault()
        setIsOpen(true)
        setActiveIndex(itemsRef.current.length - 1)
        break
    }
  }
  
  const handleMenuKeyDown = (e) => {
    switch (e.key) {
      case 'Escape':
        setIsOpen(false)
        setActiveIndex(-1)
        break
      case 'ArrowDown':
        e.preventDefault()
        setActiveIndex((prev) => (prev + 1) % itemsRef.current.length)
        break
      case 'ArrowUp':
        e.preventDefault()
        setActiveIndex((prev) => prev === 0 ? itemsRef.current.length - 1 : prev - 1)
        break
      case 'Home':
        e.preventDefault()
        setActiveIndex(0)
        break
      case 'End':
        e.preventDefault()
        setActiveIndex(itemsRef.current.length - 1)
        break
    }
  }
  
  useEffect(() => {
    if (isOpen && activeIndex >= 0) {
      itemsRef.current[activeIndex]?.focus()
    }
  }, [isOpen, activeIndex])
  
  return (
    <div className="menu-container">
      <button
        aria-haspopup="true"
        aria-expanded={isOpen}
        onKeyDown={handleTriggerKeyDown}
        onClick={() => setIsOpen(!isOpen)}
      >
        {trigger}
      </button>
      
      {isOpen && (
        <ul
          ref={menuRef}
          role="menu"
          onKeyDown={handleMenuKeyDown}
          className="menu"
        >
          {React.Children.map(children, (child, index) =>
            React.cloneElement(child, {
              ref: (el) => { itemsRef.current[index] = el },
              role: 'menuitem',
              tabIndex: -1,
            })
          )}
        </ul>
      )}
    </div>
  )
}
```

This comprehensive guide covers essential accessibility patterns and ARIA implementation for creating inclusive React applications.