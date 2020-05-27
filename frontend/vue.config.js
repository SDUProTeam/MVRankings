module.exports = {
  
  publicPath: process.env.NODE_ENV === 'production'
    ? './'
    : './',
  /* 生产环境构建文件的目录 defalut: dist */

  outputDir: "dist",

  /* 放置生成的静态文件目录（js css img） */

  assetsDir: "static",

  /* 指定生成的index.html 输出路径 相对 default: index.html */

  indexPath: "index.html",

  /* 生产环境的source map */

  productionSourceMap: true,
  
  lintOnSave: false, 
  devServer: {
    port: 8181,
    https: false,
    publicPath: '/', // 设置打包文件相对路径
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8008/', //对应自己的接口
        changeOrigin: true,
        ws: true
      }
    }
  }
}
