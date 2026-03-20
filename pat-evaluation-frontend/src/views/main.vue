<template>
  <div class="detail-page">
    <div class="page-container">
      <!-- 面包屑 -->
      <div class="breadcrumb">
        <router-link to="/search">检索</router-link>
        <span class="breadcrumb__sep">/</span>
        <span>专利详情</span>
      </div>

      <!-- 专利标题卡片 -->
      <div class="patent-header card">
        <div class="patent-header__top">
          <span class="patent-header__badge">专利信息</span>
        </div>
        <h1 class="patent-header__title">{{ patentTitle || '加载中...' }}</h1>
      </div>

      <!-- 专利元数据 -->
      <div class="patent-meta card" v-if="patMetaData.length">
        <div class="card-header">
          <span class="card-header__indicator"></span>
          <span class="card-header__title">基本信息</span>
        </div>
        <div class="meta-grid">
          <div class="meta-item" v-for="item in patMetaData" :key="item.key">
            <span class="meta-item__label">{{ item.key }}</span>
            <span class="meta-item__value">{{ item.value }}</span>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-bar">
        <button class="action-btn" :disabled="navDisabled" @click="navigateTo('/smart-search')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
            <path d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
          相似专利
        </button>
        <button class="action-btn action-btn--primary" :disabled="navDisabled" @click="navigateTo('/pat-evaluation')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          专利评估报告
        </button>
        <button class="action-btn" @click="navigateTo('/search')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
            <path d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          返回检索
        </button>
      </div>

      <!-- 错误对话框 -->
      <el-dialog title="提示" :visible.sync="dialogVisible" width="400px" center>
        <p style="text-align:center; color: var(--color-text-secondary);">
          未找到专利号为 <strong>{{ this.$store.state.patentId }}</strong> 的专利，请确认输入正确。
        </p>
        <span slot="footer">
          <el-button type="primary" @click="dialogVisible = false">确定</el-button>
        </span>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import axios from "axios";
let GET_BASIC_INFO_URI = "/api/basicinfo/get_patent_info";

export default {
  data() {
    return {
      patentTitle: null,
      patMetaData: [],
      dialogVisible: false,
      navDisabled: false,
    };
  },
  mounted() {
    let targetPatentId = this.$route.query.patentId;
    if (this.$store.state.patentId === null) {
      this.$store.commit("setPatentId", targetPatentId);
    }
    let patentId = this.$store.state.patentId;
    axios
      .get(GET_BASIC_INFO_URI + "?patid=" + patentId)
      .then((response) => {
        let d = response["data"];
        this.patentTitle = d["专利名"];
        let fieldOrder = [
          '申请号', '专利名', '主分类号', 'IPC分类号', '申请人', '当前权利人',
          '发明人', '公开日', '公开号', '代理机构', '代理人', '申请日',
          '申请人地址', '优先权', '国省代码', '摘要', '主权项',
          '引用专利', '引用文献', '法律状态', '专利类型', '转化收益（万元）'
        ];
        let pData = [];
        for (const key of fieldOrder) {
          let value = d[key];
          if (value === undefined || value === null || value === '') value = '—';
          else if (Array.isArray(value)) value = value.join('，');
          pData.push({ key: key, value: value });
        }
        this.patMetaData = pData;
        this.$store.commit("setPatentTitle", this.patentTitle);
      })
      .catch((error) => {
        if (error.response && error.response.status === 404) {
          this.dialogVisible = true;
          this.navDisabled = true;
        }
      });
  },
  methods: {
    navigateTo(dest) {
      let patentId = this.$store.state.patentId;
      if (patentId) {
        this.$router.push({ path: dest, query: { patentId: patentId } });
      } else {
        this.$router.push(dest);
      }
    },
  },
};
</script>

<style scoped>
.detail-page {
  min-height: calc(100vh - 160px);
}

.breadcrumb {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-lg);
}
.breadcrumb a {
  color: var(--color-accent);
}
.breadcrumb__sep {
  margin: 0 8px;
  color: var(--color-border);
}

.patent-header {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-lg);
}
.patent-header__top {
  margin-bottom: var(--spacing-md);
}
.patent-header__badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-accent-light);
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.patent-header__title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.5;
}

/* 元数据网格 */
.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0;
}
.meta-item {
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border-light);
}
.meta-item:nth-child(odd) {
  border-right: 1px solid var(--color-border-light);
}
.meta-item__label {
  flex-shrink: 0;
  width: 120px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.meta-item__value {
  font-size: 13px;
  color: var(--color-text-primary);
  word-break: break-all;
}

/* 操作按钮 */
.action-bar {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  margin-top: var(--spacing-lg);
}
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  font-size: 14px;
  font-weight: 500;
  font-family: var(--font-sans);
  color: var(--color-text-secondary);
  background: var(--color-bg-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}
.action-btn:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}
.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.action-btn--primary {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}
.action-btn--primary:hover:not(:disabled) {
  background: var(--color-primary-light);
  color: #fff;
  border-color: var(--color-primary-light);
}
</style>
