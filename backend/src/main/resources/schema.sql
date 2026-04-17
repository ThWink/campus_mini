-- 创建用户表
CREATE TABLE IF NOT EXISTS user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'USER',
    status INT NOT NULL DEFAULT 1,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认管理员账号
INSERT INTO user (username, password, phone, role, status, create_time) VALUES
('admin', 'admin', '13800138000', 'ADMIN', 1, NOW());

-- 插入测试用户
INSERT INTO user (username, password, phone, role, status, create_time) VALUES
('user1', 'user1', '13800138001', 'USER', 1, NOW()),
('user2', 'user2', '13800138002', 'USER', 1, NOW());
