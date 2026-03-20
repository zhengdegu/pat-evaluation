import {library} from '@fortawesome/fontawesome-svg-core'
import {faDollarSign, faDownload, faEuroSign, faSearch, faShareAlt, faHome} from '@fortawesome/free-solid-svg-icons'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import Vue from 'vue'

library.add(faSearch, faEuroSign, faShareAlt, faDownload, faDollarSign, faHome)
Vue.component('font-awesome-icon', FontAwesomeIcon)