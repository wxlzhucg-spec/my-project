<template>
	<view class="astro-report">
		<!-- 头部 -->
		<view class="report-header">
			<view class="header-icon-wrap">
				<text class="header-icon">✦</text>
			</view>
			<text class="header-title">星盘解析报告</text>
			<text class="header-sub">ASTRO CHART REPORT</text>
		</view>

		<!-- 基本信息 -->
		<view class="section-card info-card">
			<view class="card-label">
				<text class="label-dot"></text>
				<text class="label-text">出生信息</text>
			</view>
			<view class="info-grid">
				<view class="info-item">
					<text class="info-label">出生日期</text>
					<text class="info-value">{{ birthInfo.date }}</text>
				</view>
				<view class="info-item">
					<text class="info-label">出生时间</text>
					<text class="info-value">{{ birthInfo.time }}</text>
				</view>
				<view class="info-item">
					<text class="info-label">出生地点</text>
					<text class="info-value">{{ birthInfo.location }}</text>
				</view>
			</view>
		</view>

		<!-- 三巨头 -->
		<view class="section-card trinity-card">
			<view class="card-label">
				<text class="label-dot label-dot--gold"></text>
				<text class="label-text">灵魂三巨头</text>
			</view>
			<view class="trinity-grid">
				<view class="trinity-item" v-for="(item, idx) in trinity" :key="idx">
					<view class="trinity-icon-wrap" :style="{ background: item.bg }">
						<text class="trinity-icon">{{ item.icon }}</text>
					</view>
					<text class="trinity-name">{{ item.name }}</text>
					<text class="trinity-sign">{{ item.sign }}</text>
					<text class="trinity-degree">{{ item.degree }}</text>
					<view class="trinity-desc">
						<text class="desc-text">{{ item.desc }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 行星位置表 -->
		<view class="section-card planets-card">
			<view class="planets-header">
				<view class="card-label">
					<text class="label-dot label-dot--cyan"></text>
					<text class="label-text">行星位置</text>
				</view>
				<view class="header-badge">
					<text class="badge-text">{{ planets.length }} 颗行星</text>
				</view>
			</view>

			<scroll-view scroll-y class="planets-scroll" :style="{ maxHeight: planetsScrollHeight }">
				<view class="planet-list">
					<view class="planet-row" v-for="(p, idx) in planets" :key="idx">
						<view class="planet-icon-cell">
							<view class="picon-wrap" :style="{ background: p.iconBg }">
								<text class="picon">{{ p.icon }}</text>
							</view>
						</view>
						<text class="planet-name">{{ p.name }}</text>
						<text class="planet-sign">{{ p.sign }}</text>
						<text class="planet-pos">{{ p.position }}</text>
						<text class="planet-house">{{ p.house }}</text>
					</view>
				</view>
			</scroll-view>
		</view>

		<!-- 性格概要 -->
		<view class="section-card summary-card">
			<view class="card-label">
				<text class="label-dot label-dot--purple"></text>
				<text class="label-text">性格概要</text>
			</view>
			<view class="summary-content">
				<text class="summary-text">{{ personalitySummary }}</text>
			</view>
			<view class="traits-grid">
				<view class="trait-item" v-for="(t, idx) in traitsWithBar" :key="idx">
					<view class="trait-bar-wrap">
						<view class="trait-bar" :style="t.barStyle"></view>
					</view>
					<view class="trait-info">
						<text class="trait-name">{{ t.name }}</text>
						<text class="trait-val">{{ t.value }}%</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 元素分布 -->
		<view class="section-card elements-card">
			<view class="card-label">
				<text class="label-dot label-dot--orange"></text>
				<text class="label-text">四元素能量</text>
			</view>
			<view class="elements-grid">
				<view class="element-item" v-for="(el, idx) in elements" :key="idx">
					<view class="el-circle" :style="{ borderColor: el.color }">
						<text class="el-icon">{{ el.icon }}</text>
						<text class="el-percent" :style="{ color: el.color }">{{ el.percent }}%</text>
					</view>
					<text class="el-name" :style="{ color: el.color }">{{ el.name }}</text>
					<text class="el-desc">{{ el.desc }}</text>
				</view>
			</view>
		</view>

		<!-- 底部操作 -->
		<view class="action-area">
			<view class="action-btn primary-btn" hover-class="btn-hover" @tap="$emit('deep-analysis')">
				<text class="btn-text">深度解读 ✦</text>
			</view>
			<view class="action-btn secondary-btn" hover-class="btn-hover-secondary" @tap="$emit('share')">
				<text class="btn-text btn-text-secondary">分享报告</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	name: 'astro-report',
	props: {
		birthInfo: {
			type: Object,
			default: function() {
				return { date: '1995年6月15日', time: '14:30', location: '北京市' }
			}
		},
		trinity: {
			type: Array,
			default: function() {
				return [
					{ icon: '☉', name: '太阳', sign: '双子座', degree: '23°37\'', bg: 'linear-gradient(145deg, #ffd89b, #e8a87c)', desc: '思维敏捷，善于沟通表达' },
					{ icon: '☽', name: '月亮', sign: '白羊座', degree: '19°34\'', bg: 'linear-gradient(145deg, #a8edea, #82c8c8)', desc: '情绪直接，行动力强' },
					{ icon: '▲', name: '上升', sign: '天秤座', degree: '27°45\'', bg: 'linear-gradient(145deg, #d299c2, #b89ec5)', desc: '外表优雅，追求平衡和谐' }
				]
			}
		},
		planets: {
			type: Array,
			default: function() {
				return [
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
			}
		},
		personalitySummary: {
			type: String,
			default: '你的星盘呈现出强烈的风象特质，太阳与水星同在双子座，赋予你敏锐的思维能力与出色的沟通天赋。月亮位于白羊座让你的情感表达直率而真诚。上升天秤座则为你增添了一份优雅与外交手腕。你是一个既能独立思考又善于协作的人，在人群中总是能找到自己的位置并发挥影响力。'
		},
		traits: {
			type: Array,
			default: function() {
				return [
					{ name: '创造力', value: 85, color: '#9685ee' },
					{ name: '执行力', value: 72, color: '#3ec9c1' },
					{ name: '感知力', value: 90, color: '#d4607a' },
					{ name: '稳定性', value: 58, color: '#dda03f' }
				]
			}
		},
		elements: {
			type: Array,
			default: function() {
				return [
					{ icon: '🔥', name: '火象', percent: 25, desc: '热情冲动', color: '#e88555' },
					{ icon: '🌍', name: '土象', percent: 15, desc: '稳重务实', color: '#a89070' },
					{ icon: '💨', name: '风象', percent: 45, desc: '理性智慧', color: '#6898ce' },
					{ icon: '💧', name: '水象', percent: 15, desc: '敏感直觉', color: '#5ca8b8' }
				]
			}
		}
	},
	computed: {
		planetsScrollHeight: function() {
			var count = this.planets.length || 10
			return Math.min(count * 72 + 20, 520) + 'rpx'
		},
		traitsWithBar: function() {
			return this.traits.map(function(t) {
				return {
					name: t.name,
					value: t.value,
					color: t.color,
					barStyle: { width: t.value + '%', background: t.color }
				}
			})
		}
	}
}
</script>

<style scoped>
.astro-report {
	padding: 0 24rpx 40rpx;
}

/* ---- 头部 ---- */
.report-header {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 40rpx 0 36rpx;
	position: relative;
}
.header-icon-wrap {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	background: linear-gradient(145deg, #9685ee, #7d6bd6);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 28rpx rgba(130,115,220,0.30);
	margin-bottom: 20rpx;
}
.header-icon {
	font-size: 32rpx;
	color: #ffffff;
}
.header-title {
	font-size: 38rpx;
	font-weight: 700;
	color: #2c2450;
	letter-spacing: 6rpx;
	margin-bottom: 8rpx;
}
.header-sub {
	font-size: 20rpx;
	color: rgba(130,118,186,0.50);
	letter-spacing: 4rpx;
	font-weight: 300;
	font-style: italic;
}

/* ---- 通用卡片 ---- */
.section-card {
	background: rgba(255,255,255,0.88);
	border-radius: 28rpx;
	padding: 28rpx 28rpx 24rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 6rpx 28rpx rgba(100,88,170,0.08);
	border: 1rpx solid rgba(255,255,255,0.65);
}
.card-label {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 20rpx;
}
.label-dot {
	width: 10rpx;
	height: 10rpx;
	border-radius: 50%;
	background: #8276ba;
	box-shadow: 0 0 10rpx rgba(130,118,186,0.45);
}
.label-dot--gold { background: #dda03f; box-shadow: 0 0 10rpx rgba(221,160,63,0.45); }
.label-dot--cyan { background: #3ec9c1; box-shadow: 0 0 10rpx rgba(62,201,193,0.45); }
.label-dot--purple { background: #9685ee; box-shadow: 0 0 10rpx rgba(150,133,238,0.45); }
.label-dot--orange { background: #e88555; box-shadow: 0 0 10rpx rgba(232,133,85,0.45); }
.label-text {
	font-size: 26rpx;
	font-weight: 600;
	color: #2c2450;
	letter-spacing: 3rpx;
}

/* ---- 基本信息 ---- */
.info-grid {
	display: flex;
	flex-direction: column;
	gap: 14rpx;
}
.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 14rpx 18rpx;
	background: rgba(130,118,186,0.05);
	border-radius: 16rpx;
	border: 1rpx solid rgba(130,118,186,0.08);
}
.info-label {
	font-size: 24rpx;
	color: #9088b8;
	font-weight: 500;
}
.info-value {
	font-size: 26rpx;
	color: #3c3268;
	font-weight: 600;
}

/* ---- 三巨头 ---- */
.trinity-grid {
	display: flex;
	gap: 16rpx;
}
.trinity-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 20rpx 12rpx 16rpx;
	background: linear-gradient(165deg, rgba(255,255,255,0.60), rgba(244,240,252,0.45));
	border-radius: 20rpx;
	border: 1rpx solid rgba(210,200,235,0.20);
}
.trinity-icon-wrap {
	width: 64rpx;
	height: 64rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 14rpx;
	box-shadow: 0 4rpx 14rpx rgba(0,0,0,0.06);
}
.trinity-icon {
	font-size: 30rpx;
	line-height: 1;
}
.trinity-name {
	font-size: 22rpx;
	color: #9088b8;
	font-weight: 500;
	margin-bottom: 6rpx;
}
.trinity-sign {
	font-size: 28rpx;
	font-weight: 700;
	color: #2c2450;
	letter-spacing: 2rpx;
	margin-bottom: 4rpx;
}
.trinity-degree {
	font-size: 20rpx;
	color: rgba(130,118,186,0.55);
	margin-bottom: 12rpx;
}
.trinity-desc {
	text-align: center;
	max-width: 100%;
}
.desc-text {
	font-size: 20rpx;
	color: rgba(130,118,186,0.65);
	line-height: 1.5;
}

/* ---- 行星位置 ---- */
.planets-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 18rpx;
}
.header-badge {
	padding: 6rpx 18rpx;
	border-radius: 20rpx;
	background: rgba(62,201,193,0.10);
	border: 1rpx solid rgba(62,201,193,0.18);
}
.badge-text {
	font-size: 20rpx;
	color: #3ec9c1;
	font-weight: 600;
}
.planets-scroll {
	border-radius: 18rpx;
	background: rgba(250,248,255,0.50);
	border: 1rpx solid rgba(210,200,235,0.15);
}
.planet-list {
	padding: 8rpx 0;
}
.planet-row {
	display: flex;
	align-items: center;
	padding: 14rpx 18rpx;
	border-bottom: 1rpx solid rgba(210,200,235,0.10);
}
.planet-row:last-child {
	border-bottom: none;
}
.planet-icon-cell {
	margin-right: 16rpx;
	flex-shrink: 0;
}
.picon-wrap {
	width: 46rpx;
	height: 46rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}
.picon {
	font-size: 22rpx;
	line-height: 1;
}
.planet-name {
	width: 110rpx;
	font-size: 24rpx;
	color: #3c3268;
	font-weight: 600;
	flex-shrink: 0;
}
.planet-sign {
	width: 120rpx;
	font-size: 24rpx;
	color: #2c2450;
	font-weight: 600;
	flex-shrink: 0;
}
.planet-pos {
	width: 100rpx;
	font-size: 22rpx;
	color: rgba(130,118,186,0.65);
	font-family: monospace;
	flex-shrink: 0;
}
.planet-house {
	flex: 1;
	text-align: right;
	font-size: 22rpx;
	color: rgba(144,136,184,0.50);
	font-weight: 500;
}

/* ---- 性格概要 ---- */
.summary-content {
	margin-bottom: 24rpx;
	padding: 18rpx 20rpx;
	background: linear-gradient(135deg, rgba(150,133,238,0.06), rgba(125,107,214,0.04));
	border-radius: 16rpx;
	border-left: 4rpx solid #9685ee;
}
.summary-text {
	font-size: 25rpx;
	color: #48407a;
	line-height: 1.85;
	letter-spacing: 1rpx;
}
.traits-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16rpx;
}
.trait-item {
	background: rgba(250,248,255,0.60);
	padding: 16rpx 18rpx;
	border-radius: 16rpx;
	border: 1rpx solid rgba(210,200,235,0.12);
}
.trait-bar-wrap {
	height: 8rpx;
	background: rgba(210,200,235,0.25);
	border-radius: 4rpx;
	margin-bottom: 10rpx;
	overflow: hidden;
}
.trait-bar {
	height: 100%;
	border-radius: 4rpx;
	transition: width 0.6s ease;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.08);
}
.trait-info {
	display: flex;
	justify-content: space-between;
	align-items: center;
}
.trait-name {
	font-size: 22rpx;
	color: #5a4e82;
	font-weight: 500;
}
.trait-val {
	font-size: 22rpx;
	color: #8276ba;
	font-weight: 700;
}

/* ---- 四元素 ---- */
.elements-grid {
	display: flex;
	gap: 14rpx;
	justify-content: space-between;
}
.element-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 18rpx 8rpx 14rpx;
	background: rgba(250,248,255,0.55);
	border-radius: 18rpx;
	border: 1rpx solid rgba(210,200,235,0.12);
}
.el-circle {
	width: 84rpx;
	height: 84rpx;
	border-radius: 50%;
	border: 3rpx solid;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	margin-bottom: 12rpx;
	background: rgba(255,255,255,0.75);
}
.el-icon {
	font-size: 28rpx;
	line-height: 1;
	margin-bottom: 4rpx;
}
.el-percent {
	font-size: 24rpx;
	font-weight: 700;
}
.el-name {
	font-size: 24rpx;
	font-weight: 600;
	margin-bottom: 4rpx;
}
.el-desc {
	font-size: 18rpx;
	color: rgba(130,118,186,0.50);
}

/* ---- 底部按钮 ---- */
.action-area {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 16rpx;
	margin-top: 32rpx;
	padding: 0 24rpx;
}
.action-btn {
	width: 100%;
	height: 92rpx;
	border-radius: 24rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}
.primary-btn {
	background: linear-gradient(148deg, #9a8fcb 0%, #8276ba 52%, #7264af 100%);
	box-shadow: 0 8rpx 28rpx rgba(130,118,186,0.28);
	border: 1rpx solid rgba(255,255,255,0.16);
}
.secondary-btn {
	background: rgba(255,255,255,0.85);
	border: 1rpx solid rgba(130,118,186,0.18);
	box-shadow: 0 4rpx 16rpx rgba(100,88,170,0.06);
}
.btn-hover { opacity: 0.88; transform: scale(0.98); }
.btn-hover-secondary { opacity: 0.85; transform: scale(0.98); }
.btn-text {
	font-size: 28rpx;
	color: rgba(255,255,255,0.96);
	font-weight: 600;
	letter-spacing: 3rpx;
}
.btn-text-secondary {
	color: #7d6bd6;
	letter-spacing: 2rpx;
}
</style>
