import './config/elementui.config';
import './config/fontawsome.config';
import './config/echarts.config'
import './config/custom.config'
import './config/flag_config'

import Vue from 'vue';

import App from './App.vue';
import router from './router';
import store from './store';

Vue.config.productionTip = false;

new Vue({ router, store, render: h => h(App) }).$mount('#app');
