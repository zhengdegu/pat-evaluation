module.exports = {
    transpileDependencies:
        [/\/node_modules\/vue-echarts\//, /\/node_modules\/resize-detector\//],
    baseUrl: '/',
    devServer: {
        proxy: {
            '/api': {
                //target: 'http://gitlab.intelipev.com:9090/',
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                pathRewrite: {'^/api': '/api'}
            }
        }
    }
}