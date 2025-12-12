# app_main.py
# creator: Jacob Finley (jf118221@ohio.edu)
import subprocess
import sys
import os

# dependency check and installation
def check_and_install_dependencies():

    # checks if required libraries are installed and installs them using pip if they aren't

    required_packages = ['pandas', 'numpy']
    
    print("Checking and Installing Dependencies...")
    
    # check if packages are available
    try:
        import pandas
        import numpy
        print("Dependencies already satisfied.")
        return
    except ImportError:
        pass # move on to installation

    # install missing packages
    try:
        print(f"Installing missing packages: {', '.join(required_packages)}...")
        
        # use subprocess to run pip installation
        subprocess.check_call([sys.executable, "-m", "pip", "install", *required_packages])
        
        print("Installation successful!")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies via pip. Please ensure pip is installed and accessible. {e}")
        # exit if the dependencies cannot be met
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during dependency installation: {e}")
        sys.exit(1)


# Main Application Execution
def main():

    # 1. Run the dependency check first using the function we defined above
    check_and_install_dependencies()
    
    # now that dependencies are confirmed, safely import other modules from the other python files
    from db_manager import setup_database
    from data_importer import run_importer
    from gui_logic import run_app

    print("\nInitializing NBA Analytics Hub Application...")
    
    # 2. Setup Database and Schema using db_manager.py
    try:
        # This function creates the DB file and applies the schema if it doesn't exist.
        setup_database()
    except Exception as e:
        print(f"FATAL ERROR: Could not set up database schema. Aborting application. {e}")
        return

    # 3. Import Data
    # this function loads the CSV files into the database tables.
    # the function will only attempt to import if the necessary files are in the /datasets folder.
    run_importer()
    
    # 4. Start the GUI application by calling run_app from gui_logic.py
    print("\nStarting Tkinter GUI...")
    run_app()

if __name__ == '__main__':
    main()