const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    allowedHosts: 'all',
    host: process.env.DEV_SERVER_HOST || '0.0.0.0',
    port: process.env.DEV_SERVER_PORT || 8080,
    https: process.env.DEV_SERVER_HTTPS === 'true',
    client: {
      webSocketURL: {
        protocol: 'ws',
        hostname: '127.0.0.1',
        port: 443,
      },
    },
  },
})
