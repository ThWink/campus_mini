-- 说明：为 sys_user 表新增 status 字段（用户状态）
-- 建议约定：1=启用，0=禁用（可按你项目需要调整）

ALTER TABLE sys_user
    ADD COLUMN status INT NOT NULL DEFAULT 1 COMMENT '用户状态：1启用，0禁用' AFTER role;

