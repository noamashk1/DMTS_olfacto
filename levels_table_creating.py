import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk  # Make sure to import ttk for the Combobox
import csv  # To handle CSV writing
from tkinter import filedialog  # To open the file dialog for saving files
import os
from column_constants import ColumnNames


class LevelDefinitionApp:
    
    def __init__(self, master, experiment):
        self.master = master
        self.experiment = experiment
        self.master.title("Experiment Level Definition")
        self.frame = tk.Frame(self.master)
        self.frame.pack(padx=10, pady=10)
        
        # Initialize the save_button attribute
        self.save_button = None  # Initially set to None, to be defined later
        
        # Create header row for the first table
        tk.Label(self.frame, text=ColumnNames.LEVEL_NAME, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.frame, text=ColumnNames.NUMBER_OF_STIMULI, font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5)
        # Current row index for the first table
        self.current_row = 1

        # Button to add a new level
        self.add_button = tk.Button(self.frame, text="Add Level", command=self.add_level)
        self.add_button.grid(row=self.current_row, column=0, columnspan=2, pady=10)

        # Load button to create the second table
        self.load_button = tk.Button(self.frame, text="Load", command=self.load_levels)
        self.load_button.grid(row=self.current_row + 1, column=0, columnspan=2, pady=10)

        self.level_entries = []  # Store level name and stimulus counts
        self.stimuli_table_content = []
        self.stimuli_frame = None  # Frame for the stimuli table
        

        self.stimuli_container = None  # Container for scrollable content
        self.canvas = None  # Canvas for scrolling
        self.scrollbar = None  # Scrollbar for scrolling
        self.scrollable_frame = None  # Scrollable frame inside canvas
        
        
        self.save_path = None

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
        tk.Label(self.stimuli_frame, text=ColumnNames.P_FIRST, font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.P_SECOND, font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5, pady=5)
        tk.Label(self.stimuli_frame, text=ColumnNames.INDEX, font=("Arial", 12, "bold")).grid(row=0, column=5, padx=5, pady=5)
            
    
    def load_levels(self):
        # Clear previous stimuli frame if it exists
        # if self.stimuli_frame is not None:
        #     for widget in self.stimuli_frame.winfo_children():
        #         widget.destroy()
        #     self.header_titles()
        # else:
        #     # Create stimuli frame if it doesn't exist
        #     self.stimuli_frame = tk.Frame(self.master)
        #     self.stimuli_frame.pack(side="left", padx=10, pady=10)
        #     self.header_titles()
        if self.stimuli_container is not None:
            self.stimuli_container.destroy()
            
        # Create main container for scrollable content
        self.stimuli_container = tk.Frame(self.master)
        self.stimuli_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.stimuli_container, width=800, height=400)
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
                    messagebox.showwarning("Input Error", "Number of stimuli must be at least 1.")
                    return
                
                # Create rows for each stimulus
                self.create_stimuli_rows(level_name, number_of_stimuli)

                # Enable the Save button if it's not already created
                if self.save_button is None:
                    self.save_button = tk.Button(self.frame, text="Save", command=self.save_stimuli_table)
                    self.save_button.grid(row=self.current_row + 2, column=0, columnspan=2, pady=10)
                self.save_button.config(state=tk.NORMAL)  # Enable button

            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid number for the stimuli.")
            
    def save_stimuli_table(self):
        # Gather the data from the stimuli table
        data_to_save = []
        all_filled = True  # Flag to check if all fields are filled

        # Loop through all level entries to pull their contents
        for level_name, stimulus_combobox, value_combobox, p_first_entry, p_second_entry, index_entry in self.stimuli_table_content:
            
            #level_name = level_name_row.get().strip()
            odor_number = stimulus_combobox.get().strip()
            value = value_combobox.get().strip()
            p_first = p_first_entry.get().strip()
            p_second = p_second_entry.get().strip()
            index = index_entry.get().strip()

            # Check if each required field is filled
            if not odor_number or not value or not p_first or not p_second or not index or value == "Select" or odor_number == "Select":
                all_filled = False
                break

            # הוספת שורה לשמירה
            data_to_save.append([level_name, odor_number, value, p_first, p_second, index])

        if all_filled:
            levels_dir = os.path.join(os.getcwd(), "Levels")
            os.makedirs(levels_dir, exist_ok=True)  # Create it if it doesn't exist

            # Open the file dialog in the "Levels" folder
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Levels File"
            )#initialdir=levels_dir,

            if file_path:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(ColumnNames.get_csv_headers())
                    writer.writerows(data_to_save)
                    print(data_to_save)

                self.save_path = file_path
                self.master.destroy()
        else:
            messagebox.showwarning("Input Error", "Please complete all the parameters.")
                
    def create_stimuli_rows(self, level_name, number_of_stimuli):
        # Add rows for each stimulus
        # Calculate the starting row based on the number of widgets already in the grid
        start_row = len(self.stimuli_frame.grid_slaves()) // 2  # This may need adjustment if you change the number of columns

        for i in range(number_of_stimuli):
            row_idx = start_row + i + 1

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

            # Create the P(first) entry field (user input for this specific stimulus)
            p_first_entry = tk.Entry(self.stimuli_frame)
            p_first_entry.grid(row=row_idx, column=3, padx=5, pady=2)

            # Create the P(second) entry field
            p_second_entry = tk.Entry(self.stimuli_frame)
            p_second_entry.grid(row=row_idx, column=4, padx=5, pady=2)

            # Create the index entry field
            index_entry = tk.Entry(self.stimuli_frame)
            index_entry.grid(row=row_idx, column=5, padx=5, pady=2)

            # Store all relevant widgets and values for later use
            self.stimuli_table_content.append(
                (level_name, stimulus_combobox, value_combobox, p_first_entry, p_second_entry, index_entry)
            )

        # Draw a line separator after the last row of stimuli for this level
        separator = tk.Frame(self.stimuli_frame, height=1, bg="gray")  # Create a frame for the line
        separator.grid(row=start_row + number_of_stimuli + 1, column=0, columnspan=6, sticky="ew", padx=5, pady=5)  # columnspan=6 for the new columns
        
#     def load_stimulus_file(self, entry, label):
#         # Open file dialog to select a stimulus file
#         stimuli_dir = os.path.join(os.getcwd(), "stimuli")
#         default_dir = stimuli_dir if os.path.exists(stimuli_dir) else os.getcwd()
#         file_path = filedialog.askopenfilename(
#         filetypes=(("All Files", "*.*"),),
#         initialdir=default_dir,
#         title="Select Stimulus File"
#     )
# #          file_path = filedialog.askopenfilename(title="Select Stimulus File",
# #                                                  filetypes=(("All Files", "*.*"),))
#         if file_path:  # If a file was selected
#             entry.delete(0, tk.END)  # Clear the current entry
#             entry.insert(0, file_path)  # Insert the selected file path
            
#             # Update the label to show only the filename
#             filename = file_path.split("/")[-1]  # Get the filename from the path
#             label.config(text=filename)  # Update the label with just the filename
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling in the canvas"""
        if self.canvas:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        

# Application Execution
if __name__ == "__main__":
    root = tk.Tk()
    app = LevelDefinitionApp(root)
    root.mainloop()

