<template>
  <header class="site-header">
    <div class="site-header__inner">
      <a href="/search" class="site-header__brand">
        <svg class="site-header__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 12h6m-3-3v6m-7 4h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        <span class="site-header__title">生物医药领域专利价值评价系统</span>
        <span class="site-header__subtitle">Biomedical Patent Valuation</span>
      </a>
      <nav class="site-header__nav">
        <router-link to="/search" class="site-header__link" :class="{ active: $route.path === '/search' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
          </svg>
          检索
        </router-link>
        <router-link to="/import" class="site-header__link" :class="{ active: $route.path === '/import' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"/>
          </svg>
          数据导入
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script>
export default {
  name: 'NavBar'
}
</script>

<style scoped>
.site-header {
  background: var(--color-bg-white);
  border-bottom: 1px solid var(--color-border);
  height: 56px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.site-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.site-header__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}
.site-header__icon {
  width: 28px;
  height: 28px;
  color: var(--color-primary);
}
.site-header__title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 0.03em;
}
.site-header__subtitle {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-weight: 400;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-left: 4px;
}
.site-header__nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}
.site-header__link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  padding: 6px 12px;
  border-radius: var(--radius-md);
  transition: all 0.2s;
}
.site-header__link:hover,
.site-header__link.active {
  color: var(--color-primary);
  background: var(--color-accent-light);
}
</style>
