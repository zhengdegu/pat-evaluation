<template>
  <div class="evaluation-page">
    <div class="page-container">
      <div class="breadcrumb">
        <router-link to="/search">检索</router-link>
        <span class="breadcrumb__sep">›</span>
        <router-link to="/main">专利详情</router-link>
        <span class="breadcrumb__sep">›</span>
        <span>评估报告</span>
      </div>

      <div class="report-hero">
        <div class="report-hero__content">
          <div class="report-hero__chip">Evaluation Report</div>
          <h1 class="report-hero__title">{{ this.$store.state.patentTitle }}</h1>
          <p class="report-hero__sub">专利综合评估报告</p>
        </div>
        <div class="report-hero__actions">
          <button class="icon-btn" @click="reEvaluation" title="重新评估">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          </button>
          <button class="icon-btn" @click="navi('/print_report')" title="下载报告">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20"><path d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          </button>
          <button class="icon-btn" @click="navi('/main')" title="专利详情">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20"><path d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V9a2 2 0 012-2h2a2 2 0 012 2v9a2 2 0 01-2 2h-2z"/></svg>
          </button>
          <button class="icon-btn" @click="navi('/search')" title="返回检索">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </button>
        </div>
      </div>

      <div class="report-tabs">
        <el-menu :default-active="activeIndex" class="report-menu" mode="horizontal" @select="handleSelect">
          <el-menu-item index="general">总体情况</el-menu-item>
          <el-menu-item index="detailed">评估详情</el-menu-item>
        </el-menu>
      </div>

      <div class="report-content"><router-view /></div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
let START_URL = "/api/evaluation/start";
let GET_BASIC_INFO_URI = "/api/basicinfo/get_patent_info";

export default {
  data() { return { activeIndex: "general" }; },
  mounted() {
    let targetPatentId = this.$route.query.patentId;
    if (this.$store.state.patentId !== targetPatentId && targetPatentId !== null) this.$store.commit("setPatentId", targetPatentId);
    let patentId = this.$store.state.patentId;
    axios.get(GET_BASIC_INFO_URI + "?patid=" + patentId).then((response) => {
      this.$store.commit("setPatentTitle", response["data"]["专利名"]);
    }).catch((error) => { console.log(error); });
  },
  methods: {
    handleSelect(key) {
      if (key === "general") this.$router.push("/pat-evaluation");
      else this.$router.push("/pat-evaluation/" + key);
    },
    reEvaluation() {
      let patentId = this.$store.state.patentId;
      axios.get(START_URL + "?patid=" + patentId + "&reload=1").then((r) => { console.log(r); }).catch((e) => { console.log(e); });
    },
    navi(url) { this.$router.push(url); }
  }
};
</script>

<style scoped>
.evaluation-page { min-height: calc(100vh - 160px); }
.breadcrumb { font-size: 13px; color: var(--md-outline); margin-bottom: var(--space-lg); }
.breadcrumb a { color: var(--md-primary); }
.breadcrumb__sep { margin: 0 8px; color: var(--md-outline-variant); }

.report-hero {
  background: var(--md-surface-container-lowest); border-radius: var(--radius-sm);
  padding: var(--space-xl) var(--space-lg); margin-bottom: var(--space-md);
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: var(--elevation-1);
}
.report-hero__chip { display: inline-block; font-size: 11px; font-weight: 600; color: var(--md-on-primary-container); background: var(--md-primary-container); padding: 4px 14px; border-radius: var(--radius-full); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: var(--space-sm); }
.report-hero__title { font-size: 22px; font-weight: 700; color: var(--md-on-surface); line-height: 1.4; margin-bottom: 4px; }
.report-hero__sub { font-size: 14px; color: var(--md-outline); }
.report-hero__actions { display: flex; gap: var(--space-sm); flex-shrink: 0; }
.icon-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 40px; height: 40px; border-radius: var(--radius-full);
  background: var(--md-surface-container); color: var(--md-on-surface-variant);
  border: none; cursor: pointer; transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
}
.icon-btn:hover { background: var(--md-secondary-container); color: var(--md-on-secondary-container); }

.report-tabs {
  background: var(--md-surface-container-lowest); border-radius: var(--radius-sm);
  margin-bottom: var(--space-md); padding: 0 var(--space-md); box-shadow: var(--elevation-1);
}
.report-menu { border-bottom: none !important; background: transparent !important; }
.report-menu .el-menu-item { height: 48px; line-height: 48px; }
</style>
