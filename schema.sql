-- schema.sql

-- --- Only including the necessary schemas that are going to be used form data imported from kaggle ---
-- --- The full schema diagram is under /Screenshots and Demo/finalproject_ER_eraserio.png ---

CREATE TABLE ref_city (
    city_id INTEGER PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    state_province VARCHAR(50),
    country VARCHAR(50)
);

CREATE TABLE ref_season (
    season_id   INTEGER PRIMARY KEY,
    season_year TEXT NOT NULL,
    is_current  BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE bg_city_demographics (
    city_id INTEGER PRIMARY KEY,
    population BIGINT,
    median_household_income INT,
    poverty_rate DECIMAL(5, 2),
    FOREIGN KEY (city_id) REFERENCES ref_city(city_id)
);

CREATE TABLE ref_basic_stat_type (
    stat_id INTEGER PRIMARY KEY,
    stat_name VARCHAR(50) NOT NULL UNIQUE,
    stat_abbreviation VARCHAR(10) NOT NULL UNIQUE,
    description VARCHAR(200)
);

CREATE TABLE ref_advanced_stat_type (
    stat_id INTEGER PRIMARY KEY,
    stat_name VARCHAR(50) NOT NULL UNIQUE,
    stat_abbreviation VARCHAR(10) NOT NULL UNIQUE,
    formula_desc VARCHAR(200)
);

-- --- Core NBA Entity Tables ---

CREATE TABLE stat_player_bio (
    player_id INTEGER PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    height_inches INT,
    weight_lbs INT,
    birth_date DATE,
    position VARCHAR(10),
    salary_usd BIGINT
);

-- --- Fact and Bridge Tables ---

CREATE TABLE fact_player_advanced_stats (
    player_id               INTEGER NOT NULL,
    season_id               INTEGER NOT NULL,
    stat_id                 INTEGER NOT NULL,
    advanced_value          REAL,

    PRIMARY KEY (player_id, season_id, stat_id),
    FOREIGN KEY (player_id) REFERENCES stat_player_bio (player_id),
    FOREIGN KEY (season_id) REFERENCES ref_season (season_id),
    FOREIGN KEY (stat_id) REFERENCES ref_advanced_stat_type (stat_id)
);

-- --- Background Data (External Datasets) ---

CREATE TABLE bg_injury_report (
    report_id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,
    injury_date DATE NOT NULL,
    return_date DATE,
    body_part VARCHAR(50),
    severity VARCHAR(50),
    source_citation VARCHAR(200),
    FOREIGN KEY (player_id) REFERENCES stat_player_bio(player_id)
);

-- --- User and Application Tables ---

CREATE TABLE core_user_account (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE core_user_profile (
    user_id INTEGER PRIMARY KEY,
    display_name VARCHAR(50),
    timezone VARCHAR(50),
    preferences_json TEXT,
    FOREIGN KEY (user_id) REFERENCES core_user_account(user_id) ON DELETE CASCADE
);

CREATE TABLE mart_user_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    player_id INTEGER,
    prediction_type VARCHAR(50) NOT NULL,
    prediction_value VARCHAR(100) NOT NULL,
    prediction_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES core_user_account(user_id),
    FOREIGN KEY (player_id) REFERENCES stat_player_bio(player_id)
);