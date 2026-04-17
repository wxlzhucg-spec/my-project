-- =============================================================================
-- Xinyu / 心途 小程序 — 全量建表（库：xintujie）
-- Navicat：连接后新建查询，整段执行即可。
--
-- 若 emotion_records / users 已存在且结构旧，请先备份数据后 DROP 再执行，
-- 或只复制需要的 CREATE 段单独执行。
-- =============================================================================
--
-- 【users】对应页面与接口
--   注册 pages/register     → phone, password_hash, terms_agreed_at, nickname
--   完善资料 profile-edit  → avatar_url, gender, birth_*, mbti
--   Flask POST /user/register、/user/login、/user/profile、/user/bind_wx
--
-- 【emotion_records】对应 Flask POST/GET/DELETE /emotion
--   字段：openid, date, emotion_type, score, vitality, note
--   同一天同一 openid 重复 POST 为覆盖（依赖 UNIQUE(openid, date)）
--
-- 【tarot_draws】塔罗咨询 + 确认的三张牌（与小程序 tarotIntent、tarotResult 对齐）
--   user_id, theme_tag_id/label, question_text, card1~3_idx/name/num, cards_json, draw_date
-- 【explore_nodes】探索等业务预留
-- =============================================================================

CREATE DATABASE IF NOT EXISTS xintujie
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE xintujie;

-- ---------------------------------------------------------------------------
-- 1. 用户表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID，自增',
    PRIMARY KEY (id),

    phone               VARCHAR(20)   DEFAULT NULL              COMMENT '注册-手机号，唯一',
    password_hash       VARCHAR(255)  NOT NULL DEFAULT ''       COMMENT '注册-密码哈希（禁止明文）',
    terms_agreed_at     DATETIME      DEFAULT NULL               COMMENT '注册-勾选协议时间',

    nickname            VARCHAR(32)   NOT NULL DEFAULT ''       COMMENT '昵称',
    avatar_url          VARCHAR(1024) NOT NULL DEFAULT ''       COMMENT '资料-头像 URL',
    gender              ENUM('male','female','unknown') NOT NULL DEFAULT 'unknown' COMMENT '资料-性别',
    birth_date          DATE          DEFAULT NULL               COMMENT '资料-出生日期',
    birth_time          VARCHAR(8)    NOT NULL DEFAULT ''       COMMENT '资料-出生时刻 HH:MM',
    birth_province      VARCHAR(64)   NOT NULL DEFAULT ''       COMMENT '资料-省',
    birth_city          VARCHAR(64)   NOT NULL DEFAULT ''       COMMENT '资料-市',
    birth_district      VARCHAR(64)   NOT NULL DEFAULT ''       COMMENT '资料-区县',
    mbti                VARCHAR(8)    NOT NULL DEFAULT ''       COMMENT '资料-MBTI',

    open_id             VARCHAR(128)  DEFAULT NULL              COMMENT '微信 openid；手机注册占位可 p_手机号',
    union_id            VARCHAR(128)  DEFAULT NULL              COMMENT '微信 unionid',
    status              TINYINT UNSIGNED NOT NULL DEFAULT 1      COMMENT '1正常 0禁用',
    profile_completed   TINYINT UNSIGNED NOT NULL DEFAULT 0     COMMENT '1 已完善资料',
    last_login_at       DATETIME      DEFAULT NULL               COMMENT '最近登录',

    created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_open_id (open_id),
    UNIQUE KEY uk_phone (phone),
    KEY idx_union_id (union_id),
    KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='用户：注册 + 完善资料';

-- ---------------------------------------------------------------------------
-- 2. 情绪记录表（与 Flask /emotion 一致，与小程序 postEmotionRecord 一致）
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS emotion_records (
    id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    openid         VARCHAR(128)  NOT NULL COMMENT '用户标识，与登录/注册返回的 openid 一致',
    date           DATE          NOT NULL COMMENT '记录归属日 YYYY-MM-DD',
    emotion_type   INT           NOT NULL COMMENT '情绪类型（与前端 emotion_type 一致）',
    score          TINYINT UNSIGNED NOT NULL COMMENT '情绪分 0-100',
    vitality       TINYINT UNSIGNED DEFAULT NULL COMMENT '活力 0-100，可选',
    note           TEXT          COMMENT '备注/纸条',
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_openid_date (openid, date),
    KEY idx_openid (openid),
    KEY idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='情绪记录';

-- ---------------------------------------------------------------------------
-- 3. 塔罗抽牌记录
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tarot_draws (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id             BIGINT UNSIGNED NOT NULL COMMENT 'users.id，登录用户',
    theme_tag_id        VARCHAR(32)   NULL DEFAULT NULL COMMENT '预设主题 ID（如 l1/w1/s2），未选为 NULL',
    theme_tag_label     VARCHAR(64)   NULL DEFAULT NULL COMMENT '预设主题展示文案，冗余便于列表展示',
    question_text       VARCHAR(512)  NOT NULL DEFAULT '' COMMENT '自定义咨询问题；可与主题并存',
    card1_idx           TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第1张：大阿尔卡那索引 0-21，与前端抽牌序一致',
    card1_name          VARCHAR(24)   NOT NULL DEFAULT '' COMMENT '第1张牌名快照',
    card1_num           VARCHAR(16)   NOT NULL DEFAULT '' COMMENT '第1张编号（罗马数字等）',
    card2_idx           TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第2张：索引 0-21',
    card2_name          VARCHAR(24)   NOT NULL DEFAULT '' COMMENT '第2张牌名快照',
    card2_num           VARCHAR(16)   NOT NULL DEFAULT '' COMMENT '第2张编号',
    card3_idx           TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第3张：索引 0-21',
    card3_name          VARCHAR(24)   NOT NULL DEFAULT '' COMMENT '第3张牌名快照',
    card3_num           VARCHAR(16)   NOT NULL DEFAULT '' COMMENT '第3张编号',
    cards_json          JSON          NULL COMMENT '三张牌完整 JSON，结构与本地 Storage tarotResult 数组一致',
    draw_date           DATE          NOT NULL COMMENT '抽牌日历日（业务时区）',
    created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '确认落库时间',
    KEY idx_user_date (user_id, draw_date),
    KEY idx_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='塔罗咨询与确认牌面';

-- ---------------------------------------------------------------------------
-- 4. 探索星图节点
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS explore_nodes (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL COMMENT 'users.id',
    node_id         TINYINT UNSIGNED NOT NULL COMMENT '节点 0-8',
    lit_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '点亮时间',
    UNIQUE KEY uk_user_node (user_id, node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='探索星图节点';
