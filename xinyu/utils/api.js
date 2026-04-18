/**
 * 前端 HTTP 基地址：换环境只改 API_BASE。
 * 正式版小程序需 HTTPS，并在公众平台配置 request 合法域名。
 *
 * 路由（完整 URL = API_BASE + 路径）：
 *   POST   /user/register   → postRegister
 *   POST   /user/login      → postLogin
 *   GET    /user            → getUser（query: id 或 open_id）
 *   PUT    /user/profile    → putUserProfile（body 含 id）
 *   POST   /user/bind_wx    → postBindWx
 *   GET    /emotion         → getEmotionRecords（query: openid, date?）
 *   POST   /emotion         → postEmotionRecord（body: openid, emotion_type, score, note?, date?, vitality?）
 *   DELETE /emotion         → deleteEmotionRecord（query: openid, date）
 *
 * 示例：http://43.143.169.226/user/register
 *
 * 换后端地址：项目根目录建 .env 并写 VUE_APP_XINYU_API_BASE=http://你的主机（勿尾斜杠），重启 dev。
 * 影子 AI 若单独端口（本地 Flask 5001 + Shadow 8000）：VUE_APP_XINYU_SHADOW_API_BASE=http://127.0.0.1:8000
 *
 * H5 本地开发：默认直连后端；仅当设置 XINYU_USE_PROXY=1 时，API_BASE 为空并走 devServer 代理。
 * 小程序：须在微信开发者工具「详情 → 本地设置」勾选「不校验合法域名」；
 * 真机体验版/正式版不能使用裸 IP + HTTP，需在公众平台配置 HTTPS 备案域名。
 */
function _defaultRemoteApiBase() {
	return 'http://43.143.169.226'
}

function _apiBaseFromEnv() {
	var e = ''
	try {
		if (typeof process !== 'undefined' && process.env) {
			e = process.env.VUE_APP_XINYU_API_BASE || process.env.UNI_XINYU_API_BASE || ''
		}
	} catch (err) {}
	if (!e || !String(e).trim()) return null
	return String(e).trim().replace(/\/$/, '')
}

var _envApiBase = _apiBaseFromEnv()
// #ifdef H5
var _apiBase =
	_envApiBase != null
		? _envApiBase
		: process.env.NODE_ENV === 'development' && process.env.XINYU_USE_PROXY === '1'
			? ''
			: _defaultRemoteApiBase()
// #endif
// #ifndef H5
var _apiBase = _envApiBase != null ? _envApiBase : _defaultRemoteApiBase()
// #endif
export const API_BASE = _apiBase

/** 影子 FastAPI 根地址；未配置时与 API_BASE 相同（依赖 Nginx 将 /api/* 转到 8000） */
function _shadowApiBaseFromEnv() {
	var e = ''
	try {
		if (typeof process !== 'undefined' && process.env) {
			e =
				process.env.VUE_APP_XINYU_SHADOW_API_BASE ||
				process.env.UNI_XINYU_SHADOW_API_BASE ||
				''
		}
	} catch (err) {}
	if (!e || !String(e).trim()) return null
	return String(e).trim().replace(/\/$/, '')
}

var _envShadowBase = _shadowApiBaseFromEnv()
export const SHADOW_API_BASE = _envShadowBase != null ? _envShadowBase : API_BASE

export const API = {
	EMOTION: '/emotion',
	USER_REGISTER: '/user/register',
	USER_LOGIN: '/user/login',
	USER: '/user',
	USER_PROFILE: '/user/profile',
	USER_BIND_WX: '/user/bind_wx',
	TAROT_DRAW: '/tarot/draw',
	SHADOW_CHAT: '/api/chat'
}

/** 路径常量（与 API 对象一致，便于页面展示或拼接） */
export const EMOTION_RECORD_PATH = API.EMOTION
export const REGISTER_PATH = API.USER_REGISTER
export const LOGIN_PATH = API.USER_LOGIN
export const USER_PATH = API.USER
export const USER_PROFILE_PATH = API.USER_PROFILE
export const USER_BIND_WX_PATH = API.USER_BIND_WX

/** 拼接完整请求 URL */
export function apiFullUrl(path) {
	var p = path.charAt(0) === '/' ? path : '/' + path
	return API_BASE + p
}

function isBizSuccess(code) {
	return code === 0 || code === 200 || code === '0' || code === '200'
}

function parseBody(d) {
	if (typeof d === 'string') {
		if (d.indexOf('<html') >= 0 || d.indexOf('<!DOCTYPE') >= 0) return { __html: true }
		try {
			return JSON.parse(d)
		} catch (e) {
			return { __raw: d }
		}
	}
	return d
}

/** 将 uni.request fail / 异常转成用户可读的短文案（用于 Toast） */
export function describeRequestError(err) {
	var m = ''
	if (err && typeof err.message === 'string' && err.message) m = err.message
	else if (err && typeof err.errMsg === 'string' && err.errMsg) m = err.errMsg
	if (!m) return '网络异常，请检查网络或服务是否在线'
	if (m.indexOf('url not in domain list') >= 0) {
		return '域名未放行：工具勾选不校验；上架需HTTPS备案域名'
	}
	if (m.indexOf('ssl') >= 0 || m.indexOf('SSL') >= 0 || m.indexOf('certificate') >= 0) {
		return 'HTTPS证书异常，请检查域名与证书配置'
	}
	if (m.indexOf('timeout') >= 0) {
		return '请求超时，请稍后重试'
	}
	if (m.indexOf('CONNECTION_REFUSED') >= 0 || m.indexOf('connection refused') >= 0) {
		return '连接被拒绝，请确认服务已启动且端口开放'
	}
	if (
		m.indexOf('CONNECTION_RESET') >= 0 ||
		m.indexOf('connection reset') >= 0 ||
		m.indexOf('ERR_CONNECTION_RESET') >= 0
	) {
		return '连接被重置：服务器可能未运行、崩溃或防火墙/安全组拦截，请检查 5001 进程与云主机安全组'
	}
	if (m.indexOf('request:fail') >= 0) {
		return '连不上接口：查网络、防火墙、合法域名与API地址'
	}
	return m.length > 22 ? m.slice(0, 20) + '…' : m
}

/**
 * 统一请求；GET 时 data 会作为 query
 */
export function request(options) {
	var method = (options.method || 'GET').toUpperCase()
	var url = API_BASE + options.path
	var header = Object.assign({ 'Content-Type': 'application/json' }, options.header || {})
	return new Promise(function(resolve, reject) {
		uni.request({
			url: url,
			method: method,
			header: header,
			data: options.data,
			timeout: options.timeout || 25000,
			success: function(res) {
				var sc = res.statusCode
				var d = parseBody(res.data)
				if (d && d.__html) {
					reject(new Error('接口返回了网页而非 JSON，请检查 API_BASE 或 H5 代理配置'))
					return
				}
				if (sc < 200 || sc >= 300) {
					var msg = (d && d.message) || ('HTTP ' + sc)
					if (d && d.error) msg = msg + '：' + d.error
					reject(new Error(msg))
					return
				}
				/* 避免 HTTP 200 + 空 body/非 JSON 仍 resolve，出现「前端提示成功但库里没数据」 */
				if (d === undefined || d === null || typeof d !== 'object') {
					reject(new Error('接口返回空或非对象，请确认 URL 是否直连 Flask（未被 nginx 挡掉）'))
					return
				}
				if (Object.prototype.hasOwnProperty.call(d, '__raw')) {
					reject(new Error('接口返回非 JSON'))
					return
				}
				var c = d.code
				if (c === undefined || c === null || !isBizSuccess(c)) {
					reject(new Error(d.msg || d.message || d.error || ('业务失败 code=' + c)))
					return
				}
				if (d.success === false) {
					reject(new Error(d.msg || d.message || '请求失败'))
					return
				}
				resolve(d)
			},
			fail: function(err) {
				var em = (err && err.errMsg) || (err && err.message) || ''
				reject(new Error(em || '网络请求失败'))
			}
		})
	})
}

export function getApiUserId() {
	try {
		var v = uni.getStorageSync('xinyu_user_id')
		if (v !== '' && v != null && !isNaN(Number(v))) return Number(v)
	} catch (e) {}
	return 0
}

export function getApiUserPhone() {
	try {
		var v = uni.getStorageSync('xinyu_user_phone')
		if (v !== '' && v != null) return String(v).trim()
	} catch (e) {}
	return ''
}

export function getApiOpenid() {
	try {
		var v = uni.getStorageSync('xinyu_openid')
		if (v !== '' && v != null) return String(v).trim()
		v = uni.getStorageSync('openid')
		if (v !== '' && v != null) return String(v).trim()
	} catch (e) {}
	return ''
}

/** 登录/注册后写入：user 为接口返回的 data（含 id、open_id） */
export function applyUserSession(user) {
	if (!user || typeof user !== 'object') return
	if (user.id != null && user.id !== '') {
		try {
			uni.setStorageSync('xinyu_user_id', Number(user.id))
		} catch (e) {}
	}
	if (user.phone != null && user.phone !== '') {
		try {
			uni.setStorageSync('xinyu_user_phone', String(user.phone).trim())
		} catch (e0) {}
	}
	var oid = user.open_id != null ? user.open_id : user.openid
	if (oid) {
		oid = String(oid).trim()
		try {
			uni.setStorageSync('xinyu_openid', oid)
			uni.setStorageSync('openid', oid)
		} catch (e) {}
	}
}

/** 将服务端用户字段合并进本地 userProfile，供「我的」等页展示 */
function syncUserProfileFromServer(user) {
	if (!user || typeof user !== 'object') return
	try {
		var existing = {}
		var raw = uni.getStorageSync('userProfile')
		if (raw) {
			try {
				existing = JSON.parse(raw)
			} catch (e0) {}
		}
		var av =
			user.avatar_url != null && String(user.avatar_url).trim() !== ''
				? String(user.avatar_url).trim()
				: existing.avatar || ''
		var nick =
			user.nickname != null && String(user.nickname).trim() !== ''
				? String(user.nickname).trim()
				: existing.nickname || ''
		var mbti =
			user.mbti != null && String(user.mbti).trim() !== '' ? String(user.mbti).trim() : existing.mbti || ''
		uni.setStorageSync(
			'userProfile',
			JSON.stringify(
				Object.assign({}, existing, {
					nickname: nick,
					avatar: av,
					mbti: mbti
				})
			)
		)
	} catch (e1) {}
}

function applyRegisterSession(d) {
	var uid = d.user_id != null ? d.user_id : (d.data && d.data.user_id)
	var oid = d.openid != null ? d.openid : d.open_id
	if (oid == null && d.data) oid = d.data.openid != null ? d.data.openid : d.data.open_id
	if (uid !== undefined && uid !== null && uid !== '') {
		try {
			uni.setStorageSync('xinyu_user_id', Number(uid))
		} catch (e) {}
	}
	if (oid) {
		try {
			uni.setStorageSync('xinyu_openid', String(oid).trim())
			uni.setStorageSync('openid', String(oid).trim())
		} catch (e) {}
	}
}

// ---------- 用户 ----------

/** POST /user/register — 字段与 flask register() 一致，可选项从 payload 原样合并（合法值） */
export function postRegister(payload) {
	var data = {
		phone: String(payload.phone || '').trim(),
		password: String(payload.password || ''),
		nickname: String(payload.nickname || '').trim(),
		terms_agreed: payload.terms_agreed !== false
	}
	var optKeys = [
		'open_id',
		'union_id',
		'avatar_url',
		'gender',
		'birth_date',
		'birth_time',
		'birth_province',
		'birth_city',
		'birth_district',
		'mbti'
	]
	for (var i = 0; i < optKeys.length; i++) {
		var k = optKeys[i]
		var v = payload[k]
		if (v === undefined || v === null) continue
		if (k === 'gender') {
			if (v === 'male' || v === 'female' || v === 'unknown') data.gender = v
			continue
		}
		if (typeof v === 'string') {
			v = v.trim()
			if (v === '') continue
		}
		data[k] = v
	}
	return request({
		path: API.USER_REGISTER,
		method: 'POST',
		data: data
	}).then(function(d) {
		applyRegisterSession(d)
		/* 注册接口不返回 openid 时，用工 p+手机号 作为情绪接口 openid，与未绑微信账号一致 */
		var phoneStr = String(payload.phone || '').trim()
		if (phoneStr) {
			try {
				uni.setStorageSync('xinyu_user_phone', phoneStr)
			} catch (e0) {}
		}
		if (phoneStr && !getApiOpenid()) {
			try {
				var syn = 'p_' + phoneStr
				uni.setStorageSync('xinyu_openid', syn)
				uni.setStorageSync('openid', syn)
			} catch (e1) {}
		}
		return d
	})
}

/** POST /user/login */
export function postLogin(payload) {
	var phone = String(payload.phone || '').trim()
	return request({
		path: API.USER_LOGIN,
		method: 'POST',
		data: {
			phone: phone,
			password: String(payload.password || '')
		}
	}).then(function(d) {
		if (d && d.data) {
			applyUserSession(d.data)
			syncUserProfileFromServer(d.data)
		}
		if (phone) {
			try {
				uni.setStorageSync('xinyu_user_phone', phone)
			} catch (e0) {}
		}
		if (phone && !getApiOpenid()) {
			try {
				var syn2 = 'p_' + phone
				uni.setStorageSync('xinyu_openid', syn2)
				uni.setStorageSync('openid', syn2)
			} catch (e2) {}
		}
		return d
	})
}

/** GET /user?id= 或 GET /user?open_id= */
export function getUser(params) {
	var q = {}
	if (params.id != null) q.id = params.id
	if (params.open_id != null) q.open_id = params.open_id
	if (params.phone != null) q.phone = params.phone
	return request({ path: API.USER, method: 'GET', data: q })
}

/** PUT /user/profile — 自动带上 phone，本地 id 对不上数据库时由后端按 phone 回退 */
export function putUserProfile(payload) {
	var body = Object.assign({}, payload || {})
	var phone = String(body.phone || getApiUserPhone() || '').trim()
	if (phone) body.phone = phone

	function doPut(data) {
		return request({
			path: API.USER_PROFILE,
			method: 'PUT',
			data: data
		}).then(function(res) {
			var newId = res && res.data && res.data.id
			if (newId != null && newId !== '') {
				try {
					uni.setStorageSync('xinyu_user_id', Number(newId))
				} catch (e) {}
			}
			return res
		})
	}

	return doPut(body).catch(function(err) {
		var msg = (err && err.message) || ''
		// 若 id 对不上且本地有 phone，去掉 id 只按 phone 再打一次
		if (msg.indexOf('用户不存在') >= 0 && phone && body.id) {
			var retry = Object.assign({}, body)
			delete retry.id
			return doPut(retry)
		}
		throw err
	})
}

/** POST /user/bind_wx — body: id, open_id, union_id?（与 Flask bind_wx 一致） */
export function postBindWx(payload) {
	return request({
		path: API.USER_BIND_WX,
		method: 'POST',
		data: {
			id: payload.id,
			open_id: String(payload.open_id || '').trim(),
			union_id: payload.union_id != null ? String(payload.union_id).trim() : ''
		}
	})
}

// ---------- 塔罗 ----------

/** POST /tarot/draw — 保存确认的 3 张牌 + 咨询意图 */
export function postTarotDraw(payload) {
	var uid = payload.user_id || getApiUserId()
	if (!uid) return Promise.reject(new Error('未登录，无法保存抽牌'))
	var cards = payload.cards
	if (!cards || !Array.isArray(cards) || cards.length < 3) {
		return Promise.reject(new Error('cards 需为 3 张牌数组'))
	}
	return request({
		path: API.TAROT_DRAW,
		method: 'POST',
		data: {
			user_id: uid,
			theme_tag_id: payload.theme_tag_id || null,
			theme_tag_label: payload.theme_tag_label || null,
			question_text: payload.question_text || '',
			cards: cards,
			draw_date: payload.draw_date || ''
		}
	})
}

/** GET /tarot/draw?user_id= */
export function getTarotDraws(userId) {
	var uid = userId || getApiUserId()
	if (!uid) return Promise.reject(new Error('未登录'))
	return request({ path: API.TAROT_DRAW, method: 'GET', data: { user_id: uid } })
}

// ---------- 情绪 ----------

function emotionTypeFromScore(emo) {
	if (emo < 45) return 1
	if (emo < 70) return 2
	return 3
}

/**
 * POST /emotion：openid, emotion_type, score, note?, date?, vitality?（0-100，与 vitality_score 二选一）
 */
export function postEmotionRecord(payload) {
	var note = payload.note
	if (note == null || note === '') note = ''
	else note = String(note)
	var emo = Math.round(Number(payload.emotion_score))
	var et = payload.emotion_type
	if (et == null || et === '' || isNaN(Number(et))) et = emotionTypeFromScore(emo)
	var openid = String(payload.openid || '').trim()
	if (!openid) return Promise.reject(new Error('缺少openid'))

	var body = {
		openid: openid,
		emotion_type: Number(et),
		score: emo,
		note: note
	}
	if (payload.date) body.date = String(payload.date)
	var vit = payload.vitality != null ? payload.vitality : payload.vitality_score
	if (vit != null && vit !== '' && !isNaN(Number(vit))) {
		var v = Math.round(Number(vit))
		if (v >= 0 && v <= 100) body.vitality = v
	}

	return request({
		path: API.EMOTION,
		method: 'POST',
		data: body
	})
}

/** GET /emotion?openid= [&date=] */
export function getEmotionRecords(openid, date) {
	if (!openid) return Promise.reject(new Error('缺少openid'))
	var data = { openid: openid }
	if (date) data.date = date
	return request({ path: API.EMOTION, method: 'GET', data: data })
}

/** DELETE /emotion?openid=&date=（query 拼在 URL，兼容各端） */
export function deleteEmotionRecord(openid, date) {
	if (!openid || !date) return Promise.reject(new Error('缺少 openid 或 date'))
	var qs =
		'openid=' +
		encodeURIComponent(openid) +
		'&date=' +
		encodeURIComponent(date)
	return request({ path: API.EMOTION + '?' + qs, method: 'DELETE' })
}

// ---------- 影子 AI ----------

/** 将 FastAPI 等返回的 detail 转成可读字符串（detail 常为数组） */
function formatShadowHttpDetail(d) {
	if (!d || typeof d !== 'object') return ''
	var det = d.detail
	if (typeof det === 'string') return det
	if (Array.isArray(det)) {
		var parts = []
		for (var i = 0; i < det.length; i++) {
			var it = det[i]
			if (it && typeof it.msg === 'string') parts.push(it.msg)
			else if (typeof it === 'string') parts.push(it)
		}
		if (parts.length) return parts.join('；')
	}
	if (typeof d.message === 'string') return d.message
	return ''
}

/**
 * POST /api/chat — 影子 AI 情感陪伴对话
 *
 * @param {Object} payload
 * @param {string} [payload.user_id]        - 用户数据库 ID（优先，会员/手机号登录用户用此字段）
 * @param {string} [payload.open_id]       - 微信 open_id（已绑定微信的用户用此字段）
 * @param {string} payload.emotion_keyword - 当前情绪关键词（如：焦虑/迷茫/愤怒）
 * @param {string} payload.question        - 用户倾诉的问题
 * @param {string} [payload.session_id]   - 会话ID（多轮对话保持一致）
 * @param {string} [payload.supplements]   - 第二轮补充回答
 * @returns {Promise<{phase:string, reply:string, session_id?:string, error?:string}>}
 */
export function postShadowChat(payload) {
	var question = String(payload.question || '').trim()
	if (!question) return Promise.reject(new Error('请输入你的问题'))

	var body = {
		emotion_keyword: String(payload.emotion_keyword || '迷茫').trim(),
		question: question
	}
	// 优先传 user_id（手机号登录用户没有真实 open_id）
	var userId = getApiUserId()
	if (userId) body.user_id = userId
	// 仅在存在真实微信 open_id 时才下发；前端注册时写入的 'p_手机号' 伪值不算
	var openid = String(payload.open_id || '').trim()
	if (!openid) openid = getApiOpenid()
	if (openid && openid.indexOf('p_') !== 0 && !userId) body.open_id = openid
	if (payload.session_id) body.session_id = String(payload.session_id)
	if (payload.supplements) body.supplements = String(payload.supplements)

	return new Promise(function(resolve, reject) {
		uni.request({
			url: SHADOW_API_BASE + API.SHADOW_CHAT,
			method: 'POST',
			header: { 'Content-Type': 'application/json' },
			data: JSON.stringify(body),
			timeout: 200000,
			success: function(res) {
				var sc = res.statusCode
				var d = res.data
				if (sc < 200 || sc >= 300) {
					var msg = formatShadowHttpDetail(d) || ('HTTP ' + sc)
					reject(new Error(msg))
					return
				}
				if (d && d.error) {
					reject(new Error(d.error))
					return
				}
				resolve(d)
			},
			fail: function(err) {
				var em = (err && err.errMsg) || (err && err.message) || ''
				if (em.indexOf('timeout') >= 0) {
					reject(new Error('影子思考时间较长，请稍后重试'))
				} else {
					reject(new Error(em || '网络请求失败'))
				}
			}
		})
	})
}
