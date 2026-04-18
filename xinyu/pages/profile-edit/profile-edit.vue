<template>
<view class="page" :style="pageStyle">
	<view class="glow"></view>

	<view class="nav-row">
		<view class="nav-back" @tap="goBack"><text class="nav-arrow">‹</text></view>
		<text class="nav-title">完善资料</text>
		<view style="width:68rpx;"></view>
	</view>

	<!-- 头像 -->
	<view class="avatar-section" @tap="chooseAvatar">
		<view class="avatar-ring">
			<image v-if="avatar" class="avatar-img" :src="avatar" mode="aspectFill"></image>
			<view v-else class="avatar-ph"><text class="avatar-ph-t">+</text></view>
			<view class="avatar-badge"><text class="badge-icon">+</text></view>
		</view>
	</view>

	<!-- 表单卡片 -->
	<view class="form-card">

		<!-- 昵称 -->
		<view class="form-row">
			<text class="form-label">昵称</text>
			<view class="form-val-area">
				<input class="form-input" :value="nickname" @input="onNickInput"
					placeholder="请输入昵称（1-6个字）" placeholder-class="form-ph" maxlength="6" />
				<view class="icon-btn" @tap="randomNick"><text class="icon-btn-t">⇄</text></view>
			</view>
		</view>
		<view class="form-line"></view>

		<!-- 性别 -->
		<view class="form-row">
			<text class="form-label">性别</text>
			<view class="form-val-area gender-area">
				<view class="g-pill" :class="{ active: gender==='female' }" @tap="toggleGender('female')">
					<text class="g-sym">♀</text><text class="g-txt">女生</text>
				</view>
				<view class="g-pill" :class="{ active: gender==='male' }" @tap="toggleGender('male')">
					<text class="g-sym">♂</text><text class="g-txt">男生</text>
				</view>
			</view>
		</view>
		<view class="form-line"></view>

		<!-- 出生时间 (年月日时分) -->
		<picker mode="multiSelector" :range="dtRange" :value="dtIdx"
			@change="onDtChange" @columnchange="onDtColChange">
			<view class="form-row">
				<text class="form-label">出生时间</text>
				<view class="form-val-area">
					<text class="form-val" v-if="birthDate">{{ dtDisplay }}</text>
					<text class="form-ph" v-else>请选择</text>
					<text class="row-arrow">›</text>
				</view>
			</view>
		</picker>
		<view class="form-line"></view>

		<!-- 出生地 -->
		<picker mode="multiSelector" :range="regionRange" :value="regionIdx"
			@change="onRegionChange" @columnchange="onRegionColChange">
			<view class="form-row">
				<text class="form-label">出生地点</text>
				<view class="form-val-area">
					<text class="form-val" v-if="birthRegion[0]">{{ birthRegion[0] + ' ' + birthRegion[1] + ' ' + birthRegion[2] }}</text>
					<text class="form-ph" v-else>请选择</text>
					<text class="row-arrow">›</text>
				</view>
			</view>
		</picker>
		<view class="form-line"></view>

		<!-- MBTI -->
		<picker :range="mbtiList" :value="mbtiIdx" @change="onMbtiChange">
			<view class="form-row">
				<text class="form-label">MBTI</text>
				<view class="form-val-area">
					<text class="form-val" v-if="mbti">{{ mbti }}</text>
					<text class="form-ph" v-else>请选择</text>
					<text class="row-arrow">›</text>
				</view>
			</view>
		</picker>
		<view class="form-line"></view>

		<!-- 血型 -->
		<picker :range="bloodTypeList" :value="bloodTypeIdx" @change="onBloodTypeChange">
			<view class="form-row">
				<text class="form-label">血型</text>
				<view class="form-val-area">
					<text class="form-val" v-if="bloodType">{{ bloodType }}</text>
					<text class="form-ph" v-else>请选择</text>
					<text class="row-arrow">›</text>
				</view>
			</view>
		</picker>

	</view>

	<!-- 保存 -->
	<view class="save-btn" hover-class="save-hover" @tap="saveProfile">
		<text class="save-text">保存资料</text>
	</view>

	<view style="height:80rpx;"></view>
</view>
</template>

<script>
var REGION = require('@/common/region-data.js')
import { getApiUserId, getApiUserPhone, getUser, putUserProfile, describeRequestError } from '@/utils/api.js'
var ADJ = ['迷人的','可爱的','温柔的','帅气的','神秘的','快乐的','安静的','勇敢的','优雅的','灵动的','温暖的','梦幻的']
var NOUN = ['四季豆','小太阳','月亮','星星','小猫咪','蒲公英','棉花糖','小确幸','萤火虫','云朵','水蜜桃','银杏叶']
var MBTI_LIST = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']
var BLOOD_TYPE_LIST = ['A','B','AB','O']

function daysInMonth(y, m) {
	return new Date(y, m, 0).getDate()
}

export default {
	data: function() {
		return {
			avatar: '',
			nickname: '',
			gender: '',
			birthDate: '',
			birthTime: '',
			birthRegion: ['','',''],
			mbti: '',
			bloodType: '',
			saving: false,
			mbtiList: MBTI_LIST,
			mbtiIdx: 0,
			bloodTypeList: BLOOD_TYPE_LIST,
			bloodTypeIdx: 0,
			dtIdx: [55, 0, 0, 12, 0],
			regionIdx: [0, 0, 0]
		}
	},
	computed: {
		pageStyle: function() {
			var h = 44
			try {
				var info = uni.getWindowInfo ? uni.getWindowInfo() : uni.getSystemInfoSync()
				if (info && info.statusBarHeight) h = info.statusBarHeight
			} catch (e) {}
			return { paddingTop: h + 'px' }
		},
		dtRange: function() {
			var years = [], months = [], hours = [], minutes = []
			for (var y = 1950; y <= 2015; y++) years.push(y + '年')
			for (var m = 1; m <= 12; m++) months.push((m < 10 ? '0' : '') + m + '月')
			var selYear = 1950 + this.dtIdx[0]
			var selMonth = this.dtIdx[1] + 1
			var maxD = daysInMonth(selYear, selMonth)
			var days = []
			for (var d = 1; d <= maxD; d++) days.push((d < 10 ? '0' : '') + d + '日')
			for (var h = 0; h <= 23; h++) hours.push((h < 10 ? '0' : '') + h + '时')
			for (var mi = 0; mi <= 59; mi++) minutes.push((mi < 10 ? '0' : '') + mi + '分')
			return [years, months, days, hours, minutes]
		},
		regionRange: function() {
			var provinces = []
			for (var i = 0; i < REGION.length; i++) provinces.push(REGION[i].n)
			var pi = this.regionIdx[0]
			if (pi >= REGION.length) pi = 0
			var cs = REGION[pi].c
			var cities = []
			for (var j = 0; j < cs.length; j++) cities.push(cs[j].n)
			var ci = this.regionIdx[1]
			if (ci >= cs.length) ci = 0
			var districts = cs[ci] ? cs[ci].d.slice() : []
			return [provinces, cities, districts]
		},
		dtDisplay: function() {
			var y = 1950 + this.dtIdx[0]
			var m = this.dtIdx[1] + 1
			var d = this.dtIdx[2] + 1
			var h = this.dtIdx[3]
			var mi = this.dtIdx[4]
			return y + '年' + m + '月' + d + '日 ' + (h < 10 ? '0' : '') + h + ':' + (mi < 10 ? '0' : '') + mi
		}
	},
	onLoad: function() { this.loadProfile() },
	methods: {
		goBack: function() {
			if (getCurrentPages().length > 1) { uni.navigateBack(); return }
			uni.reLaunch({ url: '/pages/profile/profile' })
		},
		loadProfile: function() {
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
			this.loadLocalProfile()
		},
		loadLocalProfile: function() {
			var raw = uni.getStorageSync('userProfile')
			if (raw) {
				try {
					var p = JSON.parse(raw)
					this.applyProfileData(p)
				} catch (e) {}
			}
			if (!this.nickname) this.randomNick()
		},
		loadRemoteProfile: function(uid) {
			var self = this
			getUser({ id: uid })
				.then(function(res) {
					if (res && res.data) {
						var user = res.data
						self.applyProfileData({
							avatar: user.avatar_url || '',
							nickname: user.nickname || '',
							gender: user.gender || '',
							birthDate: user.birth_date || '',
							birthTime: user.birth_time || '',
							birthRegion: [user.birth_province || '', user.birth_city || '', user.birth_district || ''],
							mbti: user.mbti || '',
							bloodType: user.blood_type || ''
						})
					} else {
						self.loadLocalProfile()
					}
				})
				.catch(function() {
					self.loadLocalProfile()
				})
		},
		loadRemoteProfileByPhone: function(phone) {
			var self = this
			getUser({ phone: phone })
				.then(function(res) {
					if (res && res.data) {
						var user = res.data
						self.applyProfileData({
							avatar: user.avatar_url || '',
							nickname: user.nickname || '',
							gender: user.gender || '',
							birthDate: user.birth_date || '',
							birthTime: user.birth_time || '',
							birthRegion: [user.birth_province || '', user.birth_city || '', user.birth_district || ''],
							mbti: user.mbti || '',
							bloodType: user.blood_type || ''
						})
					} else {
						self.loadLocalProfile()
					}
				})
				.catch(function() {
					self.loadLocalProfile()
				})
		},
		applyProfileData: function(p) {
			this.avatar = p.avatar || ''
			this.nickname = p.nickname || ''
			this.gender = p.gender || ''
			this.birthDate = p.birthDate || ''
			this.birthTime = p.birthTime || ''
			this.birthRegion = p.birthRegion || ['','','']
			if (this.birthRegion[0]) {
				for (var ri = 0; ri < REGION.length; ri++) {
					if (REGION[ri].n === this.birthRegion[0]) {
						this.regionIdx = [ri, 0, 0]
						for (var rci = 0; rci < REGION[ri].c.length; rci++) {
							if (REGION[ri].c[rci].n === this.birthRegion[1]) {
								this.regionIdx[1] = rci
								for (var rdi = 0; rdi < REGION[ri].c[rci].d.length; rdi++) {
									if (REGION[ri].c[rci].d[rdi] === this.birthRegion[2]) {
										this.regionIdx[2] = rdi; break
									}
								}
								break
							}
						}
						break
					}
				}
			}
			this.mbti = p.mbti || ''
			if (this.mbti) {
				for (var i = 0; i < MBTI_LIST.length; i++) {
					if (MBTI_LIST[i] === this.mbti) { this.mbtiIdx = i; break }
				}
			}
			this.bloodType = p.bloodType || ''
			if (this.bloodType) {
				for (var bi = 0; bi < BLOOD_TYPE_LIST.length; bi++) {
					if (BLOOD_TYPE_LIST[bi] === this.bloodType) { this.bloodTypeIdx = bi; break }
				}
			}
			if (this.birthDate) {
				var dp = this.birthDate.split('-')
				this.dtIdx = [
					parseInt(dp[0]) - 1950,
					parseInt(dp[1]) - 1,
					parseInt(dp[2]) - 1,
					this.dtIdx[3],
					this.dtIdx[4]
				]
			}
			if (this.birthTime) {
				var tp = this.birthTime.split(':')
				this.dtIdx[3] = parseInt(tp[0])
				this.dtIdx[4] = parseInt(tp[1])
			}
		},
		randomNick: function() {
			this.nickname = ADJ[Math.floor(Math.random() * ADJ.length)] + NOUN[Math.floor(Math.random() * NOUN.length)]
		},
		onNickInput: function(e) { this.nickname = e.detail.value },
		toggleGender: function(val) { this.gender = this.gender === val ? '' : val },
		chooseAvatar: function() {
			var self = this
			uni.chooseImage({
				count: 1, sizeType: ['compressed'], sourceType: ['album','camera'],
				success: function(res) {
					if (res.tempFilePaths && res.tempFilePaths[0]) self.avatar = res.tempFilePaths[0]
				}
			})
		},

		onDtChange: function(e) {
			this.dtIdx = e.detail.value
			var y = 1950 + this.dtIdx[0]
			var m = this.dtIdx[1] + 1
			var d = this.dtIdx[2] + 1
			var h = this.dtIdx[3]
			var mi = this.dtIdx[4]
			this.birthDate = y + '-' + (m < 10 ? '0' : '') + m + '-' + (d < 10 ? '0' : '') + d
			this.birthTime = (h < 10 ? '0' : '') + h + ':' + (mi < 10 ? '0' : '') + mi
		},
		onDtColChange: function(e) {
			var col = e.detail.column
			var val = e.detail.value
			var arr = this.dtIdx.slice()
			arr[col] = val
			if (col === 0 || col === 1) {
				var maxD = daysInMonth(1950 + arr[0], arr[1] + 1)
				if (arr[2] >= maxD) arr[2] = maxD - 1
			}
			this.dtIdx = arr
		},
		onRegionChange: function(e) {
			this.regionIdx = e.detail.value
			var pi = this.regionIdx[0], ci = this.regionIdx[1], di = this.regionIdx[2]
			var p = REGION[pi] || REGION[0]
			var c = p.c[ci] || p.c[0]
			var d = (c.d[di] || c.d[0] || '')
			this.birthRegion = [p.n, c.n, d]
		},
		onRegionColChange: function(e) {
			var col = e.detail.column, val = e.detail.value
			var arr = this.regionIdx.slice()
			arr[col] = val
			if (col === 0) { arr[1] = 0; arr[2] = 0 }
			if (col === 1) { arr[2] = 0 }
			this.regionIdx = arr
		},
		onMbtiChange: function(e) {
			this.mbtiIdx = e.detail.value
			this.mbti = MBTI_LIST[this.mbtiIdx]
		},
		onBloodTypeChange: function(e) {
			this.bloodTypeIdx = e.detail.value
			this.bloodType = BLOOD_TYPE_LIST[this.bloodTypeIdx]
		},

		saveProfile: function() {
			if (this.saving) return
			if (!this.nickname.trim()) {
				uni.showToast({ title: '请输入昵称', icon: 'none' }); return
			}
			var cachedProfile = {
				avatar: this.avatar,
				nickname: this.nickname.trim(),
				gender: this.gender,
				birthDate: this.birthDate,
				birthTime: this.birthTime,
				birthRegion: this.birthRegion,
				mbti: this.mbti,
				bloodType: this.bloodType
			}
			var uid = getApiUserId()
			var phone = getApiUserPhone()
			if (!uid && !phone) {
				uni.setStorageSync('userProfile', JSON.stringify(cachedProfile))
				uni.showToast({ title: '未登录，仅本地保存', icon: 'none' })
				return
			}
		var payload = {
			nickname: cachedProfile.nickname,
			gender: this.gender || 'unknown',
			birth_date: this.birthDate || null,
			birth_time: this.birthTime || '',
			birth_province: this.birthRegion[0] || '',
			birth_city: this.birthRegion[1] || '',
			birth_district: this.birthRegion[2] || '',
			mbti: this.mbti || '',
			blood_type: this.bloodType || ''
		}
			if (uid) payload.id = uid
			if (!uid && phone) payload.phone = phone
			// 当前没有头像上传接口，只有远程 URL 才能直接入库。
			if (this.avatar && /^https?:\/\//.test(this.avatar)) {
				payload.avatar_url = this.avatar
			}
			var self = this
			this.saving = true
			uni.showLoading({ title: '保存中', mask: true })
			putUserProfile(payload)
				.then(function(res) {
					if (res && res.data && res.data.id != null && res.data.id !== '') {
						try {
							uni.setStorageSync('xinyu_user_id', Number(res.data.id))
						} catch (e0) {}
					}
					uni.setStorageSync('userProfile', JSON.stringify(cachedProfile))
					uni.hideLoading()
					uni.showToast({ title: '已保存到数据库', icon: 'success' })
					setTimeout(function() { uni.navigateBack() }, 800)
				})
				.catch(function(err) {
					uni.hideLoading()
					try {
						uni.setStorageSync('userProfile', JSON.stringify(cachedProfile))
					} catch (e1) {}
					var tip = describeRequestError(err)
					uni.showModal({
						title: '同步服务器失败',
						content: tip + '\n\n资料已保存在本机，服务器恢复后请再点保存。',
						showCancel: false
					})
				})
				.then(function() {
					self.saving = false
				})
		}
	}
}
</script>

<style scoped>
.page {
	min-height: 100vh;
	padding: 0 36rpx;
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

/* Nav */
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

/* Avatar */
.avatar-section {
	display: flex; justify-content: center;
	padding: 32rpx 0 28rpx;
	position: relative; z-index: 2;
}
.avatar-ring {
	width: 160rpx; height: 160rpx;
	border-radius: 50%; position: relative;
	border: 4rpx solid rgba(255,255,255,0.7);
	box-shadow: 0 6rpx 24rpx rgba(80,60,130,0.1);
}
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }
.avatar-ph {
	width: 100%; height: 100%; border-radius: 50%;
	background: rgba(255,255,255,0.6);
	display: flex; align-items: center; justify-content: center;
}
.avatar-ph-t { font-size: 56rpx; color: #b0a4c4; font-weight: 200; }
.avatar-badge {
	position: absolute; bottom: 2rpx; right: 2rpx;
	width: 40rpx; height: 40rpx; border-radius: 50%;
	background: #6c5c98; border: 3rpx solid #fff;
	display: flex; align-items: center; justify-content: center;
}
.badge-icon { font-size: 24rpx; color: #fff; font-weight: 600; }

/* Form Card */
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
	width: 140rpx; flex-shrink: 0;
	font-size: 28rpx; font-weight: 600; color: #2d2048;
}
.form-val-area {
	flex: 1;
	display: flex; align-items: center;
	justify-content: flex-end;
}
.form-line {
	height: 1rpx;
	background: rgba(100,80,140,0.06);
	margin-left: 140rpx;
}

/* Input */
.form-input {
	flex: 1; text-align: right;
	font-size: 28rpx; font-weight: 500; color: #2d2048;
	height: 80rpx;
}
.form-ph { font-size: 28rpx; color: #b8b0c8; }
.icon-btn {
	width: 60rpx; height: 60rpx;
	display: flex; align-items: center; justify-content: center;
	border-radius: 50%; margin-left: 12rpx;
	background: rgba(100,80,140,0.06);
}
.icon-btn-t { font-size: 28rpx; color: #6c5c98; }

/* Gender */
.gender-area { justify-content: flex-end; }
.g-pill {
	display: flex; align-items: center;
	padding: 12rpx 28rpx;
	border-radius: 40rpx;
	border: 1.5rpx solid rgba(100,80,140,0.12);
	margin-left: 16rpx;
	background: transparent;
	transition: all 0.25s;
}
.g-pill.active {
	background: #5c4d80;
	border-color: #5c4d80;
	box-shadow: 0 3rpx 12rpx rgba(92,77,128,0.2);
}
.g-sym { font-size: 28rpx; color: #6c5c88; margin-right: 6rpx; }
.g-txt { font-size: 26rpx; font-weight: 600; color: #6c5c88; }
.g-pill.active .g-sym,
.g-pill.active .g-txt { color: #fff; }

/* Picker value */
.form-val {
	font-size: 28rpx; font-weight: 500; color: #2d2048;
	flex: 1; text-align: right;
}
.row-arrow {
	font-size: 30rpx; color: #b8b0c8;
	margin-left: 8rpx;
}

/* Save */
.save-btn {
	margin-top: 48rpx;
	height: 96rpx; border-radius: 48rpx;
	background: linear-gradient(135deg, #7c6cb8 0%, #5c4d90 50%, #6c5ca8 100%);
	display: flex; align-items: center; justify-content: center;
	box-shadow: 0 8rpx 28rpx rgba(92,77,144,0.3);
	position: relative; z-index: 2;
}
.save-hover { opacity: 0.88; transform: scale(0.98); }
.save-text {
	font-size: 32rpx; font-weight: 700;
	color: #fff; letter-spacing: 6rpx;
}
</style>
