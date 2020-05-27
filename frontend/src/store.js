import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    showDialog: false, 
    login: false,
    id: null,
  },
  mutations: {                 //修改数据仓库的事件
    turn(state){
      state.showDialog = !state.showDialog;
    }, 
    turnLogin(state){
      state.login = true;
    }, 
    turnLogout(state){
      state.login = false;
    },
    setId(state, val) {
      state.id = val;
    }
  },
  actions: {                 //推荐使用的异步修改数据仓库
    change(context){   
      context.commit('turn');
   },
   changeIn(context){
     context.commit('turnLogin')
   },
   changeOut(context){
     context.commit('turnLogout')
   },
   changeId(context, val){
     context.commit('setId', val);
   }
  }
})