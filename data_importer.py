# data_importer.py
# creator: Jacob Finley (jf118221@ohio.edu)
# Purpose: data_importer.py handles the importing of datasets into the NBA Analytics Hub Demo application's database.
# this file is the most complex as it involves reading CSV files, cleaning data, and populating multiple related tables.
# it uses pandas for data manipulation and sqlite3 for database interaction

import pandas as pd
import numpy as np
import os
from db_manager import DatabaseManager, setup_database, DATABASE_NAME, SCHEMA_FILE

# configuration of the dataset file paths
DATASETS_DIR = 'datasets'
DATASET_FILES = {
    'nba_stats': os.path.join(DATASETS_DIR, 'advanced.csv'),
    'nba_injuries': os.path.join(DATASETS_DIR, 'injuries_2010-2020.csv'),
    'house_prices': os.path.join(DATASETS_DIR, 'American_Housing_Data_20231209.csv')
}


# load_data: helper function to load a CSV file into a Pandas DataFrame
# checks the file path and handles incorrect paths or read errors
# returns the DataFrame if successful, else None
def load_data(file_key):
    """Loads a CSV file into a Pandas DataFrame."""
    file_path = DATASET_FILES.get(file_key)
    if not file_path or not os.path.exists(file_path):
        print(f"WARNING: Dataset file not found for key '{file_key}' at {file_path}. Skipping import.")
        return None
    try:
        df = pd.read_csv(file_path, low_memory=False, encoding='utf-8')
        print(f"Successfully loaded {file_key} with {len(df)} rows")
        return df
    except Exception as e:
        print(f"ERROR: Failed to read {file_key} file: {e}")
        return None


# import_nba_stats: imports NBA advanced stats into relevant tables
# The data is sourced from 'advanced.csv'
# data is stroed in stat_player_bio, ref_season, ref_advanced_stat_type, and fact_player_advanced_stats
def import_nba_stats(db: DatabaseManager):
    """
    Imports core NBA stats into stat_player_bio, ref_season, and fact_player_advanced_stats.
    (Source 1: advanced.csv)
    """
    df = load_data('nba_stats')
    if df is None: 
        print("Skipping NBA stats import - file not found")
        return

    print("\n--- Starting NBA Advanced Stats Import (Source 1: advanced.csv) ---")
    
    # Clean column names and handle the data
    df.columns = df.columns.str.strip()
    
    # Create player mapping
    player_map = {name: idx + 1 for idx, name in enumerate(df['player'].unique())}
    df['player_id'] = df['player'].map(player_map)

    # Season mapping
    season_names = df['season'].unique()
    season_data = []
    season_id_map = {}

    for name in season_names:
        try:
            season_id = int(name)
        except ValueError:
            season_id = int(str(name).split('-')[0])
        
        season_id_map[name] = season_id
        season_data.append((season_id, str(name)))
    
    # insert seaosns into ref_season
    season_insert_query = """
        INSERT OR IGNORE INTO ref_season (season_id, season_year, is_current)
        VALUES (?, ?, 0)
    """
    db.executemany(season_insert_query, season_data)
    print(f"Inserted {len(season_data)} unique seasons into ref_season.")
    
    # intsert into stat_player_bio
    player_bio_df = df[['player_id', 'player', 'age', 'pos']].drop_duplicates(subset=['player_id'])
    
    player_bio_data = [
        (
            row['player_id'], 
            row['player'],
            row['age'] if pd.notna(row['age']) else None,
            row['pos'] if pd.notna(row['pos']) else 'N/A',
            0
        )
        for index, row in player_bio_df.iterrows()
    ]
    
    player_bio_insert_query = """
        INSERT OR REPLACE INTO stat_player_bio (player_id, full_name, birth_date, position, salary_usd)
        VALUES (?, ?, ?, ?, ?)
    """
    db.executemany(player_bio_insert_query, player_bio_data)
    print(f"Inserted/Updated {len(player_bio_data)} unique players into stat_player_bio.")

    # insert data into ref_advanced_stat_type
    ignore_cols = ['player_id', 'season', 'player', 'lg', 'team', 'age', 'pos', 'g', 'gs', 'mp', 'player_id']
    advanced_stats = [col for col in df.columns if col not in ignore_cols]
    
    stat_ref_data = [(i + 1, stat, stat) for i, stat in enumerate(advanced_stats)]
    stat_map = {stat: i + 1 for i, stat in enumerate(advanced_stats)}
    
    stat_ref_insert_query = """
        INSERT OR IGNORE INTO ref_advanced_stat_type (stat_id, stat_name, stat_abbreviation)
        VALUES (?, ?, ?)
    """
    db.executemany(stat_ref_insert_query, stat_ref_data)
    print(f"Inserted {len(stat_ref_data)} advanced stat types into ref_advanced_stat_type.")
    
    # insert data into fact_player_advanced_stats
    fact_advanced_data = []
    
    # iterate through the index and rows of the dataframe and insert data into  the fact table
    for index, row in df.iterrows():
        pid = row['player_id']
        season_id = season_id_map[row['season']]
        
        for stat_abbr, stat_id in stat_map.items():
            value = row.get(stat_abbr)
            if pd.notna(value):
                try:
                    fact_advanced_data.append((pid, season_id, stat_id, float(value)))
                except (ValueError, TypeError):
                    continue
    
    # insert into fact_player_advanced_stats
    fact_adv_insert_query = """
        INSERT OR IGNORE INTO fact_player_advanced_stats (player_id, season_id, stat_id, advanced_value)
        VALUES (?, ?, ?, ?)
    """
    db.executemany(fact_adv_insert_query, fact_advanced_data)
    print(f"Inserted {len(fact_advanced_data)} player advanced stats.")


# import_nba_injuries: imports NBA injury records into bg_injury_report
# The data is sourced from 'injuries_2010-2020.csv'
# data is stored in bg_injury_report
def import_nba_injuries(db: DatabaseManager):
    """
    Imports NBA injury records into bg_injury_report.
    (Source 2: injuries_2010-2020.csv)
    """
    df = load_data('nba_injuries')
    if df is None:
        print("Skipping NBA injuries import - file not found")
        return

    print("\n--- Starting NBA Injuries Import (Source 2: injuries_2010-2020.csv) ---")
    
    # strip column names
    df.columns = df.columns.str.strip()
    
    # make sure the names of columns match expected names
    df = df.rename(columns={'Date': 'injury_date', 'Team': 'team_name', 'Relinquished': 'full_name', 'Notes': 'notes'})
    
    df.dropna(subset=['full_name', 'injury_date'], inplace=True)
    df['injury_date'] = pd.to_datetime(df['injury_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df.dropna(subset=['injury_date'], inplace=True)
    
    df['full_name'] = df['full_name'].str.strip()

    # Map player names to IDs
    player_map_query = "SELECT full_name, player_id FROM stat_player_bio"
    existing_players = db.fetchall(player_map_query)
    
    player_id_map = {name.strip(): pid for name, pid in existing_players}
    
    df['player_id'] = df['full_name'].map(player_id_map)
    df.dropna(subset=['player_id'], inplace=True)
    df['player_id'] = df['player_id'].astype(int)

    # insert data into  bg_injury_report table
    injury_data = [
        (
            index + 1,
            row['player_id'],
            row['injury_date'],
            None,
            row['notes'][:50] if pd.notna(row['notes']) else 'Unknown',
            row['notes'] if pd.notna(row['notes']) else '',
            "Kaggle NBA Injuries Dataset",
        )
        for index, row in df.iterrows()
    ]
    
    # insert into bg_injury_report
    injury_insert_query = """
        INSERT OR IGNORE INTO bg_injury_report (report_id, player_id, injury_date, return_date, body_part, severity, source_citation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    db.executemany(injury_insert_query, injury_data)
    print(f"Inserted {len(injury_data)} injury records into bg_injury_report.")



# import_housing_data: imports US housing data into ref_city and bg_city_demographics
# data is sourced from 'American_Housing_Data_20231209.csv'
# data is stored in ref_city and bg_city_demographics
def import_housing_data(db: DatabaseManager):
    """
    Imports US housing data into ref_city and bg_city_demographics.
    (Source 3: American_Housing_Data_20231209.csv)
    """
    df = load_data('house_prices')
    if df is None:
        print("Skipping housing data import - file not found")
        return

    print("\n--- Starting Housing Data Import (Source 3: Housing Data) ---")
    
    # strip column names
    df.columns = df.columns.str.strip()
    
    # rename columns
    required_cols = ['Zip Code Population', 'Median Household Income', 'State', 'City']
    if not all(col in df.columns for col in required_cols):
        print(f"ERROR: Missing required columns. Found: {df.columns.tolist()}")
        return
    
    df = df.rename(columns={
        'Zip Code Population': 'population',
        'Median Household Income': 'median_income',
        'State': 'state_province',
        'City': 'city_name'
    })
    
    # group data by City/State
    city_df = df.groupby(['city_name', 'state_province']).agg({
        'median_income': 'mean',
        'population': 'sum'
    }).reset_index()
    
    city_df.dropna(subset=['city_name', 'state_province'], inplace=True)
    
    city_df['city_state'] = city_df['city_name'] + '-' + city_df['state_province']
    city_map = {name: idx + 1 for idx, name in enumerate(city_df['city_state'].unique())}
    city_df['city_id'] = city_df['city_state'].map(city_map)
    
    # insert data into ref_city
    ref_city_data = [
        (row['city_id'], row['city_name'], row['state_province'], 'USA')
        for index, row in city_df.iterrows()
    ]
    ref_city_insert_query = """
        INSERT OR IGNORE INTO ref_city (city_id, city_name, state_province, country)
        VALUES (?, ?, ?, ?)
    """
    db.executemany(ref_city_insert_query, ref_city_data)
    print(f"Inserted {len(ref_city_data)} unique cities into ref_city.")
    
    # insert data into  bg_city_demographics
    bg_demo_data = [
        (
            row['city_id'], 
            int(row['population']), 
            int(row['median_income']), 
            0.0
        )
        for index, row in city_df.iterrows()
    ]
    bg_demo_insert_query = """
        INSERT OR IGNORE INTO bg_city_demographics (city_id, population, median_household_income, poverty_rate)
        VALUES (?, ?, ?, ?)
    """
    db.executemany(bg_demo_insert_query, bg_demo_data)
    print(f"Inserted {len(bg_demo_data)} demographic records.")



# function to run the entire imprt process on the three different kaggle datasets
def run_importer():
    """Main execution function to setup DB and run all imports."""
    print("--- Starting Database Import Process ---")
    
    if not os.path.exists(DATASETS_DIR):
        os.makedirs(DATASETS_DIR)
        print(f"Created directory: {DATASETS_DIR}. Please place your CSV files inside.")
        return

    with DatabaseManager(DATABASE_NAME) as db:
        import_nba_stats(db)
        import_nba_injuries(db)
        import_housing_data(db)
        
    print("\n--- Database Import Process Complete ---")



if __name__ == '__main__':
    run_importer()