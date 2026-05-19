var path = require('path')

var plugins = [
  require('tailwindcss')({ config: path.join(__dirname, 'tailwind.config.js') }),
  require('autoprefixer')()
]

// 仅在小程序平台启用 weapp-tailwindcss 和小程序兼容插件
var platform = process.env.UNI_PLATFORM || ''
var isMP = platform.indexOf('mp-') === 0

if (isMP) {
  try {
    plugins.push(require('weapp-tailwindcss')())
  } catch (e) {}
  plugins.push(require('./postcss-mp-compat')())
}

// 仅在 H5 平台启用 rpx 转 vw
if (platform === 'h5') {
  plugins.push(require('./postcss-rpx-to-vw')())
}

module.exports = {
  plugins: plugins
}
