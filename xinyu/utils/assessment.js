/**
 * 心理测评结果 — 提交到数据库 & 从数据库恢复
 * 
 * 所有测评页面统一调用:
 *   submitAssessment(type, summary, resultJson, answers, scores, questionCount)
 *   loadAssessment(type) → { resultJson, answers, scores, summary } | null
 */
import { SHADOW_API_BASE, getApiUserId } from './api.js'

/**
 * 提交测评结果到后端数据库
 * @param {string} testType - mbti/enneagram/holland/mh/depression/intimacy
 * @param {string} summary - 主结果标签，如 "INFP" / "安全型" / "心理健康良好"
 * @param {object} resultJson - 完整结果对象
 * @param {array} [answers] - 原始答案列表
 * @param {object} [scores] - 原始得分
 * @param {number} [questionCount] - 题目数量
 */
export function submitAssessment(testType, summary, resultJson, answers, scores, questionCount) {
	var userId = getApiUserId()
	if (!userId) {
		console.warn('[assessment] 未登录，测评结果仅存本地')
		return Promise.resolve({ local: true })
	}
	var duration = null
	try {
		var start = uni.getStorageSync('assessment_start_' + testType)
		if (start) {
			duration = Math.round((Date.now() - Number(start)) / 1000)
			uni.removeStorageSync('assessment_start_' + testType)
		}
	} catch (e) {}

	return new Promise(function(resolve, reject) {
		uni.request({
			url: SHADOW_API_BASE + '/api/assessments/submit',
			method: 'POST',
			header: { 'Content-Type': 'application/json' },
			data: {
				user_id: userId,
				test_type: testType,
				summary: summary || '',
				result_json: resultJson,
				answers_json: answers || null,
				score_json: scores || null,
				question_count: questionCount || 0,
				duration_sec: duration
			},
			success: function(res) {
				if (res.statusCode >= 200 && res.statusCode < 300 && res.data && res.data.code === 0) {
					console.log('[assessment] %s 结果已存库: %s', testType, summary)
					resolve(res.data)
				} else {
					var msg = (res.data && (res.data.msg || res.data.detail)) || '提交失败'
					console.warn('[assessment] 存库失败:', msg)
					resolve({ local: true, error: msg })
				}
			},
			fail: function(err) {
				console.warn('[assessment] 存库请求失败:', err.errMsg || err.message)
				resolve({ local: true, error: err.errMsg || err.message })
			}
		})
	})
}

/**
 * 从后端数据库加载测评结果
 * @param {string} testType
 * @returns {Promise<object|null>} - { result_json, answers_json, score_json, summary, ... } 或 null
 */
export function loadAssessment(testType) {
	var userId = getApiUserId()
	if (!userId) return Promise.resolve(null)

	return new Promise(function(resolve) {
		uni.request({
			url: SHADOW_API_BASE + '/api/assessments/query',
			method: 'GET',
			data: { user_id: userId, test_type: testType },
			success: function(res) {
				if (res.statusCode >= 200 && res.statusCode < 300 && res.data && res.data.code === 0 && res.data.data) {
					resolve(res.data.data)
				} else {
					resolve(null)
				}
			},
			fail: function() {
				resolve(null)
			}
		})
	})
}

/**
 * 记录测评开始时间（用于计算 duration）
 * @param {string} testType
 */
export function markAssessmentStart(testType) {
	try {
		uni.setStorageSync('assessment_start_' + testType, String(Date.now()))
	} catch (e) {}
}
