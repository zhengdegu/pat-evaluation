import Vue from 'vue'
import Vuex from 'vuex'
import _ from "lodash";

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        patentId: null,
        patentTitle: null
    },
    mutations: {
        // 保存patent的id信息
        setPatentId(state, id) {
            if (_.isUndefined(id) || id === null || id === ''){
                state.patentId = null
            } else
                state.patentId = id;
        },
        // 保存title信息
        setPatentTitle(state, title) {
            state.patentTitle = title;
        }
    },
    actions: {}
})
