-- =============================================================================
-- 仅建 users 表。若需一次建齐 users + emotion_records + 塔罗/探索，请用：
--   server/create_all_tables_xintujie.sql
-- =============================================================================
-- users：注册页 + 完善资料页（pages/profile-edit）
-- 库名默认 xintujie，Navicat 整段执行即可
-- =============================================================================
--
-- 【注册页 pages/register】
--   昵称              -> nickname
--   手机号            -> phone
--   密码 / 确认密码   -> 仅 password_hash（后端哈希写入，确认密码不入库）
--   勾选用户协议      -> terms_agreed_at（注册成功时由后端写入当前时间）
--
-- 【完善资料页 pages/profile-edit】
--   头像              -> avatar_url（上传后存可访问 URL）
--   昵称              -> nickname（与注册共用）
--   性别 女生/男生    -> gender  female / male（未选可为 unknown）
--   出生时间(年月日时分) -> birth_date + birth_time
--   出生地点(省市区)   -> birth_province, birth_city, birth_district
--   MBTI              -> mbti（如 INTJ）
--
-- 【微信 / 登录扩展】
--   open_id / union_id -> 小程序登录后由后端写入
--   profile_completed  -> 资料保存后可由后端置 1
--
-- id：自增主键（AUTO_INCREMENT），插入用户时不要手写 id，由数据库分配 1,2,3…
-- =============================================================================

CREATE DATABASE IF NOT EXISTS xintujie
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE xintujie;

-- 若已有旧表且要重建：先备份再 DROP TABLE users;

CREATE TABLE IF NOT EXISTS users (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID（自增，勿在 INSERT 里指定）',
    PRIMARY KEY (id),

    -- —— 注册页 ——
    phone               VARCHAR(20)   DEFAULT NULL              COMMENT '注册页-手机号，唯一',
    password_hash       VARCHAR(255)  NOT NULL DEFAULT ''       COMMENT '注册页-密码哈希，禁止明文',
    terms_agreed_at     DATETIME      DEFAULT NULL               COMMENT '注册页-同意协议时间',

    -- —— 完善资料页 ——
    nickname            VARCHAR(32)   NOT NULL DEFAULT ''       COMMENT '昵称（注册可填，资料页可改）',
    avatar_url          VARCHAR(1024) NOT NULL DEFAULT ''        COMMENT '资料页-头像 URL',
    gender              ENUM('male','female','unknown') NOT NULL DEFAULT 'unknown' COMMENT '资料页-性别 male/female',
    birth_date          DATE          DEFAULT NULL               COMMENT '资料页-出生日期',
    birth_time          VARCHAR(8)    NOT NULL DEFAULT ''        COMMENT '资料页-出生时刻 HH:MM',
    birth_province      VARCHAR(64)   NOT NULL DEFAULT ''       COMMENT '资料页-出生省',
    birth_city          VARCHAR(64)   NOT NULL DEFAULT ''       COMMENT '资料页-出生市',
    birth_district      VARCHAR(64)   NOT NULL DEFAULT ''       COMMENT '资料页-出生区县',
    mbti                VARCHAR(8)    NOT NULL DEFAULT ''       COMMENT '资料页-MBTI 四位',

    -- —— 微信与状态 ——
    open_id             VARCHAR(128)  DEFAULT NULL              COMMENT '微信 openid 或占位 p_手机号',
    union_id            VARCHAR(128)  DEFAULT NULL              COMMENT '微信 unionid',
    status              TINYINT UNSIGNED NOT NULL DEFAULT 1      COMMENT '1正常 0禁用',
    profile_completed   TINYINT UNSIGNED NOT NULL DEFAULT 0     COMMENT '资料是否已完善 1是',
    last_login_at       DATETIME      DEFAULT NULL               COMMENT '最近登录时间',

    created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册创建时间',
    updated_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_open_id (open_id),
    UNIQUE KEY uk_phone (phone),
    KEY idx_union_id (union_id),
    KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='用户：注册信息 + 完善资料';
