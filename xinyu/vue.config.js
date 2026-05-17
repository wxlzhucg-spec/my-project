/** H5 开发代理配置 */
var EMOTION_API_TARGET = process.env.XINYU_API_PROXY || 'http://43.143.169.226:5001'
var SHADOW_API_TARGET = process.env.XINYU_SHADOW_PROXY || 'http://43.143.169.226'

module.exports = {
	devServer: {
		proxy: {
			'^/user': {
				target: EMOTION_API_TARGET,
				changeOrigin: true
			},
			'^/emotion': {
				target: EMOTION_API_TARGET,
				changeOrigin: true
			},
			'^/api/': {
				target: SHADOW_API_TARGET,
				changeOrigin: true
			}
		}
	}
}
