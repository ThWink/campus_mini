CREATE TABLE IF NOT EXISTS user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'USER',
    status INT NOT NULL DEFAULT 1,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    publisher_id BIGINT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    reward DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status INT NOT NULL DEFAULT 0,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_publisher_id (publisher_id),
    INDEX idx_task_status (status)
);

CREATE TABLE IF NOT EXISTS orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id BIGINT NOT NULL,
    runner_id BIGINT,
    status INT NOT NULL DEFAULT 0,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_orders_user_id (user_id),
    INDEX idx_orders_runner_id (runner_id),
    INDEX idx_orders_task_id (task_id),
    INDEX idx_orders_status (status)
);

CREATE TABLE IF NOT EXISTS comment (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT,
    task_id BIGINT NOT NULL,
    reviewer_id BIGINT,
    reviewee_id BIGINT,
    score INT NOT NULL,
    tags VARCHAR(255),
    content TEXT,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_comment_order_id (order_id),
    INDEX idx_comment_task_id (task_id),
    INDEX idx_comment_reviewer_id (reviewer_id),
    INDEX idx_comment_reviewee_id (reviewee_id),
    UNIQUE KEY uk_comment_order_reviewer (order_id, reviewer_id)
);

ALTER TABLE comment ADD COLUMN IF NOT EXISTS order_id BIGINT;
ALTER TABLE comment ADD COLUMN IF NOT EXISTS reviewer_id BIGINT;
ALTER TABLE comment ADD COLUMN IF NOT EXISTS reviewee_id BIGINT;
ALTER TABLE comment ADD COLUMN IF NOT EXISTS tags VARCHAR(255);
ALTER TABLE comment ADD COLUMN IF NOT EXISTS create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

INSERT IGNORE INTO user (username, password, phone, role, create_time)
VALUES ('admin', 'sc031215', '13800138000', 'ADMIN', NOW());

INSERT IGNORE INTO user (username, password, phone, role, create_time)
VALUES ('user1', 'user1', '13800138001', 'USER', NOW());

INSERT IGNORE INTO user (username, password, phone, role, create_time)
VALUES ('user2', 'user2', '13800138002', 'USER', NOW());
