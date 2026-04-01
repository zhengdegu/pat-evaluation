<template>
  <div class="detail-page">
    <div class="page-container">
      <div class="breadcrumb">
        <router-link to="/search">检索</router-link>
        <span class="breadcrumb__sep">›</span>
        <span>专利详情</span>
      </div>

      <div class="patent-hero">
        <div class="patent-hero__chip">Patent Detail</div>
        <h1 class="patent-hero__title">{{ patentTitle || '加载中...' }}</h1>
      </div>

      <div class="card" v-if="patMetaData.length">
        <div class="card-header">
          <span class="card-header__indicator"></span>
          <span class="card-header__title">基本信息</span>
        </div>
        <div class="meta-grid">
          <div class="meta-item" v-for="item in patMetaData" :key="item.key">
            <span class="meta-label">{{ item.key }}</span>
            <span class="meta-value">{{ item.value }}</span>
          </div>
        </div>
      </div>

      <div class="card" v-if="tradeRecords.length">
        <div class="card-header">
          <span class="card-header__indicator" style="background:var(--md-tertiary)"></span>
          <span class="card-header__title">交易记录</span>
        </div>
        <el-table :data="tradeRecords" style="width:100%" :header-cell-style="tableHeaderStyle">
          <el-table-column prop="交易类型" label="类型" width="80" align="center">
            <template slot-scope="scope">
              <span class="trade-tag" :class="'trade-tag--' + scope.row.交易类型">{{ scope.row.交易类型 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="交易日期" label="日期" width="120" />
          <el-table-column prop="原权利人" label="原权利人" min-width="200" />
          <el-table-column prop="新权利人" label="新权利人/被许可人" min-width="200" />
          <el-table-column prop="法律事件标题" label="事件" min-width="200" />
        </el-table>
      </div>

      <div class="action-row">
        <button class="md3-btn md3-btn--tonal" :disabled="navDisabled" @click="navigateTo('/smart-search')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18"><path d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
          相似专利
        </button>
        <button class="md3-btn md3-btn--filled" :disabled="navDisabled" @click="navigateTo('/pat-evaluation')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18"><path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          评估报告
        </button>
        <button class="md3-btn md3-btn--outlined" @click="navigateTo('/search')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18"><path d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
          返回检索
        </button>
      </div>

      <el-dialog title="提示" :visible.sync="dialogVisible" width="400px" center>
        <p style="text-align:center;color:var(--md-on-surface-variant)">
          未找到专利号为 <strong>{{ this.$store.state.patentId }}</strong> 的专利
        </p>
        <span slot="footer"><el-button type="primary" @click="dialogVisible = false">确定</el-button></span>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import axios from "axios";
let GET_BASIC_INFO_URI = "/api/basicinfo/get_patent_info";

export default {
  data() {
    return { patentTitle: null, patMetaData: [], tradeRecords: [], dialogVisible: false, navDisabled: false };
  },
  computed: {
    tableHeaderStyle() { return { background: 'var(--md-surface-container)', color: 'var(--md-on-surface-variant)', fontWeight: '600', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em' } }
  },
  mounted() {
    let targetPatentId = this.$route.query.patentId;
    if (this.$store.state.patentId === null) this.$store.commit("setPatentId", targetPatentId);
    let patentId = this.$store.state.patentId;
    axios.get(GET_BASIC_INFO_URI + "?patid=" + patentId).then((response) => {
      let d = response["data"];
      this.patentTitle = d["专利名"];
      let fieldOrder = ['申请号','专利名','主分类号','IPC分类号','申请人','当前权利人','发明人','公开日','公开号','代理机构','代理人','申请日','申请人地址','优先权','国省代码','摘要','主权项','引用专利','引用文献','法律状态','专利类型'];
      let pData = [];
      for (const key of fieldOrder) {
        let value = d[key];
        if (value === undefined || value === null || value === '') value = '—';
        else if (Array.isArray(value)) value = value.join('，');
        pData.push({ key: key, value: value });
      }
      this.patMetaData = pData;
      this.tradeRecords = d.trade_records || [];
      this.$store.commit("setPatentTitle", this.patentTitle);
    }).catch((error) => {
      if (error.response && error.response.status === 404) { this.dialogVisible = true; this.navDisabled = true; }
    });
  },
  methods: {
    navigateTo(dest) {
      let patentId = this.$store.state.patentId;
      if (patentId) this.$router.push({ path: dest, query: { patentId: patentId } });
      else this.$router.push(dest);
    }
  }
};
</script>

<style scoped>
.detail-page { min-height: calc(100vh - 160px); }
.breadcrumb { font-size: 13px; color: var(--md-outline); margin-bottom: var(--space-lg); }
.breadcrumb a { color: var(--md-primary); }
.breadcrumb__sep { margin: 0 8px; color: var(--md-outline-variant); }

.patent-hero {
  text-align: center; padding: var(--space-xl);
  background: var(--md-surface-container-lowest);
  border-radius: var(--radius-sm); box-shadow: var(--elevation-1);
  margin-bottom: var(--space-md);
}
.patent-hero__chip {
  display: inline-block; font-size: 11px; font-weight: 600;
  color: var(--md-on-primary-container); background: var(--md-primary-container);
  padding: 4px 14px; border-radius: var(--radius-full);
  letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: var(--space-sm);
}
.patent-hero__title { font-size: 22px; font-weight: 700; color: var(--md-on-surface); line-height: 1.5; }

.meta-grid { display: grid; grid-template-columns: repeat(2, 1fr); }
.meta-item { display: flex; padding: 14px 16px; border-bottom: 1px solid var(--md-surface-container-high); }
.meta-item:nth-child(odd) { border-right: 1px solid var(--md-surface-container-high); }
.meta-label { flex-shrink: 0; width: 120px; font-size: 13px; font-weight: 600; color: var(--md-on-surface-variant); }
.meta-value { font-size: 13px; color: var(--md-on-surface); word-break: break-all; }

.action-row { display: flex; gap: var(--space-md); justify-content: center; margin-top: var(--space-lg); }

/* MD3 按钮 */
.md3-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 28px; font-size: 14px; font-weight: 500;
  font-family: var(--font-sans); border-radius: var(--radius-full);
  cursor: pointer; transition: all 0.2s cubic-bezier(0.2, 0, 0, 1); border: none;
}
.md3-btn:disabled { opacity: 0.38; cursor: not-allowed; }
.md3-btn--filled { background: var(--md-primary); color: var(--md-on-primary); }
.md3-btn--filled:hover:not(:disabled) { box-shadow: var(--elevation-1); background: var(--sci-accent); }
.md3-btn--tonal { background: var(--md-secondary-container); color: var(--md-on-secondary-container); }
.md3-btn--tonal:hover:not(:disabled) { box-shadow: var(--elevation-1); }
.md3-btn--outlined { background: transparent; color: var(--md-primary); border: 1px solid var(--md-outline); }
.md3-btn--outlined:hover:not(:disabled) { background: var(--sci-accent-light); }

.trade-tag { display: inline-block; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: var(--radius-full); }
.trade-tag--转让 { color: var(--md-error); background: var(--md-error-container); }
.trade-tag--许可 { color: var(--md-primary); background: var(--md-primary-container); }
.trade-tag--质押 { color: var(--md-warning); background: var(--md-warning-container); }
</style>
