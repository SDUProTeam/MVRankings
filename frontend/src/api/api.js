import axios from 'axios';
import qs from 'qs'

axios.defaults.baseURL = process.env.NODE_ENV==='development' ? '/api': "http://39.106.132.48:8008/api"

let http = axios.create({
  timeout: 20000
});

export default {
  search ( data ) {
    return http.get('/search', {'params': data});
  },

  searchForFusion ( data ) {
    return http.get('/fusion', {'params': data});
  },
};