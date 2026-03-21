<template>
  <div class="market-detail">
    <title-canvas title="相关领域专利申请趋势">
      <div class="chart-wrap"><e-chart :options="applyTrends" :auto-resize="true" /></div>
    </title-canvas>
    <title-canvas title="相关领域市场交易趋势">
      <div class="chart-wrap"><e-chart :options="tradeTrends" :auto-resize="true" /></div>
    </title-canvas>
    <title-canvas title="相似专利及交易价格">
      <el-table :data="similarPatents" style="width:100%" :header-cell-style="tableHeaderStyle">
        <el-table-column type="index" label="#" width="56" align="center" />
        <el-table-column prop="title" label="专利名称" min-width="300">
          <template slot-scope="scope"><span style="font-weight:500">{{ scope.row.title }}</span></template>
        </el-table-column>
        <el-table-column prop="similarity" label="相似性" width="120" align="center">
          <template slot-scope="scope"><span class="badge-val">{{ scope.row.similarity }}</span></template>
        </el-table-column>
        <el-table-column prop="value" label="交易价格（万元）" width="160" align="right">
          <template slot-scope="scope"><span class="text-mono">{{ scope.row.value }}</span></template>
        </el-table-column>
      </el-table>
    </title-canvas>
    <title-canvas title="市场交易价格">
      <div class="price-display">
        <span class="price-currency">¥</span>
        <span class="price-value">{{ patValue[0] }}</span>
        <span class="price-sep">~</span>
        <span class="price-value">{{ patValue[1] }}</span>
        <span class="price-unit">万元</span>
      </div>
    </title-canvas>
  </div>
</template>

<script>
import axios from "axios";
import _ from "lodash";
import { sprintf } from "sprintf-js";
import barChartTemplate from "../../common/bar_chart_template.js";
import lineChartTemplate from "../../common/line_chart_template";
let APPLY_TRENDING_URL = '/api/marketfactor/applytrending';
let TRADE_TRENDING_URL = '/api/marketfactor/tradetrending';
let SIMILAR_PATENT_URL = '/api/marketfactor/similarpatents';
let ESTIMATE_PRICE_URL = '/api/marketfactor/estimateprice';

export default {
  data() {
    let applyTrends = _.cloneDeep(lineChartTemplate); applyTrends.xAxis.name = "年份"; applyTrends.yAxis.name = "申请数量";
    let tradeTrends = _.cloneDeep(barChartTemplate); tradeTrends.xAxis.name = "年份"; tradeTrends.yAxis.name = "交易金额(万元)";
    return { applyTrends, tradeTrends, similarPatents: [], totalNum: 0, patValue: ['', ''] }
  },
  computed: {
    tableHeaderStyle() { return { background: 'var(--md-surface-container)', color: 'var(--md-on-surface-variant)', fontWeight: '600', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em' } }
  },
  methods: {
    reqSimlarPats(start, size) {
      axios.get(SIMILAR_PATENT_URL + "?patid=" + this.$store.state.patentId + "&start=" + start + "&size=" + size).then((response) => {
        this.totalNum = response['data']['total'];
        let similarPatents = [];
        for (const hit of response['data'].hits) { similarPatents.push({ title: hit['_source']["专利名"], similarity: sprintf("%.2f", hit['similarity'] * 100) + "%", value: hit['_source']['转化收益（万元）'] }); }
        this.similarPatents = similarPatents;
      }).catch((e) => console.log(e));
    }
  },
  mounted() {
    let patentId = this.$store.state.patentId;
    if (patentId !== null) {
      axios.get(APPLY_TRENDING_URL + "?patid=" + patentId).then((response) => {
        let data = response.data.apply_per_year.buckets; let years = [], counts = [];
        for (const i in data) { years.push(new Date(data[i].key).getFullYear()); counts.push(data[i].doc_count); }
        this.applyTrends.xAxis.data = years; this.applyTrends.series[0].data = counts;
      }).catch((e) => console.log(e));
      this.reqSimlarPats(0, 5);
      axios.get(TRADE_TRENDING_URL + "?patid=" + patentId).then((response) => {
        let data = response.data.apply_per_year.buckets; let years = [], amounts = [];
        for (const i in data) { years.push(new Date(data[i].key).getFullYear()); amounts.push(data[i].trade_per_year.value); }
        this.tradeTrends.xAxis.data = years; this.tradeTrends.series[0].data = amounts;
      }).catch((e) => console.log(e));
      axios.get(ESTIMATE_PRICE_URL + "?patid=" + patentId).then((response) => {
        let basePrice = response.data.price;
        this.patValue = [sprintf('%.2f', basePrice - basePrice * 0.35), sprintf('%.2f', basePrice + basePrice * 0.35)];
      }).catch((e) => console.log(e));
    }
  }
}
</script>

<style scoped>
.market-detail { padding-bottom: var(--space-2xl); }
.chart-wrap { padding: var(--space-sm) 0; }
.chart-wrap .echarts { width: 100%; height: 300px; }
.badge-val { display: inline-block; font-size: 12px; font-weight: 600; color: var(--md-on-primary-container); background: var(--md-primary-container); padding: 3px 12px; border-radius: var(--radius-full); font-family: var(--font-mono); }
.price-display { display: flex; align-items: baseline; justify-content: center; gap: 6px; padding: var(--space-md) 0; }
.price-currency { font-size: 18px; font-weight: 600; color: var(--md-on-surface-variant); }
.price-value { font-size: 32px; font-weight: 700; color: var(--md-primary); font-family: var(--font-mono); }
.price-sep { font-size: 20px; color: var(--md-outline); margin: 0 4px; }
.price-unit { font-size: 15px; font-weight: 500; color: var(--md-on-surface-variant); margin-left: 4px; }
</style>
