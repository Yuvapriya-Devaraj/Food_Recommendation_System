CREATE DATABASE IF NOT EXISTS kids_food_recommendation;
USE kids_food_recommendation;

CREATE TABLE kids (
    kid_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    favorite_food JSON;
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

CREATE TABLE food (
    food_id INT AUTO_INCREMENT PRIMARY KEY,
    food_name VARCHAR(100),
    category VARCHAR(50),
    health VARCHAR(50),
    timing VARCHAR(50),
    season VARCHAR(50),
    score INT,
    taste VARCHAR(50),
    min_age INT,
    frequency_limit INT
);

CREATE TABLE kid_food_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    kid_id VARCHAR(20),
    food_id INT,
    meal_type ENUM('snack','lunch'),
    liked BOOLEAN,
    score INT DEFAULT 10,
    consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (kid_id) REFERENCES kids(kid_id),
    FOREIGN KEY (food_id) REFERENCES food(food_id)
);
