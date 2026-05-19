<template>
	<view class="page">
		<!-- 星空背景 -->
		<view class="star-layer">
			<view v-for="(s,i) in stars" :key="i" class="star" :style="s"></view>
		</view>
		<view class="orb orb-a"></view>
		<view class="orb orb-b"></view>

		<!-- 顶部导航 -->
		<view class="nav-bar">
			<view class="nav-left" @tap="goBack">
				<text class="back-icon">←</text>
			</view>
			<text class="nav-title">星盘解析</text>
			<view class="nav-right"></view>
		</view>

		<!-- 报告内容 -->
		<scroll-view scroll-y class="report-scroll">
			<astro-report
				v-if="hasData"
				:birthInfo="birthInfo"
				:trinity="trinity"
				:planets="planets"
				:personalitySummary="personalitySummary"
				:traits="traits"
				:elements="elements"
				@deep-analysis="onDeepAnalysis"
				@share="onShare"
			/>

			<!-- 信息不完整：补充输入 -->
			<view v-else class="empty-state">
				<view class="empty-icon-wrap">
					<text class="empty-icon">🔮</text>
				</view>
				<text class="empty-title">探索你的星盘密码</text>
				<text class="empty-desc">完善出生信息，解锁属于你的专属星盘解读</text>
				<view class="input-card">
					<!-- 出生时间 (年月日时分) -->
					<picker mode="multiSelector" :range="dtRange" :value="dtIdx"
						@change="onDtChange" @columnchange="onDtColChange">
						<view class="input-row">
							<text class="input-label">出生时间</text>
							<view class="input-val-area">
								<text class="input-val" v-if="form.date">{{ dtDisplay }}</text>
								<text class="input-ph" v-else>请选择</text>
								<text class="row-arrow">›</text>
							</view>
						</view>
					</picker>
					<view class="input-line"></view>

					<!-- 出生地 -->
					<picker mode="multiSelector" :range="regionRange" :value="regionIdx"
						@change="onRegionChange" @columnchange="onRegionColChange">
						<view class="input-row">
							<text class="input-label">出生地点</text>
							<view class="input-val-area">
								<text class="input-val" v-if="form.province">{{ form.province }} {{ form.city }} {{ form.district }}</text>
								<text class="input-ph" v-else>请选择</text>
								<text class="row-arrow">›</text>
							</view>
						</view>
					</picker>
				</view>
			<view
				class="submit-btn"
				:class="{ 'submit-btn--active': canSubmit }"
				@tap="generateReport"
			>
					<text class="submit-text">生成星盘报告 ✦</text>
				</view>
				<text class="submit-hint" v-if="!canSubmit">请填写完整出生信息</text>
			</view>
		</scroll-view>
	</view>
</template>

<script>
import astroReport from '@/components/astro-report/astro-report.vue'
import { getApiUserId, getApiUserPhone, getUser } from '@/utils/api.js'

var REGION = require('@/common/region-data.js')

function makeStars() {
	var arr = []
	for (var i = 0; i < 60; i++) {
		var sz = (Math.random() * 3 + 1).toFixed(0)
		arr.push({
			left: (Math.random() * 100).toFixed(1) + '%',
			top: (Math.random() * 100).toFixed(1) + '%',
			width: sz + 'rpx', height: sz + 'rpx',
			opacity: (Math.random() * 0.5 + 0.1).toFixed(2),
			animationDelay: (Math.random() * 5).toFixed(1) + 's',
			animationDuration: (Math.random() * 3 + 2).toFixed(1) + 's'
		})
	}
	return arr
}

function daysInMonth(y, m) {
	return new Date(y, m, 0).getDate()
}

export default {
	components: { astroReport },
	data: function() {
		return {
			stars: makeStars(),
			hasData: false,
			// 表单：与 profile-edit 字段对齐
			form: {
				date: '',       // YYYY-MM-DD
				time: '',       // HH:MM
				province: '',
				city: '',
				district: ''
			},
			dtIdx: [55, 0, 0, 12, 0],
			regionIdx: [0, 0, 0],
			// 报告数据
			birthInfo: {},
			trinity: [],
			planets: [],
			personalitySummary: '',
			traits: [],
			elements: []
		}
	},
	computed: {
		canSubmit: function() {
			var f = this.form
			return !!(f.date && f.time && f.province)
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
	onLoad: function() {
		this.loadUserProfile()
	},
	methods: {
		goBack: function() {
			uni.navigateBack({ delta: 1 })
		},

		/* ── 读取用户资料（与 profile-edit 逻辑一致） ── */
		loadUserProfile: function() {
			var self = this
			var uid = getApiUserId()
			if (uid) {
				getUser({ id: uid }).then(function(res) {
					if (res && res.data) {
						self.applyProfile({
							birthDate: res.data.birth_date || '',
							birthTime: res.data.birth_time || '',
							birthProvince: res.data.birth_province || '',
							birthCity: res.data.birth_city || '',
							birthDistrict: res.data.birth_district || ''
						})
					} else {
						self.loadLocalProfile()
					}
				}).catch(function() {
					self.loadLocalProfile()
				})
				return
			}
			var phone = getApiUserPhone()
			if (phone) {
				getUser({ phone: phone }).then(function(res) {
					if (res && res.data) {
						self.applyProfile({
							birthDate: res.data.birth_date || '',
							birthTime: res.data.birth_time || '',
							birthProvince: res.data.birth_province || '',
							birthCity: res.data.birth_city || '',
							birthDistrict: res.data.birth_district || ''
						})
					} else {
						self.loadLocalProfile()
					}
				}).catch(function() {
					self.loadLocalProfile()
				})
				return
			}
			self.loadLocalProfile()
		},
		loadLocalProfile: function() {
			var raw = uni.getStorageSync('userProfile')
			if (raw) {
				try {
					var p = JSON.parse(raw)
					this.applyProfile({
						birthDate: p.birthDate || '',
						birthTime: p.birthTime || '',
						birthProvince: (p.birthRegion && p.birthRegion[0]) || '',
						birthCity: (p.birthRegion && p.birthRegion[1]) || '',
						birthDistrict: (p.birthRegion && p.birthRegion[2]) || ''
					})
				} catch (e) {}
			}
		},
		applyProfile: function(p) {
			this.form.date = p.birthDate || ''
			this.form.time = p.birthTime || ''
			this.form.province = p.birthProvince || ''
			this.form.city = p.birthCity || ''
			this.form.district = p.birthDistrict || ''

			// 同步 picker 索引
			if (p.birthDate) {
				var dp = p.birthDate.split('-')
				this.dtIdx = [
					parseInt(dp[0]) - 1950,
					parseInt(dp[1]) - 1,
					parseInt(dp[2]) - 1,
					this.dtIdx[3],
					this.dtIdx[4]
				]
			}
			if (p.birthTime) {
				var tp = p.birthTime.split(':')
				this.dtIdx[3] = parseInt(tp[0])
				this.dtIdx[4] = parseInt(tp[1])
			}
			if (p.birthProvince) {
				for (var ri = 0; ri < REGION.length; ri++) {
					if (REGION[ri].n === p.birthProvince) {
						this.regionIdx = [ri, 0, 0]
						for (var rci = 0; rci < REGION[ri].c.length; rci++) {
							if (REGION[ri].c[rci].n === p.birthCity) {
								this.regionIdx[1] = rci
								for (var rdi = 0; rdi < REGION[ri].c[rci].d.length; rdi++) {
									if (REGION[ri].c[rci].d[rdi] === p.birthDistrict) {
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

			// 信息完整 → 直接生成报告
			if (this.canSubmit) {
				this.generateReport()
			}
		},

		/* ── Picker 事件 ── */
		onDtChange: function(e) {
			this.dtIdx = e.detail.value
			var y = 1950 + this.dtIdx[0]
			var m = this.dtIdx[1] + 1
			var d = this.dtIdx[2] + 1
			var h = this.dtIdx[3]
			var mi = this.dtIdx[4]
			this.form.date = y + '-' + (m < 10 ? '0' : '') + m + '-' + (d < 10 ? '0' : '') + d
			this.form.time = (h < 10 ? '0' : '') + h + ':' + (mi < 10 ? '0' : '') + mi
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
			this.form.province = p.n
			this.form.city = c.n
			this.form.district = d
		},
		onRegionColChange: function(e) {
			var col = e.detail.column, val = e.detail.value
			var arr = this.regionIdx.slice()
			arr[col] = val
			if (col === 0) { arr[1] = 0; arr[2] = 0 }
			if (col === 1) { arr[2] = 0 }
			this.regionIdx = arr
		},

		/* ── 生成报告 ── */
		generateReport: function() {
			if (!this.canSubmit) {
				uni.showToast({ title: '请填写完整信息', icon: 'none' })
				return
			}

			// 补存用户资料（与 profile-edit 字段对齐）
			this.saveBirthInfoToLocal()

			uni.showLoading({ title: '正在计算星盘...' })

			var self = this
			setTimeout(function() {
				var f = self.form
				self.birthInfo = {
					date: self.formatDate(f.date),
					time: f.time,
					location: f.province + ' ' + f.city + (f.district ? ' ' + f.district : '')
				}
				self.trinity = [
					{ icon: '☉', name: '太阳', sign: '双子座', degree: '23°37\'', bg: 'linear-gradient(145deg, #ffd89b, #e8a87c)', desc: '思维敏捷，善于沟通表达' },
					{ icon: '☽', name: '月亮', sign: '白羊座', degree: '19°34\'', bg: 'linear-gradient(145deg, #a8edea, #82c8c8)', desc: '情绪直接，行动力强' },
					{ icon: '▲', name: '上升', sign: '天秤座', degree: '27°45\'', bg: 'linear-gradient(145deg, #d299c2, #b89ec5)', desc: '外表优雅，追求平衡和谐' }
				]
				self.planets = [
					{ icon: '☉', name: '太阳', sign: '双子座', position: '23°37\'', house: '第7宫', iconBg: 'rgba(255,216,155,0.18)' },
					{ icon: '☽', name: '月亮', sign: '白羊座', position: '19°34\'', house: '第6宫', iconBg: 'rgba(168,237,234,0.18)' },
					{ icon: '☿', name: '水星', sign: '双子座', position: '23°21\'', house: '第7宫', iconBg: 'rgba(168,206,232,0.18)' },
					{ icon: '♀', name: '金星', sign: '双子座', position: '24°26\'', house: '第8宫', iconBg: 'rgba(232,186,188,0.18)' },
					{ icon: '♂', name: '火星', sign: '白羊座', position: '26°34\'', house: '第6宫', iconBg: 'rgba(232,128,128,0.18)' },
					{ icon: '♃', name: '木星', sign: '巨蟹座', position: '20°57\'', house: '第9宫', iconBg: 'rgba(180,160,220,0.18)' },
					{ icon: '♄', name: '土星', sign: '白羊座', position: '10°41\'', house: '第6宫', iconBg: 'rgba(180,175,195,0.18)' },
					{ icon: '♅', name: '天王星', sign: '双子座', position: '01°04\'', house: '第8宫', iconBg: 'rgba(150,200,230,0.18)' },
					{ icon: '♆', name: '海王星', sign: '白羊座', position: '03°59\'', house: '第5宫', iconBg: 'rgba(130,160,220,0.18)' },
					{ icon: '♇', name: '冥王星', sign: '水瓶座', position: '05°11\'', house: '第4宫', iconBg: 'rgba(140,130,190,0.18)' }
				]
				self.personalitySummary = '你的星盘呈现出强烈的风象特质，太阳与水星同在双子座，赋予你敏锐的思维能力与出色的沟通天赋。月亮位于白羊座让你的情感表达直率而真诚。上升天秤座则为你增添了一份优雅与外交手腕。你是一个既能独立思考又善于协作的人，在人群中总是能找到自己的位置并发挥影响力。'
				self.traits = [
					{ name: '创造力', value: 85, color: '#9685ee' },
					{ name: '执行力', value: 72, color: '#3ec9c1' },
					{ name: '感知力', value: 90, color: '#d4607a' },
					{ name: '稳定性', value: 58, color: '#dda03f' }
				]
				self.elements = [
					{ icon: '🔥', name: '火象', percent: 25, desc: '热情冲动', color: '#e88555' },
					{ icon: '🌍', name: '土象', percent: 15, desc: '稳重务实', color: '#a89070' },
					{ icon: '💨', name: '风象', percent: 45, desc: '理性智慧', color: '#6898ce' },
					{ icon: '💧', name: '水象', percent: 15, desc: '敏感直觉', color: '#5ca8b8' }
				]

				self.hasData = true
				uni.hideLoading()
			}, 1200)
		},

		/* ── 保存出生信息到本地（合并已有 userProfile） ── */
		saveBirthInfoToLocal: function() {
			try {
				var raw = uni.getStorageSync('userProfile')
				var profile = raw ? JSON.parse(raw) : {}
				profile.birthDate = this.form.date
				profile.birthTime = this.form.time
				profile.birthRegion = [this.form.province, this.form.city, this.form.district]
				uni.setStorageSync('userProfile', JSON.stringify(profile))
			} catch (e) {}
		},

		formatDate: function(dateStr) {
			if (!dateStr) return ''
			var parts = dateStr.split('-')
			if (parts.length === 3) {
				return parts[0] + '年' + parseInt(parts[1]) + '月' + parseInt(parts[2]) + '日'
			}
			return dateStr
		},
		onDeepAnalysis: function() {
			uni.showToast({ title: '深度解读功能开发中...', icon: 'none' })
		},
		onShare: function() {
			uni.showToast({ title: '分享功能开发中...', icon: 'none' })
		}
	}
}
</script>

<style scoped>
.page {
	padding-top: env(safe-area-inset-top);
	position: relative;
	min-height: 100vh;
	background:
		radial-gradient(ellipse 100% 50% at 50% 0%, rgba(200,188,255,0.32) 0%, rgba(200,188,255,0.08) 40%, transparent 65%),
		linear-gradient(180deg, #faf8ff 0%, #f5f1fc 30%, #efeaf9 60%, #e8e2f5 100%);
	overflow: hidden;
}

/* 星空 */
.star-layer { position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.star {
	position: absolute;
	border-radius: 50%;
	background: rgba(175,160,225,0.50);
	animation: twinkle ease-in-out infinite alternate;
}
@keyframes twinkle { 0%{opacity:0.15;transform:scale(0.8)} 100%{opacity:0.65;transform:scale(1.2)} }
.orb {
	position: absolute; border-radius: 50%;
	filter: blur(80px); pointer-events: none; z-index: 1;
}
.orb-a {
	width: 500rpx; height: 500rpx;
	right: -160rpx; top: 100rpx;
	background: radial-gradient(circle, rgba(200,180,255,0.40), transparent 70%);
	animation: drift 18s ease-in-out infinite;
}
.orb-b {
	width: 600rpx; height: 600rpx;
	left: -200rpx; bottom: -80rpx;
	background: radial-gradient(circle, rgba(210,195,255,0.28), transparent 70%);
	animation: drift 24s ease-in-out infinite reverse;
}
@keyframes drift { 0%,100%{transform:translate(0,0) scale(1);opacity:0.45} 50%{transform:translate(-30rpx,30rpx) scale(1.1);opacity:0.72} }

/* 导航 */
.nav-bar {
	position: relative; z-index: 50;
	display: flex; align-items: center; justify-content: space-between;
	padding: 16rpx 28rpx 20rpx;
	height: 88rpx;
	box-sizing: border-box;
}
.nav-left, .nav-right {
	width: 64rpx;
	display: flex;
	align-items: center;
}
.back-icon {
	font-size: 36rpx;
	color: #322c52;
	font-weight: 500;
}
.nav-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #322c52;
	letter-spacing: 6rpx;
}

/* 滚动区 */
.report-scroll {
	position: relative; z-index: 10;
	height: calc(100vh - 110rpx);
	padding-top: 12rpx;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx 32rpx 40rpx;
}
.empty-icon-wrap {
	width: 140rpx; height: 140rpx;
	border-radius: 50%;
	background: linear-gradient(145deg, rgba(150,133,238,0.15), rgba(125,107,214,0.10));
	display: flex; align-items: center; justify-content: center;
	margin-bottom: 32rpx;
	box-shadow: 0 8rpx 32rpx rgba(130,115,220,0.12), inset 0 0 30rpx rgba(255,255,255,0.40);
}
.empty-icon { font-size: 64rpx; line-height: 1; }
.empty-title {
	font-size: 36rpx;
	font-weight: 700;
	color: #2c2450;
	letter-spacing: 4rpx;
	margin-bottom: 14rpx;
}
.empty-desc {
	font-size: 26rpx;
	color: rgba(130,118,186,0.55);
	line-height: 1.6;
	margin-bottom: 44rpx;
	text-align: center;
	max-width: 500rpx;
}

/* 输入卡片 */
.input-card {
	width: 100%;
	background: rgba(255,255,255,0.92);
	border-radius: 28rpx;
	padding: 8rpx 32rpx 28rpx;
	margin-bottom: 36rpx;
	box-shadow: 0 8rpx 32rpx rgba(100,88,170,0.09);
	border: 1rpx solid rgba(255,255,255,0.75);
}
.input-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
}
.input-line {
	height: 1rpx;
	background: rgba(210,200,235,0.15);
}
.input-label {
	font-size: 26rpx;
	color: #48407a;
	font-weight: 600;
	min-width: 140rpx;
	flex-shrink: 0;
}
.input-val-area {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: flex-end;
}
.input-val {
	font-size: 26rpx;
	color: #3c3268;
	font-weight: 500;
	flex: 1;
	text-align: right;
}
.input-ph {
	font-size: 26rpx;
	color: #b8b0c8;
	flex: 1;
	text-align: right;
}
.row-arrow {
	font-size: 28rpx;
	color: #b8b0c8;
	margin-left: 8rpx;
}

/* 提交按钮 */
.submit-btn {
	width: 520rpx;
	height: 96rpx;
	border-radius: 28rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: linear-gradient(148deg, #c4bdd6 0%, #b5aec8 52%, #a8a1bc 100%);
	margin-bottom: 16rpx;
	transition: all 0.25s ease;
}
.submit-btn--active {
	background: linear-gradient(148deg, #9a8fcb 0%, #8276ba 52%, #7264af 100%) !important;
	box-shadow: 0 10rpx 36rpx rgba(130,118,186,0.30);
}
.btn-hover { opacity: 0.88; transform: scale(0.98); }
.submit-text {
	font-size: 28rpx;
	color: rgba(255,255,255,0.96);
	font-weight: 600;
	letter-spacing: 4rpx;
}
.submit-hint {
	font-size: 22rpx;
	color: rgba(180,168,210,0.55);
	letter-spacing: 1rpx;
}
</style>
