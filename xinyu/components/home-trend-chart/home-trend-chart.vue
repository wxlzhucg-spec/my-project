<template>
	<view class="card">
		<view class="card-header">
			<text class="card-title">近15日心情变化</text>
			<view class="summary-btn" @tap="onSummary">
				<text class="summary-text">影子总结</text>
			</view>
		</view>
		<view class="chart-wrap" @tap="onTap" @touchmove.stop="onMove">
			<canvas canvas-id="trendCanvas" class="trend-canvas"></canvas>
		</view>
	</view>
</template>

<script>
	export default {
		name: "home-trend-chart",
		props: {
			trendData: {
				type: Array,
				default: function() { return [] }
			}
		},
		data: function() {
			return {
				days: [],
				activeIdx: -1,
				pts: [],
				cRect: null,
				cW: 0, cH: 0,
				padT: 30, padB: 22, padL: 12, padR: 16
			}
		},
		watch: {
			trendData: {
				handler: function(val) {
					if (val && val.length > 0) {
						this.days = val
						if (this.cW > 0) {
							this.computePoints()
							this.render()
						}
					}
				},
				immediate: true,
				deep: true
			}
		},
		mounted: function() {
			var self = this
			this.$nextTick(function() {
				setTimeout(function() { self.initChart() }, 300)
			})
		},
		methods: {
			onSummary: function() {
				this.$emit('summary')
			},
			initChart: function() {
				var self = this
				var q = uni.createSelectorQuery().in(this)
				q.select('.trend-canvas').boundingClientRect().exec(function(res) {
					if (!res || !res[0] || res[0].width < 10) {
						setTimeout(function() { self.initChart() }, 500)
						return
					}
					self.cRect = res[0]
					self.cW = res[0].width
					self.cH = res[0].height
					self.computePoints()
					self.render()
				})
			},
			computePoints: function() {
				var n = this.days.length
				var cw = this.cW - this.padL - this.padR
				var ch = this.cH - this.padT - this.padB
				var pts = []
				for (var i = 0; i < n; i++) {
					pts.push({
						x: this.padL + (i / (n - 1)) * cw,
						y: this.padT + (1 - this.days[i].s / 100) * ch
					})
				}
				this.pts = pts
			},
			onTap: function(e) {
				var x = -1
				if (e.detail && typeof e.detail.x === 'number') {
					x = e.detail.x
				} else if (e.touches && e.touches[0] && this.cRect) {
					x = e.touches[0].clientX - this.cRect.left
				} else if (typeof e.offsetX === 'number') {
					x = e.offsetX
				}
				if (x >= 0) this.selectNearest(x)
			},
			onMove: function(e) {
				var touch = e.touches ? e.touches[0] : null
				if (!touch || !this.cRect) return
				var x = touch.clientX - this.cRect.left
				if (x >= 0) this.selectNearest(x)
			},
			selectNearest: function(x) {
				var closest = -1, minD = 25
				for (var i = 0; i < this.pts.length; i++) {
					var d = Math.abs(this.pts[i].x - x)
					if (d < minD) { minD = d; closest = i }
				}
				if (closest !== this.activeIdx) {
					this.activeIdx = closest
					this.render()
				}
			},
			render: function() {
				var ctx = uni.createCanvasContext('trendCanvas', this)
				var w = this.cW, h = this.cH
				var pts = this.pts, n = pts.length, data = this.days
				var pT = this.padT, pB = this.padB, pL = this.padL, pR = this.padR
				if (n < 2) return

				ctx.setStrokeStyle('rgba(110,100,170,0.07)')
				ctx.setLineWidth(0.5)
				for (var g = 0; g <= 4; g++) {
					var gy = pT + (g / 4) * (h - pT - pB)
					ctx.beginPath()
					ctx.moveTo(pL, gy)
					ctx.lineTo(w - pR, gy)
					ctx.stroke()
				}

				var grd = ctx.createLinearGradient(0, pT, 0, h - pB)
				grd.addColorStop(0, 'rgba(130,118,186,0.18)')
				grd.addColorStop(1, 'rgba(130,118,186,0)')
				ctx.setFillStyle(grd)
				ctx.beginPath()
				ctx.moveTo(pts[0].x, h - pB)
				ctx.lineTo(pts[0].x, pts[0].y)
				this.drawCurve(ctx, pts)
				ctx.lineTo(pts[n - 1].x, h - pB)
				ctx.closePath()
				ctx.fill()

				ctx.beginPath()
				ctx.moveTo(pts[0].x, pts[0].y)
				this.drawCurve(ctx, pts)
				ctx.setStrokeStyle('#8276ba')
				ctx.setLineWidth(1.6)
				ctx.stroke()

				for (var i = 0; i < n; i++) {
					var isActive = (i === this.activeIdx)
					ctx.beginPath()
					ctx.arc(pts[i].x, pts[i].y, isActive ? 5 : 2.8, 0, Math.PI * 2)
					ctx.setFillStyle(isActive ? '#7264af' : '#ffffff')
					ctx.fill()
					ctx.setStrokeStyle('#8276ba')
					ctx.setLineWidth(isActive ? 2 : 1.4)
					ctx.stroke()
					if (isActive) {
						ctx.beginPath()
						ctx.arc(pts[i].x, pts[i].y, 2.5, 0, Math.PI * 2)
						ctx.setFillStyle('#ffffff')
						ctx.fill()
					}
				}

				if (this.activeIdx >= 0) {
					var ai = this.activeIdx
					var px = pts[ai].x, py = pts[ai].y

					ctx.setStrokeStyle('rgba(110,100,170,0.10)')
					ctx.setLineWidth(0.8)
					ctx.beginPath()
					ctx.moveTo(px, pT)
					ctx.lineTo(px, h - pB)
					ctx.stroke()

					var txt = data[ai].d + '  ' + data[ai].s + '分'
					var bw = 68, bh = 24, br = 5
					var bx = px - bw / 2
					var by = py - bh - 10
					if (by < 2) by = py + 10
					if (bx < 2) bx = 2
					if (bx + bw > w - 2) bx = w - 2 - bw

					ctx.beginPath()
					ctx.moveTo(bx + br, by)
					ctx.lineTo(bx + bw - br, by)
					ctx.arcTo(bx + bw, by, bx + bw, by + br, br)
					ctx.lineTo(bx + bw, by + bh - br)
					ctx.arcTo(bx + bw, by + bh, bx + bw - br, by + bh, br)
					ctx.lineTo(bx + br, by + bh)
					ctx.arcTo(bx, by + bh, bx, by + bh - br, br)
					ctx.lineTo(bx, by + br)
					ctx.arcTo(bx, by, bx + br, by, br)
					ctx.closePath()
					ctx.setFillStyle('rgba(44,36,80,0.88)')
					ctx.fill()

					var triY = (by < py) ? by + bh : by
					var triDir = (by < py) ? 1 : -1
					ctx.beginPath()
					ctx.moveTo(px - 4, triY)
					ctx.lineTo(px, triY + 5 * triDir)
					ctx.lineTo(px + 4, triY)
					ctx.closePath()
					ctx.setFillStyle('rgba(44,36,80,0.88)')
					ctx.fill()

					ctx.setFillStyle('#ffffff')
					ctx.setFontSize(10)
					ctx.setTextAlign('center')
					ctx.fillText(txt, bx + bw / 2, by + bh / 2 + 3.5)
				}

				ctx.setFillStyle('#a89cc8')
				ctx.setFontSize(9)
				ctx.setTextAlign('center')
				var labels = [0, 3, 7, 11, 14]
				for (var li = 0; li < labels.length; li++) {
					var idx = labels[li]
					if (idx < n) {
						ctx.fillText(data[idx].d, pts[idx].x, h - 4)
					}
				}

				ctx.draw()
			},
			drawCurve: function(ctx, pts) {
				var n = pts.length
				for (var i = 0; i < n - 1; i++) {
					var p0 = pts[i > 0 ? i - 1 : 0]
					var p1 = pts[i]
					var p2 = pts[i + 1]
					var p3 = pts[i + 2 < n ? i + 2 : n - 1]
					var cp1x = p1.x + (p2.x - p0.x) / 6
					var cp1y = p1.y + (p2.y - p0.y) / 6
					var cp2x = p2.x - (p3.x - p1.x) / 6
					var cp2y = p2.y - (p3.y - p1.y) / 6
					ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y)
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
	.summary-btn {
		padding: 8rpx 20rpx;
		border-radius: 20rpx;
		border: 1rpx solid rgba(130,118,186,0.14);
		background: rgba(130,118,186,0.07);
	}
	.summary-text {
		font-size: 22rpx;
		color: #7264af;
		font-weight: 500;
	}
	.chart-wrap {
		width: 100%;
		height: 280rpx;
		position: relative;
	}
	.trend-canvas {
		width: 100%;
		height: 280rpx;
	}
</style>
