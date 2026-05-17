<template>
<view class="page" :style="pageStyle">
	<!-- 星空背景 -->
	<view class="star-layer">
		<view v-for="(s,i) in stars" :key="'s'+i" class="star" :style="s"></view>
	</view>
	<view class="orb orb-a"></view>

	<!-- 顶部导航 -->
	<view class="nav-bar">
		<view class="nav-left" @tap="goBack">
			<text class="back-icon">←</text>
		</view>
		<text class="nav-title">心理健康自测</text>
		<text class="nav-en">MENTAL HEALTH</text>
	</view>

	<!-- 进度条 -->
	<view class="progress-wrap" v-if="phase === 'test'">
		<view class="progress-bg">
			<view class="progress-fill" :style="{ width: progressPct + '%' }"></view>
		</view>
		<text class="progress-text">{{ curQ + 1 }} / {{ questions.length }}</text>
	</view>

	<!-- 答题阶段 -->
	<view v-if="phase === 'test'" class="test-phase">
		<view class="q-card">
			<view class="q-num">
				<text class="q-num-label">Q{{ curQ + 1 }}</text>
				<text class="q-dim-tag" :style="{ background: dimColor }">{{ dimLabel }}</text>
			</view>
			<text class="q-text">{{ questions[curQ].text }}</text>
		</view>
		<view class="opts">
			<view class="opt-row" v-for="(opt, oi) in freqOpts" :key="oi"
				:class="{ active: answers[curQ] === oi }"
				:style="answers[curQ] === oi ? { background: dimColor, borderColor: dimColor } : {}"
				@tap="selectOpt(oi)">
				<view class="opt-radio" :class="{ checked: answers[curQ] === oi }"
					:style="answers[curQ] === oi ? { borderColor: dimColor } : {}">
					<view class="opt-dot" v-if="answers[curQ] === oi" :style="{ background: dimColor }"></view>
				</view>
				<text class="opt-text" :style="answers[curQ] === oi ? { color: '#fff' } : {}">{{ opt }}</text>
			</view>
		</view>
		<view class="btns">
			<view class="btn-prev" v-if="curQ > 0" @tap="prevQ"><text>上一题</text></view>
			<view class="btn-next" :style="{ background: dimColor }" @tap="nextQ">
				<text>{{ curQ < questions.length - 1 ? '下一题' : '查看结果' }}</text>
			</view>
		</view>
	</view>

	<!-- 结果阶段 -->
	<scroll-view v-if="phase === 'result'" scroll-y class="result-scroll">
		<view class="result-phase">

			<!-- 总分卡片 -->
			<view class="hero-card" :style="{ borderColor: levelColor }">
				<view class="hero-glow" :style="{ background: 'radial-gradient(circle,' + levelColor + '22,transparent 65%)' }"></view>
				<text class="hero-icon">{{ levelData.icon }}</text>
				<text class="hero-level" :style="{ color: levelColor }">{{ levelData.level }}</text>
				<text class="hero-code" :style="{ color: levelColor }">{{ totalScore }}分</text>
				<text class="hero-desc">{{ levelData.desc }}</text>
			</view>

			<!-- 五维分布 -->
			<view class="section-card">
				<text class="sec-title">五维健康指数</text>
				<view class="dim-list">
					<view class="dim-row" v-for="(d, di) in dimResults" :key="di">
						<view class="dim-left">
							<text class="dim-icon">{{ d.icon }}</text>
							<text class="dim-name">{{ d.name }}</text>
						</view>
						<view class="dim-bar-wrap">
							<view class="dim-bar-bg">
								<view class="dim-bar-fill" :style="{ width: d.pct + '%', background: d.color }"></view>
							</view>
						</view>
						<text class="dim-pct" :style="{ color: d.color }">{{ d.pct }}%</text>
						<text class="dim-tag" :style="{ color: d.tagColor }">{{ d.tag }}</text>
					</view>
				</view>
			</view>

			<!-- 维度详情 -->
			<view class="section-card" v-for="(d, di) in dimResults" :key="'d'+di">
				<view class="detail-header">
					<text class="detail-icon">{{ d.icon }}</text>
					<view class="detail-info">
						<text class="detail-name">{{ d.name }}</text>
						<text class="detail-tag" :style="{ color: d.tagColor }">{{ d.tag }}</text>
					</view>
				</view>
				<text class="detail-desc">{{ d.desc }}</text>
				<view class="advice-list">
					<view class="advice-item" v-for="(a, ai) in d.advices" :key="ai">
						<text class="advice-bullet" :style="{ color: d.color }">✦</text>
						<text class="advice-text">{{ a }}</text>
					</view>
				</view>
			</view>

			<!-- 温馨提示 -->
			<view class="section-card warm-card">
				<text class="sec-title">温馨提示</text>
				<text class="warm-text">{{ warmTip }}</text>
			</view>

			<!-- 操作按钮 -->
			<view class="action-row">
				<view class="btn-retry" @tap="retest"><text>重新测试</text></view>
				<view class="btn-back" @tap="goBack"><text>返回星图</text></view>
			</view>
		</view>
	</scroll-view>
</view>
</template>

<script>
// 五大维度数据
var DIMS = [
	{ key: 'anxiety',    name: '焦虑倾向', icon: '🌊', color: '#5b8def', desc: '反映您近期感受到的紧张、不安与过度担忧程度。适度焦虑有助于保持警觉，但过高则可能影响日常生活。' },
	{ key: 'depression', name: '情绪低落', icon: '🌧️', color: '#7c6dd8', desc: '反映您近期的情绪基调、兴趣减退与愉悦感缺失程度。偶尔低落属正常，持续低落需要关注。' },
	{ key: 'stress',     name: '压力应对', icon: '⚖️', color: '#dda03f', desc: '反映您面对生活压力时的应对能力与心理韧性。良好的压力应对是心理健康的重要屏障。' },
	{ key: 'self',       name: '自我认同', icon: '🪞', color: '#d4607a', desc: '反映您对自我价值的认可程度与内在安全感。健康的自我认同是心理稳定的根基。' },
	{ key: 'social',     name: '社会连接', icon: '🤝', color: '#3ec9c1', desc: '反映您的人际关系质量与社会支持感受。良好的社会连接是心理健康的保护因素。' }
]

// 频率选项
var FREQ_OPTS = ['很少/从不', '有时', '经常', '几乎总是']

// 30道题目，每维度6题
// score: 0=很少/从不 1=有时 2=经常 3=几乎总是
// reverse: true 表示反向计分（选"很少"反而高分，代表该维度健康）
var QUESTIONS = [
	// 焦虑倾向 (6题)
	{ dim: 'anxiety', reverse: false, text: '我经常感到紧张、不安或提心吊胆。' },
	{ dim: 'anxiety', reverse: false, text: '我容易因为小事而担心，很难让自己放松下来。' },
	{ dim: 'anxiety', reverse: false, text: '我常觉得有什么不好的事情即将发生。' },
	{ dim: 'anxiety', reverse: false, text: '我很难停止脑海中的担忧想法，它们反复出现。' },
	{ dim: 'anxiety', reverse: false, text: '我会因为焦虑而出现心慌、出汗或呼吸急促。' },
	{ dim: 'anxiety', reverse: false, text: '我因紧张而难以入睡或睡眠质量差。' },
	// 情绪低落 (6题)
	{ dim: 'depression', reverse: false, text: '我经常感到心情低落、沮丧或绝望。' },
	{ dim: 'depression', reverse: false, text: '我对以前感兴趣的事情提不起劲了。' },
	{ dim: 'depression', reverse: false, text: '我感到做任何事都很费力，缺乏动力。' },
	{ dim: 'depression', reverse: false, text: '我容易哭泣或感到内心非常脆弱。' },
	{ dim: 'depression', reverse: false, text: '我觉得自己毫无价值，或对很多事感到自责。' },
	{ dim: 'depression', reverse: false, text: '我对未来感到悲观，觉得事情不会好转。' },
	// 压力应对 (6题，reverse=true，选"很少"表示该维度弱)
	{ dim: 'stress', reverse: true, text: '遇到困难时，我能够冷静分析并找到解决办法。' },
	{ dim: 'stress', reverse: true, text: '面对压力时，我能通过深呼吸、运动等方式有效调节情绪。' },
	{ dim: 'stress', reverse: true, text: '我相信自己有能力应对生活中的挑战。' },
	{ dim: 'stress', reverse: true, text: '我能在繁忙中合理分配时间，不至于过度焦虑。' },
	{ dim: 'stress', reverse: true, text: '遇到挫折后，我通常能较快恢复积极心态。' },
	{ dim: 'stress', reverse: true, text: '我能区分哪些事可以控制、哪些需要放下。' },
	// 自我认同 (6题，reverse=true)
	{ dim: 'self', reverse: true, text: '我总体上认可自己，觉得自己是值得被爱的。' },
	{ dim: 'self', reverse: true, text: '我不需要通过他人的评价来确认自己的价值。' },
	{ dim: 'self', reverse: true, text: '我能够坦然接受自己的缺点和不足。' },
	{ dim: 'self', reverse: true, text: '我清楚自己真正想要什么，不容易被他人左右。' },
	{ dim: 'self', reverse: true, text: '面对批评时，我能理性对待而不是全盘否定自己。' },
	{ dim: 'self', reverse: true, text: '我相信自己有独特的优势，不必和他人比较。' },
	// 社会连接 (6题，reverse=true)
	{ dim: 'social', reverse: true, text: '我身边有可以倾诉心事、分享喜怒哀乐的人。' },
	{ dim: 'social', reverse: true, text: '我感到自己被身边的人理解和接纳。' },
	{ dim: 'social', reverse: true, text: '遇到困难时，我愿意主动寻求他人的帮助。' },
	{ dim: 'social', reverse: true, text: '我能在人际交往中感受到温暖和归属感。' },
	{ dim: 'social', reverse: true, text: '我与家人或好友之间有稳定而良好的关系。' },
	{ dim: 'social', reverse: true, text: '我觉得自己在社交中能真实地表达自己。' }
]

// 等级判定
// 总分: 焦虑(0-18) + 低落(0-18) + 压力应对弱(0-18) + 自我认同低(0-18) + 社会连接弱(0-18) = 0-90
// 健康(压力/自我/社会)维度 reverse 计分: 选"很少"=3(该维度弱), 选"几乎总是"=0(该维度强)
function calcLevel(totalScore) {
	if (totalScore <= 18) return 0  // 良好
	if (totalScore <= 36) return 1  // 轻度
	if (totalScore <= 54) return 2  // 中度
	return 3  // 需关注
}

var LEVEL_DATA = [
	{ level: '心理健康良好', icon: '🌿', desc: '您的心理状态整体健康，各维度表现均衡。继续保持良好的生活习惯和心理调适方式。', color: '#3ec9c1' },
	{ level: '轻度波动',     icon: '🌱', desc: '您在某些方面存在轻微的心理波动，这是正常的生活起伏。适当关注并调整即可。', color: '#dda03f' },
	{ level: '中度压力',     icon: '🍂', desc: '您目前承受着一定的心理压力，部分维度需要引起重视。建议采取积极的自我调适措施。', color: '#d4607a' },
	{ level: '需要关注',     icon: '🪷', desc: '您当前的心理状态需要认真关注。建议寻求专业心理咨询师的帮助，这是一种自我关爱。', color: '#9d72ff' }
]

// 维度等级判定 (每维度0-18分)
function dimTag(score) {
	if (score <= 3) return { tag: '良好', tagColor: '#3ec9c1' }
	if (score <= 7) return { tag: '轻微', tagColor: '#dda03f' }
	if (score <= 12) return { tag: '中等', tagColor: '#d4607a' }
	return { tag: '需关注', tagColor: '#9d72ff' }
}

// 维度建议
var ADVICE_MAP = {
	anxiety: [
		'尝试每天进行10分钟正念呼吸或冥想练习',
		'将担忧写下来，区分"可控"与"不可控"事项',
		'减少咖啡因摄入，保持规律作息',
		'设定专属"担忧时间"，其余时段练习放下'
	],
	depression: [
		'每天安排一件让自己愉悦的小事，无论多小',
		'保持适度运动，哪怕只是散步15分钟',
		'尝试与信任的人倾诉内心感受',
		'如持续两周以上情绪低落，建议寻求专业帮助'
	],
	stress: [
		'学会对不合理的期望说"不"',
		'建立规律的运动习惯，释放身体紧张',
		'练习将大任务拆分为可执行的小步骤',
		'保证充足的休息和睡眠时间'
	],
	self: [
		'每天记录三件自己做得好的事情',
		'练习用温和的语气与自己对话',
		'列出自己的优势和成就，经常回顾',
		'允许自己犯错，将失败视为学习机会'
	],
	social: [
		'主动联系一位许久未交流的朋友',
		'尝试加入一个兴趣小组或社区活动',
		'练习表达真实需求，而非一味迎合他人',
		'在需要帮助时勇敢开口，接受也是一种能力'
	]
}

module.exports = {
	data: function() {
		return {
			phase: 'test',
			curQ: 0,
			answers: [],
			questions: QUESTIONS,
			freqOpts: FREQ_OPTS,
			// 结果
			totalScore: 0,
			levelData: {},
			levelColor: '',
			dimResults: [],
			warmTip: '',
			// 背景
			stars: []
		}
	},
	computed: {
		pageStyle: function() {
			return { minHeight: '100vh', background: 'linear-gradient(170deg,#0d0b1e 0%,#151231 40%,#1a1238 100%)' }
		},
		progressPct: function() {
			return Math.round(((this.curQ + 1) / this.questions.length) * 100)
		},
		dimLabel: function() {
			var q = this.questions[this.curQ]
			for (var i = 0; i < DIMS.length; i++) {
				if (DIMS[i].key === q.dim) return DIMS[i].name
			}
			return ''
		},
		dimColor: function() {
			var q = this.questions[this.curQ]
			for (var i = 0; i < DIMS.length; i++) {
				if (DIMS[i].key === q.dim) return DIMS[i].color
			}
			return '#5b8def'
		}
	},
	onLoad: function() {
		this.stars = this.makeStars()
		// 恢复已有结果
		var saved = uni.getStorageSync('mh_result')
		if (saved) {
			try {
				var d = JSON.parse(saved)
				this.totalScore = d.totalScore
				this.levelData = d.levelData
				this.levelColor = d.levelColor
				this.dimResults = d.dimResults
				this.warmTip = d.warmTip
				this.answers = d.answers || []
				this.phase = 'result'
			} catch(e) {}
		}
	},
	methods: {
		makeStars: function() {
			var arr = []
			for (var i = 0; i < 60; i++) {
				arr.push({
					position: 'absolute',
					left: Math.random() * 100 + '%',
					top: Math.random() * 100 + '%',
					width: Math.random() * 4 + 2 + 'rpx',
					height: Math.random() * 4 + 2 + 'rpx',
					background: 'rgba(255,255,255,' + (Math.random() * 0.4 + 0.1).toFixed(2) + ')',
					'border-radius': '50%'
				})
			}
			return arr
		},
		selectOpt: function(idx) {
			this.$set(this.answers, this.curQ, idx)
		},
		prevQ: function() {
			if (this.curQ > 0) this.curQ--
		},
		nextQ: function() {
			if (this.answers[this.curQ] === undefined) return
			if (this.curQ < this.questions.length - 1) {
				this.curQ++
			} else {
				this.calculateResult()
			}
		},
		calculateResult: function() {
			var self = this
			// 计算各维度得分
			// 焦虑/低落: 直接累加选项分 (0-3)，越高越差
			// 压力/自我/社会: reverse计分，选项0=3分(该维度弱), 选项3=0分(该维度强)
			var dimScores = {}
			for (var di = 0; di < DIMS.length; di++) {
				dimScores[DIMS[di].key] = 0
			}
			for (var qi = 0; qi < this.questions.length; qi++) {
				var q = this.questions[qi]
				var ansIdx = this.answers[qi] || 0
				var score = 0
				if (q.reverse) {
					// reverse: 选"很少"=该维度弱=3分, 选"几乎总是"=该维度强=0分
					score = 3 - ansIdx
				} else {
					score = ansIdx
				}
				dimScores[q.dim] += score
			}

			// 总分 (每维度0-18，5维度0-90)
			var total = 0
			for (var k in dimScores) total += dimScores[k]
			self.totalScore = total

			// 等级
			var lvlIdx = calcLevel(total)
			self.levelData = LEVEL_DATA[lvlIdx]
			self.levelColor = LEVEL_DATA[lvlIdx].color

			// 维度结果
			var dimResults = []
			for (var d = 0; d < DIMS.length; d++) {
				var dim = DIMS[d]
				var sc = dimScores[dim.key]
				var dt = dimTag(sc)
				var pct = Math.round(sc / 18 * 100)
				dimResults.push({
					key: dim.key,
					name: dim.name,
					icon: dim.icon,
					color: dim.color,
					desc: dim.desc,
					score: sc,
					pct: pct,
					tag: dt.tag,
					tagColor: dt.tagColor,
					advices: ADVICE_MAP[dim.key]
				})
			}
			self.dimResults = dimResults

			// 温馨提示
			var tips = [
				'本测试仅作为自我觉察的参考工具，不能替代专业诊断。如果您持续感到困扰，请勇敢寻求心理咨询师的帮助——这不是软弱，而是自我关爱的勇气。',
				'心理健康和身体健康一样重要，偶尔的波动是正常的。重要的是觉察、接纳并采取行动。',
				'每个人都会经历低谷期，这不代表你不坚强。寻求帮助是智慧的选择，就像生病了要看医生一样自然。'
			]
			self.warmTip = tips[lvlIdx >= 2 ? 2 : lvlIdx]

			// 保存
			self.phase = 'result'
			setTimeout(function() {
				uni.setStorageSync('mh_result', JSON.stringify({
					totalScore: self.totalScore,
					levelData: self.levelData,
					levelColor: self.levelColor,
					dimResults: self.dimResults,
					warmTip: self.warmTip,
					answers: self.answers
				}))
				self._saveToDb()
			}, 200)
		},
		retest: function() {
			this.phase = 'test'
			this.curQ = 0
			this.answers = []
			this.totalScore = 0
			this.levelData = {}
			this.levelColor = ''
			this.dimResults = []
			this.warmTip = ''
			uni.removeStorageSync('mh_result')
		},
		goBack: function() {
			uni.navigateBack({ delta: 1 })
		},
		_saveToDb: function() {
			var uid = 0
			try { uid = Number(uni.getStorageSync('xinyu_user_id')) || 0 } catch(e) {}
			if (!uid) return
			var self = this
			var summary = self.levelData.level + '(' + self.totalScore + '分)'
			var scores = {}
			for (var i = 0; i < self.dimResults.length; i++) scores[self.dimResults[i].key] = self.dimResults[i].score
			uni.request({
				url: (typeof SHADOW_API_BASE !== 'undefined' ? SHADOW_API_BASE : 'http://43.143.169.226') + '/api/assessments/submit',
				method: 'POST',
				header: { 'Content-Type': 'application/json' },
				data: {
					user_id: uid,
					test_type: 'mh',
					summary: summary,
					result_json: { totalScore: self.totalScore, levelData: self.levelData, levelColor: self.levelColor, dimResults: self.dimResults, warmTip: self.warmTip },
					score_json: scores,
					answers_json: self.answers,
					question_count: 30
				}
			})
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; padding-bottom: 60rpx; overflow: hidden; position: relative; }
.star-layer { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; }
.orb-a { position: fixed; top: -120rpx; right: -80rpx; width: 400rpx; height: 400rpx; background: radial-gradient(circle,rgba(157,114,255,0.10),transparent 65%); border-radius: 50%; pointer-events: none; z-index: 0; }

/* 导航 */
.nav-bar { position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; padding: 80rpx 0 16rpx; }
.nav-left { position: absolute; left: 32rpx; top: 80rpx; width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; }
.back-icon { font-size: 40rpx; color: rgba(255,255,255,0.7); }
.nav-title { font-size: 38rpx; font-weight: 700; color: #fff; letter-spacing: 4rpx; }
.nav-en { font-size: 20rpx; color: rgba(255,255,255,0.35); letter-spacing: 6rpx; margin-top: 4rpx; }

/* 进度条 */
.progress-wrap { position: relative; z-index: 2; margin: 32rpx 48rpx 0; display: flex; align-items: center; }
.progress-bg { flex: 1; height: 8rpx; background: rgba(255,255,255,0.08); border-radius: 4rpx; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg,#5b8def,#9d72ff); border-radius: 4rpx; transition: width 0.3s; }
.progress-text { font-size: 24rpx; color: rgba(255,255,255,0.45); margin-left: 20rpx; min-width: 80rpx; }

/* 答题 */
.test-phase { position: relative; z-index: 2; padding: 40rpx 48rpx; }
.q-card { background: rgba(255,255,255,0.04); border: 1rpx solid rgba(255,255,255,0.08); border-radius: 24rpx; padding: 48rpx 36rpx 36rpx; margin-bottom: 36rpx; }
.q-num { display: flex; align-items: center; margin-bottom: 24rpx; }
.q-num-label { font-size: 28rpx; font-weight: 700; color: #fff; margin-right: 16rpx; }
.q-dim-tag { font-size: 20rpx; color: #fff; padding: 4rpx 16rpx; border-radius: 20rpx; opacity: 0.9; }
.q-text { font-size: 32rpx; color: rgba(255,255,255,0.88); line-height: 1.7; }

/* 选项 */
.opts { margin-bottom: 48rpx; }
.opt-row { display: flex; align-items: center; padding: 24rpx 28rpx; margin-bottom: 16rpx; background: rgba(255,255,255,0.04); border: 1rpx solid rgba(255,255,255,0.08); border-radius: 16rpx; transition: all 0.2s; }
.opt-row.active { border-color: transparent; }
.opt-radio { width: 36rpx; height: 36rpx; border-radius: 50%; border: 2rpx solid rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; margin-right: 20rpx; flex-shrink: 0; transition: border-color 0.2s; }
.opt-radio.checked { border-color: #5b8def; }
.opt-dot { width: 18rpx; height: 18rpx; border-radius: 50%; background: #5b8def; }
.opt-text { font-size: 28rpx; color: rgba(255,255,255,0.65); }

/* 按钮 */
.btns { display: flex; gap: 24rpx; }
.btn-prev, .btn-next { flex: 1; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; }
.btn-prev { background: rgba(255,255,255,0.06); border: 1rpx solid rgba(255,255,255,0.12); }
.btn-prev text { font-size: 28rpx; color: rgba(255,255,255,0.6); }
.btn-next { background: #5b8def; }
.btn-next text { font-size: 28rpx; color: #fff; font-weight: 600; }

/* 结果 */
.result-scroll { position: relative; z-index: 2; height: calc(100vh - 180rpx); }
.result-phase { padding: 32rpx 48rpx 80rpx; }

/* 主卡 */
.hero-card { position: relative; background: rgba(255,255,255,0.04); border: 1rpx solid rgba(255,255,255,0.08); border-radius: 28rpx; padding: 56rpx 36rpx 44rpx; text-align: center; margin-bottom: 32rpx; overflow: hidden; }
.hero-glow { position: absolute; top: -40rpx; left: 50%; transform: translateX(-50%); width: 500rpx; height: 400rpx; pointer-events: none; }
.hero-icon { font-size: 80rpx; display: block; margin-bottom: 16rpx; }
.hero-level { font-size: 40rpx; font-weight: 700; display: block; margin-bottom: 8rpx; }
.hero-code { font-size: 28rpx; display: block; margin-bottom: 16rpx; opacity: 0.8; }
.hero-desc { font-size: 26rpx; color: rgba(255,255,255,0.6); line-height: 1.7; }

/* 区块卡片 */
.section-card { background: rgba(255,255,255,0.04); border: 1rpx solid rgba(255,255,255,0.08); border-radius: 24rpx; padding: 36rpx; margin-bottom: 24rpx; }
.sec-title { font-size: 30rpx; font-weight: 700; color: #fff; margin-bottom: 28rpx; display: block; }

/* 五维分布 */
.dim-list {}
.dim-row { display: flex; align-items: center; margin-bottom: 22rpx; }
.dim-row:last-child { margin-bottom: 0; }
.dim-left { display: flex; align-items: center; width: 180rpx; flex-shrink: 0; }
.dim-icon { font-size: 28rpx; margin-right: 8rpx; }
.dim-name { font-size: 24rpx; color: rgba(255,255,255,0.75); }
.dim-bar-wrap { flex: 1; margin: 0 16rpx; }
.dim-bar-bg { height: 14rpx; background: rgba(255,255,255,0.06); border-radius: 7rpx; overflow: hidden; }
.dim-bar-fill { height: 100%; border-radius: 7rpx; transition: width 0.5s; }
.dim-pct { font-size: 24rpx; font-weight: 600; width: 70rpx; text-align: right; flex-shrink: 0; }
.dim-tag { font-size: 20rpx; width: 80rpx; text-align: center; flex-shrink: 0; margin-left: 8rpx; }

/* 维度详情 */
.detail-header { display: flex; align-items: center; margin-bottom: 16rpx; }
.detail-icon { font-size: 36rpx; margin-right: 12rpx; }
.detail-info { display: flex; align-items: center; gap: 12rpx; }
.detail-name { font-size: 28rpx; font-weight: 600; color: #fff; }
.detail-tag { font-size: 22rpx; font-weight: 600; }
.detail-desc { font-size: 24rpx; color: rgba(255,255,255,0.55); line-height: 1.7; margin-bottom: 20rpx; }
.advice-list {}
.advice-item { display: flex; align-items: flex-start; margin-bottom: 14rpx; }
.advice-item:last-child { margin-bottom: 0; }
.advice-bullet { font-size: 22rpx; margin-right: 10rpx; flex-shrink: 0; margin-top: 2rpx; }
.advice-text { font-size: 24rpx; color: rgba(255,255,255,0.7); line-height: 1.6; }

/* 温馨提示 */
.warm-card { border-color: rgba(157,114,255,0.15); }
.warm-text { font-size: 24rpx; color: rgba(255,255,255,0.6); line-height: 1.8; }

/* 操作按钮 */
.action-row { display: flex; gap: 24rpx; margin-top: 16rpx; }
.btn-retry, .btn-back { flex: 1; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; }
.btn-retry { background: rgba(157,114,255,0.15); border: 1rpx solid rgba(157,114,255,0.3); }
.btn-retry text { font-size: 28rpx; color: #9d72ff; font-weight: 600; }
.btn-back { background: rgba(255,255,255,0.06); border: 1rpx solid rgba(255,255,255,0.12); }
.btn-back text { font-size: 28rpx; color: rgba(255,255,255,0.6); }
</style>
