import os
import re
import pandas as pd
from datetime import datetime
import sys

# Change directory to the root of the website
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "executions"))
import deploy_now

def update_calyx_progress():
    print(f"[{datetime.now()}] Reading Calyx AI Project Tracker...")
    
    file_path = r"C:\Users\tdoan\GitHub\Calyx-Ai.net\Project-Tracker.xlsx"
    index_html_path = os.path.join(base_dir, "index.html")
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return False

    try:
        xl = pd.ExcelFile(file_path)
        
        # 1. Parse Phase
        df_dash = xl.parse("Dashboard", skiprows=3)
        df_dash.columns = df_dash.iloc[0] # First row is headers
        df_dash = df_dash[1:]             # Drop the header row itself
        # Drop rows where Phase is NaN or 'Phase' string
        df_dash = df_dash[pd.to_numeric(df_dash['Phase'], errors='coerce').notnull()]
        
        total_phases = 6
        current_phase = 1
        
        in_progress_phases = df_dash[df_dash['Status'] == 'In Progress']
        if not in_progress_phases.empty:
            current_phase = int(in_progress_phases.iloc[0]['Phase'])
        else:
            completed_phases = df_dash[df_dash['Status'] == 'Completed']
            if not completed_phases.empty:
                current_phase = int(completed_phases['Phase'].max())
        
        phase_pct = min(100, int((current_phase / total_phases) * 100))

        # 2. Parse Sprint
        df_sprint = xl.parse("Sprint Plan")
        df_sprint = df_sprint[pd.to_numeric(df_sprint['Sprint'], errors='coerce').notnull()]
        
        # User requested representation out of 16 weeks/sprints
        total_sprints_rep = 16 
        current_sprint = 1
        
        in_progress_sprints = df_sprint[df_sprint['Status'] == 'In Progress']
        if not in_progress_sprints.empty:
            current_sprint = int(in_progress_sprints.iloc[-1]['Sprint'])
        else:
            completed_sprints = df_sprint[df_sprint['Status'] == 'Completed']
            if not completed_sprints.empty:
                current_sprint = int(completed_sprints['Sprint'].max())
                
        sprint_pct = min(100, int((current_sprint / total_sprints_rep) * 100))
        
        print(f"Extracted -> Phase: {current_phase}/{total_phases} ({phase_pct}%), Sprint: {current_sprint}/{total_sprints_rep} ({sprint_pct}%)")

        # 3. Modify HTML
        with open(index_html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Regex replacements
        html = re.sub(
            r'<!-- CALYX_PHASE_TEXT_START -->.*?<!-- CALYX_PHASE_TEXT_END -->',
            f'<!-- CALYX_PHASE_TEXT_START --><span id="calyx-phase-text" style="color: #bbb;">Phase {current_phase} of {total_phases}</span><!-- CALYX_PHASE_TEXT_END -->',
            html,
            flags=re.DOTALL
        )
        
        html = re.sub(
            r'<!-- CALYX_PHASE_BAR_START -->.*?<!-- CALYX_PHASE_BAR_END -->',
            f'<!-- CALYX_PHASE_BAR_START --><div id="calyx-phase-bar" style="height: 100%; width: {phase_pct}%; background: var(--accent); transition: width 1s ease-in-out; border-radius: 3px;"></div><!-- CALYX_PHASE_BAR_END -->',
            html,
            flags=re.DOTALL
        )
        
        html = re.sub(
            r'<!-- CALYX_SPRINT_TEXT_START -->.*?<!-- CALYX_SPRINT_TEXT_END -->',
            f'<!-- CALYX_SPRINT_TEXT_START --><span id="calyx-sprint-text" style="color: #bbb;">Sprint {current_sprint} of {total_sprints_rep}</span><!-- CALYX_SPRINT_TEXT_END -->',
            html,
            flags=re.DOTALL
        )
        
        html = re.sub(
            r'<!-- CALYX_SPRINT_BAR_START -->.*?<!-- CALYX_SPRINT_BAR_END -->',
            f'<!-- CALYX_SPRINT_BAR_START --><div id="calyx-sprint-bar" style="height: 100%; width: {sprint_pct}%; background: linear-gradient(90deg, var(--accent) 0%, rgba(255,255,255,0.8) 100%); transition: width 1s ease-in-out; border-radius: 3px;"></div><!-- CALYX_SPRINT_BAR_END -->',
            html,
            flags=re.DOTALL
        )

        with open(index_html_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Updated index.html successfully.")
        
        # 4. Trigger Deployment
        print("Triggering deployment with deploy_now...")
        os.chdir(base_dir) # ensure we are in the repo root for git commands
        deploy_now.deploy_cpanel_git()
        
        return True

    except Exception as e:
        print(f"Error during update process: {e}")
        return False

if __name__ == "__main__":
    update_calyx_progress()
