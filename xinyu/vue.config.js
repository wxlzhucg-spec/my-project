/** H5 开发可选代理：设置 XINYU_USE_PROXY=1 后，与 utils/api.js 中 API_BASE='' 配合使用 */
var API_DEV_TARGET = process.env.XINYU_API_PROXY || 'http://43.143.169.226:5001'

module.exports = {
	devServer: {
		proxy: {
			'^/user': {
				target: API_DEV_TARGET,
				changeOrigin: true
			},
			'^/emotion': {
				target: API_DEV_TARGET,
				changeOrigin: true
			}
		}
	}
}
