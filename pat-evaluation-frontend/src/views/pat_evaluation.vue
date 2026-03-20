<template>
  <div class="evaluation-page">
    <div class="page-container">
      <!-- 面包屑 -->
      <div class="breadcrumb">
        <router-link to="/search">检索</router-link>
        <span class="breadcrumb__sep">/</span>
        <router-link to="/main">专利详情</router-link>
        <span class="breadcrumb__sep">/</span>
        <span>评估报告</span>
      </div>

      <!-- 报告头部 -->
      <div class="report-header">
        <div class="report-header__content">
          <span class="report-header__badge">Evaluation Report</span>
          <h1 class="report-header__title">{{ this.$store.state.patentTitle }}</h1>
          <p class="report-header__subtitle">专利评估报告</p>
        </div>
        <div class="report-header__actions">
          <button class="header-action" @click="reEvaluation" title="重新评估">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
          <button class="header-action" @click="navi('/print_report')" title="下载报告">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
              <path d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </button>
          <button class="header-action" @click="navi('/main')" title="专利详情">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
              <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
          </button>
          <button class="header-action" @click="navi('/search')" title="返回检索">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 导航标签 -->
      <div class="report-nav">
        <el-menu
          :default-active="activeIndex"
          class="report-menu"
          mode="horizontal"
          @select="handleSelect"
        >
          <el-menu-item index="general">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" style="margin-right:6px">
              <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"/>
            </svg>
            总体情况
          </el-menu-item>
          <el-menu-item index="detailed">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" style="margin-right:6px">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
            </svg>
            评估详情
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 内容区域 -->
      <div class="report-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

let START_URL = "/api/evaluation/start";
let GET_BASIC_INFO_URI = "/api/basicinfo/get_patent_info";

export default {
  data() {
    return {
      activeIndex: "general",
    };
  },
  mounted() {
    let targetPatentId = this.$route.query.patentId;
    if (this.$store.state.patentId !== targetPatentId && targetPatentId !== null) {
      this.$store.commit("setPatentId", targetPatentId);
    }
    let patentId = this.$store.state.patentId;
    axios
      .get(GET_BASIC_INFO_URI + "?patid=" + patentId)
      .then((response) => {
        let patMetaData = response["data"];
        this.$store.commit("setPatentTitle", patMetaData["专利名"]);
      })
      .catch((error) => {
        console.log(error);
      });
  },
  methods: {
    handleSelect(key) {
      switch (key) {
        case "general":
          this.$router.push("/pat-evaluation");
          break;
        case "detailed":
          this.$router.push("/pat-evaluation/" + key);
          break;
      }
    },
    reEvaluation() {
      let patentId = this.$store.state.patentId;
      axios.get(START_URL + "?patid=" + patentId + "&reload=1")
        .then((response) => { console.log(response); })
        .catch((error) => { console.log(error); });
    },
    navi(url) {
      if (url === "/main") {
        window.top.location = "http://47.95.2.165/#/";
      } else if (url === "/search") {
        window.top.location = "http://47.95.2.165/#/patentadvancedsearch";
      } else {
        this.$router.push(url);
      }
    },
  },
};
</script>

<style scoped>
.evaluation-page {
  min-height: calc(100vh - 160px);
}

.breadcrumb {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-lg);
}
.breadcrumb a { color: var(--color-accent); }
.breadcrumb__sep { margin: 0 8px; color: var(--color-border); }

/* 报告头部 */
.report-header {
  background: var(--color-bg-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl) var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-sm);
}
.report-header__badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-accent-light);
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: var(--spacing-sm);
}
.report-header__title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.4;
  margin-bottom: 4px;
}
.report-header__subtitle {
  font-size: 14px;
  color: var(--color-text-tertiary);
}
.report-header__actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}
.header-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-white);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.header-action:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: var(--color-accent-light);
}

/* 导航 */
.report-nav {
  background: var(--color-bg-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
  padding: 0 var(--spacing-md);
  box-shadow: var(--shadow-sm);
}
.report-menu {
  border-bottom: none !important;
  background: transparent !important;
}
.report-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  display: inline-flex;
  align-items: center;
}
</style>
