create database url_shortner;

use url_shortner;

create table dmforlink(
    id int AUTO_INCREMENT primary key,
    original text NOT NULL,
    pipiurl varchar(10) NOT NULL unique,
    dob timestamp default current_timestamp
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE dmforlink
ADD COLUMN link_name VARCHAR(255),
ADD COLUMN user_id INT,
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;
