<template>
<view class="page" :style="{ background: pageBg }">
	<view class="nav-back" @tap="goBack">
		<text class="back-arrow">‹</text>
	</view>

	<view class="hero" :style="{ background: heroBg }">
		<view class="mascot-stage">
			<view class="mascot-halo" :style="{ background: haloBg, opacity: haloOp, transform: haloTf }"></view>
			<view class="mascot-wrap" :style="{ transform: mascotTf }">
				<svg class="sprite-svg" fill="none" viewBox="0 0 241.376 188.924">
					<defs>
						<mask id="body-mask-er" maskUnits="userSpaceOnUse" style="mask-type:alpha">
							<path d="M148.652 0C182.792 0.000197914 210.468 27.6759 210.468 61.8154C210.468 65.0652 210.216 68.2567 209.732 71.3711C228.627 82.089 241.376 102.386 241.376 125.66C241.376 158.482 215.946 185.714 183.158 187.199C162.354 188.141 139.439 188.924 120.688 188.924C101.936 188.924 79.0222 188.141 58.2178 187.199C25.4299 185.714 0 158.482 0 125.66C0 100.709 14.651 79.1799 35.8194 69.2061C35.4947 67.2817 35.3233 65.3048 35.3233 63.2881C35.3233 43.7796 51.138 27.9648 70.6465 27.9648C78.9593 27.9648 86.6002 30.8374 92.6338 35.6426C102.489 14.5861 123.868 0 148.652 0Z" fill="white"/>
						</mask>
						<filter id="body-glow-filter-er" x="-40%" y="-30%" width="180%" height="160%" filterUnits="objectBoundingBox" color-interpolation-filters="sRGB">
							<feFlood flood-opacity="0" result="BackgroundImageFix"/>
							<feBlend in="SourceGraphic" in2="BackgroundImageFix" mode="normal" result="shape"/>
							<feGaussianBlur stdDeviation="16"/>
						</filter>
						<radialGradient id="body-grad-er" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(125.451 107.208) rotate(90) scale(90.37 111.98)">
							<stop offset="0.22" :stop-color="rgbStr(gradRGB)"/>
							<stop offset="1" :stop-color="rgbStr(gradRGB)" stop-opacity="0.65"/>
						</radialGradient>
					</defs>

					<g mask="url(#body-mask-er)">
						<g filter="url(#body-glow-filter-er)">
							<ellipse cx="125.451" cy="107.208" rx="111.979" ry="90.3693" fill="url(#body-grad-er)"/>
						</g>
						<rect x="-5" y="-5" width="252" height="200" :fill="rgbStr(tintRGBA)" :opacity="tintRGBA[3]"></rect>
					</g>

					<path d="M218 154 C222 152 227 145 228 138" :stroke="'rgba(198,185,255,' + sparkA.toFixed(2) + ')'" stroke-linecap="round" stroke-width="5.2" fill="none"/>
					<path d="M29 89 C26 90 22 95 21 100" :stroke="'rgba(198,185,255,' + sparkA.toFixed(2) + ')'" stroke-linecap="round" stroke-width="5.2" fill="none"/>

					<g :transform="'translate(0 ' + faceOY.toFixed(1) + ')'">
						<path :d="buildQuadPath(browLP)" stroke="#38354a" stroke-width="3.6" stroke-linecap="round" fill="none" opacity="0.72"/>
						<path :d="buildQuadPath(browRP)" stroke="#38354a" stroke-width="3.6" stroke-linecap="round" fill="none" opacity="0.72"/>

						<ellipse cx="96" cy="99" rx="7.1" :ry="eyeR.toFixed(2)" fill="#2a2838"/>
						<ellipse :cx="96 - 1.5" :cy="99 - eyeR * 0.32" :rx="2.4" :ry="(eyeR * 0.32).toFixed(2)" fill="white" opacity="0.82"/>
						<ellipse cx="146" cy="99" rx="7.1" :ry="eyeR.toFixed(2)" fill="#2a2838"/>
						<ellipse :cx="146 - 1.5" :cy="99 - eyeR * 0.32" :rx="2.4" :ry="(eyeR * 0.32).toFixed(2)" fill="white" opacity="0.82"/>

						<g :opacity="blushA.toFixed(3)">
							<ellipse cx="70" cy="110" rx="13" ry="5.5" fill="#FF87A8" opacity="0.5" transform="rotate(-8, 70, 110)"/>
							<ellipse cx="172" cy="110" rx="13" ry="5.5" fill="#FF87A8" opacity="0.5" transform="rotate(8, 172, 110)"/>
						</g>

						<g :opacity="tearA.toFixed(3)">
							<path d="M96 112 Q92 121 94 129 Q96 137 98 129 Q100 121 96 112Z" fill="#99CCFF" opacity="0.78"/>
							<path d="M146 112 Q142 121 144 129 Q146 137 148 129 Q150 121 146 112Z" fill="#99CCFF" opacity="0.78"/>
						</g>

						<path :d="buildQuadPath(mouthP)" fill="none" stroke="#32303e" stroke-width="5" stroke-linecap="round"/>
					</g>
				</svg>
			</view>
		</view>
		<text class="mood-heading">{{ heading }}</text>
	</view>

	<view class="controls" :style="{ background: controlsBg }">
		<view class="note-row">
			<text class="note-pen">✎</text>
			<input v-model="noteText" class="note-input" placeholder="写个小纸条，记录此刻感受..." placeholder-style="color:rgba(255,255,255,0.65)" />
		</view>

		<view class="metric">
			<view class="metric-head">
				<text class="metric-title">情绪值</text>
				<text class="metric-val">{{ Math.round(targetMood) }} · {{ moodLabel }}</text>
			</view>
			<view class="slider emotion-hitbox"
				@touchstart.stop.prevent="startSlide('mood',$event)"
				@touchmove.stop.prevent="moveSlide('mood',$event)"
				@touchend.stop.prevent="endSlide"
				@mousedown.stop.prevent="startSlide('mood',$event)"
				@mousemove.stop.prevent="moveSlide('mood',$event)"
				@mouseup.stop.prevent="endSlide"
				@mouseleave.stop.prevent="endSlide">
				<view class="track emotion-track"></view>
				<view class="thumb" :style="{ left: emoThumbLeft, background: emoThumbBg }"></view>
			</view>
			<view class="hints"><text>难过</text><text>平静</text><text>开心</text></view>
		</view>

		<view class="metric">
			<view class="metric-head">
				<text class="metric-title">活力值</text>
				<text class="metric-val">{{ Math.round(targetVit) }} · {{ vitLabel }}</text>
			</view>
			<view class="slider vitality-hitbox"
				@touchstart.stop.prevent="startSlide('vit',$event)"
				@touchmove.stop.prevent="moveSlide('vit',$event)"
				@touchend.stop.prevent="endSlide"
				@mousedown.stop.prevent="startSlide('vit',$event)"
				@mousemove.stop.prevent="moveSlide('vit',$event)"
				@mouseup.stop.prevent="endSlide"
				@mouseleave.stop.prevent="endSlide">
				<view class="track vit-track" :style="{ background: vitTrackBg }"></view>
				<view class="thumb" :style="{ left: vitThumbLeft, background: vitThumbBg }"></view>
			</view>
			<view class="hints"><text>慵懒</text><text>舒展</text><text>满格</text></view>
		</view>

		<view class="actions">
			<view class="btn-primary" @tap="doConfirm"><text>完成记录</text></view>
			<view class="btn-ghost" @tap="goBack"><text>稍后再记</text></view>
		</view>
	</view>
</view>
</template>

<script>
import { postEmotionRecord, getApiUserId, getApiOpenid, describeRequestError } from '@/utils/api.js'

var lerp = function(a, b, t) { return a + (b - a) * t }
var clamp = function(v, lo, hi) { return Math.max(lo, Math.min(hi, v)) }

function weightedArr(arrs, wt) {
	var n = arrs[0].length, out = []
	for (var j = 0; j < n; j++) {
		var v = 0
		for (var i = 0; i < arrs.length; i++) v += arrs[i][j] * wt[i]
		out.push(v)
	}
	return out
}

function getWeights(e) {
	var sad = 0, calm = 0, happy = 0
	if (e < 50) { sad = 1 - e / 50; calm = e / 50 }
	else { calm = 1 - (e - 50) / 50; happy = (e - 50) / 50 }
	return [sad, calm, happy, 0]
}

var BROW_L = {
	sad: [87,90.6,96,85.5,105,90.1], calm: [87,88.9,96,87.3,105,88.9],
	happy: [87,86.9,96,82.5,105,86.9], angry: [87,86.4,96,90.5,105,86.4]
}
var BROW_R = {
	sad: [137,90.1,146,85.5,155,90.6], calm: [137,88.9,146,87.3,155,88.9],
	happy: [137,86.9,146,82.5,155,86.9], angry: [137,86.4,146,90.5,155,86.4]
}
var MOUTH = {
	sad: [108,129,120.7,121,133,129], calm: [108,123,120.7,129,133,123],
	happy: [98,118,120.7,140,143,118], angry: [106,127,120.7,123,135,127]
}
var EYE_RY = [5.1, 7.2, 8.8, 4.1]
var BLUSH  = [0.10, 0.32, 0.72, 0.06]
var TEARS  = [0.95, 0.08, 0, 0]
var GRAD_C = [[200,195,255],[215,205,255],[220,210,255],[255,200,220]]
var TINT_C = [[100,100,220,0.22],[150,130,230,0.08],[180,160,240,0.06],[220,100,150,0.14]]
var MG_C   = [[80,82,175],[108,96,200],[130,118,215],[160,72,130]]
var ST = ['sad','calm','happy','angry']

var BL_P = 4000, BL_D = 150
function blinkScale(ts) {
	var p = (ts + 1400) % BL_P
	return p >= BL_D ? 1 : 0.5 + 0.5 * Math.cos((p / BL_D) * Math.PI * 2)
}

export default {
	data: function() {
		return {
			targetMood: 76, targetVit: 65,
			curMood: 76, curVit: 65,
			noteText: '',
			trackRects: { mood: null, vit: null },
			activeSlider: '',
			pageBg: 'linear-gradient(180deg, #2d2750 0%, #221c3b 46%, #181427 100%)',
			heroBg: 'linear-gradient(180deg,rgba(110,100,195,0.72) 0%,rgba(90,80,175,0.20) 58%,rgba(20,18,36,0) 100%)',
			controlsBg: '#181427',
			mascotTf: 'translateY(0) rotate(0deg) scale(1)',
			haloBg: 'radial-gradient(circle,rgba(216,206,255,0.12) 0%,rgba(216,206,255,0.03) 42%,transparent 70%)',
			haloOp: '0', haloTf: 'translateX(-50%) scale(1)',
			emoThumbLeft: 'calc(76% - 29rpx)', emoThumbBg: '#b8a5ff',
			vitThumbLeft: 'calc(65% - 29rpx)', vitThumbBg: '#a8b2df', vitTrackBg: 'linear-gradient(90deg, rgba(96,88,136,0.92) 0%, rgba(128,118,174,0.94) 50%, rgba(148,136,192,0.92) 100%)',
			faceOY: 0, browLP: [79,89,91,88,103,89], browRP: [138,89,150,88,162,89],
			eyeR: 7.1, mouthP: [108,124,120.7,128,133,124],
			tearA: 0, blushA: 0.24, sparkA: 0.4,
			gradRGB: [220,210,255], tintRGBA: [150,130,230,0.08],
			timerId: null, lastTs: 0,
			saving: false
		}
	},
	computed: {
		heading: function() {
			if (this.targetMood < 35) return '把低落也好好接住'
			if (this.targetMood < 65) return '今天的你很平静'
			return '这一刻值得被珍藏'
		},
		moodLabel: function() {
			var m = this.targetMood
			if (m < 20) return '有点难过'
			if (m < 40) return '低低地垂着'
			if (m < 60) return '平静放松'
			if (m < 80) return '轻轻开心'
			return '明亮开心'
		},
		vitLabel: function() {
			var v = this.targetVit
			if (v < 20) return '慢慢充电'
			if (v < 40) return '有点懒洋洋'
			if (v < 60) return '舒服刚刚好'
			if (v < 80) return '开始活跃啦'
			return '能量满满'
		}
	},
	mounted: function() {
		var self = this
		this.$nextTick(function() {
			self.measureSliders()
			self.lastTs = Date.now()
			setTimeout(function() { self.tick() }, 100)
		})
	},
	beforeDestroy: function() {
		if (this.timerId) clearTimeout(this.timerId)
	},
	methods: {
		goBack: function() {
			if (getCurrentPages().length > 1) { uni.navigateBack(); return }
			uni.reLaunch({ url: '/pages/index/index' })
		},
		doConfirm: function() {
			if (this.saving) return
			var oid = getApiOpenid()
			if (!oid) {
				uni.showToast({ title: '请先登录（需写入 openid）', icon: 'none', duration: 2800 })
				return
			}
			var self = this
			this.saving = true
			var uid = getApiUserId()
			uni.showLoading({ title: '保存中', mask: true })
			postEmotionRecord({
				user_id: uid,
				openid: oid,
				emotion_score: Math.round(self.targetMood),
				vitality_score: Math.round(self.targetVit),
				note: (self.noteText || '').trim() || null
			}).then(function() {
				try {
					uni.setStorageSync('shadowEmotionSnapshot', JSON.stringify({
						mood: Math.round(self.targetMood),
						vit: Math.round(self.targetVit),
						note: (self.noteText || '').trim(),
						savedAt: Date.now()
					}))
				} catch (e) {}
				uni.hideLoading()
				uni.showToast({ title: '已记录', icon: 'success' })
				setTimeout(function() { self.goBack() }, 450)
			}).catch(function(err) {
				uni.hideLoading()
				var raw = (err && err.errMsg) || (err && err.message) || ''
				console.error('[emotion-record] save failed', raw, err)
				var msg = '保存失败'
				if (raw) {
					if (raw.indexOf('request:fail') >= 0 || raw === '网络请求失败') {
						msg = describeRequestError(err)
					} else if (raw.indexOf('timeout') >= 0) {
						msg = '请求超时，请稍后重试'
					} else {
						msg = raw.length > 36 ? raw.slice(0, 33) + '…' : raw
					}
				}
				uni.showToast({ title: msg, icon: 'none', duration: 3000 })
			}).then(function() {
				self.saving = false
			})
		},
		measureSliders: function() {
			var self = this
			var q = uni.createSelectorQuery().in(this)
			q.select('.emotion-hitbox').boundingClientRect()
			q.select('.vitality-hitbox').boundingClientRect()
			q.exec(function(r) {
				self.trackRects.mood = r && r[0] ? r[0] : null
				self.trackRects.vit  = r && r[1] ? r[1] : null
			})
		},
		startSlide: function(type, ev) {
			this.activeSlider = type
			this.slide(type, ev)
		},
		moveSlide: function(type, ev)  {
			if (this.activeSlider && this.activeSlider !== type) return
			this.slide(type, ev)
		},
		endSlide: function() {
			this.activeSlider = ''
		},
		slide: function(type, ev) {
			var rect = this.trackRects[type === 'mood' ? 'mood' : 'vit']
			var t = ev.touches && ev.touches[0]
			var clientX = t ? t.clientX : ev.clientX
			if (!rect || typeof clientX !== 'number') return
			var pct = clamp(((clientX - rect.left) / rect.width) * 100, 0, 100)
			if (type === 'mood') {
				this.targetMood = pct
				this.curMood = pct
			} else {
				this.targetVit = pct
				this.curVit = pct
			}
		},
		tick: function() {
			var self = this
			var now = Date.now()
			var dt = Math.min(40, now - (this.lastTs || now))
			this.lastTs = now
			this.curMood = this.activeSlider === 'mood'
				? this.targetMood
				: lerp(this.curMood, this.targetMood, 1 - Math.pow(0.000005, dt / 1000))
			this.curVit = this.activeSlider === 'vit'
				? this.targetVit
				: lerp(this.curVit, this.targetVit, 1 - Math.pow(0.00001, dt / 1000))
			this.computeFrame(now)
			this.timerId = setTimeout(function() { self.tick() }, 33)
		},
		computeFrame: function(ts) {
			var wt = getWeights(this.curMood)
			this.faceOY = lerp(4.5, -2.5, this.curMood / 100)
			this.browLP = weightedArr([BROW_L.sad, BROW_L.calm, BROW_L.happy, BROW_L.angry], wt)
			this.browRP = weightedArr([BROW_R.sad, BROW_R.calm, BROW_R.happy, BROW_R.angry], wt)
			var blink = blinkScale(ts)
			this.eyeR = (EYE_RY[0]*wt[0] + EYE_RY[1]*wt[1] + EYE_RY[2]*wt[2] + EYE_RY[3]*wt[3]) * blink
			this.mouthP = weightedArr([MOUTH.sad, MOUTH.calm, MOUTH.happy, MOUTH.angry], wt)
			this.tearA  = TEARS[0]*wt[0] + TEARS[1]*wt[1] + TEARS[2]*wt[2]
			this.blushA = BLUSH[0]*wt[0] + BLUSH[1]*wt[1] + BLUSH[2]*wt[2]

			var gr=0,gg=0,gb=0,tr=0,tg=0,tb=0,to=0,mr=0,mg2=0,mb=0
			for (var i=0;i<4;i++){
				gr+=GRAD_C[i][0]*wt[i]; gg+=GRAD_C[i][1]*wt[i]; gb+=GRAD_C[i][2]*wt[i]
				tr+=TINT_C[i][0]*wt[i]; tg+=TINT_C[i][1]*wt[i]; tb+=TINT_C[i][2]*wt[i]; to+=TINT_C[i][3]*wt[i]
				mr+=MG_C[i][0]*wt[i]; mg2+=MG_C[i][1]*wt[i]; mb+=MG_C[i][2]*wt[i]
			}
			this.gradRGB = [~~gr,~~gg,~~gb]
			this.tintRGBA = [~~tr,~~tg,~~tb,to]
			var e = this.curVit / 100
			var hotR = Math.round(lerp(72, 212, e))
			var hotG = Math.round(lerp(68, 90, e))
			var hotB = Math.round(lerp(148, 126, e))
			var baseR = Math.round(lerp(45, 64, e))
			var baseG = Math.round(lerp(39, 28, e))
			var baseB = Math.round(lerp(80, 46, e))
			this.pageBg = 'linear-gradient(180deg, rgb(' + hotR + ',' + hotG + ',' + hotB + ') 0%, rgb(' + Math.round(lerp(34, 44, e)) + ',' + Math.round(lerp(28, 20, e)) + ',' + Math.round(lerp(59, 34, e)) + ') 48%, rgb(' + baseR + ',' + baseG + ',' + baseB + ') 100%)'
			this.heroBg = 'linear-gradient(180deg,rgba('+~~mr+','+~~mg2+','+~~mb+',' + (0.68 + e * 0.14).toFixed(3) + ') 0%,rgba(' + Math.round(lerp(mr, 238, e * 0.9)) + ',' + Math.round(lerp(mg2, 106, e * 0.9)) + ',' + Math.round(lerp(mb, 132, e * 0.9)) + ',' + (0.12 + e * 0.20).toFixed(3) + ') 58%,rgba(20,18,36,0) 100%)'
			this.controlsBg = 'linear-gradient(180deg, rgba(' + Math.round(lerp(24, 34, e)) + ',' + Math.round(lerp(20, 18, e)) + ',' + Math.round(lerp(39, 30, e)) + ',1) 0%, rgba(' + Math.round(lerp(24, 28, e)) + ',' + Math.round(lerp(20, 14, e)) + ',' + Math.round(lerp(39, 24, e)) + ',1) 100%)'

			this.emoThumbLeft = 'calc('+this.curMood.toFixed(2)+'% - 29rpx)'
			this.vitThumbLeft = 'calc('+this.curVit.toFixed(2)+'% - 29rpx)'
			var h,s2,l2
			if(this.curMood<50){var t2=this.curMood/50;h=lerp(232,200,t2);s2=lerp(60,80,t2);l2=lerp(70,65,t2)}
			else{var t2=(this.curMood-50)/50;h=lerp(200,40,t2);s2=lerp(80,88,t2);l2=lerp(65,60,t2)}
			this.emoThumbBg='hsl('+h+','+s2+'%,'+l2+'%)'
			var vGray=Math.round(210-this.curVit*0.7)
			this.vitThumbBg='rgb('+vGray+','+vGray+','+vGray+')'

			var amp = 3 + e * 18, spd = 0.001 + e * 0.0065
			var bob = Math.sin(ts * spd) * amp
			var tilt = Math.sin(ts * spd * 0.63) * (0.4 + e * 3.2)
			var sc = 0.97 + e * 0.08
			this.mascotTf = 'translateY('+bob.toFixed(2)+'px) rotate('+tilt.toFixed(2)+'deg) scale('+sc.toFixed(3)+')'
			this.sparkA = 0.4 + e * 0.6

			var hs = 0.96 + e * 0.10 + Math.sin(ts * spd * 0.72) * 0.02
			this.haloOp = '0'
			this.haloTf = 'translateX(-50%) scale('+hs.toFixed(3)+')'
			this.haloBg = 'radial-gradient(circle,rgba('+~~gr+','+~~gg+','+~~gb+',0.10) 0%,rgba('+~~gr+','+~~gg+','+~~gb+',0.02) 40%,transparent 68%)'
			this.vitTrackBg = 'linear-gradient(90deg, rgba(' + Math.round(lerp(96, 162, e)) + ',' + Math.round(lerp(88, 82, e)) + ',' + Math.round(lerp(136, 92, e)) + ',0.92) 0%, rgba(' + Math.round(lerp(128, 214, e)) + ',' + Math.round(lerp(118, 110, e)) + ',' + Math.round(lerp(174, 92, e)) + ',0.94) 52%, rgba(' + Math.round(lerp(148, 255, e)) + ',' + Math.round(lerp(136, 142, e)) + ',' + Math.round(lerp(192, 106, e)) + ',0.92) 100%)'
		},
		buildQuadPath: function(points) {
			if (!points || points.length < 6) return ''
			return 'M ' + points[0].toFixed(1) + ' ' + points[1].toFixed(1) +
				' Q ' + points[2].toFixed(1) + ' ' + points[3].toFixed(1) +
				' ' + points[4].toFixed(1) + ' ' + points[5].toFixed(1)
		},
		rgbStr: function(color) {
			return 'rgb(' + color[0] + ',' + color[1] + ',' + color[2] + ')'
		}
	}
}
</script>

<style scoped>
.page {
	min-height: 100vh;
	position: relative;
	overflow: hidden;
	background:
		linear-gradient(180deg, #2d2750 0%, #221c3b 46%, #181427 100%);
	display: flex;
	flex-direction: column;
}

.page::before {
	content: '';
	position: absolute;
	inset: 0;
	background:
		radial-gradient(ellipse 88% 44% at 50% 2%, rgba(154, 143, 203, 0.22) 0%, rgba(154, 143, 203, 0.05) 46%, transparent 74%);
	pointer-events: none;
}

.nav-back {
	position: fixed;
	top: 88rpx;
	left: 24rpx;
	z-index: 20;
	width: 72rpx;
	height: 72rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 999rpx;
	background: rgba(72, 62, 122, 0.72);
	border: 1rpx solid rgba(214,203,245,0.12);
}

.back-arrow {
	font-size: 44rpx;
	color: #fff;
	font-weight: 300;
	margin-top: -4rpx;
}

.hero {
	position: relative;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 104rpx 44rpx 22rpx;
	transition: background 0.3s ease;
	overflow: hidden;
	z-index: 1;
}

.hero::before {
	content: '';
	position: absolute;
	left: 50%;
	top: 40rpx;
	width: 560rpx;
	height: 360rpx;
	transform: translateX(-50%);
	background: radial-gradient(circle, rgba(130, 118, 215, 0.16) 0%, rgba(130, 118, 215, 0.04) 52%, transparent 82%);
	filter: blur(26rpx);
	pointer-events: none;
}

.hero::after {
	content: '';
	position: absolute;
	left: 0;
	right: 0;
	bottom: 0;
	height: 200rpx;
	background: linear-gradient(180deg, rgba(24, 20, 39, 0) 0%, rgba(24, 20, 39, 0.78) 70%, #181427 100%);
	pointer-events: none;
}

.mascot-stage {
	position: relative;
	width: 100%;
	height: 404rpx;
	z-index: 1;
}

.mascot-halo {
	display: none;
}

.mascot-wrap {
	position: absolute;
	left: 50%;
	top: 42rpx;
	width: 492rpx;
	height: 388rpx;
	margin-left: -246rpx;
	transform-origin: 50% 60%;
	filter: drop-shadow(0 24rpx 44rpx rgba(20, 16, 38, 0.18));
	will-change: transform;
	pointer-events: none;
}

.sprite-svg {
	width: 492rpx;
	height: 388rpx;
	display: block;
}

.mood-heading {
	margin-top: -6rpx;
	font-size: 52rpx;
	font-weight: 800;
	color: #ffffff;
	text-align: center;
	line-height: 1.12;
	text-shadow: 0 10rpx 28rpx rgba(36,28,82,0.22);
	position: relative;
	z-index: 2;
}

.controls {
	position: relative;
	flex: 1;
	padding: 8rpx 44rpx 0;
	padding-bottom: calc(60rpx + env(safe-area-inset-bottom));
	background: #181427;
	border-radius: 0;
	box-shadow: none;
	border-top: none;
	z-index: 2;
}

.note-row {
	display: flex;
	align-items: center;
	height: 96rpx;
	padding: 0 34rpx;
	gap: 20rpx;
	border-radius: 999rpx;
	background: rgba(89, 74, 145, 0.92);
	border: 1rpx solid rgba(214,203,245,0.18);
	box-shadow: 0 12rpx 28rpx rgba(20,15,50,0.16), inset 0 1rpx 0 rgba(255,255,255,0.06);
	margin-bottom: 40rpx;
}

.note-pen {
	font-size: 30rpx;
	color: rgba(255,255,255,0.90);
	flex-shrink: 0;
}

.note-input {
	flex: 1;
	background: transparent;
	border: none;
	outline: none;
	color: #ffffff;
	font-size: 29rpx;
	font-weight: 600;
}

.metric {
	margin-bottom: 44rpx;
	padding: 0 0 4rpx;
	border-radius: 0;
	background: transparent;
	border: none;
	box-shadow: none;
}

.metric-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.metric-title {
	font-size: 34rpx;
	font-weight: 700;
	color: rgba(236,232,248,0.92);
}

.metric-val {
	font-size: 26rpx;
	font-weight: 600;
	color: rgba(226,218,244,0.72);
}

.slider {
	position: relative;
	height: 42rpx;
}

.track {
	position: absolute;
	top: 8rpx;
	left: 0;
	right: 0;
	height: 26rpx;
	border-radius: 999rpx;
	pointer-events: none;
	box-shadow: inset 0 1rpx 0 rgba(255,255,255,0.04), 0 4rpx 12rpx rgba(13,10,30,0.08);
}

.emotion-track {
	background: linear-gradient(90deg, rgba(116,132,240,0.88) 0%, rgba(146,126,212,0.84) 52%, rgba(200,170,255,0.70) 100%);
}

.vit-track {
	background: linear-gradient(90deg, rgba(96,88,136,0.92) 0%, rgba(128,118,174,0.94) 50%, rgba(148,136,192,0.92) 100%);
}

.thumb {
	position: absolute;
	top: 1rpx;
	width: 58rpx;
	height: 36rpx;
	border-radius: 20rpx;
	border: 3rpx solid rgba(255,255,255,0.95);
	box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.22);
	pointer-events: none;
	z-index: 3;
}

.hints {
	display: flex;
	justify-content: space-between;
	margin-top: 18rpx;
}

.hints text {
	font-size: 23rpx;
	color: rgba(214,205,236,0.46);
}

.actions {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 18rpx;
	margin-top: 8rpx;
}

.btn-ghost, .btn-primary {
	width: 100%;
	height: 96rpx;
	border-radius: 999rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.btn-ghost {
	width: auto;
	height: 64rpx;
	background: transparent;
	border: none;
}

.btn-ghost text {
	font-size: 26rpx;
	font-weight: 600;
	color: rgba(214,205,236,0.50);
}

.btn-primary {
	width: 100%;
	background: linear-gradient(148deg, #9a8fcb 0%, #8276ba 52%, #7264af 100%);
	box-shadow: 0 16rpx 36rpx rgba(100,88,170,0.30), inset 0 1rpx 0 rgba(255,255,255,0.16);
}

.btn-primary text {
	font-size: 28rpx;
	font-weight: 700;
	color: rgba(255,255,255,0.96);
}
</style>
