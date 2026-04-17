'use strict'

require('dotenv').config()
const crypto = require('crypto')
const express = require('express')
const cors = require('cors')
const mysql = require('mysql2/promise')

const app = express()
const PORT = Number(process.env.PORT || 3000)

app.use(cors())
app.use(express.json({ limit: '64kb' }))

function hashPasswordPlain(plain) {
	var salt = crypto.randomBytes(16).toString('hex')
	var hash = crypto.pbkdf2Sync(plain, salt, 310000, 32, 'sha256').toString('hex')
	return 'pbkdf2-sha256$310000$' + salt + '$' + hash
}

const pool = mysql.createPool({
	host: process.env.DB_HOST || '127.0.0.1',
	port: Number(process.env.DB_PORT || 3306),
	user: process.env.DB_USER || 'root',
	password: process.env.DB_PASSWORD || '',
	database: process.env.DB_NAME || 'xintujie',
	waitForConnections: true,
	connectionLimit: 10
})

/** 与小程序注册页一致：POST /register */
app.post('/register', async function(req, res) {
	var body = req.body || {}
	var phone = String(body.phone || '').trim()
	var password = String(body.password || '')
	var nickname = String(body.nickname || '').trim()
	if (!/^1\d{10}$/.test(phone)) {
		return res.status(200).json({ code: 400, message: '手机号格式错误' })
	}
	if (password.length < 6) {
		return res.status(200).json({ code: 400, message: '密码至少6位' })
	}
	if (!nickname) nickname = '用户' + phone.slice(-4)
	nickname = nickname.slice(0, 32)
	var openId = 'p_' + phone
	var pwdHash = hashPasswordPlain(password)
	try {
		var [r] = await pool.execute(
			'INSERT INTO users (open_id, phone, password_hash, nickname, terms_agreed_at, profile_completed) VALUES (?, ?, ?, ?, NOW(), 0)',
			[openId, phone, pwdHash, nickname]
		)
		return res.status(200).json({ code: 0, message: 'ok', user_id: r.insertId, openid: openId })
	} catch (e) {
		if (e.code === 'ER_DUP_ENTRY') {
			return res.status(200).json({ code: 400, message: '手机号已注册' })
		}
		console.error(e)
		return res.status(200).json({ code: 500, message: e.message || '服务器错误' })
	}
})

app.get('/api/health', async function(req, res) {
	try {
		await pool.query('SELECT 1')
		res.json({ ok: true, db: true })
	} catch (e) {
		res.status(500).json({ ok: false, db: false, message: e.message })
	}
})

app.post('/api/emotion-records', async function(req, res) {
	var body = req.body || {}
	var uid = Number(body.user_id)
	var emo = Math.round(Number(body.emotion_score))
	var vit = Math.round(Number(body.vitality_score))
	var note = body.note

	if (!Number.isInteger(uid) || uid <= 0) {
		return res.status(400).json({ error: 'invalid user_id' })
	}
	if (emo < 0 || emo > 100 || vit < 0 || vit > 100) {
		return res.status(400).json({ error: 'scores must be 0-100' })
	}
	var noteStr = note == null || note === '' ? null : String(note).slice(0, 65535)

	try {
		var [r] = await pool.execute(
			'INSERT INTO emotion_records (user_id, emotion_score, vitality_score, note) VALUES (?, ?, ?, ?)',
			[uid, emo, vit, noteStr]
		)
		res.json({ ok: true, id: r.insertId })
	} catch (e) {
		console.error(e)
		res.status(500).json({ error: 'db_error', message: e.message })
	}
})

app.listen(PORT, '0.0.0.0', function() {
	console.log('xinyu api listening on http://0.0.0.0:' + PORT)
})
