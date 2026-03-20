<template>
  <div class="detailed-view">
    <!-- 子导航 -->
    <div class="detail-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="detail-tab"
        :class="{ active: innerActive === tab.key }"
        @click="handleSelect(tab.key)"
      >
        <span class="detail-tab__dot" :class="{ active: innerActive === tab.key }"></span>
        {{ tab.label }}
      </button>
    </div>
    <router-view />
  </div>
</template>

<script>
export default {
  data() {
    return {
      innerActive: 'market',
      tabs: [
        { key: 'market', label: '市场要素' },
        { key: 'group', label: '专利组合要素' },
        { key: 'law', label: '法律要素' },
        { key: 'tech', label: '技术要素' },
      ]
    }
  },
  methods: {
    handleSelect(key) {
      this.innerActive = key;
      let basePath = '/pat-evaluation/detailed/';
      this.$router.push(key === 'market' ? basePath : basePath + key);
    }
  }
}
</script>

<style scoped>
.detail-tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-sm);
  background: var(--color-bg-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}
.detail-tab {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  font-family: var(--font-sans);
  color: var(--color-text-secondary);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}
.detail-tab:hover {
  color: var(--color-primary);
  background: var(--color-accent-light);
}
.detail-tab.active {
  color: var(--color-primary);
  background: var(--color-accent-light);
  border-color: rgba(0, 102, 204, 0.15);
  font-weight: 600;
}
.detail-tab__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-border);
  transition: background 0.2s;
}
.detail-tab__dot.active {
  background: var(--color-primary);
}
</style>
