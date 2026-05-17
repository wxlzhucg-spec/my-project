-- =============================================================================
-- 新增 tarot_sessions 表：存储塔罗牌 AI 解读会话完整数据
-- 关联 tarot_draws（抽牌记录）+ session_id（对话会话）+ 聊天记录 + AI 解读结果
--
-- 执行方式：在 MySQL 客户端连接 xintujie 库后执行本脚本
-- =============================================================================

USE xintujie;

CREATE TABLE IF NOT EXISTS tarot_sessions (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id             BIGINT UNSIGNED NOT NULL COMMENT '用户ID users.id',
    draw_id             BIGINT UNSIGNED DEFAULT NULL COMMENT '关联抽牌记录 tarot_draws.id',
    session_id          VARCHAR(64)     NOT NULL DEFAULT '' COMMENT '影子AI会话ID（LangGraph thread_id）',
    category            VARCHAR(32)     NOT NULL DEFAULT 'TAROT' COMMENT '会话分类（TAROT/ZODIAC/EMOTION_LOG等）',

    -- 塔罗牌快照（冗余存储，避免跨表查询）
    cards_json          JSON            NULL COMMENT '三张牌完整 JSON 快照',

    -- 用户咨询意图
    question            VARCHAR(512)    NOT NULL DEFAULT '' COMMENT '用户咨询问题/主题',
    theme_tag_id        VARCHAR(32)     NULL DEFAULT NULL COMMENT '预设主题ID',
    theme_tag_label     VARCHAR(64)     NULL DEFAULT NULL COMMENT '预设主题文案',

    -- AI 解读结果
    ai_reply            MEDIUMTEXT      NULL COMMENT 'AI 塔罗解读完整回复',
    phase               VARCHAR(32)     NOT NULL DEFAULT '' COMMENT '对话阶段：clarifying/complete',

    -- 聊天记录（完整对话历史）
    chat_messages       JSON            NULL COMMENT '对话消息列表 JSON，[{role,content,timestamp},...]',

    -- 用户画像快照（解读时使用的用户信息）
    user_snapshot       JSON            NULL COMMENT '用户信息快照（mbti/blood_type等，用于复盘）',

    -- 统计
    message_count       INT UNSIGNED    NOT NULL DEFAULT 0 COMMENT '对话消息总数',

    -- 时间
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '会话创建时间',
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',

    KEY idx_user_id (user_id),
    KEY idx_draw_id (draw_id),
    KEY idx_session_id (session_id),
    KEY idx_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='塔罗牌 AI 解读会话记录';
