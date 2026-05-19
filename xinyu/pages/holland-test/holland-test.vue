<template>
<view class="page">
	<!-- 星空背景 -->
	<view class="star-layer">
		<view v-for="(s,i) in stars" :key="i" class="star" :style="s"></view>
	</view>
	<view class="orb orb-a"></view>

	<!-- 顶部导航 -->
	<view class="nav-bar">
		<view class="nav-left" @tap="goBack">
			<text class="back-icon">←</text>
		</view>
		<text class="nav-title">霍兰德职业测试</text>
		<text class="nav-en">HOLLAND CODE</text>
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
				<text class="q-type-tag" :style="{ background: curTypeData.bgColor, color: curTypeData.textColor, borderColor: curTypeData.borderColor }">{{ curTypeData.label }}</text>
			</view>
			<text class="q-text">{{ questions[curQ].text }}</text>
			<view class="q-options">
				<view class="opt-card" :class="{ 'opt-selected': answers[curQ] === 'yes' }" @tap="selectAnswer('yes')">
					<view class="opt-badge opt-badge-yes">
						<text class="opt-badge-text">是</text>
					</view>
					<text class="opt-text">符合我的情况</text>
				</view>
				<view class="opt-card" :class="{ 'opt-selected': answers[curQ] === 'no' }" @tap="selectAnswer('no')">
					<view class="opt-badge opt-badge-no">
						<text class="opt-badge-text">否</text>
					</view>
					<text class="opt-text">不太符合</text>
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
				<view class="hero-glow" :style="heroGlowStyle"></view>
				<text class="hero-icon">{{ mainType.icon }}</text>
				<text class="hero-code">{{ mainType.code }}</text>
				<text class="hero-name">{{ mainType.name }}</text>
				<text class="hero-en">{{ mainType.en }}</text>
				<view class="hero-rule" :style="heroRuleStyle"></view>
				<text class="hero-desc">{{ mainType.desc }}</text>
			</view>

			<!-- 霍兰德代码组合 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot" :style="labelDotStyle"></view>
					<text class="label-text">你的霍兰德代码</text>
				</view>
				<view class="code-row">
					<view class="code-item" v-for="(ct, idx) in topTypes" :key="idx">
						<view class="code-badge" :style="ct.badgeSty">
							<text class="code-badge-text">{{ ct.code }}</text>
						</view>
						<text class="code-name">{{ ct.name }}</text>
						<text class="code-score">{{ ct.score }}分</text>
					</view>
				</view>
			</view>

			<!-- 六维分布图 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--purple"></view>
					<text class="label-text">六维分布</text>
				</view>
				<view class="radar-list">
					<view class="radar-item" v-for="(item, idx) in radarData" :key="idx">
						<view class="radar-left">
							<text class="radar-icon">{{ item.icon }}</text>
							<text class="radar-name">{{ item.code }} {{ item.name }}</text>
						</view>
						<view class="radar-bar-wrap">
							<view class="radar-bar" :style="item.barSty"></view>
						</view>
						<text class="radar-pct">{{ item.pct }}%</text>
					</view>
				</view>
			</view>

			<!-- 核心特质 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--cyan"></view>
					<text class="label-text">核心特质</text>
				</view>
				<view class="trait-tags">
					<view class="trait-tag" v-for="(t, idx) in mainType.traits" :key="idx" :style="{ background: mainType.tagBg, borderColor: mainType.tagBorder }">
						<text class="tag-text" :style="{ color: mainType.color }">{{ t }}</text>
					</view>
				</view>
			</view>

			<!-- 职业匹配 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--gold"></view>
					<text class="label-text">职业匹配</text>
				</view>
				<view class="career-list">
					<view class="career-group" v-for="(cg, idx) in careerGroups" :key="idx">
						<view class="career-header">
							<view class="career-dot" :style="{ background: cg.color }"></view>
							<text class="career-type-name">{{ cg.code }}型 · {{ cg.name }}</text>
						</view>
						<view class="career-tags">
							<view class="career-tag" v-for="(job, jidx) in cg.jobs" :key="jidx">
								<text class="career-tag-text">{{ job }}</text>
							</view>
						</view>
					</view>
				</view>
			</view>

			<!-- 发展建议 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--orange"></view>
					<text class="label-text">发展建议</text>
				</view>
				<view class="advice-list">
					<view class="advice-item" v-for="(adv, idx) in mainType.advices" :key="idx">
						<view class="advice-dot" :style="adviceDotStyle"></view>
						<text class="advice-text">{{ adv }}</text>
					</view>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="action-area">
				<view class="action-btn primary-btn" :style="primaryBtnStyle" @tap="onDeepAnalysis">
					<text class="btn-text">深度解读 ✦</text>
				</view>
				<view class="action-btn secondary-btn" @tap="onRetest">
					<text class="btn-text btn-text-secondary" :style="{ color: mainType.color }">重新测试</text>
				</view>
			</view>
		</view>
	</scroll-view>
</view>
</template>

<script>
// 30道霍兰德测试题
// R=现实型(0-4) I=研究型(5-9) A=艺术型(10-14) S=社会型(15-19) E=企业型(20-24) C=常规型(25-29)
var QUESTIONS = [
	// 现实型（R）
	{ text: '我喜欢组装家具、维修小电器等动手类工作。', type: 'R', reverse: false },
	{ text: '我讨厌修理自行车、电器一类的工作。', type: 'R', reverse: true },
	{ text: '我小时候经常把玩具拆开，把里面看个究竟。', type: 'R', reverse: false },
	{ text: '我喜欢参与园艺种植、修剪绿植等户外实践。', type: 'R', reverse: false },
	{ text: '我喜欢使用工具制作手工制品（如木工、模型）。', type: 'R', reverse: false },
	// 研究型（I）
	{ text: '我经常不停地思考某一问题，直到想出正确的答案。', type: 'I', reverse: false },
	{ text: '我喜欢抽象思维的工作，不喜欢动手的工作。', type: 'I', reverse: false },
	{ text: '我的理想是当一名科学家。', type: 'I', reverse: false },
	{ text: '我喜欢分析数据报告并总结内在规律。', type: 'I', reverse: false },
	{ text: '我喜欢阅读科普书籍、探索事物原理。', type: 'I', reverse: false },
	// 艺术型（A）
	{ text: '我喜欢做戏剧、音乐、歌舞、新闻采访等方面的工作。', type: 'A', reverse: false },
	{ text: '音乐能使我陶醉。', type: 'A', reverse: false },
	{ text: '我有文艺方面的天赋。', type: 'A', reverse: false },
	{ text: '我喜欢创作绘画、书法、短视频等作品。', type: 'A', reverse: false },
	{ text: '我喜欢设计独特的穿搭、房间布置方案。', type: 'A', reverse: false },
	// 社会型（S）
	{ text: '我喜欢参加各种各样的聚会。', type: 'S', reverse: false },
	{ text: '我很容易结识同性别朋友。', type: 'S', reverse: false },
	{ text: '大家公认我是一名勤劳踏实、愿为大家服务的人。', type: 'S', reverse: false },
	{ text: '我喜欢帮助同学解答学习或生活中的难题。', type: 'S', reverse: false },
	{ text: '我喜欢倾听他人烦恼并给予建议。', type: 'S', reverse: false },
	// 企业型（E）
	{ text: '我喜欢成为人们注意的焦点。', type: 'E', reverse: false },
	{ text: '我喜欢不时地夸耀一下自己取得的好成就。', type: 'E', reverse: false },
	{ text: '我曾经渴望有机会参加探险。', type: 'E', reverse: false },
	{ text: '如果待遇相同，我宁愿当商品推销员，而不愿当图书管理员。', type: 'E', reverse: false },
	{ text: '我喜欢担任学生干部，统筹班级或社团工作。', type: 'E', reverse: false },
	// 常规型（C）
	{ text: '对别人借我的和我借别人的东西，我都能记得很清楚。', type: 'C', reverse: false },
	{ text: '我喜欢在做事情前，对此事情做出细致的安排。', type: 'C', reverse: false },
	{ text: '我愿意从事虽然工资少、但是比较稳定的职业。', type: 'C', reverse: false },
	{ text: '我喜欢整理文件、表格，确保数据准确。', type: 'C', reverse: false },
	{ text: '我喜欢制定学习或工作计划并严格执行。', type: 'C', reverse: false }
]

// 类型标签数据（答题阶段显示当前题目所属类型）
var TYPE_TAG = {
	R: { label: '现实型', bgColor: 'rgba(72,163,106,0.08)', textColor: '#48a36a', borderColor: 'rgba(72,163,106,0.18)' },
	I: { label: '研究型', bgColor: 'rgba(78,140,200,0.08)', textColor: '#4e8cc8', borderColor: 'rgba(78,140,200,0.18)' },
	A: { label: '艺术型', bgColor: 'rgba(165,100,210,0.08)', textColor: '#a564d2', borderColor: 'rgba(165,100,210,0.18)' },
	S: { label: '社会型', bgColor: 'rgba(212,96,122,0.08)', textColor: '#d4607a', borderColor: 'rgba(212,96,122,0.18)' },
	E: { label: '企业型', bgColor: 'rgba(221,160,63,0.08)', textColor: '#dda03f', borderColor: 'rgba(221,160,63,0.18)' },
	C: { label: '常规型', bgColor: 'rgba(88,150,180,0.08)', textColor: '#5896b4', borderColor: 'rgba(88,150,180,0.18)' }
}

// 六种类型详细数据
var TYPE_DATA = {
	R: {
		code: 'R', name: '现实型', en: 'Realistic', icon: '🔧',
		color: '#48a36a', colorDark: '#3a8a58', glowColor: 'rgba(72,163,106,0.35)',
		tagBg: 'rgba(72,163,106,0.06)', tagBorder: 'rgba(72,163,106,0.14)',
		desc: '你是天生的实践者，享受用双手创造和解决具体问题。你偏好与物打交道胜过与人交往，在操作工具、机械和自然环境中如鱼得水。踏实、直率是你的标志，你相信行动胜于空谈。',
		traits: ['动手能力强', '务实踏实', '偏好具体任务', '机械操作敏感', '户外适应力强', '直率坦诚'],
		advices: [
			'尝试发展人际沟通能力，团队协作能让你的技术发挥更大价值',
			'不要忽视抽象思维训练，理论能帮助你更系统地解决实际问题',
			'关注行业新技术趋势，保持技能的持续更新',
			'学会表达自己的感受，不必总是将情绪藏在行动背后'
		],
		careers: ['机械工程师', '电工', '消防员', '建筑工人', '厨师', '汽车维修师', '飞行员', '运动员']
	},
	I: {
		code: 'I', name: '研究型', en: 'Investigative', icon: '🔬',
		color: '#4e8cc8', colorDark: '#3e72a8', glowColor: 'rgba(78,140,200,0.35)',
		tagBg: 'rgba(78,140,200,0.06)', tagBorder: 'rgba(78,140,200,0.14)',
		desc: '你有着强烈的求知欲，善于通过分析、推理来理解世界的运行规律。你享受独立思考的过程，更愿意在思维的世界中探索而非社交场合中消耗能量。好奇心是你的驱动力。',
		traits: ['逻辑分析力强', '求知欲旺盛', '独立思考', '好奇心驱动', '抽象思维', '理性客观'],
		advices: [
			'将思考转化为行动，避免陷入"分析瘫痪"',
			'走出思维的世界，尝试与他人分享你的见解和发现',
			'关注研究的社会价值，让知识服务于真实需求',
			'培养对不确定性的容忍度，不是所有问题都有标准答案'
		],
		careers: ['科学家', '程序员', '数据分析师', '医生', '大学教授', '药剂师', '心理学研究员', '经济学家']
	},
	A: {
		code: 'A', name: '艺术型', en: 'Artistic', icon: '🎨',
		color: '#a564d2', colorDark: '#8e50b8', glowColor: 'rgba(165,100,210,0.35)',
		tagBg: 'rgba(165,100,210,0.06)', tagBorder: 'rgba(165,100,210,0.14)',
		desc: '你追求创意与自我表达，拥有敏锐的审美感知力。你反感规则与束缚，更愿意在自由的环境中用直觉和灵感创造独特的作品。情感丰富和想象力是你的天赋所在。',
		traits: ['创造力丰富', '审美敏感', '追求独特', '情感表达力强', '想象力出众', '反感束缚'],
		advices: [
			'在追求创意的同时，建立一定的执行纪律，让灵感落地为成果',
			'学会接受建设性批评，它不是对你个性的否定',
			'在自由表达和现实约束间找到平衡点',
			'关注市场与受众反馈，让作品被更多人看见和理解'
		],
		careers: ['设计师', '作家', '摄影师', '音乐人', '导演', '画家', '广告创意总监', '建筑设计师']
	},
	S: {
		code: 'S', name: '社会型', en: 'Social', icon: '🤝',
		color: '#d4607a', colorDark: '#b84e66', glowColor: 'rgba(212,96,122,0.35)',
		tagBg: 'rgba(212,96,122,0.06)', tagBorder: 'rgba(212,96,122,0.14)',
		desc: '你天生关注他人的需求与感受，在帮助和服务他人中获得深深的满足感。你善于沟通、温暖体贴，人际关系的和谐是你最看重的事。你的价值感来自被需要。',
		traits: ['善于沟通', '乐于助人', '同理心强', '团队协作好', '耐心体贴', '人际关系敏感'],
		advices: [
			'学会识别并表达自己的需求，不要总是把他人放在第一位',
			'建立健康的界限感，不是所有帮助都需要你亲力亲为',
			'培养独立决策能力，不必总是依赖他人意见',
			'关注自身成长，在助人之外也为自己留出发展空间'
		],
		careers: ['教师', '心理咨询师', 'HR专员', '社工', '护士', '培训师', '职业顾问', '社区管理者']
	},
	E: {
		code: 'E', name: '企业型', en: 'Enterprising', icon: '🏆',
		color: '#dda03f', colorDark: '#c08828', glowColor: 'rgba(221,160,63,0.35)',
		tagBg: 'rgba(221,160,63,0.06)', tagBorder: 'rgba(221,160,63,0.14)',
		desc: '你天生具有领导力和影响力，善于说服他人、推动项目落地。你追求成就和掌控感，享受竞争和挑战。自信、果断是你的标签，你相信目标是用来超越的。',
		traits: ['领导力强', '果断自信', '目标导向', '说服力出众', '竞争意识强', '善于统筹'],
		advices: [
			'在追求成果的同时，关注团队成员的感受和需求',
			'学会放权和信任他人，不必事必躬亲',
			'培养倾听习惯，领导者也需要他人的智慧',
			'在竞争之外发展合作思维，共赢比零和更具持久价值'
		],
		careers: ['销售经理', '企业高管', '律师', '创业者', '项目经理', '市场营销总监', '政治家', '投资银行家']
	},
	C: {
		code: 'C', name: '常规型', en: 'Conventional', icon: '📋',
		color: '#5896b4', colorDark: '#467d98', glowColor: 'rgba(88,150,180,0.35)',
		tagBg: 'rgba(88,150,180,0.06)', tagBorder: 'rgba(88,150,180,0.14)',
		desc: '你注重秩序与规范，善于在规则和体系中高效运作。你做事有条不紊、严谨细致，数据的准确性对你至关重要。稳定、可靠是他人对你的最高评价。',
		traits: ['严谨细致', '条理清晰', '遵守规则', '数据处理力强', '可靠性高', '执行力强'],
		advices: [
			'在遵循规则的同时，适度培养创新思维',
			'学会应对变化和不确定性，灵活调整计划也是一种能力',
			'不要因追求完美细节而延误整体进度',
			'尝试主动承担更多决策角色，而不仅仅是执行者'
		],
		careers: ['会计', '行政助理', '图书馆管理员', '审计师', '银行柜员', '档案管理员', '税务专员', '数据录入员']
	}
}

// 类型列表（用于排序）
var TYPE_KEYS = ['R', 'I', 'A', 'S', 'E', 'C']

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
			phase: 'test',
			curQ: 0,
			answers: {},
			questions: QUESTIONS,
			mainType: {},
			radarData: [],
			topTypes: [],
			scores: {},
			careerGroups: []
		}
	},
	computed: {
		progressPct: function() {
			return Math.round(((this.curQ + 1) / this.questions.length) * 100)
		},
		curTypeData: function() {
			if (!this.questions[this.curQ]) return { label: '', bgColor: '', textColor: '', borderColor: '' }
			return TYPE_TAG[this.questions[this.curQ].type] || { label: '', bgColor: '', textColor: '', borderColor: '' }
		},
		progressBarStyle: function() {
			return { width: this.progressPct + '%' }
		},
		heroGlowStyle: function() {
			return { background: 'radial-gradient(circle,' + this.mainType.glowColor + ',transparent 65%)' }
		},
		heroRuleStyle: function() {
			return { background: 'linear-gradient(90deg, transparent,' + this.mainType.color + ',transparent)' }
		},
		labelDotStyle: function() {
			return { background: this.mainType.color, boxShadow: '0 0 10rpx ' + this.mainType.glowColor }
		},
		adviceDotStyle: function() {
			return { background: this.mainType.color, boxShadow: '0 0 8rpx ' + this.mainType.glowColor }
		},
		primaryBtnStyle: function() {
			return { background: 'linear-gradient(148deg,' + this.mainType.color + ',' + this.mainType.colorDark + ')' }
		}
	},
	onLoad: function() {
		var saved = uni.getStorageSync('holland_result')
		if (saved) {
			try {
				var r = JSON.parse(saved)
				if (r.mainType && r.mainType.code) {
					this.mainType = r.mainType
					// Pre-compute styles for items from storage
					var topTypes = r.topTypes || []
					for (var i = 0; i < topTypes.length; i++) {
						var ct = topTypes[i]
						ct.badgeSty = { background: ct.color, boxShadow: '0 4rpx 16rpx ' + ct.glowColor }
					}
					this.topTypes = topTypes
					var radarData = r.radarData || []
					for (var j = 0; j < radarData.length; j++) {
						var item = radarData[j]
						item.barSty = { width: item.pct + '%', background: item.color }
					}
					this.radarData = radarData
					this.scores = r.scores
					this.careerGroups = r.careerGroups
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
			var summary = self.mainType ? (self.mainType.code + '型-' + self.mainType.name) : ''
			var scores = {}
			for (var i = 0; i < TYPE_KEYS.length; i++) scores[TYPE_KEYS[i]] = self.scores ? self.scores[TYPE_KEYS[i]] : 0
			uni.request({
				url: (typeof SHADOW_API_BASE !== 'undefined' ? SHADOW_API_BASE : 'http://43.143.169.226') + '/api/assessments/submit',
				method: 'POST',
				header: { 'Content-Type': 'application/json' },
				data: {
					user_id: uid,
					test_type: 'holland',
					summary: summary,
					result_json: { mainType: self.mainType, radarData: self.radarData, topTypes: self.topTypes, scores: scores, careerGroups: self.careerGroups },
					score_json: scores,
					question_count: 30
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
				// 计算各类型得分
				var scores = {}
				for (var t = 0; t < TYPE_KEYS.length; t++) scores[TYPE_KEYS[t]] = 0

				for (var i = 0; i < self.questions.length; i++) {
					var q = self.questions[i]
					var ans = self.answers[i]
					if (q.reverse) {
						// 反向题：选"否"得1分
						if (ans === 'no') scores[q.type]++
					} else {
						// 正向题：选"是"得1分
						if (ans === 'yes') scores[q.type]++
					}
				}

				self.scores = scores

				// 排序找出前三类型
				var sorted = TYPE_KEYS.slice().sort(function(a, b) { return scores[b] - scores[a] })
				var topKeys = sorted.slice(0, 3)
				var mainKey = sorted[0]
				self.mainType = TYPE_DATA[mainKey]

				// 霍兰德代码组合（预计算完整数据供模板使用）
				var topTypes = []
				for (var ti = 0; ti < topKeys.length; ti++) {
					var tk = topKeys[ti]
					var ttd = TYPE_DATA[tk]
					topTypes.push({
						code: ttd.code,
						name: ttd.name,
						color: ttd.color,
						glowColor: ttd.glowColor,
						score: scores[tk],
						badgeSty: { background: ttd.color, boxShadow: '0 4rpx 16rpx ' + ttd.glowColor }
					})
				}
				self.topTypes = topTypes

				// 雷达图数据
				var totalScore = 0
				for (var s = 0; s < TYPE_KEYS.length; s++) totalScore += scores[TYPE_KEYS[s]]
				var radar = []
				for (var r = 0; r < TYPE_KEYS.length; r++) {
					var key = TYPE_KEYS[r]
					var td = TYPE_DATA[key]
					var pct = totalScore > 0 ? Math.round(scores[key] / totalScore * 100) : 0
					radar.push({
						icon: td.icon,
						code: td.code,
						name: td.name,
						pct: pct,
						color: td.color,
						barSty: { width: pct + '%', background: td.color }
					})
				}
				self.radarData = radar

				// 职业匹配（前3类型，预计算完整数据）
				var careerGroups = []
				for (var c = 0; c < topKeys.length; c++) {
					var ck = topKeys[c]
					var ctd = TYPE_DATA[ck]
					careerGroups.push({
						color: ctd.color,
						code: ctd.code,
						name: ctd.name,
						jobs: ctd.careers
					})
				}
				self.careerGroups = careerGroups

				// 保存结果
				uni.setStorageSync('holland_result', JSON.stringify({
					mainType: self.mainType,
					radarData: self.radarData,
					topTypes: self.topTypes,
					scores: self.scores,
					careerGroups: self.careerGroups
				}))
				self._saveToDb()

				self.phase = 'result'
				uni.hideLoading()
			}, 800)
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
						uni.removeStorageSync('holland_result')
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
	padding-top: env(safe-area-inset-top);
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
.nav-title { font-size: 30rpx; font-weight: 700; color: #322c52; letter-spacing: 4rpx; margin-left: 8rpx; }
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
	background: linear-gradient(90deg, #dda03f, #c08828);
	box-shadow: 0 0 14rpx rgba(221,160,63,0.30);
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
	display: flex; align-items: center; gap: 12rpx;
	margin-bottom: 24rpx;
}
.q-num-label {
	font-size: 24rpx; font-weight: 700;
	color: #dda03f;
	letter-spacing: 3rpx;
	background: rgba(221,160,63,0.08);
	padding: 6rpx 18rpx;
	border-radius: 20rpx;
	border: 1rpx solid rgba(221,160,63,0.15);
}
.q-type-tag {
	font-size: 20rpx; font-weight: 600;
	padding: 4rpx 14rpx;
	border-radius: 16rpx;
	border: 1rpx solid;
	letter-spacing: 2rpx;
}
.q-text {
	font-size: 30rpx;
	color: #2c2450;
	line-height: 1.8;
	letter-spacing: 1rpx;
	margin-bottom: 32rpx;
	font-weight: 500;
}
.q-options {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}
.opt-card {
	display: flex;
	align-items: center;
	padding: 24rpx 20rpx;
	background: rgba(250,248,255,0.60);
	border-radius: 20rpx;
	border: 2rpx solid rgba(210,200,235,0.20);
	transition: all 0.25s ease;
}
.opt-card.opt-selected {
	background: rgba(221,160,63,0.08);
	border-color: rgba(221,160,63,0.35);
	box-shadow: 0 4rpx 16rpx rgba(221,160,63,0.12);
}
.opt-badge {
	width: 52rpx; height: 52rpx;
	border-radius: 50%;
	display: flex; align-items: center; justify-content: center;
	flex-shrink: 0;
	margin-right: 16rpx;
}
.opt-badge-yes {
	background: rgba(72,163,106,0.10);
	border: 1rpx solid rgba(72,163,106,0.20);
}
.opt-badge-no {
	background: rgba(212,96,122,0.10);
	border: 1rpx solid rgba(212,96,122,0.20);
}
.opt-badge-text {
	font-size: 22rpx; font-weight: 700;
}
.opt-badge-yes .opt-badge-text { color: #48a36a; }
.opt-badge-no .opt-badge-text { color: #d4607a; }
.opt-selected .opt-badge-yes {
	background: rgba(72,163,106,0.20);
	border-color: rgba(72,163,106,0.40);
}
.opt-selected .opt-badge-no {
	background: rgba(212,96,122,0.20);
	border-color: rgba(212,96,122,0.40);
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
	background: linear-gradient(148deg, #dda03f 0%, #c08828 52%, #a87820 100%) !important;
	box-shadow: 0 8rpx 28rpx rgba(221,160,63,0.30);
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
	top: -80rpx; left: 50%;
	transform: translateX(-50%);
	pointer-events: none;
}
.hero-icon { font-size: 72rpx; margin-bottom: 16rpx; position: relative; z-index: 2; }
.hero-code {
	font-size: 22rpx; font-weight: 600;
	letter-spacing: 4rpx; margin-bottom: 8rpx;
	padding: 4rpx 20rpx; border-radius: 20rpx;
	position: relative; z-index: 2;
}
.hero-name {
	font-size: 40rpx; font-weight: 700;
	color: #2c2450; letter-spacing: 6rpx;
	margin-bottom: 6rpx;
	position: relative; z-index: 2;
}
.hero-en {
	font-size: 20rpx; letter-spacing: 4rpx; font-style: italic; font-weight: 300;
	margin-bottom: 24rpx;
	position: relative; z-index: 2;
}
.hero-rule {
	width: 60rpx; height: 1.5rpx;
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

/* 霍兰德代码 */
.code-row {
	display: flex;
	justify-content: space-around;
	padding: 8rpx 0;
}
.code-item {
	display: flex; flex-direction: column; align-items: center; gap: 8rpx;
}
.code-badge {
	width: 72rpx; height: 72rpx;
	border-radius: 50%;
	display: flex; align-items: center; justify-content: center;
}
.code-badge-text {
	font-size: 30rpx; font-weight: 800; color: #fff;
	letter-spacing: 2rpx;
}
.code-name { font-size: 22rpx; color: #48407a; font-weight: 500; letter-spacing: 1rpx; }
.code-score { font-size: 20rpx; color: rgba(130,118,186,0.60); font-weight: 600; }

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

/* 性格特质标签 */
.trait-tags {
	display: flex; flex-wrap: wrap; gap: 12rpx;
}
.trait-tag {
	padding: 10rpx 22rpx;
	border-radius: 24rpx;
	border: 1rpx solid;
}
.tag-text { font-size: 24rpx; font-weight: 500; letter-spacing: 1rpx; }

/* 职业匹配 */
.career-list {
	display: flex; flex-direction: column; gap: 20rpx;
}
.career-group {
	padding: 20rpx;
	background: rgba(250,248,255,0.60);
	border-radius: 16rpx;
	border: 1rpx solid rgba(210,200,235,0.12);
}
.career-header {
	display: flex; align-items: center; gap: 10rpx;
	margin-bottom: 12rpx;
}
.career-dot {
	width: 10rpx; height: 10rpx; border-radius: 50%;
	flex-shrink: 0;
}
.career-type-name {
	font-size: 24rpx; font-weight: 600; color: #3c3268;
	letter-spacing: 1rpx;
}
.career-tags {
	display: flex; flex-wrap: wrap; gap: 10rpx;
}
.career-tag {
	padding: 6rpx 16rpx;
	background: rgba(157,114,255,0.06);
	border-radius: 16rpx;
	border: 1rpx solid rgba(157,114,255,0.10);
}
.career-tag-text { font-size: 22rpx; color: #6d5e9a; letter-spacing: 1rpx; }

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
.btn-text-secondary { letter-spacing: 2rpx; }
</style>
