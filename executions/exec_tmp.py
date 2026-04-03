import pandas as pd
import sys

file_path = r"C:\Users\tdoan\GitHub\Calyx-Ai.net\Project-Tracker.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    print("----- DASHBOARD -----")
    df_dash = xl.parse("Dashboard", skiprows=3) # Row 3 in 0-index was the header
    print(df_dash.head(10).to_string())
    
    print("\n----- SPRINT PLAN -----")
    df_sprint = xl.parse("Sprint Plan")
    print(df_sprint.head(15).to_string())
    
except Exception as e:
    print(f"Error reading Excel: {e}")
