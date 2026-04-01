<template>
  <div class="report-print">
    <div class="report-print__actions no-print">
      <button class="md3-btn md3-btn--filled" @click="exportPDF">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18"><path d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        导出 PDF
      </button>
      <button class="md3-btn md3-btn--outlined" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18"><path d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
        返回
      </button>
    </div>
    <div class="report-print__inner">
      <h1 class="report-print__title">《{{ patentTitle }}》<br/>专利评估报告</h1>
      <h2 class="report-section">总体评估情况</h2>
      <pat-eva-general />
      <h2 class="report-section">市场要素</h2>
      <pat-eva-detailed-market />
      <h2 class="report-section">专利组合要素</h2>
      <pat-eva-detailed-group />
      <h2 class="report-section">法律要素</h2>
      <pat-eva-detailed-law />
      <h2 class="report-section">技术要素</h2>
      <pat-eva-detailed-tech />
    </div>
  </div>
</template>

<script>
import PatEvaGeneral from "../components/pat_evaluation/general/general.vue";
import PatEvaDetailedMarket from '../components/pat_evaluation/detailed/market.vue';
import PatEvaDetailedGroup from "../components/pat_evaluation/detailed/group.vue";
import PatEvaDetailedLaw from "../components/pat_evaluation/detailed/law.vue";
import PatEvaDetailedTech from "../components/pat_evaluation/detailed/tech.vue";
import axios from "axios";
let GET_BASIC_INFO_URI = "/api/basicinfo/get_patent_info";

export default {
  data() { return { patentTitle: "" }; },
  mounted() {
    let patentId = this.$store.state.patentId;
    axios.get(GET_BASIC_INFO_URI + "?patid=" + patentId).then((r) => { this.patentTitle = r['data']['专利名']; });
  },
  methods: {
    exportPDF() {
      // 将 ECharts 图表转为静态图片，确保打印时能正常显示
      let charts = document.querySelectorAll('.echarts canvas');
      let originals = [];
      charts.forEach((canvas) => {
        let img = document.createElement('img');
        img.src = canvas.toDataURL('image/png');
        img.style.width = '100%';
        img.style.height = canvas.style.height || '300px';
        img.className = 'print-chart-img';
        let parent = canvas.closest('.echarts');
        if (parent) {
          originals.push({ parent: parent, display: parent.style.display });
          let imgWrap = document.createElement('div');
          imgWrap.className = 'print-chart-wrap';
          imgWrap.appendChild(img);
          parent.parentNode.insertBefore(imgWrap, parent);
          parent.style.display = 'none';
        }
      });

      this.$nextTick(() => {
        window.print();
        // 打印后恢复
        document.querySelectorAll('.print-chart-wrap').forEach(el => el.remove());
        originals.forEach(o => { o.parent.style.display = o.display || ''; });
      });
    }
  },
  components: { PatEvaGeneral, PatEvaDetailedMarket, PatEvaDetailedGroup, PatEvaDetailedLaw, PatEvaDetailedTech }
}
</script>

<style scoped>
.report-print { background: var(--md-surface-container-lowest); min-height: 100vh; }
.report-print__actions { display: flex; gap: var(--space-md); justify-content: center; padding: var(--space-lg) 0 0; }
.report-print__inner { max-width: 800px; margin: 0 auto; padding: var(--space-2xl) var(--space-lg); }
.report-print__title { text-align: center; font-size: 24px; font-weight: 700; color: var(--md-on-surface); margin-bottom: var(--space-2xl); line-height: 1.6; counter-reset: chapter; }
.report-section { font-size: 18px; font-weight: 600; color: var(--md-on-surface); margin: var(--space-xl) 0 var(--space-md); padding-bottom: var(--space-sm); border-bottom: 2px solid var(--md-outline-variant); }
.report-section::before { counter-increment: chapter; content: counter(chapter) ". "; }
.report-print__inner >>> .card { border: none; box-shadow: none; padding: var(--space-md) 0; margin-bottom: var(--space-sm); }
.report-print__inner >>> .card:hover { box-shadow: none; }
.report-print__inner >>> .card-header { border-bottom: none; padding-bottom: var(--space-xs); }

/* MD3 按钮 */
.md3-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 28px; font-size: 14px; font-weight: 500;
  font-family: var(--font-sans); border-radius: var(--radius-full);
  cursor: pointer; transition: all 0.2s cubic-bezier(0.2, 0, 0, 1); border: none;
}
.md3-btn--filled { background: var(--md-primary); color: var(--md-on-primary); }
.md3-btn--filled:hover { box-shadow: var(--elevation-1); background: var(--sci-accent); }
.md3-btn--outlined { background: transparent; color: var(--md-primary); border: 1px solid var(--md-outline); }
.md3-btn--outlined:hover { background: var(--sci-accent-light); }

/* 打印样式 */
@media print {
  .no-print { display: none !important; }
  .report-print { padding: 0; }
  .report-print__inner { max-width: 100%; padding: 0 20mm; }
  .report-section { page-break-before: always; }
  .report-section:first-of-type { page-break-before: avoid; }
  .report-print__inner >>> .echarts { break-inside: avoid; }
  .report-print__inner >>> .el-table { break-inside: avoid; }
}
</style>
