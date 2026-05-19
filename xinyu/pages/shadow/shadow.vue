<template>
	<view class="container">
		<!-- 顶部装饰光 -->
		<view class="top-glow"></view>

		<!-- 顶部导航 -->
		<view class="nav-header">
			<view class="nav-back" v-if="fromTarot" @tap="goBack"><text class="nav-back-t">‹</text></view>
			<text class="page-title">{{ tarotReading ? '塔罗解读' : '影子' }}</text>
			<view v-if="!tarotReading && messageList.length > 1" class="nav-new-chat" @tap="onNewChat">
				<text class="nav-new-chat-text">新对话</text>
			</view>
		</view>

		<!-- 聊天区域 -->
		<scroll-view
			class="chat-scroll"
			scroll-y="true"
			:scroll-into-view="scrollToMessage"
		>
			<view class="chat-list" :class="{ 'chat-list--landing': showLanding }">
				<view v-if="showLanding" class="welcome-panel">
					<view class="landing-hero-card">
						<view class="landing-mascot-wrap" :style="{ transform: landingMascotTf }">
							<canvas canvas-id="shadowSpriteCanvas" id="shadowSpriteCanvas" class="landing-mascot-canvas"></canvas>
						</view>
						<text class="landing-caption">{{ emotionCaption }}</text>
					</view>
					<view class="landing-copy">
						<text class="landing-title">今天想聊点什么？</text>
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
							:key="ci"
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
							:key="idx"
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
					:class="msgRowCls[index]"
				>
					<view v-if="msg.role === 'ai'" class="avatar ai-avatar">
						<view class="ai-avatar-silhouette"></view>
					</view>

					<view class="message-main" :class="msgMainCls[index]">
						<text v-if="msg.role === 'ai'" class="message-role">影子</text>
						<text class="message-text">{{ msg.content }}</text>
					</view>
					
					<view v-if="msg.role === 'user'" class="avatar user-avatar" :style="userAvatarStyle">
						<view v-if="!userAvatar" class="user-avatar-placeholder">
							<text class="user-avatar-icon">👤</text>
						</view>
					</view>
				</view>

				<!-- 打字中 -->
				<view v-if="isTyping" class="message-row row-ai" id="msg-typing">
					<view class="avatar ai-avatar"><view class="ai-avatar-silhouette"></view></view>
					<view class="message-main bubble-ai typing-bubble">
						<view class="dot"></view>
						<view class="dot"></view>
						<view class="dot"></view>
					</view>
				</view>
			</view>
		</scroll-view>

		<!-- 追问状态提示 -->
		<view v-if="pendingClarification" class="clarify-hint-bar">
			<text class="clarify-hint-text">正在回答追问</text>
			<text class="clarify-hint-new" @tap="onNewChat">新对话</text>
		</view>

		<!-- 底部输入框 -->
		<view class="input-bar" :class="{ 'input-bar--with-hint': pendingClarification }" :style="{ bottom: inputBottom }">
			<input 
				class="chat-input" 
				v-model="inputText" 
				placeholder="说点什么吧…"
				placeholder-class="input-placeholder"
				:adjust-position="true"
				@confirm="sendMessage"
				confirm-type="send"
			/>
			<view class="send-btn" :class="sendBtnCls" @tap="sendMessage">
				<text class="send-btn-t">发送</text>
			</view>
		</view>

		<custom-tabbar :list="navList" />

		<!-- 新对话确认弹窗 -->
		<view v-if="showNewChatModal" class="modal-mask" @tap.self="showNewChatModal = false">
			<view class="modal-box" :class="{ 'modal-in': showNewChatModal }">
				<text class="modal-title">开始新对话</text>
				<text class="modal-desc">当前对话将被清空，确定吗？</text>
				<view class="modal-btns">
					<view class="modal-btn modal-btn-cancel" @tap="showNewChatModal = false">
						<text>取消</text>
					</view>
					<view class="modal-btn modal-btn-confirm" @tap="confirmNewChat">
						<text>确定</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import customTabbar from '@/components/custom-tabbar/custom-tabbar.vue'
	import { streamShadowChat, postTarotSession, getApiUserId, getApiOpenid, getApiUserPhone, getUser } from '@/utils/api.js'

	var STORAGE_KEY_SESSION = 'shadowChatSession'
	var STORAGE_KEY_MESSAGES = 'shadowChatMessages'
	var STORAGE_KEY_PENDING = 'shadowChatPending'
	var STORAGE_KEY_VERSION = 'shadowChatVersion'
	var STORAGE_VERSION = 4  // 版本升级时自增，自动清除旧缓存
	var MAX_MESSAGES = 200
	var DEFAULT_AI_MSG = '嗨，我是你的影子 ☁️  今天过得怎么样？\n无论有什么烦恼，都可以跟我聊聊。'

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
				inputText: '',
				isTyping: false,
				scrollToMessage: '',
				tarotReading: null,
				fromTarot: false,
				emotionSnapshot: { mood: 72, vit: 62, savedAt: 0, note: '' },
				emotionState: 'happy',
				shadowSessionId: '',
				pendingClarification: false,
				streamAbort: null,
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
				userAvatar: '',
				showNewChatModal: false,
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
				return 'calc(130rpx + env(safe-area-inset-bottom))';
			},
		bottomPadding() {
			// Scroll view must clear BOTH the tabbar and the input bar (~110rpx)
			return 'calc(260rpx + env(safe-area-inset-bottom))';
		},
		userAvatarStyle() {
			if (this.userAvatar) {
				return { backgroundImage: 'url(' + this.userAvatar + ')' }
			}
			return {}
		},
		msgRowCls() {
			return this.messageList.map(function(m) { return m.role === 'user' ? 'row-user' : 'row-ai' })
		},
		msgMainCls() {
			return this.messageList.map(function(m) { return m.role === 'user' ? 'message-main--user' : 'message-main--ai' })
		},
		sendBtnCls() {
			return { 'btn-active': this.inputText.length > 0 }
		}
	},
		mounted() {
			try {
				this.shadowCanvasCtx = uni.createCanvasContext('shadowSpriteCanvas', this)
			} catch(e) {}
			this.loadChatSession();
			this.syncEmotionSnapshot();
			this.checkTarotSession();
			this.checkSpecialistSession();
			this.startLandingAnim();
		},
		onShow() {
			this.loadUserAvatar();
			this.loadChatSession();
			this.syncEmotionSnapshot();
			this.checkTarotSession();
			this.checkSpecialistSession();
			this.startLandingAnim();
		},
		beforeDestroy() {
			if (this.landingAnimTimer) clearTimeout(this.landingAnimTimer)
			if (this.streamAbort) { this.streamAbort.abort(); this.streamAbort = null }
		},
		methods: {
			loadUserAvatar: function() {
				var self = this
				// 1. 先读 Storage 缓存
				var cached = ''
				try {
					var raw = uni.getStorageSync('userProfile')
					if (raw) { var p = JSON.parse(raw); if (p.avatar) cached = p.avatar }
				} catch (e) {}
				if (!cached) {
					try { cached = uni.getStorageSync('xinyu_user_avatar') || '' } catch(e) {}
				}
				if (cached) { self.userAvatar = cached; console.log('[shadow] avatar loaded, len=' + cached.length) }

				// 2. 远端拉取，但仅当远端有头像时才覆盖（远端为空不覆盖本地）
				var uid = getApiUserId()
				var phone = getApiUserPhone()
				var fetch = uid ? getUser({ id: uid }) : (phone ? getUser({ phone: phone }) : null)
				if (fetch) {
					fetch.then(function(res) {
						if (res && res.data && res.data.avatar_url) {
							self.userAvatar = res.data.avatar_url
						}
					}).catch(function() {})
				}
			},
			// ── 会话持久化 ──
			loadChatSession() {
				try {
					// 版本检测：版本不匹配时清除旧缓存，避免旧 session 数据干扰
					var savedVer = uni.getStorageSync(STORAGE_KEY_VERSION);
					if (savedVer !== STORAGE_VERSION) {
						console.log('[shadow] 缓存版本不匹配，清除旧会话数据');
						uni.removeStorageSync(STORAGE_KEY_SESSION);
						uni.removeStorageSync(STORAGE_KEY_MESSAGES);
						uni.removeStorageSync(STORAGE_KEY_PENDING);
						uni.setStorageSync(STORAGE_KEY_VERSION, STORAGE_VERSION);
						this.shadowSessionId = '';
						this.pendingClarification = false;
						this.messageList = [{ role: 'ai', content: DEFAULT_AI_MSG }];
						return;
					}
					var sid = uni.getStorageSync(STORAGE_KEY_SESSION) || '';
					if (sid) this.shadowSessionId = sid;
					var pending = uni.getStorageSync(STORAGE_KEY_PENDING);
					if (pending === true || pending === 'true') this.pendingClarification = true;
					var raw = uni.getStorageSync(STORAGE_KEY_MESSAGES) || '';
					if (raw) {
						var msgs = JSON.parse(raw);
						if (Array.isArray(msgs) && msgs.length > 0) {
							this.messageList = msgs;
							return;
						}
					}
				} catch (e) {}
				// 无历史记录时用默认欢迎语
				if (this.messageList.length <= 1) {
					this.messageList = [{ role: 'ai', content: DEFAULT_AI_MSG }];
				}
			},
			saveChatSession() {
				try {
					if (this.shadowSessionId) {
						uni.setStorageSync(STORAGE_KEY_SESSION, this.shadowSessionId);
					}
					uni.setStorageSync(STORAGE_KEY_PENDING, this.pendingClarification);
					var msgs = this.messageList.slice(-MAX_MESSAGES);
					uni.setStorageSync(STORAGE_KEY_MESSAGES, JSON.stringify(msgs));
				} catch (e) {}
			},
			clearChatSession() {
				if (this.streamAbort) { this.streamAbort.abort(); this.streamAbort = null }
				this.shadowSessionId = '';
				this.pendingClarification = false;
				this.messageList = [{ role: 'ai', content: DEFAULT_AI_MSG }];
				try {
					uni.removeStorageSync(STORAGE_KEY_SESSION);
					uni.removeStorageSync(STORAGE_KEY_MESSAGES);
					uni.removeStorageSync(STORAGE_KEY_PENDING);
					uni.setStorageSync(STORAGE_KEY_VERSION, STORAGE_VERSION);
				} catch (e) {}
			},
			onNewChat() {
				this.showNewChatModal = true;
			},
			confirmNewChat: function() {
				this.showNewChatModal = false;
				this.clearChatSession();
			},
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
			_drawTear(ctx, cx, cy) {
				ctx.beginPath()
				ctx.moveTo(cx, cy)
				ctx.quadraticCurveTo(cx - 4, cy + 9, cx - 2, cy + 17)
				ctx.quadraticCurveTo(cx, cy + 25, cx + 2, cy + 17)
				ctx.quadraticCurveTo(cx + 4, cy + 9, cx, cy)
				ctx.closePath()
				ctx.fill()
			},
			drawShadowSprite() {
				var ctx = this.shadowCanvasCtx
				if (!ctx) return
				var self = this
				ctx.clearRect(0, 0, 241, 189)

				function bodyPath(ctx) {
					ctx.beginPath()
					ctx.moveTo(148.652, 0)
					ctx.bezierCurveTo(182.792, 0.0002, 210.468, 27.676, 210.468, 61.815)
					ctx.bezierCurveTo(210.468, 65.065, 210.216, 68.257, 209.732, 71.371)
					ctx.bezierCurveTo(228.627, 82.089, 241.376, 102.386, 241.376, 125.66)
					ctx.bezierCurveTo(241.376, 158.482, 215.946, 185.714, 183.158, 187.199)
					ctx.bezierCurveTo(162.354, 188.141, 139.439, 188.924, 120.688, 188.924)
					ctx.bezierCurveTo(101.936, 188.924, 79.022, 188.141, 58.218, 187.199)
					ctx.bezierCurveTo(25.430, 185.714, 0, 158.482, 0, 125.66)
					ctx.bezierCurveTo(0, 100.709, 14.651, 79.180, 35.819, 69.206)
					ctx.bezierCurveTo(35.495, 67.282, 35.323, 65.305, 35.323, 63.288)
					ctx.bezierCurveTo(35.323, 43.780, 51.138, 27.965, 70.647, 27.965)
					ctx.bezierCurveTo(78.959, 27.965, 86.600, 30.837, 92.634, 35.643)
					ctx.bezierCurveTo(102.489, 14.586, 123.868, 0, 148.652, 0)
					ctx.closePath()
				}

				// body shadow
				ctx.save()
				ctx.globalAlpha = 0.06
				ctx.fillStyle = '#161230'
				ctx.beginPath()
				ctx.save()
				ctx.translate(121, 192)
				ctx.scale(1.2, 0.12)
				ctx.arc(0, 0, 50, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.restore()

				// body fill
				var gradColor = self.landingRgbStr(self.landingGradRGB)
				ctx.save()
				ctx.globalAlpha = 0.92
				if (ctx.createRadialGradient) {
					var rg = ctx.createRadialGradient(110, 85, 12, 121, 100, 115)
					rg.addColorStop(0, gradColor.replace('rgb', 'rgba').replace(')', ',1)'))
					rg.addColorStop(1, gradColor.replace('rgb', 'rgba').replace(')', ',0.78)'))
					ctx.fillStyle = rg
				} else {
					ctx.fillStyle = gradColor.replace('rgb', 'rgba').replace(')', ',0.90)')
				}
				bodyPath(ctx)
				ctx.fill()
				ctx.restore()

				// tint
				ctx.save()
				ctx.globalAlpha = self.landingTintRGBA[3]
				ctx.fillStyle = self.landingRgbStr(self.landingTintRGBA)
				bodyPath(ctx)
				ctx.fill()
				ctx.restore()

				// inner ear
				ctx.save()
				ctx.globalAlpha = 0.35
				ctx.fillStyle = '#FFB0C8'
				ctx.beginPath()
				ctx.save()
				ctx.translate(71, 28)
				ctx.scale(0.78, 1.05)
				ctx.arc(0, 0, 6.5, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.beginPath()
				ctx.save()
				ctx.translate(150, 16)
				ctx.scale(0.82, 1.0)
				ctx.arc(0, 0, 7.5, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.restore()

				var oy = self.landingFaceOY

				// brows
				ctx.save()
				ctx.globalAlpha = 0.55
				ctx.strokeStyle = '#48425e'
				ctx.lineWidth = 2.8
				ctx.lineCap = 'round'
				if (self.landingBrowLP && self.landingBrowLP.length >= 6) {
					ctx.beginPath()
					ctx.moveTo(self.landingBrowLP[0], self.landingBrowLP[1] + oy)
					ctx.quadraticCurveTo(self.landingBrowLP[2], self.landingBrowLP[3] + oy, self.landingBrowLP[4], self.landingBrowLP[5] + oy)
					ctx.stroke()
				}
				if (self.landingBrowRP && self.landingBrowRP.length >= 6) {
					ctx.beginPath()
					ctx.moveTo(self.landingBrowRP[0], self.landingBrowRP[1] + oy)
					ctx.quadraticCurveTo(self.landingBrowRP[2], self.landingBrowRP[3] + oy, self.landingBrowRP[4], self.landingBrowRP[5] + oy)
					ctx.stroke()
				}
				ctx.restore()

				// eyes
				ctx.save()
				ctx.fillStyle = '#2e2a42'
				var er = self.landingEyeR
				ctx.beginPath()
				ctx.save()
				ctx.translate(96, 99 + oy)
				ctx.scale(1, er / 7)
				ctx.arc(0, 0, 7, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.fillStyle = 'rgba(255,255,255,0.85)'
				ctx.beginPath()
				ctx.save()
				ctx.translate(94, 97 + oy)
				ctx.arc(0, 0, 2.2, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.fillStyle = '#2e2a42'
				ctx.beginPath()
				ctx.save()
				ctx.translate(146, 99 + oy)
				ctx.scale(1, er / 7)
				ctx.arc(0, 0, 7, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.fillStyle = 'rgba(255,255,255,0.85)'
				ctx.beginPath()
				ctx.save()
				ctx.translate(144, 97 + oy)
				ctx.arc(0, 0, 2.2, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.restore()

				// blush
				ctx.save()
				ctx.globalAlpha = self.landingBlushA * 0.38
				ctx.fillStyle = '#FF8FAB'
				ctx.beginPath()
				ctx.save()
				ctx.translate(66, 110 + oy)
				ctx.scale(17/6, 1)
				ctx.arc(0, 0, 6, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.beginPath()
				ctx.save()
				ctx.translate(176, 110 + oy)
				ctx.scale(17/6, 1)
				ctx.arc(0, 0, 6, 0, Math.PI * 2)
				ctx.restore()
				ctx.fill()
				ctx.restore()

				// tears
				ctx.save()
				ctx.globalAlpha = self.landingTearA * 0.72
				ctx.fillStyle = '#99CCFF'
				self._drawTear(ctx, 96, 112 + oy)
				self._drawTear(ctx, 146, 112 + oy)
				ctx.restore()

				// mouth
				ctx.save()
				ctx.strokeStyle = '#3e3858'
				ctx.lineWidth = 3.6
				ctx.lineCap = 'round'
				if (self.landingMouthP && self.landingMouthP.length >= 6) {
					ctx.beginPath()
					ctx.moveTo(self.landingMouthP[0], self.landingMouthP[1] + oy)
					ctx.quadraticCurveTo(self.landingMouthP[2], self.landingMouthP[3] + oy, self.landingMouthP[4], self.landingMouthP[5] + oy)
					ctx.stroke()
				}
				ctx.restore()

				ctx.draw()
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
					self.drawShadowSprite()
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
				this.drawShadowSprite()
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

				// 清除旧会话（塔罗进入不需要默认欢迎语）
				if (this.streamAbort) { this.streamAbort.abort(); this.streamAbort = null }
				this.shadowSessionId = '';
				this.pendingClarification = false;
				this.messageList = [];
				try {
					uni.removeStorageSync(STORAGE_KEY_SESSION);
					uni.removeStorageSync(STORAGE_KEY_MESSAGES);
					uni.removeStorageSync(STORAGE_KEY_PENDING);
					uni.setStorageSync(STORAGE_KEY_VERSION, STORAGE_VERSION);
				} catch (e) {}

				this.fromTarot = true;
				this.tarotReading = this.buildTarotReading(session);

				var intent = session.intent || {};
				var question = String(intent.question || intent.tagLabel || '帮我解读塔罗牌').trim();
				var cards = session.cards || [];

				// 在消息列表显示用户问题
				this.messageList.push({ role: 'user', content: question });
				this.isTyping = true;
				this.saveChatSession();
				this.scrollToBottom('msg-typing');

				var self = this;
				var userId = getApiUserId();
				if (!userId) {
					self.isTyping = false;
					self.messageList.push({ role: 'ai', content: '请先登录后再与影子对话。' });
					self.saveChatSession();
					self.scrollToBottom();
					return;
				}

				var payload = {
					user_id: userId,
					question: question,
					category: 'TAROT'
				};
				var openid = getApiOpenid();
				if (openid && openid.indexOf('p_') !== 0) {
					payload.open_id = openid;
				}
				payload.tarot_cards = cards;

				// 流式调用
				var firstToken = true;
				var scrollTimer = null;

				this.streamAbort = streamShadowChat(payload, {
					onSession: function(data) {
						if (data.session_id) {
							self.shadowSessionId = data.session_id;
						}
					},
					onToken: function(data) {
						var text = data.text || '';
						if (!text) return;
						if (firstToken) {
							firstToken = false;
							self.isTyping = false;
							self.messageList.push({ role: 'ai', content: text });
						} else {
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai') {
								self.$set(self.messageList[lastIdx], 'content', self.messageList[lastIdx].content + text);
							}
						}
						if (!scrollTimer) {
							scrollTimer = setTimeout(function() {
								self.scrollToBottom();
								scrollTimer = null;
							}, 80);
						}
					},
					onDone: function(data) {
						self.streamAbort = null;
						if (firstToken) {
							firstToken = false;
							self.isTyping = false;
							self.messageList.push({ role: 'ai', content: data.reply || '' });
						} else {
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai' && data.reply) {
								self.$set(self.messageList[lastIdx], 'content', data.reply);
							}
						}
						if (data.session_id) {
							self.shadowSessionId = data.session_id;
						}
						if (data.phase === 'clarifying') {
							self.pendingClarification = true;
						}
						self.saveChatSession();
						self.scrollToBottom();

						// 前端侧持久化塔罗会话
						if (data.phase === 'complete') {
							self._persistSpecialistSession('TAROT', { cards: cards }, question, data);
						}
					},
					onError: function(message) {
						self.streamAbort = null;
						self.isTyping = false;
						if (firstToken) {
							self.messageList.push({ role: 'ai', content: '出了点问题：' + (message || '请求失败') });
						} else {
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai') {
								self.$set(self.messageList[lastIdx], 'content', self.messageList[lastIdx].content + '\n\n[错误] ' + (message || '请求失败'));
							}
						}
						self.saveChatSession();
						self.scrollToBottom();
					}
				});
			},
			checkSpecialistSession() {
				var raw = '';
				try { raw = uni.getStorageSync('shadowSpecialistSession') || ''; } catch (e) {}
				if (!raw) return;
				try { uni.removeStorageSync('shadowSpecialistSession'); } catch (e) {}

				var session = {};
				try { session = JSON.parse(raw); } catch (e) { return; }
				var category = session.category || '';
				var specialistData = session.specialistData || null;
				var question = String(session.question || '').trim();
				if (!category || !specialistData) return;

				// 清除旧会话（专项进入不需要默认欢迎语）
				if (this.streamAbort) { this.streamAbort.abort(); this.streamAbort = null }
				this.shadowSessionId = '';
				this.pendingClarification = false;
				this.messageList = [];
				try {
					uni.removeStorageSync(STORAGE_KEY_SESSION);
					uni.removeStorageSync(STORAGE_KEY_MESSAGES);
					uni.removeStorageSync(STORAGE_KEY_PENDING);
					uni.setStorageSync(STORAGE_KEY_VERSION, STORAGE_VERSION);
				} catch (e) {}

				var self = this;
				// 先在消息列表显示用户问题
				this.messageList.push({ role: 'user', content: question });
				this.isTyping = true;
				this.saveChatSession();
				this.scrollToBottom('msg-typing');

				var userId = getApiUserId();
				if (!userId) {
					self.isTyping = false;
					self.messageList.push({ role: 'ai', content: '请先登录后再与影子对话。' });
					self.saveChatSession();
					self.scrollToBottom();
					return;
				}

				var payload = {
					user_id: userId,
					question: question,
					category: category
				};
				var openid = getApiOpenid();
				if (openid && openid.indexOf('p_') !== 0) {
					payload.open_id = openid;
				}

				// 根据分类设置专项数据
				if (category === 'ZODIAC') {
					payload.zodiac_data = specialistData;
				} else if (category === 'EMOTION_LOG') {
					payload.emotion_log = specialistData;
				} else if (category === 'TAROT') {
					payload.tarot_cards = specialistData.cards || specialistData;
				}

				// 流式调用
				var firstToken = true;
				var scrollTimer = null;

				this.streamAbort = streamShadowChat(payload, {
					onSession: function(data) {
						if (data.session_id) {
							self.shadowSessionId = data.session_id;
						}
					},
					onToken: function(data) {
						var text = data.text || '';
						if (!text) return;
						if (firstToken) {
							firstToken = false;
							self.isTyping = false;
							self.messageList.push({ role: 'ai', content: text });
						} else {
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai') {
								self.$set(self.messageList[lastIdx], 'content', self.messageList[lastIdx].content + text);
							}
						}
						if (!scrollTimer) {
							scrollTimer = setTimeout(function() {
								self.scrollToBottom();
								scrollTimer = null;
							}, 80);
						}
					},
					onDone: function(data) {
						self.streamAbort = null;
						if (firstToken) {
							firstToken = false;
							self.isTyping = false;
							self.messageList.push({ role: 'ai', content: data.reply || '' });
						} else {
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai' && data.reply) {
								self.$set(self.messageList[lastIdx], 'content', data.reply);
							}
						}
						if (data.session_id) {
							self.shadowSessionId = data.session_id;
						}
						if (data.phase === 'clarifying') {
							self.pendingClarification = true;
						}
						self.saveChatSession();
						self.scrollToBottom();

						// 前端侧持久化塔罗/专项会话（作为后端自动持久化的补充备份）
						if (category && data.phase === 'complete') {
							self._persistSpecialistSession(category, specialistData, question, data);
						}
					},
					onError: function(message) {
						self.streamAbort = null;
						self.isTyping = false;
						if (firstToken) {
							self.messageList.push({ role: 'ai', content: '出了点问题：' + (message || '请求失败') });
						} else {
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai') {
								self.$set(self.messageList[lastIdx], 'content', self.messageList[lastIdx].content + '\n\n[错误] ' + (message || '请求失败'));
							}
						}
						self.saveChatSession();
						self.scrollToBottom();
					}
				});
			},
			_persistSpecialistSession(cat, specialistData, question, doneData) {
				// 前端侧保存专项会话记录到数据库（补充后端自动持久化）
				var uid = getApiUserId();
				if (!uid) return;
				var drawId = '';
				try { drawId = uni.getStorageSync('tarotDrawId') || ''; } catch (e) {}

				// 构建聊天消息快照
				var msgs = [];
				for (var i = 0; i < this.messageList.length; i++) {
					var m = this.messageList[i];
					if (m.content) {
						msgs.push({ role: m.role === 'user' ? 'user' : 'ai', content: m.content });
					}
				}

				var payload = {
					user_id: uid,
					draw_id: drawId || null,
					session_id: doneData.session_id || this.shadowSessionId || '',
					category: cat,
					question: question || '',
					ai_reply: doneData.reply || '',
					phase: doneData.phase || 'complete',
					chat_messages: msgs,
					message_count: msgs.length
				};

				// 塔罗专项：附带牌面和主题数据
				if (cat === 'TAROT' && specialistData) {
					var cards = specialistData.cards || specialistData;
					if (Array.isArray(cards)) {
						payload.cards_json = cards;
					}
					var intentRaw = '';
					try { intentRaw = uni.getStorageSync('tarotIntent') || ''; } catch (e) {}
					if (intentRaw) {
						try {
							var intent = JSON.parse(intentRaw);
							payload.theme_tag_id = intent.tagId || null;
							payload.theme_tag_label = intent.tagLabel || null;
							if (intent.question && !payload.question) {
								payload.question = intent.question;
							}
						} catch (e2) {}
					}
				}

				postTarotSession(payload).catch(function(err) {
					console.warn('[shadow] 专项会话保存失败（后端已自动持久化，此为补充）', err);
				});
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

				// 取消上一次未完成的流
				if (this.streamAbort) {
					this.streamAbort.abort();
					this.streamAbort = null;
				}
				
				var userMsg = this.inputText.trim();
				this.messageList.push({
					role: 'user',
					content: userMsg
				});
				this.inputText = '';
				this.saveChatSession();
				
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
				self.saveChatSession();
				self.scrollToBottom();
				return;
			}

				var payload = {
					user_id: userId,
					question: userMsg
				};

				// 传递 open_id（仅真实微信 open_id）
				var openid = getApiOpenid();
				if (openid && openid.indexOf('p_') !== 0) {
					payload.open_id = openid;
				}

				// 两轮对话：如果有 pendingClarification，把用户当前消息作为 supplements
				if (this.pendingClarification) {
					payload.supplements = userMsg;
					this.pendingClarification = false;
				}
				if (this.shadowSessionId) {
					payload.session_id = this.shadowSessionId;
				}

				// ── 流式调用 ──
				var firstToken = true;
				var scrollTimer = null;

				this.streamAbort = streamShadowChat(payload, {
					onSession: function(data) {
						if (data.session_id) {
							self.shadowSessionId = data.session_id;
						}
					},
					onToken: function(data) {
						var text = data.text || '';
						if (!text) return;

						if (firstToken) {
							firstToken = false;
							self.isTyping = false;
							self.messageList.push({ role: 'ai', content: text });
						} else {
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai') {
								self.$set(self.messageList[lastIdx], 'content', self.messageList[lastIdx].content + text);
							}
						}

						// 节流滚动：每 80ms 最多触发一次
						if (!scrollTimer) {
							scrollTimer = setTimeout(function() {
								self.scrollToBottom();
								scrollTimer = null;
							}, 80);
						}
					},
					onDone: function(data) {
						self.streamAbort = null;

						if (firstToken) {
							// 没收到 token 但收到了 done（边界情况），用 reply
							firstToken = false;
							self.isTyping = false;
							self.messageList.push({ role: 'ai', content: data.reply || '' });
						} else {
							// 用 done 中的完整 reply 替换，确保最终内容准确
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai' && data.reply) {
								self.$set(self.messageList[lastIdx], 'content', data.reply);
							}
						}

						if (data.session_id) {
							self.shadowSessionId = data.session_id;
						}
						if (data.phase === 'clarifying') {
							self.pendingClarification = true;
						}

						self.saveChatSession();
						self.scrollToBottom();
					},
					onError: function(message) {
						self.streamAbort = null;
						self.isTyping = false;

						if (firstToken) {
							self.messageList.push({
								role: 'ai',
								content: '出了点问题：' + (message || '请求失败')
							});
						} else {
							var lastIdx = self.messageList.length - 1;
							if (lastIdx >= 0 && self.messageList[lastIdx].role === 'ai') {
								self.$set(self.messageList[lastIdx], 'content', self.messageList[lastIdx].content + '\n\n[错误] ' + (message || '请求失败'));
							}
						}

						self.saveChatSession();
						self.scrollToBottom();
					}
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
			radial-gradient(ellipse 100% 60% at 50% 0%, rgba(200, 188, 255, 0.35) 0%, rgba(200, 188, 255, 0.10) 40%, transparent 68%),
			linear-gradient(180deg, #faf8ff 0%, #f5f1fc 30%, #efeaf9 100%);
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
		background: radial-gradient(ellipse at 50% 18%, rgba(210,195,255,0.38) 0%, rgba(210,195,255,0.08) 45%, transparent 72%);
		pointer-events: none; z-index: 0;
	}

	/* ===== 顶部导航 ===== */
	.nav-header {
		position: fixed; top: 0; left: 0; width: 100%;
		padding-top: env(safe-area-inset-top);
		background: rgba(250, 247, 255, 0.82);
		backdrop-filter: blur(32px);
		-webkit-backdrop-filter: blur(32px);
		z-index: 100;
		display: flex; align-items: center; justify-content: center;
		height: calc(env(safe-area-inset-top) + 44px);
		box-sizing: border-box;
		border-bottom: 1rpx solid rgba(210, 200, 235, 0.40);
	}
	.nav-back {
		position: absolute; left: 24rpx;
		width: 64rpx; height: 64rpx;
		display: flex; align-items: center; justify-content: center;
		border-radius: 50%;
		background: rgba(255,255,255,0.88);
		border: 1rpx solid rgba(208, 200, 235, 0.55);
		box-shadow: 0 4rpx 16rpx rgba(140, 125, 200, 0.10);
		transition: transform 0.18s ease;
	}
	.nav-back:active { transform: scale(0.90); }
	.nav-back-t { font-size: 36rpx; color: #5e5480; margin-top: -3rpx; }
	.page-title {
		font-size: 34rpx; font-weight: 600;
		color: #322c52; letter-spacing: 3rpx;
	}
	.nav-new-chat {
		position: absolute; right: 24rpx;
		padding: 12rpx 26rpx;
		border-radius: 28rpx;
		background: rgba(138, 118, 200, 0.07);
		border: 1rpx solid rgba(138, 118, 200, 0.14);
		transition: all 0.18s ease;
	}
	.nav-new-chat:active {
		background: rgba(138, 118, 200, 0.15);
		transform: scale(0.95);
	}
	.nav-new-chat-text {
		font-size: 23rpx; color: #7b6db5; font-weight: 600;
		letter-spacing: 1rpx;
	}

	/* ===== 聊天滚动区 ===== */
	.chat-scroll { flex: 1; height: 100vh; box-sizing: border-box; padding-top: calc(env(safe-area-inset-top) + 44px + 10rpx); padding-bottom: calc(260rpx + env(safe-area-inset-bottom)); }
	.chat-list { padding: 28rpx 28rpx 20rpx; display: flex; flex-direction: column; gap: 8rpx; }
	.chat-list--landing {
		min-height: calc(100vh - 320rpx);
		justify-content: flex-start;
		padding-top: 16rpx;
	}

	/* ===== 欢迎区 ===== */
	.welcome-panel {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 0 24rpx 0;
		margin-top: -12rpx;
	}
	.landing-hero-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 8rpx 0 0;
		margin-bottom: 28rpx;
	}
	.landing-mascot-wrap {
		width: 180rpx;
		height: 138rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 18rpx;
		transform-origin: 50% 62%;
		will-change: transform;
	}
	.landing-mascot-canvas {
		width: 168rpx;
		height: 130rpx;
		display: block;
		filter: drop-shadow(0 14rpx 26rpx rgba(190, 172, 255, 0.25));
	}
	
	.landing-caption {
		font-size: 25rpx;
		line-height: 1.65;
		color: rgba(115, 108, 148, 0.62);
		text-align: center;
		padding: 0 20rpx;
		letter-spacing: 1rpx;
	}
	.landing-copy {
		display: flex;
		flex-direction: column;
		align-items: center;
		max-width: 580rpx;
	}
	.landing-title {
		font-size: 56rpx;
		line-height: 1.25;
		font-weight: 700;
		color: #332d52;
		text-align: center;
		letter-spacing: 3rpx;
	}
	.landing-subtitle {
		margin-top: 18rpx;
		font-size: 27rpx;
		line-height: 1.75;
		color: rgba(105, 98, 138, 0.58);
		text-align: center;
		letter-spacing: 1rpx;
	}

	/* ===== 塔罗问题气泡 ===== */
	.tarot-q-wrap {
		display: flex; justify-content: flex-end;
		margin-bottom: 28rpx;
	}
	.tarot-q-bubble {
		max-width: 66%;
		padding: 22rpx 30rpx;
		border-radius: 26rpx 26rpx 8rpx 26rpx;
		background: linear-gradient(145deg, #9685ee 0%, #7d6bd6 100%);
		box-shadow: 0 12rpx 30rpx rgba(130, 115, 220, 0.30), 0 3rpx 8rpx rgba(130, 115, 220, 0.10);
	}
	.tarot-q-text {
		font-size: 29rpx; color: rgba(255,255,255,0.97);
		line-height: 1.64; font-weight: 500;
		letter-spacing: 0.3rpx;
	}

	/* ===== 塔罗解读卡片 ===== */
	.tarot-reading-card {
		margin-bottom: 32rpx;
		padding: 28rpx 24rpx 24rpx;
		border-radius: 26rpx;
		background: rgba(255,255,255,0.92);
		box-shadow:
			0 16rpx 40rpx rgba(145, 140, 190, 0.12),
			0 4rpx 10rpx rgba(145, 140, 190, 0.05),
			inset 0 1rpx 0 rgba(255,255,255,0.92);
		border: 1rpx solid rgba(212, 208, 235, 0.58);
	}
	.trc-head { display: flex; align-items: center; margin-bottom: 24rpx; }
	.trc-icon-ring {
		width: 56rpx; height: 56rpx; border-radius: 14rpx;
		background: linear-gradient(145deg, rgba(190,175,255,0.26), rgba(142,112,215,0.18));
		border: 1rpx solid rgba(190,175,255,0.16);
		display: flex; align-items: center; justify-content: center;
		box-shadow: 0 4rpx 14rpx rgba(110, 85, 190, 0.14);
		margin-right: 16rpx;
	}
	.trc-icon-glyph { font-size: 24rpx; color: rgba(205,192,255,0.88); }
	.trc-head-text { flex: 1; display: flex; flex-direction: column; }
	.trc-head-title {
		font-size: 26rpx; font-weight: 700;
		color: #3a3d60; line-height: 1.38;
		letter-spacing: 0.5rpx;
	}
	.trc-head-sub {
		margin-top: 5rpx; font-size: 21rpx;
		color: rgba(122, 128, 162, 0.58); line-height: 1.42;
		letter-spacing: 0.5rpx;
	}

	/* 三张牌 */
	.trc-cards-strip {
		display: flex; justify-content: center; gap: 14rpx;
		padding: 20rpx 8rpx;
		border-radius: 20rpx;
		background: linear-gradient(135deg, rgba(240,238,255,0.82), rgba(232,228,250,0.70));
		border: 1rpx solid rgba(212, 208, 235, 0.50);
		margin-bottom: 12rpx;
	}
	.trc-card-col { flex: 1; display: flex; flex-direction: column; align-items: center; }
	.trc-card {
		width: 100%; max-width: 152rpx; height: 214rpx;
		border-radius: 16rpx; position: relative;
		box-shadow: 0 10rpx 28rpx rgba(15, 12, 30, 0.42);
		display: flex; flex-direction: column;
		align-items: center; justify-content: center;
		padding: 10rpx 8rpx;
		border: 1rpx solid rgba(255,255,255,0.10);
	}
	.trc-card-num {
		position: absolute; top: 10rpx; left: 12rpx;
		font-size: 17rpx; font-weight: 700;
		color: rgba(255,255,255,0.16); font-style: italic;
	}
	.trc-card-ring {
		width: 48rpx; height: 48rpx; border-radius: 50%;
		background: rgba(255,255,255,0.11);
		border: 1rpx solid rgba(255,255,255,0.13);
		display: flex; align-items: center; justify-content: center;
		margin-bottom: 8rpx;
	}
	.trc-card-sym { font-size: 24rpx; color: rgba(255,255,255,0.52); }
	.trc-card-name-inner {
		font-size: 20rpx; font-weight: 700;
		color: rgba(255,255,255,0.90); text-align: center;
	}
	.trc-card-label {
		margin-top: 12rpx; font-size: 22rpx;
		font-weight: 600; color: rgba(82, 88, 128, 0.75);
		letter-spacing: 0.5rpx;
	}

	.trc-divider {
		height: 1rpx; margin: 22rpx 0 20rpx;
		background: linear-gradient(90deg, transparent, rgba(160,148,205,0.14), transparent);
	}

	/* 解读段落 */
	.trc-reading-body { display: flex; flex-direction: column; gap: 20rpx; }
	.trc-section { padding: 0 2rpx; }
	.trc-section-title {
		display: block; font-size: 26rpx; font-weight: 700;
		color: #3c4068; line-height: 1.55;
		letter-spacing: 0.5rpx;
	}
	.trc-section-content {
		display: block; margin-top: 8rpx;
		font-size: 28rpx; line-height: 1.64;
		color: rgba(95, 102, 138, 0.76);
		letter-spacing: 0.3rpx;
	}

	/* 工具条 */
	.trc-tools { display: flex; gap: 12rpx; margin-top: 26rpx; flex-wrap: wrap; }
	.trc-tool-chip {
		display: flex; align-items: center; gap: 8rpx;
		padding: 14rpx 20rpx;
		border-radius: 18rpx;
		background: rgba(245,244,255,0.94);
		border: 1rpx solid rgba(212, 208, 235, 0.58);
		transition: all 0.18s ease;
	}
	.trc-tool-hover { background: rgba(230,228,250,0.96); transform: scale(0.96); }
	.trc-tool-emoji { font-size: 24rpx; }
	.trc-tool-text { font-size: 22rpx; color: rgba(82, 88, 128, 0.78); font-weight: 600; letter-spacing: 0.5rpx; }

	/* ===== 消息通用 ===== */
	.message-row {
		display: flex;
		margin-bottom: 32rpx;
		align-items: flex-start;
		animation: msgFadeIn 0.32s ease-out;
	}
	.row-user { justify-content: flex-end; }
	.row-ai { justify-content: flex-start; }

	@keyframes msgFadeIn {
		from { opacity: 0; transform: translateY(10rpx); }
		to { opacity: 1; transform: translateY(0); }
	}

	.avatar {
		width: 76rpx; height: 76rpx; border-radius: 50%;
		flex-shrink: 0; overflow: hidden;
		transition: transform 0.18s ease;
	}
	.avatar:active { transform: scale(0.92); }
	.ai-avatar {
		background: linear-gradient(180deg, #d4c8f5 0%, #b8a8e8 40%, #9e8cd8 100%);
		border: 1rpx solid rgba(200, 190, 240, 0.45);
		display: flex; align-items: center; justify-content: center;
		margin-right: 14rpx;
		box-shadow: 0 4rpx 16rpx rgba(140, 125, 210, 0.15);
	}
	.ai-avatar-silhouette {
		width: 44rpx; height: 56rpx;
		background: rgba(120, 105, 175, 0.35);
		border-radius: 50% 50% 45% 45% / 55% 55% 45% 45%;
		filter: blur(4rpx);
		position: relative;
	}
	.ai-avatar-silhouette::after {
		content: '';
		position: absolute;
		bottom: -14rpx;
		left: 50%;
		transform: translateX(-50%);
		width: 32rpx; height: 18rpx;
		background: rgba(120, 105, 175, 0.30);
		border-radius: 50%;
		filter: blur(3rpx);
	}
	.user-avatar {
		margin-left: 14rpx;
		background-color: rgba(235, 234, 248, 0.86);
		background-size: cover;
		background-position: center;
		background-repeat: no-repeat;
		border: 1rpx solid rgba(212, 208, 235, 0.58);
		box-shadow: 0 4rpx 12rpx rgba(140, 130, 196, 0.10);
	}
	.user-avatar-placeholder {
		width: 100%; height: 100%;
		display: flex; align-items: center; justify-content: center;
		background: linear-gradient(135deg, #e8e4f6, #ddd8f0);
	}
	.user-avatar-icon { font-size: 36rpx; opacity: 0.45; }

	.message-main {
		max-width: 74%;
		padding: 24rpx 28rpx;
		border-radius: 26rpx;
		font-size: 28rpx;
		line-height: 1.68;
		word-break: break-all;
	}
	.message-main .message-text {
		display: block;
		white-space: pre-wrap;
		word-break: break-word;
		line-height: 1.68;
		letter-spacing: 0.4rpx;
	}
	.message-role {
		display: inline-block;
		margin-bottom: 8rpx;
		font-size: 22rpx;
		font-weight: 500;
		color: rgba(140, 132, 175, 0.55);
		letter-spacing: 1rpx;
	}
	.message-main--ai,
	.bubble-ai {
		background: rgba(255,255,255,0.94);
		color: #3d3a52;
		border-top-left-radius: 8rpx;
		box-shadow: 0 6rpx 20rpx rgba(155, 148, 205, 0.08), 0 2rpx 6rpx rgba(155, 148, 205, 0.04);
		border: 1rpx solid rgba(225, 222, 242, 0.60);
	}
	.message-main--ai .message-text {
		font-size: 27rpx;
		line-height: 1.72;
		letter-spacing: 0.5rpx;
		color: #4a4562;
	}
	.message-main--user {
		background: linear-gradient(145deg, #9685ee, #7d6bd6);
		color: rgba(255,255,255,0.97);
		border-top-right-radius: 8rpx;
		box-shadow: 0 10rpx 26rpx rgba(130, 115, 220, 0.22), 0 3rpx 8rpx rgba(130, 115, 220, 0.08);
	}
	.message-main--user .message-text {
		letter-spacing: 0.3rpx;
	}

	/* 打字动画 */
	.typing-bubble { display: flex; align-items: center; height: 48rpx; padding: 22rpx 28rpx; min-width: 120rpx; }
	.dot {
		width: 13rpx; height: 13rpx;
		background: rgba(145, 135, 210, 0.48); border-radius: 50%;
		margin: 0 7rpx;
		animation: bounce 1.4s infinite ease-in-out both;
	}
	.dot:nth-child(1) { animation-delay: -0.32s; }
	.dot:nth-child(2) { animation-delay: -0.16s; }
	@keyframes bounce {
		0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
		40% { transform: scale(1); opacity: 1; }
	}

	/* ===== 底部输入栏 ===== */
	.clarify-hint-bar {
		position: fixed; left: 0; width: 100%;
		bottom: calc(114rpx + env(safe-area-inset-bottom));
		background: rgba(138, 118, 200, 0.05);
		padding: 10rpx 28rpx;
		box-sizing: border-box;
		display: flex; align-items: center; justify-content: space-between;
		z-index: 91;
		height: 54rpx;
	}
	.clarify-hint-text {
		font-size: 22rpx; color: #8278b5; font-weight: 400;
		letter-spacing: 1rpx;
	}
	.clarify-hint-new {
		font-size: 22rpx; color: #8278b5; font-weight: 600;
		text-decoration: underline;
		letter-spacing: 1rpx;
	}
	.input-bar {
		position: fixed; left: 0; width: 100%;
		background: rgba(250, 247, 255, 0.88);
		backdrop-filter: blur(26px);
		-webkit-backdrop-filter: blur(26px);
		padding: 14rpx 20rpx;
		box-sizing: border-box;
		display: flex; align-items: center;
		border-top: 1rpx solid rgba(210, 200, 235, 0.44);
		z-index: 90;
		transition: bottom 0.25s ease;
	}
	.chat-input {
		flex: 1; height: 80rpx;
		background: rgba(255, 255, 255, 0.94);
		border-radius: 999rpx;
		padding: 0 32rpx;
		font-size: 29rpx; color: #2e2c37;
		font-weight: 400;
		letter-spacing: 0.6rpx;
		border: 1rpx solid rgba(210, 200, 235, 0.58);
		box-shadow: inset 0 2rpx 6rpx rgba(140, 130, 196, 0.03);
		transition: border-color 0.2s ease, box-shadow 0.2s ease;
	}
	.chat-input:focus {
		border-color: rgba(155, 135, 215, 0.50);
		box-shadow: inset 0 2rpx 6rpx rgba(140, 130, 196, 0.03), 0 0 0 4rpx rgba(155, 135, 215, 0.07);
	}
	.input-placeholder { color: rgba(155, 148, 175, 0.65); letter-spacing: 1rpx; }
	.send-btn {
		margin-left: 14rpx;
		min-width: 96rpx;
		height: 72rpx;
		padding: 0 24rpx;
		border-radius: 999rpx;
		background: rgba(248, 246, 255, 0.96);
		border: 1rpx solid rgba(210, 200, 235, 0.55);
		display: flex; align-items: center; justify-content: center;
		transition: all 0.22s ease;
		box-shadow: none;
	}
	.send-btn:active { transform: scale(0.93); }
	.send-btn-t { font-size: 27rpx; color: #625a82; font-weight: 700; letter-spacing: 2rpx; }
	.btn-active {
		background: linear-gradient(145deg, #9685ee, #7d6bd6);
		border-color: transparent;
		box-shadow: 0 8rpx 24rpx rgba(130, 115, 220, 0.28);
	}
	.btn-active .send-btn-t { color: rgba(255,255,255,0.97); }
	.btn-active:active {
		transform: scale(0.93);
		box-shadow: 0 5rpx 14rpx rgba(130, 115, 220, 0.18);
	}

	/* 自定义弹窗 */
	.modal-mask {
		position: fixed; top: 0; left: 0; right: 0; bottom: 0;
		background: rgba(40, 35, 60, 0.45);
		z-index: 999;
		display: flex; align-items: center; justify-content: center;
	}
	.modal-box {
		width: 520rpx;
		background: #fff;
		border-radius: 24rpx;
		padding: 36rpx 32rpx 24rpx;
		box-shadow: 0 16rpx 48rpx rgba(80, 70, 120, 0.15), 0 4rpx 12rpx rgba(80, 70, 120, 0.06);
		animation: modalIn 0.2s ease-out both;
	}
	@keyframes modalIn {
		from { opacity: 0; transform: scale(0.94) translateY(16rpx); }
		to { opacity: 1; transform: scale(1) translateY(0); }
	}
	.modal-title {
		display: block; text-align: center;
		font-size: 28rpx; font-weight: 600; color: #3d3a52;
		margin-bottom: 12rpx; letter-spacing: 0.5rpx;
	}
	.modal-desc {
		display: block; text-align: center;
		font-size: 24rpx; color: #8b82a6;
		line-height: 1.4; margin-bottom: 28rpx;
	}
	.modal-btns {
		display: flex; border-top: 1rpx solid rgba(210, 206, 230, 0.45);
	}
	.modal-btn {
		flex: 1; text-align: center; padding: 18rpx 0;
		font-size: 27rpx;
	}
	.modal-btn-cancel { color: #9b92b2; }
	.modal-btn-cancel:active { background: rgba(155,146,178,0.06); }
	.modal-btn-confirm { color: #7d6bd6; font-weight: 600; position: relative; }
	.modal-btn-confirm::before {
		content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
		width: 1rpx; height: 32rpx; background: rgba(200,195,225,0.60);
	}
	.modal-btn-confirm:active { background: rgba(125,107,214,0.05); }
</style>
