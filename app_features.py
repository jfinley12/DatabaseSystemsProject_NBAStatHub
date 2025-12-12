# app_features.py
# creator: Jacob Finley (jf118221@ohio.edu)
# Purpose: app_features.py contains the core application logic for user management (registration, login, predictions)
#          and analytical views for the NBA Analytics Hub Demo application.
import sqlite3
import hashlib
from db_manager import DatabaseManager, DATABASE_NAME

# initializing this variable globally so we always can track the current user session
CURRENT_USER_ID = None

# Functions for the CRUD operations on users and predictions
# our GUI will be able to write new users, authenticate logins, and submit player predictions
def get_current_user():
    """Returns the ID of the currently logged-in user."""
    return CURRENT_USER_ID

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    """Registers a new user."""
    if not email or not password:
        return False, "Email and password cannot be empty."
    
    hashed_pw = hash_password(password)
    
    try:
        # hashing the password to meet the seucirty requirement mentioned in the project description
        with DatabaseManager(DATABASE_NAME) as db:
            db.begin_transaction()
            
            # insert into core_user_account
            account_query = "INSERT INTO core_user_account (email, password_hash) VALUES (?, ?)"
            db.execute(account_query, (email, hashed_pw))
        
            # retrieve the new user_id that has been created
            user_id = db.fetch_one("SELECT last_insert_rowid()")[0]
            
            # insert into core_user_profile
            profile_query = "INSERT INTO core_user_profile (user_id, display_name) VALUES (?, ?)"
            db.execute(profile_query, (user_id, email.split('@')[0]))
            
            db.commit_transaction()
            return True, f"Registration successful for {email}. User ID: {user_id}"
        
    # recommened error handling for unique email constraint violation        
    except sqlite3.IntegrityError:
        return False, "Registration failed: This email is already registered."
    except Exception as e:
        return False, f"Registration failed due to an internal error: {e}"



def login_user(email, password):
    # logging in after a user already exists
    global CURRENT_USER_ID
    
    # recall the hashed password for comparison
    hashed_pw = hash_password(password)
    
    # query the database to verify credentials and set the CURRENT_USER_ID
    try:
        with DatabaseManager(DATABASE_NAME) as db:
            query = "SELECT user_id, password_hash FROM core_user_account WHERE email = ?"
            result = db.fetch_one(query, (email,))
            
            if result and result[1] == hashed_pw:
                CURRENT_USER_ID = result[0]
                return True, f"Login successful. Welcome, User ID {CURRENT_USER_ID}."
            else:
                CURRENT_USER_ID = None
                return False, "Login failed: Invalid email or password."
    except Exception as e:
        return False, f"Login failed: {e}"



def submit_player_prediction(player_name, pred_type, pred_value):
    # Allows a logged-in user to submit a prediction about a player
    global CURRENT_USER_ID
    
    if CURRENT_USER_ID is None:
        return False, "Error: You must be logged in to submit a prediction."
        
    try:
        with DatabaseManager(DATABASE_NAME) as db:
            # get the player_id based on name
            player_query = "SELECT player_id FROM stat_player_bio WHERE full_name LIKE ? LIMIT 1"
            player_result = db.fetch_one(player_query, (f"%{player_name.strip()}%",))
            
            if not player_result:
                return False, f"Error: Player '{player_name}' not found in the database."
                
            player_id = player_result[0]
            
            # insert the prediction into the mart_user_predictions table
            insert_query = """
                INSERT INTO mart_user_predictions (user_id, player_id, prediction_type, prediction_value, prediction_date)
                VALUES (?, ?, ?, ?, DATE('now'))
            """
            db.execute(insert_query, (CURRENT_USER_ID, player_id, pred_type, pred_value))
            
            return True, f"Prediction '{pred_type}' for {player_name} submitted successfully!"
            
    except Exception as e:
        return False, f"Prediction submission failed: {e}"


# ANALYTICAL VIEWS for the GUI to call and display results
# ANALYTICAL VIEW 1: Top 5 Players by a Fixed Advanced Stat (e.g., 'orb_percent')
# ANALYTICAL VIEW 2: Most Frequently Injured Players
# ANALYTICAL VIEW 3: Team Demographics Summary

def get_top_advanced_stat(stat_abbr='orb_percent'):
    # Finds the top 5 players for the stat abbreviation provided

    print(f"Executing Analytical View 1: Top 5 players by '{stat_abbr}'")
    

    # select the top 5 players based on the provided advanced stat abbreviation and output their names, stat values, and ranks
    try:
        with DatabaseManager(DATABASE_NAME) as db:
            query = """
                SELECT
                    T1.full_name,
                    T3.advanced_value,
                    RANK() OVER (ORDER BY T3.advanced_value DESC) AS Rank
                FROM stat_player_bio T1
                JOIN fact_player_advanced_stats T3 ON T1.player_id = T3.player_id
                JOIN ref_advanced_stat_type T2 ON T3.stat_id = T2.stat_id
                WHERE T2.stat_abbreviation = ?
                ORDER BY T3.advanced_value DESC
                LIMIT 5
            """
            result = db.fetchall(query, (stat_abbr,))
            header = ["Player Name", f"{stat_abbr} Value", "Rank"]
            return result, header
    except Exception as e:
        print(f"Error in get_top_advanced_stat: {e}")
        return [], ["Player Name", f"{stat_abbr} Value", "Rank"]

def get_most_injured_players():

    # Outputs the players who were injured the most.
    print("Executing Analytical View 2: Most Frequently Injured Players")
    
    # select the players whose name appeared the most in the injury database
    # output the player name, the number of injuries and the top 5 most injured players
    try:
        with DatabaseManager(DATABASE_NAME) as db:
            query = """
                SELECT
                    T1.full_name,
                    COUNT(T2.report_id) AS total_injuries,
                    RANK() OVER (ORDER BY COUNT(T2.report_id) DESC) AS injury_rank
                FROM stat_player_bio T1
                JOIN bg_injury_report T2 ON T1.player_id = T2.player_id
                GROUP BY T1.player_id, T1.full_name
                HAVING total_injuries > 0
                ORDER BY total_injuries DESC
                LIMIT 5
            """
            result = db.fetchall(query)
            header = ["Player Name", "Total Injuries", "Injury Rank"]
            return result, header
    except Exception as e:
        print(f"Error in get_most_injured_players: {e}")
        return [], ["Player Name", "Total Injuries", "Injury Rank"]

def get_team_demographics_summary():
    
    # Outputs demographics for cities in the database.
    print("Executing Analytical View 3: City Demographics Summary")
    
    try:
        with DatabaseManager(DATABASE_NAME) as db:
            query = """
                SELECT
                    T1.city_name,
                    T1.state_province,
                    PRINTF('$%,d', CAST(T2.median_household_income AS INTEGER)) AS median_income,
                    PRINTF('%,d', T2.population) AS population
                FROM ref_city T1
                JOIN bg_city_demographics T2 ON T1.city_id = T2.city_id
                ORDER BY T2.median_household_income DESC
                LIMIT 10
            """
            result = db.fetchall(query)
            header = ["City", "State", "Median Household Income", "Population"]
            return result, header
    except Exception as e:
        print(f"Error in get_team_demographics_summary: {e}")
        return [], ["City", "State", "Median Household Income", "Population"]

# format_results: a helper function to format all of the players and cities into a readabel table 

def format_results(header, data):
    # Formats SQL results into a readable string
    if not data:
        return "No data found for this query."

    # calculate column widths
    widths = [len(h) for h in header]
    for row in data:
        for i, item in enumerate(row):
            widths[i] = max(widths[i], len(str(item)))

    # separator line
    separator = '+-' + '-+-'.join(['-' * w for w in widths]) + '-+'

    output = separator + '\n'
    # header row
    header_row = '| ' + ' | '.join(h.ljust(widths[i]) for i, h in enumerate(header)) + ' |'
    output += header_row + '\n'
    output += separator + '\n'

    # data rows
    for row in data:
        row_str = '| ' + ' | '.join(str(item).ljust(widths[i]) for i, item in enumerate(row)) + ' |'
        output += row_str + '\n'
    output += separator

    # return the output into the GUI
    return output