
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

class ParametersApp:
    def __init__(self, root):#, experiment
        self.root = root
        # self.root.title("Data Analysis App")
        # self.experiment = experiment  # Reference to Experiment instance
        # # Set window size and position
        # window_width = 700
        # window_height = 600
        # screen_width = self.root.winfo_screenwidth()
        # screen_height = self.root.winfo_screenheight()
        # x_position = (screen_width // 2) - (window_width // 2)
        # y_position = (screen_height // 2) - (window_height // 2)
        # self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        #
        # # Font style for widgets
        self.font_style = tkFont.Font(family="Helvetica", size=13)
#####################################################################################
        # Variable to track selected display option
        self.lick_time_display_option = tk.StringVar(value='1')  # Default to 1

        # lick_time (when to start counting licks) Radiobuttons frame
        self.lick_time_radiobuttons_frame = tk.Frame(root)
        self.lick_time_radiobuttons_frame.pack(pady=10)
        self.lick_time_custom_input_label = tk.Label(self.lick_time_radiobuttons_frame, text=" When to start counting the licks:", font=self.font_style)
        self.lick_time_custom_input_label.pack(anchor=tk.W)
        # Radiobuttons with command to trigger display of entry field
        tk.Radiobutton(self.lick_time_radiobuttons_frame, text="With stim", variable=self.lick_time_display_option, value='1',
                       font=self.font_style, command=self.lick_time_show_entry_field).pack(anchor=tk.W)
        tk.Radiobutton(self.lick_time_radiobuttons_frame, text="After stim", variable=self.lick_time_display_option, value='2',
                       font=self.font_style, command=self.lick_time_show_entry_field).pack(anchor=tk.W)

        # Radiobutton with associated entry field
        self.lick_time_bin_size_frame = tk.Frame(self.lick_time_radiobuttons_frame)
        self.lick_time_bin_size_radiobutton = tk.Radiobutton(self.lick_time_bin_size_frame, text="By time",
                                                   variable=self.lick_time_display_option, value='3',
                                                   font=self.font_style, command=self.lick_time_show_entry_field)
        self.lick_time_bin_size_radiobutton.pack(side=tk.LEFT) #

        # Entry field for custom bin size (initially hidden)
        self.lick_time_bin_size_entry = tk.Entry(self.lick_time_bin_size_frame, font=self.font_style, width=5)
        self.lick_time_bin_size_entry.pack(side=tk.LEFT, padx=5)
        self.lick_time_bin_size_entry.pack_forget()  # Hide initially
        self.lick_time_bin_size_frame.pack(anchor=tk.W)

###################################################################

        self.start_trial_display_option = tk.StringVar(value='1')  # Default to 1

        # Radiobuttons frame
        self.start_trial_radiobuttons_frame = tk.Frame(root)
        self.start_trial_radiobuttons_frame.pack(pady=10)
        self.start_trial_custom_input_label = tk.Label(self.start_trial_radiobuttons_frame, text="Start trial:", font=self.font_style)
        self.start_trial_custom_input_label.pack(anchor=tk.W)
        # Radiobuttons with command to trigger display of entry field
        tk.Radiobutton(self.start_trial_radiobuttons_frame, text="Immediately", variable=self.start_trial_display_option, value='1',
                       font=self.font_style, command=self.start_trial_show_entry_field).pack(anchor=tk.W)

        # Radiobutton with associated entry field
        self.start_trial_bin_size_frame = tk.Frame(self.start_trial_radiobuttons_frame)
        self.start_trial_bin_size_radiobutton = tk.Radiobutton(self.start_trial_bin_size_frame, text="By time",
                                                   variable=self.start_trial_display_option, value='2',
                                                   font=self.font_style, command=self.start_trial_show_entry_field)
        self.start_trial_bin_size_radiobutton.pack(side=tk.LEFT)

        # Entry field for custom bin size (initially hidden)
        self.start_trial_bin_size_entry = tk.Entry(self.start_trial_bin_size_frame, font=self.font_style, width=5)
        self.start_trial_bin_size_entry.pack(side=tk.LEFT, padx=5)
        self.start_trial_bin_size_entry.pack_forget()  # Hide initially
        self.start_trial_bin_size_frame.pack(anchor=tk.W)

 ##################################################################
        self.IR_no_RFID_frame = tk.Frame(root)
        self.custom_input_label3 = tk.Label(self.IR_no_RFID_frame, text="IR detected- no RFID:", font=self.font_style)
        self.custom_input_label3.pack(side=tk.LEFT)
        self.option_var = tk.StringVar(value="Take the Last RFID")  # Default value
        self.IR_no_RFID = ttk.OptionMenu(self.IR_no_RFID_frame, self.option_var, "Take the Last RFID", "Take the Last RFID", "dont start trial")
        self.IR_no_RFID.pack(pady=2,side=tk.LEFT)
        # Add IR_no_RFID_frame to the root window
        self.IR_no_RFID_frame.pack(pady=10)

####################################################################

        # Entry field for custom bin size (initially hidden)
        self.num_licks_frame = tk.Frame(root)
        self.num_licks_label = tk.Label(self.num_licks_frame, text="num of licks as response:", font=self.font_style)
        self.num_licks_label.pack(side=tk.LEFT)
        self.licks_entry = tk.Entry(self.num_licks_frame, font=self.font_style, width=5)
        self.licks_entry.insert(0,"5")
        self.licks_entry.pack(side=tk.LEFT, padx=10)
        self.num_licks_frame.pack(anchor=tk.W,pady=10)

#####################################################################
        
        self.time_licks_frame = tk.Frame(root)
        self.time_licks_label = tk.Label(self.time_licks_frame, text="time to count licks after the stimulus (sec):", font=self.font_style)
        self.time_licks_label.pack(side=tk.LEFT)
        self.time_licks_entry = tk.Entry(self.time_licks_frame, font=self.font_style, width=5)
        self.time_licks_entry.insert(0,"2")
        self.time_licks_entry.pack(side=tk.LEFT, padx=10)
        self.time_licks_frame.pack(anchor=tk.W,pady=10)
        
#####################################################################
        
        self.time_open_valve_frame = tk.Frame(root)
        self.time_open_valve_label = tk.Label(self.time_open_valve_frame, text="open valve duration (sec):", font=self.font_style)
        self.time_open_valve_label.pack(side=tk.LEFT)
        self.time_open_valve_entry = tk.Entry(self.time_open_valve_frame, font=self.font_style, width=5)
        self.time_open_valve_entry.insert(0,"0.017")
        self.time_open_valve_entry.pack(side=tk.LEFT, padx=10)
        self.time_open_valve_frame.pack(anchor=tk.W,pady=10)

#####################################################################
        # Punishment timeout (seconds)
        self.punishment_timeout_frame = tk.Frame(root)
        self.punishment_timeout_label = tk.Label(self.punishment_timeout_frame, text="timeout_punishment (sec):", font=self.font_style)
        self.punishment_timeout_label.pack(side=tk.LEFT)
        self.punishment_timeout_entry = tk.Entry(self.punishment_timeout_frame, font=self.font_style, width=5)
        self.punishment_timeout_entry.insert(0, "5")
        self.punishment_timeout_entry.pack(side=tk.LEFT, padx=10)
        self.punishment_timeout_frame.pack(anchor=tk.W, pady=10)

#####################################################################
        # Entry field for custom bin size (initially hidden)
#         self.ITI_frame = tk.Frame(root)
#         self.ITI_label = tk.Label(self.ITI_frame, text="ITI:", font=self.font_style)
#         self.ITI_label.pack(side=tk.LEFT)
#         self.ITI_entry = tk.Entry(self.ITI_frame, font=self.font_style, width=5)
#         self.ITI_entry.insert(0,"3")
#         self.ITI_entry.pack(side=tk.LEFT, padx=10)
#         self.ITI_frame.pack(anchor=tk.W, pady=10)
#####################################################################
        self.ITI_display_option = tk.StringVar(value='1')  # Default to 1

        # Radiobuttons frame
        self.ITI_radiobuttons_frame = tk.Frame(root)
        self.ITI_radiobuttons_frame.pack(pady=10)
        self.ITI_custom_input_label = tk.Label(self.ITI_radiobuttons_frame, text="ITI:", font=self.font_style)
        self.ITI_custom_input_label.pack(anchor=tk.W)
        # Radiobuttons with command to trigger display of entry field
        tk.Radiobutton(self.ITI_radiobuttons_frame, text="exit and enter", variable=self.ITI_display_option, value='1',
                       font=self.font_style, command=self.ITI_show_entry_field).pack(anchor=tk.W)

        # Radiobutton with associated entry field
        self.ITI_bin_size_frame = tk.Frame(self.ITI_radiobuttons_frame)
        self.ITI_bin_size_radiobutton = tk.Radiobutton(self.ITI_bin_size_frame, text="By time",
                                                   variable=self.ITI_display_option, value='2',
                                                   font=self.font_style, command=self.ITI_show_entry_field)
        self.ITI_bin_size_radiobutton.pack(side=tk.LEFT)

        # Entry field for custom bin size (initially hidden)
        self.ITI_bin_size_entry = tk.Entry(self.ITI_bin_size_frame, font=self.font_style, width=5)
        self.ITI_bin_size_entry.pack(side=tk.LEFT, padx=5)
        self.ITI_bin_size_entry.pack_forget()  # Hide initially
        self.ITI_bin_size_frame.pack(anchor=tk.W)
#####################################################################

        # OK button to run analysis
        # self.ok_button = tk.Button(root, text="OK", command=self.get_parameters, font=self.font_style)
        # self.ok_button.pack(pady=20)
    
###################################################################
    def lick_time_show_entry_field(self):
        """Show entry field only when 'By Bin Size' is selected."""
        if self.lick_time_display_option.get() == '3':  # Show entry if "By Bin Size" is selected
            self.lick_time_bin_size_entry.pack(side=tk.LEFT, padx=5)
        else:  # Hide entry for other options
            self.lick_time_bin_size_entry.pack_forget()

    def start_trial_show_entry_field(self):
        """Show entry field only when 'By Bin Size' is selected."""
        if self.start_trial_display_option.get() == '2':  # Show entry if "By Bin Size" is selected
            self.start_trial_bin_size_entry.pack(side=tk.LEFT, padx=5)
        else:  # Hide entry for other options
            self.start_trial_bin_size_entry.pack_forget()
            
    def ITI_show_entry_field(self):
        """Show entry field only when 'By Bin Size' is selected."""
        if self.ITI_display_option.get() == '2':  # Show entry if "By Bin Size" is selected
            self.ITI_bin_size_entry.pack(side=tk.LEFT, padx=5)
        else:  # Hide entry for other options
            self.ITI_bin_size_entry.pack_forget()

#     def get_parameters(self):
# 
#         """Retrieve all user-selected parameters from the GUI."""
#         parameters = {
#             "display_option": self.display_option.get(),
#             "bin_size": self.bin_size_entry.get() if self.display_option.get() == '3' else None,
#             # Add other options similarly, following the widget structure
#             # For example:
#             "start_trial_option": self.display_option2.get(),
#             "start_trial_time": self.bin_size_entry2.get() if self.display_option2.get() == '2' else None,
#             "IR_no_RFID_option": self.option_var.get(),
#             "lick_threshold": self.licks_entry.get(),
#             "time_to_lick_after_stim": self.time_licks_entry.get(),
#             "ITI": self.ITI_display_option.get(),
#             "ITI_time": self.ITI_bin_size_entry.get() if self.ITI_display_option.get() == '2' else None,
#         }
#         # Set parameters in the Experiment class
#         self.experiment.set_parameters(parameters)
#         return parameters
############################################
    # def run_analysis(self):
    #     """Run analysis using all selected parameters."""
    #     params = self.get_parameters()
    #     print("Running analysis with the following parameters:")
    #     print(params)
# Example usage
def run():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
if __name__ == "__main__":
    run()
    # root = tk.Tk()
    # app = App(root)
    # root.mainloop()
