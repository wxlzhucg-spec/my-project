var path = require('path')

module.exports = {
  plugins: [
    require('tailwindcss')({ config: path.join(__dirname, 'tailwind.config.js') }),
    require('autoprefixer')(),
    require('./postcss-rpx-to-vw')()
  ]
}
