-- ============================================
-- Xinyu App 数据库初始化脚本
-- ============================================

CREATE DATABASE IF NOT EXISTS xintujie
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE xintujie;

-- 用户表：注册页 + 完善资料页（见 server/create_users_table.sql 字段说明）
CREATE TABLE IF NOT EXISTS users (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID（自增）',
    PRIMARY KEY (id),
    phone               VARCHAR(20)   DEFAULT NULL              COMMENT '注册-手机号',
    password_hash       VARCHAR(255)  NOT NULL DEFAULT ''       COMMENT '注册-密码哈希',
    terms_agreed_at     DATETIME      DEFAULT NULL               COMMENT '注册-同意协议时间',
    nickname            VARCHAR(32)   NOT NULL DEFAULT ''        COMMENT '昵称',
    avatar_url          VARCHAR(1024) NOT NULL DEFAULT ''       COMMENT '资料-头像 URL',
    gender              ENUM('male','female','unknown') NOT NULL DEFAULT 'unknown' COMMENT '资料-性别',
    birth_date          DATE          DEFAULT NULL                COMMENT '资料-出生日期',
    birth_time          VARCHAR(8)    NOT NULL DEFAULT ''        COMMENT '资料-出生时间 HH:MM',
    birth_province      VARCHAR(64)   NOT NULL DEFAULT ''        COMMENT '资料-省',
    birth_city          VARCHAR(64)   NOT NULL DEFAULT ''        COMMENT '资料-市',
    birth_district      VARCHAR(64)   NOT NULL DEFAULT ''        COMMENT '资料-区县',
    mbti                VARCHAR(8)    NOT NULL DEFAULT ''        COMMENT '资料-MBTI',
    open_id             VARCHAR(128)  DEFAULT NULL              COMMENT '微信 openid',
    union_id            VARCHAR(128)  DEFAULT NULL              COMMENT '微信 unionid',
    status              TINYINT UNSIGNED NOT NULL DEFAULT 1      COMMENT '1正常 0禁用',
    profile_completed   TINYINT UNSIGNED NOT NULL DEFAULT 0      COMMENT '资料是否完善',
    last_login_at       DATETIME      DEFAULT NULL               COMMENT '最近登录',
    created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_open_id (open_id),
    UNIQUE KEY uk_phone (phone),
    KEY idx_union_id (union_id),
    KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户：注册+完善资料';

-- 情绪记录表（与 Flask /emotion、小程序 utils/api.js 一致）
CREATE TABLE IF NOT EXISTS emotion_records (
    id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    openid         VARCHAR(128)  NOT NULL COMMENT '用户标识',
    date           DATE          NOT NULL COMMENT '归属日',
    emotion_type   INT           NOT NULL,
    score          TINYINT UNSIGNED NOT NULL COMMENT '情绪分 0-100',
    vitality       TINYINT UNSIGNED DEFAULT NULL COMMENT '活力 0-100',
    note           TEXT,
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_openid_date (openid, date),
    KEY idx_openid (openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情绪记录';

-- 塔罗咨询与确认牌面（与小程序 tarotIntent + tarotResult 对齐）
CREATE TABLE IF NOT EXISTS tarot_draws (
    id                  BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id             BIGINT UNSIGNED NOT NULL COMMENT '用户ID users.id',
    theme_tag_id        VARCHAR(32)   NULL DEFAULT NULL COMMENT '预设主题ID',
    theme_tag_label     VARCHAR(64)   NULL DEFAULT NULL COMMENT '预设主题文案',
    question_text       VARCHAR(512)  NOT NULL DEFAULT '' COMMENT '自定义咨询问题',
    card1_idx           TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第1张 阿尔卡那索引0-21',
    card1_name          VARCHAR(24)   NOT NULL DEFAULT '' COMMENT '第1张牌名',
    card1_num           VARCHAR(16)   NOT NULL DEFAULT '' COMMENT '第1张编号',
    card2_idx           TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第2张索引',
    card2_name          VARCHAR(24)   NOT NULL DEFAULT '' COMMENT '第2张牌名',
    card2_num           VARCHAR(16)   NOT NULL DEFAULT '' COMMENT '第2张编号',
    card3_idx           TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '第3张索引',
    card3_name          VARCHAR(24)   NOT NULL DEFAULT '' COMMENT '第3张牌名',
    card3_num           VARCHAR(16)   NOT NULL DEFAULT '' COMMENT '第3张编号',
    cards_json          JSON          NULL COMMENT '三张牌完整JSON快照',
    draw_date           DATE          NOT NULL COMMENT '抽牌日期',
    created_at          DATETIME      DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_date (user_id, draw_date),
    INDEX idx_user_created (user_id, created_at)
) ENGINE=InnoDB COMMENT='塔罗抽牌记录表';

-- 探索星图节点记录表
CREATE TABLE IF NOT EXISTS explore_nodes (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL        COMMENT '用户ID',
    node_id         TINYINT UNSIGNED NOT NULL        COMMENT '节点ID 0-8',
    lit_at          DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '点亮时间',
    UNIQUE KEY uk_user_node (user_id, node_id)
) ENGINE=InnoDB COMMENT='探索星图节点点亮记录';
