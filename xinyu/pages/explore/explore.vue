<template>
<view class="page">

	<!-- 星空背景 -->
	<view class="star-layer">
		<view v-for="(s,i) in stars" :key="i" class="star" :style="s"></view>
	</view>
	<view class="orb orb-a"></view>
	<view class="orb orb-b"></view>

	<!-- 顶部 -->
	<view class="hdr">
		<view class="logo-col">
			<text class="logo">灵　境</text>
			<text class="logo-en">SOUL CONSTELLATION</text>
		</view>
		<view class="hdr-pill">
			<view class="hdr-dot"></view>
			<text class="hdr-frac">{{ litCount }} / {{ nodeCount }}</text>
		</view>
	</view>

	<!-- 状态卡 -->
	<view class="status-card">
		<view class="sc-left">
			<text class="sc-title">探索灵魂之境</text>
			<view class="sc-bar-wrap">
				<view class="sc-bar" :style="barStyle"></view>
			</view>
			<text class="sc-sub">点亮每颗星辰，绘制属于你的专属星图</text>
		</view>
		<view class="sc-right">
			<text class="sc-num">{{ litCount }}</text>
			<text class="sc-label">OF EIGHT</text>
		</view>
	</view>

	<!-- 星图滚动区 -->
	<scroll-view scroll-y class="map-scroll" :scroll-top="scrollTop" :scroll-with-animation="true">
		<view class="map-canvas">
			<!-- 连线 -->
			<view v-for="(ln,i) in lineData" :key="'l-'+i"
				class="conn-line" :class="{ 'line-lit': ln.lit }"
				:style="ln.style"></view>

			<!-- 节点 -->
		<view v-for="(nd,i) in nodes" :key="'n-'+i"
			class="node" :class="nd.cls"
			:style="nd.posStyle"
			@tap="openModal(i)">
			<!-- 光晕 -->
			<view class="aura" v-if="nd.lit || !nd.isFinal" :style="nd.auraSty"></view>
			<!-- 菱形 -->
			<view class="diamond" :class="nd.diamondCls">
				<view class="diamond-inner" :style="nd.diamondInnerSty"></view>
				<text class="node-icon">{{ nd.icon }}</text>
			</view>
			<!-- 文字 -->
			<view class="node-text">
				<text class="node-title" :style="nd.titleSty">{{ nd.displayName }}</text>
				<view class="title-line" :style="nd.lineSty"></view>
				<text class="node-tag" :style="nd.tagSty">{{ nd.en }}</text>
			</view>
			</view>
		</view>
	</scroll-view>

	<!-- 底部 Modal -->
	<view class="modal-bg" v-if="showModal" @tap="closeModal">
		<view class="modal-sheet" :class="{ open: modalReady }" @tap.stop>
			<view class="m-handle"></view>
			<view class="m-glow"></view>
			<text class="m-icon-big">{{ curNode.icon }}</text>
			<text class="m-title">{{ curNode.name }}</text>
			<text class="m-en">{{ curNode.en }}</text>
			<view class="m-rule"></view>
			<text class="m-quote">{{ curNode.quote }}</text>
			<text class="m-desc">{{ curNode.desc }}</text>
			<view class="m-btn" :class="btnClass" hover-class="m-btn-hover" @tap="onAction">
				<text class="m-btn-text">{{ btnLabel }}</text>
			</view>
			<text class="m-skip" @tap="closeModal">返回星图</text>
		</view>
	</view>

	<custom-tabbar :list="navList" />
</view>
</template>

<script>
import customTabbar from '@/components/custom-tabbar/custom-tabbar.vue'

var NODES = [
	{ id:0, name:'星盘解析', en:'Astro Chart',     icon:'🔮', color:'#3ec9c1', glow:'rgba(62,201,193,0.4)',  lit:true,  x:50, y:180, quote:'宇宙在你降生时，拍下了一张快照。', desc:'日月星辰的落位，是解读你性格底色的密码。' },
	{ id:1, name:'人格解码', en:'MBTI Matrix',     icon:'🧠', color:'#3ec9c1', glow:'rgba(62,201,193,0.4)',  lit:true,  x:26, y:360, quote:'你感知世界的方式，构成了世界的样貌。', desc:'16型人格维度，找到真实的自我坐标。' },
	{ id:2, name:'九型人格', en:'Enneagram',       icon:'💎', color:'#9d72ff', glow:'rgba(157,114,255,0.4)', lit:false, x:74, y:360, quote:'九种核心动机，驱动你一切行为的选择。', desc:'深入发现你的核心驱动力与深层恐惧。' },
	{ id:3, name:'亲密关系', en:'Intimacy',         icon:'🪢', color:'#d4607a', glow:'rgba(212,96,122,0.35)', lit:false, x:22, y:560, quote:'爱是一场映射，照见最初的恐惧与渴望。', desc:'剖析你在亲密关系中的模式与内在需求。' },
	{ id:4, name:'心理健康', en:'Mental Health',    icon:'🪷', color:'#9d72ff', glow:'rgba(157,114,255,0.4)', lit:false, x:58, y:540, quote:'不要畏惧深渊，那是光照不进的真实。', desc:'一次温和而深刻的心理健康自我觉察。' },
	{ id:5, name:'抑郁评估', en:'Depression Risk',  icon:'🌘', color:'#d4607a', glow:'rgba(212,96,122,0.35)', lit:false, x:80, y:720, quote:'倾听内心深处的回响，温柔面对每一处暗影。', desc:'科学评估抑郁风险等级，为你提供守护建议。' },
	{ id:6, name:'职业发展', en:'Career Path',      icon:'🧭', color:'#dda03f', glow:'rgba(221,160,63,0.4)',  lit:false, x:38, y:760, quote:'天赋不是学会的技能，而是本能的喜悦。', desc:'辨清核心才干，定位你在世间最耀眼的坐标。' },
	{ id:7, name:'本我觉醒', en:'The Awakening',    icon:'✨', color:'#dda03f', glow:'rgba(221,160,63,0.4)',  lit:false, x:50, y:950, quote:'万物皆有裂痕，那是光照进来的地方。', desc:'点亮所有前置星辰后方可开启。', isFinal:true }
]

var EDGES = [[0,1],[0,2],[1,3],[1,4],[2,4],[2,5],[3,6],[4,5],[4,6],[5,7],[6,7]]
var MAP_H = 1300, MAP_RPX = 2500

function scaleY(y) { return Math.round(y / MAP_H * MAP_RPX) }

function enrichNode(n) {
	var nd = Object.assign({}, n, { yr: scaleY(n.y) })
	if (nd.isFinal && !nd.lit) nd.cls = 'node-final'
	else if (nd.lit) nd.cls = 'node-lit'
	else nd.cls = 'node-dim'
	nd.posStyle = { left: nd.x + '%', top: nd.yr + 'rpx' }
	var bg = nd.lit ? 'radial-gradient(circle,' + nd.glow + ',transparent 65%)' : 'radial-gradient(circle,rgba(150,133,238,0.22),transparent 65%)'
	nd.auraSty = { background: bg }
	nd.diamondCls = nd.isFinal ? ['diamond-circle'] : []
	nd.diamondInnerSty = nd.lit ? { borderColor: nd.color, boxShadow: '0 0 28rpx ' + nd.glow } : {}
	nd.titleSty = nd.lit ? {} : { color: 'rgba(115,108,148,0.40)' }
	nd.lineSty = { background: nd.lit ? nd.color : 'rgba(150,133,238,0.25)' }
	nd.tagSty = { color: nd.lit ? nd.color : 'rgba(150,133,238,0.32)' }
	if (nd.lit) nd.displayName = nd.name
	else if (nd.isFinal) nd.displayName = '— 终极 —'
	else nd.displayName = '待点亮'
	return nd
}

export default {
	components: { customTabbar },
	data: function() {
		var nodes = []
		for (var i = 0; i < NODES.length; i++) {
			nodes.push(enrichNode(NODES[i]))
		}
		return {
			nodes: nodes,
			lineData: [],
			showModal: false,
			modalReady: false,
			curIdx: -1,
			scrollTop: 0,
			stars: this.makeStars(),
			navList: [
				{ label: '首页', active: false, path: '/pages/index/index' },
				{ label: '探索', active: true, path: '/pages/explore/explore' },
				{ label: '影子', active: false, path: '/pages/shadow/shadow' },
				{ label: '我的', active: false, path: '/pages/profile/profile' }
			]
		}
	},
	computed: {
		litCount: function() {
			var c = 0; for (var i = 0; i < this.nodes.length; i++) { if (this.nodes[i].lit) c++ } return c
		},
		progress: function() { return Math.round(this.litCount / this.nodes.length * 100) },
		allLit: function() {
			for (var i = 0; i < this.nodes.length; i++) { if (!this.nodes[i].isFinal && !this.nodes[i].lit) return false } return true
		},
		curNode: function() { return this.curIdx >= 0 ? this.nodes[this.curIdx] : {} },
		btnClass: function() {
			var cls = []
			if (this.curNode.lit) cls.push('m-btn-lit')
			if (this.curNode.isFinal && !this.allLit && !this.curNode.lit) cls.push('m-btn-lock')
			return cls
		},
		barStyle: function() {
			return { width: this.progress + '%' }
		},
		nodeCount: function() { return this.nodes.length },
		btnLabel: function() {
			if (!this.curNode.name) return ''
			if (this.curNode.id === 0) return '开始星盘解析 ✦'
			if (this.curNode.id === 1) return '开始MBTI测试 ✦'
			if (this.curNode.id === 2) return '开始人格测试 ✦'
			if (this.curNode.id === 3) return '开始亲密关系测试 ✦'
			if (this.curNode.id === 4) return '开始心理自测 ✦'
			if (this.curNode.id === 5) return '开始抑郁评估 ✦'
			if (this.curNode.id === 6) return '开始职业测试 ✦'
			if (this.curNode.lit) return '查看灵魂报告 ✦'
			if (this.curNode.isFinal && !this.allLit) return '锁定中 (需点亮前置星辰)'
			return '点亮此星辰 ✦'
		}
	},
	mounted: function() {
		var self = this
		setTimeout(function() { self.computeLines() }, 400)
		setTimeout(function() { self.scrollTop = 60 }, 800)
	},
	methods: {
		makeStars: function() {
			var arr = []
			for (var i = 0; i < 70; i++) {
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
		},
		computeLines: function() {
			var self = this
			uni.createSelectorQuery().in(this).select('.map-canvas').boundingClientRect().exec(function(res) {
				if (!res || !res[0] || res[0].width < 10) {
					setTimeout(function() { self.computeLines() }, 500); return
				}
				var w = res[0].width, h = res[0].height
				var lines = []
				for (var i = 0; i < EDGES.length; i++) {
					var ai = EDGES[i][0], bi = EDGES[i][1]
					var na = self.nodes[ai], nb = self.nodes[bi]
					var x1 = na.x / 100 * w, y1 = na.yr / MAP_RPX * h
					var x2 = nb.x / 100 * w, y2 = nb.yr / MAP_RPX * h
					var dx = x2-x1, dy = y2-y1
					var len = Math.sqrt(dx*dx + dy*dy)
					var angle = Math.atan2(dy, dx) * 180 / Math.PI
					lines.push({
						lit: na.lit && nb.lit,
						style: {
							left: x1 + 'px', top: y1 + 'px',
							width: len + 'px',
							transform: 'rotate(' + angle.toFixed(2) + 'deg)'
						}
					})
				}
				self.lineData = lines
			})
		},
		openModal: function(i) {
			this.curIdx = i
			this.showModal = true
			this.modalReady = false
			var self = this
			setTimeout(function() { self.modalReady = true }, 50)
		},
		closeModal: function() { this.modalReady = false; var self = this; setTimeout(function() { self.showModal = false }, 350) },
		onAction: function() {
			var nd = this.nodes[this.curIdx]
			if (!nd) return
			// 星盘解析：已点亮则跳转报告页，未点亮则先点亮再跳转
			if (nd.id === 0) {
				if (!nd.lit) {
					this.$set(this.nodes, this.curIdx, enrichNode(Object.assign({}, nd, { lit: true })))
					this.computeLines()
				}
				this.closeModal()
				var self = this
				setTimeout(function() {
					uni.navigateTo({ url: '/pages/astro-report/astro-report' })
				}, 380)
				return
			}
			// 九型人格：跳转测试页
			if (nd.id === 2) {
				if (!nd.lit) {
					this.$set(this.nodes, this.curIdx, enrichNode(Object.assign({}, nd, { lit: true })))
					this.computeLines()
				}
				this.closeModal()
				var self = this
				setTimeout(function() {
					uni.navigateTo({ url: '/pages/enneagram-test/enneagram-test' })
				}, 380)
				return
			}
			// 亲密关系：跳转亲密关系测试页
			if (nd.id === 3) {
				if (!nd.lit) {
					this.$set(this.nodes, this.curIdx, enrichNode(Object.assign({}, nd, { lit: true })))
					this.computeLines()
				}
				this.closeModal()
				var self = this
				setTimeout(function() {
					uni.navigateTo({ url: '/pages/intimacy-test/intimacy-test' })
				}, 380)
				return
			}
			// 人格解码：跳转MBTI测试页
			if (nd.id === 1) {
				if (!nd.lit) {
					this.$set(this.nodes, this.curIdx, enrichNode(Object.assign({}, nd, { lit: true })))
					this.computeLines()
				}
				this.closeModal()
				var self = this
				setTimeout(function() {
					uni.navigateTo({ url: '/pages/mbti-test/mbti-test' })
				}, 380)
				return
			}
			// 职业发展：跳转霍兰德测试页
			if (nd.id === 6) {
				if (!nd.lit) {
					this.$set(this.nodes, this.curIdx, enrichNode(Object.assign({}, nd, { lit: true })))
					this.computeLines()
				}
				this.closeModal()
				var self = this
				setTimeout(function() {
					uni.navigateTo({ url: '/pages/holland-test/holland-test' })
				}, 380)
				return
			}
			// 心理健康：跳转心理健康测试页
			if (nd.id === 4) {
				if (!nd.lit) {
					this.$set(this.nodes, this.curIdx, enrichNode(Object.assign({}, nd, { lit: true })))
					this.computeLines()
				}
				this.closeModal()
				var self = this
				setTimeout(function() {
					uni.navigateTo({ url: '/pages/mh-test/mh-test' })
				}, 380)
				return
			}
			// 抑郁评估：跳转抑郁测试页
			if (nd.id === 5) {
				if (!nd.lit) {
					this.$set(this.nodes, this.curIdx, enrichNode(Object.assign({}, nd, { lit: true })))
					this.computeLines()
				}
				this.closeModal()
				var self = this
				setTimeout(function() {
					uni.navigateTo({ url: '/pages/depression-test/depression-test' })
				}, 380)
				return
			}
			if (nd.lit) { this.closeModal(); return }
			if (nd.isFinal && !this.allLit) return
			this.$set(this.nodes, this.curIdx, enrichNode(Object.assign({}, nd, { lit: true })))
			this.computeLines()
			this.closeModal()
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
	right: -160rpx; top: 60rpx;
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

/* Header */
.hdr {
	position: relative; z-index: 40;
	padding: 16rpx 32rpx 20rpx;
	display: flex; justify-content: space-between; align-items: center;
}
.logo-col { display: flex; flex-direction: column; }
.logo {
	font-size: 38rpx; font-weight: 700;
	letter-spacing: 10rpx; color: #322c52;
}
.logo-en {
	font-size: 18rpx; font-weight: 300;
	letter-spacing: 6rpx; color: rgba(115,108,148,0.48);
	font-style: italic; margin-top: 4rpx;
}
.hdr-pill {
	height: 52rpx; padding: 0 22rpx;
	border-radius: 30rpx;
	background: rgba(255,255,255,0.72);
	border: 1rpx solid rgba(210,200,235,0.50);
	display: flex; align-items: center;
	box-shadow: 0 4rpx 16rpx rgba(140,125,200,0.08);
}
.hdr-dot {
	width: 8rpx; height: 8rpx; border-radius: 50%;
	background: #9685ee; box-shadow: 0 0 12rpx rgba(150,133,238,0.55);
	margin-right: 12rpx;
	animation: dotPulse 3s ease-in-out infinite;
}
@keyframes dotPulse { 0%,100%{opacity:0.5;transform:scale(0.8)} 50%{opacity:1;transform:scale(1.4)} }
.hdr-frac { font-size: 22rpx; color: rgba(105,98,138,0.58); letter-spacing: 3rpx; font-style: italic; }

/* Status card */
.status-card {
	position: relative; z-index: 35;
	margin: 12rpx 28rpx 0;
	background: rgba(255,255,255,0.88);
	border: 1rpx solid rgba(210,200,235,0.50);
	border-radius: 28rpx;
	padding: 28rpx 32rpx;
	display: flex; align-items: center; justify-content: space-between;
	box-shadow: 0 16rpx 40rpx rgba(145,140,190,0.10), 0 4rpx 10rpx rgba(145,140,190,0.05), inset 0 1rpx 0 rgba(255,255,255,0.92);
}
.sc-left { flex: 1; }
.sc-title { font-size: 26rpx; color: #322c52; letter-spacing: 4rpx; font-weight: 600; }
.sc-bar-wrap {
	height: 4rpx; border-radius: 4rpx;
	background: rgba(210,200,235,0.30);
	margin: 14rpx 0 12rpx;
}
.sc-bar {
	height: 100%; border-radius: 4rpx;
	background: linear-gradient(90deg, #9685ee, #7d6bd6);
	box-shadow: 0 0 14rpx rgba(130,115,220,0.25);
	transition: width 0.8s ease;
}
.sc-sub { font-size: 20rpx; color: rgba(115,108,148,0.50); letter-spacing: 2rpx; font-style: italic; }
.sc-right { display: flex; flex-direction: column; align-items: center; margin-left: 24rpx; }
.sc-num { font-size: 56rpx; font-weight: 300; font-style: italic; color: #7d6bd6; text-shadow: 0 0 20rpx rgba(130,115,220,0.18); line-height: 1; }
.sc-label { font-size: 16rpx; color: rgba(115,108,148,0.42); letter-spacing: 3rpx; margin-top: 8rpx; }

/* Map */
.map-scroll {
	position: relative; z-index: 30;
	height: calc(100vh - 300rpx);
	margin-top: 16rpx;
}
.map-canvas {
	position: relative;
	width: 100%;
	height: 2500rpx;
}

/* Lines */
.conn-line {
	position: absolute;
	height: 1rpx;
	background: rgba(210,200,235,0.30);
	transform-origin: 0 50%;
	z-index: 1;
}
.conn-line.line-lit {
	height: 2rpx;
	background: linear-gradient(90deg, rgba(150,133,238,0.45), rgba(125,107,214,0.65));
	box-shadow: 0 0 10rpx rgba(130,115,220,0.18);
}

/* Node */
.node {
	position: absolute;
	transform: translate(-50%,-50%);
	display: flex; flex-direction: column; align-items: center;
	z-index: 5;
}
.aura {
	position: absolute;
	width: 160rpx; height: 160rpx;
	border-radius: 50%;
	z-index: 0; pointer-events: none;
}
.node-lit .aura { animation: aura 4.5s ease-in-out infinite; }
.node-dim .aura { animation: dimAura 3s ease-in-out infinite; }
@keyframes aura { 0%,100%{opacity:0.18;transform:scale(0.85)} 50%{opacity:0.48;transform:scale(1.15)} }
@keyframes dimAura { 0%,100%{opacity:0.28;transform:scale(0.8)} 50%{opacity:0.62;transform:scale(1.3)} }
.node-dim { animation: dimBreath 4s ease-in-out infinite alternate; }
@keyframes dimBreath { 0%,100%{opacity:0.6;transform:translate(-50%,-50%) scale(0.94)} 50%{opacity:1;transform:translate(-50%,-50%) scale(1.04)} }

/* Diamond */
.diamond {
	position: relative;
	width: 88rpx; height: 88rpx;
	display: flex; align-items: center; justify-content: center;
	z-index: 2;
}
.diamond-inner {
	position: absolute; width: 100%; height: 100%;
	transform: rotate(45deg);
	border-radius: 20rpx;
	background: rgba(255,255,255,0.88);
	border: 1rpx solid rgba(210,200,235,0.55);
	box-shadow: inset 0 1rpx 1rpx rgba(255,255,255,0.60), 0 6rpx 20rpx rgba(145,140,190,0.12);
	transition: all 0.4s;
}
.diamond-circle .diamond-inner {
	border-radius: 50%;
	transform: none;
}
.node-icon { position: relative; z-index: 3; font-size: 40rpx; line-height: 1; }
.node-final .node-icon { filter: blur(4rpx); opacity: 0.30; }
.node-dim .diamond-inner {
	background: rgba(245,244,255,0.82);
	border-color: rgba(150,133,238,0.35);
	box-shadow: 0 0 24rpx rgba(150,133,238,0.18), inset 0 1rpx 1rpx rgba(255,255,255,0.50);
}

/* Node text */
.node-text {
	margin-top: 18rpx;
	display: flex; flex-direction: column; align-items: center;
	z-index: 2;
}
.node-title {
	font-size: 22rpx; font-weight: 600;
	letter-spacing: 4rpx; color: #322c52;
}
.title-line {
	width: 24rpx; height: 2rpx;
	margin: 8rpx 0 6rpx;
	border-radius: 2rpx; opacity: 0.6;
}
.node-tag {
	font-size: 18rpx; font-style: italic;
	letter-spacing: 4rpx; opacity: 0.85;
}
.node-final .node-title { color: rgba(115,108,148,0.30); letter-spacing: 8rpx; }

/* Modal */
.modal-bg {
	position: fixed; inset: 0; z-index: 100;
	background: rgba(50,44,82,0.35);
	display: flex; align-items: flex-end;
}
.modal-sheet {
	width: 100%;
	background: linear-gradient(165deg, rgba(252,250,255,0.98), rgba(245,241,252,0.98));
	border-top: 1rpx solid rgba(210,200,235,0.50);
	border-radius: 48rpx 48rpx 0 0;
	padding: 0 40rpx calc(60rpx + env(safe-area-inset-bottom) + 120rpx);
	transform: translateY(100%);
	transition: transform 0.45s cubic-bezier(0.22,1,0.36,1);
	position: relative; overflow: hidden;
	box-shadow: 0 -24rpx 60rpx rgba(145,140,190,0.18), inset 0 1rpx 0 rgba(255,255,255,0.92);
}
.modal-sheet.open { transform: translateY(0); }
.m-handle {
	width: 60rpx; height: 6rpx; border-radius: 6rpx;
	background: rgba(210,200,235,0.40);
	margin: 24rpx auto 40rpx;
}
.m-glow {
	position: absolute; top: -120rpx; left: 50%; transform: translateX(-50%);
	width: 400rpx; height: 280rpx; border-radius: 50%;
	background: radial-gradient(circle, rgba(200,180,255,0.18), transparent 70%);
	pointer-events: none;
}
.m-icon-big { display: block; text-align: center; font-size: 64rpx; margin-bottom: 24rpx; }
.m-title {
	display: block; text-align: center;
	font-size: 42rpx; font-weight: 700; letter-spacing: 8rpx;
	color: #322c52;
	margin-bottom: 10rpx;
}
.m-en {
	display: block; text-align: center;
	font-size: 22rpx; font-style: italic; font-weight: 300;
	letter-spacing: 6rpx; color: rgba(150,133,238,0.72);
	margin-bottom: 32rpx;
}
.m-rule {
	width: 60rpx; height: 1.5rpx; margin: 0 auto 30rpx;
	background: linear-gradient(90deg, transparent, rgba(150,133,238,0.45), transparent);
	opacity: 0.85;
}
.m-quote {
	display: block; text-align: center;
	font-size: 26rpx; font-weight: 300;
	color: rgba(50,44,82,0.78);
	line-height: 2; letter-spacing: 2rpx;
	margin-bottom: 20rpx; padding: 0 16rpx;
}
.m-desc {
	display: block; text-align: center;
	font-size: 24rpx; color: rgba(115,108,148,0.55);
	line-height: 1.8; letter-spacing: 2rpx;
	margin-bottom: 40rpx; padding: 0 20rpx;
}
.m-btn {
	height: 96rpx; border-radius: 24rpx;
	background: linear-gradient(145deg, #9685ee, #7d6bd6);
	display: flex; align-items: center; justify-content: center;
	box-shadow: 0 10rpx 32rpx rgba(130,115,220,0.28);
}
.m-btn-lit {
	background: linear-gradient(145deg, #9685ee, #7d6bd6) !important;
	box-shadow: 0 10rpx 32rpx rgba(130,115,220,0.28) !important;
}
.m-btn-lock {
	background: rgba(210,200,235,0.22) !important;
	box-shadow: none !important;
}
.m-btn-lock .m-btn-text { color: rgba(115,108,148,0.30) !important; }
.m-btn-lit .m-btn-text { color: rgba(255,255,255,0.97) !important; }
.m-btn-hover { opacity: 0.88; transform: scale(0.98); }
.m-btn-text {
	font-size: 28rpx; font-weight: 700;
	letter-spacing: 5rpx; color: rgba(255,255,255,0.97);
}
.m-skip {
	display: block; text-align: center;
	margin-top: 24rpx;
	font-size: 22rpx; color: rgba(115,108,148,0.38);
	letter-spacing: 4rpx; font-style: italic;
}
</style>
