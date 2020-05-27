import Vue from 'vue'
import Router from 'vue-router'
// import Mixup from '@/components/Mixup'
// import Fusion from '@/components/Fusion'
// import Cards from '@/components/Cards'
// import HelloWorld from '@/components/HelloWorld'

Vue.use(Router)

let head = document.getElementsByTagName('head');
let meta = document.createElement('meta');
meta.name = 'referrer';
//根据实际情况修改referrer的值，可选值参考上文
meta.content = 'no-referrer';
head[0].appendChild(meta);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: (resolve) => require(['./components/Mixup.vue'], resolve)
    },
    {
      path: '/movies',
      name: 'movies',
      component: (resolve) => require(['./components/Cards.vue'], resolve)
    },
    {
      path: '/mixup',
      name: 'mixup',
      component: (resolve) => require(['./components/Mixup.vue'], resolve)
    },
    {
      path: '/fusion',
      name: 'fusion',
      component: (resolve) => require(['./components/Fusion.vue'], resolve)
    },
  ]
})
