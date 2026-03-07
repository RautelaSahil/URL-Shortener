CREATE DATABASE IF NOT EXISTS url_shortner;
USE url_shortner;

-- ------------------ USERS ------------------

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------ LINKS ------------------

CREATE TABLE IF NOT EXISTS link (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original TEXT NOT NULL,
    short VARCHAR(10) NOT NULL UNIQUE,
    link_name VARCHAR(255),
    click_count INT DEFAULT 0,
    dob TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,

    INDEX idx_short (short),
    INDEX idx_user (user_id),

    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
