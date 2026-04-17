<template>
	<view class="container">
		<!-- 顶部装饰光效 -->
		<view class="top-bg-glow"></view>

		<!-- 顶部问候头 -->
		<view class="home-header">
			<view class="header-left">
				<text class="header-greeting">{{ greeting }}</text>
				<text class="header-date">{{ dateStr }}</text>
			</view>
			<view class="header-avatar">
				<text class="avatar-text">心</text>
			</view>
		</view>

		<!-- 模块 1: 情绪数据 -->
		<home-emotion-card @change-score="handleScoreChange" @open-record="openEmotionOverlay" />

		<!-- 模块 2: 情绪趋势 -->
		<home-trend-chart />

		<!-- 模块 3: 星座运势 -->
		<home-horoscope :horoscope="horoscopeData" @toggle="handleHoroToggle" />

		<!-- 模块 4: 塔罗 -->
		<home-tarot ref="tarotRef" @analyze="handleTarotAnalyze" @open-draw="onOpenTarotDraw" />

		<!-- 塔罗抽卡：全屏遮罩 + 底部弹层（主题与自定义问题已在首页选好并传入） -->
		<tarot-draw-panel
			v-if="showTarotDraw"
			:prefill-tag-id="tarotPrefillTagId"
			:prefill-question="tarotPrefillQuestion"
			@close="onTarotDrawClose"
		/>

		<!-- 底部导航栏 -->
		<custom-tabbar :list="navList" />

	</view>
</template>

<script>
	import homeEmotionCard from '@/components/home-emotion-card/home-emotion-card.vue'
	import homeTrendChart from '@/components/home-trend-chart/home-trend-chart.vue'
	import homeHoroscope from '@/components/home-horoscope/home-horoscope.vue'
	import homeTarot from '@/components/home-tarot/home-tarot.vue'
	import customTabbar from '@/components/custom-tabbar/custom-tabbar.vue'
	import tarotDrawPanel from '@/components/tarot-draw-panel/tarot-draw-panel.vue'

	export default {
		components: {
			homeEmotionCard,
			homeTrendChart,
			homeHoroscope,
			homeTarot,
			customTabbar,
			tarotDrawPanel
		},
		computed: {
			greeting: function() {
				var h = new Date().getHours()
				if (h < 6) return '夜深了，好好休息'
				if (h < 11) return '早上好'
				if (h < 13) return '中午好'
				if (h < 18) return '下午好'
				return '晚上好'
			},
			dateStr: function() {
				var d = new Date()
				var days = ['日', '一', '二', '三', '四', '五', '六']
				return (d.getMonth() + 1) + '月' + d.getDate() + '日 · 周' + days[d.getDay()]
			}
		},
		data() {
			return {
				showTarotDraw: false,
				tarotPrefillTagId: '',
				tarotPrefillQuestion: '',
				horoscopeData: {
					name: '天蝎座',
					status: '你今天运势开挂啦〜〜',
					summary: '影子总结',
					ratings: [
						{ label: '综合', val: 4 },
						{ label: '爱情', val: 5 },
						{ label: '工作', val: 4 },
						{ label: '财富', val: 4 }
					],
					desc: '今天要把钱包看紧一点，这是最重要的。另外，很多事可能会有所延迟，要保持一个平常心对待，不要着急去判断它的好与坏，每件事都有它的两面性。今天的直觉非常准，在面对复杂的人际关系时，不妨多听听内心的声音。'
				},
				navList: [
					{ label: '首页', active: true, path: '/pages/index/index' },
					{ label: '探索', active: false, path: '/pages/explore/explore' },
					{ label: '影子', active: false, path: '/pages/shadow/shadow' },
					{ label: '我的', active: false, path: '/pages/profile/profile' }
				]
			}
		},
		onShow: function() {
			this.refreshTarot()
		},
		methods: {
			openEmotionOverlay() {
				uni.navigateTo({
					url: '/pages/emotion-record/emotion-record'
				});
			},
			handleScoreChange() {
				console.log('User changes emotion score');
			},
			handleHoroToggle(expanded) {
				console.log('Horoscope expanded:', expanded);
			},
			refreshTarot: function() {
				if (this.$refs.tarotRef && this.$refs.tarotRef.checkDrawn) {
					this.$refs.tarotRef.checkDrawn()
				}
			},
			onOpenTarotDraw: function(payload) {
				var p = payload || {}
				this.tarotPrefillTagId = p.tagId || ''
				this.tarotPrefillQuestion = typeof p.customQuestion === 'string' ? p.customQuestion : ''
				this.showTarotDraw = true
			},
			onTarotDrawClose: function() {
				this.showTarotDraw = false
				this.refreshTarot()
			},
			handleTarotAnalyze: function() {
				var resultRaw = ''
				var intentRaw = ''
				try { resultRaw = uni.getStorageSync('tarotResult') || '' } catch (e) {}
				try { intentRaw = uni.getStorageSync('tarotIntent') || '' } catch (e) {}

				var cards = []
				var intent = {}
				try { cards = JSON.parse(resultRaw) } catch (e) {}
				try { intent = JSON.parse(intentRaw) } catch (e) {}

				if (!cards || cards.length < 3) {
					uni.showToast({ title: '未找到抽牌结果', icon: 'none' })
					return
				}

				try {
					uni.setStorageSync('shadowTarotSession', JSON.stringify({
						cards: cards,
						intent: intent
					}))
				} catch (e) {}

				uni.navigateTo({ url: '/pages/shadow/shadow' })
			}
		}
	}
</script>

<style scoped>
	.container {
		padding: 35rpx;
		background: linear-gradient(180deg, #ede9f7 0%, #e4dff2 25%, #d8d1ec 55%, #c8c2de 100%);
		min-height: 100vh;
		padding-bottom: 240rpx;
		position: relative;
		overflow-x: hidden;
	}

	.top-bg-glow {
		position: absolute;
		top: -60rpx;
		left: -20%;
		width: 140%;
		height: 600rpx;
		background: radial-gradient(ellipse at 50% 20%, rgba(255,255,255,0.36) 0%, transparent 62%);
		pointer-events: none;
		z-index: 0;
	}

	/* 问候头部 */
	.home-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 28rpx;
		position: relative;
		z-index: 1;
	}
	.header-left {
		display: flex;
		flex-direction: column;
		gap: 6rpx;
	}
	.header-greeting {
		font-size: 36rpx;
		font-weight: 700;
		color: #2c2450;
		letter-spacing: 1rpx;
	}
	.header-date {
		font-size: 22rpx;
		color: rgba(90, 78, 130, 0.58);
		font-weight: 400;
	}
	.header-avatar {
		width: 72rpx;
		height: 72rpx;
		border-radius: 50%;
		background: linear-gradient(148deg, rgba(255,255,255,0.90) 0%, rgba(220,214,244,0.80) 100%);
		border: 1.5rpx solid rgba(255,255,255,0.7);
		box-shadow: 0 4rpx 18rpx rgba(100,88,160,0.10);
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.avatar-text {
		font-size: 30rpx;
		color: #7264af;
		font-weight: 700;
	}
</style>
