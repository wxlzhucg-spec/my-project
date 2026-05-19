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
		<text class="nav-title">亲密关系测试</text>
		<text class="nav-en">INTIMACY STYLE</text>
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
				<text class="q-dim-tag" :style="{ background: curDimColor }">{{ curDimLabel }}</text>
			</view>
			<text class="q-text">{{ questions[curQ].text }}</text>
		</view>
		<view class="opts">
			<view class="opt-row" v-for="(opt, oi) in agreeOpts" :key="oi"
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
			<view class="btn-next" :style="{ background: curDimColor }" @tap="nextQ">
				<text>{{ curQ < questions.length - 1 ? '下一题' : '查看结果' }}</text>
			</view>
		</view>
	</view>

	<!-- 结果阶段 -->
	<scroll-view v-if="phase === 'result'" scroll-y class="result-scroll">
		<view class="result-phase">

			<!-- 依恋类型主卡 -->
			<view class="hero-card" :style="{ borderColor: resultData.color }">
				<view class="hero-glow" :style="heroGlowStyle"></view>
				<text class="hero-icon">{{ resultData.icon }}</text>
				<text class="hero-level" :style="{ color: resultData.color }">{{ resultData.name }}</text>
				<text class="hero-code" :style="{ color: resultData.color }">{{ resultData.enName }}</text>
				<text class="hero-desc">{{ resultData.desc }}</text>
			</view>

			<!-- 三维坐标 -->
			<view class="section-card">
				<text class="sec-title">依恋三维坐标</text>
				<view class="axis-list">
					<view class="axis-row" v-for="(a, ai) in axisResults" :key="ai">
						<view class="axis-left">
							<text class="axis-icon">{{ a.icon }}</text>
							<text class="axis-name">{{ a.name }}</text>
						</view>
						<view class="axis-bar-wrap">
							<view class="axis-bar-bg">
								<view class="axis-bar-fill" :style="a.barStyle"></view>
							</view>
						</view>
						<text class="axis-pct" :style="{ color: a.color }">{{ a.pct }}%</text>
						<text class="axis-tag" :style="{ color: a.tagColor }">{{ a.tag }}</text>
					</view>
				</view>
				<text class="axis-note">{{ axisNote }}</text>
			</view>

			<!-- 依恋类型详解 -->
			<view class="section-card">
				<text class="sec-title">你的依恋画像</text>
				<view class="trait-list">
					<view class="trait-item" v-for="(t, ti) in resultData.traits" :key="ti">
						<text class="trait-bullet" :style="{ color: resultData.color }">✦</text>
						<text class="trait-text">{{ t }}</text>
					</view>
				</view>
			</view>

			<!-- 亲密关系中的表现 -->
			<view class="section-card">
				<text class="sec-title">亲密关系中的你</text>
				<view class="scene-list">
					<view class="scene-item" v-for="(s, si) in resultData.scenes" :key="si">
						<view class="scene-header">
							<text class="scene-icon">{{ s.icon }}</text>
							<text class="scene-name">{{ s.title }}</text>
						</view>
						<text class="scene-desc">{{ s.desc }}</text>
					</view>
				</view>
			</view>

			<!-- 与各类型相处指南 -->
			<view class="section-card">
				<text class="sec-title">与不同类型相处</text>
				<view class="pair-list">
					<view class="pair-item" v-for="(p, pi) in resultData.pairGuide" :key="pi">
						<view class="pair-header">
							<text class="pair-icon">{{ p.icon }}</text>
							<text class="pair-name">{{ p.name }}</text>
							<text class="pair-harmony" :style="{ color: p.harmonyColor }">{{ p.harmony }}</text>
						</view>
						<text class="pair-tip">{{ p.tip }}</text>
					</view>
				</view>
			</view>

			<!-- 成长建议 -->
			<view class="section-card">
				<text class="sec-title">成长之路</text>
				<view class="advice-list">
					<view class="advice-item" v-for="(a, ai) in resultData.advices" :key="ai">
						<text class="advice-bullet" :style="{ color: resultData.color }">✦</text>
						<text class="advice-text">{{ a }}</text>
					</view>
				</view>
			</view>

			<!-- 温馨提示 -->
			<view class="section-card warm-card">
				<text class="sec-title">温馨提示</text>
				<text class="warm-text">依恋风格并非固定不变，它会随着人生经历和自我觉察而变化。理解自己的依恋风格，是建立健康亲密关系的第一步。每一段关系都是成长的机会。</text>
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
// 三大维度
var AXES = [
	{ key: 'avoid',   name: '回避倾向', icon: '🧊', color: '#5b8def', lowTag: '亲近自在', highTag: '倾向回避',
	  desc: '反映您在亲密关系中保持独立与距离的倾向。高回避者倾向自我依赖，低回避者更愿亲近依赖。' },
	{ key: 'anxiety', name: '焦虑倾向', icon: '🌊', color: '#d4607a', lowTag: '内心安定', highTag: '倾向焦虑',
	  desc: '反映您对被抛弃和不被爱的担忧程度。高焦虑者需要反复确认爱意，低焦虑者对关系更有安全感。' },
	{ key: 'secure', name: '安全感',   icon: '⚓', color: '#3ec9c1', lowTag: '需建设', highTag: '根基稳',
	  desc: '反映您在亲密关系中的整体安全感受。高安全感者既能亲密又能独立，是健康关系的基石。' }
]

var AGREE_OPTS = ['很不符合', '较不符合', '比较符合', '非常符合']

// 24道题目
var QUESTIONS = [
	// 回避倾向 (8题，reverse=true表示选"很不符合"代表回避高)
	{ dim: 'avoid', reverse: true, text: '我很容易与他人建立亲密的情感联结。' },
	{ dim: 'avoid', reverse: false, text: '当关系变得过于亲近时，我会本能地想要后退。' },
	{ dim: 'avoid', reverse: true, text: '我愿意向伴侣展示自己脆弱的一面。' },
	{ dim: 'avoid', reverse: false, text: '我更喜欢保持一定距离，不完全依赖对方。' },
	{ dim: 'avoid', reverse: true, text: '我享受与伴侣之间的深度交流和情感分享。' },
	{ dim: 'avoid', reverse: false, text: '伴侣过于依赖我时，我会感到窒息。' },
	{ dim: 'avoid', reverse: true, text: '我渴望与伴侣在精神层面深度联结。' },
	{ dim: 'avoid', reverse: false, text: '我很难完全信任一个人，总觉得靠不住。' },
	// 焦虑倾向 (8题)
	{ dim: 'anxiety', reverse: false, text: '我经常担心伴侣不够爱我，或会离开我。' },
	{ dim: 'anxiety', reverse: false, text: '对方没有及时回复消息时，我会胡思乱想。' },
	{ dim: 'anxiety', reverse: true, text: '即使伴侣不在身边，我也相信自己被爱着。' },
	{ dim: 'anxiety', reverse: false, text: '我需要伴侣反复确认对我的感情才安心。' },
	{ dim: 'anxiety', reverse: false, text: '伴侣与异性正常交往时，我会感到不安或嫉妒。' },
	{ dim: 'anxiety', reverse: true, text: '我能接受关系中适度的独立空间。' },
	{ dim: 'anxiety', reverse: false, text: '争吵之后，我很难主动和好，害怕关系已经破裂。' },
	{ dim: 'anxiety', reverse: false, text: '我总觉得自己在关系中做得不够好。' },
	// 安全感 (8题，reverse=true表示选"很不符合"代表安全感低)
	{ dim: 'secure', reverse: true, text: '我相信自己是值得被爱的。' },
	{ dim: 'secure', reverse: true, text: '遇到矛盾时，我能冷静沟通而不是逃避或指责。' },
	{ dim: 'secure', reverse: true, text: '我能平衡亲密与独立，不会失去自我。' },
	{ dim: 'secure', reverse: true, text: '即使关系遇到困难，我也相信能一起解决。' },
	{ dim: 'secure', reverse: true, text: '我能接纳伴侣的缺点，不会试图改变对方。' },
	{ dim: 'secure', reverse: true, text: '我表达需求时是坦诚的，不被动攻击。' },
	{ dim: 'secure', reverse: true, text: '我不会因为害怕冲突而压抑自己的感受。' },
	{ dim: 'secure', reverse: true, text: '我相信好的关系是可能的，而不是童话。' }
]

// 依恋类型判定
// 回避高 + 焦虑低 = 疏离型
// 回避低 + 焦虑高 = 痴迷型
// 回避高 + 焦虑高 = 恐惧型
// 回避低 + 焦虑低 = 安全型
function calcType(avoidPct, anxietyPct) {
	var avoidHigh = avoidPct > 50
	var anxietyHigh = anxietyPct > 50
	if (!avoidHigh && !anxietyHigh) return 'secure'
	if (avoidHigh && !anxietyHigh) return 'dismissive'
	if (!avoidHigh && anxietyHigh) return 'preoccupied'
	return 'fearful'
}

var TYPE_DATA = {
	secure: {
		name: '安全型依恋', enName: 'SECURE', icon: '⚓', color: '#3ec9c1',
		desc: '您在亲密关系中拥有稳定的安全感。您既能享受亲密，又能保持独立；既信任伴侣，也相信自己的价值。这是最健康的依恋风格，是长久幸福关系的根基。',
		traits: [
			'对亲密关系持积极开放的态度',
			'能自然地表达情感需求，也能回应对方',
			'面对冲突时倾向建设性沟通',
			'不会因伴侣的独立空间而感到威胁',
			'相信自己值得被爱，也相信他人值得信任',
			'关系中既能亲密无间，又不失自我'
		],
		scenes: [
			{ icon: '💬', title: '冲突处理', desc: '面对分歧时，您倾向于直接沟通、寻找共识，而非回避或指责。您相信矛盾是可以解决的。' },
			{ icon: '🫂', title: '情感表达', desc: '您能自然地表达爱意和脆弱，不会觉得示弱是危险的。也善于接纳伴侣的情感表达。' },
			{ icon: '🏠', title: '独立空间', desc: '您尊重彼此的个人空间，不会因为伴侣需要独处而感到被拒绝，也不会因分开而焦虑。' }
		],
		pairGuide: [
			{ icon: '🧊', name: '疏离型', harmony: '需磨合', harmonyColor: '#dda03f', tip: '给对方空间，但温和地表达你也需要情感联结。不要用追求亲密去"逼"对方。' },
			{ icon: '🌊', name: '痴迷型', harmony: '互补型', harmonyColor: '#3ec9c1', tip: '你的稳定感能安抚对方的不安，但也要设定健康边界，避免被对方的焦虑消耗。' },
			{ icon: '🌪️', name: '恐惧型', harmony: '需耐心', harmonyColor: '#d4607a', tip: '你的安全感是最好的疗愈。保持一致性，让对方慢慢相信"这次不一样"。' }
		],
		advices: [
			'继续维护关系的健康节奏，不要把安全感视为理所当然',
			'偶尔觉察是否有"过度适应"的倾向——安全型有时会忽略自己的需求',
			'帮助伴侣建立安全感的同时，保持自己的能量平衡',
			'在关系中持续成长，让亲密成为彼此的养分而非习惯'
		]
	},
	dismissive: {
		name: '疏离型依恋', enName: 'DISMISSIVE', icon: '🧊', color: '#5b8def',
		desc: '您在亲密关系中倾向于保持独立和距离。您重视自我依靠，对过度亲密会感到不适。这并非不需要爱，而是保护自己的一种方式。理解这个模式，是走向更深层联结的第一步。',
		traits: [
			'重视独立自主，倾向于自我依赖',
			'亲密程度增加时会本能地后退',
			'不太善于表达脆弱和情感需求',
			'对伴侣的情感需求有时感到不解或不耐烦',
			'倾向于用理性化来回避情感体验',
			'内心深处可能有未被承认的孤独感'
		],
		scenes: [
			{ icon: '💬', title: '冲突处理', desc: '面对冲突时，您倾向于退缩、冷处理或理性分析，而非直面情感。沉默和距离是您惯用的"安全策略"。' },
			{ icon: '🫂', title: '情感表达', desc: '表达爱意对您来说不太自然，您更习惯用行动而非语言来示爱。当伴侣需要情感回应时，您可能感到手足无措。' },
			{ icon: '🏠', title: '独立空间', desc: '您非常重视个人空间，有时会因伴侣的"粘人"而感到压力。但您的独立也可能被误解为不在乎。' }
		],
		pairGuide: [
			{ icon: '⚓', name: '安全型', harmony: '可成长', harmonyColor: '#3ec9c1', tip: '对方的稳定感能帮助您慢慢敞开，试着在安全的节奏中增加一点点亲密。' },
			{ icon: '🌊', name: '痴迷型', harmony: '追逃循环', harmonyColor: '#d4607a', tip: '你们的组合容易陷入"追-逃"模式：对方越追，您越逃。试着停下来，承认自己的需求。' },
			{ icon: '🌪️', name: '恐惧型', harmony: '双重距离', harmonyColor: '#9d72ff', tip: '两人都倾向回避，关系可能维持在表面的"和平"。需要有人先迈出一步。' }
		],
		advices: [
			'试着向信任的人分享一点内心感受，不需要一下子敞开所有',
			'当想要后退时，停下来问问自己：我是在保护什么？',
			'练习对伴侣说"我需要一些时间思考，但我没有不理你"',
			'承认自己也需要爱——独立和亲密并不矛盾'
		]
	},
	preoccupied: {
		name: '痴迷型依恋', enName: 'PREOCCUPIED', icon: '🌊', color: '#d4607a',
		desc: '您在亲密关系中渴望深度联结，但对被抛弃有强烈的担忧。您会投入大量情感能量在关系上，伴侣的回应直接牵动您的情绪。这份对爱的渴望本身是美好的，学会在爱中安放自己，是您的成长课题。',
		traits: [
			'对亲密关系有强烈的需求和渴望',
			'经常担心伴侣不够爱自己或会离开',
			'对伴侣的言行高度敏感，容易过度解读',
			'需要频繁的确认和保证才能安心',
			'容易在关系中失去自我边界',
			'对分离和被拒绝有强烈的恐惧'
		],
		scenes: [
			{ icon: '💬', title: '冲突处理', desc: '冲突时您倾向于追求立即解决，无法忍受"悬而未决"的状态。沉默或不回应会激发您最深的焦虑。' },
			{ icon: '🫂', title: '情感表达', desc: '您善于表达情感，但有时强度会让伴侣感到压力。您的爱很热烈，但需要学习"刚刚好"的力度。' },
			{ icon: '🏠', title: '独立空间', desc: '伴侣需要独处时，您容易感到被拒绝。学会不把"空间"等同于"不爱"，是您的重要功课。' }
		],
		pairGuide: [
			{ icon: '⚓', name: '安全型', harmony: '互补型', harmonyColor: '#3ec9c1', tip: '对方的稳定感能安抚您的不安。接受对方的节奏，不要用自己的焦虑去"测试"爱。' },
			{ icon: '🧊', name: '疏离型', harmony: '追逃循环', harmonyColor: '#d4607a', tip: '最容易陷入"追-逃"模式的组合。觉察自己是否在用追逐来缓解焦虑，试着先安抚自己。' },
			{ icon: '🌊', name: '痴迷型', harmony: '情绪共振', harmonyColor: '#dda03f', tip: '两人的焦虑可能互相放大。约定"暂停-回归"的沟通规则，避免情绪漩涡。' }
		],
		advices: [
			'练习在焦虑升起时先安抚自己，而不是立即向外寻求确认',
			'建立"自我安抚清单"：散步、写日记、深呼吸——在找伴侣之前先照顾自己',
			'试着区分"我害怕"和"真的有危险"——焦虑不等于事实',
			'培养独立于关系的自我价值感——你值得被爱，不需要不断证明'
		]
	},
	fearful: {
		name: '恐惧型依恋', enName: 'FEARFUL', icon: '🌪️', color: '#9d72ff',
		desc: '您在亲密关系中同时渴望亲密又害怕亲密。您想要被爱，但当关系深入时会感到不安全和想逃离。这种"又想要又害怕"的矛盾是最痛苦的模式，但请相信——觉察到这一点，改变就已经开始了。',
		traits: [
			'渴望亲密但又害怕被伤害',
			'对伴侣的情感信号高度敏感但倾向负面解读',
			'关系中常经历"推开-拉回"的反复',
			'自我评价偏低，怀疑自己是否值得被爱',
			'对信任他人有极大的困难',
			'内心承受着渴望与恐惧的持续拉扯'
		],
		scenes: [
			{ icon: '💬', title: '冲突处理', desc: '冲突时您可能在攻击和逃避之间反复——既想修复关系，又害怕受伤而提前撤退。情绪波动较大。' },
			{ icon: '🫂', title: '情感表达', desc: '您会表达情感，但很快又因感到危险而收回。这种"推拉"模式让伴侣困惑，也让您自己疲惫。' },
			{ icon: '🏠', title: '独立空间', desc: '独处时渴望陪伴，在一起时又害怕依赖。这种矛盾让关系充满了不确定性和紧张感。' }
		],
		pairGuide: [
			{ icon: '⚓', name: '安全型', harmony: '最佳疗愈', harmonyColor: '#3ec9c1', tip: '对方的稳定和一致是最好的疗愈因子。允许自己慢慢相信，不要提前"预防性"地推开。' },
			{ icon: '🧊', name: '疏离型', harmony: '双重距离', harmonyColor: '#dda03f', tip: '两人的回避可能让关系始终无法深入。需要有人先展现脆弱——这很难，但值得。' },
			{ icon: '🌊', name: '痴迷型', harmony: '焦虑共鸣', harmonyColor: '#d4607a', tip: '你们的焦虑可能互相激发，但理解彼此的恐惧也能带来深层共鸣。需要明确的沟通规则。' }
		],
		advices: [
			'当想要"逃跑"时，停下来问自己：我是在回应真实威胁，还是旧日恐惧？',
			'找一个安全的人练习"一点点信任"——不需要一次性交出全部',
			'当感到矛盾时，试着对伴侣说"我需要你，但我现在也有点害怕"',
			'考虑专业心理咨询——疗愈恐惧型依恋，专业陪伴是最快也最安全的路'
		]
	}
}

module.exports = {
	data: function() {
		return {
			phase: 'test',
			curQ: 0,
			answers: [],
			questions: QUESTIONS,
			agreeOpts: AGREE_OPTS,
			// 结果
			resultData: {},
			axisResults: [],
			axisNote: '',
			// 背景
			stars: []
		}
	},
	computed: {
		pageStyle: function() {
			return { minHeight: '100vh', background: 'linear-gradient(170deg,#0d0b1e 0%,#151231 40%,#20102e 100%)' }
		},
		progressPct: function() {
			return Math.round(((this.curQ + 1) / this.questions.length) * 100)
		},
		progressBarStyle: function() {
			return { width: this.progressPct + '%' }
		},
		curDimLabel: function() {
			var q = this.questions[this.curQ]
			for (var i = 0; i < AXES.length; i++) {
				if (AXES[i].key === q.dim) return AXES[i].name
			}
			return ''
		},
		curDimColor: function() {
			var q = this.questions[this.curQ]
			for (var i = 0; i < AXES.length; i++) {
				if (AXES[i].key === q.dim) return AXES[i].color
			}
			return '#d4607a'
		},
		heroGlowStyle: function() {
			return { background: 'radial-gradient(circle,' + this.resultData.color + '22,transparent 65%)' }
		},
		curOptStyles: function() {
			var styles = []
			for (var i = 0; i < this.agreeOpts.length; i++) {
				if (this.answers[this.curQ] === i) {
					styles.push({ background: this.curDimColor, borderColor: this.curDimColor })
				} else {
					styles.push({})
				}
			}
			return styles
		},
		curOptRadioStyles: function() {
			var styles = []
			for (var i = 0; i < this.agreeOpts.length; i++) {
				if (this.answers[this.curQ] === i) {
					styles.push({ borderColor: this.curDimColor })
				} else {
					styles.push({})
				}
			}
			return styles
		},
		curOptTextStyles: function() {
			var styles = []
			for (var i = 0; i < this.agreeOpts.length; i++) {
				if (this.answers[this.curQ] === i) {
					styles.push({ color: '#fff' })
				} else {
					styles.push({})
				}
			}
			return styles
		},
		optDotStyle: function() {
			return { background: this.curDimColor }
		}
	},
	onLoad: function() {
		this.stars = this.makeStars()
		var saved = uni.getStorageSync('intimacy_result')
		if (saved) {
			try {
				var d = JSON.parse(saved)
				this.resultData = d.resultData
				this.axisResults = d.axisResults
				this.axisNote = d.axisNote
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
			// 每维度8题，每题0-3分
			// 回避: reverse题选"很不符合"=3分(回避高)，非reverse题选"非常符合"=3分(回避高)
			// 焦虑: 非reverse选"非常符合"=3分(焦虑高)，reverse选"很不符合"=3分(焦虑高)
			// 安全: reverse选"很不符合"=3分(安全低→需建设)，reverse选"非常符合"=0分(安全高→根基稳)
			// 但为了直观，我们计算"维度特征分"而非"问题分"
			// 回避特征分: reverse题(3-ans), 非reverse题(ans)
			// 焦虑特征分: 非reverse题(ans), reverse题(3-ans)
			// 安全特征分: reverse题(ans) 直接代表安全感高

			var dimRaw = {}
			for (var di = 0; di < AXES.length; di++) {
				dimRaw[AXES[di].key] = 0
			}
			for (var qi = 0; qi < this.questions.length; qi++) {
				var q = this.questions[qi]
				var ans = this.answers[qi] || 0
				var score = 0
				if (q.dim === 'avoid') {
					// 回避特征分: reverse题反着算，非reverse正着算
					score = q.reverse ? (3 - ans) : ans
				} else if (q.dim === 'anxiety') {
					// 焦虑特征分: 非reverse正着算，reverse反着算
					score = q.reverse ? (3 - ans) : ans
				} else {
					// 安全感: reverse题正着算（选"非常符合"=安全感高）
					score = q.reverse ? ans : (3 - ans)
				}
				dimRaw[q.dim] += score
			}

			// 百分比 (每维度满分 8*3=24)
			var avoidPct = Math.round(dimRaw.avoid / 24 * 100)
			var anxietyPct = Math.round(dimRaw.anxiety / 24 * 100)
			var securePct = Math.round(dimRaw.secure / 24 * 100)

			// 三维结果
			var axisResults = [
				{
					key: 'avoid', name: '回避倾向', icon: '🧊', color: '#5b8def',
					pct: avoidPct,
					tag: avoidPct > 50 ? '倾向回避' : '亲近自在',
					tagColor: avoidPct > 50 ? '#5b8def' : '#3ec9c1',
					barStyle: { width: avoidPct + '%', background: '#5b8def' }
				},
				{
					key: 'anxiety', name: '焦虑倾向', icon: '🌊', color: '#d4607a',
					pct: anxietyPct,
					tag: anxietyPct > 50 ? '倾向焦虑' : '内心安定',
					tagColor: anxietyPct > 50 ? '#d4607a' : '#3ec9c1',
					barStyle: { width: anxietyPct + '%', background: '#d4607a' }
				},
				{
					key: 'secure', name: '安全感', icon: '⚓', color: '#3ec9c1',
					pct: securePct,
					tag: securePct > 50 ? '根基稳' : '需建设',
					tagColor: securePct > 50 ? '#3ec9c1' : '#dda03f',
					barStyle: { width: securePct + '%', background: '#3ec9c1' }
				}
			]
			self.axisResults = axisResults

			// 判定依恋类型
			var typeKey = calcType(avoidPct, anxietyPct)
			self.resultData = TYPE_DATA[typeKey]

			// 坐标说明
			var notes = {
				secure: '您的回避和焦虑倾向都较低，安全感充沛。这是最健康的依恋风格，为您和伴侣提供了稳固的情感基础。',
				dismissive: '您的回避倾向较高而焦虑较低。您习惯自我依赖，对亲密感到不适。理解这个模式，是走向更深层联结的第一步。',
				preoccupied: '您的焦虑倾向较高而回避较低。您渴望亲密但常担忧被抛弃。学会在爱中安放自己，是您的成长课题。',
				fearful: '您的回避和焦虑倾向都较高——既渴望亲密又害怕亲密。这种矛盾是最痛苦的，但觉察到它，改变就已经开始。'
			}
			self.axisNote = notes[typeKey]

			// 保存
			self.phase = 'result'
			setTimeout(function() {
				uni.setStorageSync('intimacy_result', JSON.stringify({
					resultData: self.resultData,
					axisResults: self.axisResults,
					axisNote: self.axisNote,
					answers: self.answers
				}))
				self._saveToDb()
			}, 200)
		},
		retest: function() {
			this.phase = 'test'
			this.curQ = 0
			this.answers = []
			this.resultData = {}
			this.axisResults = []
			this.axisNote = ''
			uni.removeStorageSync('intimacy_result')
		},
		goBack: function() {
			uni.navigateBack({ delta: 1 })
		},
		_saveToDb: function() {
			var uid = 0
			try { uid = Number(uni.getStorageSync('xinyu_user_id')) || 0 } catch(e) {}
			if (!uid) return
			var self = this
			var summary = self.resultData.name || ''
			var scores = {}
			for (var i = 0; i < self.axisResults.length; i++) scores[self.axisResults[i].key] = self.axisResults[i].pct
			uni.request({
				url: (typeof SHADOW_API_BASE !== 'undefined' ? SHADOW_API_BASE : 'http://43.143.169.226') + '/api/assessments/submit',
				method: 'POST',
				header: { 'Content-Type': 'application/json' },
				data: {
					user_id: uid,
					test_type: 'intimacy',
					summary: summary,
					result_json: { resultData: self.resultData, axisResults: self.axisResults, axisNote: self.axisNote },
					score_json: scores,
					answers_json: self.answers,
					question_count: 24
				}
			})
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; padding-bottom: 60rpx; overflow: hidden; position: relative; }
.star-layer { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; }
.orb-a { position: fixed; top: -120rpx; right: -80rpx; width: 400rpx; height: 400rpx; background: radial-gradient(circle,rgba(212,96,122,0.10),transparent 65%); border-radius: 50%; pointer-events: none; z-index: 0; }
.orb-b { position: fixed; bottom: -100rpx; left: -60rpx; width: 350rpx; height: 350rpx; background: radial-gradient(circle,rgba(91,141,239,0.08),transparent 65%); border-radius: 50%; pointer-events: none; z-index: 0; }

/* 导航 */
.nav-bar { position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; padding: 80rpx 0 16rpx; }
.nav-left { position: absolute; left: 32rpx; top: 80rpx; width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; }
.back-icon { font-size: 40rpx; color: rgba(255,255,255,0.7); }
.nav-title { font-size: 38rpx; font-weight: 700; color: #fff; letter-spacing: 4rpx; }
.nav-en { font-size: 20rpx; color: rgba(255,255,255,0.35); letter-spacing: 6rpx; margin-top: 4rpx; }

/* 进度条 */
.progress-wrap { position: relative; z-index: 2; margin: 32rpx 48rpx 0; display: flex; align-items: center; }
.progress-bg { flex: 1; height: 8rpx; background: rgba(255,255,255,0.08); border-radius: 4rpx; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg,#d4607a,#9d72ff); border-radius: 4rpx; transition: width 0.3s; }
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
.opt-radio.checked { border-color: #d4607a; }
.opt-dot { width: 18rpx; height: 18rpx; border-radius: 50%; background: #d4607a; }
.opt-text { font-size: 28rpx; color: rgba(255,255,255,0.65); }

/* 按钮 */
.btns { display: flex; gap: 24rpx; }
.btn-prev, .btn-next { flex: 1; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; }
.btn-prev { background: rgba(255,255,255,0.06); border: 1rpx solid rgba(255,255,255,0.12); }
.btn-prev text { font-size: 28rpx; color: rgba(255,255,255,0.6); }
.btn-next { background: #d4607a; }
.btn-next text { font-size: 28rpx; color: #fff; font-weight: 600; }

/* 结果 */
.result-scroll { position: relative; z-index: 2; height: calc(100vh - 180rpx); }
.result-phase { padding: 32rpx 48rpx 80rpx; }

/* 主卡 */
.hero-card { position: relative; background: rgba(255,255,255,0.04); border: 1rpx solid rgba(255,255,255,0.08); border-radius: 28rpx; padding: 56rpx 36rpx 44rpx; text-align: center; margin-bottom: 32rpx; overflow: hidden; }
.hero-glow { position: absolute; top: -40rpx; left: 50%; transform: translateX(-50%); width: 500rpx; height: 400rpx; pointer-events: none; }
.hero-icon { font-size: 80rpx; display: block; margin-bottom: 16rpx; }
.hero-level { font-size: 40rpx; font-weight: 700; display: block; margin-bottom: 8rpx; }
.hero-code { font-size: 28rpx; display: block; margin-bottom: 16rpx; opacity: 0.8; letter-spacing: 4rpx; }
.hero-desc { font-size: 26rpx; color: rgba(255,255,255,0.6); line-height: 1.7; }

/* 区块卡片 */
.section-card { background: rgba(255,255,255,0.04); border: 1rpx solid rgba(255,255,255,0.08); border-radius: 24rpx; padding: 36rpx; margin-bottom: 24rpx; }
.sec-title { font-size: 30rpx; font-weight: 700; color: #fff; margin-bottom: 28rpx; display: block; }

/* 三维坐标 */
.axis-list {}
.axis-row { display: flex; align-items: center; margin-bottom: 22rpx; }
.axis-row:last-child { margin-bottom: 0; }
.axis-left { display: flex; align-items: center; width: 180rpx; flex-shrink: 0; }
.axis-icon { font-size: 28rpx; margin-right: 8rpx; }
.axis-name { font-size: 24rpx; color: rgba(255,255,255,0.75); }
.axis-bar-wrap { flex: 1; margin: 0 16rpx; }
.axis-bar-bg { height: 14rpx; background: rgba(255,255,255,0.06); border-radius: 7rpx; overflow: hidden; }
.axis-bar-fill { height: 100%; border-radius: 7rpx; transition: width 0.5s; }
.axis-pct { font-size: 24rpx; font-weight: 600; width: 70rpx; text-align: right; flex-shrink: 0; }
.axis-tag { font-size: 20rpx; width: 100rpx; text-align: center; flex-shrink: 0; margin-left: 8rpx; }
.axis-note { display: block; font-size: 24rpx; color: rgba(255,255,255,0.5); line-height: 1.7; margin-top: 24rpx; }

/* 特质 */
.trait-list {}
.trait-item { display: flex; align-items: flex-start; margin-bottom: 14rpx; }
.trait-item:last-child { margin-bottom: 0; }
.trait-bullet { font-size: 22rpx; margin-right: 10rpx; flex-shrink: 0; margin-top: 2rpx; }
.trait-text { font-size: 24rpx; color: rgba(255,255,255,0.7); line-height: 1.6; }

/* 场景 */
.scene-list {}
.scene-item { margin-bottom: 24rpx; }
.scene-item:last-child { margin-bottom: 0; }
.scene-header { display: flex; align-items: center; margin-bottom: 10rpx; }
.scene-icon { font-size: 30rpx; margin-right: 10rpx; }
.scene-name { font-size: 26rpx; font-weight: 600; color: #fff; }
.scene-desc { font-size: 24rpx; color: rgba(255,255,255,0.6); line-height: 1.7; }

/* 配对指南 */
.pair-list {}
.pair-item { margin-bottom: 20rpx; padding-bottom: 20rpx; border-bottom: 1rpx solid rgba(255,255,255,0.04); }
.pair-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.pair-header { display: flex; align-items: center; margin-bottom: 8rpx; }
.pair-icon { font-size: 28rpx; margin-right: 8rpx; }
.pair-name { font-size: 26rpx; font-weight: 600; color: #fff; }
.pair-harmony { font-size: 20rpx; margin-left: auto; font-weight: 600; }
.pair-tip { font-size: 24rpx; color: rgba(255,255,255,0.6); line-height: 1.6; }

/* 成长建议 */
.advice-list {}
.advice-item { display: flex; align-items: flex-start; margin-bottom: 14rpx; }
.advice-item:last-child { margin-bottom: 0; }
.advice-bullet { font-size: 22rpx; margin-right: 10rpx; flex-shrink: 0; margin-top: 2rpx; }
.advice-text { font-size: 24rpx; color: rgba(255,255,255,0.7); line-height: 1.6; }

/* 温馨提示 */
.warm-card { border-color: rgba(212,96,122,0.15); }
.warm-text { font-size: 24rpx; color: rgba(255,255,255,0.55); line-height: 1.8; }

/* 操作按钮 */
.action-row { display: flex; gap: 24rpx; margin-top: 16rpx; }
.btn-retry, .btn-back { flex: 1; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; }
.btn-retry { background: rgba(212,96,122,0.15); border: 1rpx solid rgba(212,96,122,0.3); }
.btn-retry text { font-size: 28rpx; color: #d4607a; font-weight: 600; }
.btn-back { background: rgba(255,255,255,0.06); border: 1rpx solid rgba(255,255,255,0.12); }
.btn-back text { font-size: 28rpx; color: rgba(255,255,255,0.6); }
</style>
