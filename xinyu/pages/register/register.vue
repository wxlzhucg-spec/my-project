<template>
<view class="page">
	<view class="glow"></view>

	<view class="nav-row">
		<view class="nav-back" @tap="goBack"><text class="nav-arrow">‹</text></view>
		<text class="nav-title">注册账号</text>
		<view style="width:68rpx;"></view>
	</view>

	<text class="sub-hint">信息将保存至用户表：手机号、密码（由服务端加密）、昵称</text>

	<view class="form-card">
		<view class="form-row">
			<text class="form-label">昵称</text>
			<input class="form-input" v-model="nickname" placeholder="选填，默认用手机号后4位" placeholder-class="form-ph" maxlength="32" />
		</view>
		<view class="form-line"></view>
		<view class="form-row">
			<text class="form-label">手机号</text>
			<input class="form-input" type="number" v-model="phone" placeholder="11位手机号" placeholder-class="form-ph" maxlength="11" />
		</view>
		<view class="form-line"></view>
		<view class="form-row">
			<text class="form-label">密码</text>
			<input class="form-input" password v-model="password" placeholder="至少6位" placeholder-class="form-ph" maxlength="32" />
		</view>
		<view class="form-line"></view>
		<view class="form-row">
			<text class="form-label">确认密码</text>
			<input class="form-input" password v-model="password2" placeholder="再输入一次" placeholder-class="form-ph" maxlength="32" />
		</view>
	</view>

	<view class="agree-row" @tap="toggleAgree">
		<view class="agree-box" :class="{ on: agreed }"><text v-if="agreed" class="agree-tick">✓</text></view>
		<text class="agree-txt">我已阅读并同意《用户协议》与《隐私政策》</text>
	</view>

	<view class="save-btn" hover-class="save-hover" @tap="submit">
		<text class="save-text">注册</text>
	</view>

	<view class="foot-switch" @tap="goLogin">
		<text class="foot-switch-t">已有账号？去登录</text>
	</view>

	<view class="foot-hint">
		<text class="foot-txt">接口：POST {{ apiHint }}</text>
	</view>

	<view style="height:80rpx;"></view>
</view>
</template>

<script>
import { API_BASE, REGISTER_PATH, postRegister, postLogin, describeRequestError } from '@/utils/api.js'

export default {
	data: function() {
		return {
			nickname: '',
			phone: '',
			password: '',
			password2: '',
			agreed: false,
			submitting: false
		}
	},
	computed: {
		apiHint: function() {
			return API_BASE + REGISTER_PATH
		}
	},
	methods: {
		goBack: function() {
			if (getCurrentPages().length > 1) { uni.navigateBack(); return }
			uni.reLaunch({ url: '/pages/index/index' })
		},
		goLogin: function() {
			uni.redirectTo({ url: '/pages/login/login' })
		},
		toggleAgree: function() {
			this.agreed = !this.agreed
		},
		submit: function() {
			if (this.submitting) return
			var phone = (this.phone || '').trim()
			var pwd = this.password || ''
			var pwd2 = this.password2 || ''
			if (!/^1\d{10}$/.test(phone)) {
				uni.showToast({ title: '请输入正确手机号', icon: 'none' })
				return
			}
			if (pwd.length < 6) {
				uni.showToast({ title: '密码至少6位', icon: 'none' })
				return
			}
			if (pwd !== pwd2) {
				uni.showToast({ title: '两次密码不一致', icon: 'none' })
				return
			}
			if (!this.agreed) {
				uni.showToast({ title: '请先勾选同意协议', icon: 'none' })
				return
			}
			var nick = (this.nickname || '').trim()
			if (!nick) {
				nick = '用户' + phone.slice(-4)
			}
			var self = this
			var registerOk = false
			this.submitting = true
			uni.showLoading({ title: '提交中', mask: true })
			postRegister({ phone: phone, password: pwd, nickname: nick, terms_agreed: true })
				.then(function() {
					registerOk = true
					uni.showLoading({ title: '正在登录', mask: true })
					return postLogin({ phone: phone, password: pwd })
				})
				.then(function() {
					uni.hideLoading()
					uni.showToast({ title: '注册成功，已登录', icon: 'success' })
					setTimeout(function() {
						self.goBack()
					}, 600)
				})
				.catch(function(err) {
					uni.hideLoading()
					var raw = (err && err.errMsg) || (err && err.message) || '注册失败'
					if (registerOk) {
						uni.showToast({ title: '注册成功，自动登录失败，请稍后重试', icon: 'none', duration: 2800 })
						return
					}
					if (raw.indexOf('request:fail') >= 0 || raw === '网络请求失败') {
						raw = describeRequestError(err)
					}
					/* 后端 409：手机号已存在 */
					if (raw.indexOf('409') >= 0 || raw.indexOf('已注册') >= 0) {
						raw = '该手机号已注册，请直接登录或换手机号'
					}
					uni.showToast({ title: raw.length > 22 ? raw.slice(0, 20) + '…' : raw, icon: 'none', duration: 2800 })
				})
				.then(function() {
					self.submitting = false
				})
		}
	}
}
</script>

<style scoped>
.page {
	padding-top: env(safe-area-inset-top);
	min-height: 100vh;
	padding-left: 36rpx; padding-right: 36rpx;
	background: linear-gradient(180deg, #d6d0e2 0%, #c8c0d8 30%, #b8aece 60%, #a498be 100%);
	position: relative;
}
.glow {
	position: absolute;
	top: -60rpx; left: -20%;
	width: 140%; height: 600rpx;
	background: radial-gradient(ellipse at 50% 30%, rgba(255,255,255,0.22) 0%, transparent 65%);
	pointer-events: none;
}
.nav-row {
	display: flex; align-items: center; justify-content: space-between;
	padding: 20rpx 0 12rpx;
	position: relative; z-index: 2;
}
.nav-back {
	width: 68rpx; height: 68rpx;
	display: flex; align-items: center; justify-content: center;
	border-radius: 50%;
	background: rgba(255,255,255,0.5);
}
.nav-arrow { font-size: 40rpx; color: #4a3d68; font-weight: 300; }
.nav-title { font-size: 34rpx; font-weight: 700; color: #2d2048; letter-spacing: 2rpx; }
.sub-hint {
	display: block;
	font-size: 24rpx;
	color: rgba(45,32,72,0.55);
	line-height: 1.5;
	padding: 0 8rpx 24rpx;
	position: relative; z-index: 2;
}
.form-card {
	background: rgba(255,255,255,0.82);
	border-radius: 28rpx;
	padding: 0 32rpx;
	border: 1rpx solid rgba(255,255,255,0.5);
	box-shadow: 0 6rpx 24rpx rgba(80,60,130,0.07);
	position: relative; z-index: 2;
}
.form-row {
	display: flex;
	align-items: center;
	min-height: 108rpx;
	padding: 12rpx 0;
}
.form-label {
	width: 160rpx; flex-shrink: 0;
	font-size: 28rpx; font-weight: 600; color: #2d2048;
}
.form-input {
	flex: 1;
	font-size: 28rpx; font-weight: 500; color: #2d2048;
	height: 80rpx;
}
.form-ph { font-size: 28rpx; color: #b8b0c8; }
.form-line {
	height: 1rpx;
	background: rgba(100,80,140,0.06);
	margin-left: 160rpx;
}
.agree-row {
	display: flex;
	align-items: flex-start;
	margin-top: 28rpx;
	padding: 0 8rpx;
	position: relative; z-index: 2;
}
.agree-box {
	width: 36rpx; height: 36rpx;
	border-radius: 8rpx;
	border: 2rpx solid rgba(92,77,128,0.35);
	margin-right: 16rpx;
	margin-top: 4rpx;
	flex-shrink: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(255,255,255,0.5);
}
.agree-box.on {
	background: #5c4d80;
	border-color: #5c4d80;
}
.agree-tick { font-size: 22rpx; color: #fff; font-weight: 700; }
.agree-txt {
	font-size: 24rpx;
	color: rgba(45,32,72,0.65);
	line-height: 1.45;
}
.save-btn {
	margin-top: 40rpx;
	height: 96rpx; border-radius: 48rpx;
	background: linear-gradient(135deg, #7c6cb8 0%, #5c4d90 50%, #6c5ca8 100%);
	display: flex; align-items: center; justify-content: center;
	box-shadow: 0 8rpx 28rpx rgba(92,77,144,0.3);
	position: relative; z-index: 2;
}
.save-hover { opacity: 0.88; transform: scale(0.98); }
.save-text {
	font-size: 32rpx; font-weight: 700;
	color: #fff; letter-spacing: 12rpx;
	padding-left: 12rpx;
}
.foot-switch {
	margin-top: 28rpx;
	padding: 0 8rpx;
	display: flex;
	justify-content: center;
	position: relative; z-index: 2;
}
.foot-switch-t {
	font-size: 26rpx;
	color: #5c4d90;
	text-decoration: underline;
}
.foot-hint {
	margin-top: 24rpx;
	padding: 0 8rpx;
	position: relative; z-index: 2;
}
.foot-txt {
	font-size: 22rpx;
	color: rgba(45,32,72,0.4);
	word-break: break-all;
}
</style>
