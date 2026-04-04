import pandas as pd
import re

file_path = r"C:\Users\tdoan\GitHub\Calyx-Ai.net\Project-Tracker.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    df_backlog = xl.parse("Backlog")
    
    # calculate total sprints
    sprints = pd.to_numeric(df_backlog['Sprint'], errors='coerce').dropna()
    total_sprints = int(sprints.max()) if not sprints.empty else 0
    print(f"Total Sprints: {total_sprints}")
    
    # calculate phases
    def extract_phase(epic_str):
        if pd.isna(epic_str):
             return None
        match = re.search(r'Phase\s+(\d+)', str(epic_str), re.IGNORECASE)
        if match:
             return int(match.group(1))
        return None
        
    df_backlog['Phase_Num'] = df_backlog['Epic'].apply(extract_phase)
    phases = df_backlog['Phase_Num'].dropna()
    total_phases = int(phases.max()) if not phases.empty else 0
    print(f"Total Phases: {total_phases}")
    
except Exception as e:
    print(f"Error: {e}")
