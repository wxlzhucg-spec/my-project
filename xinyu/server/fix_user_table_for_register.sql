-- 注册 POST /user/register 报 500 时，多半是 users 表缺列或列名不一致
-- 在 Navicat 选中库 xintujie，按需执行；已存在的列会报错，跳过即可

USE xintujie;

-- Flask 注册 INSERT 会用到的列（缺则补）
ALTER TABLE users ADD COLUMN terms_agreed_at DATETIME DEFAULT NULL COMMENT '同意协议时间' AFTER password_hash;

-- 若没有 password_hash 而有 password（老表），需自行改名或建新表
-- ALTER TABLE users CHANGE COLUMN password password_hash VARCHAR(255) NOT NULL DEFAULT '';

-- 若列名是 openid 而代码写的是 open_id：
-- ALTER TABLE users CHANGE COLUMN openid open_id VARCHAR(128) DEFAULT NULL;

-- 核对表结构（执行后在结果里看列名是否与 Flask 一致）
-- DESCRIBE users;
