<template>
	<view class="card">
		<!-- 头部 -->
		<view class="card-header">
			<view class="title-row">
				<text class="horo-name">{{ horoscope.name }}</text>
				<text class="horo-sub">{{ horoscope.status }}</text>
			</view>
			<view class="tag-btn" @tap="$emit('summary')">
				<text class="tag-text">影子总结</text>
			</view>
		</view>

		<!-- 星级评分 -->
		<view class="stars-grid">
			<view class="star-col" v-for="(item, idx) in starList" :key="idx">
				<text class="star-cat">{{ item.label }}</text>
				<text class="star-icons">{{ item.icons }}</text>
			</view>
		</view>

		<!-- 内容标签 -->
		<view class="tab-bar">
			<view v-for="(tab, idx) in tabs" :key="idx"
				class="tab-item" :class="{ active: activeTab === idx }"
				@tap="switchTab(idx)">
				<text class="tab-text" :class="{ active: activeTab === idx }">{{ tab.label }}</text>
			</view>
		</view>

		<!-- 运势内容（可折叠 + 半透明渐隐） -->
		<view class="content-wrap">
			<view class="content-text" :class="{ collapsed: !expanded }">
				<text class="body-text">{{ tabs[activeTab].content }}</text>
			</view>
			<view v-if="!expanded" class="fade-mask"></view>
		</view>

		<!-- 展开/收起 -->
		<view class="expand-row" @tap="toggleExpand">
			<text class="expand-label">{{ expanded ? '收起' : '展开全部' }}</text>
			<view class="expand-chevron" :class="{ 'expand-chevron--up': expanded }">
				<view class="chevron-shape"></view>
			</view>
		</view>
	</view>
</template>

<script>
	function makeStars(val) {
		var s = ''
		for (var i = 0; i < 5; i++) s += (i < val ? '★' : '☆')
		return s
	}

	export default {
		name: "home-horoscope",
		props: {
			horoscope: {
				type: Object,
				default: function() {
					return {
						name: '天蝎座',
						status: '你今天运势开挂啦～～',
						ratings: [
							{ label: '综合', val: 4 },
							{ label: '爱情', val: 5 },
							{ label: '工作', val: 4 },
							{ label: '财富', val: 4 }
						]
					}
				}
			}
		},
		data: function() {
			return {
				activeTab: 0,
				expanded: false,
				tabs: [
					{
						label: '综合运势',
						content: '今天要把钱包看紧一点，这是最重要的。另外，很多事可能会有所延迟，要保持一颗平常心对待，不要着急去判断它的好与坏，每件事都有它的两面性。今天的直觉非常准，在面对复杂的人际关系时，不妨多听听内心的声音。整体来看今天适合做一些长远规划，而不是追求即时的回报。'
					},
					{
						label: '感情运势',
						content: '单身的朋友今天桃花运不错，可能在社交场合遇到让你心动的人。有伴侣的则适合来一次深度对话，聊聊彼此最近的感受。今天的沟通氛围特别好，平时不好意思说的话，现在可以自然地表达出来。不要害怕展示脆弱的一面，真实的情感交流才能拉近距离。'
					},
					{
						label: '工作运势',
						content: '工作上可能会收到一些延迟的反馈，不要因此感到焦虑。今天适合整理手头的项目，把之前积攒的细节问题一一处理。团队协作方面会有不错的进展，同事之间的配合比较默契。如果有新的想法，可以先记录下来，等到下周再正式提出。'
					},
					{
						label: '财富运势',
						content: '今天在财务方面需要格外谨慎，避免冲动消费和投资决策。如果有人向你推荐"稳赚不赔"的机会，务必保持警惕。日常开销方面倒是可以适当犒劳自己，但大额支出建议再考虑几天。整体财运平稳，适合做预算和理财规划。'
					}
				]
			}
		},
		computed: {
			starList: function() {
				var ratings = this.horoscope.ratings || []
				var list = []
				for (var i = 0; i < ratings.length; i++) {
					list.push({
						label: ratings[i].label,
						icons: makeStars(ratings[i].val)
					})
				}
				return list
			}
		},
		methods: {
			switchTab: function(idx) {
				this.activeTab = idx
				this.expanded = false
			},
			toggleExpand: function() {
				this.expanded = !this.expanded
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

	/* 头部 */
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 28rpx;
	}
	.title-row {
		display: flex;
		align-items: baseline;
		flex: 1;
		overflow: hidden;
	}
	.horo-name {
		font-size: 34rpx;
		font-weight: 800;
		color: #2c2450;
		flex-shrink: 0;
	}
	.horo-sub {
		font-size: 26rpx;
		color: #7264af;
		margin-left: 14rpx;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.tag-btn {
		flex-shrink: 0;
		margin-left: 16rpx;
		padding: 10rpx 22rpx;
		border-radius: 24rpx;
		border: 1rpx solid rgba(130,118,186,0.14);
		background: rgba(130,118,186,0.07);
	}
	.tag-text {
		font-size: 22rpx;
		color: #7264af;
		font-weight: 500;
	}

	/* 星级 */
	.stars-grid {
		display: flex;
		justify-content: space-between;
		margin-bottom: 28rpx;
		background: rgba(130,118,186,0.05);
		border-radius: 18rpx;
		padding: 16rpx 8rpx;
	}
	.star-col {
		display: flex;
		flex-direction: column;
		align-items: center;
		flex: 1;
	}
	.star-cat {
		font-size: 22rpx;
		color: #9088b8;
		margin-bottom: 10rpx;
	}
	.star-icons {
		font-size: 20rpx;
		color: #b89848;
		letter-spacing: 3rpx;
	}

	/* 标签栏 */
	.tab-bar {
		display: flex;
		gap: 12rpx;
		margin-bottom: 24rpx;
	}
	.tab-item {
		flex: 1;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 16rpx;
		background: rgba(130,118,186,0.07);
		transition: background 0.2s;
	}
	.tab-item.active {
		background: #8276ba;
	}
	.tab-text {
		font-size: 22rpx;
		color: #9088b8;
		font-weight: 500;
	}
	.tab-text.active {
		color: #ffffff;
	}

	/* 内容区 */
	.content-wrap {
		position: relative;
		margin-bottom: 20rpx;
	}
	.content-text {
		overflow: hidden;
	}
	.content-text.collapsed {
		max-height: 120rpx;
	}
	.body-text {
		font-size: 26rpx;
		color: #48407a;
		line-height: 1.7;
	}
	.fade-mask {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 80rpx;
		background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,0.88) 100%);
		pointer-events: none;
	}

	/* 展开按钮 */
	.expand-row {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 10rpx;
		padding-top: 20rpx;
	}
	.expand-label {
		font-size: 24rpx;
		color: #8276ba;
		font-weight: 500;
	}
	.expand-chevron {
		width: 32rpx;
		height: 32rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: transform 0.25s;
	}
	.expand-chevron--up {
		transform: rotate(180deg);
	}
	.chevron-shape {
		width: 14rpx;
		height: 14rpx;
		border-right: 2.5rpx solid #8276ba;
		border-bottom: 2.5rpx solid #8276ba;
		transform: rotate(45deg) translateY(-3rpx);
	}
</style>
