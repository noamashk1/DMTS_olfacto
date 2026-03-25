import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk  # Make sure to import ttk for the Combobox
import csv  # To handle CSV writing
from tkinter import filedialog  # To open the file dialog for saving files
import os
from column_constants import ColumnNames


def _raise_tk_window(win):
    """Lift window to front; helps when running inside Thonny/IDE (dialogs behind IDE)."""
    try:
        win.lift()
        win.attributes("-topmost", True)
        win.update_idletasks()
        win.attributes("-topmost", False)
        win.focus_force()
    except tk.TclError:
        pass


class LevelDefinitionApp:
    
    def __init__(self, master, experiment):
        self.master = master
        self.experiment = experiment
        self.master.title("Experiment Level Definition")
        self.frame = tk.Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        # Instruction line: clarify the two-step flow
        instruction = "Step 1: Add levels (name + number of stimuli).\nStep 2: Build the stimuli table, set its parameters, then Save."
        tk.Label(self.frame, text=instruction, font=("Arial", 9), wraplength=500, justify=tk.LEFT).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Initialize the save_button attribute
        self.save_button = None  # Initially set to None, to be defined later
        
        # Create header row for the first table
        tk.Label(self.frame, text=ColumnNames.LEVEL_NAME, font=("Arial", 12, "bold")).grid(row=1, column=0, padx=5, pady=5)
        tk.Label(self.frame, text=ColumnNames.NUMBER_OF_STIMULI, font=("Arial", 12, "bold")).grid(row=1, column=1, padx=5, pady=5)
        # Current row index for the first table
        self.current_row = 2

        # Button to add a new level
        self.add_button = tk.Button(self.frame, text="Add level row", command=self.add_level)
        self.add_button.grid(row=self.current_row, column=0, columnspan=2, pady=10)

        # Load button to create the second table
        self.load_button = tk.Button(self.frame, text="Build stimuli table", command=self.load_levels)
        self.load_button.grid(row=self.current_row + 1, column=0, columnspan=2, pady=10)

        self.level_entries = []  # Store level name and stimulus counts
        self.stimuli_table_content = []
        self.stimuli_frame = None  # Frame for the stimuli table
        

        self.stimuli_container = None  # Container for scrollable content
        self.canvas = None  # Canvas for scrolling
        self.scrollbar = None  # Scrollbar for scrolling
        self.scrollable_frame = None  # Scrollable frame inside canvas
        
        
        self.save_path = None
        self.go_prob = None  # Probability for go (0-100)

    def add_level(self):
        level_name_entry = tk.Entry(self.frame)
        level_name_entry.grid(row=self.current_row, column=0, padx=5, pady=5)

        stimuli_count_entry = tk.Entry(self.frame)  # Make the entry shorter
        stimuli_count_entry.grid(row=self.current_row, column=1, padx=5, pady=5)

        self.level_entries.append((level_name_entry, stimuli_count_entry))  # Save entries to access later

        # Update the current row and reposition buttons
        self.current_row += 1
        self.update_buttons()

    def update_buttons(self):
        # Update the positions of the Add and Load buttons
        self.add_button.grid(row=self.current_row, column=0, columnspan=2, pady=10)
        self.load_button.grid(row=self.current_row + 1, column=0, columnspan=2, pady=10)
        
    def header_titles(self):
        # Create header for the stimuli table
        tk.Label(self.stimuli_frame, text=ColumnNames.LEVEL_NAME, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.ODOR_NUMBER, font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.VALUE, font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.P_GO, font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.P_STIM, font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.IS_NEUROLUX, font=("Arial", 12, "bold")).grid(row=0, column=5, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.P_NEUROLUX, font=("Arial", 12, "bold")).grid(row=0, column=6, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.INDEX, font=("Arial", 12, "bold")).grid(row=0, column=7, padx=5, pady=5)
            
    
    def load_levels(self):
        # Reset go_prob to ensure clean state
        self.go_prob = None
        
        # Ask user for go probability
        dialog = tk.Toplevel(self.master)
        dialog.title("Go Probability")
        dialog.geometry("300x150")
        dialog.transient(self.master)
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text="Enter Go Probability (0-100):", font=("Arial", 10)).pack(pady=10)
        
        entry = tk.Entry(dialog, font=("Arial", 12), width=10)
        entry.pack(pady=5)
        entry.focus()
        
        error_label = tk.Label(dialog, text="", fg="red", font=("Arial", 9))
        error_label.pack(pady=2)
        
        def validate_and_close():
            try:
                value = int(entry.get().strip())
                if 0 <= value <= 100:
                    self.go_prob = value
                    dialog.destroy()
                else:
                    error_label.config(text="Please enter a number between 0 and 100")
            except ValueError:
                error_label.config(text="Please enter a valid number")
        
        def on_enter(event):
            validate_and_close()
        
        entry.bind("<Return>", on_enter)
        
        ok_button = tk.Button(dialog, text="OK", command=validate_and_close, width=10)
        ok_button.pack(pady=10)
        _raise_tk_window(dialog)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        # If user closed dialog without entering valid value, return
        if self.go_prob is None:
            return
        
        # Clear previous stimuli frame if it exists
        if self.stimuli_container is not None:
            self.stimuli_container.destroy()
            
        # Create main container for scrollable content
        self.stimuli_container = tk.Frame(self.master)
        self.stimuli_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.stimuli_container, width=1100, height=400)
        self.scrollbar = tk.Scrollbar(self.stimuli_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Set stimuli_frame to be the scrollable frame
        self.stimuli_frame = self.scrollable_frame
        self.header_titles()


        # Attempt to build the second table based on user input
        for level_entry, count_entry in self.level_entries:
            level_name = level_entry.get().strip()
            try:
                number_of_stimuli = int(count_entry.get().strip())
                
                if number_of_stimuli < 1:
                    messagebox.showwarning(
                        "Input Error",
                        "Number of stimuli must be at least 1.",
                        parent=self.master,
                    )
                    return
                
                # Create rows for each stimulus
                self.create_stimuli_rows(level_name, number_of_stimuli)

                # Enable the Save button if it's not already created
                if self.save_button is None:
                    self.save_button = tk.Button(self.frame, text="Save", command=self.save_stimuli_table)
                    self.save_button.grid(row=self.current_row + 2, column=0, columnspan=2, pady=10)
                self.save_button.config(state=tk.NORMAL)  # Enable button

            except ValueError:
                messagebox.showwarning(
                    "Input Error",
                    "Please enter a valid number for the stimuli.",
                    parent=self.master,
                )
            
    def save_stimuli_table(self):
        # Gather the data from the stimuli table
        data_to_save = []
        all_filled = True  # Flag to check if all fields are filled

        # Loop through all level entries to pull their contents
        for level_name, stimulus_combobox, value_combobox, p_go_entry, p_stim_entry, is_neurolux_combobox, p_neurolux_entry, row_index in self.stimuli_table_content:
            
            #level_name = level_name_row.get().strip()
            odor_number = stimulus_combobox.get().strip()
            value = value_combobox.get().strip()
            p_go = p_go_entry.get().strip()
            p_stim = p_stim_entry.get().strip()
            is_neurolux = is_neurolux_combobox.get().strip()
            p_neurolux = p_neurolux_entry.get().strip()
            index = str(row_index)  # INDEX is auto-filled (read-only)

            # Check if each required field is filled (index is auto-generated, so not checked)
            if not odor_number or not value or not p_go or not p_stim or not p_neurolux or value == "Select" or odor_number == "Select":
                all_filled = False
                break

            # Validate P(neurolux) is a number between 0-100
            try:
                p_neurolux_val = float(p_neurolux)
                if p_neurolux_val < 0 or p_neurolux_val > 100:
                    messagebox.showwarning(
                        "Input Error",
                        f"P(neurolux) must be between 0 and 100. Found: {p_neurolux}",
                        parent=self.master,
                    )
                    all_filled = False
                    break
            except ValueError:
                messagebox.showwarning(
                    "Input Error",
                    f"P(neurolux) must be a valid number. Found: {p_neurolux}",
                    parent=self.master,
                )
                all_filled = False
                break

            # הוספת שורה לשמירה
            data_to_save.append([level_name, odor_number, value, p_go, p_stim, is_neurolux, p_neurolux, index])

        # if all_filled:
        #     # Check if levels with only one stimulus have P(go) = 100
        #     from collections import Counter
        #     level_counts = Counter([row[0] for row in data_to_save])  # Count stimuli per level
            
        #     for level_name, stimulus_count in level_counts.items():
        #         if stimulus_count == 1:
        #             # Find the row for this level
        #             for row in data_to_save:
        #                 if row[0] == level_name:  # level_name is the first element
        #                     p_go_value = row[3]  # p_go is the 4th element (index 3)
        #                     try:
        #                         if float(p_go_value) != 100:
        #                             messagebox.showwarning("Input Error", 
        #                                 f"Level '{level_name}' has only one stimulus. P(go) must be 100, but found: {p_go_value}")
        #                             all_filled = False
        #                             break
        #                     except ValueError:
        #                         messagebox.showwarning("Input Error", 
        #                             f"Level '{level_name}' has only one stimulus. P(go) must be 100, but the value '{p_go_value}' is not a valid number.")
        #                         all_filled = False
        #                         break
        #             if not all_filled:
        #                 break
            
        if all_filled:
            levels_dir = os.path.join(os.getcwd(), "Levels")
            os.makedirs(levels_dir, exist_ok=True)  # Create it if it doesn't exist

            # Open the file dialog in the "Levels" folder
            _raise_tk_window(self.master)
            file_path = filedialog.asksaveasfilename(
                initialdir=levels_dir,
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Levels File",
                parent=self.master,
            )

            if file_path:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(ColumnNames.get_csv_headers())
                    writer.writerows(data_to_save)
                    print(data_to_save)

                self.save_path = file_path
                self.master.destroy()
        else:
            messagebox.showwarning(
                "Input Error",
                "Please complete all the parameters.",
                parent=self.master,
            )
                
    def create_stimuli_rows(self, level_name, number_of_stimuli):
        # Add rows for each stimulus
        # Calculate the starting row based on the number of widgets already in the grid
        start_row = len(self.stimuli_frame.grid_slaves()) // 2  # This may need adjustment if you change the number of columns

        for i in range(number_of_stimuli):
            row_idx = start_row + i + 1
            # Global row index (1-based) across the whole table
            row_index = len(self.stimuli_table_content) + 1

            # Add Level Name label
            tk.Label(self.stimuli_frame, text=level_name).grid(row=row_idx, column=0, padx=5, pady=2)

            # Create GPIO Combobox for odor selection
            gpio_keys = list(self.experiment.GPIO_dict.keys())  # Get GPIO keys from experiment
            stimulus_combobox = ttk.Combobox(self.stimuli_frame, values=gpio_keys, state="readonly")
            stimulus_combobox.grid(row=row_idx, column=1, padx=5, pady=2)
            stimulus_combobox.set("Select")  # Placeholder

            # Create a Combobox for the value column
            value_combobox = ttk.Combobox(self.stimuli_frame, values=[r"go\no-go", "catch"])
            value_combobox.grid(row=row_idx, column=2, padx=5, pady=2)
            value_combobox.set("Select")  # Set a default placeholder in the combobox

            # Create the P(go) entry field (user input for this specific stimulus)
            p_go_entry = tk.Entry(self.stimuli_frame)
            p_go_entry.grid(row=row_idx, column=3, padx=5, pady=2)
            if self.go_prob is not None:
                p_go_entry.insert(0, str(self.go_prob))

            # Create the P(stim) entry field
            p_stim_entry = tk.Entry(self.stimuli_frame)
            p_stim_entry.grid(row=row_idx, column=4, padx=5, pady=2)

            # Create the is neurolux combobox with Yes/No options (default No)
            is_neurolux_combobox = ttk.Combobox(self.stimuli_frame, values=["No", "Yes"], state="readonly")
            is_neurolux_combobox.grid(row=row_idx, column=5, padx=5, pady=2)
            is_neurolux_combobox.set("No")  # Default to No

            # Create the P(neurolux) entry field for numbers 0-100
            p_neurolux_entry = tk.Entry(self.stimuli_frame)
            p_neurolux_entry.grid(row=row_idx, column=6, padx=5, pady=2)
            p_neurolux_entry.insert(0, "0")  # Default value 0

            # Create the index label (auto-filled, read-only)
            index_label = tk.Label(self.stimuli_frame, text=str(row_index))
            index_label.grid(row=row_idx, column=7, padx=5, pady=2)

            # Store all relevant widgets and values for later use
            self.stimuli_table_content.append(
                (level_name, stimulus_combobox, value_combobox, p_go_entry, p_stim_entry, is_neurolux_combobox, p_neurolux_entry, row_index)
            )

        # Draw a line separator after the last row of stimuli for this level
        separator = tk.Frame(self.stimuli_frame, height=1, bg="gray")  # Create a frame for the line
        separator.grid(row=start_row + number_of_stimuli + 1, column=0, columnspan=8, sticky="ew", padx=5, pady=5)  # columnspan=8 for all columns including index at the end
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling in the canvas"""
        if self.canvas:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        

# Application Execution
if __name__ == "__main__":
    root = tk.Tk()
    app = LevelDefinitionApp(root)
    root.mainloop()

