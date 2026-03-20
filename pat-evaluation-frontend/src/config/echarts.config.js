import Vue from 'vue'
import ECharts from 'vue-echarts/components/ECharts.vue'

import 'echarts/lib/chart/bar'
import 'echarts/lib/chart/line'

// 雷达图
import "echarts/lib/chart/radar"
import 'echarts/lib/component/radar'

Vue.component('e-chart', ECharts)