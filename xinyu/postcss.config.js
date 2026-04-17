module.exports = {
  plugins: [
    require('autoprefixer')(),
    require('./postcss-rpx-to-vw')()
  ]
}
