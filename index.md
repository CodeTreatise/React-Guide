---
layout: default
title: "React.js Master Learning Guide"
description: "Complete React.js learning path from beginner to production-ready developer"
---

<div class="hero-section">
  <h1>🚀 React.js Master Learning Guide</h1>
  <p class="lead">Complete React.js learning path from beginner to production-ready developer</p>
  <p class="subtitle">16-20 weeks intensive learning program covering everything from fundamentals to advanced patterns</p>
  
  <div class="cta-buttons">
    <a href="{{ '/REACT_LEARNING_MASTER_PLAN/' | relative_url }}" class="btn btn-primary">Start Learning</a>
    <a href="{{ '/QUICK_START_GUIDE/' | relative_url }}" class="btn btn-secondary">Quick Start</a>
  </div>
</div>

## 🎯 What You'll Learn

<div class="features-grid">
  <div class="feature">
    <h3>🔧 React Fundamentals</h3>
    <p>Master JSX, components, props, state, and event handling</p>
  </div>
  
  <div class="feature">
    <h3>🪝 Modern Hooks</h3>
    <p>Deep dive into useState, useEffect, custom hooks, and advanced patterns</p>
  </div>
  
  <div class="feature">
    <h3>📊 State Management</h3>
    <p>Context API, Redux, Zustand, and enterprise-level state solutions</p>
  </div>
  
  <div class="feature">
    <h3>⚡ Performance</h3>
    <p>Optimization techniques, lazy loading, and production-ready patterns</p>
  </div>
  
  <div class="feature">
    <h3>🧪 Testing</h3>
    <p>Unit tests, integration tests, and testing best practices</p>
  </div>
  
  <div class="feature">
    <h3>🚀 Deployment</h3>
    <p>Build tools, CI/CD, and production deployment strategies</p>
  </div>
</div>

## 📚 Learning Modules

{% assign modules = site.pages | where_exp: "page", "page.path contains 'README.md'" | sort: "path" %}

<div class="modules-list">
  {% for module in modules %}
    {% if module.path contains 'README.md' and module.path != 'README.md' %}
      {% assign module_number = module.path | split: '/' | first | split: '-' | first %}
      {% assign module_name = module.path | split: '/' | first | split: '-' | slice: 1, 10 | join: ' ' %}
      
      <div class="module-item">
        <h3>
          <a href="{{ module.url | relative_url }}">
            Module {{ module_number }}: {{ module_name | capitalize }}
          </a>
        </h3>
        <p>{{ module.description | default: "Comprehensive coverage of " | append: module_name }}</p>
      </div>
    {% endif %}
  {% endfor %}
</div>

## 🏁 Quick Start

1. **Prerequisites**: Basic JavaScript knowledge (ES6+ preferred)
2. **Duration**: 16-20 weeks intensive learning
3. **Approach**: Theory + Hands-on projects + Real-world applications

<div class="quick-links">
  <a href="{{ '/REACT_LEARNING_MASTER_PLAN/' | relative_url }}" class="quick-link">
    📋 **Master Plan** - Complete learning roadmap
  </a>
  
  <a href="{{ '/QUICK_START_GUIDE/' | relative_url }}" class="quick-link">
    ⚡ **Quick Start** - Jump right in
  </a>
  
  <a href="{{ '/LEARNING_COMPLETION_SUMMARY/' | relative_url }}" class="quick-link">
    📊 **Progress Tracker** - Monitor your progress
  </a>
</div>

## 🤝 Contributing

This is an open-source learning resource. Feel free to:
- Report issues or suggest improvements
- Add your own learning notes
- Share your project implementations
- Help other learners in discussions

---

<div class="footer-cta">
  <p><strong>Ready to become a React expert?</strong></p>
  <a href="{{ '/REACT_LEARNING_MASTER_PLAN/' | relative_url }}" class="btn btn-primary">Start Your Journey</a>
</div>

<style>
.hero-section {
  text-align: center;
  padding: 60px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 3rem;
  margin-bottom: 20px;
  color: white;
}

.lead {
  font-size: 1.3rem;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 30px;
}

.cta-buttons {
  margin-top: 30px;
}

.btn {
  display: inline-block;
  padding: 12px 30px;
  margin: 0 10px;
  text-decoration: none;
  border-radius: 5px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #28a745;
  color: white;
}

.btn-secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin: 40px 0;
}

.feature {
  padding: 30px;
  border-radius: 10px;
  background: #f8f9fa;
  border-left: 4px solid #007bff;
}

.feature h3 {
  color: #007bff;
  margin-bottom: 15px;
}

.modules-list {
  margin: 40px 0;
}

.module-item {
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.module-item h3 a {
  color: #007bff;
  text-decoration: none;
}

.module-item h3 a:hover {
  text-decoration: underline;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 40px 0;
}

.quick-link {
  display: block;
  padding: 20px;
  background: #fff;
  border: 2px solid #007bff;
  border-radius: 8px;
  text-decoration: none;
  color: #007bff;
  text-align: center;
  transition: all 0.3s ease;
}

.quick-link:hover {
  background: #007bff;
  color: white;
  transform: translateY(-2px);
}

.footer-cta {
  text-align: center;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 10px;
  margin-top: 60px;
}

@media (max-width: 768px) {
  .hero-section h1 {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .cta-buttons {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    margin: 5px 0;
    width: 200px;
  }
}
</style>
