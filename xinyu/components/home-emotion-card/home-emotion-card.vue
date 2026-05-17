<template>
	<view class="card">
		<view class="card-header">
			<text class="card-title">今日心情</text>
			<view class="update-info" :class="{ 'update-pending': !updatedToday }" @tap="goToRecord">
				<view class="update-dot"></view>
				<text class="update-text">{{ updatedToday ? '已更新' : '待更新' }}</text>
			</view>
		</view>

		<!-- 已更新：显示分数 + 圆环 -->
		<view v-if="updatedToday" class="emotion-content">
			<view class="score-display">
				<view class="score-left">
					<view class="score-num-row">
						<text class="score-big">{{ calcScore }}</text>
						<text class="score-unit">分</text>
					</view>
					<text class="score-label">{{ moodLabel }}</text>
				</view>
			</view>
			<view class="ring-group">
				<view class="ring-item">
					<canvas canvas-id="emoRingCanvas" class="ring-canvas emo-rc"></canvas>
					<view class="ring-text">
						<text class="ring-val">{{ emoVal }}</text>
						<text class="ring-lab">情绪</text>
					</view>
				</view>
				<view class="ring-item">
					<canvas canvas-id="vitRingCanvas" class="ring-canvas vit-rc"></canvas>
					<view class="ring-text">
						<text class="ring-val">{{ vitVal }}</text>
						<text class="ring-lab">活力</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 未更新：显示待更新占位 -->
		<view v-else class="emotion-content pending-content">
			<view class="pending-center">
				<view class="pending-icon-wrap">
					<text class="pending-icon">☁️</text>
				</view>
				<text class="pending-hint">点击记录今日心情</text>
				<text class="pending-sub">情绪 60% + 活力 40% = 综合分</text>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		name: "home-emotion-card",
		props: {
			score: { type: Number, default: 89 },
			emoVal: { type: Number, default: 76 },
			vitVal: { type: Number, default: 92 },
			updatedToday: { type: Boolean, default: true }
		},
		mounted: function() {
			var self = this
			this.$nextTick(function() {
				setTimeout(function() { self.drawRings() }, 200)
			})
		},
		computed: {
			calcScore: function() {
				return Math.round(this.emoVal * 0.6 + this.vitVal * 0.4)
			},
			moodLabel: function() {
				if (!this.updatedToday) return ''
				var s = this.calcScore
				if (s >= 90) return '元气满满 ✦'
				if (s >= 75) return '状态良好'
				if (s >= 60) return '还算平稳'
				if (s >= 45) return '有点疲惫'
				return '需要关爱'
			}
		},
		methods: {
			goToRecord: function() {
				this.$emit('open-record')
			},
			drawRings: function() {
				if (!this.updatedToday) return
				var self = this
				var q = uni.createSelectorQuery().in(this)
				q.select('.emo-rc').boundingClientRect()
				q.select('.vit-rc').boundingClientRect()
				q.exec(function(res) {
					if (res && res[0] && res[0].width > 0) {
						self.drawOneRing('emoRingCanvas', res[0].width, res[0].height, self.emoVal / 100)
					}
					if (res && res[1] && res[1].width > 0) {
						self.drawOneRing('vitRingCanvas', res[1].width, res[1].height, self.vitVal / 100)
					}
				})
			},
			drawOneRing: function(canvasId, w, h, pct) {
				var ctx = uni.createCanvasContext(canvasId, this)
				var lw = w * 0.1
				var cx = w / 2, cy = h / 2
				var r = (Math.min(w, h) - lw) / 2

				ctx.beginPath()
				ctx.arc(cx, cy, r, 0, Math.PI * 2)
				ctx.setStrokeStyle('#e0dbf4')
				ctx.setLineWidth(lw)
				ctx.stroke()

				if (pct > 0) {
					var start = -Math.PI / 2
					var end = start + pct * Math.PI * 2
					ctx.beginPath()
					ctx.arc(cx, cy, r, start, end)
					ctx.setStrokeStyle('#8276ba')
					ctx.setLineWidth(lw * 0.92)
					ctx.setLineCap('round')
					ctx.stroke()
				}

				ctx.draw()
			}
		},
		watch: {
			updatedToday: function(val) {
				if (val) {
					var self = this
					this.$nextTick(function() {
						setTimeout(function() { self.drawRings() }, 150)
					})
				}
			}
		}
	}
</script>

<style scoped>
	.card {
		background: rgba(255,255,255,0.88);
		border-radius: 32rpx;
		padding: 36rpx 32rpx;
		margin-bottom: 24rpx;
		box-shadow: 0 6rpx 28rpx rgba(100,88,170,0.08);
		border: 1rpx solid rgba(255,255,255,0.65);
	}
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24rpx;
	}
	.card-title {
		font-size: 28rpx;
		font-weight: 600;
		color: #2c2450;
	}
	.update-info {
		display: flex;
		align-items: center;
		gap: 8rpx;
		background: rgba(130,118,186,0.09);
		padding: 6rpx 16rpx;
		border-radius: 20rpx;
	}
	.update-info.update-pending {
		background: rgba(220,180,80,0.12);
	}
	.update-dot {
		width: 10rpx;
		height: 10rpx;
		border-radius: 50%;
		background: #9088c0;
	}
	.update-pending .update-dot {
		background: #d4a84a;
		animation: dotPulse 1.5s ease-in-out infinite;
	}
	@keyframes dotPulse {
		0%, 100% { opacity: 0.35; transform: scale(0.85); }
		50% { opacity: 1; transform: scale(1); }
	}
	.update-text {
		font-size: 22rpx;
		color: #9088b8;
		font-weight: 600;
	}
	.update-pending .update-text {
		color: #c49a48;
	}

	.emotion-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	/* ── 已更新状态 ── */
	.score-display {
		display: flex;
		align-items: flex-start;
	}
	.score-left {
		display: flex;
		flex-direction: column;
	}
	.score-num-row {
		display: flex;
		align-items: baseline;
	}
	.score-big {
		font-size: 104rpx;
		font-weight: bold;
		line-height: 1;
		color: #2c2450;
	}
	.score-unit {
		font-size: 28rpx;
		margin-left: 8rpx;
		font-weight: 500;
		color: #5a4e82;
	}
	.score-label {
		font-size: 22rpx;
		color: #8276ba;
		font-weight: 500;
		margin-top: 8rpx;
		letter-spacing: 1rpx;
	}
	.ring-group {
		display: flex;
		gap: 24rpx;
	}
	.ring-item {
		position: relative;
		width: 104rpx;
		height: 104rpx;
	}
	.ring-canvas {
		width: 104rpx;
		height: 104rpx;
	}
	.ring-text {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		z-index: 2;
	}
	.ring-val {
		font-size: 24rpx;
		font-weight: bold;
		line-height: 1;
		margin-bottom: 4rpx;
		color: #4a4278;
	}
	.ring-lab {
		font-size: 16rpx;
		color: #9088b8;
		transform: scale(0.9);
	}

	/* ── 待更新状态 ── */
	.pending-content {
		min-height: 160rpx;
	}
	.pending-center {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 20rpx 0;
	}
	.pending-icon-wrap {
		width: 72rpx; height: 72rpx;
		border-radius: 50%;
		background: linear-gradient(135deg, #f0edf9, #e8e3f4);
		display: flex; align-items: center; justify-content: center;
		margin-bottom: 14rpx;
	}
	.pending-icon { font-size: 32rpx; }
	.pending-hint {
		font-size: 26rpx;
		color: #7d6bd6;
		font-weight: 500;
		margin-bottom: 6rpx;
	}
	.pending-sub {
		font-size: 20rpx;
		color: #a098bc;
	}
</style>
