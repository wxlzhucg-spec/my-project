<template>
	<view class="overlay-root">
		<!-- 固定在背后的毛玻璃遮罩 -->
		<view class="modal-backdrop" :style="{ background: backdropBackground }"></view>

		<!-- 整体可滚动的页面 -->
		<scroll-view class="page-scroll" scroll-y="true">
			<view class="page-flow">

				<!-- ── 上半：透明英雄区 ── -->
				<view class="hero-section" @tap="handleBackdropTap">
					<view class="hero-gradient" :style="{ background: gradientBackground }"></view>

					<!-- 纸条输入（顶部，阻止点击穿透到关闭） -->
					<view class="note-input-container" @tap.stop @touchstart.stop @touchmove.stop>
						<svg fill="none" viewBox="0 0 20 20"><path d="M9.167 2.5H4.167C3.724 2.5 3.301 2.676 2.988 2.988C2.676 3.301 2.5 3.725 2.5 4.167V15.833C2.5 16.275 2.676 16.699 2.988 17.012C3.301 17.324 3.724 17.5 4.167 17.5H15.833C16.275 17.5 16.699 17.324 17.012 17.012C17.324 16.699 17.5 16.275 17.5 15.833V10.833M16.083 2.745C16.239 2.589 16.451 2.501 16.672 2.501C16.893 2.501 17.105 2.589 17.261 2.745C17.417 2.9 17.505 3.112 17.505 3.333C17.505 3.554 17.417 3.766 17.261 3.922L9.601 11.583C9.444 11.735 9.233 11.819 9.015 11.817C8.797 11.815 8.588 11.728 8.433 11.573C8.279 11.419 8.191 11.21 8.189 10.991C8.187 10.773 8.271 10.562 8.423 10.405L16.083 2.745Z" stroke="rgba(255,255,255,0.8)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
						<input v-model="noteText" class="note-input" placeholder="写个小纸条，记录此刻感受..." />
					</view>

					<!-- 精灵 -->
					<view class="mascot-stage" @tap.stop>
						<view class="mascot-halo" :style="{ background: haloBackground, opacity: haloOpacity, transform: haloTransform }"></view>
						<view class="mascot-wrap" :style="{ transform: mascotTransform }">
							<svg class="mascot-svg" fill="none" viewBox="0 0 241.376 188.924">
								<mask id="body-mask" maskUnits="userSpaceOnUse" style="mask-type:alpha">
									<path d="M148.652 0C182.792 0.000197914 210.468 27.6759 210.468 61.8154C210.468 65.0652 210.216 68.2567 209.732 71.3711C228.627 82.089 241.376 102.386 241.376 125.66C241.376 158.482 215.946 185.714 183.158 187.199C162.354 188.141 139.439 188.924 120.688 188.924C101.936 188.924 79.0222 188.141 58.2178 187.199C25.4299 185.714 0 158.482 0 125.66C0 100.709 14.651 79.1799 35.8194 69.2061C35.4947 67.2817 35.3233 65.3048 35.3233 63.2881C35.3233 43.7796 51.138 27.9648 70.6465 27.9648C78.9593 27.9648 86.6002 30.8374 92.6338 35.6426C102.489 14.5861 123.868 0 148.652 0Z" fill="white"/>
								</mask>
								<g mask="url(#body-mask)">
									<g filter="url(#body-glow-filter)">
										<ellipse cx="125.451" cy="107.208" rx="111.979" ry="90.3693" fill="url(#body-grad)"/>
									</g>
									<rect x="-5" y="-5" width="252" height="200" :fill="bodyTintFill" :opacity="bodyTintOpacity"/>
								</g>
								<path d="M218 154 C222 152 227 145 228 138" stroke="#FFE08A" stroke-linecap="round" stroke-width="5.2" fill="none" :opacity="sparkOpacity"/>
								<path d="M29 89 C26 90 22 95 21 100" stroke="#FFE08A" stroke-linecap="round" stroke-width="5.2" fill="none" :opacity="sparkOpacity"/>
								<g id="face-layer">
									<g :transform="faceInnerTransform">
										<path :d="browLD" stroke="#2C2C35" stroke-width="5" stroke-linecap="round" fill="none"/>
										<path :d="browRD" stroke="#2C2C35" stroke-width="5" stroke-linecap="round" fill="none"/>
										<ellipse cx="91" cy="98" rx="7.5" :ry="eyeRy" fill="#2C2C35"/>
										<ellipse cx="151" cy="98" rx="7.5" :ry="eyeRy" fill="#2C2C35"/>
										<g :opacity="blushOpacity">
											<ellipse cx="68" cy="108" rx="11" ry="6" fill="#FF7799" transform="rotate(-12, 68, 108)"/>
											<ellipse cx="174" cy="108" rx="11" ry="6" fill="#FF7799" transform="rotate(12, 174, 108)"/>
										</g>
										<g :opacity="tearsOpacity">
											<path d="M91 111 Q87 120 89 128 Q91 136 93 128 Q95 120 91 111Z" fill="#88BBFF"/>
											<path d="M151 111 Q147 120 149 128 Q151 136 153 128 Q155 120 151 111Z" fill="#88BBFF"/>
										</g>
										<path :d="mouthArcD" fill="none" stroke="#2C2C35" stroke-width="5.5" stroke-linecap="round"/>
									</g>
								</g>
								<defs>
									<filter id="body-glow-filter" x="-40" y="-36" width="330" height="286" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
										<feFlood flood-opacity="0" result="BackgroundImageFix"/>
										<feBlend in="SourceGraphic" in2="BackgroundImageFix" mode="normal" result="shape"/>
										<feGaussianBlur stdDeviation="18"/>
									</filter>
									<radialGradient id="body-grad" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(125.451 107.208) rotate(90) scale(90.37 111.98)">
										<stop offset="0.22" :stop-color="gradStopColor"/>
										<stop offset="1" :stop-color="gradStopColor" stop-opacity="0.69"/>
									</radialGradient>
								</defs>
							</svg>
						</view>
					</view>

					<!-- 标题 + 状态胶囊 -->
					<view class="hero-copy" @tap.stop>
						<text class="hero-title">{{ moodHeading }}</text>
					</view>
					<view class="status-pills" @tap.stop>
						<view class="status-pill">
							<text class="status-pill-label">情绪</text>
							<text class="status-pill-value">{{ moodLabel }}</text>
						</view>
						<view class="status-pill">
							<text class="status-pill-label">活力</text>
							<text class="status-pill-value">{{ vitalityLabel }}</text>
						</view>
					</view>
				</view>

				<!-- ── 下半：深色操控区（直接连着上面，无悬浮）── -->
				<view class="control-section">
					<view class="panel-handle"></view>

					<view class="metric-block">
						<view class="metric-header">
							<text class="metric-title">情绪值</text>
							<text class="metric-value">{{ roundedMood }} · {{ moodLabel }}</text>
						</view>
						<view
							class="slider-wrap emotion emotion-hitbox"
							@touchstart.stop.prevent="startSlide('mood', $event)"
							@touchmove.stop.prevent="moveSlide('mood', $event)"
						>
							<view class="slider-track emotion"></view>
							<view class="slider-thumb" :style="{ left: emotionThumbLeft, background: emotionThumbBg }"></view>
						</view>
						<view class="slider-hints">
							<text>难过</text>
							<text>平静</text>
							<text>开心</text>
						</view>
					</view>

					<view class="metric-block">
						<view class="metric-header">
							<text class="metric-title">活力值</text>
							<text class="metric-value">{{ roundedVitality }} · {{ vitalityLabel }}</text>
						</view>
						<view
							class="slider-wrap vitality vitality-hitbox"
							@touchstart.stop.prevent="startSlide('vitality', $event)"
							@touchmove.stop.prevent="moveSlide('vitality', $event)"
						>
							<view class="slider-track vitality"></view>
							<view class="slider-thumb" :style="{ left: vitalityThumbLeft, background: vitalityThumbBg }"></view>
						</view>
						<view class="slider-hints vitality-hints">
							<text>慵懒</text>
							<text>舒展</text>
							<text>满格</text>
						</view>
					</view>

					<view class="panel-actions">
						<view class="ghost-btn" @tap="handleBackdropTap">
							<text>稍后再记</text>
						</view>
						<view class="ok-btn" @tap="handleConfirm">
							<text>记录现在</text>
						</view>
					</view>
				</view>

			</view>
		</scroll-view>
	</view>
</template>

<script>
const lerp = (a, b, t) => a + (b - a) * t

function clamp(v, lo, hi) {
	return Math.max(lo, Math.min(hi, v))
}

function weightedArr(arrs, weights) {
	const n = arrs[0].length
	const out = new Array(n).fill(0)
	arrs.forEach((arr, i) => {
		for (let j = 0; j < n; j++) out[j] += arr[j] * weights[i]
	})
	return out
}

function getWeights(e) {
	let sad = 0
	let calm = 0
	let happy = 0
	if (e < 50) {
		sad = 1 - e / 50
		calm = e / 50
	} else {
		calm = 1 - (e - 50) / 50
		happy = (e - 50) / 50
	}
	return { sad, calm, happy, angry: 0 }
}

const BROW = {
	happy: { l: [79, 87, 91, 81, 103, 87], r: [138, 87, 150, 81, 162, 87] },
	calm: { l: [79, 89, 91, 88, 103, 89], r: [138, 89, 150, 88, 162, 89] },
	sad: { l: [79, 91, 91, 84, 103, 89], r: [138, 89, 150, 84, 162, 91] },
	angry: { l: [79, 85, 91, 92, 103, 85], r: [138, 85, 150, 92, 162, 85] }
}

const MOUTH_ARC = {
	happy: [100, 120, 120.7, 138, 141, 120],
	calm: [108, 124, 120.7, 128, 133, 124],
	sad: [108, 130, 120.7, 122, 133, 130],
	angry: [105, 128, 120.7, 124, 136, 128]
}

const EYE_RY = {
	sad: 5.6,
	calm: 7.1,
	happy: 8.5,
	angry: 4.8
}

const BLUSH = {
	sad: 0.16,
	calm: 0.24,
	happy: 0.58,
	angry: 0.08
}

const TEARS = {
	sad: 0.95,
	calm: 0.08,
	happy: 0,
	angry: 0
}

const GRAD_COLOR = {
	sad: [200, 195, 255],
	calm: [215, 200, 255],
	happy: [255, 230, 168],
	angry: [255, 218, 168]
}

const TINT = {
	sad: [100, 100, 220, 0.22],
	calm: [150, 130, 230, 0.08],
	happy: [255, 230, 168, 0],
	angry: [255, 110, 80, 0.18]
}

const MODAL_GRAD = {
	sad: [116, 116, 210],
	calm: [132, 118, 214],
	happy: [164, 142, 226],
	angry: [182, 128, 198]
}

const BLINK_PERIOD = 4000
const BLINK_DUR = 150
function blinkScale(ts) {
	const phase = (ts + 1400) % BLINK_PERIOD
	if (phase >= BLINK_DUR) return 1
	return 0.5 + 0.5 * Math.cos((phase / BLINK_DUR) * Math.PI * 2)
}

export default {
	name: 'emotion-record-overlay',
	props: {
		initialMood: {
			type: Number,
			default: 76
		},
		initialVitality: {
			type: Number,
			default: 65
		}
	},
	data() {
		return {
			targetMood: this.initialMood,
			targetVit: this.initialVitality,
			curMood: this.initialMood,
			curVit: this.initialVitality,
			noteText: '',
			trackRects: {
				mood: null,
				vitality: null
			},
			faceInnerTransform: 'translate(0,0)',
			browLD: '',
			browRD: '',
			eyeRy: '7.5',
			mouthArcD: '',
			tearsOpacity: '0',
			blushOpacity: '0.6',
			bodyTintFill: 'rgb(0,0,0)',
			bodyTintOpacity: '0',
			gradStopColor: 'rgb(255,255,255)',
			mascotTransform: 'translateY(0px) rotate(0deg) scale(1)',
			sparkOpacity: '0.4',
			backdropBackground: 'rgba(24,22,42,0.26)',
			gradientBackground: 'linear-gradient(180deg,rgba(154,143,203,0.52) 0%,rgba(130,118,186,0.18) 56%,transparent 100%)',
			haloBackground: 'radial-gradient(circle, rgba(216,206,255,0.16) 0%, rgba(216,206,255,0.04) 42%, rgba(216,206,255,0) 70%)',
			haloOpacity: '0.08',
			haloTransform: 'translateX(-50%) scale(1)',
			emotionThumbLeft: 'calc(76% - 14.5px)',
			emotionThumbBg: '#f6cc34',
			vitalityThumbLeft: 'calc(65% - 14.5px)',
			vitalityThumbBg: '#d4d4d4',
			timerId: null,
			lastTs: 0
		}
	},
	computed: {
		roundedMood() {
			return Math.round(this.targetMood)
		},
		roundedVitality() {
			return Math.round(this.targetVit)
		},
		moodLabel() {
			const mood = this.targetMood
			if (mood < 20) return '有点难过'
			if (mood < 40) return '低低地垂着'
			if (mood < 60) return '平静放松'
			if (mood < 80) return '轻轻开心'
			return '明亮开心'
		},
		vitalityLabel() {
			const vitality = this.targetVit
			if (vitality < 20) return '慢慢充电'
			if (vitality < 40) return '有点懒洋洋'
			if (vitality < 60) return '舒服刚刚好'
			if (vitality < 80) return '开始活跃啦'
			return '能量满满'
		},
		moodHeading() {
			const mood = this.targetMood
			if (mood < 35) return '把低落也好好接住'
			if (mood < 65) return '今天的你很平静'
			return '这一刻值得被珍藏'
		},
		moodSubheading() {
			return `情绪决定表情，活力决定节奏。让小精灵替你把现在的自己记下来。`
		}
	},
	mounted() {
		this.$nextTick(() => {
			// Lock body scroll so background page doesn't move
			if (typeof document !== 'undefined') {
				document.body.style.overflow = 'hidden'
				document.documentElement.style.overflow = 'hidden'
				
				// Fix for some mobile browsers
				document.body.addEventListener('touchmove', this.preventDefault, { passive: false })
			}
			this.measureTracks()
			this.lastTs = Date.now()
			this.tick()
		})
	},
	beforeDestroy() {
		// Restore body scroll
		if (typeof document !== 'undefined') {
			document.body.style.overflow = ''
			document.documentElement.style.overflow = ''
			document.body.removeEventListener('touchmove', this.preventDefault)
		}
		if (this.timerId) {
			clearTimeout(this.timerId)
		}
	},
	methods: {
		preventDefault(e) {
			e.preventDefault()
		},
		measureTracks() {
			const query = uni.createSelectorQuery().in(this)
			query.select('.emotion-hitbox').boundingClientRect()
			query.select('.vitality-hitbox').boundingClientRect()
			query.exec((rects) => {
				this.trackRects.mood = rects && rects[0] ? rects[0] : null
				this.trackRects.vitality = rects && rects[1] ? rects[1] : null
			})
		},
		handleBackdropTap() {
			this.$emit('close')
		},
		handleConfirm() {
			this.$emit('confirm', {
				mood: Math.round(this.targetMood),
				vitality: Math.round(this.targetVit),
				noteText: this.noteText
			})
		},
		startSlide(type, event) {
			this.updateSlider(type, event)
		},
		moveSlide(type, event) {
			this.updateSlider(type, event)
		},
		updateSlider(type, event) {
			const rect = this.trackRects[type]
			const touch = event.touches && event.touches[0]
			if (!rect || !touch) return
			let percentage = ((touch.clientX - rect.left) / rect.width) * 100
			percentage = clamp(percentage, 0, 100)
			if (type === 'mood') {
				this.targetMood = percentage
				return
			}
			this.targetVit = percentage
		},
		tick() {
			const now = Date.now()
			const dt = Math.min(40, now - (this.lastTs || now))
			this.lastTs = now

			const tM = 1 - Math.pow(0.000005, dt / 1000)
			const tV = 1 - Math.pow(0.00001, dt / 1000)
			this.curMood = lerp(this.curMood, this.targetMood, tM)
			this.curVit = lerp(this.curVit, this.targetVit, tV)

			this.renderFrame(now)
			this.timerId = setTimeout(() => this.tick(), 16)
		},
		renderFrame(ts) {
			const w = getWeights(this.curMood)
			const states = ['sad', 'calm', 'happy', 'angry']
			const weights = [w.sad, w.calm, w.happy, w.angry]

			const faceY = lerp(4, -3, this.curMood / 100)
			this.faceInnerTransform = `translate(0, ${faceY.toFixed(1)})`

			const bl = weightedArr([BROW.sad.l, BROW.calm.l, BROW.happy.l, BROW.angry.l], weights)
			const br = weightedArr([BROW.sad.r, BROW.calm.r, BROW.happy.r, BROW.angry.r], weights)
			this.browLD = `M ${bl[0].toFixed(1)} ${bl[1].toFixed(1)} Q ${bl[2].toFixed(1)} ${bl[3].toFixed(1)} ${bl[4].toFixed(1)} ${bl[5].toFixed(1)}`
			this.browRD = `M ${br[0].toFixed(1)} ${br[1].toFixed(1)} Q ${br[2].toFixed(1)} ${br[3].toFixed(1)} ${br[4].toFixed(1)} ${br[5].toFixed(1)}`

			const blink = blinkScale(ts)
			const moodEyeRy =
				EYE_RY.sad * w.sad +
				EYE_RY.calm * w.calm +
				EYE_RY.happy * w.happy +
				EYE_RY.angry * w.angry
			this.eyeRy = (moodEyeRy * blink).toFixed(2)

			const ma = weightedArr([MOUTH_ARC.sad, MOUTH_ARC.calm, MOUTH_ARC.happy, MOUTH_ARC.angry], weights)
			this.mouthArcD = `M ${ma[0].toFixed(1)} ${ma[1].toFixed(1)} Q ${ma[2].toFixed(1)} ${ma[3].toFixed(1)} ${ma[4].toFixed(1)} ${ma[5].toFixed(1)}`

			this.tearsOpacity = (
				TEARS.sad * w.sad +
				TEARS.calm * w.calm +
				TEARS.happy * w.happy +
				TEARS.angry * w.angry
			).toFixed(3)
			this.blushOpacity = (
				BLUSH.sad * w.sad +
				BLUSH.calm * w.calm +
				BLUSH.happy * w.happy +
				BLUSH.angry * w.angry
			).toFixed(3)

			let tr = 0
			let tg = 0
			let tb = 0
			let to = 0
			states.forEach((s, i) => {
				const c = TINT[s]
				tr += c[0] * weights[i]
				tg += c[1] * weights[i]
				tb += c[2] * weights[i]
				to += c[3] * weights[i]
			})
			this.bodyTintFill = `rgb(${~~tr},${~~tg},${~~tb})`
			this.bodyTintOpacity = to.toFixed(3)

			let gr = 0
			let gg = 0
			let gb = 0
			states.forEach((s, i) => {
				const c = GRAD_COLOR[s]
				gr += c[0] * weights[i]
				gg += c[1] * weights[i]
				gb += c[2] * weights[i]
			})
			this.gradStopColor = `rgb(${~~gr},${~~gg},${~~gb})`

			let mgr = 0
			let mgg = 0
			let mgb = 0
			states.forEach((s, i) => {
				const c = MODAL_GRAD[s]
				mgr += c[0] * weights[i]
				mgg += c[1] * weights[i]
				mgb += c[2] * weights[i]
			})
			this.gradientBackground = `linear-gradient(180deg,rgba(${~~mgr},${~~mgg},${~~mgb},0.52) 0%,rgba(${~~mgr},${~~mgg},${~~mgb},0.18) 56%,transparent 100%)`

			this.emotionThumbLeft = `calc(${this.curMood.toFixed(2)}% - 14.5px)`
			this.vitalityThumbLeft = `calc(${this.curVit.toFixed(2)}% - 14.5px)`

			let h
			let s
			let l
			if (this.curMood < 50) {
				const t = this.curMood / 50
				h = lerp(232, 200, t)
				s = lerp(60, 80, t)
				l = lerp(70, 65, t)
			} else {
				const t = (this.curMood - 50) / 50
				h = lerp(200, 40, t)
				s = lerp(80, 88, t)
				l = lerp(65, 60, t)
			}
			this.emotionThumbBg = `hsl(${h},${s}%,${l}%)`
			const vGray = Math.round(210 - this.curVit * 0.7)
			this.vitalityThumbBg = `rgb(${vGray},${vGray},${vGray})`

			const e = this.curVit / 100
			const amp = 3 + e * 18
			const speed = 0.001 + e * 0.0065
			const bob = Math.sin(ts * speed) * amp
			const tilt = Math.sin(ts * speed * 0.63) * (0.4 + e * 3.2)
			const scale = 0.97 + e * 0.08
			const haloScale = 0.96 + e * 0.12 + Math.sin(ts * speed * 0.72) * 0.03
			this.mascotTransform = `translateY(${bob.toFixed(2)}px) rotate(${tilt.toFixed(2)}deg) scale(${scale.toFixed(3)})`
			this.sparkOpacity = (0.15 + e * 0.85).toFixed(2)
			this.backdropBackground = `rgba(24,22,42,${(0.24 - e * 0.06).toFixed(3)})`
			this.haloOpacity = (0.03 + e * 0.05).toFixed(3)
			this.haloTransform = `translateX(-50%) scale(${haloScale.toFixed(3)})`
			this.haloBackground = `radial-gradient(circle, rgba(${~~gr},${~~gg},${~~gb},0.16) 0%, rgba(${~~gr},${~~gg},${~~gb},0.04) 42%, rgba(${~~gr},${~~gg},${~~gb},0) 70%)`
		}
	}
}
</script>

<style scoped>
/* ─── 根容器：固定全屏，内容在 scroll-view 里滚动 ─── */
.overlay-root {
	position: fixed;
	inset: 0;
	z-index: 100;
}

/* 固定的毛玻璃遮罩层，始终在视口里 */
.modal-backdrop {
	position: fixed;
	inset: 0;
	backdrop-filter: blur(18rpx);
	-webkit-backdrop-filter: blur(18rpx);
	transition: background 0.4s ease;
}

/* 可滚动的主容器 */
.page-scroll {
	position: absolute;
	inset: 0;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
}

/* 内容流：上半 + 下半竖向排列 */
.page-flow {
	position: relative;
	min-height: 100%;
	display: flex;
	flex-direction: column;
}

/* ─── 上半：透明英雄区 ─── */
.hero-section {
	position: relative;
	flex: 1;
	min-height: 640rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 88rpx 40rpx 32rpx;
	gap: 0;
	overflow: hidden;
}

.hero-section::after {
	content: '';
	position: absolute;
	left: 0;
	right: 0;
	bottom: 0;
	height: 140rpx;
	background: linear-gradient(180deg, rgba(18, 16, 31, 0) 0%, rgba(18, 16, 31, 0.82) 100%);
	pointer-events: none;
}

/* 跟随精灵颜色变化的渐变光晕（覆盖英雄区） */
.hero-gradient {
	position: absolute;
	inset: 0;
	pointer-events: none;
	opacity: 0.92;
	transition: background 0.35s ease;
}

/* 纸条输入：顶部白色胶囊 */
.note-input-container {
	position: relative;
	z-index: 2;
	width: 100%;
	height: 88rpx;
	background: rgba(255, 255, 255, 0.08);
	border: 1rpx solid rgba(214, 203, 245, 0.18);
	border-radius: 999rpx;
	display: flex;
	align-items: center;
	padding: 0 28rpx;
	gap: 16rpx;
	backdrop-filter: blur(14rpx);
	-webkit-backdrop-filter: blur(14rpx);
	margin-bottom: 20rpx;
	box-shadow: inset 0 1rpx 0 rgba(255, 255, 255, 0.08);
	transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.note-input-container:focus-within {
	background: rgba(255, 255, 255, 0.15);
	border-color: rgba(214, 203, 245, 0.34);
	box-shadow: 0 0 0 6rpx rgba(130, 118, 186, 0.10);
}

.note-input-container svg {
	width: 32rpx;
	height: 32rpx;
	flex-shrink: 0;
	opacity: 0.85;
}

.note-input {
	flex: 1;
	background: transparent;
	border: none;
	outline: none;
	color: #ffffff;
	font-size: 28rpx;
	font-weight: 500;
}

/* 精灵容器：固定高度，内部用绝对定位保持精灵居中 */
.mascot-stage {
	position: relative;
	width: 100%;
	height: 424rpx;
	flex-shrink: 0;
	z-index: 1;
}

.mascot-halo {
	position: absolute;
	left: 50%;
	top: 108rpx;
	width: 300rpx;
	height: 170rpx;
	margin-left: -150rpx;
	filter: blur(42rpx);
	will-change: transform, opacity;
	pointer-events: none;
}

.mascot-wrap {
	position: absolute;
	left: 50%;
	top: 20rpx;
	width: 482rpx;
	height: 420rpx;
	margin-left: -241rpx;
	transform-origin: 50% 60%;
	filter: drop-shadow(0 24rpx 38rpx rgba(32, 26, 60, 0.16));
	will-change: transform;
	pointer-events: none;
}

.mascot-svg {
	width: 100%;
	height: 100%;
	display: block;
	overflow: visible;
}

/* 情绪标题 */
.hero-copy {
	width: 100%;
	text-align: center;
	margin-top: 0;
	margin-bottom: 20rpx;
}

.hero-title {
	display: block;
	font-size: 48rpx;
	font-weight: 800;
	color: #ffffff;
	letter-spacing: 1rpx;
	text-shadow: 0 4rpx 16rpx rgba(35, 28, 68, 0.22);
	position: relative;
	z-index: 2;
}

/* 状态胶囊 */
.status-pills {
	display: flex;
	justify-content: center;
	gap: 16rpx;
	margin-bottom: 36rpx;
	position: relative;
	z-index: 2;
}

.status-pill {
	min-width: 192rpx;
	padding: 18rpx 28rpx;
	border-radius: 999rpx;
	background: rgba(255, 255, 255, 0.08);
	border: 1rpx solid rgba(214, 203, 245, 0.16);
	backdrop-filter: blur(18rpx);
	-webkit-backdrop-filter: blur(18rpx);
}

.status-pill-label {
	display: block;
	font-size: 20rpx;
	color: rgba(255, 255, 255, 0.6);
}

.status-pill-value {
	display: block;
	margin-top: 6rpx;
	font-size: 28rpx;
	font-weight: 600;
	color: #ffffff;
}

/* ─── 下半：深色操控区，紧接英雄区 ─── */
.control-section {
	background: linear-gradient(180deg, rgba(24, 22, 40, 0.98) 0%, rgba(20, 18, 36, 1) 100%);
	border-radius: 44rpx 44rpx 0 0;
	padding: 28rpx 40rpx;
	padding-bottom: calc(60rpx + env(safe-area-inset-bottom));
	box-shadow: 0 -16rpx 42rpx rgba(18, 15, 34, 0.30);
	border-top: 1rpx solid rgba(214, 203, 245, 0.08);
}

.panel-handle {
	width: 72rpx;
	height: 8rpx;
	margin: 0 auto 32rpx;
	border-radius: 999rpx;
	background: rgba(214, 203, 245, 0.18);
}

/* 情绪值 / 活力值区块 */
.metric-block {
	margin-bottom: 40rpx;
	padding: 24rpx 24rpx 20rpx;
	border-radius: 28rpx;
	background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%);
	border: 1rpx solid rgba(214,203,245,0.07);
}

.metric-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 22rpx;
}

.metric-title {
	font-size: 30rpx;
	font-weight: 600;
	color: rgba(255, 255, 255, 0.92);
}

.metric-value {
	font-size: 24rpx;
	color: rgba(214, 205, 236, 0.44);
}

.slider-wrap {
	position: relative;
	height: 36rpx;
}

.slider-track {
	position: absolute;
	top: 8rpx;
	left: 0;
	right: 0;
	height: 20rpx;
	border-radius: 999rpx;
	pointer-events: none;
}

.slider-track.emotion {
	background: linear-gradient(90deg, rgba(116,132,240,0.90) 0%, rgba(146,126,212,0.86) 52%, rgba(224,190,112,0.76) 100%);
}

.slider-track.vitality {
	background: linear-gradient(90deg, rgba(255,255,255,0.06) 0%, rgba(179,166,220,0.24) 50%, rgba(255,255,255,0.14) 100%);
}

.slider-thumb {
	position: absolute;
	top: 0;
	width: 58rpx;
	height: 36rpx;
	border-radius: 999rpx;
	border: 4rpx solid rgba(255, 255, 255, 0.92);
	box-shadow: 0 8rpx 18rpx rgba(20,18,36,0.32);
	pointer-events: none;
	z-index: 3;
	will-change: left, background-color;
}

.slider-hints {
	display: flex;
	justify-content: space-between;
	margin-top: 16rpx;
}

.slider-hints text {
	font-size: 22rpx;
	color: rgba(214,205,236,0.24);
}

/* 按钮区 */
.panel-actions {
	display: flex;
	gap: 20rpx;
	margin-top: 56rpx;
}

.ghost-btn,
.ok-btn {
	flex: 1;
	height: 96rpx;
	border-radius: 999rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.ghost-btn {
	background: rgba(255, 255, 255, 0.06);
	border: 1rpx solid rgba(214, 203, 245, 0.12);
}

.ghost-btn text {
	font-size: 28rpx;
	font-weight: 600;
	color: rgba(214, 205, 236, 0.54);
}

.ok-btn {
	background: linear-gradient(148deg, #9a8fcb 0%, #8276ba 52%, #7264af 100%);
	box-shadow: 0 12rpx 32rpx rgba(100, 88, 170, 0.34), inset 0 1rpx 0 rgba(255, 255, 255, 0.16);
}

.ok-btn text {
	font-size: 28rpx;
	font-weight: 700;
	color: rgba(255, 255, 255, 0.96);
}
</style>
