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
		<home-emotion-card :emo-val="emoVal" :vit-val="vitVal" :updated-today="updatedToday" @change-score="handleScoreChange" @open-record="openEmotionOverlay" />

		<!-- 模块 2: 情绪趋势 -->
		<home-trend-chart :trend-data="trendData" @summary="handleTrendSummary" />

		<!-- 模块 3: 星座运势 -->
		<home-horoscope ref="horoscopeRef" :horoscope="horoscopeData" @toggle="handleHoroToggle" @summary="handleHoroSummary" />

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
	import { getDailyFortune } from '@/utils/api'

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
				emoVal: 60,
				vitVal: 60,
				updatedToday: false,
				trendData: [],
				horoscopeData: {
					name: '天蝎座',
					status: '你今天运势开挂啦～～',
					summary: '影子总结',
					ratings: [
						{ label: '综合', val: 4 },
						{ label: '爱情', val: 5 },
						{ label: '工作', val: 4 },
						{ label: '财富', val: 4 }
					],
					desc: ''
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
			this.loadFortune()
			this.loadEmotionData()
		},
		methods: {
			loadEmotionData: function() {
				var self = this
				var today = new Date()
				var todayKey = today.getFullYear() + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + String(today.getDate()).padStart(2, '0')

				// 1) 读取本地快照
				var snapshot = null
				try { snapshot = JSON.parse(uni.getStorageSync('shadowEmotionSnapshot') || '') } catch (e) {}

				if (snapshot && snapshot.mood != null) {
					// 快照存在且是今天的
					var snapDate = ''
					if (snapshot.savedAt) {
						var sd = new Date(snapshot.savedAt)
						snapDate = sd.getFullYear() + '-' + String(sd.getMonth() + 1).padStart(2, '0') + '-' + String(sd.getDate()).padStart(2, '0')
					}
					if (!snapDate || snapDate === todayKey) {
						self.emoVal = Math.round(snapshot.mood)
						self.vitVal = Math.round(snapshot.vit)
						self.updatedToday = true
					}
				}

				// 2) 读取本地历史 → 构建15日趋势
				var hist = {}
				try { hist = JSON.parse(uni.getStorageSync('shadowEmotionHistory') || '{}') } catch (e) {}

				// 如果快照没命中今天，尝试从历史记录中取
				if (!self.updatedToday && hist[todayKey]) {
					self.emoVal = hist[todayKey].mood || 60
					self.vitVal = hist[todayKey].vit || 60
					self.updatedToday = true
				}

				// 构建15天趋势数据
				var trendArr = []
				for (var i = 14; i >= 0; i--) {
					var d = new Date(today)
					d.setDate(d.getDate() - i)
					var key = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
					var label = (d.getMonth() + 1) + '/' + d.getDate()
					var rec = hist[key]
					if (rec) {
						// 有数据：情绪*60% + 活力*40%
						var mood = rec.mood != null ? rec.mood : 60
						var vit = rec.vit != null ? rec.vit : 60
						var score = Math.round(mood * 0.6 + vit * 0.4)
						trendArr.push({ d: label, s: score })
					} else {
						// 无数据：默认60
						trendArr.push({ d: label, s: 60 })
					}
				}
				self.trendData = trendArr

				// 3) 尝试远程API补充（不覆盖本地已有数据）
				var openid = ''
				try { openid = uni.getStorageSync('xinyu_openid') || uni.getStorageSync('openid') || '' } catch (e) {}
				if (openid) {
					var baseUrl = 'http://43.143.169.226'
					try {
						if (typeof process !== 'undefined' && process.env && (process.env.VUE_APP_XINYU_API_BASE || process.env.UNI_XINYU_API_BASE)) {
							baseUrl = (process.env.VUE_APP_XINYU_API_BASE || process.env.UNI_XINYU_API_BASE).replace(/\/$/, '')
						}
					} catch (e2) {}
					uni.request({
						url: baseUrl + '/emotion?openid=' + encodeURIComponent(openid),
						method: 'GET',
						timeout: 8000,
						success: function(res) {
							var d = res && res.data
							if (!d || d.code !== 200 || !Array.isArray(d.data) || d.data.length === 0) return
							var records = d.data
							// 远程数据按日期建索引
							var remoteMap = {}
							for (var j = 0; j < records.length; j++) {
								var r = records[j]
								if (r.date) remoteMap[r.date] = r
							}
							// 如果今天没有本地数据，用远程数据
							if (!self.updatedToday && remoteMap[todayKey]) {
								var todayRec = remoteMap[todayKey]
								self.emoVal = todayRec.score || 60
								self.vitVal = todayRec.vitality != null ? todayRec.vitality : 60
								self.updatedToday = true
							}
							// 补充趋势中本地没有的日期
							var newTrend = []
							for (var k = 14; k >= 0; k--) {
								var dd = new Date(today)
								dd.setDate(dd.getDate() - k)
								var dk = dd.getFullYear() + '-' + String(dd.getMonth() + 1).padStart(2, '0') + '-' + String(dd.getDate()).padStart(2, '0')
								var dl = (dd.getMonth() + 1) + '/' + dd.getDate()
								var localRec = hist[dk]
								var remoteRec = remoteMap[dk]
								if (localRec) {
									var mm = localRec.mood != null ? localRec.mood : 60
									var vv = localRec.vit != null ? localRec.vit : 60
									newTrend.push({ d: dl, s: Math.round(mm * 0.6 + vv * 0.4) })
								} else if (remoteRec) {
									var em2 = remoteRec.score || 60
									var vi2 = remoteRec.vitality != null ? remoteRec.vitality : 60
									newTrend.push({ d: dl, s: Math.round(em2 * 0.6 + vi2 * 0.4) })
								} else {
									newTrend.push({ d: dl, s: 60 })
								}
							}
							self.trendData = newTrend
						}
					})
				}
			},
			loadFortune: function() {
				var self = this
				getDailyFortune().then(function(data) {
					if (data && data.sign) {
						self.horoscopeData = {
							name: data.sign || self.horoscopeData.name,
							status: data.status || self.horoscopeData.status,
							ratings: data.ratings || self.horoscopeData.ratings,
							desc: ''
						}
						// 更新组件内部的 tabs 数据
						if (self.$refs.horoscopeRef && data.tabs && Array.isArray(data.tabs)) {
							self.$refs.horoscopeRef.tabs = data.tabs
						}
					}
				}).catch(function(err) {
					console.warn('[fortune] 运势获取失败，使用默认数据:', err)
				})
			},
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
			handleHoroSummary() {
				// 构造星座运势专项数据
				var horoData = this.horoscopeData || {}
				var tabs = (this.$refs.horoscopeRef && this.$refs.horoscopeRef.tabs) || []
				var fortuneText = ''
				for (var i = 0; i < tabs.length; i++) {
					fortuneText += tabs[i].label + '：' + tabs[i].content + '\n'
				}
				var specialistSession = {
					category: 'ZODIAC',
					question: '帮我解读一下今天的星座运势',
					specialistData: {
						sign: horoData.name || '',
						status: horoData.status || '',
						ratings: horoData.ratings || [],
						fortune_text: fortuneText.trim()
					}
				}
				try {
					uni.setStorageSync('shadowSpecialistSession', JSON.stringify(specialistSession))
				} catch (e) {}
				uni.navigateTo({ url: '/pages/shadow/shadow' })
			},
			handleTrendSummary() {
				// 构造情绪记录专项数据
				var specialistSession = {
					category: 'EMOTION_LOG',
					question: '帮我分析一下最近的心情变化',
					specialistData: {
						mood: this.emoVal,
						vitality: this.vitVal,
						trend: this.trendData
					}
				}
				try {
					uni.setStorageSync('shadowSpecialistSession', JSON.stringify(specialistSession))
				} catch (e) {}
				uni.navigateTo({ url: '/pages/shadow/shadow' })
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
		width: 100%;
		box-sizing: border-box;
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
		padding-top: env(safe-area-inset-top);
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
