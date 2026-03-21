<template>
  <div class="report-print">
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
  components: { PatEvaGeneral, PatEvaDetailedMarket, PatEvaDetailedGroup, PatEvaDetailedLaw, PatEvaDetailedTech }
}
</script>

<style scoped>
.report-print { background: var(--md-surface-container-lowest); min-height: 100vh; }
.report-print__inner { max-width: 800px; margin: 0 auto; padding: var(--space-2xl) var(--space-lg); }
.report-print__title { text-align: center; font-size: 24px; font-weight: 700; color: var(--md-on-surface); margin-bottom: var(--space-2xl); line-height: 1.6; counter-reset: chapter; }
.report-section { font-size: 18px; font-weight: 600; color: var(--md-on-surface); margin: var(--space-xl) 0 var(--space-md); padding-bottom: var(--space-sm); border-bottom: 2px solid var(--md-outline-variant); }
.report-section::before { counter-increment: chapter; content: counter(chapter) ". "; }
.report-print__inner >>> .card { border: none; box-shadow: none; padding: var(--space-md) 0; margin-bottom: var(--space-sm); }
.report-print__inner >>> .card:hover { box-shadow: none; }
.report-print__inner >>> .card-header { border-bottom: none; padding-bottom: var(--space-xs); }
@media print { .report-print { padding: 0; } .report-print__inner { max-width: 100%; } }
</style>
