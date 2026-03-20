<template>
  <div class="law-detail">
    <!-- 有效期 -->
    <title-canvas title="专利有效期">
      <div class="validity-bar">
        <el-progress
          id="validityperiod"
          :text-inside="true"
          :stroke-width="28"
          :percentage="validityperiod"
          :show-text="true"
          :color="'var(--color-primary)'"
        />
      </div>
    </title-canvas>

    <!-- 多国申请 -->
    <title-canvas title="多国申请情况">
      <div class="country-grid">
        <div class="country-item" v-for="c in countries" :key="c.code">
          <div class="country-flag">
            <flag :iso="c.code" />
          </div>
          <span class="country-name">{{ c.name }}</span>
          <span class="country-status" :class="getStatusClass(c.code)">
            {{ getStatusText(c.code) }}
          </span>
        </div>
      </div>
    </title-canvas>

    <!-- 诉讼 -->
    <title-canvas title="法律诉讼情况">
      <el-table v-if="lawSuites.length" :data="lawSuites" style="width:100%" :header-cell-style="tableHeaderStyle">
        <el-table-column type="index" label="#" width="56" align="center" />
        <el-table-column prop="id" label="案号" width="200" />
        <el-table-column prop="reason" label="案由" min-width="200" />
        <el-table-column prop="prosecutor" label="原告" width="160" />
        <el-table-column prop="defendant" label="被告" width="160" />
      </el-table>
      <div v-else class="empty-state">
        <span class="text-tertiary">暂无诉讼记录</span>
      </div>
    </title-canvas>
  </div>
</template>

<script>
import axios from "axios";

let GET_VALID_DATE_URL = "/api/lawfactor/validityperiod";
let MULTIPLE_APPLY_URL = '/api/lawfactor/multipleapplications';
let LAW_SUITE_URL = "/api/lawfactor/lawsuits";
let PAT_VALID_DATE_CN = 25;

export default {
  data() {
    return {
      validityperiod: 0,
      appliedCountry: {},
      lawSuites: [],
      countries: [
        { code: 'us', key: 'US', name: '美国' },
        { code: 'gb', key: 'GB', name: '英国' },
        { code: 'fr', key: 'FR', name: '法国' },
        { code: 'de', key: 'DE', name: '德国' },
        { code: 'jp', key: 'JP', name: '日本' },
        { code: 'kr', key: 'KR', name: '韩国' },
      ]
    }
  },
  computed: {
    tableHeaderStyle() {
      return {
        background: '#f8f9fb', color: '#5a6577', fontWeight: '600',
        fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em'
      }
    }
  },
  methods: {
    getStatusText(code) {
      let key = code.toUpperCase();
      if (!this.appliedCountry.hasOwnProperty(key)) return '未申请';
      return this.appliedCountry[key] === 'approved' ? '已授权' : '已申请';
    },
    getStatusClass(code) {
      let key = code.toUpperCase();
      if (!this.appliedCountry.hasOwnProperty(key)) return 'status--none';
      return this.appliedCountry[key] === 'approved' ? 'status--approved' : 'status--applied';
    }
  },
  mounted() {
    let patentId = this.$store.state.patentId;
    if (patentId !== null) {
      axios.get(GET_VALID_DATE_URL + "?patid=" + patentId)
        .then((response) => {
          let fromDate = response.data.validity.from;
          let status = response.data.validity.status;
          if (status === 'valid') {
            fromDate = new Date(Date.parse(fromDate));
            let now = new Date(Date.now());
            let validLeft = PAT_VALID_DATE_CN - (now.getFullYear() - fromDate.getFullYear());
            this.validityperiod = validLeft / PAT_VALID_DATE_CN * 100;
            this.$nextTick(() => {
              let el = document.getElementById("validityperiod");
              if (el) {
                let textEl = el.getElementsByClassName("el-progress-bar__innerText")[0];
                if (textEl) textEl.textContent = `有效期剩余 ${validLeft} 年`;
              }
            });
          }
        }).catch((e) => console.log(e));

      axios.get(MULTIPLE_APPLY_URL + "?patid=" + patentId)
        .then((response) => {
          let countries = {};
          for (const i of response.data.applications) {
            countries[i.country] = i.status;
          }
          this.appliedCountry = countries;
        }).catch((e) => console.log(e));

      axios.get(LAW_SUITE_URL + "?patid=" + patentId)
        .then((response) => {
          this.lawSuites = response.data.hits.map(r => ({
            id: r['_source']['案号'],
            reason: r['_source']['案由'],
            prosecutor: r['_source']['当事人'].split(',')[0],
            defendant: r['_source']['当事人'].split(',')[1]
          }));
        }).catch((e) => console.log(e));
    }
  }
}
</script>

<style scoped>
.law-detail {
  padding-bottom: var(--spacing-2xl);
}

.validity-bar {
  padding: var(--spacing-md) 0;
}

/* 国家网格 */
.country-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--spacing-md);
}
.country-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: var(--spacing-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}
.country-flag {
  font-size: 24px;
}
.country-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.country-status {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 20px;
}
.status--approved {
  color: var(--color-success);
  background: rgba(45, 138, 86, 0.1);
}
.status--applied {
  color: var(--color-warning);
  background: rgba(197, 136, 12, 0.1);
}
.status--none {
  color: var(--color-text-tertiary);
  background: var(--color-bg);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-xl);
}
</style>
