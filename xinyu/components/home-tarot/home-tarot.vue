<template>
	<view class="tarot-wrapper">
		<text class="tarot-title">塔罗解惑</text>

		<!-- 未抽卡：扇形牌堆 -->
		<view class="stage" v-if="!hasResult">
			<view v-for="(card, i) in fanCards" :key="i" class="card-wrap" :style="card.style">
				<view class="card-face">
					<view class="card-frame">
						<view class="cat-icon">
							<view class="ear ear-l"></view>
							<view class="ear ear-r"></view>
							<view class="head"></view>
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 未抽卡：主题 + 自定义问题（紧挨在「点击抽卡」上方） -->
		<view class="tarot-theme-panel" v-if="!hasResult">
			<view class="theme-head">
				<text class="theme-head-title">主题</text>
				<text class="theme-head-meta">必选其一</text>
			</view>
			<view class="theme-tag-grid">
				<view
					v-for="t in tarotThemeTags"
					:key="t.id"
					class="theme-tag"
					:class="['theme-tag--' + t.cat, { 'theme-tag--on': selectedTagId === t.id }]"
					hover-class="theme-tag-hover"
					@tap="toggleThemeTag(t.id)">
					<text class="theme-tag-t">{{ t.label }}</text>
				</view>
			</view>
			<input
				class="theme-question-input"
				type="text"
				:value="customQuestion"
				@input="onQuestionInput"
				placeholder="自定义问题（与主题二选一）"
				placeholder-class="theme-question-ph"
				confirm-type="done"
				maxlength="120"
			/>
		</view>

		<!-- 已抽卡：展示 3 张结果 -->
		<view class="result-area" v-else>
			<view class="result-pos-row">
				<view v-for="(card, i) in drawnCards" :key="'r'+i" class="result-col">
					<view class="result-card" :style="{ background: card.bg }">
						<view class="rc-c rc-tl"></view>
						<view class="rc-c rc-tr"></view>
						<view class="rc-c rc-bl"></view>
						<view class="rc-c rc-br"></view>
						<text class="rc-num">{{ card.num }}</text>
						<view class="rc-ring">
							<text class="rc-sym">{{ card.symbol }}</text>
						</view>
						<text class="rc-name">{{ card.name }}</text>
						<text class="rc-desc">{{ card.desc }}</text>
					</view>
					<text class="rc-pos-label">{{ posLabels[i] }}</text>
				</view>
			</view>
		</view>

		<view class="btn-row">
			<view
				class="draw-btn"
				:class="{ 'draw-btn--disabled': !canDraw }"
				hover-class="canDraw ? 'draw-btn-hover' : ''"
				@tap="onDrawBtn"
			>
				<text class="draw-btn-text">{{ hasResult ? '解析卡牌' : '点击抽卡' }}</text>
			</view>
			<text class="draw-hint" :class="{ 'draw-hint--show': !hasResult && !canDraw }">请先选定标签再抽牌</text>
		</view>
		<view v-if="hasResult" class="reset-row" @tap="resetDraw">
			<text class="reset-link">重新抽一次</text>
		</view>
	</view>
</template>

<script>
	var ANGLES = [-26,-20,-14.5,-10,-5.5,-1.5,1.5,5.5,10,14.5,20,26]
	var CW = 48, CH = 70, COUNT = 12, MID = (COUNT - 1) / 2

	export default {
		name: "home-tarot",
		data: function() {
			var fanCards = []
			for (var i = 0; i < COUNT; i++) {
				var deg = ANGLES[i]
				var offset = (i - MID) * 17
				var yShift = Math.abs(i - MID) * 2.5
				var z = i <= MID ? i + 1 : COUNT - i
				fanCards.push({
					style: {
						left: 'calc(50% + ' + offset + 'px - ' + (CW / 2) + 'px)',
						bottom: (38 - yShift) + 'px',
						width: CW + 'px',
						height: CH + 'px',
						zIndex: z,
						transform: 'rotate(' + deg + 'deg)'
					}
				})
			}
		return {
			fanCards: fanCards,
			hasResult: false,
			drawnCards: [],
			posLabels: ['过去', '现在', '未来'],
			selectedTagId: '',
			customQuestion: '',
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
				]
			}
		},
		computed: {
			canDraw: function() {
				return !!(this.selectedTagId || (this.customQuestion || '').trim())
			}
		},
		mounted: function() { this.checkDrawn() },
		methods: {
			checkDrawn: function() {
				var raw = uni.getStorageSync('tarotResult')
				if (raw) {
					try {
						var cards = JSON.parse(raw)
						if (cards && cards.length === 3) {
							this.drawnCards = cards
							this.hasResult = true
							return
						}
					} catch (e) {}
				}
				this.hasResult = false
				this.drawnCards = []
			},
			onDrawBtn: function() {
				if (this.hasResult) {
					this.$emit('analyze')
				} else {
					if (!this.canDraw) {
						uni.showToast({ title: '请先选择一个主题或填写自定义问题', icon: 'none' })
						return
					}
					this.$emit('open-draw', {
						tagId: this.selectedTagId,
						customQuestion: this.customQuestion
					})
				}
			},
			toggleThemeTag: function(id) {
				this.selectedTagId = this.selectedTagId === id ? '' : id
			},
			onQuestionInput: function(e) {
				var v = (e.detail && e.detail.value) != null ? e.detail.value : ''
				this.customQuestion = v
			},
			resetDraw: function() {
				try { uni.removeStorageSync('tarotResult') } catch (e) {}
				try { uni.removeStorageSync('tarotIntent') } catch (e) {}
				try { uni.removeStorageSync('tarotDrawId') } catch (e) {}
				this.hasResult = false
				this.drawnCards = []
			}
		}
	}
</script>

<!-- placeholder-class 在部分端需非 scoped -->
<style>
.theme-question-ph {
	color: rgba(95,82,125,0.38);
	font-size: 24rpx;
}
</style>

<style scoped>
	.tarot-wrapper {
		width: 100%;
		border-radius: 32rpx;
		overflow: hidden;
		margin-bottom: 24rpx;
		position: relative;
		background: linear-gradient(
			168deg,
			rgba(255, 255, 255, 0.92) 0%,
			rgba(244, 240, 252, 0.86) 42%,
			rgba(232, 226, 248, 0.82) 100%
		);
		border: 1rpx solid rgba(255, 255, 255, 0.75);
		box-shadow:
			0 10rpx 36rpx rgba(100, 88, 170, 0.09),
			inset 0 1rpx 0 rgba(255, 255, 255, 0.88);
	}
	.tarot-title {
		position: absolute;
		top: 28rpx;
		left: 32rpx;
		font-size: 28rpx;
		font-weight: 700;
		color: #2c2450;
		letter-spacing: 2rpx;
		z-index: 10;
	}

	/* ---- 主题区 ---- */
	.tarot-theme-panel {
		margin: 16rpx 20rpx 0;
		padding: 20rpx 20rpx 22rpx;
		border-radius: 22rpx;
		background: linear-gradient(
			180deg,
			rgba(255, 255, 255, 0.60) 0%,
			rgba(228, 222, 248, 0.50) 100%
		);
		border: 1rpx solid rgba(140, 128, 196, 0.13);
		box-shadow:
			inset 0 1rpx 0 rgba(255, 255, 255, 0.78),
			0 4rpx 18rpx rgba(100, 88, 160, 0.05);
	}
	.theme-head {
		display: flex;
		flex-direction: row;
		align-items: baseline;
		justify-content: space-between;
		margin-bottom: 16rpx;
	}
	.theme-head-title {
		font-size: 26rpx;
		font-weight: 600;
		color: #3c3268;
		letter-spacing: 2rpx;
	}
	.theme-head-meta {
		font-size: 20rpx;
		color: rgba(100, 88, 150, 0.40);
	}
	.theme-tag-grid {
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		column-gap: 10rpx;
		row-gap: 12rpx;
		width: 100%;
		box-sizing: border-box;
	}
	.theme-tag {
		box-sizing: border-box;
		padding: 16rpx 4rpx;
		border-radius: 14rpx;
		text-align: center;
		background: rgba(255, 255, 255, 0.75);
		border: 1rpx solid rgba(140, 128, 196, 0.10);
	}
	.theme-tag--love,
	.theme-tag--work,
	.theme-tag--study {
		background: rgba(255, 255, 255, 0.68);
		border-color: rgba(140, 128, 196, 0.10);
	}
	.theme-tag--on {
		background: linear-gradient(148deg, rgba(130, 118, 186, 0.32), rgba(110, 98, 168, 0.28)) !important;
		border-color: rgba(130, 118, 186, 0.28);
		box-shadow: 0 3rpx 14rpx rgba(100, 88, 160, 0.12);
	}
	.theme-tag-t {
		font-size: 19rpx;
		line-height: 1.3;
		color: #4a4278;
	}
	.theme-tag--on .theme-tag-t {
		color: #2c2450;
		font-weight: 600;
	}
	.theme-tag-hover {
		opacity: 0.9;
	}
	.theme-question-input {
		width: 100%;
		height: 58rpx;
		line-height: 58rpx;
		margin-top: 18rpx;
		padding: 0 22rpx;
		box-sizing: border-box;
		font-size: 24rpx;
		color: #3c3268;
		background: rgba(255, 255, 255, 0.82);
		border-radius: 14rpx;
		border: 1rpx solid rgba(140, 128, 196, 0.12);
	}
	/* ---- 扇形 ---- */
	.stage {
		height: 280rpx;
		margin-top: 72rpx;
		position: relative;
	}
	.card-wrap {
		position: absolute;
		transform-origin: 50% 110%;
	}
	.card-face {
		width: 100%;
		height: 100%;
		background: linear-gradient(168deg, #7870aa 0%, #6560a0 48%, #5a5898 100%);
		border-radius: 8rpx;
		border: 1rpx solid rgba(200, 190, 235, 0.30);
		box-shadow: 0 4rpx 16rpx rgba(80, 70, 140, 0.24);
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.card-frame {
		width: 76%;
		height: 80%;
		border: 1rpx solid rgba(220, 210, 248, 0.20);
		border-radius: 5rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.cat-icon { position: relative; width: 22rpx; height: 22rpx; }
	.head {
		width: 22rpx;
		height: 18rpx;
		background: rgba(220, 212, 248, 0.24);
		border-radius: 50% 50% 42% 42%;
		position: absolute;
		bottom: 0;
		left: 0;
	}
	.ear {
		position: absolute;
		top: 0;
		width: 0;
		height: 0;
		border-left: 6rpx solid transparent;
		border-right: 6rpx solid transparent;
		border-bottom: 8rpx solid rgba(220, 212, 248, 0.24);
	}
	.ear-l { left: 0; }
	.ear-r { right: 0; }

	/* ---- 结果展示 ---- */
	.result-area {
		padding: 76rpx 28rpx 0;
	}
	.result-pos-row {
		display: flex;
		justify-content: center;
		gap: 18rpx;
	}
	.result-col {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.result-card {
		width: 100%;
		height: 256rpx;
		border-radius: 18rpx;
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 14rpx 8rpx;
		box-sizing: border-box;
		box-shadow: 0 8rpx 22rpx rgba(80, 64, 140, 0.14);
	}
	.rc-pos-label {
		margin-top: 14rpx;
		font-size: 20rpx;
		color: rgba(90, 78, 130, 0.50);
		font-weight: 500;
		letter-spacing: 2rpx;
	}
	.rc-c { position: absolute; width: 18rpx; height: 18rpx; }
	.rc-tl { top: 12rpx; left: 12rpx; border-top: 1.5rpx solid rgba(0,0,0,0.08); border-left: 1.5rpx solid rgba(0,0,0,0.08); }
	.rc-tr { top: 12rpx; right: 12rpx; border-top: 1.5rpx solid rgba(0,0,0,0.08); border-right: 1.5rpx solid rgba(0,0,0,0.08); }
	.rc-bl { bottom: 12rpx; left: 12rpx; border-bottom: 1.5rpx solid rgba(0,0,0,0.08); border-left: 1.5rpx solid rgba(0,0,0,0.08); }
	.rc-br { bottom: 12rpx; right: 12rpx; border-bottom: 1.5rpx solid rgba(0,0,0,0.08); border-right: 1.5rpx solid rgba(0,0,0,0.08); }
	.rc-num {
		position: absolute; top: 14rpx; left: 16rpx;
		font-size: 17rpx; font-weight: 700;
		color: rgba(0,0,0,0.14); font-style: italic;
	}
	.rc-ring {
		width: 56rpx; height: 56rpx;
		border-radius: 50%;
		background: rgba(255,255,255,0.46);
		display: flex; align-items: center; justify-content: center;
		margin-bottom: 10rpx;
		box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.06);
	}
	.rc-sym { font-size: 28rpx; color: rgba(0,0,0,0.18); }
	.rc-name {
		font-size: 24rpx; font-weight: 800;
		color: rgba(30,24,60,0.88); letter-spacing: 1.5rpx;
	}
	.rc-desc {
		font-size: 17rpx; color: rgba(60,52,100,0.44);
		margin-top: 5rpx; letter-spacing: 1rpx;
		text-align: center;
	}

	/* ---- 按钮 ---- */
	.btn-row {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin: 28rpx 0 14rpx;
	}
	.draw-btn {
		width: 280rpx;
		height: 72rpx;
		border-radius: 20rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(148deg, #9a8fcb 0%, #8276ba 52%, #7264af 100%);
		box-shadow: 0 6rpx 22rpx rgba(100, 88, 170, 0.24);
		border: 1rpx solid rgba(255, 255, 255, 0.16);
		transition: opacity 0.2s ease, transform 0.18s ease;
	}
	.draw-btn--disabled {
		background: linear-gradient(148deg, #c4bdd6 0%, #b5aec8 52%, #a8a1bc 100%);
		box-shadow: none;
	}
	.draw-btn--disabled .draw-btn-text {
		color: rgba(255,255,255,0.45);
	}
	.draw-btn-hover {
		opacity: 0.88;
	}
	.draw-btn-text {
		font-size: 26rpx;
		color: rgba(255, 255, 255, 0.96);
		font-weight: 600;
		letter-spacing: 2rpx;
	}
	.reset-row {
		display: flex;
		justify-content: center;
		padding-bottom: 28rpx;
	}
	.reset-link {
		font-size: 22rpx;
		color: rgba(130, 118, 186, 0.48);
		font-weight: 400;
	}
	.draw-hint {
		display: block;
		text-align: center;
		font-size: 20rpx;
		color: rgba(180, 168, 210, 0.55);
		margin-top: 10rpx;
		letter-spacing: 1rpx;
		height: 28rpx;
		line-height: 28rpx;
		opacity: 0;
		transition: opacity 0.2s ease;
	}
	.draw-hint--show {
		opacity: 1;
	}
</style>
