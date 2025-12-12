# DatabaseSystemsProject_NBAStatHub
This repository houses the final project for CS 3620 (Database Systems), implementing a functional NBA Analytics Hub using Python and SQLite.

The project encompasses a full-stack database application including schema definition, data import, and a graphical user interface (GUI) for interactive analysis.

---

## Project Architecture & Files

| File Name | Description | Role/Layer |
| :--- | :--- | :--- |
| **`app_main.py`** | The main application driver. Initializes the database schema, runs data import, and launches the Tkinter GUI. | Entry Point |
| **`app_features.py`** | Contains all business logic, user authentication, and the SQL queries for the analytical views. | Business Logic & Query Handler |
| **`data_importer.py`** | Handles the ETL process: cleans, transforms, and loads raw CSV data into the SQLite database tables. | ETL/Data Loader |
| **`db_manager.py`** | The database abstraction layer. Provides a robust context manager for handling connection opening, closing, and explicit transactions (commit/rollback). | Database Wrapper |
| **`gui_logic.py`** | Builds and controls the Tkinter GUI, managing user input and acting as the interface to the `app_features.py` logic. | Presentation/GUI |
| **`schema.sql`** | Defines the entire database structure using SQL DDL (CREATE TABLE statements, keys, and constraints). | Schema Definition |
| **`nba_stats_hub.db`** | The resulting SQLite database file after setup and data import. | Database Storage |

---

## 💾 Data Sources & Setup

### Data Source Links
The project integrates data from three external sources. The downloaded CSV files must be placed inside a folder named `datasets/` in the project root.

1.  **Database 1 (Advanced Stats):** NBA player/season performance metrics.
                                  ** Link: https://www.kaggle.com/datasets/sumitrodatta/nba-aba-baa-stats?resource=download
2.  **Database 2 (Injury Records):** NBA player injury records (since 2010).
                                  ** Link: https://www.kaggle.com/datasets/ghopkins/nba-injuries-2010-2018
3.  **Database 3 (Demographics):** US City incomes and population by zip code.
                                ** Link: https://www.kaggle.com/datasets/jeremylarcher/american-house-prices-and-demographics-of-top-cities

### How to Run

1.  Ensure Python 3 and the necessary libraries (e.g., `pandas`, `tkinter`, `sqlite3`) are installed.
2.  Place the raw CSV files into the `datasets/` folder.
3.  Run the main application driver:
    ```bash
    python3 app_main.py 
    ```

---

## Analytical Views (Interactive SQL)

The application provides three interactive analytical views, each powered by a complex SQL query utilizing the imported data:

| View # | Query Purpose | Tables Used |
| :--- | :--- | :--- |
| **View 1** | **Top 5 Advanced Stat:** Ranks the 5 highest players by a fixed advanced stat (`orb_percent`). | `stat_player_bio`, `fact_player_advanced_stats` |
| **View 2** | **Injury Frequency:** Outputs the player who appears as 'Relinquished' (injured) the most times. | `stat_player_bio`, `bg_injury_report` |
| **View 3** | **Demographics Summary:** Outputs the median household income and population for the top 10 cities imported. | `ref_city`, `bg_city_demographics` |

---

## 🖼️ Supporting Documentation

* **Screenshots and Demo:** This folder holds the screenshots and demo artifacts submitted during project checkpoints.
* **Video Demo:** appears within the repo as 'GUI_demo_finley_jacob.mp4'