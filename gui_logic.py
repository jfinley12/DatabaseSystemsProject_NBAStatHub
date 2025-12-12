# gui_logic.py
# creator: Jacob Finley (jf118221@ohio.edu)
# the use of tkinter: to create a simple GUI for the NBA Analytics Hub Demo application and dislpay results of analytical queries
# the gui will have user log in and registration functionality, as well as buttons to run the analytical queries and display results in a text area
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
from app_features import register_user, login_user, submit_player_prediction, \
                         get_top_advanced_stat, get_most_injured_players, \
                         get_team_demographics_summary, get_current_user, format_results

class NBAAnalyticsApp:
    def __init__(self, master):
        # initialization of the main Tkinter window
        self.master = master
        master.title("NBA Analytics Hub Demo")
        master.geometry("1000x800")
        
        # display of the current user status (whether they are logged in or not)
        self.status_var = tk.StringVar(master, value="Status: Logged Out")
        self.status_label = tk.Label(master, textvariable=self.status_var, fg="blue")
        self.status_label.pack(pady=10)

        # Output Text Area for results and logs
        self.output_text = scrolledtext.ScrolledText(master, height=15, width=120, state='disabled', wrap=tk.WORD)
        self.output_text.pack(pady=10, padx=10)
        
        # Sectioning and Framing for the different functionalities of the gui
        
        # Frame 1: authentication and and writing to the user account and prediction tables
        auth_frame = tk.LabelFrame(master, text="1. User Auth & Write Actions (CRUD)", padx=10, pady=10)
        auth_frame.pack(padx=10, pady=5, fill="x")
        self._setup_auth_frame(auth_frame)

        # Frame 2: Analytical Views for each of the kaggle analytical queries
        analytics_frame = tk.LabelFrame(master, text="2. Analytical Views (SQL Power)", padx=10, pady=10)
        analytics_frame.pack(padx=10, pady=5, fill="x")
        self._setup_analytics_frame(analytics_frame)
        
        self._log_output("Welcome to the NBA Analytics Hub. Please register or log in.")

    def _log_output(self, message):
        # helper function: append messages to the ScrolledText widget that is used for output display
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    # set up of the authentication and user action frame    
    def _setup_auth_frame(self, frame):
        tk.Label(frame, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.email_entry = tk.Entry(frame, width=20)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(frame, width=20, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(frame, text="Register (WRITE)", command=self._handle_register).grid(row=0, column=2, padx=10)
        tk.Button(frame, text="Login (AUTH)", command=self._handle_login).grid(row=1, column=2, padx=10)

        tk.Label(frame, text="Prediction Player Name:").grid(row=0, column=4, padx=5)
        self.pred_player_entry = tk.Entry(frame, width=20)
        self.pred_player_entry.insert(0, "LeBron James") 
        self.pred_player_entry.grid(row=0, column=5, padx=5)

        tk.Label(frame, text="Prediction Type (e.g., MVP):").grid(row=1, column=4, padx=5)
        self.pred_type_entry = tk.Entry(frame, width=20)
        self.pred_type_entry.insert(0, "MVP_PRED")
        self.pred_type_entry.grid(row=1, column=5, padx=5)
        
        tk.Button(frame, text="Submit Prediction (WRITE/TXN)", command=self._handle_prediction).grid(row=0, column=6, rowspan=2, padx=10)

    # the data handling for the registration, login, and prediction submission buttons
    def _handle_register(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        success, message = register_user(email, password)
        if success: messagebox.showinfo("Success", message)
        else: messagebox.showerror("Error", message)
        self._log_output(f"Registration Attempt: {message}")

    def _handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        success, message = login_user(email, password)
        if success: 
            self.status_var.set(f"Status: Logged In (User ID: {get_current_user()})")
            messagebox.showinfo("Success", message)
        else: messagebox.showerror("Error", message)
        self._log_output(f"Login Attempt: {message}")
        
    def _handle_prediction(self):
        player_name = self.pred_player_entry.get()
        pred_type = self.pred_type_entry.get()
        success, message = submit_player_prediction(player_name, pred_type, "1st Place") 
        if success: messagebox.showinfo("Success", message)
        else: messagebox.showerror("Error", message)
        self._log_output(f"Prediction Submission: {message}")

    # the three Analytical Views
    
    def _setup_analytics_frame(self, frame):

        # ANALYTICAL VIEW 1: finding the top 5 players for the fixed advanced stat 'orb_percent'
        tk.Button(frame, text="Top 5 Players by ORB%", 
                  command=self._display_top_orb).grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        # ANALYTICAL VIEW 2: finding the top 5 most frequently injured players
        tk.Button(frame, text="Top 5 Most Injured Players", 
                  command=self._display_most_injured).grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        # ANALYTICAL VIEW 3: team demographics summary (top 10 cities by income and population)
        tk.Button(frame, text="Top 10 City Demographics Summary", 
                  command=self._display_demographics).grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    # functino to display the results of each of the analytical queries described before 
    def _display_top_orb(self):

        # orb_percent is the fixed stat abbreviation used in app_features.py
        stat_abbr = 'orb_percent' 
        self._log_output(f"--- Running Analytical Query 1: Top 5 players by {stat_abbr} ---")
        data, header = get_top_advanced_stat(stat_abbr=stat_abbr)
        output = format_results(header, data)
        self._log_output("Query Results:")
        self._log_output(output)

    def _display_most_injured(self):
        self._log_output("--- Running Analytical Query 2: Top 5 Most Frequently Injured Players ---")
        data, header = get_most_injured_players()
        output = format_results(header, data)
        self._log_output("Query Results:")
        self._log_output(output)

    def _display_demographics(self):
        self._log_output("--- Running Analytical Query 3: Top 10 City Demographics Summary (Income/Population) ---")
        data, header = get_team_demographics_summary()
        output = format_results(header, data)
        self._log_output("Query Results:")
        self._log_output(output)
        

# execution entry point
def run_app():
    root = tk.Tk()
    app = NBAAnalyticsApp(root)
    root.mainloop()

if __name__ == '__main__':
    run_app()