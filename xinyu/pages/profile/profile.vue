<template>
	<view class="container" :style="containerStyle">
		<view class="top-bg-glow"></view>
		<text class="page-title">我的</text>

		<!-- 用户信息头部 -->
		<view class="user-header" @tap="goEditProfile">
			<view class="avatar-container">
				<image v-if="userInfo.avatar" class="avatar" :src="userInfo.avatar" mode="aspectFill"></image>
				<view v-else class="avatar avatar-empty"><text class="avatar-empty-text">+</text></view>
				<view class="avatar-badge"></view>
			</view>
			<view class="user-info">
				<view class="name-row">
					<text class="nickname">{{ userInfo.nickname }}</text>
					<view class="vip-tag" v-if="userInfo.mbti">{{ userInfo.mbti }}</view>
				</view>
				<text class="sub-desc">{{ userInfo.desc }}</text>
			</view>
			<view class="arrow-icon">›</view>
		</view>

		<!-- 统计数据面板 -->
		<view class="stats-panel">
			<view class="stat-item">
				<text class="stat-val">12</text>
				<text class="stat-label">记录/天</text>
			</view>
			<view class="stat-item">
				<text class="stat-val">3</text>
				<text class="stat-label">报告/份</text>
			</view>
			<view class="stat-item">
				<text class="stat-val">89</text>
				<text class="stat-label">平均/分</text>
			</view>
		</view>

		<!-- 测试记录 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">测试记录</text>
			</view>
			<view class="record-list">
				<view class="record-item" v-for="(item, index) in testRecords" :key="index">
					<view class="record-icon test-icon"></view>
					<view class="record-content">
						<text class="record-name">{{ item.title }}</text>
						<text class="record-date">{{ item.date }}</text>
					</view>
					<view class="record-tag"><text>{{ item.tag }}</text></view>
				</view>
			</view>
		</view>

		<!-- 报告记录 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">报告记录</text>
			</view>
			<view class="record-list">
				<view class="record-item" v-for="(item, index) in reportRecords" :key="index">
					<view class="record-icon report-icon"></view>
					<view class="record-content">
						<text class="record-name">{{ item.title }}</text>
						<text class="record-date">{{ item.date }}</text>
					</view>
					<view class="record-action"><text>查看</text></view>
				</view>
			</view>
		</view>

		<view class="auth-links">
			<view class="auth-link" @tap="goLogin">
				<text class="auth-link-t">已有账号？去登录</text>
			</view>
			<view class="auth-link" @tap="goRegister">
				<text class="auth-link-t">没有账号？去注册</text>
			</view>
		</view>

		<custom-tabbar :list="navList" />
	</view>
</template>

<script>
	import customTabbar from '@/components/custom-tabbar/custom-tabbar.vue'
	import { getApiUserId, getApiUserPhone, getUser } from '@/utils/api.js'

	export default {
		components: {
			customTabbar
		},
		onShow: function() {
			this.loadUserProfile()
		},
		data() {
			return {
				userInfo: {
					nickname: '点击完善资料',
					desc: '已守护你的情绪 12 天',
					avatar: '',
					mbti: ''
				},
				testRecords: [
					{ title: 'MBTI 职业性格测试', date: '2026-03-20', tag: '性格' },
					{ title: 'SCL-90 症状自评量表', date: '2026-03-15', tag: '健康' }
				],
				reportRecords: [
					{ title: '2026年3月 心理健康月报', date: '2026-03-21' },
					{ title: '深度人格解析报告', date: '2026-03-16' }
				],
				navList: [
					{ label: '首页', active: false, path: '/pages/index/index' },
					{ label: '探索', active: false, path: '/pages/explore/explore' },
					{ label: '影子', active: false, path: '/pages/shadow/shadow' },
					{ label: '我的', active: true, path: '/pages/profile/profile' }
				]
			}
		},
		methods: {
			goRegister: function() {
				uni.navigateTo({ url: '/pages/register/register' })
			},
			goLogin: function() {
				uni.navigateTo({ url: '/pages/login/login' })
			},
			loadUserProfile: function() {
				var uid = getApiUserId()
				if (uid) {
					this.loadRemoteProfile(uid)
					return
				}
				var phone = getApiUserPhone()
				if (phone) {
					this.loadRemoteProfileByPhone(phone)
					return
				}
				this.loadCachedProfile()
			},
			loadCachedProfile: function() {
				var raw = uni.getStorageSync('userProfile')
				if (raw) {
					try {
						var d = JSON.parse(raw)
						this.userInfo.nickname = d.nickname || '点击完善资料'
						this.userInfo.avatar = d.avatar || ''
						this.userInfo.mbti = d.mbti || ''
					} catch (e) {}
				}
			},
			loadRemoteProfile: function(uid) {
				var self = this
				getUser({ id: uid })
					.then(function(res) {
						if (res && res.data) {
							var d = res.data
							self.userInfo.nickname = d.nickname || '点击完善资料'
							self.userInfo.avatar = d.avatar_url || ''
							self.userInfo.mbti = d.mbti || ''
							uni.setStorageSync('userProfile', JSON.stringify({
								avatar: d.avatar_url || '',
								nickname: d.nickname || '',
								gender: d.gender || '',
								birthDate: d.birth_date || '',
								birthTime: d.birth_time || '',
								birthRegion: [d.birth_province || '', d.birth_city || '', d.birth_district || ''],
								mbti: d.mbti || ''
							}))
						} else {
							self.loadCachedProfile()
						}
					})
					.catch(function() {
						self.loadCachedProfile()
					})
			},
			loadRemoteProfileByPhone: function(phone) {
				var self = this
				getUser({ phone: phone })
					.then(function(res) {
						if (res && res.data) {
							var d = res.data
							self.userInfo.nickname = d.nickname || '点击完善资料'
							self.userInfo.avatar = d.avatar_url || ''
							self.userInfo.mbti = d.mbti || ''
							if (d.id != null && d.id !== '') {
								try {
									uni.setStorageSync('xinyu_user_id', Number(d.id))
								} catch (e0) {}
							}
							uni.setStorageSync('userProfile', JSON.stringify({
								avatar: d.avatar_url || '',
								nickname: d.nickname || '',
								gender: d.gender || '',
								birthDate: d.birth_date || '',
								birthTime: d.birth_time || '',
								birthRegion: [d.birth_province || '', d.birth_city || '', d.birth_district || ''],
								mbti: d.mbti || ''
							}))
						} else {
							self.loadCachedProfile()
						}
					})
					.catch(function() {
						self.loadCachedProfile()
					})
			},
			goEditProfile: function() {
				uni.navigateTo({ url: '/pages/profile-edit/profile-edit' })
			}
		},
		computed: {
			containerStyle() {
				var statusBarHeight = 44
				try {
					var info = uni.getWindowInfo ? uni.getWindowInfo() : uni.getSystemInfoSync()
					if (info && info.statusBarHeight) {
						statusBarHeight = info.statusBarHeight
					}
				} catch (e) {}
				return {
					paddingTop: 'calc(' + statusBarHeight + 'px + 20rpx)',
					paddingBottom: 'calc(240rpx + env(safe-area-inset-bottom))'
				}
			}
		}
	}
</script>

<style scoped>
	.container {
		padding: 35rpx;
		background: linear-gradient(180deg, #d6d0e2 0%, #c8c0d8 30%, #b8aece 60%, #a498be 100%);
		min-height: 100vh;
		position: relative;
		overflow-x: hidden;
	}

	.top-bg-glow {
		position: absolute;
		top: -60rpx;
		left: -20%;
		width: 140%;
		height: 600rpx;
		background: radial-gradient(ellipse at 50% 30%, rgba(255,255,255,0.22) 0%, transparent 65%);
		pointer-events: none;
		z-index: 0;
	}

	.page-title {
		font-size: 40rpx;
		font-weight: bold;
		color: #2d2048;
		margin-bottom: 40rpx;
		display: block;
		position: relative;
		z-index: 1;
	}

	.user-header {
		display: flex;
		align-items: center;
		padding: 30rpx 10rpx 50rpx 10rpx;
		position: relative;
		z-index: 1;
	}

	.avatar-container {
		position: relative;
		width: 140rpx;
		height: 140rpx;
		margin-right: 32rpx;
	}

	.avatar {
		width: 100%;
		height: 100%;
		border-radius: 70rpx;
		border: 4rpx solid rgba(255, 255, 255, 0.7);
		box-shadow: 0 8rpx 24rpx rgba(80, 60, 130, 0.1);
		background-color: rgba(255, 255, 255, 0.6);
	}
	.avatar-empty {
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.avatar-empty-text {
		font-size: 52rpx;
		color: #b0a4c4;
		font-weight: 200;
	}

	.avatar-badge {
		position: absolute;
		right: 0;
		bottom: 8rpx;
		width: 28rpx;
		height: 28rpx;
		background: #8878a8;
		border: 4rpx solid #ffffff;
		border-radius: 50%;
	}

	.user-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.name-row {
		display: flex;
		align-items: center;
		margin-bottom: 12rpx;
	}

	.nickname {
		font-size: 40rpx;
		font-weight: 700;
		color: #2d2048;
		letter-spacing: 1rpx;
	}

	.vip-tag {
		background: linear-gradient(135deg, rgba(136, 120, 168, 0.8), rgba(80, 60, 120, 0.8));
		color: #ffffff;
		font-size: 20rpx;
		font-weight: 600;
		padding: 4rpx 12rpx;
		border-radius: 12rpx;
		margin-left: 16rpx;
	}

	.sub-desc {
		font-size: 26rpx;
		color: rgba(45, 32, 72, 0.7);
	}

	.arrow-icon {
		font-size: 32rpx;
		color: rgba(45, 32, 72, 0.5);
		font-family: monospace;
	}

	.stats-panel {
		display: flex;
		background: rgba(255, 255, 255, 0.82);
		border-radius: 32rpx;
		padding: 40rpx 20rpx;
		margin-bottom: 24rpx;
		box-shadow: 0 6rpx 24rpx rgba(80, 60, 130, 0.07);
		border: 1rpx solid rgba(255,255,255,0.5);
		position: relative;
		z-index: 1;
	}

	.stat-item {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		border-right: 1rpx solid rgba(100, 80, 140, 0.1);
	}
	
	.stat-item:last-child {
		border-right: none;
	}

	.stat-val {
		font-size: 36rpx;
		font-weight: 700;
		color: #2d2048;
		margin-bottom: 8rpx;
	}

	.stat-label {
		font-size: 24rpx;
		color: #6c5c88;
	}

	.section-card {
		background: rgba(255, 255, 255, 0.82);
		border-radius: 32rpx;
		padding: 36rpx 32rpx;
		margin-bottom: 24rpx;
		box-shadow: 0 6rpx 24rpx rgba(80, 60, 130, 0.07);
		border: 1rpx solid rgba(255,255,255,0.5);
		position: relative;
		z-index: 1;
	}

	.section-header {
		margin-bottom: 28rpx;
	}

	.section-title {
		font-size: 28rpx;
		font-weight: 600;
		color: #2d2048;
	}

	.record-list {
		display: flex;
		flex-direction: column;
	}

	.record-item {
		display: flex;
		align-items: center;
		padding: 24rpx 0;
		border-bottom: 1rpx solid rgba(100, 80, 140, 0.1);
	}
	
	.record-item:last-child {
		border-bottom: none;
		padding-bottom: 0;
	}

	.record-icon {
		width: 72rpx;
		height: 72rpx;
		border-radius: 20rpx;
		margin-right: 24rpx;
	}

	.test-icon {
		background: linear-gradient(135deg, rgba(232, 245, 233, 0.8), rgba(200, 230, 201, 0.8));
	}

	.report-icon {
		background: linear-gradient(135deg, rgba(227, 242, 253, 0.8), rgba(187, 222, 251, 0.8));
	}

	.record-content {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.record-name {
		font-size: 28rpx;
		color: #2d2048;
		margin-bottom: 8rpx;
		font-weight: 500;
	}

	.record-date {
		font-size: 22rpx;
		color: #6c5c88;
	}

	.record-tag {
		background-color: rgba(100, 80, 140, 0.08);
		padding: 4rpx 12rpx;
		border-radius: 8rpx;
	}

	.record-tag text {
		font-size: 20rpx;
		color: #6c5c88;
	}

	.record-action {
		padding: 8rpx 20rpx;
		border-radius: 20rpx;
		border: 1rpx solid rgba(100, 80, 140, 0.12);
		background: rgba(100, 80, 140, 0.06);
	}

	.record-action text {
		font-size: 22rpx;
		color: #6c5c88;
		font-weight: 500;
	}

	.auth-links {
		padding: 24rpx 0 8rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.auth-link {
		display: flex;
		justify-content: center;
	}
	.auth-link + .auth-link {
		margin-top: 16rpx;
	}
	.auth-link-t {
		font-size: 26rpx;
		color: #5c4d90;
		text-decoration: underline;
	}
</style>
