<template>
  <div class="general-overview">
    <div class="price-card card">
      <div class="card-header">
        <span class="card-header__indicator"></span>
        <span class="card-header__title">总体价格估计</span>
      </div>
      <div class="price-display">
        <span class="price-currency">¥</span>
        <span class="price-value">{{ patEvalue[0] }}</span>
        <span class="price-sep">~</span>
        <span class="price-value">{{ patEvalue[1] }}</span>
        <span class="price-unit">万元</span>
      </div>
      <p class="price-note">基于多维度因素综合评估得出的价格区间（尚无真实交易数据，仅供参考）</p>
    </div>

    <div class="radar-card card">
      <div class="card-header">
        <span class="card-header__indicator"></span>
        <span class="card-header__title">总体评价概览</span>
      </div>
      <div class="radar-wrap">
        <e-chart ref="radarChart" :options="chartData" :auto-resize="true" style="width:480px;height:380px;" />
      </div>
      <p class="text-tertiary text-right" style="font-size:12px;margin-top:var(--space-sm)">备注：各项评估项的最高取值均为 100</p>
    </div>

    <el-dialog title="评估确认" :visible.sync="dialogVisible" width="420px" center>
      <p style="text-align:center;color:var(--md-on-surface-variant)">专利《{{ this.$store.state.patentTitle }}》尚未评估，是否立即评估？</p>
      <span slot="footer">
        <el-button @click="back()">取消</el-button>
        <el-button type="primary" @click="startEvaluation()">开始评估</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from "axios";
import { sprintf } from "sprintf-js";
let START_URL = '/api/evaluation/start';

function buildRadarOption(values) {
  return {
    title: { show: false },
    radar: {
      name: { color: '#171D1B', fontSize: 14, fontWeight: 600 },
      indicator: [
        { name: '市场因素', max: 120 }, { name: '技术因素', max: 120 },
        { name: '法律因素', max: 120 }, { name: '专利组合因素', max: 120 }
      ],
      splitArea: { areaStyle: { color: ['#E9EFEC', '#F5FBF8', '#E9EFEC', '#F5FBF8'] } },
      splitLine: { lineStyle: { color: '#BFC9C5' } },
      axisLine: { lineStyle: { color: '#BFC9C5' } }
    },
    series: [{
      type: 'radar', symbol: 'circle', symbolSize: 8,
      itemStyle: { color: '#00897B', borderColor: '#fff', borderWidth: 2 },
      lineStyle: { color: '#006B5E', width: 2.5 },
      areaStyle: {
        color: { type: 'radial', x: 0.5, y: 0.5, r: 0.5,
          colorStops: [{ offset: 0, color: 'rgba(0,137,123,0.35)' }, { offset: 1, color: 'rgba(0,137,123,0.06)' }]
        }
      },
      data: [{ value: values, name: '评估情况',
        label: { show: true, color: '#171D1B', fontWeight: 700, fontSize: 14,
          formatter: function(p) { return sprintf("%.1f", p.value); }
        }
      }]
    }]
  };
}

export default {
  data() { return { patEvalue: [0, 0], chartData: buildRadarOption([0, 0, 0, 0]), dialogVisible: false }; },
  mounted() { this.getData(); },
  methods: {
    getData() {
      let patentId = this.$store.state.patentId;
      if (!patentId) { this.dialogVisible = true; return; }
      axios.get(START_URL + "?patid=" + patentId).then((response) => {
        if (response.data['valid'] === false) { this.dialogVisible = true; return; }
        this.showEvaluation(response.data);
      }).catch(() => { this.dialogVisible = true; });
    },
    startEvaluation() {
      let patentId = this.$store.state.patentId;
      axios.get(START_URL + "?patid=" + patentId + "&reload=1").then((response) => {
        this.showEvaluation(response.data); this.dialogVisible = false;
      }).catch((error) => { console.log(error); });
    },
    showEvaluation(data) {
      var values = [data.market_point, data.tech_point, data.combine_point, data.law_point];
      var option = buildRadarOption(values);
      this.$nextTick(function() {
        var chart = this.$refs.radarChart;
        if (chart) { if (chart.chart) chart.chart.setOption(option, true); else this.chartData = option; }
        else this.chartData = option;
      });
      this.patEvalue = [sprintf("%.2f", data.price[0]), sprintf("%.2f", data.price[1])];
    },
    back() { this.dialogVisible = false; this.$router.push('/main'); }
  }
}
</script>

<style scoped>
.general-overview { padding-bottom: var(--space-2xl); }
.price-card { text-align: center; padding: var(--space-xl); }
.price-display { display: flex; align-items: baseline; justify-content: center; gap: 6px; margin: var(--space-md) 0; }
.price-currency { font-size: 20px; font-weight: 600; color: var(--md-on-surface-variant); }
.price-value { font-size: 40px; font-weight: 700; color: var(--md-primary); font-family: var(--font-mono); letter-spacing: -0.02em; }
.price-sep { font-size: 24px; color: var(--md-outline); margin: 0 4px; }
.price-unit { font-size: 16px; font-weight: 500; color: var(--md-on-surface-variant); margin-left: 4px; }
.price-note { font-size: 13px; color: var(--md-outline); }
.radar-wrap { display: flex; justify-content: center; padding: var(--space-lg) 0; }
</style>
