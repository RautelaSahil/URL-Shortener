create database url_shortner;

use url_shortner;



CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE link (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original TEXT NOT NULL,
    short VARCHAR(10) NOT NULL UNIQUE,
    dob TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    link_name VARCHAR(255),
    user_id INT,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
