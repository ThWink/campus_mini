-- 创建管理员账号
INSERT INTO user (username, password, phone, role, create_time) VALUES
('admin', 'admin', '13800138000', 'ADMIN', NOW());

-- 创建测试用户
INSERT INTO user (username, password, phone, role, create_time) VALUES
('user1', 'user1', '13800138001', 'USER', NOW()),
('user2', 'user2', '13800138002', 'USER', NOW());
