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
		<text class="nav-title">MBTI 性格测试</text>
		<text class="nav-en">MYERS-BRIGGS</text>
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
				<text class="q-type-tag" :style="{ background: curDimData.bgColor, color: curDimData.textColor, borderColor: curDimData.borderColor }">{{ curDimData.label }}</text>
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
				<text class="hero-icon">{{ resultData.icon }}</text>
				<text class="hero-code" :style="{ color: resultData.color }">{{ resultData.type }}</text>
				<text class="hero-name">{{ resultData.name }}</text>
				<text class="hero-en">{{ resultData.en }}</text>
				<view class="hero-rule" :style="heroRuleStyle"></view>
				<text class="hero-desc">{{ resultData.desc }}</text>
			</view>

			<!-- 四维倾向 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot" :style="labelDotStyle"></view>
					<text class="label-text">四维倾向</text>
				</view>
				<view class="dim-list">
					<view class="dim-item" v-for="(dm, idx) in dimData" :key="idx">
						<view class="dim-bar-row">
							<text class="dim-letter dim-letter-left" :class="{ 'dim-letter-active': dm.leftActive }">{{ dm.left }}</text>
							<view class="dim-bar-wrap">
								<view class="dim-bar-bg"></view>
								<view class="dim-bar-fill" :style="dm.dimBarSty"></view>
							</view>
							<text class="dim-letter dim-letter-right" :class="{ 'dim-letter-active': !dm.leftActive }">{{ dm.right }}</text>
						</view>
						<view class="dim-labels">
							<text class="dim-label" :class="{ 'dim-label-active': dm.leftActive }">{{ dm.leftName }}</text>
							<text class="dim-label" :class="{ 'dim-label-active': !dm.leftActive }">{{ dm.rightName }}</text>
						</view>
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
					<view class="trait-tag" v-for="(t, idx) in resultData.traits" :key="idx" :style="{ background: resultData.tagBg, borderColor: resultData.tagBorder }">
						<text class="tag-text" :style="{ color: resultData.color }">{{ t }}</text>
					</view>
				</view>
			</view>

			<!-- 认知功能栈 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--purple"></view>
					<text class="label-text">认知功能栈</text>
				</view>
				<view class="func-list">
					<view class="func-item" v-for="(fc, idx) in resultData.functions" :key="idx">
						<view class="func-rank" :class="{ 'func-rank-main': idx === 0 }">
							<text class="func-rank-text">{{ idx + 1 }}</text>
						</view>
						<view class="func-info">
							<text class="func-name">{{ fc.name }}</text>
							<text class="func-desc">{{ fc.desc }}</text>
						</view>
						<view class="func-bar-wrap">
							<view class="func-bar" :style="fc.funcBarSty"></view>
						</view>
					</view>
				</view>
			</view>

			<!-- 职业匹配 -->
			<view class="section-card">
				<view class="card-label">
					<view class="label-dot label-dot--gold"></view>
					<text class="label-text">职业匹配</text>
				</view>
				<view class="career-tags">
					<view class="career-tag" v-for="(job, jidx) in resultData.careers" :key="jidx">
						<text class="career-tag-text">{{ job }}</text>
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
					<view class="advice-item" v-for="(adv, idx) in resultData.advices" :key="idx">
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
					<text class="btn-text btn-text-secondary" :style="{ color: resultData.color }">重新测试</text>
				</view>
			</view>
		</view>
	</scroll-view>
</view>
</template>

<script>
// 28道MBTI精简版测试题
// 每维度7题：E/I(0-6), S/N(7-13), T/F(14-20), J/P(21-27)
// pole: 选"是"时倾向的维度; reverse: 选"否"时倾向该维度
var QUESTIONS = [
	// E/I 维度 (0-6)
	{ text: '在聚会中，我通常会主动与陌生人交谈。', dim: 'EI', pole: 'E' },
	{ text: '独处一段时间后，我会感到无聊和寂寞。', dim: 'EI', pole: 'E' },
	{ text: '我更喜欢和一群朋友一起度过周末，而非独自看书。', dim: 'EI', pole: 'E' },
	{ text: '在团队讨论中，我通常是先发言的那个人。', dim: 'EI', pole: 'E' },
	{ text: '我的精力来源是与他人的互动和交流。', dim: 'EI', pole: 'E' },
	{ text: '我习惯在行动之前先深思熟虑，而不是边做边想。', dim: 'EI', pole: 'I' },
	{ text: '我更倾向于在心里反复思考，而不是立刻说出来。', dim: 'EI', pole: 'I' },
	// S/N 维度 (7-13)
	{ text: '我更关注事物的具体细节，而非背后的意义。', dim: 'SN', pole: 'S' },
	{ text: '我更信任亲身经历和验证过的事实。', dim: 'SN', pole: 'S' },
	{ text: '我做事更倾向于按照已验证的方法，而非尝试新途径。', dim: 'SN', pole: 'S' },
	{ text: '我喜欢用具体的例子来解释事情，而非抽象的概念。', dim: 'SN', pole: 'S' },
	{ text: '我经常思考未来的可能性和事物之间的深层联系。', dim: 'SN', pole: 'N' },
	{ text: '我更被新颖的想法所吸引，而非实用的细节。', dim: 'SN', pole: 'N' },
	{ text: '我喜欢阅读隐喻和象征意义丰富的作品。', dim: 'SN', pole: 'N' },
	// T/F 维度 (14-20)
	{ text: '做决定时，我更看重逻辑分析而非个人感受。', dim: 'TF', pole: 'T' },
	{ text: '我认为坚持原则比照顾情面更重要。', dim: 'TF', pole: 'T' },
	{ text: '我更擅长发现方案中的逻辑漏洞。', dim: 'TF', pole: 'T' },
	{ text: '我更在意事情是否公平，而非是否让人舒服。', dim: 'TF', pole: 'T' },
	{ text: '做决定时，我会优先考虑对他人的影响。', dim: 'TF', pole: 'F' },
	{ text: '我更擅长察觉和体谅他人的情绪变化。', dim: 'TF', pole: 'F' },
	{ text: '和谐的人际关系比赢得争论更重要。', dim: 'TF', pole: 'F' },
	// J/P 维度 (21-27)
	{ text: '我喜欢提前制定计划，并按计划行事。', dim: 'JP', pole: 'J' },
	{ text: '我的桌面和工作空间通常保持整洁有序。', dim: 'JP', pole: 'J' },
	{ text: '我习惯在截止日期之前完成任务。', dim: 'JP', pole: 'J' },
	{ text: '做决定时，我倾向于快速下结论，不喜欢悬而不决。', dim: 'JP', pole: 'J' },
	{ text: '我喜欢保持选择的开放性，不喜欢过早下结论。', dim: 'JP', pole: 'P' },
	{ text: '我更享受即兴发挥，而非按部就班。', dim: 'JP', pole: 'P' },
	{ text: '我觉得计划是用来参考的，随时可以调整。', dim: 'JP', pole: 'P' }
]

// 维度标签数据
var DIM_TAG = {
	EI: { label: '精力方向', bgColor: 'rgba(78,140,200,0.08)', textColor: '#4e8cc8', borderColor: 'rgba(78,140,200,0.18)' },
	SN: { label: '认知方式', bgColor: 'rgba(165,100,210,0.08)', textColor: '#a564d2', borderColor: 'rgba(165,100,210,0.18)' },
	TF: { label: '决策方式', bgColor: 'rgba(72,163,106,0.08)', textColor: '#48a36a', borderColor: 'rgba(72,163,106,0.18)' },
	JP: { label: '生活态度', bgColor: 'rgba(221,160,63,0.08)', textColor: '#dda03f', borderColor: 'rgba(221,160,63,0.18)' }
}

// 16种MBTI类型数据
var MBTI_DATA = {
	INTJ: {
		type: 'INTJ', name: '策略家', en: 'The Architect', icon: '🏰',
		color: '#6c5ce7', colorDark: '#5a4bd6', heroGlow: 'rgba(108,92,231,0.30)',
		tagBg: 'rgba(108,92,231,0.06)', tagBorder: 'rgba(108,92,231,0.14)',
		desc: '你拥有独立的战略思维和远见卓识，擅长将创新构想转化为可执行的系统方案。你对知识有强烈的渴望，持续追求自我提升，相信一切事物都可以被优化和改进。',
		traits: ['战略远见', '独立思考', '追求卓越', '逻辑严密', '目标坚定', '高度自律'],
		functions: [
			{ name: 'Ni 内倾直觉', desc: '洞察本质与未来趋势', pct: 95 },
			{ name: 'Te 外倾思维', desc: '高效组织与执行决策', pct: 80 },
			{ name: 'Fi 内倾情感', desc: '坚守内在价值与信念', pct: 55 },
			{ name: 'Se 外倾感觉', desc: '感知当下的现实细节', pct: 30 }
		],
		careers: ['战略顾问', '科学家', '软件架构师', '投资分析师', '大学教授', '系统工程师'],
		advices: ['学会欣赏他人的情感需求，逻辑不是唯一的答案', '对"足够好"保持接纳，不必凡事追求完美方案', '偶尔放下长远规划，享受当下的体验', '向值得信任的人敞开心扉，独立不意味着孤岛']
	},
	INTP: {
		type: 'INTP', name: '逻辑学家', en: 'The Logician', icon: '🔬',
		color: '#4e8cc8', colorDark: '#3e72a8', heroGlow: 'rgba(78,140,200,0.30)',
		tagBg: 'rgba(78,140,200,0.06)', tagBorder: 'rgba(78,140,200,0.14)',
		desc: '你热衷于探索逻辑与知识的边界，擅长从复杂信息中发现规律和矛盾。你的思维灵活而深邃，总是在追问"为什么"和"如果怎样"，对真理有近乎执念的追求。',
		traits: ['逻辑分析', '求知欲强', '思维灵活', '独立自主', '客观理性', '创新求变'],
		functions: [
			{ name: 'Ti 内倾思维', desc: '深层逻辑分析与建构', pct: 95 },
			{ name: 'Ne 外倾直觉', desc: '发散联想与可能性探索', pct: 80 },
			{ name: 'Si 内倾感觉', desc: '积累经验与内部参照', pct: 50 },
			{ name: 'Fe 外倾情感', desc: '感知与回应他人情感', pct: 25 }
		],
		careers: ['程序员', '数学家', '哲学研究者', '数据科学家', '理论物理学家', '语言学研究者'],
		advices: ['将思考转化为行动，避免陷入"分析瘫痪"', '学会表达自己的情感，内心世界不需要独自承受', '在追求真理的同时，关注知识的社会应用价值', '建立稳定的日常节奏，减少对灵感的过度依赖']
	},
	ENTJ: {
		type: 'ENTJ', name: '指挥官', en: 'The Commander', icon: '⚔️',
		color: '#c44d4d', colorDark: '#a84040', heroGlow: 'rgba(196,77,77,0.30)',
		tagBg: 'rgba(196,77,77,0.06)', tagBorder: 'rgba(196,77,77,0.14)',
		desc: '你天生具有领导力和决断力，善于制定战略并带领团队高效执行。你目标明确、意志坚定，相信效率和质量是可以兼得的，挑战只会让你更加兴奋。',
		traits: ['领导力强', '目标导向', '果断决策', '效率至上', '战略思维', '追求卓越'],
		functions: [
			{ name: 'Te 外倾思维', desc: '高效组织与系统执行', pct: 95 },
			{ name: 'Ni 内倾直觉', desc: '预见趋势与长远规划', pct: 80 },
			{ name: 'Se 外倾感觉', desc: '敏锐感知现实环境', pct: 55 },
			{ name: 'Fi 内倾情感', desc: '内在价值与情感深度', pct: 30 }
		],
		careers: ['企业高管', '创业者', '律师', '管理咨询师', '项目经理', '政治家'],
		advices: ['在追求效率的同时，关注团队成员的感受与需求', '学会放权和信任他人，领导不是控制', '偶尔允许计划外的惊喜，灵活也是一种力量', '关注内心感受，强大不意味着忽视柔软']
	},
	ENTP: {
		type: 'ENTP', name: '辩论家', en: 'The Debater', icon: '💡',
		color: '#dda03f', colorDark: '#c08828', heroGlow: 'rgba(221,160,63,0.30)',
		tagBg: 'rgba(221,160,63,0.06)', tagBorder: 'rgba(221,160,63,0.14)',
		desc: '你充满创造力和好奇心，享受从不同角度审视问题、挑战常规的过程。你机智灵活，善于发现他人忽略的可能性，在辩论和头脑风暴中如鱼得水。',
		traits: ['思维敏捷', '创新求变', '善于辩论', '好奇心强', '适应力强', '挑战权威'],
		functions: [
			{ name: 'Ne 外倾直觉', desc: '发散联想与可能探索', pct: 95 },
			{ name: 'Ti 内倾思维', desc: '深层逻辑分析与建构', pct: 80 },
			{ name: 'Fe 外倾情感', desc: '感知与调动社交氛围', pct: 55 },
			{ name: 'Si 内倾感觉', desc: '经验积累与细节关注', pct: 30 }
		],
		careers: ['创业者', '产品经理', '营销策划', '记者', '咨询师', '发明家'],
		advices: ['将创意落地为行动，想法只有执行才有价值', '学会倾听而非总是反驳，理解也是一种智慧', '专注于完成一件事，而非同时启动十个', '在挑战他人观点时，也试着理解对方的立场']
	},
	INFJ: {
		type: 'INFJ', name: '提倡者', en: 'The Advocate', icon: '🌙',
		color: '#a564d2', colorDark: '#8e50b8', heroGlow: 'rgba(165,100,210,0.30)',
		tagBg: 'rgba(165,100,210,0.06)', tagBorder: 'rgba(165,100,210,0.14)',
		desc: '你拥有深刻的洞察力和理想主义精神，能够看见事物更深层的意义和联系。你温和而坚定，在内心深处怀有改变世界的使命感，用行动诠释什么是"安静的力量"。',
		traits: ['洞察深刻', '理想主义', '富有同理心', '使命感强', '温和坚定', '追求意义'],
		functions: [
			{ name: 'Ni 内倾直觉', desc: '洞察本质与预见未来', pct: 95 },
			{ name: 'Fe 外倾情感', desc: '共情他人与和谐互动', pct: 80 },
			{ name: 'Ti 内倾思维', desc: '内部逻辑与系统思考', pct: 55 },
			{ name: 'Se 外倾感觉', desc: '感知当下的现实细节', pct: 30 }
		],
		careers: ['心理咨询师', '作家', '非营利组织管理者', '人力资源专家', '教师', '艺术治疗师'],
		advices: ['不要为他人的期待过度消耗自己，你的能量是有限的', '学会拒绝，设立健康的界限是一种自爱', '接受现实的不完美，理想是用来指引方向而非苛责当下', '允许自己享受感官的快乐，不必为每一个行为赋予深层意义']
	},
	INFP: {
		type: 'INFP', name: '调停者', en: 'The Mediator', icon: '🦋',
		color: '#d4607a', colorDark: '#b84e66', heroGlow: 'rgba(212,96,122,0.30)',
		tagBg: 'rgba(212,96,122,0.06)', tagBorder: 'rgba(212,96,122,0.14)',
		desc: '你拥有丰富的内心世界和强烈的价值观，追求真实与意义。你温柔敏感，善于理解他人的感受，在创意表达和帮助他人的过程中找到生命的价值。',
		traits: ['内心丰富', '价值驱动', '共情力强', '创意表达', '追求真实', '理想主义'],
		functions: [
			{ name: 'Fi 内倾情感', desc: '坚守内在价值与真实', pct: 95 },
			{ name: 'Ne 外倾直觉', desc: '发散联想与可能探索', pct: 80 },
			{ name: 'Si 内倾感觉', desc: '珍视记忆与经验参照', pct: 55 },
			{ name: 'Te 外倾思维', desc: '组织执行与目标达成', pct: 30 }
		],
		careers: ['作家', '心理咨询师', '社工', '平面设计师', '音乐人', '人文学科研究者'],
		advices: ['将理想转化为具体行动，梦想需要落地', '不要过度内耗，学会将情感转化为创造', '接受世界的复杂性，真实不总是美好的但值得面对', '在付出中保留自我，你的价值不取决于他人的认可']
	},
	ENFJ: {
		type: 'ENFJ', name: '主人公', en: 'The Protagonist', icon: '🌟',
		color: '#e88555', colorDark: '#c87040', heroGlow: 'rgba(232,133,85,0.30)',
		tagBg: 'rgba(232,133,85,0.06)', tagBorder: 'rgba(232,133,85,0.14)',
		desc: '你天生具有感染力和领导力，善于激励他人实现潜能。你热情、有担当，总是把团队和他人放在心上，相信每个人都有成长的可能，而你就是那个点亮他人的人。',
		traits: ['感染力强', '善于激励', '责任感重', '洞察人心', '组织能力', '乐于奉献'],
		functions: [
			{ name: 'Fe 外倾情感', desc: '共情与协调人际和谐', pct: 95 },
			{ name: 'Ni 内倾直觉', desc: '洞察未来与深层意义', pct: 80 },
			{ name: 'Se 外倾感觉', desc: '感知当下与即时行动', pct: 55 },
			{ name: 'Ti 内倾思维', desc: '内部分析与逻辑校验', pct: 30 }
		],
		careers: ['教师', '人力资源总监', '培训师', '心理咨询师', '公关经理', '社区领袖'],
		advices: ['关注自己的需求，助人也需要自我充电', '学会接受他人的拒绝，不是每个人都需要被拯救', '在做决定时平衡情感与逻辑', '不要因追求和谐而回避必要的冲突']
	},
	ENFP: {
		type: 'ENFP', name: '竞选者', en: 'The Campaigner', icon: '🌈',
		color: '#48a36a', colorDark: '#3a8a58', heroGlow: 'rgba(72,163,106,0.30)',
		tagBg: 'rgba(72,163,106,0.06)', tagBorder: 'rgba(72,163,106,0.14)',
		desc: '你充满热情和创造力，对生活和人际关系有着不竭的好奇心。你善于发现可能性、连接人与人，用你的热情和创意为世界带来色彩，相信生活应该充满意义和乐趣。',
		traits: ['热情洋溢', '创造力强', '善于社交', '好奇心旺盛', '适应力强', '感染力强'],
		functions: [
			{ name: 'Ne 外倾直觉', desc: '发散联想与可能性探索', pct: 95 },
			{ name: 'Fi 内倾情感', desc: '坚守内在价值与真实', pct: 80 },
			{ name: 'Te 外倾思维', desc: '组织执行与目标达成', pct: 55 },
			{ name: 'Si 内倾感觉', desc: '经验积累与细节关注', pct: 30 }
		],
		careers: ['创意总监', '记者', '心理咨询师', '演员', '创业者', '公关专员'],
		advices: ['专注完成一件事，而非同时追逐十个想法', '学会面对无聊和困难，成长需要坚持', '在热情之外建立执行纪律，让创意落地', '不要因害怕冲突而回避深度沟通']
	},
	ISTJ: {
		type: 'ISTJ', name: '物流师', en: 'The Logistician', icon: '📋',
		color: '#5896b4', colorDark: '#467d98', heroGlow: 'rgba(88,150,180,0.30)',
		tagBg: 'rgba(88,150,180,0.06)', tagBorder: 'rgba(88,150,180,0.14)',
		desc: '你是最可靠的存在，以责任和秩序为核心价值。你做事有条不紊、严谨细致，用事实和经验来指导行动，是团队中稳定的基石和值得信赖的执行者。',
		traits: ['严谨负责', '条理清晰', '忠诚可靠', '注重事实', '执行力强', '遵守规则'],
		functions: [
			{ name: 'Si 内倾感觉', desc: '经验参照与细节记忆', pct: 95 },
			{ name: 'Te 外倾思维', desc: '高效组织与系统执行', pct: 80 },
			{ name: 'Fi 内倾情感', desc: '坚守内在价值与忠诚', pct: 55 },
			{ name: 'Ne 外倾直觉', desc: '可能性探索与联想', pct: 30 }
		],
		careers: ['会计师', '审计师', '法官', '项目经理', '系统管理员', '军官'],
		advices: ['在遵循规则的同时，尝试接纳新的方法与思路', '学会应对变化和不确定性，灵活不是混乱', '关注他人的情感需求，效率之外还有温度', '偶尔放下责任的重担，允许自己享受放松']
	},
	ISFJ: {
		type: 'ISFJ', name: '守卫者', en: 'The Defender', icon: '🛡️',
		color: '#5ca8b8', colorDark: '#4a8e9c', heroGlow: 'rgba(92,168,184,0.30)',
		tagBg: 'rgba(92,168,184,0.06)', tagBorder: 'rgba(92,168,184,0.14)',
		desc: '你温暖而忠诚，总是默默守护着身边的人。你细心周到、责任感强，善于记住他人的需要和偏好，用实际行动表达关心，是朋友和团队最可靠的依靠。',
		traits: ['温暖忠诚', '细心周到', '责任感强', '乐于助人', '谦逊可靠', '注重细节'],
		functions: [
			{ name: 'Si 内倾感觉', desc: '珍视记忆与细节关注', pct: 95 },
			{ name: 'Fe 外倾情感', desc: '共情他人与和谐维护', pct: 80 },
			{ name: 'Ti 内倾思维', desc: '内部分析与逻辑校验', pct: 55 },
			{ name: 'Ne 外倾直觉', desc: '可能性探索与联想', pct: 30 }
		],
		careers: ['护士', '行政助理', '小学教师', '社工', '图书管理员', '室内设计师'],
		advices: ['学会表达自己的需求，付出不应是单向的', '不要因害怕冲突而压抑自己的感受', '接纳变化，不是所有事情都能提前规划', '为自己留出时间，你同样值得被照顾']
	},
	ESTJ: {
		type: 'ESTJ', name: '总经理', en: 'The Executive', icon: '🏛️',
		color: '#8b6e4e', colorDark: '#725a3e', heroGlow: 'rgba(139,110,78,0.30)',
		tagBg: 'rgba(139,110,78,0.06)', tagBorder: 'rgba(139,110,78,0.14)',
		desc: '你坚定果断、重视秩序和传统，善于将愿景转化为可执行的计划。你组织能力强、标准明确，相信纪律和努力是成功的基石，是团队中值得信赖的中流砥柱。',
		traits: ['果断坚定', '组织力强', '标准明确', '重视传统', '执行力强', '以身作则'],
		functions: [
			{ name: 'Te 外倾思维', desc: '高效组织与系统执行', pct: 95 },
			{ name: 'Si 内倾感觉', desc: '经验参照与流程优化', pct: 80 },
			{ name: 'Ne 外倾直觉', desc: '可能性探索与联想', pct: 55 },
			{ name: 'Fi 内倾情感', desc: '内在价值与情感深度', pct: 30 }
		],
		careers: ['企业高管', '项目经理', '法官', '财务总监', '军官', '学校管理者'],
		advices: ['在坚持标准的同时，学会倾听不同的声音', '关注他人的感受，高效不意味着忽略人情', '适度放权，信任他人的能力', '接受"足够好"而非苛求完美执行']
	},
	ESFJ: {
		type: 'ESFJ', name: '执政官', en: 'The Consul', icon: '🤝',
		color: '#d4607a', colorDark: '#b84e66', heroGlow: 'rgba(212,96,122,0.30)',
		tagBg: 'rgba(212,96,122,0.06)', tagBorder: 'rgba(212,96,122,0.14)',
		desc: '你热心肠、善于照顾他人，是团队中的粘合剂和温暖的源泉。你重视和谐与归属感，总是第一个伸出援手的人，用真诚和关怀让身边的每个人都感到被重视。',
		traits: ['热心助人', '善于社交', '责任感强', '重视和谐', '注重细节', '忠诚可靠'],
		functions: [
			{ name: 'Fe 外倾情感', desc: '共情协调与社交驱动', pct: 95 },
			{ name: 'Si 内倾感觉', desc: '珍视传统与细节记忆', pct: 80 },
			{ name: 'Ne 外倾直觉', desc: '可能性探索与联想', pct: 55 },
			{ name: 'Ti 内倾思维', desc: '内部分析与逻辑校验', pct: 30 }
		],
		careers: ['人力资源经理', '护士', '教师', '销售经理', '活动策划', '客户关系经理'],
		advices: ['不要因过度迎合他人而忽略自己的需求', '学会接受批评，它不是对你个人的否定', '在维护和谐的同时，允许必要的坦诚和冲突', '关注事情的本质而非表面的人情']
	},
	ISTP: {
		type: 'ISTP', name: '鉴赏家', en: 'The Virtuoso', icon: '🔧',
		color: '#48a36a', colorDark: '#3a8a58', heroGlow: 'rgba(72,163,106,0.30)',
		tagBg: 'rgba(72,163,106,0.06)', tagBorder: 'rgba(72,163,106,0.14)',
		desc: '你冷静灵活、善于在实践中解决问题。你对机械和工具有天生的敏感度，享受用双手探索和创造的过程。你喜欢理解事物的运作原理，并能在危机中保持沉着。',
		traits: ['冷静沉着', '动手能力强', '灵活应变', '独立自主', '逻辑务实', '享受探索'],
		functions: [
			{ name: 'Ti 内倾思维', desc: '深层逻辑分析与建构', pct: 95 },
			{ name: 'Se 外倾感觉', desc: '敏锐感知与即时反应', pct: 80 },
			{ name: 'Ni 内倾直觉', desc: '洞察趋势与深层模式', pct: 55 },
			{ name: 'Fe 外倾情感', desc: '感知与回应他人情感', pct: 30 }
		],
		careers: ['机械工程师', '飞行员', '消防员', '法医', '程序员', '运动员'],
		advices: ['学会表达自己的感受，沉默不等于没有情绪', '在行动之前多一些规划，减少不必要的风险', '对他人多一些耐心，不是所有人都能跟上你的节奏', '在追求自由的同时，建立稳定的人际连接']
	},
	ISFP: {
		type: 'ISFP', name: '探险家', en: 'The Adventurer', icon: '🎨',
		color: '#a564d2', colorDark: '#8e50b8', heroGlow: 'rgba(165,100,210,0.30)',
		tagBg: 'rgba(165,100,210,0.06)', tagBorder: 'rgba(165,100,210,0.14)',
		desc: '你温柔敏感、拥有独特的审美与价值观，用行动和创作表达内心世界。你追求自由和真实，不喜欢被规则束缚，相信每个人都有权利以自己的方式绽放。',
		traits: ['审美敏锐', '温柔敏感', '追求自由', '活在当下', '忠于自我', '行动胜于言辞'],
		functions: [
			{ name: 'Fi 内倾情感', desc: '坚守内在价值与真实', pct: 95 },
			{ name: 'Se 外倾感觉', desc: '感知当下的美好细节', pct: 80 },
			{ name: 'Ni 内倾直觉', desc: '洞察趋势与深层意义', pct: 55 },
			{ name: 'Te 外倾思维', desc: '组织执行与目标达成', pct: 30 }
		],
		careers: ['设计师', '摄影师', '花艺师', '音乐人', '厨师', '兽医'],
		advices: ['为自己的才华设定长期目标，让天赋不只是爱好', '学会面对冲突，回避不能解决问题', '在追求自由的同时，建立一定的生活秩序', '将内心的感受用言语表达，而非仅依赖行动']
	},
	ESTP: {
		type: 'ESTP', name: '企业家', en: 'The Entrepreneur', icon: '⚡',
		color: '#c44d4d', colorDark: '#a84040', heroGlow: 'rgba(196,77,77,0.30)',
		tagBg: 'rgba(196,77,77,0.06)', tagBorder: 'rgba(196,77,77,0.14)',
		desc: '你精力充沛、行动力极强，善于抓住当下的机会。你果断、务实，在高压环境中如鱼得水，相信行动比理论更有说服力，规则是用来被灵活运用的。',
		traits: ['行动力强', '果断务实', '适应力强', '冒险精神', '观察敏锐', '享受当下'],
		functions: [
			{ name: 'Se 外倾感觉', desc: '敏锐感知与即时反应', pct: 95 },
			{ name: 'Ti 内倾思维', desc: '深层逻辑分析与建构', pct: 80 },
			{ name: 'Fe 外倾情感', desc: '感知与调动社交氛围', pct: 55 },
			{ name: 'Ni 内倾直觉', desc: '洞察趋势与深层模式', pct: 30 }
		],
		careers: ['销售总监', '企业家', '运动员', '急救医生', '飞行员', '谈判专家'],
		advices: ['在行动之前多一些思考，避免冲动决策', '关注长远规划，不只活在当下', '学会耐心倾听他人，理解比说服更重要', '控制风险，勇敢不等于鲁莽']
	},
	ESFP: {
		type: 'ESFP', name: '表演者', en: 'The Entertainer', icon: '🎭',
		color: '#e88555', colorDark: '#c87040', heroGlow: 'rgba(232,133,85,0.30)',
		tagBg: 'rgba(232,133,85,0.06)', tagBorder: 'rgba(232,133,85,0.14)',
		desc: '你天生是聚光灯下的明星，用热情和魅力感染身边的每一个人。你热爱生活、享受当下，善于发现日常中的快乐并放大分享，让平凡的日子变得精彩纷呈。',
		traits: ['热情开朗', '感染力强', '活在当下', '善于社交', '乐观积极', '适应力强'],
		functions: [
			{ name: 'Se 外倾感觉', desc: '敏锐感知与享受当下', pct: 95 },
			{ name: 'Fi 内倾情感', desc: '坚守内在价值与真实', pct: 80 },
			{ name: 'Te 外倾思维', desc: '组织执行与目标达成', pct: 55 },
			{ name: 'Ni 内倾直觉', desc: '洞察趋势与深层模式', pct: 30 }
		],
		careers: ['演员', '活动策划', '旅游顾问', '健身教练', '公关专员', '销售代表'],
		advices: ['在享受当下的同时，为未来做些准备', '学会面对无聊和困难，不是所有事都有即时的快乐', '深入完成一件事，而非浅尝辄止', '在社交之外留出独处和反思的空间']
	}
}

var DIM_COLORS = {
	EI: { leftColor: '#4e8cc8', rightColor: '#6c5ce7' },
	SN: { leftColor: '#5896b4', rightColor: '#a564d2' },
	TF: { leftColor: '#48a36a', rightColor: '#d4607a' },
	JP: { leftColor: '#dda03f', rightColor: '#3ec9c1' }
}

var DIM_INFO = {
	EI: { left: 'E', leftName: '外向', right: 'I', rightName: '内向' },
	SN: { left: 'S', leftName: '实感', right: 'N', rightName: '直觉' },
	TF: { left: 'T', leftName: '思维', right: 'F', rightName: '情感' },
	JP: { left: 'J', rightName: '感知', right: 'P', leftName: '判断' }
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
			phase: 'test',
			curQ: 0,
			answers: {},
			questions: QUESTIONS,
			resultData: {},
			dimData: []
		}
	},
	computed: {
		progressPct: function() {
			return Math.round(((this.curQ + 1) / this.questions.length) * 100)
		},
		progressBarStyle: function() {
			return { width: this.progressPct + '%' }
		},
		curDimData: function() {
			if (!this.questions[this.curQ]) return { label: '', bgColor: '', textColor: '', borderColor: '' }
			return DIM_TAG[this.questions[this.curQ].dim] || { label: '', bgColor: '', textColor: '', borderColor: '' }
		},
		heroGlowStyle: function() {
			return { background: 'radial-gradient(circle,' + this.resultData.heroGlow + ',transparent 65%)' }
		},
		heroRuleStyle: function() {
			return { background: 'linear-gradient(90deg, transparent,' + this.resultData.color + ',transparent)' }
		},
		labelDotStyle: function() {
			return { background: this.resultData.color, boxShadow: '0 0 10rpx ' + this.resultData.heroGlow }
		},
		adviceDotStyle: function() {
			return { background: this.resultData.color, boxShadow: '0 0 8rpx ' + this.resultData.heroGlow }
		},
		primaryBtnStyle: function() {
			return { background: 'linear-gradient(148deg,' + this.resultData.color + ',' + this.resultData.colorDark + ')' }
		}
	},
	onLoad: function() {
		var saved = uni.getStorageSync('mbti_result')
		if (saved) {
			try {
				var r = JSON.parse(saved)
				if (r.resultData && r.resultData.type) {
					this.resultData = r.resultData
					this.dimData = r.dimData
					// 确保 dimBarSty 存在（旧缓存可能没有）
					for (var d = 0; d < this.dimData.length; d++) {
						var dm = this.dimData[d]
						if (!dm.dimBarSty) {
							dm.dimBarSty = { left: dm.pct + '%', background: dm.leftActive ? dm.leftColor : dm.rightColor }
						}
					}
					// 确保 funcBarSty 存在
					var funcs = this.resultData.functions || []
					for (var fi = 0; fi < funcs.length; fi++) {
						if (!funcs[fi].funcBarSty) {
							funcs[fi].funcBarSty = {
								width: funcs[fi].pct + '%',
								background: fi === 0 ? this.resultData.color : 'rgba(157,114,255,0.35)'
							}
						}
					}
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
			var summary = self.resultData.type || ''
			uni.request({
				url: (typeof SHADOW_API_BASE !== 'undefined' ? SHADOW_API_BASE : 'http://43.143.169.226') + '/api/assessments/submit',
				method: 'POST',
				header: { 'Content-Type': 'application/json' },
				data: {
					user_id: uid,
					test_type: 'mbti',
					summary: summary,
					result_json: { resultData: self.resultData, dimData: self.dimData },
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
				// 计算各维度得分
				var dimScores = { E: 0, I: 0, S: 0, N: 0, T: 0, F: 0, J: 0, P: 0 }
				for (var i = 0; i < self.questions.length; i++) {
					var q = self.questions[i]
					var ans = self.answers[i]
					if (ans === 'yes') {
						dimScores[q.pole]++
					}
				}
				// 每维度7题，补算对立面
				dimScores.I = 7 - dimScores.E
				dimScores.N = 7 - dimScores.S
				dimScores.F = 7 - dimScores.T
				dimScores.P = 7 - dimScores.J

				// 确定四个字母
				var typeStr = (dimScores.E >= dimScores.I ? 'E' : 'I')
					+ (dimScores.S >= dimScores.N ? 'S' : 'N')
					+ (dimScores.T >= dimScores.F ? 'T' : 'F')
					+ (dimScores.J >= dimScores.P ? 'J' : 'P')

				self.resultData = MBTI_DATA[typeStr]

				// 为 functions 预计算 funcBarSty
				var funcs = self.resultData.functions || []
				for (var fi = 0; fi < funcs.length; fi++) {
					funcs[fi].funcBarSty = {
						width: funcs[fi].pct + '%',
						background: fi === 0 ? self.resultData.color : 'rgba(157,114,255,0.35)'
					}
				}

				// 四维倾向数据
				var dims = ['EI', 'SN', 'TF', 'JP']
				var dimData = []
				for (var d = 0; d < dims.length; d++) {
					var dk = dims[d]
					var di = DIM_INFO[dk]
					var dc = DIM_COLORS[dk]
					var leftScore = dimScores[di.left]
					var rightScore = dimScores[di.right]
					var total = leftScore + rightScore
					var pct = total > 0 ? Math.round(leftScore / total * 100) : 50
					dimData.push({
						left: di.left, right: di.right,
						leftName: di.leftName, rightName: di.rightName,
						leftActive: leftScore >= rightScore,
						pct: pct,
						leftColor: dc.leftColor,
						rightColor: dc.rightColor,
						dimBarSty: { left: pct + '%', background: leftScore >= rightScore ? dc.leftColor : dc.rightColor }
					})
				}
				self.dimData = dimData

				// 保存结果
				uni.setStorageSync('mbti_result', JSON.stringify({
					resultData: self.resultData,
					dimData: self.dimData
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
						uni.removeStorageSync('mbti_result')
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
	display: flex; align-items: center; gap: 12rpx;
	margin-bottom: 24rpx;
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
	background: rgba(157,114,255,0.08);
	border-color: rgba(157,114,255,0.35);
	box-shadow: 0 4rpx 16rpx rgba(157,114,255,0.12);
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
	top: -80rpx; left: 50%;
	transform: translateX(-50%);
	pointer-events: none;
}
.hero-icon { font-size: 72rpx; margin-bottom: 16rpx; position: relative; z-index: 2; }
.hero-code {
	font-size: 36rpx; font-weight: 800;
	letter-spacing: 8rpx;
	position: relative; z-index: 2;
	margin-bottom: 4rpx;
}
.hero-name {
	font-size: 32rpx; font-weight: 700;
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

/* 四维倾向 */
.dim-list {
	display: flex; flex-direction: column; gap: 24rpx;
}
.dim-item {
	padding: 0 8rpx;
}
.dim-bar-row {
	display: flex; align-items: center; gap: 16rpx;
	margin-bottom: 6rpx;
}
.dim-letter {
	font-size: 24rpx; font-weight: 800;
	color: rgba(130,118,186,0.35);
	width: 36rpx; text-align: center;
	letter-spacing: 2rpx;
}
.dim-letter-active {
	color: #2c2450;
}
.dim-bar-wrap {
	flex: 1; height: 12rpx; border-radius: 6rpx;
	background: rgba(210,200,235,0.18);
	position: relative; overflow: hidden;
}
.dim-bar-bg {
	position: absolute; inset: 0;
	background: rgba(210,200,235,0.12);
}
.dim-bar-fill {
	position: absolute;
	width: 12rpx; height: 12rpx;
	border-radius: 50%;
	top: 0;
	transform: translateX(-50%);
	box-shadow: 0 0 12rpx rgba(0,0,0,0.08);
	transition: left 0.6s ease;
}
.dim-labels {
	display: flex; justify-content: space-between;
	padding: 0 4rpx;
}
.dim-label {
	font-size: 20rpx; color: rgba(130,118,186,0.40);
	letter-spacing: 2rpx;
}
.dim-label-active {
	color: #48407a;
	font-weight: 600;
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

/* 认知功能栈 */
.func-list {
	display: flex; flex-direction: column; gap: 16rpx;
}
.func-item {
	display: flex; align-items: center; gap: 14rpx;
}
.func-rank {
	width: 36rpx; height: 36rpx;
	border-radius: 50%;
	background: rgba(210,200,235,0.18);
	display: flex; align-items: center; justify-content: center;
	flex-shrink: 0;
}
.func-rank-main {
	background: rgba(157,114,255,0.15);
}
.func-rank-text {
	font-size: 20rpx; font-weight: 700; color: #7d6bd6;
}
.func-info {
	flex: 1;
	display: flex; flex-direction: column; gap: 2rpx;
}
.func-name { font-size: 24rpx; color: #3c3268; font-weight: 600; letter-spacing: 1rpx; }
.func-desc { font-size: 20rpx; color: rgba(130,118,186,0.60); letter-spacing: 1rpx; }
.func-bar-wrap {
	width: 120rpx; height: 6rpx; border-radius: 3rpx;
	background: rgba(210,200,235,0.18); overflow: hidden;
	flex-shrink: 0;
}
.func-bar {
	height: 100%; border-radius: 3rpx;
	transition: width 0.6s ease;
}

/* 职业匹配 */
.career-tags {
	display: flex; flex-wrap: wrap; gap: 10rpx;
}
.career-tag {
	padding: 8rpx 18rpx;
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
