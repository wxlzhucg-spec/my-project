-- =============================================================================
-- 已有库升级：为 tarot_draws 增加「咨询意图 + 牌索引 + JSON 快照」
-- 在备份后于目标库执行；若某列已存在会报错，跳过该行或手工调整。
-- MySQL < 5.7 无 JSON 类型：将下方 cards_json 改为 TEXT。
-- =============================================================================

USE xintujie;

ALTER TABLE tarot_draws
    ADD COLUMN theme_tag_id VARCHAR(32) NULL DEFAULT NULL COMMENT '预设主题 ID' AFTER user_id,
    ADD COLUMN theme_tag_label VARCHAR(64) NULL DEFAULT NULL COMMENT '预设主题文案' AFTER theme_tag_id,
    ADD COLUMN question_text VARCHAR(512) NOT NULL DEFAULT '' COMMENT '自定义咨询问题' AFTER theme_tag_label,
    ADD COLUMN card1_idx TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第1张 阿尔卡那索引0-21' AFTER question_text,
    ADD COLUMN card2_idx TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第2张索引' AFTER card1_idx,
    ADD COLUMN card3_idx TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第3张索引' AFTER card2_idx,
    ADD COLUMN cards_json JSON NULL COMMENT '三张牌 JSON 快照' AFTER created_at;

-- 若旧表 card*_name 为 VARCHAR(16)，可酌情放宽（按需取消注释执行）
-- ALTER TABLE tarot_draws
--     MODIFY COLUMN card1_name VARCHAR(24) NOT NULL DEFAULT '',
--     MODIFY COLUMN card1_num  VARCHAR(16) NOT NULL DEFAULT '',
--     MODIFY COLUMN card2_name VARCHAR(24) NOT NULL DEFAULT '',
--     MODIFY COLUMN card2_num  VARCHAR(16) NOT NULL DEFAULT '',
--     MODIFY COLUMN card3_name VARCHAR(24) NOT NULL DEFAULT '',
--     MODIFY COLUMN card3_num  VARCHAR(16) NOT NULL DEFAULT '';

-- 可选：按用户+时间拉流水（若已存在同名索引请删除本行）
-- ALTER TABLE tarot_draws ADD KEY idx_user_created (user_id, created_at);
