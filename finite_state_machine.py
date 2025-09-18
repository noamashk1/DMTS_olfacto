import os
import serial
import time
import lgpio
import threading
from trial import Trial
from datetime import datetime
import numpy as np
import sounddevice as sd
import psutil
import gc
import tracemalloc
import objgraph
import logging
import pandas as pd
import shutil
import glob

audio_lock = threading.Lock()
valve_pin = 4 
IR_pin = 27  
lick_pin = 17  
exit_odor_valve_pin = 21

# lgpio setup
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, valve_pin, 0)
lgpio.gpio_claim_input(h, IR_pin)
lgpio.gpio_claim_input(h, lick_pin)
lgpio.gpio_claim_output(h, exit_odor_valve_pin, 0)

ports = glob.glob('/dev/ttyUSB*')
if not ports:
    raise Exception("No USB serial device found!")

port = ports[0] 
ser = serial.Serial(port=port, baudrate=9600, timeout=0.01)
print(f"Connected to {port}")


# ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
#                     timeout=0.01)  # timeo1  # Change '/dev/ttyS0' to the detected port

LOG_FILE = "debug_log.txt"
memory_log_file = "memory_debug_log.txt"

process = psutil.Process(os.getpid())
tracemalloc.start()

def log_open_files_count():
    process = psutil.Process(os.getpid())
    open_files = process.open_files()
    num_open_files = len(open_files)
    file_logger.info(f"Open file descriptors: {num_open_files}")
    
def log_memory_usage_snap(trial_number=None):
    with open(memory_log_file, "a") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"\n--- Memory snapshot at {now} ---"
        if trial_number is not None:
            header += f" (After trial {trial_number})"
        f.write(header + "\n")

        # tracemalloc - מצב זיכרון לפי קוד
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        f.write("Top 10 memory allocations by line:\n")
        for stat in top_stats[:10]:
            f.write(str(stat) + "\n")

        # objgraph - סוגי האובייקטים הכי נפוצים
        f.write("\nTop 10 most common object types:\n")
        common_types = objgraph.most_common_types(limit=10)
        for obj_type, count in common_types:
            f.write(f"{obj_type}: {count}\n")

        # ספירת אובייקטים מסוג Trial (דוגמה)
        count_trial = objgraph.count('Trial')
        f.write(f"\nCount of 'Trial' objects: {count_trial}\n")

        f.write("--- End of snapshot ---\n")

def log_message(message: str):
    """Write message to log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def log_memory_usage(tag=""):
    """Log current memory usage in MB."""
    mem = process.memory_info().rss / (1024 * 1024)  # in MB
    log_message(f"[MEM] {tag} Memory usage: {mem:.2f} MB")

def log_thread_count(tag=""):
    """Log number of active threads."""
    log_message(f"[THREADS] {tag} Active threads: {len(threading.enumerate())}")

def debug_serial_data(data):
    """Log exact raw content of the serial input (including hidden chars)."""
    log_message(f"[SERIAL RAW] {repr(data)}")

class State:
    def __init__(self, name, fsm):
        self.name = name
        self.fsm = fsm
        if self.fsm.exp.live_w.activate_window:
            self.fsm.exp.live_w.deactivate_states_indicators(name)

    def on_event(self, event):
        pass


class IdleState(State):
    def __init__(self, fsm):
        super().__init__("Idle", fsm)
        ser.flushInput()  # clear the data from the serial
        self.fsm.current_trial.clear_trial()
        if self.fsm.exp.live_w.activate_window:
            self.fsm.exp.live_w.update_last_rfid('')
            self.fsm.exp.live_w.update_level('')
            self.fsm.exp.live_w.update_score('')
            self.fsm.exp.live_w.update_trial_value('')

        log_memory_usage("Enter Idle")

        threading.Thread(target=self.wait_for_event, daemon=True).start()

    def wait_for_event(self):
        minutes_passed = 0
        last_log_time = time.time()

        while True:

            if time.time() - last_log_time > 60:
                minutes_passed += 1
                last_log_time = time.time()
                print(f"[IdleState] Waiting for RFID... {minutes_passed} minutes passed")

                if minutes_passed % 30 == 0: 
                    try:
                        self.fsm.exp.upload_data()

                    except PermissionError:
                        print("PermissionError")
                    except FileNotFoundError:
                        print("FileNotFoundError")
                    except Exception as e:
                        print(f"Exception: {e}")
                 
                if minutes_passed % 5 == 0:
                    log_memory_usage("IdleState periodic check")
                    #log_thread_count("IdleState periodic check")
                #if minutes_passed % 10 == 0:
                    #log_memory_usage_snap()
                    #log_open_files_count()

            if ser.in_waiting > 0 and not self.fsm.exp.live_w.pause:
                try:
                    raw_data = ser.readline()
                    mouse_id = raw_data.decode('utf-8').rstrip()
                except Exception as e:
                    print(f"[IdleState] Error reading RFID: {e}")
                    continue

                if self.recognize_mouse(mouse_id):
                    self.fsm.current_trial.update_current_mouse(self.fsm.exp.mice_dict[mouse_id])
                    print("\nmouse: " + self.fsm.exp.mice_dict[mouse_id].get_id())
                    print("Level: " + self.fsm.exp.mice_dict[mouse_id].get_level())
                    

                    if hasattr(self.fsm.exp, 'live_w') and self.fsm.exp.live_w is not None:
                        try:
                            if self.fsm.exp.live_w.activate_window:
                                self.fsm.exp.live_w.update_last_rfid(mouse_id)
                                self.fsm.exp.live_w.update_level(self.fsm.exp.mice_dict[mouse_id].get_level())
                        except Exception as e:
                            print(f"[IdleState] Warning: Could not update GUI: {e}")
                    
                    self.on_event('in_port')
                    break
            else:
                #ser.flushInput()
                time.sleep(0.05)

    def on_event(self, event):
        if event == 'in_port':
            print("Transitioning from Idle to in_port")
            self.fsm.state = InPortState(self.fsm)

    def recognize_mouse(self, data: str):
        if data in self.fsm.exp.mice_dict:
            return True
        else:
            print("mouse ID: '" + data + "' does not exist in the mouse dictionary.")
            return False


class InPortState(State):
    def __init__(self, fsm):
        super().__init__("port", fsm)
        threading.Thread(target=self.wait_for_event, daemon=True).start()

    def wait_for_event(self):
        timeout_seconds = 15  # timeout
        start_time = time.time()

        while lgpio.gpio_read(h, IR_pin) != 1:
            if time.time() - start_time > timeout_seconds:
                print("Timeout in InPortState: returning to IdleState")
                self.on_event("timeout")
                return
            time.sleep(0.09)

        if self.fsm.exp.live_w.activate_window:
            self.fsm.exp.live_w.toggle_indicator("IR", "on")
            time.sleep(0.1)
            self.fsm.exp.live_w.toggle_indicator("IR", "off")
        else:
            time.sleep(0.1)
        print("The mouse entered!")

        if self.fsm.exp.exp_params["start_trial_time"] is not None:
            time.sleep(int(self.fsm.exp.exp_params["start_trial_time"]))
            print("Sleep before start trial")

        self.on_event('IR_stim')

    def on_event(self, event):
        if event == 'IR_stim':
            print("Transitioning from InPort to Trial")
            self.fsm.state = TrialState(self.fsm)
        elif event == 'timeout':
            print("Transitioning from InPort to Idle due to timeout")
            self.fsm.state = IdleState(self.fsm)


class TrialState(State):
    def __init__(self, fsm):
        super().__init__("trial", fsm)
        log_memory_usage("Enter Trial")
        self.got_response = None
        self.stop_threads = False
        self.trial_thread = threading.Thread(target=self.run_trial)
        self.trial_thread.start()

    def run_trial(self):
        self.fsm.current_trial.start_time = datetime.now().strftime('%H:%M:%S.%f')  # Get current time
        self.fsm.current_trial.calculate_stim()
        if self.fsm.exp.live_w.activate_window:
            self.fsm.exp.live_w.update_trial_value(self.fsm.current_trial.current_value)

        # Run odor stimulation first, then receive input
        self.odor_stim()
        self.receive_input()
        if self.fsm.current_trial.score is None:
            self.fsm.current_trial.score = self.evaluate_response()
            print("score: " + self.fsm.current_trial.score)
            if self.fsm.exp.live_w.activate_window:
                self.fsm.exp.live_w.update_score(self.fsm.current_trial.score)

            if self.fsm.current_trial.score == 'hit':
                self.give_reward()
            elif self.fsm.current_trial.score == 'fa':
                self.give_punishment()
        
        log_memory_usage("After Trial")
        self.on_event('trial_over')
        
    def odor_stim(self):
        first_stim_number = self.fsm.current_trial.first_stim_number
        first_odor_gpio = self.fsm.exp.GPIO_dict[first_stim_number]
        second_stim_number = self.fsm.current_trial.second_stim_number
        second_odor_gpio = self.fsm.exp.GPIO_dict[second_stim_number]
        stim_duration = float(self.fsm.exp.exp_params["open_odor_duration"])
        
        try:
            # First odor preparation
            self.valve_on(first_odor_gpio)
            time.sleep(float(self.fsm.exp.exp_params["load_odor_duration"]))
            
            """first odor stim"""
            if self.fsm.exp.live_w.activate_window:
                self.fsm.exp.live_w.toggle_indicator("stim", "on")
            self.valve_on(exit_odor_valve_pin)
            time.sleep(stim_duration)
            self.valve_off(exit_odor_valve_pin)
            self.valve_off(first_odor_gpio)
            if self.fsm.exp.live_w.activate_window:
                self.fsm.exp.live_w.toggle_indicator("stim", "off")
                
            """then sleep between two odors"""
            self.valve_on(second_odor_gpio)
            load_odor_duration = float(self.fsm.exp.exp_params["load_odor_duration"])
            inter_odor_delay = 1.0
            inter_delay = max(load_odor_duration, inter_odor_delay)
            if load_odor_duration > inter_odor_delay:
                print("[WARNING] The inter-odor delay is shorter than the odor load duration. The wait time between odors is increased due to the load time.")
            time.sleep(inter_delay)
                
            """second odor stim"""
            if self.fsm.exp.live_w.activate_window:
                self.fsm.exp.live_w.toggle_indicator("stim", "on")
            self.valve_on(exit_odor_valve_pin)
            time.sleep(stim_duration)
            
        finally:
            self.valve_off(exit_odor_valve_pin)
            self.valve_off(first_odor_gpio)
            self.valve_off(second_odor_gpio)
            if self.fsm.exp.live_w.activate_window:
                self.fsm.exp.live_w.toggle_indicator("stim", "off")
        
        print("Odors completed.")
            

    def receive_input(self):
        if self.fsm.exp.exp_params["lick_time_bin_size"] is not None: # By time
            time.sleep(int(self.fsm.exp.exp_params["lick_time_bin_size"]))
        elif self.fsm.exp.exp_params["lick_time"] == "1": # After stim
            pass

        counter = 0
        self.got_response = False
        previous_lick_state = 0  # Track previous state for edge detection (0 = LOW)
        print('waiting for licks...')
        
        # Use only the post-stimulus time for lick detection
        response_time = int(self.fsm.exp.exp_params["time_to_lick_after_stim"])
        
        start_time = time.time()
        
        while (time.time() - start_time) < response_time:
            current_lick_state = lgpio.gpio_read(h, lick_pin)
            # Only count lick on transition from LOW to HIGH (rising edge)
            if current_lick_state == 1 and previous_lick_state == 0:  # 1 == HIGH, 0 == LOW
                if self.fsm.exp.live_w.activate_window:
                    self.fsm.exp.live_w.toggle_indicator("lick", "on")
                    time.sleep(0.08) #wait for the lick to be visible on the indicator
                self.fsm.current_trial.add_lick_time()
                counter += 1
                
                if self.fsm.exp.live_w.activate_window:
                    self.fsm.exp.live_w.toggle_indicator("lick", "off")
                print("lick detected")

                if counter >= int(self.fsm.exp.exp_params["lick_threshold"]) and not self.got_response:
                    self.got_response = True
                    print('threshold reached')
                    break
            
            # Update previous state for next iteration
            previous_lick_state = current_lick_state
            time.sleep(0.08)

        if not self.got_response:
            print('no response')
        print('num of licks: ' + str(counter))

    def give_reward(self):
        self.valve_on(valve_pin)
        time.sleep(float(self.fsm.exp.exp_params["open_valve_duration"]))
        self.valve_off(valve_pin)

    def valve_on(self, gpio_number):
        print("gpio_number: "+str(gpio_number))
        lgpio.gpio_write(h, gpio_number, 1)
        
    def valve_off(self, gpio_number):
        lgpio.gpio_write(h, gpio_number, 0)

    def give_punishment(self):  # after changing to .npz
        with audio_lock:
            sd.stop()
            try:
                sd.play(self.fsm.noise, samplerate=self.fsm.noise_Fs, blocking=True)  #sd.wait(
            finally:
                sd.stop()
                time.sleep(float(self.fsm.exp.exp_params["timeout_punishment"])) 

    def evaluate_response(self):
        value = self.fsm.current_trial.current_value
        if value == 'go':
            return 'hit' if self.got_response else 'miss'
        elif value == 'no-go':
            return 'fa' if self.got_response else 'cr'
        elif value == 'catch':
            return 'catch - response' if self.got_response else 'catch - no response'

    def on_event(self, event):
        if event == 'trial_over':
            time.sleep(0.5)
            self.fsm.current_trial.write_trial_to_csv(self.fsm.exp.txt_file_path)
            if self.fsm.exp.exp_params['ITI_time'] is None:
                while lgpio.gpio_read(h, IR_pin) == 1:  # 1 == HIGH
                    time.sleep(0.09)
                time.sleep(1)  # wait one sec after exit- before pass to the next trial
            else:
                time.sleep(int(self.fsm.exp.exp_params['ITI_time']))
            print("Transitioning from trial to idle")
            self.fsm.state = IdleState(self.fsm)

class FiniteStateMachine:

    def __init__(self, experiment=None):
        self.exp = experiment
        self.current_trial = Trial(self)
        self.state = IdleState(self)
        self.all_signals_df = None
        
        # Load white noise for punishment
        try:
            with np.load('/home/educage/Projects/DMTS_olfacto/stimuli/white_noise.npz', mmap_mode='r') as z:
                self.noise = z['noise']
                self.noise_Fs = int(z['Fs'])
        except FileNotFoundError:
            print("Warning: white_noise.npz not found, punishment audio will not work")

        # Build a DataFrame with all stimuli referenced by the levels table
        self._build_all_signals_df()

    def _build_all_signals_df(self):
        try:
            if self.exp is None or self.exp.levels_df is None:
                print("[FSM] No levels_df available; skipping all_signals_df build")
                return
            if "Stimulus Path" not in self.exp.levels_df.columns:
                print("[FSM] 'Stimulus Path' column not found in levels_df; skipping all_signals_df build")
                return

            # Collect both "Stimulus Path" and "base Stim" paths, filter out non-strings and empty
            paths = [p for p in self.exp.levels_df["stim path"].tolist() if isinstance(p, str) and len(p) > 0]
            unique_paths = []
            seen = set()
            for p in paths:
                if p not in seen:
                    seen.add(p)
                    unique_paths.append(p)

            rows = []
            for p in unique_paths:
                try:
                    data = None
                    fs = None
                    # Support .npz and .npy
                    if p.lower().endswith('.npz'):
                        with np.load(p, mmap_mode='r') as z:
                            if 'data' in z:
                                data = z['data']
                            elif 'noise' in z:
                                data = z['noise']
                            else:
                                # Fallback: first array-like entry
                                for k in z.files:
                                    arr = z[k]
                                    if isinstance(arr, np.ndarray):
                                        data = arr
                                        break
                            if 'rate' in z:
                                fs = int(z['rate'].item()) if hasattr(z['rate'], 'item') else int(z['rate'])
                            elif 'Fs' in z:
                                fs = int(z['Fs'].item()) if hasattr(z['Fs'], 'item') else int(z['Fs'])
                    else:
                        # .npy or raw array
                        arr = np.load(p, mmap_mode='r')
                        data = arr
                        # No fs info in .npy files; leave as None or set a conventional default if needed

                    if data is None:
                        print(f"[FSM] Warning: could not extract data from {p}")
                        continue

                    rows.append({
                        'path': p,
                        'data': data,
                        'fs': fs
                    })
                except Exception as e:
                    print(f"[FSM] Error loading stimulus '{p}': {e}")

            if rows:
                # Create DataFrame with fixed column order
                self.all_signals_df = pd.DataFrame(rows, columns=['path', 'data', 'fs'])
                print(f"[FSM] all_signals_df built with {len(self.all_signals_df)} entries")
            else:
                self.all_signals_df = pd.DataFrame(columns=['path', 'data', 'fs'])
                print("[FSM] all_signals_df built empty (no stimuli loaded)")
        except Exception as e:
            print(f"[FSM] Failed to build all_signals_df: {e}")


    def on_event(self, event):
        self.state.on_event(event)

    def get_state(self):
        return self.state.name


if __name__ == "__main__":
    fsm = FiniteStateMachine()
# 
# import serial
# import time
# import RPi.GPIO as GPIO
# import threading
# from trial import Trial
# from datetime import datetime
# import numpy as np
# import sounddevice as sd
# #
# valve_pin = 4#23
# IR_pin = 22#25
# lick_pin = 17#24
# #
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(IR_pin, GPIO.IN)
# GPIO.setup(lick_pin, GPIO.IN)
# GPIO.setup(valve_pin, GPIO.OUT)
# #
# GPIO.setwarnings(False)
# #
# ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
#                     timeout=0.01)  # timeout=1  # Change '/dev/ttyS0' to the detected port
# #
# #
# class State:
#     def __init__(self, name, fsm):
#         self.name = name
#         self.fsm = fsm
#         self.fsm.exp.live_w.deactivate_states_indicators(name)
# #
#     def on_event(self, event):
#         pass
# #
# #
# class IdleState(State):
#     def __init__(self, fsm):
#         super().__init__("Idle", fsm)
#         ser.flushInput()  # clear the data from the serial
#         self.fsm.current_trial.clear_trial()
#         self.fsm.exp.live_w.update_last_rfid('')
#         self.fsm.exp.live_w.update_level('')
#         self.fsm.exp.live_w.update_score('')
#         self.fsm.exp.live_w.update_trial_value('')
# #
#         threading.Thread(target=self.wait_for_event, daemon=True).start()
# #
#     def wait_for_event(self):
#         minutes_passed = 0
#         last_log_time = time.time()
# #
#         while True:
# #
#             if time.time() - last_log_time > 60:
#                 minutes_passed += 1
#                 last_log_time = time.time()
#                 print(f"[IdleState] Waiting for RFID... {minutes_passed} minutes passed")
# #
#             if ser.in_waiting > 0 and not self.fsm.exp.live_w.pause:
#                 try:
#                     mouse_id = ser.readline().decode('utf-8').rstrip()
#                 except Exception as e:
#                     print(f"[IdleState] Error reading RFID: {e}")
#                     continue
# #
#                 if self.recognize_mouse(mouse_id):
#                     self.fsm.current_trial.update_current_mouse(self.fsm.exp.mice_dict[mouse_id])
#                     print("mouse: " + self.fsm.exp.mice_dict[mouse_id].get_id())
#                     print("Level: " + self.fsm.exp.mice_dict[mouse_id].get_level())
#                     self.fsm.exp.live_w.update_last_rfid(mouse_id)
#                     self.fsm.exp.live_w.update_level(self.fsm.exp.mice_dict[mouse_id].get_level())
#                     self.on_event('in_port')
#                     break
#             else:
#                 ser.flushInput()
#                 time.sleep(0.05)
# #
# #     def wait_for_event(self):
# #         while True:
# #             if ser.in_waiting > 0 and not self.fsm.exp.live_w.pause:
# #                 mouse_id = ser.readline().decode('utf-8').rstrip()
# #                 if self.recognize_mouse(mouse_id):
# #                     self.fsm.current_trial.update_current_mouse(self.fsm.exp.mice_dict[mouse_id])
# #                     print("mouse: " + self.fsm.exp.mice_dict[mouse_id].get_id())
# #                     print("Level: " + self.fsm.exp.mice_dict[mouse_id].get_level())
# #                     self.fsm.exp.live_w.update_last_rfid(mouse_id)
# #                     self.fsm.exp.live_w.update_level(self.fsm.exp.mice_dict[mouse_id].get_level())
# #                     self.on_event('in_port')
# #                     break
# #             else:
# #                 ser.flushInput()  # Flush input buffer
# #                 time.sleep(0.05)
# #
#     def on_event(self, event):
#         if event == 'in_port':
#             print("Transitioning from Idle to in_port")
#             self.fsm.state = InPortState(self.fsm)
# #
#     def recognize_mouse(self, data: str):
#         if data in self.fsm.exp.mice_dict:
#             print('recognized mouse: ' + data)
#             return True
#         else:
#             print("mouse ID: '" + data + "' does not exist in the mouse dictionary.")
#             return False
# #
# #
# # class InPortState(State):
# #     def __init__(self, fsm):
# #         super().__init__("port", fsm)
# #         threading.Thread(target=self.wait_for_event, daemon=True).start()
# #
# #     def wait_for_event(self):
# #         while GPIO.input(IR_pin) != GPIO.HIGH:
# #             time.sleep(0.09)
# #         self.fsm.exp.live_w.toggle_indicator("IR", "on")
# #         time.sleep(0.1)
# #         self.fsm.exp.live_w.toggle_indicator("IR", "off")
# #         print("The mouse entered!")
# #         if self.fsm.exp.exp_params["start_trial_time"] is not None:
# #             time.sleep(int(self.fsm.exp.exp_params["start_trial_time"]))
# #             print("sleep before start trial")
# #         self.on_event('IR_stim')
# #
# #     def on_event(self, event):
# #         if event == 'IR_stim':
# #             print("Transitioning from in_port to trial")
# #             self.fsm.state = TrialState(self.fsm)
# #
# class InPortState(State):
#     def __init__(self, fsm):
#         super().__init__("port", fsm)
#         threading.Thread(target=self.wait_for_event, daemon=True).start()
# #
#     def wait_for_event(self):
#         timeout_seconds = 15  # timeout
#         start_time = time.time()
# #
#         while GPIO.input(IR_pin) != GPIO.HIGH:
#             if time.time() - start_time > timeout_seconds:
#                 print("Timeout in InPortState: returning to IdleState")
#                 self.on_event("timeout")
#                 return
#             time.sleep(0.09)
# #
#         self.fsm.exp.live_w.toggle_indicator("IR", "on")
#         time.sleep(0.1)
#         self.fsm.exp.live_w.toggle_indicator("IR", "off")
#         print("The mouse entered!")
# #
#         if self.fsm.exp.exp_params["start_trial_time"] is not None:
#             time.sleep(int(self.fsm.exp.exp_params["start_trial_time"]))
#             print("Sleep before start trial")
# #
#         self.on_event('IR_stim')
# #
#     def on_event(self, event):
#         if event == 'IR_stim':
#             print("Transitioning from InPort to Trial")
#             self.fsm.state = TrialState(self.fsm)
#         elif event == 'timeout':
#             print("Transitioning from InPort to Idle due to timeout")
#             self.fsm.state = IdleState(self.fsm)
# #
# class TrialState(State):
#     def __init__(self, fsm):
#         super().__init__("trial", fsm)
#         self.got_response = None
#         self.stop_threads = False
#         self.trial_thread = threading.Thread(target=self.run_trial)
#         self.trial_thread.start()
# #
#     def run_trial(self):
#         self.fsm.current_trial.start_time = datetime.now().strftime('%H:%M:%S.%f')  # Get current time
#         self.fsm.current_trial.calculate_stim()
#         self.fsm.exp.live_w.update_trial_value(self.fsm.current_trial.current_value)
# #
#         stim_thread = threading.Thread(target=self.tdt_as_stim)
#         input_thread = threading.Thread(target=self.receive_input, args=(lambda: self.stop_threads,))
# #
#         stim_thread.start()
#         input_thread.start()
# #
# #         stim_thread.join()
# #         self.stop_threads = True
# #         input_thread.join()
#         while stim_thread.is_alive():
#             if self.got_response:
#                 self.stop_threads = True
#                 break
#             time.sleep(0.05)
# #
#         stim_thread.join()
#         self.stop_threads = True
#         input_thread.join()
#         if self.fsm.current_trial.score is None:
#             self.fsm.current_trial.score = self.evaluate_response()
#             print("score: " + self.fsm.current_trial.score)
#             self.fsm.exp.live_w.update_score(self.fsm.current_trial.score)
# #
#             if self.fsm.current_trial.score == 'hit':
#                 self.give_reward()
#             elif self.fsm.current_trial.score == 'fa':
#                 self.give_punishment()
# #
#         self.on_event('trial_over')
# #
#     def give_reward(self):
#         GPIO.output(valve_pin, GPIO.HIGH)
#         #time.sleep(0.03)
#         time.sleep(float(self.fsm.exp.exp_params["open_valve_duration"]))
#         GPIO.output(valve_pin, GPIO.LOW)
# #
# #     def give_punishment(self):
# #         try:
# #             noise = np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/white_noise.npy')
# #             sd.play(noise, len(noise))
# #             sd.wait()
# #         finally:
# #             self.fsm.exp.live_w.toggle_indicator("stim", "off")
# #             time.sleep(5) #timeout as punishment
# #
#     def give_punishment(self): #after changing to .npz
#         try:
#             data = np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/white_noise.npz')
#             noise = data['noise']
#             Fs = int(data['Fs'])
#             sd.play(noise, samplerate=Fs)
#             sd.wait()
#         finally:
#             self.fsm.exp.live_w.toggle_indicator("stim", "off")
#             time.sleep(5) #timeout as punishment
# #
# #
# #
# #     def tdt_as_stim(self):
# #         stim_path = self.fsm.current_trial.current_stim_path
# #         print(stim_path)
# #         try:
# #             tone_shape = np.load(stim_path)
# #             sd.play(tone_shape, len(tone_shape))
# #             sd.wait()
# #         finally:
# #             self.fsm.exp.live_w.toggle_indicator("stim", "off")
# #             time.sleep(int(self.fsm.exp.exp_params["time_to_lick_after_stim"]))
# #             print('stimulus done')
#     def tdt_as_stim(self):
#         stim_path = self.fsm.current_trial.current_stim_path
#         try:
#             stim_data = np.load(stim_path)
#             if isinstance(stim_data, np.lib.npyio.NpzFile):
#                 stim_array = stim_data["data"]
#                 sample_rate = stim_data["rate"].item()  # .item() -> int
#             else:
#                 stim_array = stim_data
#                 sample_rate = int(300000)
#                 print("Should use NPZ file!!!! now this is the default sampling rate: 300000 !!!!!")
# #
#             stim_duration = len(stim_array) / sample_rate
#             print("stim_duration: " +str(stim_duration))
# #
# #             sd.play(stim_array, sample_rate)
#             sd.play(stim_array, len(stim_array))
# #
#             start_time = time.time()
#             while time.time() - start_time < stim_duration:
#                 if self.got_response:
#                     print("Early response detected — stopping stimulus")
#                     sd.stop()
#                     return
#                 time.sleep(0.05)
# #
#             sd.wait()
#             time_to_lick = int(self.fsm.exp.exp_params["time_to_lick_after_stim"])
#             print("Stimulus done. Waiting post-stim lick window...")
# #
#             start_post = time.time()
#             while time.time() - start_post < time_to_lick:
#                 if self.got_response:
#                     print("Early response during post-stim window — skipping rest")
#                     return
#                 time.sleep(0.05)
# #
#             print("Post-stim lick window completed.")
# #
#         finally:
#             self.fsm.exp.live_w.toggle_indicator("stim", "off")
# #
# #
#     def receive_input(self, stop):
#         if self.fsm.exp.exp_params["lick_time_bin_size"] is not None:
#             time.sleep(int(self.fsm.exp.exp_params["lick_time_bin_size"]))
#         elif self.fsm.exp.exp_params["lick_time"] == "1":
#             pass
#         elif self.fsm.exp.exp_params["lick_time"] == "2":
#             time.sleep(int(self.fsm.exp.exp_params["stimulus_length"]))
# #
#         counter = 0
#         self.got_response = False
#         print('waiting for licks...')
#         while not stop():
#             if GPIO.input(lick_pin) == GPIO.HIGH:
#                 self.fsm.exp.live_w.toggle_indicator("lick", "on")
#                 self.fsm.current_trial.add_lick_time()
#                 counter += 1
#                 time.sleep(0.08)
#                 self.fsm.exp.live_w.toggle_indicator("lick", "off")
#                 print("lick detected")
# #
#                 if counter >= int(self.fsm.exp.exp_params["lick_threshold"]) and not self.got_response:
#                     self.got_response = True
#                     print('threshold reached')
# #
# #                     self.fsm.current_trial.score = self.evaluate_response()
# #                     print(f"Immediate evaluation: {self.fsm.current_trial.score}")
# #
# #                     if self.fsm.current_trial.score == 'hit':
# #                         self.give_reward()
# #                     elif self.fsm.current_trial.score == 'fa':
# #                         self.give_punishment()
# #                     self.fsm.exp.live_w.update_score(self.fsm.current_trial.score)
#                     break
# #
#             time.sleep(0.08)
# #
#         if not self.got_response:
#             print('no response')
#         print('num of licks:', counter)
# #
# #     def receive_input(self, stop):
# #         if self.fsm.exp.exp_params["lick_time_bin_size"] is not None:
# #             time.sleep(int(self.fsm.exp.exp_params["lick_time_bin_size"]))
# #         elif self.fsm.exp.exp_params["lick_time"] == "1":
# #             pass
# #         elif self.fsm.exp.exp_params["lick_time"] == "2":
# #             time.sleep(int(self.fsm.exp.exp_params["stimulus_length"]))
# #
# #         counter = 0
# #         self.got_response = False
# #         print('waiting for licks...')
# #         while not stop():
# #             if GPIO.input(lick_pin) == GPIO.HIGH:
# #                 self.fsm.exp.live_w.toggle_indicator("lick", "on")
# #                 self.fsm.current_trial.add_lick_time()
# #                 counter += 1
# #                 time.sleep(0.08)
# #                 self.fsm.exp.live_w.toggle_indicator("lick", "off")
# #                 print("lick detected")
# #             time.sleep(0.08)
# #         if counter >= int(self.fsm.exp.exp_params["lick_threshold"]):
# #             self.got_response = True
# #             print('threshold reached')
# #         else:
# #             print('no response')
# #         print('num of licks:', counter)
# #
#     def on_event(self, event):
#         if event == 'trial_over':
#             time.sleep(0.5)
#             self.fsm.current_trial.write_trial_to_csv(self.fsm.exp.txt_file_path)
#             if self.fsm.exp.exp_params['ITI_time'] is None:
#                 while GPIO.input(IR_pin) == GPIO.HIGH:
#                     time.sleep(0.09)
#                 time.sleep(1) # wait one sec after exit- before pass to the next trial
#             else:
#                 time.sleep(int(self.fsm.exp.exp_params['ITI_time']))
#             print("Transitioning from trial to idle")
#             self.fsm.state = IdleState(self.fsm)
# #
#     def evaluate_response(self):
#         value = self.fsm.current_trial.current_value
#         if value == 'go':
#             return 'hit' if self.got_response else 'miss'
#         elif value == 'no-go':
#             return 'fa' if self.got_response else 'cr'
#         elif value == 'catch':
#             return 'catch - response' if self.got_response else 'catch - no response'
# #
# class FiniteStateMachine:
# #
#     def __init__(self, experiment=None):
#         self.exp = experiment
#         self.current_trial = Trial(self)
#         self.state = IdleState(self)
# #
#     def on_event(self, event):
#         self.state.on_event(event)
# #
#     def get_state(self):
#         return self.state.name
# #
# #
# if __name__ == "__main__":
#     fsm = FiniteStateMachine()
# #
# 
# 
# 
# 
# 
# 

