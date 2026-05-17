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
		<text class="nav-title">九型人格</text>
		<text class="nav-en">ENNEAGRAM</text>
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
			</view>
			<view class="q-options">
				<!-- 选项 A -->
				<view class="opt-card" :class="{ 'opt-selected': answers[curQ] === 'A' }" @tap="selectAnswer('A')">
					<view class="opt-badge opt-badge-a">
						<text class="opt-badge-text">A</text>
					</view>
					<text class="opt-text">{{ questions[curQ].a }}</text>
				</view>
				<!-- 选项 B -->
				<view class="opt-card" :class="{ 'opt-selected': answers[curQ] === 'B' }" @tap="selectAnswer('B')">
					<view class="opt-badge opt-badge-b">
						<text class="opt-badge-text">B</text>
					</view>
					<text class="opt-text">{{ questions[curQ].b }}</text>
				</view>
			</view>
		</view>

		<!-- 底部按钮 -->
		<view class="test-footer">
			<view class="prev-btn" v-if="curQ > 0" @tap="prevQuestion">
				<text class="prev-text">上一题</text>
			</view>
			<view class="next-btn" :class="{ 'next-btn-active': answers[curQ] }" @tap="nextQuestion">
				<text class="next-text">{{ curQ < questions.length - 1 ? '下一题' : '查看结果' }}</text>
			</view>
		</view>
	</view>

	<!-- 结果阶段 -->
	<scroll-view scroll-y class="result-scroll" v-if="phase === 'result'">
		<view class="result-phase">
			<!-- 主类型卡片 -->
			<view class="result-hero">
				<view class="hero-glow"></view>
				<text class="hero-icon">{{ mainType.icon }}</text>
				<text class="hero-num">第{{ mainType.num }}型</text>
				<text class="hero-name">{{ mainType.name }}</text>
				<text class="hero-en">{{ mainType.en }}</text>
				<view class="hero-rule"></view>
				<text class="hero-desc">{{ mainType.desc }}</text>
			</view>

			<!-- 核心动机 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot"></view>
					<text class="label-text">核心动机与恐惧</text>
				</view>
				<view class="motive-grid">
					<view class="motive-item">
						<text class="motive-label">核心动机</text>
						<text class="motive-val">{{ mainType.motive }}</text>
					</view>
					<view class="motive-line"></view>
					<view class="motive-item">
						<text class="motive-label">核心恐惧</text>
						<text class="motive-val">{{ mainType.fear }}</text>
					</view>
				</view>
			</view>

			<!-- 九型雷达图 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--purple"></view>
					<text class="label-text">九型分布</text>
				</view>
				<view class="radar-list">
					<view class="radar-item" v-for="(item, idx) in radarData" :key="idx">
						<view class="radar-left">
							<text class="radar-icon">{{ item.icon }}</text>
							<text class="radar-name">{{ item.name }}</text>
						</view>
						<view class="radar-bar-wrap">
							<view class="radar-bar" :style="{ width: item.pct + '%', background: item.color }"></view>
						</view>
						<text class="radar-pct">{{ item.pct }}%</text>
					</view>
				</view>
			</view>

			<!-- 侧翼分析 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--gold"></view>
					<text class="label-text">侧翼分析</text>
				</view>
				<view class="wing-row">
					<view class="wing-item">
						<text class="wing-label">左翼 {{ mainType.num }}w{{ wingLeft }}</text>
						<text class="wing-desc">{{ getTypeInfo(wingLeft).brief }}</text>
					</view>
					<view class="wing-divider"></view>
					<view class="wing-item">
						<text class="wing-label">右翼 {{ mainType.num }}w{{ wingRight }}</text>
						<text class="wing-desc">{{ getTypeInfo(wingRight).brief }}</text>
					</view>
				</view>
			</view>

			<!-- 性格特质 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--cyan"></view>
					<text class="label-text">性格特质</text>
				</view>
				<view class="trait-tags">
					<view class="trait-tag" v-for="(t, idx) in mainType.traits" :key="idx">
						<text class="tag-text">{{ t }}</text>
					</view>
				</view>
			</view>

			<!-- 发展建议 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--orange"></view>
					<text class="label-text">成长建议</text>
				</view>
				<view class="advice-list">
					<view class="advice-item" v-for="(adv, idx) in mainType.advices" :key="idx">
						<view class="advice-dot"></view>
						<text class="advice-text">{{ adv }}</text>
					</view>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="action-area">
				<view class="action-btn primary-btn" @tap="onDeepAnalysis">
					<text class="btn-text">深度解读 ✦</text>
				</view>
				<view class="action-btn secondary-btn" @tap="onRetest">
					<text class="btn-text btn-text-secondary">重新测试</text>
				</view>
			</view>
		</view>
	</scroll-view>
</view>
</template>

<script>
// 36道测试题
var QUESTIONS = [
	{ a: '服务他人、因应他人的需求，对我而言是重要的。', b: '寻求看待事物和做事的各种方法，对我而言是重要的。' },
	{ a: '面对困扰时，我会陷在里面。', b: '面对困扰时，我会想办法放轻松。' },
	{ a: '我向来是愿意支持他人，为他人付出，喜欢有人为伴的。', b: '我向来是严肃的、克制的、喜欢讨论问题。' },
	{ a: '我向来认为自己是个平静的、随和的人。', b: '我向来认为自己是个严肃的、自律的人。' },
	{ a: '我喜欢社交生活且喜欢结识各样的朋友。', b: '我对社交生活不感兴趣，而且怕与人交往。' },
	{ a: '做决定对我而言通常很困难。', b: '做决定对我而言很少有困难。' },
	{ a: '我一向认为我自己是务实的、脚踏实地的。', b: '我一向认为我自己是有创意的、具原创性的。' },
	{ a: '大体而言，我太开放、天真。', b: '大体而言，我太机警、谨慎。' },
	{ a: '我主要是借由思考、分析资讯来做决定。', b: '我主要是借由感觉、依循直觉来做决定。' },
	{ a: '我一向觉得自己很有自信、很强悍。', b: '我一向觉得自己很谦虚、很温和。' },
	{ a: '我通常是冷静、镇定、闲适的。', b: '我通常是认真、急躁、绷紧的。' },
	{ a: '我常担心事情不可行，或担心结果不完美。', b: '我常担心错失机会，或担心错过好玩的事。' },
	{ a: '我通常把注意力放在别人的需要上。', b: '我通常把注意力放在自己的需要上。' },
	{ a: '我通常觉得主导情况是负担。', b: '我通常觉得主导情况是乐事。' },
	{ a: '大体而言，我是乐观的。', b: '大体而言，我是悲观的。' },
	{ a: '我倾向把焦点放在人的问题上。', b: '我倾向把焦点放在工作的问题上。' },
	{ a: '我向来是个重感情的人。', b: '我向来是个重逻辑的人。' },
	{ a: '我一向是努力工作、有纪律的。', b: '我一向是随兴所至、不太努力的。' },
	{ a: '我主要的专长是看到事情的可能性。', b: '我主要的专长是看到事情的实用性。' },
	{ a: '我倾向于依赖他人。', b: '我倾向于独立作业。' },
	{ a: '大体而言，我是个心胸宽大的人。', b: '大体而言，我是个吹毛求疵的人。' },
	{ a: '我通常是很快活、好玩的。', b: '我通常是严肃、忧郁的。' },
	{ a: '我通常很难拒绝他人的请求。', b: '我通常很难对他人提出请求。' },
	{ a: '我通常很难表达自己内在的感受。', b: '我通常很容易表达自己内在的感受。' },
	{ a: '面对全新的经验时，我通常会自问这是否精彩、有用。', b: '面对全新的经验时，我通常会自问这是否好玩、有趣。' },
	{ a: '做决定时，我通常依据逻辑和分析。', b: '做决定时，我通常依据感觉和价值观。' },
	{ a: '我一向是愿意支持他人，为他人付出，喜欢有人为伴的。', b: '我向来是严肃的、克制的、喜欢讨论问题。' },
	{ a: '我向来认为自己是个平静的、随和的人。', b: '我向来认为自己是个严肃的、自律的人。' },
	{ a: '我向来是愿意支持他人，为他人付出，喜欢有人为伴的。', b: '我向来是严肃的、克制的、喜欢讨论问题。' },
	{ a: '我向来认为自己是个平静的、随和的人。', b: '我向来认为自己是个严肃的、自律的人。' },
	{ a: '我喜欢社交生活且喜欢结识各样的朋友。', b: '我对社交生活不感兴趣，而且怕与人交往。' },
	{ a: '做决定对我而言通常很困难。', b: '做决定对我而言很少有困难。' },
	{ a: '我一向认为我自己是务实的、脚踏实地的。', b: '我一向认为我自己是有创意的、具原创性的。' },
	{ a: '大体而言，我太开放、天真。', b: '大体而言，我太机警、谨慎。' },
	{ a: '我主要是借由思考、分析资讯来做决定。', b: '我主要是借由感觉、依循直觉来做决定。' },
	{ a: '我一向觉得自己很有自信、很强悍。', b: '我一向觉得自己很谦虚、很温和。' }
]

// 9组题目映射（每组4题对应1-9号人格）
// 题号1-36，索引0-35
// 第1组(1号): Q1,Q2,Q27,Q28 → 索引 0,1,26,27
// 第2组(2号): Q3,Q4,Q29,Q30 → 索引 2,3,28,29
// 第3组(3号): Q5,Q6,Q31,Q32 → 索引 4,5,30,31
// 第4组(4号): Q7,Q8,Q33,Q34 → 索引 6,7,32,33
// 第5组(5号): Q9,Q10,Q35,Q36 → 索引 8,9,34,35
// 第6组(6号): Q11,Q12 → 索引 10,11
// 第7组(7号): Q13,Q14 → 索引 12,13
// 第8组(8号): Q15,Q16 → 索引 14,15
// 第9组(9号): Q17,Q18 → 索引 16,17
// 补充映射（Q19-Q26对应1-8号加强）：
// Q19→1号, Q20→2号, Q21→3号, Q22→4号, Q23→5号, Q24→6号, Q25→7号, Q26→8号
var GROUP_MAP = [
	[0, 1, 26, 27],    // 1号 完美主义者
	[2, 3, 28, 29],    // 2号 助人者
	[4, 5, 30, 31],    // 3号 成就者
	[6, 7, 32, 33],    // 4号 个人主义者
	[8, 9, 34, 35],    // 5号 探索者
	[10, 11],           // 6号 忠诚者
	[12, 13],           // 7号 享乐者
	[14, 15],           // 8号 挑战者
	[16, 17, 18, 19, 20, 21, 22, 23, 24, 25]  // 9号 和平者（剩余题补充）
]

// A选项得分权重（对应每组的A倾向）
// 1号A: 严谨完美 | 2号A: 助人付出 | 3号A: 社交成就 | 4号A: 创意感受
// 5号A: 思考分析 | 6号A: 忧虑谨慎 | 7号A: 乐观享乐 | 8号A: 自信主导 | 9号A: 平和随和
var A_SCORES = [3, 3, 3, 2, 2, 1, 2, 1, 3, 1, 3, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 3, 2, 3, 2, 2, 1, 1, 1, 3, 1]
var B_SCORES = [1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 3, 3, 3, 1, 1, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 1, 3]

// 九型人格数据
var TYPE_DATA = {
	1: {
		num: 1, name: '完美主义者', en: 'The Reformer', icon: '🎯',
		desc: '你有着强烈的内在标准和对秩序的追求。你相信凡事都有正确的方式，并致力于让世界变得更好。你诚实、正直，始终如一地追求进步。',
		motive: '做正确的事，追求完美与进步',
		fear: '变得腐败、邪恶或缺陷',
		traits: ['自律', '严谨', '有原则', '追求完美', '批判性思维', '责任感强'],
		advices: ['学会接纳"足够好"而非追求绝对完美', '对他人多一些宽容，减少评判', '关注内心的感受，而非仅仅遵循规则', '允许自己犯错，将错误视为成长的机会'],
		brief: '注重原则与标准，追求正确与完善',
		color: '#e88555'
	},
	2: {
		num: 2, name: '助人者', en: 'The Helper', icon: '🤝',
		desc: '你天生关注他人的需求，并从中获得满足感。你温暖、体贴、善解人意，总是把别人的需要放在首位。你的价值感来自于被需要。',
		motive: '被爱与被需要，帮助他人',
		fear: '变得没有价值、不被需要',
		traits: ['温暖', '慷慨', '善解人意', '自我牺牲', '人际敏感', '取悦他人'],
		advices: ['学会识别并表达自己的需求', '不要因付出而期待回报', '建立健康的界限感', '学会接受他人的帮助'],
		brief: '关注他人需求，以爱与付出定义自我',
		color: '#d4607a'
	},
	3: {
		num: 3, name: '成就者', en: 'The Achiever', icon: '🏆',
		desc: '你目标明确，追求成功与认可。你高效、自信，善于展现最好的一面。你相信行动胜于言语，用实际成果证明自己的价值。',
		motive: '获得成功与认可，证明自身价值',
		fear: '变得毫无价值、失败',
		traits: ['高效', '自信', '目标导向', '适应力强', '竞争力', '形象管理'],
		advices: ['关注真实的内在感受，而非外在形象', '允许自己休息，不必时刻追求高效', '学会在亲密关系中展现脆弱', '定义成功不仅限于成就和认可'],
		brief: '追求成功与认可，用成就定义自我价值',
		color: '#dda03f'
	},
	4: {
		num: 4, name: '个人主义者', en: 'The Individualist', icon: '🎨',
		desc: '你追求真实与独特，渴望深刻地体验生命的每一刻。你敏感、富有创造力，总是能感受到他人忽略的细微情感。你相信独一无二才是真实的。',
		motive: '找到真实的自我，追求独特与深刻',
		fear: '变得平庸、没有身份认同',
		traits: ['敏感', '创造力', '追求真实', '情感深沉', '独特审美', '内省'],
		advices: ['不要沉溺于负面情绪，学会行动', '接受平凡也是一种美好', '关注当下而非过去的遗憾', '建立稳定的生活节奏'],
		brief: '追求独特与深刻体验，以感受定义真实',
		color: '#9d72ff'
	},
	5: {
		num: 5, name: '探索者', en: 'The Investigator', icon: '🔬',
		desc: '你渴望理解世界运行的规律，通过观察、分析和思考来构建自己的知识体系。你独立、专注，更愿意在内心世界中探索而非社交场合中消耗能量。',
		motive: '获取知识与能力，理解世界',
		fear: '变得无用、无能或被消耗',
		traits: ['独立', '分析力强', '求知欲', '冷静客观', '深度思考', '珍惜能量'],
		advices: ['不要过度囤积知识，学会分享与行动', '走出思维世界，参与现实互动', '表达你的感受，而不只是想法', '信任自己的能力，不必事事精通'],
		brief: '以知识与思考构建安全，追求理解与能力',
		color: '#6898ce'
	},
	6: {
		num: 6, name: '忠诚者', en: 'The Loyalist', icon: '🛡️',
		desc: '你时刻关注潜在风险，追求安全感与确定性。你忠诚、负责，对信任的人给予坚定支持。你在警惕与勇气之间不断寻找平衡。',
		motive: '获得安全感与确定的支持',
		fear: '失去支持与指引，陷入不确定',
		traits: ['忠诚', '警觉', '责任感', '准备充分', '质疑精神', '寻求安全'],
		advices: ['信任自己的判断，减少不必要的担忧', '接纳不确定性是生活的一部分', '关注积极的可能性，而非只看风险', '培养内在的力量感，而非过度依赖外部支持'],
		brief: '以警惕与忠诚应对不确定，寻求安全与支持',
		color: '#5ca8b8'
	},
	7: {
		num: 7, name: '享乐者', en: 'The Enthusiast', icon: '🌈',
		desc: '你充满活力与好奇心，追求丰富多样的体验。你乐观、善于发现可能性，总是在规划下一个精彩的冒险。你相信生活应该是快乐而充实的。',
		motive: '保持快乐与自由，体验一切可能',
		fear: '陷入痛苦、被剥夺快乐',
		traits: ['乐观', '好奇心', '多才多艺', '即兴灵活', '追求新鲜', '避免痛苦'],
		advices: '学会面对而非逃避痛苦与不适'.split('。').filter(function(s){return s}).concat(['深入完成一件事，而非浅尝辄止', '学会享受当下的宁静，而非追逐刺激', '允许自己慢下来，感受深层的满足']),
		brief: '追求快乐与自由，以新鲜体验逃避痛苦',
		color: '#3ec9c1'
	},
	8: {
		num: 8, name: '挑战者', en: 'The Challenger', icon: '⚡',
		desc: '你天生强大而果断，追求掌控与影响力。你直率、勇敢，不愿被任何人或环境所控制。你保护自己在乎的人，用力量与正义定义自己的存在。',
		motive: '保护自己与掌控环境，展现力量',
		fear: '被控制、变得脆弱或受伤',
		traits: ['果断', '力量感', '直率', '保护欲', '反抗不公', '掌控欲'],
		advices: ['展现脆弱不是软弱，是真正的勇气', '学会倾听与妥协，而非只靠力量', '关注他人的感受，减少压迫感', '控制愤怒，将其转化为建设性的力量'],
		brief: '以力量与掌控保护自我，追求正义与影响',
		color: '#c44d4d'
	},
	9: {
		num: 9, name: '和平者', en: 'The Peacemaker', icon: '☮️',
		desc: '你追求内外的和谐与平静，善于在不同立场间搭建桥梁。你温和、包容，能够理解各种观点。你相信避免冲突、维持安宁是最佳生活方式。',
		motive: '保持内心平静与外在和谐',
		fear: '失去与断裂联系，陷入冲突',
		traits: ['随和', '包容', '调解能力', '避免冲突', '适应性强', '感受迟钝'],
		advices: ['不要压抑自己的需求与愤怒', '积极表达立场，回避冲突不代表和平', '关注自己的优先事项，而非随波逐流', '识别被动抵抗的行为模式'],
		brief: '追求和谐与平静，以包容与回避维持安宁',
		color: '#a89070'
	}
}

function makeStars() {
	var arr = []
	for (var i = 0; i < 50; i++) {
		var sz = (Math.random() * 3 + 1).toFixed(0)
		arr.push({
			left: (Math.random() * 100).toFixed(1) + '%',
			top: (Math.random() * 100).toFixed(1) + '%',
			width: sz + 'rpx', height: sz + 'rpx',
			opacity: (Math.random() * 0.5 + 0.1).toFixed(2),
			animationDelay: (Math.random() * 5).toFixed(1) + 's',
			animationDuration: (Math.random() * 3 + 2).toFixed(1) + 's'
		})
	}
	return arr
}

export default {
	data: function() {
		return {
			stars: makeStars(),
			phase: 'test',   // test | result
			curQ: 0,
			answers: {},      // { 0: 'A', 1: 'B', ... }
			questions: QUESTIONS,
			mainType: {},
			radarData: [],
			wingLeft: 0,
			wingRight: 0,
			scores: {}        // { 1: score, 2: score, ... }
		}
	},
	computed: {
		pageStyle: function() {
			var h = 44
			try { var info = uni.getWindowInfo ? uni.getWindowInfo() : uni.getSystemInfoSync(); if (info.statusBarHeight) h = info.statusBarHeight } catch(e){}
			return { paddingTop: h + 'px' }
		},
		progressPct: function() {
			return Math.round(((this.curQ + 1) / this.questions.length) * 100)
		}
	},
	onLoad: function() {
		// 检查是否有已保存的结果
		var saved = uni.getStorageSync('enneagram_result')
		if (saved) {
			try {
				var r = JSON.parse(saved)
				if (r.mainType && r.mainType.num) {
					this.mainType = r.mainType
					this.radarData = r.radarData
					this.wingLeft = r.wingLeft
					this.wingRight = r.wingRight
					this.scores = r.scores
					this.phase = 'result'
				}
			} catch(e) {}
		}
	},
	methods: {
		goBack: function() {
			uni.navigateBack({ delta: 1 })
		},
		_saveToDb: function() {
			var uid = 0
			try { uid = Number(uni.getStorageSync('xinyu_user_id')) || 0 } catch(e) {}
			if (!uid) return
			var self = this
			var summary = self.mainType ? (self.mainType.code + '号' + self.mainType.name) : ''
			uni.request({
				url: (typeof SHADOW_API_BASE !== 'undefined' ? SHADOW_API_BASE : 'http://43.143.169.226') + '/api/assessments/submit',
				method: 'POST',
				header: { 'Content-Type': 'application/json' },
				data: {
					user_id: uid,
					test_type: 'enneagram',
					summary: summary,
					result_json: { mainType: self.mainType, radarData: self.radarData, wingLeft: self.wingLeft, wingRight: self.wingRight, scores: self.scores },
					score_json: self.scores,
					question_count: self.questions.length
				}
			})
		},
		selectAnswer: function(choice) {
			this.$set(this.answers, this.curQ, choice)
		},
		prevQuestion: function() {
			if (this.curQ > 0) this.curQ--
		},
		nextQuestion: function() {
			if (!this.answers[this.curQ]) {
				uni.showToast({ title: '请先选择一个选项', icon: 'none' })
				return
			}
			if (this.curQ < this.questions.length - 1) {
				this.curQ++
			} else {
				this.calculateResult()
			}
		},
		calculateResult: function() {
			uni.showLoading({ title: '解析中...' })
			var self = this
			setTimeout(function() {
				// 计算每型的分数
				var scores = {}
				for (var t = 1; t <= 9; t++) scores[t] = 0

				// 基于A/B选项和权重计算
				for (var i = 0; i < self.questions.length; i++) {
					var ans = self.answers[i]
					if (ans === 'A') {
						// A选项对应的型别加分
						var aScore = A_SCORES[i]
						if (aScore) scores[aScore] = (scores[aScore] || 0) + 1
					} else if (ans === 'B') {
						var bScore = B_SCORES[i]
						if (bScore) scores[bScore] = (scores[bScore] || 0) + 1
					}
				}

				// 额外：基于组别映射加强
				for (var g = 0; g < GROUP_MAP.length; g++) {
					var typeNum = g + 1
					var group = GROUP_MAP[g]
					var groupScore = 0
					for (var gi = 0; gi < group.length; gi++) {
						var qIdx = group[gi]
						if (qIdx < self.questions.length) {
							var a = self.answers[qIdx]
							if (a === 'A') groupScore += 2
							else if (a === 'B') groupScore += 1
						}
					}
					scores[typeNum] = (scores[typeNum] || 0) + groupScore
				}

				self.scores = scores

				// 找出主类型
				var maxScore = 0, mainNum = 9
				for (var n = 1; n <= 9; n++) {
					if (scores[n] > maxScore) {
						maxScore = scores[n]
						mainNum = n
					}
				}

				self.mainType = TYPE_DATA[mainNum]

				// 侧翼（相邻类型）
				self.wingLeft = mainNum === 1 ? 9 : mainNum - 1
				self.wingRight = mainNum === 9 ? 1 : mainNum + 1

				// 雷达图数据
				var totalScore = 0
				for (var s = 1; s <= 9; s++) totalScore += scores[s]
				var radar = []
				for (var r = 1; r <= 9; r++) {
					var td = TYPE_DATA[r]
					radar.push({
						icon: td.icon,
						name: td.num + '号 ' + td.name,
						pct: totalScore > 0 ? Math.round(scores[r] / totalScore * 100) : 0,
						color: td.color
					})
				}
				self.radarData = radar

				// 保存结果
				uni.setStorageSync('enneagram_result', JSON.stringify({
					mainType: self.mainType,
					radarData: self.radarData,
					wingLeft: self.wingLeft,
					wingRight: self.wingRight,
					scores: self.scores
				}))
				self._saveToDb()

				self.phase = 'result'
				uni.hideLoading()
			}, 800)
		},
		getTypeInfo: function(num) {
			return TYPE_DATA[num] || { brief: '' }
		},
		onDeepAnalysis: function() {
			uni.showToast({ title: '深度解读功能开发中...', icon: 'none' })
		},
		onRetest: function() {
			var self = this
			uni.showModal({
				title: '重新测试',
				content: '确定要重新开始测试吗？当前结果将被覆盖。',
				success: function(res) {
					if (res.confirm) {
						uni.removeStorageSync('enneagram_result')
						self.phase = 'test'
						self.curQ = 0
						self.answers = {}
					}
				}
			})
		}
	}
}
</script>

<style scoped>
.page {
	position: relative;
	min-height: 100vh;
	background:
		radial-gradient(ellipse 100% 50% at 50% 0%, rgba(200,188,255,0.32) 0%, rgba(200,188,255,0.08) 40%, transparent 65%),
		linear-gradient(180deg, #faf8ff 0%, #f5f1fc 30%, #efeaf9 60%, #e8e2f5 100%);
	overflow: hidden;
}

/* 星空 */
.star-layer { position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.star {
	position: absolute;
	border-radius: 50%;
	background: rgba(175,160,225,0.50);
	animation: twinkle ease-in-out infinite alternate;
}
@keyframes twinkle { 0%{opacity:0.15;transform:scale(0.8)} 100%{opacity:0.65;transform:scale(1.2)} }
.orb {
	position: absolute; border-radius: 50%;
	filter: blur(80px); pointer-events: none; z-index: 1;
}
.orb-a {
	width: 500rpx; height: 500rpx;
	right: -160rpx; top: 100rpx;
	background: radial-gradient(circle, rgba(200,180,255,0.40), transparent 70%);
	animation: drift 18s ease-in-out infinite;
}
@keyframes drift { 0%,100%{transform:translate(0,0) scale(1);opacity:0.45} 50%{transform:translate(-30rpx,30rpx) scale(1.1);opacity:0.72} }

/* 导航 */
.nav-bar {
	position: relative; z-index: 50;
	display: flex; align-items: center;
	padding: 16rpx 28rpx 12rpx;
	height: 88rpx;
	box-sizing: border-box;
}
.nav-left { width: 64rpx; display: flex; align-items: center; }
.back-icon { font-size: 36rpx; color: #322c52; font-weight: 500; }
.nav-title { font-size: 32rpx; font-weight: 700; color: #322c52; letter-spacing: 6rpx; margin-left: 8rpx; }
.nav-en { font-size: 18rpx; font-weight: 300; color: rgba(130,118,186,0.50); letter-spacing: 4rpx; font-style: italic; margin-left: 12rpx; margin-top: 4rpx; }

/* 进度条 */
.progress-wrap {
	position: relative; z-index: 10;
	display: flex; align-items: center;
	padding: 0 32rpx 16rpx;
	gap: 16rpx;
}
.progress-bg {
	flex: 1; height: 6rpx; border-radius: 6rpx;
	background: rgba(210,200,235,0.30);
	overflow: hidden;
}
.progress-fill {
	height: 100%; border-radius: 6rpx;
	background: linear-gradient(90deg, #9d72ff, #7d6bd6);
	box-shadow: 0 0 14rpx rgba(157,114,255,0.30);
	transition: width 0.4s ease;
}
.progress-text {
	font-size: 22rpx; color: rgba(130,118,186,0.60);
	font-weight: 500; letter-spacing: 2rpx;
	white-space: nowrap;
}

/* 答题 */
.test-phase {
	position: relative; z-index: 10;
	padding: 0 28rpx;
	display: flex;
	flex-direction: column;
	height: calc(100vh - 200rpx);
}
.q-card {
	flex: 1;
	background: rgba(255,255,255,0.92);
	border-radius: 28rpx;
	padding: 32rpx 28rpx;
	box-shadow: 0 8rpx 32rpx rgba(100,88,170,0.09);
	border: 1rpx solid rgba(255,255,255,0.75);
}
.q-num {
	display: flex; align-items: center;
	margin-bottom: 28rpx;
}
.q-num-label {
	font-size: 24rpx; font-weight: 700;
	color: #9d72ff;
	letter-spacing: 3rpx;
	background: rgba(157,114,255,0.08);
	padding: 6rpx 18rpx;
	border-radius: 20rpx;
	border: 1rpx solid rgba(157,114,255,0.15);
}
.q-options {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}
.opt-card {
	display: flex;
	align-items: flex-start;
	padding: 24rpx 20rpx;
	background: rgba(250,248,255,0.60);
	border-radius: 20rpx;
	border: 2rpx solid rgba(210,200,235,0.20);
	transition: all 0.25s ease;
}
.opt-card.opt-selected {
	background: rgba(157,114,255,0.08);
	border-color: rgba(157,114,255,0.35);
	box-shadow: 0 4rpx 16rpx rgba(157,114,255,0.12);
}
.opt-badge {
	width: 44rpx; height: 44rpx;
	border-radius: 50%;
	display: flex; align-items: center; justify-content: center;
	flex-shrink: 0;
	margin-right: 16rpx;
	margin-top: 2rpx;
}
.opt-badge-a {
	background: rgba(157,114,255,0.10);
	border: 1rpx solid rgba(157,114,255,0.20);
}
.opt-badge-b {
	background: rgba(62,201,193,0.10);
	border: 1rpx solid rgba(62,201,193,0.20);
}
.opt-badge-text {
	font-size: 22rpx; font-weight: 700;
}
.opt-badge-a .opt-badge-text { color: #9d72ff; }
.opt-badge-b .opt-badge-text { color: #3ec9c1; }
.opt-selected .opt-badge-a {
	background: rgba(157,114,255,0.20);
	border-color: rgba(157,114,255,0.40);
}
.opt-selected .opt-badge-b {
	background: rgba(62,201,193,0.20);
	border-color: rgba(62,201,193,0.40);
}
.opt-text {
	font-size: 26rpx;
	color: #3c3268;
	line-height: 1.7;
	letter-spacing: 1rpx;
	flex: 1;
}
.opt-selected .opt-text {
	color: #2c2450;
	font-weight: 500;
}

/* 底部按钮 */
.test-footer {
	display: flex;
	gap: 16rpx;
	padding: 24rpx 0 40rpx;
	align-items: center;
}
.prev-btn {
	width: 180rpx; height: 84rpx;
	border-radius: 22rpx;
	background: rgba(255,255,255,0.85);
	border: 1rpx solid rgba(210,200,235,0.30);
	display: flex; align-items: center; justify-content: center;
}
.prev-text { font-size: 26rpx; color: #7d6bd6; font-weight: 500; letter-spacing: 2rpx; }
.next-btn {
	flex: 1; height: 84rpx;
	border-radius: 22rpx;
	background: linear-gradient(148deg, #c4bdd6 0%, #b5aec8 52%, #a8a1bc 100%);
	display: flex; align-items: center; justify-content: center;
	transition: all 0.25s ease;
}
.next-btn-active {
	background: linear-gradient(148deg, #9d72ff 0%, #8276ba 52%, #7264af 100%) !important;
	box-shadow: 0 8rpx 28rpx rgba(157,114,255,0.30);
}
.next-text {
	font-size: 28rpx; color: rgba(255,255,255,0.96);
	font-weight: 600; letter-spacing: 4rpx;
}

/* 结果阶段 */
.result-scroll {
	position: relative; z-index: 10;
	height: calc(100vh - 88rpx);
}
.result-phase {
	padding: 12rpx 24rpx 60rpx;
}

/* 主类型卡片 */
.result-hero {
	position: relative;
	background: rgba(255,255,255,0.92);
	border-radius: 28rpx;
	padding: 48rpx 32rpx 36rpx;
	margin-bottom: 20rpx;
	display: flex; flex-direction: column; align-items: center;
	box-shadow: 0 8rpx 32rpx rgba(100,88,170,0.09);
	border: 1rpx solid rgba(255,255,255,0.75);
	overflow: hidden;
}
.hero-glow {
	position: absolute;
	width: 300rpx; height: 300rpx;
	border-radius: 50%;
	background: radial-gradient(circle, rgba(157,114,255,0.12), transparent 70%);
	top: -80rpx; left: 50%;
	transform: translateX(-50%);
	pointer-events: none;
}
.hero-icon { font-size: 72rpx; margin-bottom: 16rpx; position: relative; z-index: 2; }
.hero-num {
	font-size: 22rpx; color: #9d72ff; font-weight: 600;
	letter-spacing: 4rpx; margin-bottom: 8rpx;
	background: rgba(157,114,255,0.08);
	padding: 4rpx 20rpx; border-radius: 20rpx;
	border: 1rpx solid rgba(157,114,255,0.15);
	position: relative; z-index: 2;
}
.hero-name {
	font-size: 40rpx; font-weight: 700;
	color: #2c2450; letter-spacing: 6rpx;
	margin-bottom: 6rpx;
	position: relative; z-index: 2;
}
.hero-en {
	font-size: 20rpx; color: rgba(157,114,255,0.50);
	letter-spacing: 4rpx; font-style: italic; font-weight: 300;
	margin-bottom: 24rpx;
	position: relative; z-index: 2;
}
.hero-rule {
	width: 60rpx; height: 1.5rpx;
	background: linear-gradient(90deg, transparent, rgba(157,114,255,0.45), transparent);
	margin-bottom: 24rpx;
	position: relative; z-index: 2;
}
.hero-desc {
	font-size: 26rpx; color: #48407a;
	line-height: 1.9; letter-spacing: 1rpx;
	text-align: center;
	position: relative; z-index: 2;
	padding: 0 16rpx;
}

/* 通用卡片 */
.section-card {
	background: rgba(255,255,255,0.88);
	border-radius: 28rpx;
	padding: 28rpx 28rpx 24rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 6rpx 28rpx rgba(100,88,170,0.08);
	border: 1rpx solid rgba(255,255,255,0.65);
}
.card-label {
	display: flex; align-items: center;
	gap: 12rpx; margin-bottom: 20rpx;
}
.label-dot {
	width: 10rpx; height: 10rpx; border-radius: 50%;
	background: #9d72ff;
	box-shadow: 0 0 10rpx rgba(157,114,255,0.45);
}
.label-dot--gold { background: #dda03f; box-shadow: 0 0 10rpx rgba(221,160,63,0.45); }
.label-dot--purple { background: #9685ee; box-shadow: 0 0 10rpx rgba(150,133,238,0.45); }
.label-dot--cyan { background: #3ec9c1; box-shadow: 0 0 10rpx rgba(62,201,193,0.45); }
.label-dot--orange { background: #e88555; box-shadow: 0 0 10rpx rgba(232,133,85,0.45); }
.label-text { font-size: 26rpx; font-weight: 600; color: #2c2450; letter-spacing: 3rpx; }

/* 核心动机 */
.motive-grid {
	display: flex; flex-direction: column; gap: 16rpx;
}
.motive-item {
	display: flex; justify-content: space-between; align-items: center;
	padding: 16rpx 18rpx;
	background: rgba(157,114,255,0.04);
	border-radius: 16rpx;
	border: 1rpx solid rgba(157,114,255,0.08);
}
.motive-label { font-size: 24rpx; color: #9088b8; font-weight: 500; }
.motive-val { font-size: 25rpx; color: #3c3268; font-weight: 600; max-width: 420rpx; text-align: right; }
.motive-line { height: 1rpx; background: rgba(210,200,235,0.15); }

/* 雷达图 */
.radar-list {
	display: flex; flex-direction: column; gap: 14rpx;
}
.radar-item {
	display: flex; align-items: center; gap: 12rpx;
}
.radar-left {
	width: 180rpx;
	display: flex; align-items: center; gap: 8rpx;
	flex-shrink: 0;
}
.radar-icon { font-size: 24rpx; line-height: 1; }
.radar-name { font-size: 22rpx; color: #48407a; font-weight: 500; white-space: nowrap; }
.radar-bar-wrap {
	flex: 1; height: 8rpx; border-radius: 4rpx;
	background: rgba(210,200,235,0.20); overflow: hidden;
}
.radar-bar {
	height: 100%; border-radius: 4rpx;
	transition: width 0.6s ease;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06);
}
.radar-pct {
	width: 70rpx; text-align: right;
	font-size: 22rpx; color: #8276ba; font-weight: 700;
}

/* 侧翼 */
.wing-row {
	display: flex; align-items: center; gap: 20rpx;
}
.wing-item {
	flex: 1;
	padding: 20rpx;
	background: rgba(250,248,255,0.60);
	border-radius: 16rpx;
	border: 1rpx solid rgba(210,200,235,0.12);
	display: flex; flex-direction: column; gap: 8rpx;
}
.wing-label { font-size: 24rpx; color: #9d72ff; font-weight: 600; letter-spacing: 2rpx; }
.wing-desc { font-size: 22rpx; color: rgba(130,118,186,0.70); line-height: 1.6; }
.wing-divider {
	width: 1rpx; height: 80rpx;
	background: rgba(210,200,235,0.20);
}

/* 性格特质标签 */
.trait-tags {
	display: flex; flex-wrap: wrap; gap: 12rpx;
}
.trait-tag {
	padding: 10rpx 22rpx;
	background: rgba(157,114,255,0.06);
	border-radius: 24rpx;
	border: 1rpx solid rgba(157,114,255,0.12);
}
.tag-text { font-size: 24rpx; color: #7d6bd6; font-weight: 500; letter-spacing: 1rpx; }

/* 发展建议 */
.advice-list {
	display: flex; flex-direction: column; gap: 16rpx;
}
.advice-item {
	display: flex; align-items: flex-start; gap: 12rpx;
}
.advice-dot {
	width: 10rpx; height: 10rpx; border-radius: 50%;
	background: #9d72ff; margin-top: 14rpx; flex-shrink: 0;
	box-shadow: 0 0 8rpx rgba(157,114,255,0.30);
}
.advice-text {
	font-size: 25rpx; color: #48407a; line-height: 1.8; letter-spacing: 1rpx;
}

/* 操作按钮 */
.action-area {
	display: flex; flex-direction: column;
	align-items: center; gap: 16rpx;
	margin-top: 32rpx; padding: 0 24rpx;
}
.action-btn {
	width: 100%; height: 92rpx;
	border-radius: 24rpx;
	display: flex; align-items: center; justify-content: center;
}
.primary-btn {
	background: linear-gradient(148deg, #9d72ff 0%, #8276ba 52%, #7264af 100%);
	box-shadow: 0 8rpx 28rpx rgba(157,114,255,0.28);
	border: 1rpx solid rgba(255,255,255,0.16);
}
.secondary-btn {
	background: rgba(255,255,255,0.85);
	border: 1rpx solid rgba(157,114,255,0.18);
	box-shadow: 0 4rpx 16rpx rgba(100,88,170,0.06);
}
.btn-text {
	font-size: 28rpx; color: rgba(255,255,255,0.96);
	font-weight: 600; letter-spacing: 3rpx;
}
.btn-text-secondary { color: #9d72ff; letter-spacing: 2rpx; }
</style>
