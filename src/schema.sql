CREATE DATABASE IF NOT EXISTS mye030_project;
USE mye030_project;

CREATE TABLE IF NOT EXISTS countries (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    iso_code CHAR(2) NOT NULL,
    iso3_code CHAR(3),
    name VARCHAR(100) NOT NULL,
    official_name VARCHAR(100),
    capital VARCHAR(100),
    continent VARCHAR(50),
    region_name VARCHAR(100),
    subregion_name VARCHAR(100),
    intermediate_region_name VARCHAR(100),
    status VARCHAR(50),
    development_status VARCHAR(50),
    area_sq_km DECIMAL(15, 2),
    population BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS former_country_names (
    id INT AUTO_INCREMENT PRIMARY KEY,
    former_name VARCHAR(100) NOT NULL,
    current_name VARCHAR(100) NOT NULL,  
    country_id INT,                      
    start_date DATE,                     
    end_date DATE,                       
    FOREIGN KEY (country_id) REFERENCES countries(country_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS years (
    year_id INT PRIMARY KEY,  
    total_matches INT DEFAULT 0,
    total_draws INT DEFAULT 0,
    total_penalty_shootouts INT DEFAULT 0,
    total_goals INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    year INT NOT NULL,  
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    home_score SMALLINT NOT NULL,
    away_score SMALLINT NOT NULL,
    city VARCHAR(100),
    country_id INT,
    has_penalty_shootout BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (home_team_id) REFERENCES countries(country_id),
    FOREIGN KEY (away_team_id) REFERENCES countries(country_id),
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (year) REFERENCES years(year_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    first_appearance_year INT,
    last_appearance_year INT,
    total_goals INT DEFAULT 0,
    max_goals_in_match INT DEFAULT 0,
    UNIQUE (name)  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS goals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    player_id INT NOT NULL,
    team_id INT NOT NULL,
    year INT NOT NULL,  
    own_goal BOOLEAN DEFAULT FALSE,
    penalty BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES countries(country_id),
    FOREIGN KEY (year) REFERENCES years(year_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS country_year_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    year INT NOT NULL,
    matches_played INT DEFAULT 0,
    wins INT DEFAULT 0,
    draws INT DEFAULT 0,
    losses INT DEFAULT 0,
    goals_for INT DEFAULT 0,
    goals_against INT DEFAULT 0,
    home_matches INT DEFAULT 0,
    home_wins INT DEFAULT 0,
    home_draws INT DEFAULT 0,
    home_losses INT DEFAULT 0,
    away_matches INT DEFAULT 0,
    away_wins INT DEFAULT 0,
    away_draws INT DEFAULT 0,
    away_losses INT DEFAULT 0,
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (year) REFERENCES years(year_id),
    UNIQUE (country_id, year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS player_year_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    country_id INT NOT NULL,
    year INT NOT NULL,
    goals INT DEFAULT 0,
    matches_with_goals INT DEFAULT 0,
    penalties INT DEFAULT 0,
    own_goals INT DEFAULT 0,
    team_total_matches INT DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (year) REFERENCES years(year_id),
    UNIQUE (player_id, country_id, year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS shootouts (
    shootout_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    winner_id INT NOT NULL,
    first_shooter_id INT,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (winner_id) REFERENCES countries(country_id),
    FOREIGN KEY (first_shooter_id) REFERENCES countries(country_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
