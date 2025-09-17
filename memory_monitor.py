import psutil
import os
import sys
import threading
import time
import subprocess
import tkinter as tk
import smtplib
from General_functions import send_email


class MemoryMonitor:
    def __init__(self, experiment, threshold_mb=400, check_interval=10*60):
        """
        Memory monitoring system
        experiment: experiment object
        threshold_mb: memory threshold in MB above which a restart will be triggered
        check_interval: how many seconds to check between checks
        """
        self.experiment = experiment
        self.threshold_mb = threshold_mb
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread = None
        self.warning_shown = False  # Flag indicating that the warning has already been shown
        
    def start_monitoring(self):
        """Starts memory monitoring in the background"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print(f"[MemoryMonitor] Memory monitoring started (threshold: {self.threshold_mb}MB)")
    
    def stop_monitoring(self):
        """Stops memory monitoring"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=1)
            print("[MemoryMonitor] Memory monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                current_memory = self._get_current_memory_mb()
                print(f"[MemoryMonitor] Memory usage {current_memory:.1f}MB , threshold {self.threshold_mb}MB")
                
                # Check if memory has reached 100MB below threshold and warning hasn't been shown yet
                if not self.warning_shown and current_memory > (self.threshold_mb - 100):
                    message = f"""Warning: Memory is approaching the threshold!

                Current usage: {current_memory:.1f}MB
                Threshold: {self.threshold_mb}MB
                
                When the system reaches the threshold, it will restart automatically.
                The experiment will continue with tha same parameters.
                
                Even after an automatic restart, it is advisable to manually restart again. """
                    send_email(to_email = self.experiment.user_email, subject = "WARNING: Memory usage", body = message )
                    self._show_memory_warning(current_memory)
                    self.warning_shown = True
                
                if current_memory > self.threshold_mb:
                    print(f"[MemoryMonitor] WARNING: Memory usage {current_memory:.1f}MB exceeds threshold {self.threshold_mb}MB")
                    self._handle_memory_overflow()
                    break  # Exit the loop after handling overflow
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"[MemoryMonitor] Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _get_current_memory_mb(self):
        """Returns the current memory usage in MB"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Conversion to MB
        except Exception as e:
            print(f"[MemoryMonitor] Error getting memory usage: {e}")
            return 0
    
    def _show_memory_warning(self, current_memory):
        """Shows a warning to the user about approaching the threshold"""
        try:
            # Creating a separate thread to show the message so it doesn't stop the system
            def show_warning():
                try:
                    # Creating a simple warning window using Toplevel instead of Tk
                    warning_window = tk.Toplevel()
                    warning_window.title("Memory Warning")
                    warning_window.geometry("450x250")
                    warning_window.resizable(False, False)
                    warning_window.transient()  # Make it a transient window
                    warning_window.grab_set()   # Make it modal
                    
                    # Handle window close button (X)
                    def on_closing():
                        warning_window.destroy()
                    
                    warning_window.protocol("WM_DELETE_WINDOW", on_closing)
                    
                    # Message in English
                    message = f"""Warning: Memory is approaching the threshold!

Current usage: {current_memory:.1f}MB
Threshold: {self.threshold_mb}MB

When the system reaches the threshold, it will restart automatically."""
                    
                    # Label with the message
                    label = tk.Label(warning_window, text=message, font=("Arial", 12), 
                                   justify=tk.CENTER, wraplength=380)
                    label.pack(pady=20)
                    
                    # OK button with proper command
                    def close_window():
                        warning_window.destroy()
                    
                    ok_button = tk.Button(warning_window, text="OK", command=close_window,
                                        font=("Arial", 12), width=10)
                    ok_button.pack(pady=10)
                    
                    # Positioning the window in the center of the screen
                    warning_window.update_idletasks()
                    x = (warning_window.winfo_screenwidth() // 2) - (warning_window.winfo_width() // 2)
                    y = (warning_window.winfo_screenheight() // 2) - (warning_window.winfo_height() // 2)
                    warning_window.geometry(f"+{x}+{y}")
                    
                    # Showing the window
                    warning_window.lift()
                    warning_window.focus_force()
                    
                    print(f"[MemoryMonitor] Memory warning shown: {current_memory:.1f}MB (threshold: {self.threshold_mb}MB)")
                    
                except Exception as e:
                    print(f"[MemoryMonitor] Error showing warning: {e}")
            
            # Running the message in a separate thread
            warning_thread = threading.Thread(target=show_warning, daemon=True)
            warning_thread.start()
            
        except Exception as e:
            print(f"[MemoryMonitor] Error in _show_memory_warning: {e}")


    def _handle_memory_overflow(self):
        """Handles memory overflow above the threshold"""
        try:
            print("[MemoryMonitor] Handling memory overflow - saving state and restarting...")
            
            # Saving current state
            self.experiment.save_minimal_state()
            
            # Creating restart script
            restart_script = self._create_restart_script()
            
            # Restarting the experiment
            self._restart_experiment(restart_script)
            
        except Exception as e:
            print(f"[MemoryMonitor] Error during memory overflow handling: {e}")
    
    def _create_restart_script(self):
        """Creates a Python script that restarts the experiment"""
        try:
            # Getting the full path to experiment.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            experiment_path = os.path.join(current_dir, "experiment.py")
            
            script_content = f'''#!/usr/bin/env python3
import sys
import os

print("[RestartScript] Starting restart process...")
print("[RestartScript] Current working directory:", os.getcwd())

# Adding the current directory to PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print("[RestartScript] Script directory:", current_dir)
print("[RestartScript] Python interpreter:", sys.executable)

# Checking if experiment.py exists
experiment_path = "{experiment_path}"
if os.path.exists(experiment_path):
    print("[RestartScript] Found experiment.py at:", experiment_path)
else:
    print("[RestartScript] ERROR: experiment.py not found at:", experiment_path)
    sys.exit(1)

print("Restarting experiment automatically...")
print(f"Experiment name: {self.experiment.txt_file_name}")

# Running the experiment with full path
cmd = f'"{sys.executable}" "{experiment_path}" --restart {self.experiment.txt_file_name}'
print("[RestartScript] Running command:", cmd)

# Changing to the correct directory and running
os.chdir(current_dir)
result = os.system(cmd)
print(f"[RestartScript] Command completed with result: {{result}}")
'''
            
            script_path = "restart_experiment.py"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Granting execution permissions to the script
            try:
                os.chmod(script_path, 0o755)
                print(f"[MemoryMonitor] Made script executable: {script_path}")
            except Exception as e:
                print(f"[MemoryMonitor] Warning: Could not make script executable: {e}")
            
            print(f"[MemoryMonitor] Restart script created: {script_path}")
            return script_path
            
        except Exception as e:
            print(f"[MemoryMonitor] Error creating restart script: {e}")
            return None
    
    def _restart_experiment(self, restart_script):
        """Restarts the experiment"""
        try:
            print(f"[MemoryMonitor] Restarting experiment: {self.experiment.txt_file_name}")
            
            # Running the script in the background from the same directory
            if restart_script and os.path.exists(restart_script):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                restart_script_path = os.path.join(current_dir, restart_script)
                
                print(f"[MemoryMonitor] Spawning restart script: {restart_script_path}")
                print(f"[MemoryMonitor] Working directory: {current_dir}")
                
                # Running the script with subprocess instead of os.system
                process = subprocess.Popen([sys.executable, restart_script_path], 
                                        cwd=current_dir)
                
                # Short wait and then exit
                time.sleep(1)
                print("[MemoryMonitor] Restart initiated, exiting current process...")
                
                # Cleaning up resources before exiting
                try:
                    if hasattr(self.experiment, 'live_w') and self.experiment.live_w:
                        try:
                            self.experiment.live_w.root.destroy()
                            time.sleep(0.1)
                        except:
                            pass
                except:
                    pass
                
                try:
                    if hasattr(self.experiment, 'root') and self.experiment.root:
                        try:
                            self.experiment.root.quit()
                            time.sleep(0.1)
                        except:
                            pass
                except:
                    pass
                
                # Small wait to allow GUI to close
                time.sleep(0.5)
                print("[MemoryMonitor] pre os.exist")
                if process.poll() is None:
                    print("Child started successfully")
                # Exiting the current process
                sys.exit(0)#os._exit(0)
            else:
                print("[MemoryMonitor] Restart script not found, cannot restart")
                
        except Exception as e:
            print(f"[MemoryMonitor] Error during experiment restart: {e}")
            import traceback
            traceback.print_exc()
