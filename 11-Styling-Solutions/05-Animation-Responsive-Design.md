# Animation & Responsive Design Patterns

## Table of Contents
1. [CSS Animation Fundamentals](#css-animation-fundamentals)
2. [React Animation Libraries](#react-animation-libraries)
3. [Responsive Design Strategies](#responsive-design-strategies)
4. [Mobile-First Patterns](#mobile-first-patterns)
5. [Performance Considerations](#performance-considerations)
6. [Advanced Animation Patterns](#advanced-animation-patterns)
7. [Accessibility in Animations](#accessibility-in-animations)
8. [Real-World Examples](#real-world-examples)

---

## CSS Animation Fundamentals

### Modern CSS Animations

```css
/* CSS Variables for animations */
:root {
  --animation-duration-fast: 150ms;
  --animation-duration-normal: 250ms;
  --animation-duration-slow: 350ms;
  --animation-easing-ease-in: cubic-bezier(0.4, 0, 1, 1);
  --animation-easing-ease-out: cubic-bezier(0, 0, 0.2, 1);
  --animation-easing-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --animation-easing-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

/* Keyframe animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

/* Animation utility classes */
.animate-fade-in {
  animation: fadeIn var(--animation-duration-normal) var(--animation-easing-ease-out) both;
}

.animate-slide-in-left {
  animation: slideInLeft var(--animation-duration-normal) var(--animation-easing-ease-out) both;
}

.animate-scale-in {
  animation: scaleIn var(--animation-duration-fast) var(--animation-easing-ease-out) both;
}

.animate-shimmer {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: shimmer 1.5s infinite;
}

/* Hover animations */
.hover-lift {
  transition: transform var(--animation-duration-fast) var(--animation-easing-ease-out);
}

.hover-lift:hover {
  transform: translateY(-2px);
}

.hover-scale {
  transition: transform var(--animation-duration-fast) var(--animation-easing-ease-out);
}

.hover-scale:hover {
  transform: scale(1.05);
}

/* Focus animations */
.focus-ring {
  transition: box-shadow var(--animation-duration-fast) var(--animation-easing-ease-out);
}

.focus-ring:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
}
```

### React CSS Animation Integration

```jsx
{% raw %}
{% raw %}
import React, { useState, useEffect } from 'react'
import './animations.css'

// Staggered list animations
const StaggeredList = ({ items }) => {
  const [isVisible, setIsVisible] = useState(false)
  
  useEffect(() => {
    setIsVisible(true)
  }, [])
  
  return (
    <div className="staggered-list">
      {items.map((item, index) => (
        <div
          key={item.id}
          className={`list-item ${isVisible ? 'animate-fade-in' : ''}`}
          style={{
            animationDelay: `${index * 50}ms`,
          }}
        >
          {item.content}
        </div>
      ))}
    </div>
  )
}

// Loading skeleton with shimmer
const SkeletonLoader = ({ lines = 3, width = '100%' }) => {
  return (
    <div className="skeleton-container">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="skeleton-line animate-shimmer"
          style={{
            width: index === lines - 1 ? '60%' : width,
            height: '1rem',
            marginBottom: '0.5rem',
            borderRadius: '0.25rem',
          }}
        />
      ))}
    </div>
  )
}

// Page transition animations
const PageTransition = ({ children, isVisible }) => {
  return (
    <div
      className={`page-transition ${
        isVisible ? 'animate-fade-in' : 'animate-fade-out'
      }`}
    >
      {children}
    </div>
  )
}

// CSS custom properties for dynamic animations
const DynamicAnimationComponent = ({ color, duration, delay }) => {
  const style = {
    '--animation-color': color,
    '--animation-duration': `${duration}ms`,
    '--animation-delay': `${delay}ms`,
  }
  
  return (
    <div className="dynamic-animation" style={style}>
      Animated content
    </div>
  )
}
{% endraw %}
{% endraw %}
```

---

## React Animation Libraries

### Framer Motion Integration

```jsx
import { motion, AnimatePresence, useAnimation, useInView } from 'framer-motion'
import { useRef, useEffect } from 'react'

// Basic motion components
const FadeInBox = ({ children, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay,
        ease: [0.25, 0.25, 0, 1]
      }}
    >
      {children}
    </motion.div>
  )
}

// Staggered children animations
const StaggerContainer = ({ children }) => {
  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3,
      },
    },
  }
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5 }
    },
  }
  
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {React.Children.map(children, (child, index) => (
        <motion.div key={index} variants={itemVariants}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  )
}

// Page transitions with AnimatePresence
const PageTransitions = ({ children, pathname }) => {
  const pageVariants = {
    initial: {
      opacity: 0,
      x: '-100vw',
    },
    in: {
      opacity: 1,
      x: 0,
    },
    out: {
      opacity: 0,
      x: '100vw',
    },
  }
  
  const pageTransition = {
    type: 'tween',
    ease: 'anticipate',
    duration: 0.5,
  }
  
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial="initial"
        animate="in"
        exit="out"
        variants={pageVariants}
        transition={pageTransition}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

// Scroll-triggered animations
const ScrollTriggeredAnimation = ({ children }) => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })
  const controls = useAnimation()
  
  useEffect(() => {
    if (isInView) {
      controls.start('visible')
    }
  }, [isInView, controls])
  
  return (
    <motion.div
      ref={ref}
      animate={controls}
      initial="hidden"
      variants={{
        hidden: { opacity: 0, scale: 0.8 },
        visible: { 
          opacity: 1, 
          scale: 1,
          transition: { duration: 0.6, ease: 'easeOut' }
        },
      }}
    >
      {children}
    </motion.div>
  )
}

// Gesture animations
const DraggableCard = ({ children }) => {
  return (
    <motion.div
      drag
      dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
      dragElastic={0.2}
      whileDrag={{ scale: 1.05, rotate: 5 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="draggable-card"
    >
      {children}
    </motion.div>
  )
}

// Complex animation sequences
const ComplexAnimationSequence = () => {
  const controls = useAnimation()
  
  const runSequence = async () => {
    await controls.start({
      scale: 1.2,
      transition: { duration: 0.3 }
    })
    
    await controls.start({
      rotate: 360,
      transition: { duration: 0.5 }
    })
    
    await controls.start({
      scale: 1,
      rotate: 0,
      transition: { duration: 0.3 }
    })
  }
  
  return (
    <motion.div
      animate={controls}
      onClick={runSequence}
      className="complex-animation-trigger"
    >
      Click me for sequence
    </motion.div>
  )
}
```

### React Spring Animations

```jsx
{% raw %}
{% raw %}
import { useSpring, animated, useTransition, useChain, useSpringRef } from '@react-spring/web'
import { useState } from 'react'

// Basic spring animation
const SpringBox = ({ isVisible }) => {
  const styles = useSpring({
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? 'translateY(0px)' : 'translateY(-40px)',
    config: { tension: 300, friction: 30 },
  })
  
  return (
    <animated.div style={styles}>
      Spring animated content
    </animated.div>
  )
}

// List transitions
const SpringList = ({ items }) => {
  const transitions = useTransition(items, {
    from: { opacity: 0, transform: 'translateX(-100%)' },
    enter: { opacity: 1, transform: 'translateX(0%)' },
    leave: { opacity: 0, transform: 'translateX(100%)' },
    config: { tension: 200, friction: 25 },
  })
  
  return (
    <div className="spring-list">
      {transitions((style, item) => (
        <animated.div style={style} className="spring-list-item">
          {item.content}
        </animated.div>
      ))}
    </div>
  )
}

// Chained animations
const ChainedAnimations = ({ trigger }) => {
  const springRef = useSpringRef()
  const transitionRef = useSpringRef()
  
  const springs = useSpring({
    ref: springRef,
    from: { scale: 0, opacity: 0 },
    to: { scale: trigger ? 1 : 0, opacity: trigger ? 1 : 0 },
  })
  
  const transitions = useTransition(trigger ? ['item1', 'item2', 'item3'] : [], {
    ref: transitionRef,
    from: { opacity: 0, transform: 'translateY(-20px)' },
    enter: { opacity: 1, transform: 'translateY(0px)' },
    leave: { opacity: 0, transform: 'translateY(20px)' },
    trail: 100,
  })
  
  useChain(trigger ? [springRef, transitionRef] : [transitionRef, springRef], [0, 0.3])
  
  return (
    <animated.div style={springs}>
      {transitions((style, item) => (
        <animated.div style={style}>
          {item}
        </animated.div>
      ))}
    </animated.div>
  )
}

// Physics-based animations
const PhysicsAnimation = () => {
  const [isActive, setIsActive] = useState(false)
  
  const { x, opacity } = useSpring({
    x: isActive ? 200 : 0,
    opacity: isActive ? 1 : 0.3,
    config: {
      mass: 1,
      tension: 180,
      friction: 12,
      clamp: true,
    },
  })
  
  return (
    <animated.div
      style={{
        transform: x.to(x => `translateX(${x}px)`),
        opacity,
      }}
      onClick={() => setIsActive(!isActive)}
    >
      Physics-based movement
    </animated.div>
  )
}
{% endraw %}
{% endraw %}
```

---

## Responsive Design Strategies

### Container Queries

```css
/* Container queries for component-based responsive design */
.card-container {
  container-type: inline-size;
  container-name: card;
}

.card {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
}

/* Component responds to its container, not viewport */
@container card (min-width: 300px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1rem;
  }
  
  .card-image {
    aspect-ratio: 1;
  }
}

@container card (min-width: 500px) {
  .card {
    padding: 2rem;
  }
  
  .card-title {
    font-size: 1.5rem;
  }
}

/* Container query units */
.responsive-text {
  font-size: 4cqw; /* 4% of container width */
  line-height: 6cqh; /* 6% of container height */
}
```

### React Responsive Hooks

```jsx
{% raw %}
{% raw %}
import { useState, useEffect } from 'react'

// Custom responsive hooks
const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false)
  
  useEffect(() => {
    const media = window.matchMedia(query)
    
    if (media.matches !== matches) {
      setMatches(media.matches)
    }
    
    const listener = () => setMatches(media.matches)
    media.addEventListener('change', listener)
    
    return () => media.removeEventListener('change', listener)
  }, [matches, query])
  
  return matches
}

const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState('mobile')
  
  useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth
      
      if (width < 640) {
        setBreakpoint('mobile')
      } else if (width < 768) {
        setBreakpoint('sm')
      } else if (width < 1024) {
        setBreakpoint('md')
      } else if (width < 1280) {
        setBreakpoint('lg')
      } else {
        setBreakpoint('xl')
      }
    }
    
    updateBreakpoint()
    window.addEventListener('resize', updateBreakpoint)
    
    return () => window.removeEventListener('resize', updateBreakpoint)
  }, [])
  
  return breakpoint
}

const useViewportSize = () => {
  const [size, setSize] = useState({ width: 0, height: 0 })
  
  useEffect(() => {
    const updateSize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      })
    }
    
    updateSize()
    window.addEventListener('resize', updateSize)
    
    return () => window.removeEventListener('resize', updateSize)
  }, [])
  
  return size
}

// Responsive components
const ResponsiveGrid = ({ children }) => {
  const breakpoint = useBreakpoint()
  
  const gridConfig = {
    mobile: { columns: 1, gap: '1rem' },
    sm: { columns: 2, gap: '1rem' },
    md: { columns: 3, gap: '1.5rem' },
    lg: { columns: 4, gap: '2rem' },
    xl: { columns: 5, gap: '2rem' },
  }
  
  const config = gridConfig[breakpoint]
  
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${config.columns}, 1fr)`,
        gap: config.gap,
      }}
    >
      {children}
    </div>
  )
}

const ResponsiveNavigation = () => {
  const isMobile = useMediaQuery('(max-width: 768px)')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  if (isMobile) {
    return (
      <nav className="mobile-nav">
        <button 
          className="menu-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          ☰
        </button>
        
        {mobileMenuOpen && (
          <div className="mobile-menu">
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
          </div>
        )}
      </nav>
    )
  }
  
  return (
    <nav className="desktop-nav">
      <a href="/">Home</a>
      <a href="/about">About</a>
      <a href="/contact">Contact</a>
    </nav>
  )
}

// Responsive image component
const ResponsiveImage = ({ src, alt, sizes }) => {
  const { width } = useViewportSize()
  
  const getSrcSet = () => {
    return Object.entries(sizes)
      .map(([size, url]) => `${url} ${size}w`)
      .join(', ')
  }
  
  const getSizes = () => {
    if (width < 640) return '100vw'
    if (width < 1024) return '50vw'
    return '33vw'
  }
  
  return (
    <img
      src={src}
      alt={alt}
      srcSet={getSrcSet()}
      sizes={getSizes()}
      loading="lazy"
      style={{ width: '100%', height: 'auto' }}
    />
  )
}
{% endraw %}
{% endraw %}
```

---

## Mobile-First Patterns

### Progressive Enhancement CSS

```css
/* Mobile-first base styles */
.component {
  padding: 1rem;
  font-size: 1rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.component-grid {
  display: block;
}

.component-item {
  margin-bottom: 1rem;
  padding: 0.75rem;
}

/* Enhanced styles for larger screens */
@media (min-width: 640px) {
  .component {
    padding: 1.5rem;
    font-size: 1.125rem;
  }
  
  .component-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .component-item {
    margin-bottom: 0;
    padding: 1rem;
  }
}

@media (min-width: 1024px) {
  .component {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .component-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
  
  .component-item {
    padding: 1.5rem;
    transition: transform 0.2s ease;
  }
  
  .component-item:hover {
    transform: translateY(-2px);
  }
}
```

### Touch-Friendly Interactions

```jsx
{% raw %}
{% raw %}
import React, { useState, useRef } from 'react'

// Touch gesture handler
const useTouchGestures = () => {
  const [touchStart, setTouchStart] = useState(null)
  const [touchEnd, setTouchEnd] = useState(null)
  
  const minSwipeDistance = 50
  
  const onTouchStart = (e) => {
    setTouchEnd(null)
    setTouchStart(e.targetTouches[0].clientX)
  }
  
  const onTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX)
  }
  
  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return
    
    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > minSwipeDistance
    const isRightSwipe = distance < -minSwipeDistance
    
    return { isLeftSwipe, isRightSwipe }
  }
  
  return { onTouchStart, onTouchMove, onTouchEnd }
}

// Touch-friendly button component
const TouchButton = ({ children, onPress, ...props }) => {
  const [isPressed, setIsPressed] = useState(false)
  
  const handleTouchStart = () => {
    setIsPressed(true)
  }
  
  const handleTouchEnd = () => {
    setIsPressed(false)
    onPress?.()
  }
  
  return (
    <button
      className={`touch-button ${isPressed ? 'pressed' : ''}`}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onMouseDown={handleTouchStart}
      onMouseUp={handleTouchEnd}
      onMouseLeave={() => setIsPressed(false)}
      style={{
        minHeight: '44px', // iOS recommended touch target
        minWidth: '44px',
        padding: '12px 16px',
        border: 'none',
        borderRadius: '8px',
        fontSize: '16px', // Prevents zoom on iOS
        background: isPressed ? '#007bff' : '#0056b3',
        color: 'white',
        transform: isPressed ? 'scale(0.98)' : 'scale(1)',
        transition: 'all 0.1s ease',
      }}
      {...props}
    >
      {children}
    </button>
  )
}

// Swipeable card component
const SwipeableCard = ({ children, onSwipeLeft, onSwipeRight }) => {
  const gestures = useTouchGestures()
  
  const handleTouchEnd = () => {
    const result = gestures.onTouchEnd()
    if (!result) return
    
    if (result.isLeftSwipe) {
      onSwipeLeft?.()
    } else if (result.isRightSwipe) {
      onSwipeRight?.()
    }
  }
  
  return (
    <div
      className="swipeable-card"
      onTouchStart={gestures.onTouchStart}
      onTouchMove={gestures.onTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{
        userSelect: 'none',
        touchAction: 'pan-x',
      }}
    >
      {children}
    </div>
  )
}

// Mobile-optimized modal
const MobileModal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef()
  
  useEffect(() => {
    if (isOpen) {
      // Prevent body scroll
      document.body.style.overflow = 'hidden'
      // Focus management
      modalRef.current?.focus()
    } else {
      document.body.style.overflow = 'auto'
    }
    
    return () => {
      document.body.style.overflow = 'auto'
    }
  }, [isOpen])
  
  if (!isOpen) return null
  
  return (
    <div className="mobile-modal-overlay">
      <div
        ref={modalRef}
        className="mobile-modal"
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          maxHeight: '90vh',
          background: 'white',
          borderRadius: '16px 16px 0 0',
          padding: '1rem',
          transform: isOpen ? 'translateY(0)' : 'translateY(100%)',
          transition: 'transform 0.3s ease',
        }}
        tabIndex={-1}
      >
        <div className="modal-handle">
          <div style={{
            width: '40px',
            height: '4px',
            background: '#ccc',
            borderRadius: '2px',
            margin: '0 auto 1rem',
          }} />
        </div>
        
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'none',
            border: 'none',
            fontSize: '24px',
          }}
        >
          ×
        </button>
        
        {children}
      </div>
    </div>
  )
}
{% endraw %}
{% endraw %}
```

---

## Performance Considerations

### Animation Performance Optimization

```jsx
import { useMemo, useCallback } from 'react'

// GPU-accelerated animations
const GPUAnimatedComponent = ({ isVisible }) => {
  const animationStyles = useMemo(() => ({
    transform: isVisible ? 'translateZ(0) scale(1)' : 'translateZ(0) scale(0.95)',
    opacity: isVisible ? 1 : 0,
    // Force GPU acceleration
    willChange: 'transform, opacity',
    backfaceVisibility: 'hidden',
    transition: 'transform 0.3s ease, opacity 0.3s ease',
  }), [isVisible])
  
  return (
    <div style={animationStyles}>
      GPU accelerated content
    </div>
  )
}

// Intersection Observer for scroll animations
const useIntersectionObserver = (options = {}) => {
  const [isIntersecting, setIsIntersecting] = useState(false)
  const ref = useRef()
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting)
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options,
      }
    )
    
    if (ref.current) {
      observer.observe(ref.current)
    }
    
    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [options])
  
  return [ref, isIntersecting]
}

const ScrollTriggeredComponent = ({ children }) => {
  const [ref, isVisible] = useIntersectionObserver()
  
  return (
    <div
      ref={ref}
      style={{
        transform: isVisible ? 'translateY(0)' : 'translateY(50px)',
        opacity: isVisible ? 1 : 0,
        transition: 'transform 0.6s ease, opacity 0.6s ease',
      }}
    >
      {children}
    </div>
  )
}

// Debounced resize handler
const useDebouncedResize = (callback, delay = 250) => {
  const timeoutRef = useRef()
  
  useEffect(() => {
    const handleResize = () => {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(callback, delay)
    }
    
    window.addEventListener('resize', handleResize)
    
    return () => {
      window.removeEventListener('resize', handleResize)
      clearTimeout(timeoutRef.current)
    }
  }, [callback, delay])
}

// Reduced motion support
const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)
    
    const handler = () => setPrefersReducedMotion(mediaQuery.matches)
    mediaQuery.addEventListener('change', handler)
    
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])
  
  return prefersReducedMotion
}

const MotionAwareComponent = ({ children }) => {
  const prefersReducedMotion = useReducedMotion()
  
  const animationProps = prefersReducedMotion
    ? {}
    : {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.5 },
      }
  
  return (
    <motion.div {...animationProps}>
      {children}
    </motion.div>
  )
}
```

---

## Advanced Animation Patterns

### Shared Element Transitions

```jsx
{% raw %}
{% raw %}
import { motion, AnimateSharedLayout } from 'framer-motion'

const SharedElementExample = () => {
  const [selectedId, setSelectedId] = useState(null)
  const items = [
    { id: 1, title: 'Item 1', content: 'Content 1' },
    { id: 2, title: 'Item 2', content: 'Content 2' },
    { id: 3, title: 'Item 3', content: 'Content 3' },
  ]
  
  return (
    <div className="shared-element-container">
      {items.map(item => (
        <motion.div
          key={item.id}
          layoutId={item.id}
          onClick={() => setSelectedId(item.id)}
          className="shared-element-item"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <motion.h3 layoutId={`title-${item.id}`}>
            {item.title}
          </motion.h3>
        </motion.div>
      ))}
      
      <AnimatePresence>
        {selectedId && (
          <motion.div
            layoutId={selectedId}
            className="shared-element-expanded"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.h3 layoutId={`title-${selectedId}`}>
              {items.find(item => item.id === selectedId)?.title}
            </motion.h3>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              {items.find(item => item.id === selectedId)?.content}
            </motion.p>
            <motion.button
              onClick={() => setSelectedId(null)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              Close
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
{% endraw %}
{% endraw %}
```

### Morphing Animations

```jsx
// SVG morphing animation
const MorphingIcon = ({ isExpanded }) => {
  const pathVariants = {
    collapsed: {
      d: "M3 12h18m-9-9v18",
    },
    expanded: {
      d: "M6 18L18 6M6 6l12 12",
    },
  }
  
  return (
    <motion.svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <motion.path
        variants={pathVariants}
        animate={isExpanded ? "expanded" : "collapsed"}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      />
    </motion.svg>
  )
}

// Shape morphing
const MorphingShape = ({ shape }) => {
  const shapeVariants = {
    circle: {
      borderRadius: "50%",
      rotate: 0,
    },
    square: {
      borderRadius: "0%",
      rotate: 45,
    },
    rounded: {
      borderRadius: "25%",
      rotate: 90,
    },
  }
  
  return (
    <motion.div
      className="morphing-shape"
      variants={shapeVariants}
      animate={shape}
      transition={{ 
        duration: 0.5, 
        ease: "easeInOut",
        type: "spring",
        stiffness: 100,
      }}
      style={{
        width: 100,
        height: 100,
        background: 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)',
      }}
    />
  )
}
```

---

## Accessibility in Animations

### Accessible Animation Patterns

```jsx
// Respect user preferences
const AccessibleAnimation = ({ children, ...animationProps }) => {
  const prefersReducedMotion = useReducedMotion()
  
  // Disable animations for users who prefer reduced motion
  const safeAnimationProps = prefersReducedMotion
    ? { initial: false, animate: false, transition: { duration: 0 } }
    : animationProps
  
  return (
    <motion.div {...safeAnimationProps}>
      {children}
    </motion.div>
  )
}

// Focus management during animations
const AccessibleModal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef()
  const previousFocusRef = useRef()
  
  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement
      // Wait for animation to complete before focusing
      setTimeout(() => {
        modalRef.current?.focus()
      }, 300)
    } else {
      // Return focus to previous element
      previousFocusRef.current?.focus()
    }
  }, [isOpen])
  
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.3 }}
          className="modal-overlay"
        >
          <div
            ref={modalRef}
            className="modal-content"
            role="dialog"
            aria-modal="true"
            tabIndex={-1}
          >
            {children}
            <button onClick={onClose} aria-label="Close modal">
              ×
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Screen reader friendly loading states
const AccessibleLoader = ({ isLoading, children }) => {
  return (
    <div>
      {isLoading && (
        <div
          role="status"
          aria-live="polite"
          aria-label="Loading content"
        >
          <motion.div
            className="spinner"
            animate={{ rotate: 360 }}
            transition={{ 
              duration: 1, 
              repeat: Infinity, 
              ease: "linear" 
            }}
          />
          <span className="sr-only">Loading...</span>
        </div>
      )}
      
      <div aria-hidden={isLoading}>
        {children}
      </div>
    </div>
  )
}
```

---

## Real-World Examples

### E-commerce Product Gallery

```jsx
{% raw %}
{% raw %}
const ProductGallery = ({ products }) => {
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [filter, setFilter] = useState('all')
  
  const filteredProducts = products.filter(product => 
    filter === 'all' || product.category === filter
  )
  
  return (
    <div className="product-gallery">
      {/* Filter buttons */}
      <div className="filter-buttons">
        {['all', 'electronics', 'clothing', 'books'].map(category => (
          <motion.button
            key={category}
            onClick={() => setFilter(category)}
            className={`filter-btn ${filter === category ? 'active' : ''}`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {category}
          </motion.button>
        ))}
      </div>
      
      {/* Product grid */}
      <motion.div 
        layout
        className="product-grid"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
          gap: '1rem',
        }}
      >
        <AnimatePresence>
          {filteredProducts.map(product => (
            <motion.div
              key={product.id}
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              whileHover={{ y: -5 }}
              className="product-card"
              onClick={() => setSelectedProduct(product)}
            >
              <img src={product.image} alt={product.name} />
              <h3>{product.name}</h3>
              <p>${product.price}</p>
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>
      
      {/* Product modal */}
      <AnimatePresence>
        {selectedProduct && (
          <motion.div
            className="product-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedProduct(null)}
          >
            <motion.div
              className="product-modal"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={e => e.stopPropagation()}
            >
              <img src={selectedProduct.image} alt={selectedProduct.name} />
              <div className="product-details">
                <h2>{selectedProduct.name}</h2>
                <p>{selectedProduct.description}</p>
                <p className="price">${selectedProduct.price}</p>
                <button className="add-to-cart">Add to Cart</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
{% endraw %}
{% endraw %}
```

### Dashboard with Animated Charts

```jsx
{% raw %}
{% raw %}
const AnimatedDashboard = ({ data }) => {
  const [selectedMetric, setSelectedMetric] = useState('revenue')
  
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      {/* Metric cards */}
      <div className="metric-cards">
        {Object.entries(data.metrics).map(([key, value], index) => (
          <motion.div
            key={key}
            className="metric-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => setSelectedMetric(key)}
          >
            <h3>{key}</h3>
            <motion.div
              className="metric-value"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 + 0.3, type: 'spring' }}
            >
              {value}
            </motion.div>
          </motion.div>
        ))}
      </div>
      
      {/* Animated chart */}
      <motion.div
        className="chart-container"
        key={selectedMetric}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <h2>Trending {selectedMetric}</h2>
        <AnimatedChart data={data.charts[selectedMetric]} />
      </motion.div>
    </div>
  )
}

const AnimatedChart = ({ data }) => {
  return (
    <div className="chart">
      {data.map((point, index) => (
        <motion.div
          key={index}
          className="chart-bar"
          initial={{ height: 0 }}
          animate={{ height: `${point.value}%` }}
          transition={{ 
            delay: index * 0.1,
            duration: 0.5,
            ease: 'easeOut'
          }}
          style={{
            background: `hsl(${point.value * 2}, 70%, 50%)`,
          }}
        />
      ))}
    </div>
  )
}
{% endraw %}
{% endraw %}
```

This comprehensive guide covers animation and responsive design patterns for React applications, providing practical techniques for creating engaging, accessible, and performant user interfaces across all device types.
