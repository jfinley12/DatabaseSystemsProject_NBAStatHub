# using sqlite, the purpose of this demo is to go through the basic CRUD testing operations for the user accounts and stat tables
# I want to compartmentalize the different parts of this project, starting with the demo_players.py file to make sure that the 
# basic operations are working as expected before moving on to having everything working together in the main app

import sqlite3
import os

DB_NAME = 'nba_stats_hub_DEMO.db'

def create_mock_tables(conn):
    """Sets up minimal tables needed for the R/W/U/D/F demo."""
    cursor = conn.cursor()
    
    # 1. core_user_account (for Write/Read/Update/Delete)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_user_account (
            user_id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            pwd_hash TEXT NOT NULL,
            created_at TIMESTAMP
        );
    """)

    # 2. core_user_profile (for Update)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_user_profile (
            user_id INTEGER PRIMARY KEY,
            display_name TEXT,
            FOREIGN KEY (user_id) REFERENCES core_user_account(user_id) ON DELETE CASCADE
        );
    """)

    # 3. stat_player_bio (for Filter/Analytical View)
    # Mock data is loaded into this table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stat_player_bio (
            player_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            salary_usd BIGINT
        );
    """)

    # Insert mock data for the so we can filter and see results
    mock_players = [
        (1, 'Star Player A', 45000000),
        (2, 'Role Player B', 5000000),
        (3, 'Superstar C', 50000000),
        (4, 'Bench Player D', 1500000)
    ]
    cursor.executemany("INSERT OR IGNORE INTO stat_player_bio VALUES (?, ?, ?)", mock_players)
    conn.commit()

# testing the CREATION and READING of user accounts
def create_user(conn, email, password_hash):
    """(WRITE) Inserts a new user into the database."""
    print(f"\n--- WRITE: Creating user '{email}' ---")
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO core_user_account (email, pwd_hash, created_at) VALUES (?, ?, datetime('now'))", 
                       (email, password_hash))
        new_user_id = cursor.lastrowid                        # last inserted row id gives us the new user id
        
        # Also create a linked profile entry
        cursor.execute("INSERT INTO core_user_profile (user_id, display_name) VALUES (?, ?)", 
                       (new_user_id, email.split('@')[0]))
        conn.commit()
        print(f"SUCCESS: User created with ID {new_user_id}")  # success message when a new user is created with an id
        return new_user_id
    except sqlite3.IntegrityError:                             # assert we are not duplicating emails when creating users
        print("ERROR: User with this email already exists.")
        return None

def read_user(conn, user_id):
    """(READ) Retrieves and displays a user's account and profile data."""
    print(f"\n--- READ: Fetching User ID {user_id} ---")
    cursor = conn.cursor()

    # selecting from both account and profile tables to get complete user info
    cursor.execute("""                              
        SELECT a.user_id, a.email, p.display_name
        FROM core_user_account a JOIN core_user_profile p ON a.user_id = p.user_id
        WHERE a.user_id = ?
    """, (user_id,))
    
    user_data = cursor.fetchone()
    if user_data:
        print(f"Result: ID={user_data[0]}, Email={user_data[1]}, Display Name={user_data[2]}")
        return user_data
    else:
        print(f"FAILURE: User ID {user_id} not found.")
        return None

# testing the UPDATING of user profiles
def update_display_name(conn, user_id, new_name):
    """(UPDATE) Changes the user's display name."""
    print(f"\n--- UPDATE: Changing display name for ID {user_id} to '{new_name}' ---")
    cursor = conn.cursor()
    cursor.execute("UPDATE core_user_profile SET display_name = ? WHERE user_id = ?", 
                   (new_name, user_id))
    conn.commit()
    print("SUCCESS: Display name updated.")

# testing the DELETION of user accounts
def delete_user(conn, user_id):
    """(DELETE) Removes a user account and profile (due to ON DELETE CASCADE FK)."""
    print(f"\n--- DELETE: Removing User ID {user_id} ---")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM core_user_account WHERE user_id = ?", (user_id,))
    conn.commit()
    print("SUCCESS: User account and profile deleted.")

# testing the FILTERING of players based on salary using the inserted mock data
def filter_top_paid_players(conn, min_salary):
    """(FILTER/ANALYTICAL) Finds players above a specific salary threshold."""
    print(f"\n--- FILTER/ANALYTICAL: Players with Salary > ${min_salary:,} ---")
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, salary_usd FROM stat_player_bio WHERE salary_usd > ?", (min_salary,))
    results = cursor.fetchall()
    
    if results:
        for name, salary in results:
            print(f"- {name}: ${salary:,}")
    else:
        print("No players found meeting the criteria.")
    
    return results

def main():
    # Clean up previous database file if it exists
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    conn.execute('PRAGMA foreign_keys = ON;') # Enable FK constraints
    create_mock_tables(conn)

    # 1. WRITE and READ
    user_id = create_user(conn, 'testuser@example.com', 'hashed_pass123')
    if user_id:
        read_user(conn, user_id)
    
        # 2. UPDATE
        update_display_name(conn, user_id, 'MVP_Analyst')
        read_user(conn, user_id) # Verify update
        
        # 3. FILTER
        filter_top_paid_players(conn, 40000000) # Find all players over $40M
        
        # 4. DELETE
        delete_user(conn, user_id)
        read_user(conn, user_id) # Verify deletion

    conn.close()

if __name__ == "__main__":
    main()