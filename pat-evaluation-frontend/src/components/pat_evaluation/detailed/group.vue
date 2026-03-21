<template>
  <div class="group-detail">
    <title-canvas title="专利申请人专利分布">
      <div class="chart-wrap"><e-chart :options="applyDistribution" :auto-resize="true" /></div>
    </title-canvas>
    <title-canvas title="专利依赖关系">
      <div class="empty-state"><span class="text-tertiary">暂无数据</span></div>
    </title-canvas>
  </div>
</template>

<script>
import axios from "axios";
import _ from "lodash";
import barChartTemplate from "../../common/bar_chart_template.js";
let DISTRIBUTION_URL = "/api/combinationfactor/distribution";

export default {
  data() {
    let applyDistribution = _.cloneDeep(barChartTemplate); applyDistribution.xAxis.name = "分类"; applyDistribution.yAxis.name = "持有数量";
    return { applyDistribution };
  },
  mounted() {
    let patentId = this.$store.state.patentId;
    if (patentId !== null) {
      axios.get(DISTRIBUTION_URL + "?patid=" + patentId).then((response) => {
        let data = response.data.apply_per_class.buckets; let keys = [], nums = [];
        for (const i of data) { keys.push(i.key); nums.push(i.doc_count); }
        this.applyDistribution.xAxis.data = keys; this.applyDistribution.series[0].data = nums;
      }).catch((e) => console.log(e));
    }
  }
};
</script>

<style scoped>
.group-detail { padding-bottom: var(--space-2xl); }
.chart-wrap { padding: var(--space-sm) 0; }
.chart-wrap .echarts { width: 100%; height: 300px; }
.empty-state { text-align: center; padding: var(--space-xl); }
</style>
