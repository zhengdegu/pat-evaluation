import Vue from 'vue'
import Router from 'vue-router'
import Main from './views/main.vue'
import PatEvaluation from './views/pat_evaluation.vue'
import PatEvaGeneral from "./components/pat_evaluation/general/general.vue";
import PatEvaDetailed from "./components/pat_evaluation/detailed/detailed.vue";
import PatEvaDetailedMarket from './components/pat_evaluation/detailed/market.vue'
import PatEvaDetailedGroup from "./components/pat_evaluation/detailed/group.vue";
import PatEvaDetailedLaw from "./components/pat_evaluation/detailed/law.vue";
import PatEvaDetailedTech from "./components/pat_evaluation/detailed/tech.vue";
import SmartSearch from './views/smart_search.vue'
import FuzzSearch from "./views/fuzz_search.vue";
import Report from "./views/report.vue";
import DataImport from "./views/data_import.vue";

Vue.use(Router)

export default new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        {path: '/', redirect: '/search'},
        {path: '/search', name:"搜索", component: FuzzSearch},
        {path: '/import', name:"数据导入", component: DataImport},
        {path: '/main', name: '生物医药领域专利价值评价', component: Main},
        {path: '/print_report', name:'报告打印版本', component: Report},
        {path: '/smart-search', name: '生物医药领域专利价值评价', component: SmartSearch}, {
            path: '/pat-evaluation',
            name: '生物医药领域专利价值评价',
            component: PatEvaluation,
            children: [
                {path: '/', name: '总体情况', component: PatEvaGeneral}, {
                    path: 'detailed',
                    name: '评估详情',
                    component: PatEvaDetailed,
                    children: [
                        {
                            path: '/',
                            name: '市场因素',
                            component: PatEvaDetailedMarket
                        },
                        {
                            path: 'group',
                            name: '专利组合要素',
                            component: PatEvaDetailedGroup
                        }, 
                        {
                            path: 'law',
                            name: '法律要素',
                            component: PatEvaDetailedLaw
                        },
                        {
                            path: 'tech',
                            name: '技术要素',
                            component: PatEvaDetailedTech
                        }
                    ]
                }
            ]
        }
    ]
})
