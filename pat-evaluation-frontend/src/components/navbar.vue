<template>
  <header class="nav-rail">
    <div class="nav-rail__inner">
      <a href="/search" class="nav-brand">
        <div class="nav-brand__icon">
          <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
            <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity="0.2"/>
            <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
        </div>
        <div class="nav-brand__text">
          <span class="nav-brand__title">专利价值评价</span>
          <span class="nav-brand__domain">Biomedical · Patent Valuation</span>
        </div>
      </a>
      <nav class="nav-links">
        <router-link to="/search" class="nav-chip" :class="{ 'nav-chip--active': $route.path === '/search' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
          </svg>
          检索
        </router-link>
        <router-link to="/import" class="nav-chip" :class="{ 'nav-chip--active': $route.path === '/import' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
            <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"/>
          </svg>
          数据导入
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script>
export default { name: 'NavBar' }
</script>

<style scoped>
.nav-rail {
  background: var(--md-surface-container-lowest);
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 0 var(--md-outline-variant);
}
.nav-rail__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}
.nav-brand__icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  background: var(--md-primary-container);
  color: var(--md-on-primary-container);
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-brand__text { display: flex; flex-direction: column; }
.nav-brand__title {
  font-size: 16px;
  font-weight: 700;
  color: var(--md-on-surface);
  letter-spacing: 0.01em;
  line-height: 1.2;
}
.nav-brand__domain {
  font-size: 11px;
  color: var(--md-outline);
  font-weight: 500;
  letter-spacing: 0.04em;
  line-height: 1.2;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}
.nav-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--md-on-surface-variant);
  padding: 8px 20px;
  border-radius: var(--radius-full);
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  text-decoration: none;
}
.nav-chip:hover {
  background: var(--sci-accent-light);
  color: var(--md-on-surface);
}
.nav-chip--active {
  background: var(--md-secondary-container);
  color: var(--md-on-secondary-container);
  font-weight: 600;
}
</style>
