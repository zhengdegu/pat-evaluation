<template>
  <div class="detailed-view">
    <div class="detail-tabs">
      <button v-for="tab in tabs" :key="tab.key" class="detail-tab" :class="{ active: innerActive === tab.key }" @click="handleSelect(tab.key)">
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
        { key: 'market', label: '市场要素' }, { key: 'group', label: '专利组合要素' },
        { key: 'law', label: '法律要素' }, { key: 'tech', label: '技术要素' }
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
  display: flex; gap: var(--space-sm); margin-bottom: var(--space-lg);
  padding: var(--space-sm); background: var(--md-surface-container-lowest);
  border-radius: var(--radius-sm); box-shadow: var(--elevation-1);
}
.detail-tab {
  flex: 1; display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px 16px; font-size: 14px; font-weight: 500; font-family: var(--font-sans);
  color: var(--md-on-surface-variant); background: transparent;
  border: none; border-radius: var(--radius-xs); cursor: pointer; transition: all 0.2s;
}
.detail-tab:hover { color: var(--md-on-surface); background: var(--md-surface-container); }
.detail-tab.active { color: var(--md-on-secondary-container); background: var(--md-secondary-container); font-weight: 600; }
.detail-tab__dot { width: 6px; height: 6px; border-radius: 50%; background: var(--md-outline-variant); transition: background 0.2s; }
.detail-tab__dot.active { background: var(--md-primary); }
</style>
