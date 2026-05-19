<template>
	<view class="tabbar-float">
		<view class="tabbar-inner">
			<view v-for="(item, index) in localList" :key="index"
				class="tab-item" :class="{ active: item.active }"
				@tap="switchTab(index)">
				<view class="tab-icon">
					<view class="tab-icon-shell" :class="item.iconCls">
						<view class="icon-core"></view>
					</view>
				</view>
				<text class="tab-label">{{ item.label }}</text>
				<view class="tab-line" v-if="item.active"></view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		name: "custom-tabbar",
		props: {
			list: {
				type: Array,
				default: function() {
					return [
						{ label: '首页', active: true, path: '/pages/index/index' },
						{ label: '探索', active: false, path: '/pages/explore/explore' },
						{ label: '影子', active: false, path: '/pages/shadow/shadow' },
						{ label: '我的', active: false, path: '/pages/profile/profile' }
					]
				}
			}
		},
		data: function() {
			return {
				localList: [],
				iconNames: ['home', 'explore', 'shadow', 'profile']
			}
		},
		mounted: function() {
			var self = this
			this.localList = JSON.parse(JSON.stringify(this.list)).map(function(item, index) {
				item.iconCls = 'icon-' + self.iconNames[index]
				return item
			})
		},
		methods: {
			switchTab: function(index) {
				var target = this.localList[index]
				if (target.active) return
				this.localList = this.localList.map(function(item, i) {
					return Object.assign({}, item, { active: i === index })
				})
				uni.reLaunch({ url: target.path })
			}
		}
	}
</script>

<style scoped>
	.tabbar-float {
		position: fixed;
		bottom: 0;
		left: 0;
		width: 100%;
		padding: 0 0 calc(10rpx + env(safe-area-inset-bottom)) 0;
		display: flex;
		justify-content: center;
		z-index: 1000;
		pointer-events: none;
	}
	.tabbar-inner {
		pointer-events: auto;
		width: 78%;
		display: flex;
		justify-content: space-around;
		align-items: center;
		padding: 14rpx 8rpx 12rpx;
		border-radius: 48rpx;
		background: rgba(255,255,255,0.9);
		box-shadow:
			0 10rpx 30rpx rgba(80,60,130,0.12),
			0 2rpx 8rpx rgba(80,60,130,0.05),
			inset 0 1rpx 0 rgba(255,255,255,0.85);
		border: 1rpx solid rgba(255,255,255,0.72);
		backdrop-filter: blur(18px);
	}
	.tab-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		position: relative;
		padding: 4rpx 0;
		min-width: 100rpx;
	}
	.tab-icon {
		width: 60rpx;
		height: 52rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 2rpx;
		border-radius: 18rpx;
		transition: background 0.25s ease, transform 0.25s ease;
	}
	.tab-item.active .tab-icon {
		background: linear-gradient(180deg, rgba(114,96,160,0.12), rgba(114,96,160,0.03));
		transform: translateY(-1rpx);
	}
	.tab-icon-shell {
		position: relative;
		width: 42rpx;
		height: 42rpx;
		color: #aba2be;
		transition: color 0.25s ease, transform 0.25s ease;
	}
	.tab-item.active .tab-icon-shell {
		color: #574a7b;
		transform: translateY(-1rpx);
	}
	.tab-icon-shell::before,
	.tab-icon-shell::after,
	.tab-icon-shell .icon-core,
	.tab-icon-shell .icon-core::after {
		content: '';
		position: absolute;
		box-sizing: border-box;
	}

	.icon-home::before {
		left: 12rpx;
		top: 8rpx;
		width: 18rpx;
		height: 18rpx;
		border-left: 3rpx solid currentColor;
		border-top: 3rpx solid currentColor;
		transform: rotate(45deg);
		border-top-left-radius: 6rpx;
	}
	.icon-home .icon-core {
		left: 9rpx;
		bottom: 7rpx;
		width: 24rpx;
		height: 16rpx;
		border: 3rpx solid currentColor;
		border-top: none;
		border-radius: 0 0 7rpx 7rpx;
	}
	.icon-home .icon-core::after {
		left: 7rpx;
		bottom: -3rpx;
		width: 7rpx;
		height: 10rpx;
		border: 3rpx solid currentColor;
		border-bottom: none;
		border-radius: 5rpx 5rpx 0 0;
	}

	.icon-explore::before {
		left: 8rpx;
		top: 8rpx;
		width: 26rpx;
		height: 26rpx;
		border: 3rpx solid currentColor;
		border-radius: 50%;
	}
	.icon-explore .icon-core {
		left: 20rpx;
		top: 10rpx;
		width: 3rpx;
		height: 14rpx;
		background: currentColor;
		border-radius: 99rpx;
		transform: rotate(42deg);
		transform-origin: 50% 100%;
	}
	.icon-explore .icon-core::after {
		left: -2rpx;
		top: 13rpx;
		width: 7rpx;
		height: 7rpx;
		background: currentColor;
		border-radius: 50%;
	}

	.icon-shadow::before {
		left: 9rpx;
		top: 8rpx;
		width: 22rpx;
		height: 22rpx;
		border: 3rpx solid currentColor;
		border-right-color: transparent;
		border-top-color: transparent;
		border-radius: 50%;
		transform: rotate(38deg);
	}
	.icon-shadow .icon-core {
		right: 8rpx;
		top: 9rpx;
		width: 5rpx;
		height: 5rpx;
		background: currentColor;
		border-radius: 50%;
		box-shadow:
			-7rpx 9rpx 0 -1rpx currentColor,
			3rpx 12rpx 0 -2rpx currentColor;
	}

	.icon-profile::before {
		left: 13rpx;
		top: 7rpx;
		width: 16rpx;
		height: 16rpx;
		border: 3rpx solid currentColor;
		border-radius: 50%;
	}
	.icon-profile .icon-core {
		left: 8rpx;
		bottom: 6rpx;
		width: 26rpx;
		height: 13rpx;
		border: 3rpx solid currentColor;
		border-top: none;
		border-radius: 0 0 14rpx 14rpx;
	}
	.tab-label {
		font-size: 20rpx;
		font-weight: 500;
		color: #a9a0bc;
		transition: color 0.25s;
		letter-spacing: 1rpx;
	}
	.tab-item.active .tab-label {
		color: #4f436f;
		font-weight: 700;
	}
.tab-line {
	position: absolute;
	bottom: -4rpx;
	width: 34rpx;
	height: 4rpx;
	border-radius: 4rpx;
	background: linear-gradient(90deg, #6f61a1, #57497d);
}
/* trigger-rebuild */
</style>
