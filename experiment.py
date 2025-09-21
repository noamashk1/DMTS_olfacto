import json
from typing import List, Dict, Any
import trial
from level import Level
from mouse import Mouse
from finite_state_machine import FiniteStateMachine
import tkinter as tk
from tkinter import simpledialog
import threading
import GUI_sections
import live_window
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import state_io
import memory_monitor
import time
import subprocess
import shutil


###  use those commands on terminal to push changes to git

# cd /home/educage/Projects/DMTS_olfacto
# git add .
# git commit -m ""
# git push
# 

###
class Experiment:
    def __init__(self, exp_name, mice_dict: dict[str, Mouse] = None, levels_df = None, exp_params = None, auto_start = False, user_email = None):
        """
        Creating a new experiment
        auto_start: if True, the experiment will start automatically if parameters are available
        """
        
        self.exp_params = exp_params
        self.fsm = None
        self.live_w = None
        self.levels_df = levels_df
        self.mice_dict = mice_dict
        self.results = []
        self.stim_length = 2
        self.txt_file_name = exp_name
        self.txt_file_path = None
        self.exp_folder_path =None
        self.auto_start = auto_start
        if user_email is None:
            self.user_email = "noam4596@gmail.com"  # Email for memory warnings
        else:
            self.user_email = user_email
        # Creating experiment folder
        self.new_txt_file(self.txt_file_name)
        self.remote_folder = "/mnt/labfolder/Noam/results"
        self.GPIO_dict = {
                1: 5,
                2: 6,
                3: 13,
                4: 19,
                5: 26,
                6: 21,
                7: 20,
                8: 16
            }
        self.root = tk.Tk()
        self.GUI = GUI_sections.TkinterApp(self.root, self, exp_name = self.txt_file_name)
        
        # If there are loaded parameters, update the GUI
#         if self.auto_start and self.exp_params and self.levels_df is not None and self.mice_dict:
#             print("[DEBUG] Updating GUI with loaded data...")
#             self.GUI.update_gui_with_loaded_data(self.levels_df, self.mice_dict, self.exp_params)
        
        # Starting memory monitoring system
        self.memory_monitor = memory_monitor.MemoryMonitor(self, threshold_mb=450)
        self.memory_monitor.start_monitoring()
        
        # Starting the experiment
        self.run_experiment()
        self.root.mainloop()
        self.root.destroy()

    def set_parameters(self, parameters):
        """This method is called by App when the OK button is pressed."""
        self.exp_params = parameters
        print("\nParameters set in Experiment:\n", self.exp_params,"\n")

    def set_mice_dict(self, mice_dict):
        """This method is called by App when the OK button is pressed."""
        self.mice_dict = mice_dict

    def set_levels_df(self, levels_df):
        """This method is called by App when the OK button is pressed."""
        self.levels_df = levels_df
        

    def new_txt_file(self, filename):
        # Build the path: ./experiments/filename/
        folder_path = os.path.join(os.getcwd(), "experiments", filename)
        self.exp_folder_path = folder_path
        os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists

        self.txt_file_path = os.path.join(folder_path,filename+".txt")  
        # Create the file only if it does not exist; do not truncate if it exists
        if not os.path.exists(self.txt_file_path):
            with open(self.txt_file_path, 'w') as file:
                pass

    def save_minimal_state(self):
        """
        Saving the minimal state of the experiment
        """
        if self.exp_params and self.levels_df is not None and self.mice_dict:
            state_io.save_minimal_state(
                self.txt_file_name,
                self.exp_params,
                self.levels_df,
                self.mice_dict,
                self.txt_file_name,
                self.txt_file_path,
                self.user_email
            )
        else:
            print("Cannot save state - missing required data")

    def get_memory_status(self):
        """Returning the current memory status"""
        if hasattr(self, 'memory_monitor'):
            return self.memory_monitor._get_current_memory_mb()
        return 0
    
    def stop_memory_monitoring(self):
        """Stopping memory monitoring"""
        if hasattr(self, 'memory_monitor'):
            self.memory_monitor.stop_monitoring()
    
    def restart_memory_monitoring(self):
        """Restarting memory monitoring"""
        if hasattr(self, 'memory_monitor'):
            self.memory_monitor.start_monitoring()

    def run_experiment(self):
        # Check if there are parameters or if this is auto-start
        if self.exp_params is None and not self.auto_start:
            self.root.after(100, lambda: self.run_experiment())  # Check again after 100ms
        else:
            # Continue with the experiment once parameters are set
            # Start experiment in a separate thread to keep the GUI responsive
            threading.Thread(target=self.start_experiment, daemon=True).start()

    def start_experiment(self):
        # This method runs the actual experiment (on a separate thread)
        try:
            # If this is auto-start, open the live window
            if self.auto_start:
                self.root.after(200, self.run_live_window)
                
            # Create FSM only after live_w is created
            if self.auto_start and (self.live_w is None):
                print("[DEBUG] WARNING: LiveWindow not available, waiting...")
                # Additional wait and another attempt
                time.sleep(1)
                self.open_live_window()
                
            if self.auto_start and (self.live_w is None):
                print("[DEBUG] ERROR: Failed to create LiveWindow, cannot continue")
                return
                
            fsm = FiniteStateMachine(self)
            self.fsm = fsm
            print("FSM created: The experiment has begun.")
            
        except Exception as e:
            print(f"[DEBUG] Error in start_experiment: {e}")
            import traceback
            traceback.print_exc()

    def run_live_window(self):
        self.root.after(0, self.open_live_window)
        
    def open_live_window(self):
        if self.live_w is None:
            try:
                self.live_w = live_window.LiveWindow()
                print("LiveWindow created successfully")
                # Short wait to ensure the window is created successfully
                time.sleep(0.5)
            except Exception as e:
                print(f"[DEBUG] Error creating LiveWindow: {e}")
                self.live_w = None
#         else:
#             print("[DEBUG] LiveWindow already exists")
        
        # Check that live_w was indeed created
        if self.live_w is None:
            print("[DEBUG] WARNING: LiveWindow creation failed!")

    def change_mouse_level(self, mouse: Mouse, new_level: Level):
        mouse.update_level(new_level)

    def save_results(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)

    def create_GPIO_dict(self):

        def save_and_close():
            temp_dict = {}
            for idx, entry in enumerate(gpio_entries):
                index = idx + 1
                gpio_val = entry.get().strip()
                if not gpio_val.isdigit():
                    messagebox.showerror("Input Error", f"GPIO value at row {index} must be a number.")
                    return
                temp_dict[index] = int(gpio_val)
            self.GPIO_dict = temp_dict
            print(self.GPIO_dict)
            top.destroy()

        def add_row():
            row_idx = len(gpio_entries)
            if row_idx >= 32:
                messagebox.showwarning("Limit", "Maximum 32 rows allowed.")
                return
            idx_label = tk.Label(table_frame, text=str(row_idx + 1), width=10)
            idx_label.grid(row=row_idx + 1, column=0, padx=5, pady=2)
            gpio_entry = tk.Entry(table_frame, width=10)
            gpio_entry.grid(row=row_idx + 1, column=1, padx=5, pady=2)
            gpio_entry.insert(0, "")
            gpio_entries.append(gpio_entry)

        # Create the popup window
        top = tk.Toplevel(self.root)
        top.title("Set GPIO Mapping")
        top.geometry("250x350")
        table_frame = tk.Frame(top)
        table_frame.pack(padx=10, pady=10)

        # Table headers
        tk.Label(table_frame, text="Index", font=("Arial", 10, "bold"), width=10).grid(row=0, column=0, padx=5, pady=2)
        tk.Label(table_frame, text="GPIO Number", font=("Arial", 10, "bold"), width=10).grid(row=0, column=1, padx=5, pady=2)

        gpio_entries = []
        # Fill with current values from self.GPIO_dict (sorted by index)
        for i, idx in enumerate(sorted(self.GPIO_dict.keys())):
            gpio_num = self.GPIO_dict[idx]
            idx_label = tk.Label(table_frame, text=str(idx), width=10)
            idx_label.grid(row=i + 1, column=0, padx=5, pady=2)
            gpio_entry = tk.Entry(table_frame, width=10)
            gpio_entry.grid(row=i + 1, column=1, padx=5, pady=2)
            gpio_entry.insert(0, str(gpio_num))
            gpio_entries.append(gpio_entry)

        # Add row button
        add_btn = tk.Button(top, text="Add Row", command=add_row)
        add_btn.pack(pady=5)

        # Save button
        save_btn = tk.Button(top, text="Save", command=save_and_close)
        save_btn.pack(pady=5)
            
    def upload_data(self):
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "mount", "-a"], check=True)
        src = self.exp_folder_path
        dst = os.path.join(self.remote_folder, os.path.basename(src))
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print("data updated")

if __name__ == "__main__":
    import sys
    
    # Check if this is a restart
    restart_mode = False
    restart_exp_name = None
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--restart":
        if len(sys.argv) > 2:
            restart_exp_name = sys.argv[2]
            restart_mode = True
        else:
            print("Usage: python experiment.py --restart <experiment_name>")
            sys.exit(1)
    
    # If this is a restart, try to load the state
    if restart_mode and restart_exp_name:
        print(f"Attempting to restart experiment: {restart_exp_name}")
        
        # Loading the state
        state_data = state_io.load_minimal_state(restart_exp_name)
        
        if state_data:
            print("State loaded successfully, starting experiment...")
            # Creating the experiment with loaded parameters
            experiment = Experiment(
                exp_name=restart_exp_name,
                mice_dict=state_data['mice_dict'],
                levels_df=state_data['levels_df'],
                exp_params=state_data['exp_params'],
                auto_start=True,
                user_email=state_data['user_email']
            )
        else:
            print(f"Failed to load state for {restart_exp_name}")
            sys.exit(1)
    else:
        # Normal startup - creating a new experiment folder
        created_folder_name = None

        def create_experiment_folder():
            global created_folder_name

            exp_name = entry.get().strip()
            if not exp_name:
                messagebox.showwarning("Input Error", "Please enter a valid experiment name.")
                return

            date_str = datetime.now().strftime("%d_%m_%Y")
            base_dir = "experiments"
            os.makedirs(base_dir, exist_ok=True)

            folder_name = f"{exp_name}_{date_str}"
            full_path = os.path.join(base_dir, folder_name)

            if os.path.exists(full_path):
                # Check if there is a saved state available
                if state_io.check_if_restart_available(folder_name):
                    answer = messagebox.askyesno("Restart Available", 
                        f"The folder '{folder_name}' exists and has a saved state.\nDo you want to restart the experiment?")
                    if answer:
                        # Restart
                        created_folder_name = folder_name
                        root.destroy()
                        return
                
                # Ask if they want to use the existing folder
                answer = messagebox.askyesno("Folder Exists", f"The folder '{folder_name}' already exists.\nDo you want to use it?")
                if not answer:
                    return  # Do nothing, let the user change the name or cancel
            else:
                os.makedirs(full_path)

            created_folder_name = folder_name
            root.destroy()

        # Creating the GUI window
        root = tk.Tk()
        root.title("Experiment Setup")
        root.geometry("300x120")

        tk.Label(root, text="Enter Experiment Name:").pack(pady=10)

        entry = tk.Entry(root, width=30)
        entry.insert(0, "exp")  # Default text
        entry.pack()

        tk.Button(root, text="Create Folder", command=create_experiment_folder).pack(pady=10)

        root.mainloop()

        # Creating the experiment
        if created_folder_name:
            experiment = Experiment(exp_name=created_folder_name)

