<template>
	<view class="container">
		<!-- 顶部装饰光 -->
		<view class="top-glow"></view>

		<!-- 顶部导航 -->
		<view class="nav-header" :style="{ paddingTop: statusBarHeight + 'px' }">
			<view class="nav-back" v-if="fromTarot" @tap="goBack"><text class="nav-back-t">‹</text></view>
			<text class="page-title">{{ tarotReading ? '塔罗解读' : '影子' }}</text>
		</view>

		<!-- 聊天区域 -->
		<scroll-view 
			class="chat-scroll" 
			scroll-y="true" 
			:scroll-into-view="scrollToMessage"
			:style="{ paddingTop: `calc(${statusBarHeight}px + 44px + 10rpx)`, paddingBottom: bottomPadding }"
		>
			<view class="chat-list" :class="{ 'chat-list--landing': showLanding }">
				<view v-if="showLanding" class="welcome-panel">
					<view class="landing-hero-card">
						<view class="landing-mascot-wrap" :style="{ transform: landingMascotTf }">
							<svg class="landing-mascot" fill="none" viewBox="0 0 241.376 188.924">
								<defs>
									<mask id="body-mask-shadow" maskUnits="userSpaceOnUse" style="mask-type:alpha">
										<path d="M148.652 0C182.792 0.000197914 210.468 27.6759 210.468 61.8154C210.468 65.0652 210.216 68.2567 209.732 71.3711C228.627 82.089 241.376 102.386 241.376 125.66C241.376 158.482 215.946 185.714 183.158 187.199C162.354 188.141 139.439 188.924 120.688 188.924C101.936 188.924 79.0222 188.141 58.2178 187.199C25.4299 185.714 0 158.482 0 125.66C0 100.709 14.651 79.1799 35.8194 69.2061C35.4947 67.2817 35.3233 65.3048 35.3233 63.2881C35.3233 43.7796 51.138 27.9648 70.6465 27.9648C78.9593 27.9648 86.6002 30.8374 92.6338 35.6426C102.489 14.5861 123.868 0 148.652 0Z" fill="white"/>
									</mask>
									<filter id="body-glow-filter-shadow" x="-40%" y="-30%" width="180%" height="160%" filterUnits="objectBoundingBox" color-interpolation-filters="sRGB">
										<feFlood flood-opacity="0" result="BackgroundImageFix"/>
										<feBlend in="SourceGraphic" in2="BackgroundImageFix" mode="normal" result="shape"/>
										<feGaussianBlur stdDeviation="16"/>
									</filter>
									<radialGradient id="body-grad-shadow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(125.451 107.208) rotate(90) scale(90.37 111.98)">
										<stop offset="0.22" :stop-color="landingRgbStr(landingGradRGB)"/>
										<stop offset="1" :stop-color="landingRgbStr(landingGradRGB)" stop-opacity="0.72"/>
									</radialGradient>
								</defs>

								<g mask="url(#body-mask-shadow)">
									<g filter="url(#body-glow-filter-shadow)">
										<ellipse cx="125.451" cy="107.208" rx="111.979" ry="90.3693" fill="url(#body-grad-shadow)"/>
									</g>
									<rect x="-5" y="-5" width="252" height="200" :fill="landingRgbStr(landingTintRGBA)" :opacity="landingTintRGBA[3]"></rect>
								</g>

								<path d="M218 154 C222 152 227 145 228 138" :stroke="'rgba(206,196,255,' + landingSparkA.toFixed(2) + ')'" stroke-linecap="round" stroke-width="5.2" fill="none"/>
								<path d="M29 89 C26 90 22 95 21 100" :stroke="'rgba(206,196,255,' + landingSparkA.toFixed(2) + ')'" stroke-linecap="round" stroke-width="5.2" fill="none"/>

								<g :transform="'translate(0 ' + landingFaceOY.toFixed(1) + ')'">
									<path :d="buildQuadPath(landingBrowLP)" stroke="#3d3952" stroke-width="3.5" stroke-linecap="round" fill="none" opacity="0.72"/>
									<path :d="buildQuadPath(landingBrowRP)" stroke="#3d3952" stroke-width="3.5" stroke-linecap="round" fill="none" opacity="0.72"/>

									<ellipse cx="96" cy="99" rx="7" :ry="landingEyeR.toFixed(2)" fill="#2d2a3d"/>
									<ellipse :cx="94.6" :cy="99 - landingEyeR * 0.30" :rx="2.3" :ry="(landingEyeR * 0.30).toFixed(2)" fill="white" opacity="0.84"/>
									<ellipse cx="146" cy="99" rx="7" :ry="landingEyeR.toFixed(2)" fill="#2d2a3d"/>
									<ellipse :cx="144.6" :cy="99 - landingEyeR * 0.30" :rx="2.3" :ry="(landingEyeR * 0.30).toFixed(2)" fill="white" opacity="0.84"/>

									<g :opacity="landingBlushA.toFixed(3)">
										<ellipse cx="70" cy="110" rx="12.2" ry="5.2" fill="#FF8BAB" opacity="0.48" transform="rotate(-8, 70, 110)"/>
										<ellipse cx="172" cy="110" rx="12.2" ry="5.2" fill="#FF8BAB" opacity="0.48" transform="rotate(8, 172, 110)"/>
									</g>

									<g :opacity="landingTearA.toFixed(3)">
										<path d="M96 112 Q92 121 94 129 Q96 137 98 129 Q100 121 96 112Z" fill="#99CCFF" opacity="0.72"/>
										<path d="M146 112 Q142 121 144 129 Q146 137 148 129 Q150 121 146 112Z" fill="#99CCFF" opacity="0.72"/>
									</g>

									<path :d="buildQuadPath(landingMouthP)" fill="none" stroke="#343142" stroke-width="4.9" stroke-linecap="round"/>
								</g>
							</svg>
						</view>
						<text class="landing-caption">{{ emotionCaption }}</text>
					</view>
					<view class="landing-copy">
						<text class="landing-title">今天想聊点什么？</text>
						<text class="landing-subtitle">把脑海里绕来绕去的念头交给我，我们慢慢理顺。</text>
					</view>
				</view>

				<!-- 塔罗解读：用户问题 -->
				<view v-if="tarotReading" class="tarot-q-wrap">
					<view class="tarot-q-bubble">
						<text class="tarot-q-text">{{ tarotReading.questionText }}</text>
					</view>
				</view>

				<!-- 塔罗解读：结果卡片 -->
				<view v-if="tarotReading" class="tarot-reading-card">
					<view class="trc-head">
						<view class="trc-icon-ring">
							<text class="trc-icon-glyph">✦</text>
						</view>
						<view class="trc-head-text">
							<text class="trc-head-title">使用你选择的智慧卡解答</text>
							<text class="trc-head-sub">结果为系统抽取，若与你心意不符，可继续追问</text>
						</view>
					</view>

					<!-- 三张牌 -->
					<view class="trc-cards-strip">
						<view
							v-for="(card, ci) in tarotReading.cards"
							:key="'trc' + ci"
							class="trc-card-col"
						>
							<view class="trc-card" :style="{ background: card.bg }">
								<text class="trc-card-num">{{ card.num }}</text>
								<view class="trc-card-ring"><text class="trc-card-sym">{{ card.symbol }}</text></view>
								<text class="trc-card-name-inner">{{ card.name }}</text>
							</view>
							<text class="trc-card-label">{{ card.displayName }}</text>
						</view>
					</view>

					<!-- 分隔 -->
					<view class="trc-divider"></view>

					<!-- 解读段落 -->
					<view class="trc-reading-body">
						<view
							v-for="(item, idx) in tarotReading.sections"
							:key="'trs' + idx"
							class="trc-section"
						>
							<text class="trc-section-title">{{ item.title }}</text>
							<text class="trc-section-content">{{ item.content }}</text>
						</view>
					</view>

					<!-- 底部工具条 -->
					<view class="trc-tools">
						<view class="trc-tool-chip" hover-class="trc-tool-hover">
							<text class="trc-tool-emoji">💬</text>
							<text class="trc-tool-text">继续追问</text>
						</view>
						<view class="trc-tool-chip" hover-class="trc-tool-hover">
							<text class="trc-tool-emoji">🫧</text>
							<text class="trc-tool-text">情绪连接</text>
						</view>
						<view class="trc-tool-chip" hover-class="trc-tool-hover">
							<text class="trc-tool-emoji">📊</text>
							<text class="trc-tool-text">聊天分析</text>
						</view>
					</view>
				</view>

				<!-- 普通消息 -->
				<view
					v-if="!showLanding"
					v-for="(msg, index) in messageList" 
					:key="index"
					:id="'msg-' + index"
					class="message-row"
					:class="msg.role === 'user' ? 'row-user' : 'row-ai'"
				>
					<view v-if="msg.role === 'ai'" class="avatar ai-avatar">
						<text class="ai-avatar-t">影</text>
					</view>
					
					<view class="message-main" :class="msg.role === 'user' ? 'message-main--user' : 'message-main--ai'">
						<text v-if="msg.role === 'ai'" class="message-role">影子</text>
						<text class="message-text">{{ msg.content }}</text>
					</view>
					
					<view v-if="msg.role === 'user'" class="avatar user-avatar">
						<image src="/static/default-avatar.png" mode="aspectFill"></image>
					</view>
				</view>

				<!-- 打字中 -->
				<view v-if="isTyping" class="message-row row-ai" id="msg-typing">
					<view class="avatar ai-avatar"><text class="ai-avatar-t">影</text></view>
					<view class="message-main bubble-ai typing-bubble">
						<view class="dot"></view>
						<view class="dot"></view>
						<view class="dot"></view>
					</view>
				</view>
			</view>
		</scroll-view>

		<!-- 底部输入框 -->
		<view class="input-bar" :style="{ bottom: inputBottom }">
			<input 
				class="chat-input" 
				v-model="inputText" 
				placeholder="输入内容"
				placeholder-class="input-placeholder"
				:adjust-position="true"
				@confirm="sendMessage"
				confirm-type="send"
			/>
			<view class="send-btn" :class="{ 'btn-active': inputText.length > 0 }" @tap="sendMessage">
				<text class="send-btn-t">发送</text>
			</view>
		</view>

		<custom-tabbar :list="navList" />
	</view>
</template>

<script>
	import customTabbar from '@/components/custom-tabbar/custom-tabbar.vue'
	import { postShadowChat, getApiUserId } from '@/utils/api.js'

	var LANDING_BROW_L = {
		sad: [87,90.6,96,85.5,105,90.1], calm: [87,88.9,96,87.3,105,88.9],
		happy: [87,86.9,96,82.5,105,86.9], angry: [87,86.4,96,90.5,105,86.4]
	}
	var LANDING_BROW_R = {
		sad: [137,90.1,146,85.5,155,90.6], calm: [137,88.9,146,87.3,155,88.9],
		happy: [137,86.9,146,82.5,155,86.9], angry: [137,86.4,146,90.5,155,86.4]
	}
	var LANDING_MOUTH = {
		sad: [108,129,120.7,121,133,129], calm: [108,123,120.7,129,133,123],
		happy: [100,118,120.7,138,141,118], angry: [106,127,120.7,123,135,127]
	}
	var LANDING_EYE_RY = [5.1, 7.0, 8.6, 4.0]
	var LANDING_BLUSH = [0.10, 0.28, 0.70, 0.08]
	var LANDING_TEARS = [0.95, 0.08, 0, 0]
	var LANDING_GRAD = [[214,210,255],[226,220,255],[255,243,189],[255,214,203]]
	var LANDING_TINT = [[140,132,220,0.08],[168,146,230,0.08],[255,216,120,0.10],[255,154,138,0.12]]

	export default {
		components: {
			customTabbar
		},
		data() {
			return {
				statusBarHeight: 44,
				inputText: '',
				isTyping: false,
				scrollToMessage: '',
				tarotReading: null,
				fromTarot: false,
				emotionSnapshot: { mood: 72, vit: 62, savedAt: 0, note: '' },
				emotionState: 'happy',
				shadowSessionId: '',
				pendingClarification: false,
				landingFaceOY: -1.8,
				landingBaseFaceOY: -1.8,
				landingBrowLP: [87,86.9,96,82.5,105,86.9],
				landingBrowRP: [137,86.9,146,82.5,155,86.9],
				landingEyeR: 8.4,
				landingBaseEyeR: 8.4,
				landingMouthP: [100,118,120.7,138,141,118],
				landingBlushA: 0.70,
				landingBaseBlushA: 0.70,
				landingTearA: 0,
				landingSparkA: 0.72,
				landingBaseSparkA: 0.72,
				landingGradRGB: [255,243,189],
				landingTintRGBA: [255,216,120,0.10],
				landingMascotTf: 'translateY(0px) rotate(0deg) scale(1)',
				landingAnimTimer: null,
				messageList: [
					{
						role: 'ai',
						content: '你好，我是你的影子。今天过得怎么样？无论有什么烦恼，都可以跟我倾诉。'
					}
				],
				navList: [
					{ label: '首页', active: false, path: '/pages/index/index' },
					{ label: '探索', active: false, path: '/pages/explore/explore' },
					{ label: '影子', active: true, path: '/pages/shadow/shadow' },
					{ label: '我的', active: false, path: '/pages/profile/profile' }
				]
			}
		},
		computed: {
			showLanding() {
				return !this.tarotReading && this.messageList.length <= 1;
			},
			emotionCaption() {
				var note = (this.emotionSnapshot.note || '').trim()
				if (note) return note.length > 18 ? note.slice(0, 18) + '…' : note
				if (this.emotionState === 'sad') return '今天先抱抱自己，再慢慢说'
				if (this.emotionState === 'calm') return '状态还不错，适合慢慢整理想法'
				if (this.emotionState === 'angry') return '能量有点满，先帮你把情绪理顺'
				return '今天亮晶晶的，聊聊你想解决什么'
			},
			inputBottom() {
				// The custom tabbar occupies effectively env(safe-area-inset-bottom) + its base height (~110rpx-130rpx)
				return `calc(130rpx + env(safe-area-inset-bottom))`;
			},
			bottomPadding() {
				// Scroll view must clear BOTH the tabbar and the input bar (~110rpx)
				return `calc(260rpx + env(safe-area-inset-bottom))`;
			}
		},
		mounted() {
			try {
				var info = uni.getWindowInfo ? uni.getWindowInfo() : uni.getSystemInfoSync();
				if (info && info.statusBarHeight) {
					this.statusBarHeight = info.statusBarHeight;
				}
			} catch (e) {}
			this.syncEmotionSnapshot();
			this.checkTarotSession();
			this.startLandingAnim();
		},
		onShow() {
			this.syncEmotionSnapshot();
			this.checkTarotSession();
			this.startLandingAnim();
		},
		beforeDestroy() {
			if (this.landingAnimTimer) clearTimeout(this.landingAnimTimer)
		},
		methods: {
			clamp(v, lo, hi) {
				return Math.max(lo, Math.min(hi, v));
			},
			weightedArr(arrs, wt) {
				var n = arrs[0].length, out = []
				for (var j = 0; j < n; j++) {
					var v = 0
					for (var i = 0; i < arrs.length; i++) v += arrs[i][j] * wt[i]
					out.push(v)
				}
				return out
			},
			getMoodWeights(e) {
				var sad = 0, calm = 0, happy = 0
				if (e < 50) { sad = 1 - e / 50; calm = e / 50 }
				else { calm = 1 - (e - 50) / 50; happy = (e - 50) / 50 }
				return [sad, calm, happy, 0]
			},
			buildQuadPath(points) {
				if (!points || points.length < 6) return ''
				return 'M ' + points[0].toFixed(1) + ' ' + points[1].toFixed(1) +
					' Q ' + points[2].toFixed(1) + ' ' + points[3].toFixed(1) +
					' ' + points[4].toFixed(1) + ' ' + points[5].toFixed(1)
			},
			landingRgbStr(color) {
				return 'rgb(' + color[0] + ',' + color[1] + ',' + color[2] + ')'
			},
			startLandingAnim() {
				var self = this
				if (this.landingAnimTimer) clearTimeout(this.landingAnimTimer)
				(function tick() {
					var ts = Date.now()
					var bob = Math.sin(ts * 0.0021) * 5.5
					var tilt = Math.sin(ts * 0.0013) * 1.4
					var pulse = (Math.sin(ts * 0.0024) + 1) / 2
					var blinkPhase = (ts + 900) % 4200
					var blink = 1
					if (blinkPhase < 180) blink = 0.26 + 0.74 * Math.abs(Math.cos((blinkPhase / 180) * Math.PI))
					self.landingMascotTf = 'translateY(' + bob.toFixed(2) + 'px) rotate(' + tilt.toFixed(2) + 'deg) scale(' + (1 + pulse * 0.016).toFixed(3) + ')'
					self.landingFaceOY = self.landingBaseFaceOY + bob * 0.16
					self.landingEyeR = Math.max(1.4, self.landingBaseEyeR * blink)
					self.landingBlushA = self.clamp(self.landingBaseBlushA * (0.94 + pulse * 0.08), 0.04, 0.84)
					self.landingSparkA = self.clamp(self.landingBaseSparkA * (0.88 + pulse * 0.16), 0.16, 0.98)
					self.landingAnimTimer = setTimeout(tick, 33)
				})()
			},
			syncEmotionSnapshot() {
				var raw = ''
				try { raw = uni.getStorageSync('shadowEmotionSnapshot') || '' } catch (e) {}
				if (!raw) {
					this.applyEmotionSnapshot(this.emotionSnapshot)
					return
				}
				var snap = null
				try { snap = JSON.parse(raw) } catch (e) {}
				if (!snap || typeof snap.mood !== 'number') return
				this.applyEmotionSnapshot(snap)
			},
			applyEmotionSnapshot(snap) {
				var mood = this.clamp(Number(snap.mood || 72), 0, 100)
				var vit = this.clamp(Number(snap.vit || 62), 0, 100)
				this.emotionSnapshot = {
					mood: mood,
					vit: vit,
					savedAt: Number(snap.savedAt || 0),
					note: snap.note || ''
				}
				var state = 'happy'
				if (mood < 28) state = 'sad'
				else if (mood < 58) state = 'calm'
				else if (mood > 78 && vit > 84) state = 'angry'
				this.emotionState = state
				var wt = this.getMoodWeights(mood)
				if (state === 'angry') wt = [0, 0, 0, 1]
				this.landingBaseFaceOY = 4.5 + (mood / 100) * -7
				this.landingBrowLP = this.weightedArr([LANDING_BROW_L.sad, LANDING_BROW_L.calm, LANDING_BROW_L.happy, LANDING_BROW_L.angry], wt)
				this.landingBrowRP = this.weightedArr([LANDING_BROW_R.sad, LANDING_BROW_R.calm, LANDING_BROW_R.happy, LANDING_BROW_R.angry], wt)
				this.landingBaseEyeR = LANDING_EYE_RY[0]*wt[0] + LANDING_EYE_RY[1]*wt[1] + LANDING_EYE_RY[2]*wt[2] + LANDING_EYE_RY[3]*wt[3]
				this.landingMouthP = this.weightedArr([LANDING_MOUTH.sad, LANDING_MOUTH.calm, LANDING_MOUTH.happy, LANDING_MOUTH.angry], wt)
				this.landingBaseBlushA = LANDING_BLUSH[0]*wt[0] + LANDING_BLUSH[1]*wt[1] + LANDING_BLUSH[2]*wt[2] + LANDING_BLUSH[3]*wt[3]
				this.landingTearA = LANDING_TEARS[0]*wt[0] + LANDING_TEARS[1]*wt[1] + LANDING_TEARS[2]*wt[2] + LANDING_TEARS[3]*wt[3]
				this.landingBaseSparkA = 0.32 + vit / 100 * 0.42
				var gr=0, gg=0, gb=0, tr=0, tg=0, tb=0, to=0
				for (var i = 0; i < 4; i++) {
					gr += LANDING_GRAD[i][0] * wt[i]
					gg += LANDING_GRAD[i][1] * wt[i]
					gb += LANDING_GRAD[i][2] * wt[i]
					tr += LANDING_TINT[i][0] * wt[i]
					tg += LANDING_TINT[i][1] * wt[i]
					tb += LANDING_TINT[i][2] * wt[i]
					to += LANDING_TINT[i][3] * wt[i]
				}
				this.landingGradRGB = [Math.round(gr), Math.round(gg), Math.round(gb)]
				this.landingTintRGBA = [Math.round(tr), Math.round(tg), Math.round(tb), to]
				this.landingFaceOY = this.landingBaseFaceOY
				this.landingEyeR = this.landingBaseEyeR
				this.landingBlushA = this.landingBaseBlushA
				this.landingSparkA = this.landingBaseSparkA
			},
			goBack() {
				if (getCurrentPages().length > 1) {
					uni.navigateBack();
				} else {
					uni.reLaunch({ url: '/pages/index/index' });
				}
			},
			checkTarotSession() {
				var raw = '';
				try { raw = uni.getStorageSync('shadowTarotSession') || ''; } catch (e) {}
				if (!raw) return;
				try { uni.removeStorageSync('shadowTarotSession'); } catch (e) {}
				var session = {};
				try { session = JSON.parse(raw); } catch (e) { return; }
				if (!session || !session.cards || session.cards.length < 3) return;

				this.fromTarot = true;
				this.tarotReading = this.buildTarotReading(session);
				this.scrollToBottom();
			},
			buildTarotReading(session) {
				var cards = (session.cards || []).slice(0, 3);
				var intent = session.intent || {};
				var names = ['第一张', '第二张', '第三张'];
				var sections = [];
				for (var i = 0; i < cards.length; i++) {
					var card = cards[i] || {};
					sections.push({
						title: (card.name || names[i]) + '：',
						content:
							(card.desc || '这张牌正在提醒你关注当下的内心感受。') +
							' 现在更适合把注意力放回自己，看看这张牌与你眼前的问题是如何呼应的。'
					});
					card.displayName = card.name || names[i];
				}
				return {
					questionText: intent.question || intent.tagLabel || '我的塔罗指引',
					intentTag: intent.tagLabel || '',
					intentQuestion: intent.question || '',
					cards: cards,
					sections: sections
				};
			},
			sendMessage() {
				if (!this.inputText.trim()) return;
				
				var userMsg = this.inputText.trim();
				this.messageList.push({
					role: 'user',
					content: userMsg
				});
				this.inputText = '';
				
				this.scrollToBottom();
				
				// Show typing indicator
				this.isTyping = true;
				this.scrollToBottom('msg-typing');

			var self = this;
			var userId = getApiUserId();
			if (!userId) {
				self.isTyping = false;
				self.messageList.push({
					role: 'ai',
					content: '请先登录后再与影子对话。'
				});
				self.scrollToBottom();
				return;
			}

			// 根据情绪快照推断 emotion_keyword
				var mood = this.emotionSnapshot.mood || 72;
				var vit = this.emotionSnapshot.vit || 62;
				var keyword = '迷茫';
				if (mood < 28) keyword = '失落';
				else if (mood < 50) keyword = '焦虑';
				else if (mood > 78 && vit > 84) keyword = '愤怒';
				else if (mood >= 50) keyword = '困惑';

				var payload = {
					emotion_keyword: keyword,
					question: userMsg
				};

				// 两轮对话：如果有 pendingClarification，把用户当前消息作为 supplements
				if (this.pendingClarification) {
					payload.supplements = userMsg;
					this.pendingClarification = false;
				}
				if (this.shadowSessionId) {
					payload.session_id = this.shadowSessionId;
				}

				postShadowChat(payload).then(function(res) {
					self.isTyping = false;
					if (!res) {
						self.messageList.push({ role: 'ai', content: '影子暂时断开了链接，请稍后重试。' });
						self.scrollToBottom();
						return;
					}
					// 保存 session_id
					if (res.debug_info && res.debug_info.session_id) {
						self.shadowSessionId = res.debug_info.session_id;
					}
					var reply = res.reply || '影子暂时断开了链接...';
					self.messageList.push({ role: 'ai', content: reply });

					// 如果是追问阶段，标记 pending
					if (res.phase === 'clarifying') {
						self.pendingClarification = true;
					}

					self.scrollToBottom();
				}).catch(function(err) {
					self.isTyping = false;
					var errMsg = err && err.message ? err.message : '请求失败';
					self.messageList.push({ role: 'ai', content: '出了点问题：' + errMsg });
					self.scrollToBottom();
				});
			},
			scrollToBottom(id) {
				this.$nextTick(() => {
					setTimeout(() => {
						if (id) {
							this.scrollToMessage = id;
						} else {
							this.scrollToMessage = 'msg-' + (this.messageList.length - 1);
						}
					}, 100);
				});
			}
		}
	}
</script>

<style scoped>
	/* ===== 全局容器 ===== */
	.container {
		background:
			radial-gradient(ellipse 92% 56% at 50% 0%, rgba(226, 214, 255, 0.38) 0%, rgba(226, 214, 255, 0.08) 34%, transparent 62%),
			linear-gradient(180deg, #ffffff 0%, #fcfbff 50%, #faf8ff 100%);
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		position: relative;
		overflow: hidden;
	}
	.top-glow {
		position: absolute;
		top: -120rpx; left: -8%;
		width: 116%; height: 520rpx;
		background: radial-gradient(ellipse at 50% 18%, rgba(232,220,255,0.42) 0%, rgba(232,220,255,0.10) 42%, transparent 72%);
		pointer-events: none; z-index: 0;
	}

	/* ===== 顶部导航 ===== */
	.nav-header {
		position: fixed; top: 0; left: 0; width: 100%;
		background: rgba(255, 255, 255, 0.82);
		backdrop-filter: blur(28px);
		-webkit-backdrop-filter: blur(28px);
		z-index: 100;
		display: flex; align-items: center; justify-content: center;
		height: 44px;
		border-bottom: 1rpx solid rgba(228, 223, 242, 0.72);
	}
	.nav-back {
		position: absolute; left: 24rpx;
		width: 62rpx; height: 62rpx;
		display: flex; align-items: center; justify-content: center;
		border-radius: 50%;
		background: rgba(255,255,255,0.96);
		border: 1rpx solid rgba(229,223,244,0.92);
		box-shadow: 0 6rpx 16rpx rgba(160, 152, 196, 0.10);
	}
	.nav-back-t { font-size: 40rpx; color: #4d456f; margin-top: -4rpx; }
	.page-title {
		font-size: 32rpx; font-weight: 700;
		color: #28233b; letter-spacing: 0;
	}

	/* ===== 聊天滚动区 ===== */
	.chat-scroll { flex: 1; height: 100vh; box-sizing: border-box; }
	.chat-list { padding: 28rpx 28rpx 24rpx; display: flex; flex-direction: column; }
	.chat-list--landing {
		min-height: calc(100vh - 320rpx);
		justify-content: flex-start;
		padding-top: 8rpx;
	}

	/* ===== 欢迎区 ===== */
	.welcome-panel {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 0 24rpx 0;
		margin-top: -18rpx;
	}
	.landing-hero-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 12rpx 0 0;
		margin-bottom: 18rpx;
	}
	.landing-mascot-wrap {
		width: 188rpx;
		height: 144rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 12rpx;
		transform-origin: 50% 62%;
		will-change: transform;
	}
	.landing-mascot {
		width: 172rpx;
		height: 134rpx;
		display: block;
		filter: drop-shadow(0 14rpx 24rpx rgba(255, 214, 103, 0.16));
	}
	.landing-caption {
		font-size: 25rpx;
		line-height: 1.5;
		color: rgba(108, 102, 136, 0.72);
		text-align: center;
		padding: 0 18rpx;
	}
	.landing-copy {
		display: flex;
		flex-direction: column;
		align-items: center;
		max-width: 560rpx;
	}
	.landing-title {
		font-size: 52rpx;
		line-height: 1.18;
		font-weight: 700;
		color: #23212c;
		text-align: center;
	}
	.landing-subtitle {
		margin-top: 12rpx;
		font-size: 27rpx;
		line-height: 1.6;
		color: rgba(103, 97, 132, 0.70);
		text-align: center;
	}

	/* ===== 塔罗问题气泡 ===== */
	.tarot-q-wrap {
		display: flex; justify-content: flex-end;
		margin-bottom: 24rpx;
	}
	.tarot-q-bubble {
		max-width: 64%;
		padding: 24rpx 32rpx;
		border-radius: 26rpx 26rpx 8rpx 26rpx;
		background: linear-gradient(140deg, #6d82ff 0%, #8c72ef 100%);
		box-shadow: 0 12rpx 32rpx rgba(118, 116, 214, 0.26);
	}
	.tarot-q-text {
		font-size: 28rpx; color: rgba(255,255,255,0.96);
		line-height: 1.6; font-weight: 500;
	}

	/* ===== 塔罗解读卡片 ===== */
	.tarot-reading-card {
		margin-bottom: 32rpx;
		padding: 30rpx 26rpx 26rpx;
		border-radius: 28rpx;
		background: rgba(255,255,255,0.76);
		box-shadow:
			0 18rpx 42rpx rgba(152, 158, 210, 0.12),
			inset 0 1rpx 0 rgba(255,255,255,0.88);
		border: 1rpx solid rgba(216, 218, 242, 0.88);
	}
	.trc-head { display: flex; align-items: center; margin-bottom: 24rpx; }
	.trc-icon-ring {
		width: 60rpx; height: 60rpx; border-radius: 16rpx;
		background: linear-gradient(145deg, rgba(196,172,255,0.30), rgba(148,116,220,0.22));
		border: 1rpx solid rgba(196,172,255,0.20);
		display: flex; align-items: center; justify-content: center;
		box-shadow: 0 6rpx 18rpx rgba(100, 72, 200, 0.20);
		margin-right: 18rpx;
	}
	.trc-icon-glyph { font-size: 26rpx; color: rgba(220,200,255,0.95); }
	.trc-head-text { flex: 1; display: flex; flex-direction: column; }
	.trc-head-title {
		font-size: 27rpx; font-weight: 700;
		color: #3c4268; line-height: 1.35;
	}
	.trc-head-sub {
		margin-top: 6rpx; font-size: 21rpx;
		color: rgba(118, 126, 166, 0.68); line-height: 1.4;
	}

	/* 三张牌 */
	.trc-cards-strip {
		display: flex; justify-content: center; gap: 16rpx;
		padding: 20rpx 10rpx;
		border-radius: 20rpx;
		background: rgba(238, 242, 255, 0.86);
		border: 1rpx solid rgba(216, 218, 242, 0.80);
		margin-bottom: 12rpx;
	}
	.trc-card-col { flex: 1; display: flex; flex-direction: column; align-items: center; }
	.trc-card {
		width: 100%; max-width: 156rpx; height: 220rpx;
		border-radius: 18rpx; position: relative;
		box-shadow: 0 12rpx 30rpx rgba(12, 10, 28, 0.45);
		display: flex; flex-direction: column;
		align-items: center; justify-content: center;
		padding: 12rpx 8rpx;
		border: 1rpx solid rgba(255,255,255,0.08);
	}
	.trc-card-num {
		position: absolute; top: 12rpx; left: 14rpx;
		font-size: 18rpx; font-weight: 700;
		color: rgba(255,255,255,0.18); font-style: italic;
	}
	.trc-card-ring {
		width: 52rpx; height: 52rpx; border-radius: 50%;
		background: rgba(255,255,255,0.12);
		border: 1rpx solid rgba(255,255,255,0.14);
		display: flex; align-items: center; justify-content: center;
		margin-bottom: 10rpx;
	}
	.trc-card-sym { font-size: 26rpx; color: rgba(255,255,255,0.55); }
	.trc-card-name-inner {
		font-size: 21rpx; font-weight: 700;
		color: rgba(255,255,255,0.88); text-align: center;
	}
	.trc-card-label {
		margin-top: 14rpx; font-size: 23rpx;
		font-weight: 600; color: rgba(88, 95, 138, 0.82);
	}

	.trc-divider {
		height: 1rpx; margin: 22rpx 0 20rpx;
		background: linear-gradient(90deg, transparent, rgba(148,132,210,0.18), transparent);
	}

	/* 解读段落 */
	.trc-reading-body { display: flex; flex-direction: column; gap: 22rpx; }
	.trc-section { padding: 0 2rpx; }
	.trc-section-title {
		display: block; font-size: 27rpx; font-weight: 700;
		color: #3d446e; line-height: 1.55;
	}
	.trc-section-content {
		display: block; margin-top: 8rpx;
		font-size: 26rpx; line-height: 1.78;
		color: rgba(92, 100, 138, 0.82);
	}

	/* 工具条 */
	.trc-tools { display: flex; gap: 14rpx; margin-top: 28rpx; flex-wrap: wrap; }
	.trc-tool-chip {
		display: flex; align-items: center; gap: 8rpx;
		padding: 16rpx 22rpx;
		border-radius: 16rpx;
		background: rgba(244, 246, 255, 0.92);
		border: 1rpx solid rgba(216, 218, 242, 0.84);
	}
	.trc-tool-hover { background: rgba(230, 234, 252, 0.96); }
	.trc-tool-emoji { font-size: 26rpx; }
	.trc-tool-text { font-size: 23rpx; color: rgba(88, 95, 138, 0.86); font-weight: 600; }

	/* ===== 消息通用 ===== */
	.message-row { display: flex; margin-bottom: 26rpx; align-items: flex-start; }
	.row-user { justify-content: flex-end; }
	.row-ai { justify-content: flex-start; }

	.avatar {
		width: 64rpx; height: 64rpx; border-radius: 18rpx;
		flex-shrink: 0; overflow: hidden;
	}
	.ai-avatar {
		background: linear-gradient(145deg, #9fb3ff 0%, #8f87f0 100%);
		border: 1rpx solid rgba(192,194,244,0.64);
		display: flex; align-items: center; justify-content: center;
		margin-right: 16rpx;
		box-shadow: 0 10rpx 18rpx rgba(125, 133, 225, 0.18);
	}
	.ai-avatar-t { font-size: 28rpx; font-weight: 800; color: rgba(255,255,255,0.96); }
	.user-avatar {
		margin-left: 16rpx;
		background: rgba(232, 234, 248, 0.84);
		border: 1rpx solid rgba(223,227,246,0.92);
	}
	.user-avatar image { width: 100%; height: 100%; }

	.message-main {
		max-width: 72%;
		padding: 22rpx 26rpx;
		border-radius: 28rpx;
		font-size: 29rpx;
		line-height: 1.7;
		word-break: break-all;
	}
	.message-main .message-text {
		display: block;
		white-space: pre-wrap;
		word-break: break-word;
		line-height: 1.72;
	}
	.message-role {
		display: inline-block;
		margin-bottom: 10rpx;
		font-size: 22rpx;
		font-weight: 700;
		color: rgba(129, 122, 170, 0.84);
		letter-spacing: 1rpx;
	}
	.message-main--ai,
	.bubble-ai {
		background: rgba(255,255,255,0.98);
		color: #394062;
		border-top-left-radius: 10rpx;
		box-shadow: 0 10rpx 24rpx rgba(165, 170, 214, 0.10);
		border: 1rpx solid rgba(232, 234, 246, 0.96);
	}
	.message-main--user {
		background: linear-gradient(145deg, #6a84ff, #886feb);
		color: rgba(255,255,255,0.96);
		border-top-right-radius: 10rpx;
		box-shadow: 0 14rpx 28rpx rgba(123, 118, 214, 0.22);
	}

	/* 打字动画 */
	.typing-bubble { display: flex; align-items: center; height: 44rpx; padding: 22rpx 28rpx; min-width: 112rpx; }
	.dot {
		width: 12rpx; height: 12rpx;
		background: rgba(132, 144, 214, 0.62); border-radius: 50%;
		margin: 0 6rpx;
		animation: bounce 1.4s infinite ease-in-out both;
	}
	.dot:nth-child(1) { animation-delay: -0.32s; }
	.dot:nth-child(2) { animation-delay: -0.16s; }
	@keyframes bounce {
		0%, 80%, 100% { transform: scale(0); }
		40% { transform: scale(1); }
	}

	/* ===== 底部输入栏 ===== */
	.input-bar {
		position: fixed; left: 0; width: 100%;
		background: rgba(255, 255, 255, 0.88);
		backdrop-filter: blur(22px);
		-webkit-backdrop-filter: blur(22px);
		padding: 16rpx 20rpx;
		box-sizing: border-box;
		display: flex; align-items: center;
		border-top: 1rpx solid rgba(242, 238, 249, 0.96);
		z-index: 90;
	}
	.chat-input {
		flex: 1; height: 82rpx;
		background: rgba(250, 248, 255, 0.96);
		border-radius: 999rpx;
		padding: 0 30rpx;
		font-size: 29rpx; color: #2e2c37;
		font-weight: 400;
		border: 1rpx solid rgba(239, 233, 248, 1);
		box-shadow: none;
	}
	.input-placeholder { color: rgba(150, 144, 166, 0.88); }
	.send-btn {
		margin-left: 14rpx;
		min-width: 96rpx;
		height: 72rpx;
		padding: 0 24rpx;
		border-radius: 999rpx;
		background: rgba(250, 248, 255, 0.96);
		border: 1rpx solid rgba(239, 233, 248, 1);
		display: flex; align-items: center; justify-content: center;
		transition: all 0.2s;
		box-shadow: none;
	}
	.send-btn-t { font-size: 27rpx; color: #5a5570; font-weight: 700; }
	.btn-active {
		background: linear-gradient(145deg, #8e7aeb, #7b68da);
		border-color: transparent;
		box-shadow: 0 10rpx 22rpx rgba(136, 120, 219, 0.20);
	}
	.btn-active .send-btn-t { color: rgba(255,255,255,0.96); }
</style>
