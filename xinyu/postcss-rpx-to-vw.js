// Converts rpx units to vw for H5 builds.
// 750rpx = 100vw (standard uni-app viewport assumption)
module.exports = function rpxToVw() {
  return function (css) {
    if (process.env.UNI_PLATFORM !== 'h5') return
    css.walkDecls(function (decl) {
      if (decl.value && decl.value.indexOf('rpx') !== -1) {
        decl.value = decl.value.replace(/(\d*\.?\d+)rpx/g, function (_, n) {
          return (parseFloat(n) / 750 * 100).toFixed(5) + 'vw'
        })
      }
    })
  }
}
