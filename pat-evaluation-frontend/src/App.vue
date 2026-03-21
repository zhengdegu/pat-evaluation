<template>
  <div id="app" class="app-layout">
    <NavBar v-if="showNav" />
    <main class="app-main">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </main>
    <footer v-if="showNav" class="app-footer">
      <div class="page-container">
        <span class="app-footer__text">© 2025 生物医药领域专利价值评价系统 · Biomedical Patent Valuation Platform</span>
      </div>
    </footer>
  </div>
</template>

<script>
import NavBar from "@/components/navbar.vue";

export default {
  data() {
    return { showNav: true };
  },
  components: { NavBar },
  mounted() {
    let path = this.$route.path;
    let targetPatentId = this.$route.query.patentId;
    if (this.$store.state.patentId === null) {
      this.$store.commit('setPatentId', targetPatentId);
      if (path === '/downloadReport') {
        this.showNav = false;
        this.$router.push('/print_report');
      }
    }
  }
}
</script>

<style scoped>
.app-main {
  flex: 1;
  padding: var(--space-xl) 0;
}
.app-footer {
  background: var(--md-surface-container-lowest);
  border-top: 1px solid var(--md-outline-variant);
  padding: var(--space-md) 0;
  text-align: center;
}
.app-footer__text {
  font-size: 12px;
  color: var(--md-outline);
  letter-spacing: 0.02em;
}
</style>
