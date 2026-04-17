-- 删除并重建 emotion_records（会清空该表全部数据，执行前请确认）
USE xintujie;

DROP TABLE IF EXISTS emotion_records;

CREATE TABLE emotion_records (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    emotion_score   TINYINT UNSIGNED NOT NULL DEFAULT 50 COMMENT '情绪分 0-100',
    vitality_score  TINYINT UNSIGNED NOT NULL DEFAULT 50 COMMENT '活力分 0-100',
    note            TEXT COMMENT '备注',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    KEY idx_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情绪记录表';
