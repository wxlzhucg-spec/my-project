-- 已有 users 表时按需逐条执行；某列已存在则跳过该条
USE xintujie;

ALTER TABLE users MODIFY COLUMN open_id VARCHAR(128) DEFAULT NULL COMMENT '微信 openid';

ALTER TABLE users ADD COLUMN union_id VARCHAR(128) DEFAULT NULL COMMENT '微信 unionid' AFTER open_id;
ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT NULL COMMENT '手机号' AFTER union_id;
ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '' COMMENT '密码哈希' AFTER phone;
ALTER TABLE users ADD COLUMN status TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '1正常 0禁用' AFTER mbti;
ALTER TABLE users ADD COLUMN profile_completed TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '资料是否完善' AFTER status;
ALTER TABLE users ADD COLUMN last_login_at DATETIME DEFAULT NULL COMMENT '最近登录' AFTER profile_completed;

ALTER TABLE users ADD UNIQUE KEY uk_phone (phone);
ALTER TABLE users ADD KEY idx_union_id (union_id);
ALTER TABLE users ADD KEY idx_created (created_at);
