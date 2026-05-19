<template>
<view class="page" :style="pageStyle">
	<!-- 星空背景 -->
	<view class="star-layer">
		<view v-for="(s,i) in stars" :key="i" class="star" :style="s"></view>
	</view>
	<view class="orb orb-a"></view>
	<view class="orb orb-b"></view>

	<!-- 顶部导航 -->
	<view class="nav-bar">
		<view class="nav-left" @tap="goBack">
			<text class="back-icon">←</text>
		</view>
		<text class="nav-title">抑郁风险评估</text>
		<text class="nav-en">DEPRESSION RISK</text>
	</view>

	<!-- 进度条 -->
	<view class="progress-wrap" v-if="phase === 'test'">
		<view class="progress-bg">
			<view class="progress-fill" :style="progressBarStyle"></view>
		</view>
		<text class="progress-text">{{ curQ + 1 }} / {{ questions.length }}</text>
	</view>

	<!-- 答题阶段 -->
	<view v-if="phase === 'test'" class="test-phase">
		<view class="q-card">
			<view class="q-num">
				<text class="q-num-label">Q{{ curQ + 1 }}</text>
				<text class="q-dim-tag" :style="dimTagStyle">{{ curDimLabel }}</text>
			</view>
			<text class="q-text">{{ questions[curQ].text }}</text>
		</view>
		<view class="opts">
			<view class="opt-row" v-for="(opt, oi) in freqOpts" :key="oi"
				:class="{ active: answers[curQ] === oi }"
				:style="curOptStyles[oi]"
				@tap="selectOpt(oi)">
				<view class="opt-radio" :class="{ checked: answers[curQ] === oi }"
					:style="curOptRadioStyles[oi]">
					<view class="opt-dot" v-if="answers[curQ] === oi" :style="optDotStyle"></view>
				</view>
				<text class="opt-text" :style="curOptTextStyles[oi]">{{ opt }}</text>
			</view>
		</view>
		<view class="btns">
			<view class="btn-prev" v-if="curQ > 0" @tap="prevQ"><text>上一题</text></view>
			<view class="btn-next" :style="btnNextStyle" @tap="nextQ">
				<text>{{ curQ < questions.length - 1 ? '下一题' : '查看结果' }}</text>
			</view>
		</view>
	</view>

	<!-- 结果阶段 -->
	<scroll-view v-if="phase === 'result'" scroll-y class="result-scroll">
		<view class="result-phase">

			<!-- 主等级卡片 -->
		<view class="hero-card" :style="heroCardStyle">
			<view class="hero-glow" :style="heroGlowStyle"></view>
				<text class="hero-icon">{{ resultData.icon }}</text>
			<text class="hero-level" :style="heroLevelStyle">{{ resultData.level }}</text>
			<text class="hero-code" :style="heroCodeStyle">{{ totalScore }}分 / {{ maxScore }}分</text>
				<text class="hero-desc">{{ resultData.desc }}</text>
			</view>

			<!-- 四维指标 -->
			<view class="section-card">
				<text class="sec-title">四维风险指标</text>
				<view class="dim-list">
					<view class="dim-row" v-for="(d, di) in dimResults" :key="di">
						<view class="dim-left">
							<text class="dim-icon">{{ d.icon }}</text>
							<text class="dim-name">{{ d.name }}</text>
						</view>
						<view class="dim-bar-wrap">
							<view class="dim-bar-bg">
								<view class="dim-bar-fill" :style="d.dimBarSty"></view>
							</view>
						</view>
					<text class="dim-pct" :style="d.dimPctSty">{{ d.pct }}%</text>
					<text class="dim-tag" :style="d.dimTagTextSty">{{ d.tag }}</text>
					</view>
				</view>
			</view>

			<!-- 症状清单 -->
			<view class="section-card">
				<text class="sec-title">症状频率分布</text>
				<view class="symp-list">
					<view class="symp-row" v-for="(q, qi) in questions" :key="qi">
						<text class="symp-idx">{{ qi + 1 }}</text>
						<text class="symp-text">{{ q.shortText }}</text>
						<view class="symp-dots">
							<view class="symp-dot" v-for="(o, oi) in 4" :key="oi"
								:class="dotFilledCls[qi][oi]"
								:style="symptomDotStyles[qi][oi]"></view>
						</view>
						<text class="symp-freq">{{ freqShort[answers[qi] || 0] }}</text>
					</view>
				</view>
			</view>

			<!-- 维度详情与建议 -->
			<view class="section-card" v-for="(d, di) in dimResults" :key="di">
				<view class="detail-header">
					<text class="detail-icon">{{ d.icon }}</text>
					<view class="detail-info">
						<text class="detail-name">{{ d.name }}</text>
						<text class="detail-tag" :style="d.detailTagSty">{{ d.tag }}</text>
					</view>
				</view>
				<text class="detail-desc">{{ d.desc }}</text>
				<view class="advice-list">
					<view class="advice-item" v-for="(a, ai) in d.advices" :key="ai">
						<text class="advice-bullet" :style="d.adviceBulletSty">✦</text>
						<text class="advice-text">{{ a }}</text>
					</view>
				</view>
			</view>

			<!-- 安全提示 -->
			<view class="section-card safe-card" v-if="totalScore >= 20">
				<text class="sec-title">关怀提醒</text>
				<text class="safe-text">如果您正在经历持续的情绪痛苦，或出现自伤、轻生的想法，请务必寻求专业帮助。这不是软弱，而是对自己最大的温柔。</text>
				<view class="safe-nums">
					<text class="safe-num">📍 全国24小时心理援助热线：400-161-9995</text>
					<text class="safe-num">📍 北京心理危机研究与干预中心：010-82951332</text>
					<text class="safe-num">📍 生命热线：400-821-1215</text>
				</view>
			</view>

			<!-- 重要声明 -->
			<view class="section-card warn-card">
				<text class="sec-title">重要声明</text>
				<text class="warn-text">本测试基于 PHQ-9 抑郁症筛查量表改编，仅作为自我觉察参考工具，不能替代专业精神科诊断。如测试结果提示中重度及以上风险，建议尽快前往正规医院精神心理科进行专业评估。</text>
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
// 四大维度
var DIMS = [
	{ key: 'core',   name: '核心症状', icon: '🌧️', color: '#7c6dd8',
	  desc: '反映情绪低落、兴趣丧失、精力匮乏等抑郁核心症状的严重程度。这些是判断抑郁程度的关键指标。' },
	{ key: 'cogn',   name: '认知功能', icon: '🧩', color: '#5b8def',
	  desc: '反映注意力、自我评价、决策能力等认知层面的受影响程度。抑郁常伴随认知功能的下降。' },
	{ key: 'soma',   name: '躯体症状', icon: '💫', color: '#d4607a',
	  desc: '反映睡眠、食欲、躯体不适等生理层面的变化。身心一体，身体症状往往是情绪的信号。' },
	{ key: 'social', name: '社会功能', icon: '🕸️', color: '#dda03f',
	  desc: '反映日常生活、工作学习、人际交往等社会功能受影响的程度。这是评估抑郁对生活实际影响的重要维度。' }
]

// 频率选项 (PHQ-9 标准计分 0-3)
var FREQ_OPTS = ['完全不会', '好几天', '一半以上天数', '几乎每天']
var FREQ_SHORT = ['无', '偶有', '频繁', '持续']

// 20道题目
// dim: 维度, text: 完整题目, shortText: 症状简称
var QUESTIONS = [
	// 核心症状 (5题, 0-15分)
	{ dim: 'core', text: '做事时提不起劲或没有兴趣。', shortText: '兴趣减退' },
	{ dim: 'core', text: '感到心情低落、沮丧或绝望。', shortText: '情绪低落' },
	{ dim: 'core', text: '感觉疲惫，没有精力做任何事。', shortText: '精力不足' },
	{ dim: 'core', text: '觉得生活没有意义，找不到活下去的动力。', shortText: '意义缺失' },
	{ dim: 'core', text: '容易哭泣，或感到内心空洞麻木。', shortText: '情绪脆弱' },
	// 认知功能 (5题, 0-15分)
	{ dim: 'cogn', text: '很难集中注意力，例如读报或看电视时。', shortText: '注意力差' },
	{ dim: 'cogn', text: '觉得自己很差劲，或让自己和家人失望了。', shortText: '自我否定' },
	{ dim: 'cogn', text: '对做决定感到困难，哪怕是日常小事。', shortText: '决策困难' },
	{ dim: 'cogn', text: '反复出现消极想法，难以自行摆脱。', shortText: '消极思维' },
	{ dim: 'cogn', text: '对未来感到悲观，觉得事情不可能好转。', shortText: '未来悲观' },
	// 躯体症状 (5题, 0-15分)
	{ dim: 'soma', text: '入睡困难、睡不安稳或睡眠过多。', shortText: '睡眠障碍' },
	{ dim: 'soma', text: '食欲不振，或暴饮暴食。', shortText: '食欲异常' },
	{ dim: 'soma', text: '动作或说话速度明显变慢，或相反变得烦躁不安。', shortText: '精神运动异常' },
	{ dim: 'soma', text: '经常感到身体不适，但查不出明确器质性问题。', shortText: '躯体化症状' },
	{ dim: 'soma', text: '性欲明显减退，对亲密关系失去兴趣。', shortText: '性欲减退' },
	// 社会功能 (5题, 0-15分)
	{ dim: 'social', text: '不想与人交流，主动回避社交活动。', shortText: '社交退缩' },
	{ dim: 'social', text: '工作或学习效率明显下降。', shortText: '效率下降' },
	{ dim: 'social', text: '日常家务或个人卫生难以维持。', shortText: '日常困难' },
	{ dim: 'social', text: '与家人朋友的关系变得紧张或疏远。', shortText: '关系恶化' },
	{ dim: 'social', text: '觉得自己成为了他人的负担。', shortText: '负担感' }
]

// 等级判定 (总分 0-60)
function calcLevel(total) {
	if (total <= 4)  return 0  // 无抑郁
	if (total <= 9)  return 1  // 轻微
	if (total <= 19) return 2  // 轻度
	if (total <= 34) return 3  // 中度
	if (total <= 49) return 4  // 中重度
	return 5  // 重度
}

var LEVEL_DATA = [
	{ level: '无明显抑郁', icon: '☀️', desc: '您目前未显示出抑郁症状，心理状态健康。请继续保持良好的生活节奏和积极的心态。', color: '#3ec9c1' },
	{ level: '亚健康状态', icon: '🌤️', desc: '您有极轻微的情绪波动，属于正常范围。注意保持作息规律和适度运动即可。', color: '#6dc8a0' },
	{ level: '轻度抑郁倾向', icon: '⛅', desc: '您存在轻度抑郁倾向，部分症状已开始影响生活。建议主动调节并关注情绪变化。', color: '#dda03f' },
	{ level: '中度抑郁风险', icon: '🌧️', desc: '您存在中度抑郁风险，多个维度的症状已对生活产生明显影响。建议认真对待，考虑寻求专业心理咨询。', color: '#d4607a' },
	{ level: '中重度抑郁风险', icon: '🌩️', desc: '您存在中重度抑郁风险，症状已较严重地影响日常生活。强烈建议尽快前往专业机构进行评估和干预。', color: '#9d72ff' },
	{ level: '重度抑郁风险', icon: '🌘', desc: '您目前存在重度抑郁风险，亟需专业帮助。请尽快联系心理咨询师或精神科医生，这不是软弱，是自我保护。', color: '#8b5cf6' }
]

// 维度等级 (每维 0-15)
function dimTag(score) {
	if (score <= 1)  return { tag: '正常', tagColor: '#3ec9c1' }
	if (score <= 4)  return { tag: '轻微', tagColor: '#6dc8a0' }
	if (score <= 8)  return { tag: '轻度', tagColor: '#dda03f' }
	if (score <= 11) return { tag: '中度', tagColor: '#d4607a' }
	return { tag: '重度', tagColor: '#9d72ff' }
}

// 维度建议
var ADVICE_MAP = {
	core: [
		'每天安排一件让自己愉悦的小事，即使当下提不起兴趣',
		'尝试在阳光充足的时间段外出散步15-30分钟',
		'接纳"没有精力"的状态，不要因此自责',
		'如果低落情绪持续两周以上，建议寻求专业帮助'
	],
	cogn: [
		'将大任务拆解为小步骤，一次只做一件事',
		'练习"思维暂停"技术：当消极想法出现时，想象按下暂停键',
		'写下自我否定的想法，旁边写出客观的反面证据',
		'决策困难时，先用"足够好"代替"最好"的标准'
	],
	soma: [
		'建立固定的作息时间，即使睡不着也按时躺下/起床',
		'适度运动有助于改善睡眠和食欲，从轻量运动开始',
		'关注身体的信号，但不必过度解读每一个不适',
		'规律饮食，避免用咖啡因或酒精自我调节'
	],
	social: [
		'从一个信任的人开始，试着分享一点自己的感受',
		'降低社交期待，不必强迫自己表现得"正常"',
		'告诉身边人你需要的是陪伴，而不一定是建议',
		'在能够承担的范围内维持最基本的日常社交'
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
			freqShort: FREQ_SHORT,
			maxScore: 60,
			// 结果
			totalScore: 0,
			resultData: {},
			levelColor: '',
			dimResults: [],
			// 背景
			stars: []
		}
	},
	computed: {
		pageStyle: function() {
			return { minHeight: '100vh', background: 'linear-gradient(170deg,#0d0b1e 0%,#151231 40%,#1e1238 100%)' }
		},
		progressPct: function() {
			return Math.round(((this.curQ + 1) / this.questions.length) * 100)
		},
		progressBarStyle: function() {
			return { width: this.progressPct + '%' }
		},
		curDimLabel: function() {
			var q = this.questions[this.curQ]
			for (var i = 0; i < DIMS.length; i++) {
				if (DIMS[i].key === q.dim) return DIMS[i].name
			}
			return ''
		},
		curDimColor: function() {
			var q = this.questions[this.curQ]
			for (var i = 0; i < DIMS.length; i++) {
				if (DIMS[i].key === q.dim) return DIMS[i].color
			}
			return '#7c6dd8'
		},
		dimTagStyle: function() {
			return { background: this.curDimColor }
		},
		curOptStyles: function() {
			var arr = []
			for (var oi = 0; oi < this.freqOpts.length; oi++) {
				if (this.answers[this.curQ] === oi) {
					arr.push({ background: this.curDimColor, borderColor: this.curDimColor })
				} else {
					arr.push({})
				}
			}
			return arr
		},
		curOptRadioStyles: function() {
			var arr = []
			for (var oi = 0; oi < this.freqOpts.length; oi++) {
				if (this.answers[this.curQ] === oi) {
					arr.push({ borderColor: this.curDimColor })
				} else {
					arr.push({})
				}
			}
			return arr
		},
		optDotStyle: function() {
			return { background: this.curDimColor }
		},
		curOptTextStyles: function() {
			var arr = []
			for (var oi = 0; oi < this.freqOpts.length; oi++) {
				if (this.answers[this.curQ] === oi) {
					arr.push({ color: '#fff' })
				} else {
					arr.push({})
				}
			}
			return arr
		},
		btnNextStyle: function() {
			return { background: this.curDimColor }
		},
		heroGlowStyle: function() {
			return { background: 'radial-gradient(circle,' + this.levelColor + '22,transparent 65%)' }
		},
		heroCardStyle: function() {
			return { borderColor: this.levelColor }
		},
		heroLevelStyle: function() {
			return { color: this.levelColor }
		},
		heroCodeStyle: function() {
			return { color: this.levelColor }
		},
		symptomDotStyles: function() {
			var colors = ['rgba(255,255,255,0.15)', '#3ec9c1', '#dda03f', '#d4607a']
			var result = []
			for (var qi = 0; qi < this.questions.length; qi++) {
				var row = []
				var ans = this.answers[qi] || 0
				for (var oi = 0; oi < 4; oi++) {
					if (ans >= oi) {
						row.push({ background: colors[ans] || colors[0] })
					} else {
						row.push({})
					}
				}
				result.push(row)
			}
			return result
		},
		dotFilledCls: function() {
			var result = []
			for (var qi = 0; qi < this.questions.length; qi++) {
				var row = []
				var ans = this.answers[qi] || 0
				for (var oi = 0; oi < 4; oi++) {
					row.push({ filled: ans >= oi })
				}
				result.push(row)
			}
			return result
		}
	},
	onLoad: function() {
		this.stars = this.makeStars()
		var saved = uni.getStorageSync('depression_result')
		if (saved) {
			try {
				var d = JSON.parse(saved)
				this.totalScore = d.totalScore
				this.resultData = d.resultData
				this.levelColor = d.levelColor
				this.dimResults = d.dimResults
				this._recomputeDimStyles()
				this.answers = d.answers || []
				this.phase = 'result'
			} catch(e) {}
		}
	},
	methods: {
		_recomputeDimStyles: function() {
			for (var i = 0; i < this.dimResults.length; i++) {
				var d = this.dimResults[i]
				this.$set(d, 'dimBarSty', { width: d.pct + '%', background: d.color })
				this.$set(d, 'dimPctSty', { color: d.color })
				this.$set(d, 'dimTagTextSty', { color: d.tagColor })
				this.$set(d, 'detailTagSty', { color: d.tagColor })
				this.$set(d, 'adviceBulletSty', { color: d.color })
			}
		},
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
			var dimScores = {}
			for (var di = 0; di < DIMS.length; di++) {
				dimScores[DIMS[di].key] = 0
			}
			for (var qi = 0; qi < this.questions.length; qi++) {
				var q = this.questions[qi]
				var ansIdx = this.answers[qi] || 0
				dimScores[q.dim] += ansIdx
			}

			// 总分
			var total = 0
			for (var k in dimScores) total += dimScores[k]
			self.totalScore = total

			// 等级
			var lvlIdx = calcLevel(total)
			self.resultData = LEVEL_DATA[lvlIdx]
			self.levelColor = LEVEL_DATA[lvlIdx].color

			// 维度结果
			var dimResults = []
			for (var d = 0; d < DIMS.length; d++) {
				var dim = DIMS[d]
				var sc = dimScores[dim.key]
				var dt = dimTag(sc)
				var pct = Math.round(sc / 15 * 100)
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
					advices: ADVICE_MAP[dim.key],
					dimBarSty: { width: pct + '%', background: dim.color },
					dimPctSty: { color: dim.color },
					dimTagTextSty: { color: dt.tagColor },
					detailTagSty: { color: dt.tagColor },
					adviceBulletSty: { color: dim.color }
				})
			}
			self.dimResults = dimResults

			// 保存
			self.phase = 'result'
			setTimeout(function() {
				uni.setStorageSync('depression_result', JSON.stringify({
					totalScore: self.totalScore,
					resultData: self.resultData,
					levelColor: self.levelColor,
					dimResults: self.dimResults,
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
			this.resultData = {}
			this.levelColor = ''
			this.dimResults = []
			uni.removeStorageSync('depression_result')
		},
		goBack: function() {
			uni.navigateBack({ delta: 1 })
		},
		_saveToDb: function() {
			var uid = 0
			try { uid = Number(uni.getStorageSync('xinyu_user_id')) || 0 } catch(e) {}
			if (!uid) return
			var self = this
			var summary = self.resultData.level + '(' + self.totalScore + '分)'
			var scores = {}
			for (var i = 0; i < self.dimResults.length; i++) scores[self.dimResults[i].key] = self.dimResults[i].score
			uni.request({
				url: (typeof SHADOW_API_BASE !== 'undefined' ? SHADOW_API_BASE : 'http://43.143.169.226') + '/api/assessments/submit',
				method: 'POST',
				header: { 'Content-Type': 'application/json' },
				data: {
					user_id: uid,
					test_type: 'depression',
					summary: summary,
					result_json: { totalScore: self.totalScore, resultData: self.resultData, levelColor: self.levelColor, dimResults: self.dimResults },
					score_json: scores,
					answers_json: self.answers,
					question_count: 20
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
.orb-b { position: fixed; bottom: -100rpx; left: -60rpx; width: 350rpx; height: 350rpx; background: radial-gradient(circle,rgba(212,96,122,0.08),transparent 65%); border-radius: 50%; pointer-events: none; z-index: 0; }

/* 导航 */
.nav-bar { position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; padding: 80rpx 0 16rpx; }
.nav-left { position: absolute; left: 32rpx; top: 80rpx; width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; }
.back-icon { font-size: 40rpx; color: rgba(255,255,255,0.7); }
.nav-title { font-size: 38rpx; font-weight: 700; color: #fff; letter-spacing: 4rpx; }
.nav-en { font-size: 20rpx; color: rgba(255,255,255,0.35); letter-spacing: 6rpx; margin-top: 4rpx; }

/* 进度条 */
.progress-wrap { position: relative; z-index: 2; margin: 32rpx 48rpx 0; display: flex; align-items: center; }
.progress-bg { flex: 1; height: 8rpx; background: rgba(255,255,255,0.08); border-radius: 4rpx; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg,#7c6dd8,#d4607a); border-radius: 4rpx; transition: width 0.3s; }
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
.opt-radio.checked { border-color: #7c6dd8; }
.opt-dot { width: 18rpx; height: 18rpx; border-radius: 50%; background: #7c6dd8; }
.opt-text { font-size: 28rpx; color: rgba(255,255,255,0.65); }

/* 按钮 */
.btns { display: flex; gap: 24rpx; }
.btn-prev, .btn-next { flex: 1; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; }
.btn-prev { background: rgba(255,255,255,0.06); border: 1rpx solid rgba(255,255,255,0.12); }
.btn-prev text { font-size: 28rpx; color: rgba(255,255,255,0.6); }
.btn-next { background: #7c6dd8; }
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

/* 四维分布 */
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

/* 症状清单 */
.symp-list {}
.symp-row { display: flex; align-items: center; padding: 14rpx 0; border-bottom: 1rpx solid rgba(255,255,255,0.04); }
.symp-row:last-child { border-bottom: none; }
.symp-idx { font-size: 22rpx; color: rgba(255,255,255,0.25); width: 40rpx; flex-shrink: 0; }
.symp-text { font-size: 24rpx; color: rgba(255,255,255,0.7); flex: 1; }
.symp-dots { display: flex; gap: 6rpx; margin: 0 12rpx; flex-shrink: 0; }
.symp-dot { width: 14rpx; height: 14rpx; border-radius: 50%; background: rgba(255,255,255,0.08); transition: background 0.2s; }
.symp-dot.filled { background: #7c6dd8; }
.symp-freq { font-size: 20rpx; color: rgba(255,255,255,0.4); width: 56rpx; text-align: center; flex-shrink: 0; }

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

/* 安全提示 */
.safe-card { border-color: rgba(212,96,122,0.2); background: rgba(212,96,122,0.04); }
.safe-text { font-size: 26rpx; color: rgba(255,255,255,0.7); line-height: 1.8; margin-bottom: 20rpx; }
.safe-nums {}
.safe-num { display: block; font-size: 24rpx; color: rgba(255,255,255,0.6); line-height: 2; }

/* 声明 */
.warn-card { border-color: rgba(255,255,255,0.06); }
.warn-text { font-size: 24rpx; color: rgba(255,255,255,0.45); line-height: 1.8; }

/* 操作按钮 */
.action-row { display: flex; gap: 24rpx; margin-top: 16rpx; }
.btn-retry, .btn-back { flex: 1; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; }
.btn-retry { background: rgba(124,109,216,0.15); border: 1rpx solid rgba(124,109,216,0.3); }
.btn-retry text { font-size: 28rpx; color: #7c6dd8; font-weight: 600; }
.btn-back { background: rgba(255,255,255,0.06); border: 1rpx solid rgba(255,255,255,0.12); }
.btn-back text { font-size: 28rpx; color: rgba(255,255,255,0.6); }
</style>
