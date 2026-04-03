import os
import re
import pandas as pd
import openpyxl
from datetime import datetime
import sys

# Change directory to the root of the website
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "executions"))
import deploy_now
import deploy_cpanel

def map_backlog_to_sprint(file_path):
    # Reads Backlog and computes sprint statuses mathematically
    xl = pd.ExcelFile(file_path)
    df_backlog = xl.parse("Backlog")
    
    sprint_status_map = {}
    
    for sprint_val, group in df_backlog.groupby('Sprint'):
        if pd.isna(sprint_val):
            continue
            
        sprint = None
        try:
            sprint = int(float(sprint_val))
        except:
            continue
            
        statuses = group['Status'].astype(str).str.strip().tolist()
        # Drop nan and empty
        valid_statuses = [s for s in statuses if s and s.lower() != 'nan' and s.lower() != 'none']
        
        if not valid_statuses:
            sprint_status_map[sprint] = 'Not Started'
            continue
            
        all_done = all(s in ['Done', 'Completed'] for s in valid_statuses)
        any_in_progress = any(s in ['In Progress', 'Done', 'Completed'] for s in valid_statuses)
        
        if all_done:
            sprint_status_map[sprint] = 'Completed'
        elif any_in_progress:
            sprint_status_map[sprint] = 'In Progress'
        else:
            sprint_status_map[sprint] = 'Not Started'
            
    return sprint_status_map

def update_calyx_progress():
    print(f"[{datetime.now()}] Updating Calyx AI Project Tracker...")
    
    file_path = r"C:\Users\tdoan\GitHub\Calyx-Ai.net\Project-Tracker.xlsx"
    index_html_path = os.path.join(base_dir, "index.html")
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return False

    try:
        # 1. Math computation from Backlog
        sprint_status_map = map_backlog_to_sprint(file_path)
        print("Computed Sprint Statuses from Backlog:", sprint_status_map)

        # 2. Open Workbook with openpyxl to edit cells losslessly
        wb = openpyxl.load_workbook(file_path)
        
        ws_sprint = wb["Sprint Plan"]
        # Update Sprint Plan and collect Phase lists
        phase_sprint_statuses = {} # Dict of Phase -> List of Sprint Statuses
        
        for r in range(2, 50):
            val_sprint = ws_sprint.cell(row=r, column=1).value
            val_phase = ws_sprint.cell(row=r, column=3).value
            
            if val_sprint is None:
                continue
                
            try:
                sprint_num = int(float(val_sprint))
            except:
                continue
                
            # Update Sprint Plan Status column (7)
            if sprint_num in sprint_status_map:
                new_status = sprint_status_map[sprint_num]
                ws_sprint.cell(row=r, column=7).value = new_status
            else:
                new_status = 'Not Started'
                ws_sprint.cell(row=r, column=7).value = new_status
                
            # Collect for Phase rollup
            if val_phase:
                phase_str = str(val_phase).replace("Phase", "").strip()
                try:
                    phase_num = int(float(phase_str))
                    if phase_num not in phase_sprint_statuses:
                        phase_sprint_statuses[phase_num] = []
                    phase_sprint_statuses[phase_num].append(new_status)
                except:
                    pass

        # Calculate Phase statuses
        phase_status_map = {}
        for phase_num, statuses in phase_sprint_statuses.items():
            if all(s == 'Completed' for s in statuses):
                phase_status_map[phase_num] = 'Completed'
            elif any(s in ['In Progress', 'Completed'] for s in statuses):
                phase_status_map[phase_num] = 'In Progress'
            else:
                phase_status_map[phase_num] = 'Not Started'
                
        print("Computed Phase Statuses:", phase_status_map)
        
        # Update Dashboard
        ws_dash = wb["Dashboard"]
        # Also update the "Last Updated" text
        for r in range(1, 4):
            if str(ws_dash.cell(row=r, column=1).value).startswith("Last Updated:"):
                ws_dash.cell(row=r, column=1).value = f"Last Updated: {datetime.now().strftime('%B %d, %Y')}"
                
        for r in range(5, 50):
            val_phase = ws_dash.cell(row=r, column=1).value
            if val_phase is None:
                continue
                
            try:
                phase_num = int(float(val_phase))
                if phase_num in phase_status_map:
                    ws_dash.cell(row=r, column=4).value = phase_status_map[phase_num]
            except:
                continue

        # Save workbook
        try:
            wb.save(file_path)
            print("Saved updated Project-Tracker.xlsx.")
        except PermissionError:
            print(f"Warning: Could not save to {file_path} because it is currently open in Excel. Website calculation will proceed with computed values.")
        except Exception as e:
            print(f"Warning: Could not save Excel file: {e}")
        
        # 3. Determine explicit active Sprint and Phase for Website
        total_phases = 6
        current_phase = 1
        
        # Find active phase
        in_prog_phases = [k for k, v in phase_status_map.items() if v == 'In Progress']
        if in_prog_phases:
            current_phase = max(in_prog_phases) # If multiple are somehow parallel, take the highest
        else:
            comp_phases = [k for k, v in phase_status_map.items() if v == 'Completed']
            if comp_phases:
                current_phase = max(comp_phases)
                
        phase_pct = min(100, int((current_phase / total_phases) * 100))

        # Find active sprint
        total_sprints_rep = 16 
        current_sprint = 1
        
        # Any that are 'In progress'
        in_prog_sprints = [k for k, v in sprint_status_map.items() if v == 'In Progress']
        if in_prog_sprints:
            current_sprint = max(in_prog_sprints)
        else:
            comp_sprints = [k for k, v in sprint_status_map.items() if v == 'Completed']
            if comp_sprints:
                max_comp = max(comp_sprints)
                # If sprint 8 is completed, the user is starting Sprint 9
                current_sprint = min(total_sprints_rep, max_comp + 1)
                
        sprint_pct = min(100, int((current_sprint / total_sprints_rep) * 100))
        
        print(f"Website values -> Phase: {current_phase}/{total_phases} ({phase_pct}%), Sprint: {current_sprint}/{total_sprints_rep} ({sprint_pct}%)")

        # 4. Modify HTML
        with open(index_html_path, "r", encoding="utf-8") as f:
            html = f.read()

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
        
        # 5. Trigger Deployment
        print("Triggering deployment with deploy_now...")
        os.chdir(base_dir) # ensure we are in the repo root for git commands
        deploy_now.deploy_cpanel_git()
        
        return True

    except Exception as e:
        print(f"Error during update process: {e}")
        return False

if __name__ == "__main__":
    update_calyx_progress()
