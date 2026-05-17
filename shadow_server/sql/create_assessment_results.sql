-- =============================================================
-- 心理测评结果表 (assessment_results)
-- 统一存储各类心理测评的结果数据
-- 
-- 执行方式: MySQL 客户端整段执行
-- 依赖: users 表（user_id 外键关联）
-- =============================================================

USE xintujie;

CREATE TABLE IF NOT EXISTS assessment_results (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL COMMENT 'users.id',
    test_type       VARCHAR(32)    NOT NULL COMMENT '测评类型: mbti/enneagram/holland/mh/depression/intimacy',
    
    -- 主结果概要
    summary         VARCHAR(256)   NOT NULL DEFAULT '' COMMENT '主结果标签: 如 INFP/安全型/心理健康良好/中度抑郁风险',
    
    -- 详细结果 JSON (各测评结构不同)
    result_json     JSON           NOT NULL COMMENT '完整测评结果 JSON',
    
    -- 原始答题 JSON (可追溯)
    answers_json    JSON           DEFAULT NULL COMMENT '原始答案 [{q:0, a:1}, ...]',
    score_json      JSON           DEFAULT NULL COMMENT '原始得分 {dim1: 5, dim2: 3, ...}',

    -- 统计
    question_count  SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '题目数量',
    duration_sec    INT UNSIGNED   DEFAULT NULL COMMENT '作答耗时(秒)',

    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_user_type (user_id, test_type),
    KEY idx_type (test_type),
    KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='心理测评结果 — 统一存储各类型测评数据';
