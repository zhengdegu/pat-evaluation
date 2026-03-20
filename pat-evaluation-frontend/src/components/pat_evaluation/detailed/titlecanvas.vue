<template>
  <div class="card">
    <div class="card-header">
      <span class="card-header__indicator"></span>
      <span class="card-header__title">{{ title }}</span>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: String
  }
}
</script>

<style scoped>
.card-body {
  padding: var(--spacing-sm) 0 0;
}
</style>
