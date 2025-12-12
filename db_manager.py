# db_manager.py
# creator: Jacob Finley (jf118221@ohio.edu)
# Purpose: db_manager.py handles the database connection and schema setup for the NBA Analytics Hub Demo application.

import sqlite3
import os

DATABASE_NAME = 'nba_stats_hub.db' # the database that gets created
SCHEMA_FILE = 'schema.sql'


def setup_database():
    # checks if the database exists
    #  if not, creates it and applies the schema
    if os.path.exists(DATABASE_NAME):
        print(f"Database '{DATABASE_NAME}' already exists. Skipping schema creation.")
        return

    if not os.path.exists(SCHEMA_FILE):
        print(f"ERROR: Schema file '{SCHEMA_FILE}' not found. Cannot create database.")
        raise FileNotFoundError(f"Schema file '{SCHEMA_FILE}' not found")

    # since the db doesn't exist create it based on the schema file
    print(f"Executing SQL script from: {SCHEMA_FILE}")
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            with open(SCHEMA_FILE, 'r') as f:
                sql_script = f.read()
            conn.executescript(sql_script)
        print("Schema created successfully.")
        print("Database setup complete.")
    except Exception as e:
        print(f"Error during database setup: {e}")
        raise



# class DatabaseManager:
# handles the connection to the SQLite database and provides methods for executing queries and managing transactions
# functions are: initialize, enter, exit, begin_transaction, commit_transaction, rollback_transaction, execute, executemany, fetchall, fetch_one
# initialize: sets up the database name and connection attributes
#   enter: opens the database connection and creates a cursor
#    exit: commits changes and closes the connection
#   begin_transaction: starts an explicit transaction
#   commit_transaction: commits the explicit transaction
#   rollback_transaction: rolls back the explicit transaction
#   execute: executes a single SQL query
#   executemany: executes a SQL query against all parameter sequences or mappings
#   fetchall: fetches all rows resulting from a query
#   fetch_one: fetches a single row resulting from a query
class DatabaseManager:

    # a context manager class for handling SQLite database connections and transactions
    def __init__(self, db_name):
        self.db_name = db_name
        self._connection = None
        self._cursor = None

    def __enter__(self):
        # opens the database connection and creates a cursor
        try:
            self._connection = sqlite3.connect(self.db_name)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON;")
            self._cursor = self._connection.cursor()
            return self
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        # commits changes and closes the connection
        if self._connection:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
            self._connection.close()
        self._connection = None
        self._cursor = None

    def begin_transaction(self):
        # starts an explicit transaction 
        if self._connection:
            self._connection.execute("BEGIN")

    def commit_transaction(self):
        # commits the explicit transacton
        if self._connection:
            self._connection.commit()

    def rollback_transaction(self):
        # rolls back the explicit transaction
        if self._connection:
            self._connection.rollback()

    def execute(self, query, params=()):
        # executes a single SQL query
        if self._cursor is None:
            raise AttributeError("Cursor is not initialized. Ensure DatabaseManager is used within a 'with' block.")
        self._cursor.execute(query, params)
        return self._cursor.lastrowid

    def executemany(self, query, param_list):
        # Executes a SQL query against all parameter sequences or mappings
        if self._cursor is None:
            raise AttributeError("Cursor is not initialized. Ensure DatabaseManager is used within a 'with' block.")
        self._cursor.executemany(query, param_list)

    def fetchall(self, query, params=()):
        # fetches all rows resulting from a query
        if self._cursor is None:
            raise AttributeError("Cursor is not initialized. Ensure DatabaseManager is used within a 'with' block.")
        self._cursor.execute(query, params)
        return self._cursor.fetchall()

    def fetch_one(self, query, params=()):
        # fetches a single row resulting from a query
        if self._cursor is None:
            raise AttributeError("Cursor is not initialized. Ensure DatabaseManager is used within a 'with' block.")
        self._cursor.execute(query, params)
        return self._cursor.fetchone()