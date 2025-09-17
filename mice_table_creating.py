import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from tkinter import scrolledtext
from tkinter import filedialog
import serial
import threading
import General_functions
import pandas as pd
from mouse import Mouse
import os
# Main application
class MainApp:
    def __init__(self, master, GUI):
        self.master = master
        self.main_GUI = GUI
        
        # Initial parameter
        self.mice_list = None
        self.mice_dict = None
        self.option_vars = []
        self.stop_event = threading.Event()
        self.serial_thread = None
        self.miceTableFrame = tk.LabelFrame(self.master)
        self.miceTableFrame.grid(row=0, column=0, padx=10, pady=10)
        self.miceBtnsFrame = tk.LabelFrame(master)
        self.miceBtnsFrame.grid(row=0, column=1, padx=10, pady=10)
        self.create_mice_table()

        # Button to open the new parameter window
        self.get_parameter_button = tk.Button(self.miceBtnsFrame, text="Update mice table", command=self.open_parameter_window)
        self.get_parameter_button.pack(pady=10)
        self.load_mice_button = tk.Button(self.miceBtnsFrame, text="Load mice table", command=self.load_mice_list_from_file)
        self.load_mice_button.pack(pady=10)

    def load_mice_list_from_file(self):
#         if len(self.main_GUI.levels_list) == 0:
#             messagebox.showerror("Error", "You must first set levels for the experiment.")
#             return
#         file_path = filedialog.askopenfilename(
#             title="Select Mice List TXT File",
#             filetypes=[("Text Files", "*.txt")])
        # Get the parent directory of the current working directory
        #parent_dir = os.path.dirname(os.getcwd())
        parent_dir = os.getcwd()
        # Construct the default path to the "experiments" folder
        default_dir = os.path.join(parent_dir, "experiments")
        
        # Open file dialog, starting in the "experiments" folder if it exists
        initial_dir = default_dir if os.path.exists(default_dir) else parent_dir
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select Mice List File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if not file_path:
            return  

        try:
            with open(file_path, "r") as file:
                lines = file.read().strip().splitlines()
                cleaned_lines = [line.strip() for line in lines if line.strip()]
                self.mice_list = cleaned_lines
                self.create_mice_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load mice list from TXT:\n{e}")
 
    
    def set_new_mice_list(self,data_list):
        self.mice_list = data_list
        self.create_mice_table()

    def update_mice_display(self):
        try:
            if self.mice_dict is not None:
                # יצירת רשימת עכברים מהמילון
                mice_list = list(self.mice_dict.keys())
                self.set_new_mice_list(mice_list)
                print("[MiceTable] Mice display updated successfully")
            else:
                print("[MiceTable] No mice data to update")
        except Exception as e:
            print(f"[MiceTable] Error updating mice display: {e}")

                    
    def open_parameter_window(self):
        if len(self.main_GUI.levels_list) == 0:
            messagebox.showerror("Error", "You must first set levels for the experiment.")
            return
        if self.serial_thread is not None and self.serial_thread.is_alive():
            # Stop the existing thread if it's running
            self.stop_event.set()
            self.serial_thread.join()  # Wait for it to finish
            self.stop_event.clear()  # Reset the event
        self.stop_event.clear()  # Clear event flag
        self.serial_thread = threading.Thread(target=self.read_from_serial)
        self.serial_thread.start()
        
                # Create a new Toplevel window
        self.parameter_window = tk.Toplevel(self.master)
        self.parameter_window.title("mice table")
        
        General_functions.center_the_window(self.parameter_window,'500x300')

        
        # Data Display Box for serial readings
        self.data_display = scrolledtext.ScrolledText(self.parameter_window, height=15, width=15, state=tk.DISABLED)
        self.data_display.pack(side=tk.LEFT, padx=5, pady=5)

        # Unique Data Display Box
        self.unique_data_display = scrolledtext.ScrolledText(self.parameter_window, height=15, width=15, state=tk.DISABLED)
        self.unique_data_display.pack(side=tk.RIGHT, padx=5, pady=5)

        # Add to List Button
        self.add_to_list_button = tk.Button(self.parameter_window, text="Add to List", command=self.add_to_list)
        self.add_to_list_button.pack()


        # Clear Button
        self.clear_button = tk.Button(self.parameter_window, text="Clear", command=self.clear_box)
        self.clear_button.pack()

        # Done Button
        self.done_button = tk.Button(self.parameter_window, text="Done", command=self.save_and_close)
        self.done_button.pack()

        threading.Thread(target=self.read_from_serial, daemon=True).start()
        # Wait for the parameter_window to close before proceeding
        self.parameter_window.wait_window()  # This makes the window modal-like
        
    def read_from_serial(self):
        try:
            # Setup Serial Connection (adjust COM4 and 9600 to your needs)
            ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=0.01)#timeout=1  # Change '/dev/ttyS0' to the detected port
            while not self.stop_event.is_set():#True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    self.display_data(line)
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        finally:
            if self.serial_thread:
                try:
                    ser.close()
                except Exception:
                    pass
                
    def display_data(self, data):
        # Allow editing the text widget by setting it to normal
        self.data_display.config(state=tk.NORMAL)
        
        # Clear the existing text
        self.data_display.delete("1.0", tk.END)
        
        # Insert the new data
        self.data_display.insert(tk.END, data + "\n")
        
        # Automatically scroll to the end (useful if it would add multiple lines)
        self.data_display.yview(tk.END)
        
        # Disable editing again
        self.data_display.config(state=tk.DISABLED)
        
    def add_to_list(self):
        # Extract the last line from data_display
        data_display_content = self.data_display.get("1.0", tk.END).strip().split("\n")
        if data_display_content:
            last_line = data_display_content[-1]
            if last_line not in self.unique_data_display.get("1.0", tk.END):
                self.unique_data_display.config(state=tk.NORMAL)
                self.unique_data_display.insert(tk.END, last_line + "\n")
                self.unique_data_display.config(state=tk.DISABLED)
                
    def clear_box(self):
        # Clear the existing text
        self.unique_data_display.config(state=tk.NORMAL)
        self.unique_data_display.delete("1.0", tk.END)
        self.unique_data_display.config(state=tk.DISABLED)

    def save_and_close(self):
        self.stop_event.set()
        text_content = self.unique_data_display.get("1.0", tk.END).strip()
        
        # Split the content by lines
        data_list = text_content.split("\n")
        print(data_list)
        # Return the list
        print(self.mice_list)
        self.set_new_mice_list(data_list)
        print(self.mice_list)
        print(f"Mice list received and saved: {self.mice_list}")  
        self.parameter_window.destroy()



    def create_mice_table(self):#self.mice_list,self.miceTableFrame
        for widget in self.miceTableFrame.winfo_children():
            widget.destroy()
        tk.Label(self.miceTableFrame, text="Mouse", font=("Arial", 12, "bold"), borderwidth=2).grid(row=0, column=0,
                                                                                          sticky="nsew", padx=10,
                                                                                          pady=10)
        tk.Label(self.miceTableFrame, text="Level", font=("Arial", 12, "bold"), borderwidth=2).grid(row=0, column=1,
                                                                                          sticky="nsew", padx=10,
                                                                                          pady=10)
        if self.mice_list:
            # Style configuration
            label_font = ("Arial", 10)
            entry_font = ("Arial", 10)
            # Populate the table
            self.option_vars = []
            for i, item in enumerate(self.mice_list):
                # Create a label for each list item
                label = tk.Label(self.miceTableFrame, text=item, font=label_font, borderwidth=0)
                label.grid(row=i + 1, column=0, sticky="nsew", padx=5, pady=2)

                option_var = tk.StringVar(value=str(self.main_GUI.levels_list[0]))  # Default value
                OptionMenu = ttk.OptionMenu(self.miceTableFrame, option_var,self.main_GUI.levels_list[0], *self.main_GUI.levels_list)
                OptionMenu.grid(row=i + 1, column=1, sticky="nsew", padx=5, pady=2)

                # Store the StringVar in a list for later access
                self.option_vars.append(option_var)

            # Configure grid size weights for uniformity
            self.miceTableFrame.grid_columnconfigure(0, weight=1)  # Mouse column
            self.miceTableFrame.grid_columnconfigure(1, weight=0)  # Level column, keeping it narrower
            for row in range(len(self.mice_list) + 1):
                self.miceTableFrame.grid_rowconfigure(row, weight=0)  # No expansion for rows to keep height small
            self.set_mice_as_dict()


    def set_mice_as_dict(self):
        # Retrieve data from the labels and the OptionMenus
        data = {}
        for i in range(len(self.mice_list)):
            mouse_label = self.miceTableFrame.grid_slaves(row=i + 1, column=0)[0]  # Get label for Mouse
            selected_level = self.option_vars[i].get()  # Get the selected value from the stored StringVar

            mouse_name = mouse_label.cget("text")  # Get the text of the label

            # Add to dictionary: mouse name as key and selected level as value
            data[mouse_name] = Mouse(mouse_name,selected_level)
        self.mice_dict = data
        print(f"mice list: {list(data.keys())}")  # Display the dictionary


