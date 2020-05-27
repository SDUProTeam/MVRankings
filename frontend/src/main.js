import Vue from 'vue'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import App from './App'
import Menu from './components/Menu'
import Movie from './components/Movie'
import http from './api/api'
import store from './store'


Vue.use(ElementUI);

Vue.config.productionTip = false

Vue.prototype.$axios = http;

new Vue({
  router, 
  store, 
  render: h => h(Menu)
}).$mount('#menu')

new Vue({
  router,
  store, 
  render: h => h(App)
}).$mount('#app')

Vue.component("movie-item", Movie)

