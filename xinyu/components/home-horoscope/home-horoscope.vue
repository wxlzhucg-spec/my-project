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
						status: '今天慢慢来，一切刚刚好',
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
						content: '今天的节奏偏柔和，不用急着赶路。上午可能会有一些小琐碎找上门，不过别烦，一件件来就好。下午状态会慢慢回来，适合做一些需要耐心的事。晚上给自己留一点独处的时间，你会觉得这一天其实挺充实的。'
					},
					{
						label: '感情运势',
						content: '不管身边有没有人，今天都值得好好照顾自己的感受。如果心里有话想对某个人说，白天比晚上更适合开口。单身的朋友不用刻意寻找什么，做让自己舒服的事，吸引力自然会来。'
					},
					{
						label: '工作运势',
						content: '今天工作上的节奏不快不慢，正好适合查漏补缺。之前搁置的小事可以顺手处理掉，清完之后心里会踏实很多。如果遇到拿不准的决定，不用今天一定给答案，放一放反而更清晰。'
					},
					{
						label: '财富运势',
						content: '今天花钱前多想一秒就够了，不需要太紧张。如果有固定的账单或转账，上午处理完会更安心。小额的消费可以随心，但大额的决定再等一天也不迟。'
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
		created: function() {
			this.collapseTimer = null
		},
		beforeDestroy: function() {
			if (this.collapseTimer) {
				clearTimeout(this.collapseTimer)
				this.collapseTimer = null
			}
		},
		methods: {
			switchTab: function(idx) {
				this.activeTab = idx
			},
			toggleExpand: function() {
				this.expanded = !this.expanded
				if (this.collapseTimer) {
					clearTimeout(this.collapseTimer)
					this.collapseTimer = null
				}
				if (this.expanded) {
					var self = this
					this.collapseTimer = setTimeout(function() {
						self.expanded = false
						self.collapseTimer = null
					}, 15000)
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
		transition: max-height 0.35s ease;
	}
	.content-text.collapsed {
		max-height: 120rpx;
	}
	.content-text:not(.collapsed) {
		max-height: 800rpx;
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
		transition: opacity 0.3s ease;
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
