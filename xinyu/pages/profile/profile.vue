<template>
	<view class="container">
		<view class="top-bg-glow"></view>

		<!-- 用户信息头部 -->
		<view class="user-header" @tap="goEditProfile">
			<view class="avatar-container">
				<view class="avatar" :style="avatarStyle">
					<view v-if="!userInfo.avatar" class="avatar-empty"><text class="avatar-empty-text">+</text></view>
				</view>
				<view class="avatar-badge"><text class="badge-icon">✎</text></view>
			</view>
			<view class="user-info">
				<view class="name-row">
					<text class="nickname">{{ userInfo.nickname }}</text>
					<view class="mbti-tag" v-if="userInfo.mbti">{{ userInfo.mbti }}</view>
				</view>
				<text class="sub-desc">{{ userInfo.desc }}</text>
			</view>
			<text class="arrow-icon">›</text>
		</view>

		<!-- 统计数据面板 -->
		<view class="stats-panel">
			<view class="stat-item">
				<text class="stat-icon">📝</text>
				<text class="stat-val">12</text>
				<text class="stat-label">记录/天</text>
			</view>
			<view class="stat-divider"></view>
			<view class="stat-item">
				<text class="stat-icon">📋</text>
				<text class="stat-val">3</text>
				<text class="stat-label">报告/份</text>
			</view>
			<view class="stat-divider"></view>
			<view class="stat-item">
				<text class="stat-icon">💚</text>
				<text class="stat-val">89</text>
				<text class="stat-label">平均/分</text>
			</view>
		</view>

		<!-- 功能菜单 -->
		<view class="menu-card">
			<view class="menu-item" @tap="goEditProfile">
				<view class="menu-icon-wrap menu-icon-profile">
					<text class="menu-emoji">👤</text>
				</view>
				<text class="menu-label">个人资料</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-sep"></view>
			<view class="menu-item">
				<view class="menu-icon-wrap menu-icon-test">
					<text class="menu-emoji">🧠</text>
				</view>
				<text class="menu-label">心理测试</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-sep"></view>
			<view class="menu-item">
				<view class="menu-icon-wrap menu-icon-report">
					<text class="menu-emoji">📊</text>
				</view>
				<text class="menu-label">健康报告</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-sep"></view>
			<view class="menu-item">
				<view class="menu-icon-wrap menu-icon-setting">
					<text class="menu-emoji">⚙️</text>
				</view>
				<text class="menu-label">设置</text>
				<text class="menu-arrow">›</text>
			</view>
		</view>

		<!-- 测试记录 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">测试记录</text>
				<text class="section-more">全部 ›</text>
			</view>
			<view class="record-list">
				<view class="record-item" v-for="(item, index) in testRecords" :key="index">
					<view class="record-dot" :class="item.dotCls"></view>
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
				<text class="section-more">全部 ›</text>
			</view>
			<view class="record-list">
				<view class="record-item" v-for="(item, index) in reportRecords" :key="index">
					<view class="record-dot" :class="item.dotCls"></view>
					<view class="record-content">
						<text class="record-name">{{ item.title }}</text>
						<text class="record-date">{{ item.date }}</text>
					</view>
					<view class="record-action"><text>查看</text></view>
				</view>
			</view>
		</view>

		<!-- 底部登录 -->
		<view class="auth-area">
			<view class="auth-btn auth-btn-login" @tap="goLogin">
				<text class="auth-btn-t">登录账号</text>
			</view>
			<view class="auth-divider">
				<view class="auth-line"></view>
				<text class="auth-or">或</text>
				<view class="auth-line"></view>
			</view>
			<view class="auth-btn auth-btn-register" @tap="goRegister">
				<text class="auth-btn-t2">注册新账号</text>
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
					{ title: 'MBTI 职业性格测试', date: '2026-03-20', tag: '性格', dotCls: 'dot-green' },
					{ title: 'SCL-90 症状自评量表', date: '2026-03-15', tag: '健康', dotCls: 'dot-blue' }
				],
				reportRecords: [
					{ title: '2026年3月 心理健康月报', date: '2026-03-21', dotCls: 'dot-purple' },
					{ title: '深度人格解析报告', date: '2026-03-16', dotCls: 'dot-orange' }
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
							// 远程头像为空时，从本地缓存补充
							if (!self.userInfo.avatar) {
								var cachedRaw = uni.getStorageSync('userProfile')
								if (cachedRaw) {
									try {
										var cached = JSON.parse(cachedRaw)
										if (cached.avatar) self.userInfo.avatar = cached.avatar
									} catch (e) {}
								}
							}
							uni.setStorageSync('userProfile', JSON.stringify({
								avatar: self.userInfo.avatar,
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
							// 远程头像为空时，从本地缓存补充
							if (!self.userInfo.avatar) {
								var cachedRaw = uni.getStorageSync('userProfile')
								if (cachedRaw) {
									try {
										var cached = JSON.parse(cachedRaw)
										if (cached.avatar) self.userInfo.avatar = cached.avatar
									} catch (e) {}
								}
							}
							if (d.id != null && d.id !== '') {
								try { uni.setStorageSync('xinyu_user_id', Number(d.id)) } catch (e0) {}
							}
							uni.setStorageSync('userProfile', JSON.stringify({
								avatar: self.userInfo.avatar,
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
		avatarStyle() {
			if (this.userInfo.avatar) {
				return { backgroundImage: 'url(' + this.userInfo.avatar + ')' }
			}
			return {}
		}
	}
	}
</script>

<style scoped>
	.container {
		width: 100%;
		box-sizing: border-box;
		padding-top: calc(env(safe-area-inset-top) + 20rpx);
		padding-left: 35rpx; padding-right: 35rpx; padding-bottom: calc(240rpx + env(safe-area-inset-bottom));
		background: linear-gradient(180deg, #ddd8ea 0%, #cec6de 35%, #bfb5d2 65%, #a998c2 100%);
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
		background: radial-gradient(ellipse at 50% 30%, rgba(255,255,255,0.25) 0%, transparent 65%);
		pointer-events: none;
		z-index: 0;
	}

	/* ── 用户头部 ── */
	.user-header {
		display: flex;
		align-items: center;
		padding: 24rpx 10rpx 44rpx;
		position: relative;
		z-index: 1;
	}

	.avatar-container {
		position: relative;
		width: 128rpx;
		height: 128rpx;
		margin-right: 28rpx;
		flex-shrink: 0;
	}

	.avatar {
		width: 100%;
		height: 100%;
		border-radius: 50%;
		border: 3rpx solid rgba(255,255,255,0.65);
		box-shadow: 0 8rpx 28rpx rgba(80, 60, 130, 0.12);
		background-color: rgba(255,255,255,0.55);
		background-size: cover;
		background-position: center;
		background-repeat: no-repeat;
		overflow: hidden;
	}

	.avatar-empty {
		width: 100%; height: 100%;
		display: flex; align-items: center; justify-content: center;
		background: linear-gradient(135deg, #e8e4f6, #ddd8f0);
		border-radius: 50%;
	}
	.avatar-empty-text {
		font-size: 48rpx;
		color: #b0a4c4;
		font-weight: 200;
	}

	.avatar-badge {
		position: absolute;
		right: -4rpx;
		bottom: -4rpx;
		width: 38rpx;
		height: 38rpx;
		background: #7d6bd6;
		border: 3rpx solid #fff;
		border-radius: 50%;
		display: flex; align-items: center; justify-content: center;
		box-shadow: 0 4rpx 12rpx rgba(125,107,214,0.25);
	}
	.badge-icon {
		font-size: 18rpx;
		color: #fff;
	}

	.user-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.name-row {
		display: flex;
		align-items: center;
		margin-bottom: 8rpx;
	}

	.nickname {
		font-size: 38rpx;
		font-weight: 700;
		color: #2d2048;
		letter-spacing: 0.5rpx;
	}

	.mbti-tag {
		background: linear-gradient(135deg, #8b78c4, #6d58b0);
		color: #fff;
		font-size: 20rpx;
		font-weight: 600;
		padding: 4rpx 14rpx;
		border-radius: 16rpx;
		margin-left: 14rpx;
		letter-spacing: 0.5rpx;
	}

	.sub-desc {
		font-size: 25rpx;
		color: rgba(45, 32, 72, 0.65);
		letter-spacing: 0.3rpx;
	}

	.arrow-icon {
		font-size: 36rpx;
		color: rgba(45, 32, 72, 0.35);
		font-family: monospace;
		margin-left: 8rpx;
	}

	/* ── 统计面板 ── */
	.stats-panel {
		display: flex;
		align-items: center;
		background: rgba(255,255,255,0.80);
		border-radius: 28rpx;
		padding: 36rpx 16rpx;
		margin-bottom: 24rpx;
		box-shadow: 0 6rpx 28rpx rgba(80, 60, 130, 0.07);
		border: 1rpx solid rgba(255,255,255,0.5);
		position: relative;
		z-index: 1;
	}

	.stat-item {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.stat-icon { font-size: 28rpx; margin-bottom: 8rpx; }
	.stat-val {
		font-size: 36rpx;
		font-weight: 700;
		color: #2d2048;
		margin-bottom: 4rpx;
	}
	.stat-label {
		font-size: 22rpx;
		color: #8b7da8;
		letter-spacing: 0.5rpx;
	}

	.stat-divider {
		width: 1rpx;
		height: 56rpx;
		background: rgba(100, 80, 140, 0.10);
	}

	/* ── 功能菜单 ── */
	.menu-card {
		background: rgba(255,255,255,0.80);
		border-radius: 28rpx;
		padding: 8rpx 0;
		margin-bottom: 24rpx;
		box-shadow: 0 6rpx 28rpx rgba(80, 60, 130, 0.07);
		border: 1rpx solid rgba(255,255,255,0.5);
		position: relative;
		z-index: 1;
	}

	.menu-item {
		display: flex;
		align-items: center;
		padding: 28rpx 32rpx;
		transition: background 0.15s;
	}
	.menu-item:active { background: rgba(125,107,214,0.05); }

	.menu-icon-wrap {
		width: 52rpx; height: 52rpx;
		border-radius: 14rpx;
		display: flex; align-items: center; justify-content: center;
		margin-right: 24rpx;
	}
	.menu-icon-profile { background: rgba(175,160,220,0.18); }
	.menu-icon-test { background: rgba(160,210,175,0.20); }
	.menu-icon-report { background: rgba(160,190,230,0.20); }
	.menu-icon-setting { background: rgba(200,190,210,0.18); }
	.menu-emoji { font-size: 26rpx; }

	.menu-label {
		flex: 1;
		font-size: 28rpx;
		color: #2d2048;
		font-weight: 500;
	}

	.menu-arrow {
		font-size: 30rpx;
		color: rgba(45, 32, 72, 0.30);
		font-family: monospace;
	}

	.menu-sep {
		height: 1rpx;
		background: rgba(100, 80, 140, 0.08);
		margin: 0 32rpx;
	}

	/* ── 记录卡片 ── */
	.section-card {
		background: rgba(255,255,255,0.80);
		border-radius: 28rpx;
		padding: 32rpx 32rpx 28rpx;
		margin-bottom: 24rpx;
		box-shadow: 0 6rpx 28rpx rgba(80, 60, 130, 0.07);
		border: 1rpx solid rgba(255,255,255,0.5);
		position: relative;
		z-index: 1;
	}

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 24rpx;
	}

	.section-title {
		font-size: 28rpx;
		font-weight: 600;
		color: #2d2048;
	}

	.section-more {
		font-size: 22rpx;
		color: #8b7da8;
	}

	.record-list {
		display: flex;
		flex-direction: column;
	}

	.record-item {
		display: flex;
		align-items: center;
		padding: 22rpx 0;
		border-bottom: 1rpx solid rgba(100, 80, 140, 0.06);
	}
	.record-item:last-child {
		border-bottom: none;
		padding-bottom: 0;
	}

	.record-dot {
		width: 14rpx;
		height: 14rpx;
		border-radius: 50%;
		margin-right: 20rpx;
		flex-shrink: 0;
	}
	.dot-green { background: #a0d4a4; }
	.dot-blue { background: #a0c4e8; }
	.dot-purple { background: #b8a8e0; }
	.dot-orange { background: #e0c8a0; }

	.record-content {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.record-name {
		font-size: 27rpx;
		color: #2d2048;
		margin-bottom: 6rpx;
		font-weight: 500;
	}

	.record-date {
		font-size: 21rpx;
		color: #8b7da8;
	}

	.record-tag {
		background: rgba(100, 80, 140, 0.07);
		padding: 4rpx 14rpx;
		border-radius: 16rpx;
	}
	.record-tag text {
		font-size: 20rpx;
		color: #8b7da8;
	}

	.record-action {
		padding: 8rpx 20rpx;
		border-radius: 20rpx;
		border: 1rpx solid rgba(125,107,214,0.20);
		background: rgba(125,107,214,0.06);
	}
	.record-action text {
		font-size: 22rpx;
		color: #7d6bd6;
		font-weight: 500;
	}

	/* ── 底部登录区 ── */
	.auth-area {
		padding: 16rpx 0 8rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		position: relative;
		z-index: 1;
	}

	.auth-btn {
		width: 100%;
		height: 88rpx;
		border-radius: 44rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.auth-btn-login {
		background: linear-gradient(135deg, #8b78c4, #6d58b0);
		box-shadow: 0 8rpx 24rpx rgba(109,88,176,0.22);
	}
	.auth-btn-login:active {
		transform: scale(0.97);
		box-shadow: 0 4rpx 14rpx rgba(109,88,176,0.15);
	}

	.auth-btn-t {
		font-size: 28rpx;
		color: #fff;
		font-weight: 600;
		letter-spacing: 2rpx;
	}

	.auth-divider {
		display: flex;
		align-items: center;
		width: 100%;
		margin: 24rpx 0;
	}
	.auth-line { flex: 1; height: 1rpx; background: rgba(100,80,140,0.12); }
	.auth-or { font-size: 22rpx; color: #8b7da8; padding: 0 20rpx; }

	.auth-btn-register {
		background: rgba(255,255,255,0.50);
		border: 1rpx solid rgba(125,107,214,0.25);
	}
	.auth-btn-register:active { background: rgba(255,255,255,0.65); }

	.auth-btn-t2 {
		font-size: 28rpx;
		color: #7d6bd6;
		font-weight: 500;
		letter-spacing: 1rpx;
	}
</style>
