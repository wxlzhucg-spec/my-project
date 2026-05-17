-- =============================================================
-- 每日个性化运势表 (daily_fortune)
-- 用于存储基于用户星盘+星历+LLM生成的每日运势
-- 
-- 执行方式: Navicat 或 MySQL 客户端整段执行
-- 依赖: users 表（user_id 外键关联）
-- =============================================================

USE xintujie;

CREATE TABLE IF NOT EXISTS daily_fortune (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL COMMENT 'users.id',
    sign            VARCHAR(16)    NOT NULL COMMENT '星座: 白羊座/金牛座/...',
    fortune_date    DATE           NOT NULL COMMENT '运势日期 YYYY-MM-DD',

    status          VARCHAR(128)   NOT NULL DEFAULT '' COMMENT '一句话状态，如"你今天运势开挂啦~~"',
    ratings         JSON           NOT NULL COMMENT '[{label,val}] x4, label=综合|爱情|工作|财富, val=1-5',
    tabs            JSON           NOT NULL COMMENT '[{label,content}] x4, 四维度详细文案',

    natal_summary   TEXT           DEFAULT NULL COMMENT '本命盘摘要(调试用)',
    ephemeris_text  TEXT           DEFAULT NULL COMMENT '当日星历(调试用)',
    raw_response    TEXT           DEFAULT NULL COMMENT 'LLM原始返回(调试用)',

    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_user_date (user_id, fortune_date),
    KEY idx_date (fortune_date),
    KEY idx_sign (sign)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='每日个性化运势 — 基于星盘+星历+LLM生成';
