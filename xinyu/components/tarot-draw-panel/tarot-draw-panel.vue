<template>
<view :class="embedded ? 'tdm-embedded-wrap' : 'tdm-modal-root'">
	<view :class="embedded ? 'tdm-embedded-inner' : 'tdm-sheet tdm-sheet--fullscreen'">
		<view v-if="!embedded" class="tdm-sheet-shine"></view>
		<view v-if="!embedded" class="tdm-topbar">
			<text class="tdm-sheet-title">塔罗抽牌</text>
		</view>
		<view :class="embedded ? 'tdm-embedded-body' : 'tdm-sheet-body'">
<view class="page-root" :class="{
		'page-fan-pick': phase==='fanPick',
		'page-root--in-sheet': !embedded,
		'page-root--pick-ui': phase==='fanPick',
		'page-root--reveal-ui': phase==='preview'
	}">
	<view class="ambient"></view>
	<view class="nav-back" @tap="goBack"><text class="back-icon">‹</text></view>

	<!-- 提示 -->
	<text class="hint" v-if="phase==='shuffle'||phase==='shuffling'">正在为你洗牌...</text>
	<text class="hint hint--preview" v-if="phase==='preview'&&!pvDone">即将揭晓</text>
	<text class="hint hint--preview hint--glow" v-if="phase==='preview'&&pvDone">你的卡牌已揭晓</text>

	<!-- ===== 选牌 ===== -->
	<view v-if="phase==='fanPick'" class="pick-stack" :class="{ 'pick-stack--entering': fanPickEntering }">

		<view v-if="pickComplete" class="pick-complete-mask">
			<text class="pick-complete-text">三张已齐，解牌中...</text>
		</view>

		<view class="pick-header">
			<view class="pick-head-row">
				<text class="pick-title-one">{{ pickComplete ? '牌已落定' : '凭直觉选出三张' }}</text>
				<view class="pick-head-count" :class="{ 'pick-count--done': selected.length === 3 }">{{ selected.length }}/3</view>
			</view>
			<view class="pick-progress-track pick-progress-track--soft">
				<view class="pick-progress-fill" :style="{ width: pickProgressPercent + '%' }"></view>
			</view>
		</view>

		<view class="strip-stage strip-stage--arc">
			<scroll-view scroll-x class="strip-scroll" :scroll-left="stripScrollTarget" :show-scrollbar="false" :enable-flex="true" @scroll="onStripScroll">
				<view class="strip-inner">
					<view
						v-for="gi in deckIndexList"
						:key="'strip'+gi"
						class="strip-card"
						:class="{ stripPicked: !!pickedFan[gi], 'strip-card--focus': stripNearCenter(gi) }"
						:style="getStripCardStyle(gi)"
						@tap="pickFanByGlobal(gi)">
						<view class="fc-face fc-face-strip">
							<view class="fc-frame">
								<view class="cat cat--strip"><view class="ce ce-l"></view><view class="ce ce-r"></view><view class="ch"></view></view>
							</view>
						</view>
					</view>
				</view>
			</scroll-view>
			<view class="strip-edge strip-edge-left"></view>
			<view class="strip-edge strip-edge-right"></view>
		</view>

		<view class="slots-row slots-row--pick">
			<view v-for="si in 3" :key="'sl'+si" class="slot-box">
				<view v-if="selected.length >= si" class="slot-card">
					<view class="slot-back">
						<view class="slot-bframe">
							<view class="cat cat--slot"><view class="ce ce-l"></view><view class="ce ce-r"></view><view class="ch"></view></view>
						</view>
					</view>
				</view>
				<view v-else class="slot-empty"></view>
				<text class="slot-caption">{{ posLabels[si - 1] }}</text>
			</view>
		</view>

	</view>

	<!-- ===== 洗牌 / 摊开：扇形动效 ===== -->
	<view
		v-else-if="phase==='shuffle'||phase==='shuffling'||phase==='revealing'"
		class="fan-area">
		<view class="fan-pan-inner">
			<view v-for="(f,i) in fanCount" :key="'fan-'+i"
				class="fan-card"
				:class="{ fanCardLong: phase==='revealing', fanPicked: false }"
				:style="getFanStyle(i)">
				<view class="fc-face">
					<view class="fc-frame">
						<view class="cat"><view class="ce ce-l"></view><view class="ce ce-r"></view><view class="ch"></view></view>
					</view>
				</view>
			</view>
		</view>
	</view>

	<!-- ===== 预览阶段：放大翻牌 ===== -->
	<view class="pv-row" v-if="phase==='preview'">
		<view v-for="si in 3" :key="'pv'+si" class="pv-col">
			<view class="pv-card" :class="{ pvFlipping: pvFlipping===(si-1), pvFlipped: !!pvFlipped[si-1] }">
				<view class="pv-back" v-if="!pvFlipped[si-1]">
					<view class="pv-bframe">
						<view class="cat cat--pv"><view class="ce ce-l"></view><view class="ce ce-r"></view><view class="ch"></view></view>
					</view>
				</view>
				<view class="pv-front" v-else :style="{ background: getCard(si-1).bg }">
					<view class="pf-c pf-tl"></view>
					<view class="pf-c pf-tr"></view>
					<view class="pf-c pf-bl"></view>
					<view class="pf-c pf-br"></view>
					<text class="pf-num">{{ getCard(si-1).num }}</text>
					<view class="pf-ring">
						<text class="pf-sym">{{ getCard(si-1).symbol }}</text>
					</view>
					<text class="pf-name">{{ getCard(si-1).name }}</text>
					<view class="pf-div"></view>
					<text class="pf-desc">{{ getCard(si-1).desc }}</text>
				</view>
			</view>
			<text class="pv-pos-label" :class="{ 'pv-pos--shown': !!pvFlipped[si-1] }">{{ posLabels[si-1] }}</text>
		</view>
	</view>

	<!-- ===== 操作按钮：预览完成后确认 ===== -->
	<view v-if="showActBtn" class="act-btn" :class="{ disabled: !canAct }" hover-class="act-hover" @tap="doAction">
		<text class="act-text">{{ actionLabel }}</text>
	</view>
	<view v-if="showActBtn" class="act-cancel-row" hover-class="act-cancel-hover" @tap="goBack">
		<text class="act-cancel-text">取消，不保存这次结果</text>
	</view>
</view>
		</view>
	</view>
</view>
</template>

<script>
import { getApiUserId, postTarotDraw, describeRequestError } from '@/utils/api.js'

var ARCANA = [
	{ name: '愚者',     num: '0',    symbol: '◇', desc: '自由与冒险', bg: 'linear-gradient(165deg,#eae6f2,#c5bada)' },
	{ name: '魔术师',   num: 'I',    symbol: '∞', desc: '创造与意志', bg: 'linear-gradient(165deg,#d8eaf8,#a4c4e4)' },
	{ name: '女祭司',   num: 'II',   symbol: '☽', desc: '智慧与直觉', bg: 'linear-gradient(165deg,#ddd8ee,#b0a6d4)' },
	{ name: '女皇',     num: 'III',  symbol: '♛', desc: '丰饶与滋养', bg: 'linear-gradient(165deg,#d8f2e2,#9ed8b8)' },
	{ name: '皇帝',     num: 'IV',   symbol: '♔', desc: '权威与稳定', bg: 'linear-gradient(165deg,#fce6cc,#e4b888)' },
	{ name: '教皇',     num: 'V',    symbol: '✝', desc: '信仰与传承', bg: 'linear-gradient(165deg,#e4ddd0,#c4b8a0)' },
	{ name: '恋人',     num: 'VI',   symbol: '♡', desc: '选择与连结', bg: 'linear-gradient(165deg,#fce2ea,#e8a0b8)' },
	{ name: '战车',     num: 'VII',  symbol: '⚔', desc: '胜利与决心', bg: 'linear-gradient(165deg,#d4dfe8,#9eb8d0)' },
	{ name: '力量',     num: 'VIII', symbol: '☼', desc: '力量与勇气', bg: 'linear-gradient(165deg,#f8ead4,#e2c8a0)' },
	{ name: '隐者',     num: 'IX',   symbol: '◈', desc: '内省与智慧', bg: 'linear-gradient(165deg,#dcdcdc,#b0b0b0)' },
	{ name: '命运之轮', num: 'X',    symbol: '☸', desc: '转变与机遇', bg: 'linear-gradient(165deg,#eae0f6,#c2b0e0)' },
	{ name: '正义',     num: 'XI',   symbol: '⚖', desc: '公正与平衡', bg: 'linear-gradient(165deg,#f2ead4,#d4c4a0)' },
	{ name: '倒吊人',   num: 'XII',  symbol: '♃', desc: '牺牲与领悟', bg: 'linear-gradient(165deg,#d8e2ea,#a8c0d4)' },
	{ name: '死神',     num: 'XIII', symbol: '♄', desc: '结束与新生', bg: 'linear-gradient(165deg,#e2d4d4,#b89898)' },
	{ name: '节制',     num: 'XIV',  symbol: '☯', desc: '调和与耐心', bg: 'linear-gradient(165deg,#e2ece8,#a8c8b8)' },
	{ name: '恶魔',     num: 'XV',   symbol: '♆', desc: '诱惑与束缚', bg: 'linear-gradient(165deg,#dcd4dc,#a898a8)' },
	{ name: '高塔',     num: 'XVI',  symbol: '⚡', desc: '变革与觉醒', bg: 'linear-gradient(165deg,#eadccc,#c8a888)' },
	{ name: '星星',     num: 'XVII', symbol: '✦', desc: '希望与指引', bg: 'linear-gradient(165deg,#d4e4f8,#9ec0e4)' },
	{ name: '月亮',     num: 'XVIII',symbol: '☾', desc: '幻象与梦境', bg: 'linear-gradient(165deg,#d8d8f8,#a8a8e0)' },
	{ name: '太阳',     num: 'XIX',  symbol: '☀', desc: '喜悦与成功', bg: 'linear-gradient(165deg,#fef4d2,#f0d68a)' },
	{ name: '审判',     num: 'XX',   symbol: '♅', desc: '觉醒与重生', bg: 'linear-gradient(165deg,#eae2d4,#d0c0a0)' },
	{ name: '世界',     num: 'XXI',  symbol: '◎', desc: '完成与圆满', bg: 'linear-gradient(165deg,#d4ead8,#a0c8b0)' }
]

function shuffle(arr) {
	var a = arr.slice()
	for (var i = a.length - 1; i > 0; i--) {
		var j = Math.floor(Math.random() * (i + 1))
		var t = a[i]; a[i] = a[j]; a[j] = t
	}
	return a
}

var FAN_DECK = 78
var FAN_VISIBLE = 19
var FAN_ARM = 6
/* 与 CSS 保持一致：strip-inner 左 padding=64rpx, strip-card width=88rpx + margin-right=14rpx=102rpx step */
var STRIP_PAD_RPX = 64
var STRIP_CARD_W_RPX = 88
var STRIP_STEP_RPX = 102

export default {
	name: 'TarotDrawPanel',
	props: {
		embedded: {
			type: Boolean,
			default: false
		},
		prefillTagId: {
			type: String,
			default: ''
		},
		prefillQuestion: {
			type: String,
			default: ''
		}
	},
	data: function() {
		var indices = []
		for (var k = 0; k < FAN_DECK; k++) indices.push(k)
		indices = shuffle(indices)
		var allCards = []
		for (var i = 0; i < FAN_DECK; i++) {
			allCards.push({ idx: indices[i] % 22, picked: false })
		}
		var fanArcana = []
		for (var j = 0; j < FAN_DECK; j++) {
			fanArcana.push(allCards[j].idx)
		}
		return {
			phase: 'shuffle',
			collapsed: false,
			fanScale: 1,
			fanCount: FAN_VISIBLE,
			fanDeckTotal: FAN_DECK,
			allCards: allCards,
			fanArcana: fanArcana,
			pickComplete: false,
			posLabels: ['过去', '现在', '未来'],
			tarotThemeTags: [
				{ id: 'l1', label: '恋情发展', cat: 'love' },
				{ id: 'l2', label: '爱情真相', cat: 'love' },
				{ id: 'l3', label: 'TA的真心', cat: 'love' },
				{ id: 'l4', label: '终身伴侣', cat: 'love' },
				{ id: 'w1', label: '工作运程', cat: 'work' },
				{ id: 'w2', label: '认识自我', cat: 'work' },
				{ id: 'w3', label: '事业决策', cat: 'work' },
				{ id: 'w4', label: '事业工作', cat: 'work' },
				{ id: 's1', label: '学习运程', cat: 'study' },
				{ id: 's2', label: '学习问题', cat: 'study' }
			],
			selectedTagId: '',
			customQuestion: '',
			pickedFan: {},
			selected: [],
			pvFlipped: {},
			pvFlipping: -1,
			pvDone: false,
			autoShuffleStarted: false,
			fanPickEntering: false,
			stripScrollLeft: 0,
			stripScrollTarget: 0,
			_stripMetrics: null
		}
	},
	created: function() {
		if (this.prefillTagId) this.selectedTagId = this.prefillTagId
		if (this.prefillQuestion != null && this.prefillQuestion !== '') {
			this.customQuestion = String(this.prefillQuestion)
		}
	},
	mounted: function() {
		var self = this
		if (self.autoShuffleStarted) return
		self.autoShuffleStarted = true
		self.$nextTick(function() {
			setTimeout(function() {
				if (self.phase === 'shuffle') self.startShuffle()
			}, 50)
		})
	},
	computed: {
		showActBtn: function() {
			return this.phase === 'preview' && this.pvDone
		},
		canAct: function() {
			return this.phase === 'preview' && this.pvDone
		},
		actionLabel: function() {
			if (this.phase === 'preview' && this.pvDone) return '确认抽卡'
			return ''
		},
		deckIndexList: function() {
			var n = this.fanDeckTotal
			var a = []
			for (var i = 0; i < n; i++) a.push(i)
			return a
		},
		pickProgressPercent: function() {
			return Math.round((this.selected.length / 3) * 100)
		}
	},
	methods: {
		goBack: function() {
			if (!this.embedded) {
				this.$emit('close')
				return
			}
			if (getCurrentPages().length > 1) { uni.navigateBack(); return }
			uni.reLaunch({ url: '/pages/index/index' })
		},
		stripMetrics: function() {
			if (this._stripMetrics) return this._stripMetrics
			try {
				var w = uni.getSystemInfoSync().windowWidth
				this._stripMetrics = { pr: w / 750, vw: w }
			} catch (e) {
				this._stripMetrics = { pr: 0.5, vw: 375 }
			}
			return this._stripMetrics
		},
		onStripScroll: function(e) {
			var d = e.detail || {}
			if (typeof d.scrollLeft === 'number') {
				this.stripScrollLeft = d.scrollLeft
				this.stripScrollTarget = d.scrollLeft
			}
		},
		centerStrip: function() {
			var m = this.stripMetrics()
			var pr = m.pr
			var vw = m.vw
			var mid = (this.fanDeckTotal - 1) / 2
			var target = STRIP_PAD_RPX * pr + mid * STRIP_STEP_RPX * pr + STRIP_CARD_W_RPX * pr * 0.5 - vw * 0.5
			if (target < 0) target = 0
			this.stripScrollLeft = target
			this.stripScrollTarget = target
		},
		_stripDelta: function(gi) {
			if (this.phase !== 'fanPick') return 0
			var m = this.stripMetrics()
			var pr = m.pr
			var vw = m.vw
			var padL = STRIP_PAD_RPX * pr
			var cardW = STRIP_CARD_W_RPX * pr
			var step = STRIP_STEP_RPX * pr
			var sl = this.stripScrollLeft || 0
			var cx = padL + gi * step + cardW * 0.5 - sl
			var delta = (cx - vw * 0.5) / step
			if (delta > 12) delta = 12
			if (delta < -12) delta = -12
			return delta
		},
		stripNearCenter: function(gi) {
			return this.phase === 'fanPick' && !this.pickedFan[gi] && Math.abs(this._stripDelta(gi)) < 0.36
		},
		/* 牌带：平铺排列，中心牌轻微放大 */
		getStripCardStyle: function(gi) {
			if (this.phase !== 'fanPick') {
				return { zIndex: 1 }
			}
			var absD = Math.abs(this._stripDelta(gi))
			var isCenter = absD < 0.5
			var isSub = absD < 1.5
			var sc = isCenter ? 1.06 : (isSub ? 1.02 : 1)
			var z = isCenter ? 10 : (isSub ? 6 : 1)
			return {
				zIndex: z,
				transform: 'scale(' + sc + ')',
				transformOrigin: '50% 100%',
				transition: 'transform 0.18s ease, opacity 0.16s ease'
			}
		},
		selectedTagLabel: function() {
			var id = this.selectedTagId
			if (!id) return ''
			var list = this.tarotThemeTags
			for (var i = 0; i < list.length; i++) {
				if (list[i].id === id) return list[i].label
			}
			return ''
		},
		/* 洗牌/摊开：槽位相对扇心；几何按原 13 张扇总跨度缩放 */
		getFanStyle: function(idx) {
			var n = FAN_VISIBLE
			var hw = 48
			var sc = typeof this.fanScale === 'number' ? this.fanScale : 1
			var spread = this.phase === 'revealing' ? 1.12 : 1
			if (this.collapsed) {
				return {
					left: 'calc(50% - ' + hw + 'rpx)',
					bottom: '40rpx',
					transform: 'rotate(0deg) scale(' + (0.92 * sc) + ')',
					zIndex: idx
				}
			}
			var mid = (n - 1) / 2
			var maxD = Math.max(mid, n - 1 - mid)
			var s = spread * (FAN_ARM / maxD)
			var deg = (idx - mid) * 4.8 * s
			var offX = (idx - mid) * 36 * s
			var arcY = Math.abs(idx - mid) * 4 * s
			var z = idx <= mid ? idx : n - 1 - idx
			return {
				left: 'calc(50% + ' + offX + 'rpx - ' + hw + 'rpx)',
				bottom: (50 - arcY) + 'rpx',
				transform: 'rotate(' + deg + 'deg) scale(' + sc + ')',
				zIndex: z
			}
		},

		/* ---- 洗牌动效 ---- */
		doAction: function() {
			if (!this.canAct) return
			if (this.phase === 'preview' && this.pvDone) { this.confirmDraw(); return }
		},
		startShuffle: function() {
			var self = this
			/* 与 .fan-card transition 时长对齐，避免下一拍动画未结束就切状态 */
			var beat = 560
			self.phase = 'shuffling'
			self.collapsed = true
			self.fanScale = 0.9
			self.$forceUpdate()
			setTimeout(function() {
				self.collapsed = false
				self.$forceUpdate()
				setTimeout(function() {
					self.collapsed = true
					self.$forceUpdate()
					setTimeout(function() {
						self.collapsed = false
						self.$forceUpdate()
						setTimeout(function() {
							self.collapsed = true
							self.$forceUpdate()
							setTimeout(function() {
								self.collapsed = false
								self.phase = 'revealing'
								self.fanScale = 0.98
								self.$forceUpdate()
								setTimeout(function() {
									self.fanScale = 1
									self.fanPickEntering = true
									self.phase = 'fanPick'
									self.$forceUpdate()
									self.$nextTick(function() {
										self.centerStrip()
										self.$forceUpdate()
										setTimeout(function() {
											self.fanPickEntering = false
											self.$forceUpdate()
										}, 280)
									})
								}, 180)
							}, beat - 60)

						}, beat - 40)
					}, beat - 40)
				}, beat)
			}, 380)
		},

		pickFanByGlobal: function(g) {
			if (this.phase !== 'fanPick') return
			if (this.pickedFan[g]) return
			if (this.selected.length >= 3) return
			this.$set(this.pickedFan, g, true)
			this.selected.push(this.fanArcana[g])
			this.$forceUpdate()
			if (this.selected.length === 3) {
				this.pickComplete = true
				this.$forceUpdate()
				var self = this
				setTimeout(function() {
					self.pickComplete = false
					self.startPreview()
				}, 900)
			}
		},
		getCard: function(si) {
			if (si >= this.selected.length) return {}
			return ARCANA[this.selected[si]] || {}
		},

		/* ---- 预览翻牌 ---- */
		startPreview: function() {
			this.phase = 'preview'
			this.pvFlipped = {}
			this.pvFlipping = -1
			this.pvDone = false
			this.$forceUpdate()
			var self = this
			setTimeout(function() { self.flipPv(0) }, 380)
		},
		flipPv: function(idx) {
			var self = this
			if (idx >= 3) {
				self.pvFlipping = -1
				self.pvDone = true
				self.$forceUpdate()
				return
			}
			self.pvFlipping = idx
			self.$forceUpdate()
			/* 280ms 折叠到 scaleX(0)，切换内容，再用 280ms 展开；下张牌 320ms 后开始 */
			setTimeout(function() {
				var obj = {}
				for (var k in self.pvFlipped) obj[k] = true
				obj[idx] = true
				self.pvFlipped = obj
				self.pvFlipping = -1
				self.$forceUpdate()
				setTimeout(function() { self.flipPv(idx + 1) }, 320)
			}, 280)
		},

		/* ---- 确认 ---- */
		confirmDraw: function() {
			var result = []
			for (var i = 0; i < 3; i++) {
				var idx = this.selected[i]
				var card = ARCANA[idx]
				result.push({
					idx: idx,
					name: card.name,
					num: card.num,
					symbol: card.symbol,
					desc: card.desc,
					bg: card.bg
				})
			}
			var intent = {
				tagId: this.selectedTagId,
				tagLabel: this.selectedTagLabel(),
				question: (this.customQuestion || '').trim()
			}
			uni.setStorageSync('tarotResult', JSON.stringify(result))
			uni.setStorageSync('tarotIntent', JSON.stringify(intent))

			var self = this
			var uid = getApiUserId()
			if (uid) {
				postTarotDraw({
					user_id: uid,
					theme_tag_id: intent.tagId || null,
					theme_tag_label: intent.tagLabel || null,
					question_text: intent.question || '',
					cards: result
				}).then(function(res) {
					var drawId = res && res.data && res.data.id
					if (drawId) {
						try { uni.setStorageSync('tarotDrawId', drawId) } catch (e) {}
					}
				}).catch(function(err) {
					console.warn('[tarot] 保存到服务器失败（本地已存）', describeRequestError(err))
				})
			}

			if (!self.embedded) {
				self.$emit('close')
				return
			}
			uni.navigateBack()
		}
	}
}
</script>

<style scoped>
/* —— 全屏浮窗（非 embedded） —— */
.tdm-modal-root {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	z-index: 2000;
}
.tdm-sheet {
	position: relative;
	width: 100%;
	background:
		radial-gradient(ellipse 140% 70% at 50% -8%, rgba(160,130,220,0.22) 0%, transparent 52%),
		radial-gradient(ellipse 80% 50% at 100% 30%, rgba(100,80,160,0.08) 0%, transparent 45%),
		linear-gradient(175deg, #2d2648 0%, #221c3a 18%, #1a1530 52%, #17122c 100%);
	border: none;
	display: flex;
	flex-direction: column;
	overflow: hidden;
}
.tdm-sheet--fullscreen {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	min-height: 100%;
	height: 100%;
	padding-top: constant(safe-area-inset-top);
	padding-top: env(safe-area-inset-top);
	padding-bottom: constant(safe-area-inset-bottom);
	padding-bottom: env(safe-area-inset-bottom);
	box-sizing: border-box;
	animation: tdmFullIn 0.32s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
}
@keyframes tdmFullIn {
	from {
		opacity: 0;
	}
	to {
		opacity: 1;
	}
}
.tdm-sheet-shine {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 200rpx;
	pointer-events: none;
	background: radial-gradient(ellipse 90% 100% at 50% 0%, rgba(255,255,255,0.06) 0%, transparent 70%);
	z-index: 1;
}
.tdm-topbar {
	flex-shrink: 0;
	padding: 16rpx 32rpx 28rpx;
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: center;
	position: relative;
	z-index: 2;
}
.tdm-sheet-title {
	font-size: 30rpx;
	font-weight: 700;
	color: rgba(230,218,255,0.88);
	letter-spacing: 16rpx;
	text-indent: 16rpx;
}
.tdm-sheet-body {
	flex: 1;
	min-height: 0;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	position: relative;
	z-index: 2;
}
.tdm-embedded-wrap {
	width: 100%;
	min-height: 100%;
}
.tdm-embedded-inner {
	width: 100%;
	min-height: 100vh;
}
.tdm-embedded-body {
	min-height: 100vh;
}

.page-root {
	position: fixed;
	top: 0; left: 0; right: 0; bottom: 0;
	background: #1e1832;
	display: flex;
	flex-direction: column;
	align-items: center;
	overflow: hidden;
}
.page-root--in-sheet {
	position: relative;
	top: auto;
	left: auto;
	right: auto;
	bottom: auto;
	width: 100%;
	flex: 1;
	min-height: 0;
	max-height: 100%;
	overflow: hidden;
	background: transparent;
}
.page-root--in-sheet.page-fan-pick {
	touch-action: pan-x;
	overflow-y: auto;
	overflow-x: hidden;
	-webkit-overflow-scrolling: touch;
}
.page-root--in-sheet .nav-back {
	top: 8rpx;
	left: 24rpx;
	width: 64rpx;
	height: 64rpx;
	background: rgba(255,255,255,0.07);
	box-shadow: none;
}
.page-root--in-sheet .hint {
	margin-top: 88rpx;
}
.page-root--in-sheet .hint--preview {
	margin-top: 40rpx;
}
.page-root--in-sheet .ambient {
	opacity: 1;
	background: radial-gradient(ellipse, rgba(140,110,200,0.12) 0%, transparent 68%);
}
.page-root.page-fan-pick {
	touch-action: pan-x;
	overflow-y: auto;
	overflow-x: hidden;
	-webkit-overflow-scrolling: touch;
}
/* 选牌阶段：比洗牌/揭晓更「亮」的雾紫层，形成阶段感 */
.page-root.page-root--pick-ui {
	background:
		radial-gradient(ellipse 105% 52% at 50% 8%, rgba(166, 144, 224, 0.10) 0%, transparent 52%),
		linear-gradient(180deg, #271f3d 0%, #1d1831 52%, #171227 100%);
}
.page-root--in-sheet.page-root--pick-ui {
	background:
		radial-gradient(ellipse 100% 44% at 50% 0%, rgba(170, 150, 230, 0.08) 0%, transparent 42%),
		linear-gradient(180deg, rgba(39, 31, 61, 0.9) 0%, rgba(25, 20, 43, 0.97) 58%, rgba(20, 16, 33, 1) 100%);
}
.page-root.page-root--pick-ui .ambient {
	background: radial-gradient(ellipse, rgba(150, 130, 210, 0.12) 0%, transparent 72%);
	height: 500rpx;
	top: -15%;
}
/* 揭晓阶段：略偏暖的聚光，与选牌区的冷雾区分 */
.page-root.page-root--reveal-ui {
	background:
		radial-gradient(ellipse 90% 50% at 50% 18%, rgba(190, 165, 230, 0.12) 0%, transparent 50%),
		linear-gradient(180deg, #261f3a 0%, #1c1830 55%, #16122a 100%);
}
.page-root--in-sheet.page-root--reveal-ui {
	background:
		radial-gradient(ellipse 100% 45% at 50% 0%, rgba(200, 175, 245, 0.1) 0%, transparent 45%),
		linear-gradient(175deg, rgba(40, 34, 62, 0.5) 0%, rgba(22, 18, 36, 0.98) 100%);
}
.page-root.page-root--reveal-ui .ambient {
	background: radial-gradient(ellipse, rgba(180, 150, 220, 0.14) 0%, transparent 70%);
}
.ambient {
	position: absolute;
	top: -15%; left: 50%;
	transform: translateX(-50%);
	width: 140%; height: 500rpx;
	border-radius: 50%;
	background: radial-gradient(ellipse, rgba(120,100,180,0.15) 0%, transparent 70%);
	pointer-events: none;
}
.nav-back {
	position: absolute;
	top: 88rpx; left: 28rpx; z-index: 30;
	width: 68rpx; height: 68rpx;
	display: flex; align-items: center; justify-content: center;
	border-radius: 50%;
	background: rgba(255,255,255,0.06);
}
.back-icon { font-size: 42rpx; color: rgba(255,255,255,0.6); }
.hint {
	margin-top: 128rpx;
	font-size: 34rpx; font-weight: 600;
	color: rgba(255,255,255,0.88);
	letter-spacing: 4rpx; text-align: center;
}
.hint--sub {
	margin-top: 16rpx;
	font-size: 22rpx; font-weight: 400;
	color: rgba(200,188,240,0.52);
	letter-spacing: 2rpx;
}
.hint--glow {
	color: rgba(230,220,255,0.96);
	text-shadow: 0 0 28rpx rgba(180,150,255,0.38);
}

/* ======== 扇形牌 ======== */
.fan-area {
	position: relative;
	width: 100%; height: 400rpx;
	margin-top: 24rpx;
}
.fan-pan-inner {
	position: relative;
	width: 100%;
	height: 100%;
	min-height: 400rpx;
}
.strip-scroll {
	width: 100%;
	height: 240rpx;
	white-space: nowrap;
}
.strip-inner {
	display: inline-flex;
	flex-direction: row;
	align-items: flex-end;
	height: 200rpx;
	padding: 16rpx 64rpx 16rpx;
	box-sizing: border-box;
	position: relative;
	gap: 0;
}
.strip-stage--arc {
	perspective: none;
}
.strip-card {
	flex-shrink: 0;
	width: 88rpx;
	height: 132rpx;
	margin-right: 14rpx;
	position: relative;
	transform-style: flat;
	backface-visibility: hidden;
}
.strip-card:last-child {
	margin-right: 0;
}
.strip-card.stripPicked {
	opacity: 0.22;
	pointer-events: none;
	filter: brightness(0.8);
}
.strip-card--focus .fc-face.fc-face-strip {
	background: linear-gradient(168deg, #5c4f8e 0%, #483d78 48%, #3e3468 100%);
	box-shadow:
		0 8rpx 20rpx rgba(0,0,0,0.28),
		inset 0 1rpx 0 rgba(255,255,255,0.14);
	border: 1rpx solid rgba(210,200,255,0.28);
}
.strip-card--focus .fc-face.fc-face-strip .fc-frame {
	border-color: rgba(220,210,255,0.16);
}
.strip-card--focus .fc-face.fc-face-strip .ch {
	background: rgba(220,210,255,0.14);
}
.strip-card--focus .fc-face.fc-face-strip .ce {
	border-bottom-color: rgba(220,210,255,0.14);
}
.strip-card .fc-face,
.strip-card .fc-frame,
.strip-card .cat,
.strip-card .ce,
.strip-card .ch {
	pointer-events: none;
}
/* ======== 选牌阶段 ======== */
.pick-stack {
	width: 100%;
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	align-items: stretch;
	box-sizing: border-box;
	padding: 88rpx 32rpx 36rpx;
	position: relative;
	opacity: 1;
	transform: translateY(0) scale(1);
	transition: opacity 0.26s ease-out, transform 0.36s cubic-bezier(0.2, 0.82, 0.2, 1);
	will-change: opacity, transform;
}
.pick-stack--entering {
	opacity: 0;
	transform: translateY(34rpx) scale(0.972);
}
.page-root--in-sheet .pick-stack {
	padding-top: 60rpx;
	padding-bottom: calc(36rpx + env(safe-area-inset-bottom));
}
.page-root--in-sheet.page-root--pick-ui .nav-back {
	top: 4rpx;
}
.pick-header {
	padding: 0 0 24rpx;
	box-sizing: border-box;
}
.pick-stack--entering .pick-header {
	opacity: 0.86;
	transform: translateY(10rpx);
}
.pick-head-row {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: space-between;
	gap: 20rpx;
	margin-bottom: 18rpx;
}
.pick-title-one {
	flex: 1;
	font-size: 32rpx;
	font-weight: 700;
	color: rgba(255,255,255,0.92);
	line-height: 1.34;
	letter-spacing: 1rpx;
}
.pick-head-count {
	flex-shrink: 0;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	min-width: 88rpx;
	height: 56rpx;
	padding: 0 16rpx;
	border-radius: 999rpx;
	background: rgba(130,118,186,0.18);
	border: 1rpx solid rgba(210,195,255,0.16);
	box-shadow: inset 0 1rpx 0 rgba(255,255,255,0.08);
	font-size: 26rpx;
	font-weight: 700;
	color: rgba(240,234,255,0.90);
	letter-spacing: 1rpx;
	transition: background 0.3s, border-color 0.3s, transform 0.25s ease;
}
.pick-count--done {
	background: rgba(160,130,240,0.32);
	border-color: rgba(210,190,255,0.38);
	transform: scale(1.04);
}
.pick-progress-track {
	height: 6rpx;
	border-radius: 999rpx;
	background: rgba(255,255,255,0.07);
	overflow: hidden;
}
.pick-progress-track--soft {
	height: 6rpx;
	background: rgba(255,255,255,0.07);
	box-shadow: inset 0 1rpx 0 rgba(255,255,255,0.04);
}
.pick-progress-fill {
	height: 100%;
	border-radius: 999rpx;
	background: linear-gradient(90deg, rgba(130,105,196,0.9), rgba(190,158,228,0.95));
	transition: width 0.45s cubic-bezier(0.32, 0.72, 0, 1);
}
.strip-stage {
	position: relative;
	margin: 0 -32rpx;
	border-radius: 0;
	overflow: hidden;
	background: transparent;
	box-shadow: none;
}
.strip-stage::before {
	display: none;
}
.strip-stage::after {
	display: none;
}
.strip-stage.strip-stage--arc {
	overflow: hidden;
}
.strip-edge {
	position: absolute;
	top: 0;
	bottom: 0;
	width: 80rpx;
	z-index: 4;
	pointer-events: none;
}
.strip-edge-left {
	left: 0;
	background: linear-gradient(90deg, rgba(22,18,40,0.88) 0%, rgba(22,18,40,0.32) 48%, transparent 100%);
}
.strip-edge-right {
	right: 0;
	background: linear-gradient(270deg, rgba(22,18,40,0.88) 0%, rgba(22,18,40,0.32) 48%, transparent 100%);
}
.strip-card .fc-frame {
	border: 1rpx solid rgba(210,200,255,0.12);
	opacity: 1;
}
.cat--strip {
	width: 30rpx;
	height: 30rpx;
}
.cat--strip .ce {
	border-left-width: 8rpx;
	border-right-width: 8rpx;
	border-bottom-width: 11rpx;
}
.cat--slot {
	width: 36rpx;
	height: 36rpx;
}
.cat--slot .ce {
	border-left-width: 9rpx;
	border-right-width: 9rpx;
	border-bottom-width: 13rpx;
}
.cat--pv {
	width: 44rpx;
	height: 44rpx;
}
.cat--pv .ce {
	border-left-width: 11rpx;
	border-right-width: 11rpx;
	border-bottom-width: 15rpx;
}
/* 触摸落在整张牌区域，便于冒泡到 .fan-area（小程序上子节点常抢事件） */
.fan-card .fc-face,
.fan-card .fc-frame,
.fan-card .cat,
.fan-card .ce,
.fan-card .ch {
	pointer-events: none;
}
.fan-scroll-hint {
	position: absolute;
	left: 0; right: 0; bottom: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 80;
	pointer-events: none;
}
.fan-card {
	position: absolute;
	width: 100rpx; height: 146rpx;
	transform-origin: 50% 120%;
	transition: transform 0.62s cubic-bezier(0.32, 0.72, 0, 1),
	            left 0.62s cubic-bezier(0.32, 0.72, 0, 1),
	            bottom 0.62s cubic-bezier(0.32, 0.72, 0, 1),
	            width 0.62s cubic-bezier(0.32, 0.72, 0, 1),
	            height 0.62s cubic-bezier(0.32, 0.72, 0, 1);
}
.fan-card.fanCardLong {
	width: 108rpx;
	height: 158rpx;
}
.fan-card.fanPicked {
	opacity: 0.38;
	pointer-events: none;
	filter: brightness(0.75);
}
.fc-face {
	width: 100%; height: 100%;
	background: linear-gradient(170deg, #3d3560, #2a2450);
	border-radius: 10rpx;
	border: 1.5rpx solid rgba(140,120,200,0.3);
	box-shadow: 0 4rpx 18rpx rgba(0,0,0,0.5);
	display: flex; align-items: center; justify-content: center;
}
.fc-face.fc-face-strip {
	border: 1rpx solid rgba(194,176,255,0.16);
	border-radius: 14rpx;
	background: linear-gradient(168deg, #453a72 0%, #392f60 48%, #2e2650 100%);
	box-shadow:
		0 6rpx 16rpx rgba(0,0,0,0.22),
		inset 0 1rpx 0 rgba(255,255,255,0.08);
	transition: box-shadow 0.18s ease, transform 0.18s ease;
}
.fc-frame {
	width: 78%; height: 80%;
	border: 1rpx solid rgba(224,216,255,0.12);
	border-radius: 8rpx;
	display: flex; align-items: center; justify-content: center;
}

/* 通用猫头 */
.cat, .cat-lg { position: relative; }
.cat { width: 36rpx; height: 36rpx; }
.cat-lg { width: 48rpx; height: 48rpx; }
.ch {
	width: 100%; height: 78%;
	background: rgba(200,188,240,0.18);
	border-radius: 50% 50% 42% 42%;
	position: absolute; bottom: 0; left: 0;
}
.ce {
	position: absolute; top: 0;
	width: 0; height: 0;
	border-left: 9rpx solid transparent;
	border-right: 9rpx solid transparent;
	border-bottom: 13rpx solid rgba(200,188,240,0.18);
}
.cat-lg .ce { border-left-width: 12rpx; border-right-width: 12rpx; border-bottom-width: 16rpx; }
.ce-l { left: 1rpx; }
.ce-r { right: 1rpx; }

/* ======== 水平滑动 ======== */
.scroll-wrap {
	width: 100%;
	margin-top: 24rpx;
}
.card-scroll {
	width: 100%; height: 300rpx;
	white-space: nowrap;
}
.card-track {
	display: inline-flex;
	align-items: flex-end;
	height: 300rpx;
	padding-bottom: 20rpx;
}
.pad-l, .pad-r { width: 48rpx; height: 10rpx; flex-shrink: 0; }
.s-card {
	position: relative;
	width: 106rpx; height: 154rpx;
	flex-shrink: 0;
	margin-left: -42rpx;
	transition: opacity 0.35s, transform 0.35s;
}
.s-card.picked {
	opacity: 0;
	transform: scale(0.5) translateY(-50rpx);
	pointer-events: none;
}
.s-face {
	width: 100%; height: 100%;
	background: linear-gradient(170deg, #3d3560, #2a2450);
	border-radius: 10rpx;
	border: 1.5rpx solid rgba(140,120,200,0.3);
	box-shadow: 0 4rpx 18rpx rgba(0,0,0,0.45);
	display: flex; align-items: center; justify-content: center;
}
.s-frame {
	width: 76%; height: 80%;
	border: 1rpx solid rgba(150,150,180,0.18);
	border-radius: 5rpx;
	display: flex; align-items: center; justify-content: center;
}
.s-frame .cat { width: 32rpx; height: 32rpx; }

/* ======== 卡槽：与牌带分区，含三格落位标题 ======== */
.slots-area {
	width: 100%;
	margin-top: 0;
	padding: 0;
	background: transparent;
}
.slots-row {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: flex-end;
	flex-wrap: nowrap;
	width: 100%;
	padding: 0;
	gap: 10rpx;
	box-sizing: border-box;
}
.slot-box {
	width: 122rpx;
	flex: 1;
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	align-items: center;
	margin: 0;
	max-width: 200rpx;
}
.slot-caption {
	font-size: 18rpx;
	font-weight: 500;
	color: rgba(200,188,240,0.42);
	letter-spacing: 3rpx;
	margin-top: 10rpx;
}
.slots-row--pick {
	padding: 24rpx 0 0;
	justify-content: center;
	gap: 20rpx;
}
.slot-empty {
	width: 122rpx;
	height: 198rpx;
	box-sizing: border-box;
	border-radius: 18rpx;
	border: 1rpx dashed rgba(255,255,255,0.12);
	background: transparent;
	display: flex;
	align-items: center;
	justify-content: center;
}
.slot-n {
	font-size: 32rpx;
	color: rgba(255,255,255,0.14);
	font-weight: 600;
}
.slot-card {
	width: 122rpx;
	height: 198rpx;
	border-radius: 18rpx;
	overflow: hidden;
	box-sizing: border-box;
	animation: slotPop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes slotPop {
	0% { transform: scale(0.15) translateY(-40rpx); opacity: 0; }
	100% { transform: scale(1) translateY(0); opacity: 1; }
}
.slot-back {
	width: 100%; height: 100%;
	background: linear-gradient(168deg, #453a72, #2e2748);
	border: none;
	border-radius: 18rpx;
	box-shadow: 0 6rpx 22rpx rgba(0,0,0,0.28);
	display: flex; align-items: center; justify-content: center;
}
.slot-bframe {
	width: 76%;
	height: 82%;
	border: none;
	border-radius: 8rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0.92;
}
.slots-area {
	margin-top: 0;
	padding: 8rpx 0 0;
	border-radius: 0;
	background: transparent;
	box-shadow: none;
}
.slots-row {
	gap: 12rpx;
}
.slot-box {
	width: auto;
	min-width: 0;
}
.slot-empty,
.slot-card {
	width: 120rpx;
	height: 180rpx;
	border-radius: 18rpx;
}
.slot-empty {
	border: 1.5rpx dashed rgba(180,162,240,0.20);
	background: rgba(255,255,255,0.02);
	box-shadow: inset 0 1rpx 0 rgba(255,255,255,0.03);
}
.slot-n {
	font-size: 26rpx;
	letter-spacing: 2rpx;
	color: rgba(255,255,255,0.16);
}
.slot-card {
	animation: slotPop 0.34s cubic-bezier(0.2, 0.84, 0.28, 1.2);
}
@keyframes slotPop {
	0% { transform: translateY(18rpx) scale(0.82); opacity: 0; }
	100% { transform: translateY(0) scale(1); opacity: 1; }
}
.slot-back {
	border: 1rpx solid rgba(194,176,255,0.10);
	border-radius: 18rpx;
	box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.14), inset 0 1rpx 0 rgba(255,255,255,0.06);
}
.slot-bframe {
	border: 1rpx solid rgba(199,184,255,0.1);
	border-radius: 10rpx;
}

/* ======== 选满3张反馈层 ======== */
.pick-complete-mask {
	position: absolute;
	top: 0; left: 0; right: 0; bottom: 0;
	z-index: 50;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(20,16,42,0.52);
	backdrop-filter: blur(8px);
	animation: maskIn 0.3s ease-out;
}
@keyframes maskIn {
	from { opacity: 0; }
	to { opacity: 1; }
}
.pick-complete-text {
	font-size: 34rpx;
	font-weight: 600;
	color: rgba(240,230,255,0.96);
	letter-spacing: 4rpx;
	text-shadow: 0 0 32rpx rgba(180,150,255,0.48);
}

/* ======== 预览放大 ======== */
.hint--preview {
	margin-top: 56rpx;
	font-size: 28rpx;
	font-weight: 500;
	letter-spacing: 6rpx;
}
.pv-row {
	display: flex; justify-content: center;
	width: 100%; padding: 0 24rpx;
	margin-top: 24rpx;
	gap: 14rpx;
	box-sizing: border-box;
}
.pv-col {
	display: flex;
	flex-direction: column;
	align-items: center;
	flex: 1;
	min-width: 0;
}
.pv-pos-label {
	margin-top: 12rpx;
	font-size: 20rpx;
	color: rgba(200,188,240,0.0);
	letter-spacing: 3rpx;
	font-weight: 500;
	transition: color 0.38s ease;
}
.pv-pos--shown {
	color: rgba(200,188,240,0.56);
}
/* 牌宽=(750-48-28)/3≈224rpx，高=224×1.5≈336rpx，保持 2:3 塔罗比例 */
.pv-card {
	width: 100%;
	aspect-ratio: 2 / 3;
	height: 336rpx;
	border-radius: 16rpx;
	overflow: hidden;
	transition: transform 0.28s cubic-bezier(0.4, 0, 0.6, 1);
}
.pv-card.pvFlipping { transform: scaleX(0); }
.pv-back {
	width: 100%; height: 100%;
	background: linear-gradient(168deg, #453a72 0%, #392f60 48%, #2e2650 100%);
	border: 1rpx solid rgba(194,176,255,0.16);
	border-radius: 16rpx;
	display: flex; align-items: center; justify-content: center;
	box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.32),
	            inset 0 1rpx 0 rgba(255,255,255,0.08);
}
.pv-bframe {
	width: 76%; height: 82%;
	border: 1rpx solid rgba(199,184,255,0.14);
	border-radius: 10rpx;
	display: flex; align-items: center; justify-content: center;
}

/* 预览正面 */
.pv-front {
	width: 100%; height: 100%;
	border-radius: 16rpx;
	position: relative;
	display: flex; flex-direction: column;
	align-items: center; justify-content: center;
	padding: 18rpx 12rpx;
	box-sizing: border-box;
}
.pf-c { position: absolute; width: 20rpx; height: 20rpx; }
.pf-tl { top: 14rpx; left: 14rpx; border-top: 1.5rpx solid rgba(0,0,0,0.12); border-left: 1.5rpx solid rgba(0,0,0,0.12); }
.pf-tr { top: 14rpx; right: 14rpx; border-top: 1.5rpx solid rgba(0,0,0,0.12); border-right: 1.5rpx solid rgba(0,0,0,0.12); }
.pf-bl { bottom: 14rpx; left: 14rpx; border-bottom: 1.5rpx solid rgba(0,0,0,0.12); border-left: 1.5rpx solid rgba(0,0,0,0.12); }
.pf-br { bottom: 14rpx; right: 14rpx; border-bottom: 1.5rpx solid rgba(0,0,0,0.12); border-right: 1.5rpx solid rgba(0,0,0,0.12); }
.pf-num {
	position: absolute; top: 16rpx; left: 18rpx;
	font-size: 18rpx; font-weight: 700;
	color: rgba(0,0,0,0.2); font-style: italic;
}
.pf-ring {
	width: 72rpx; height: 72rpx;
	border-radius: 50%;
	background: rgba(255,255,255,0.42);
	display: flex; align-items: center; justify-content: center;
	margin-bottom: 12rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.08);
}
.pf-sym { font-size: 36rpx; color: rgba(0,0,0,0.22); }
.pf-name {
	font-size: 26rpx; font-weight: 800;
	color: rgba(30,30,50,0.88); letter-spacing: 3rpx;
}
.pf-div {
	width: 40rpx; height: 1.5rpx;
	background: rgba(0,0,0,0.10);
	margin: 8rpx 0; border-radius: 2rpx;
}
.pf-desc {
	font-size: 18rpx; color: rgba(50,50,70,0.52); letter-spacing: 1.5rpx;
	text-align: center;
}

/* ======== 按钮 ======== */
.act-btn {
	margin-top: 36rpx;
	width: 380rpx; height: 90rpx;
	background: linear-gradient(148deg, #9a8fcb 0%, #8276ba 52%, #7264af 100%);
	border-radius: 999rpx;
	display: flex; align-items: center; justify-content: center;
	box-shadow: 0 10rpx 32rpx rgba(100,88,170,0.42),
	            inset 0 1rpx 0 rgba(255,255,255,0.16);
	border: 1rpx solid rgba(220,210,255,0.20);
}
.act-btn.disabled {
	background: rgba(255,255,255,0.08);
	box-shadow: none;
	border-color: transparent;
}
.act-hover { opacity: 0.88; transform: scale(0.98); }
.act-text {
	font-size: 28rpx; font-weight: 700;
	color: rgba(255,255,255,0.96); letter-spacing: 5rpx;
}
.act-btn.disabled .act-text { color: rgba(255,255,255,0.18); }
.act-cancel-row {
	margin-top: 22rpx;
	padding: 10rpx 24rpx;
}
.act-cancel-hover { opacity: 0.6; }
.act-cancel-text {
	font-size: 22rpx;
	color: rgba(200,188,240,0.38);
	font-weight: 400;
	letter-spacing: 1rpx;
}
</style>
