
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

class ParametersApp:
    def __init__(self, root):#, experiment
        self.root = root

        self.font_style = tkFont.Font(family="Helvetica", size=13)
#####################################################################################
        # Variable to track selected display option
        self.lick_time_display_option = tk.StringVar(value='1')  # Default to "After stim"

        # lick_time (when to start counting licks) Radiobuttons frame
        self.lick_time_radiobuttons_frame = tk.Frame(root)
        self.lick_time_radiobuttons_frame.pack(pady=10)
        self.lick_time_custom_input_label = tk.Label(self.lick_time_radiobuttons_frame, text=" When to start counting the licks:", font=self.font_style)
        self.lick_time_custom_input_label.pack(anchor=tk.W)
        # Radiobuttons with command to trigger display of entry field
        tk.Radiobutton(self.lick_time_radiobuttons_frame, text="After stim", variable=self.lick_time_display_option, value='1',
                       font=self.font_style, command=self.lick_time_show_entry_field).pack(anchor=tk.W)

        # Radiobutton with associated entry field
        self.lick_time_bin_size_frame = tk.Frame(self.lick_time_radiobuttons_frame)
        self.lick_time_bin_size_radiobutton = tk.Radiobutton(self.lick_time_bin_size_frame, text="By time",
                                                   variable=self.lick_time_display_option, value='2',
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
        self.time_open_valve_label = tk.Label(self.time_open_valve_frame, text="open valve (reward) duration (sec):", font=self.font_style)
        self.time_open_valve_label.pack(side=tk.LEFT)
        self.time_open_valve_entry = tk.Entry(self.time_open_valve_frame, font=self.font_style, width=5)
        self.time_open_valve_entry.insert(0,"0.017")
        self.time_open_valve_entry.pack(side=tk.LEFT, padx=10)
        self.time_open_valve_frame.pack(anchor=tk.W,pady=10)

#####################################################################
        
        self.time_open_odor_frame = tk.Frame(root)
        self.time_open_odor_label = tk.Label(self.time_open_odor_frame, text="open odor (stimulus) duration (sec):", font=self.font_style)
        self.time_open_odor_label.pack(side=tk.LEFT)
        self.time_open_odor_entry = tk.Entry(self.time_open_odor_frame, font=self.font_style, width=5)
        self.time_open_odor_entry.insert(0,"0.5")
        self.time_open_odor_entry.pack(side=tk.LEFT, padx=10)
        self.time_open_odor_frame.pack(anchor=tk.W,pady=10)

#####################################################################
        
        self.load_odor_duration_frame = tk.Frame(root)
        self.load_odor_duration_label = tk.Label(self.load_odor_duration_frame, text="load odor duration (sec):", font=self.font_style)
        self.load_odor_duration_label.pack(side=tk.LEFT)
        self.load_odor_duration_entry = tk.Entry(self.load_odor_duration_frame, font=self.font_style, width=5)
        self.load_odor_duration_entry.insert(0,"1")
        self.load_odor_duration_entry.pack(side=tk.LEFT, padx=10)
        self.load_odor_duration_frame.pack(anchor=tk.W,pady=10)

#####################################################################
        
        self.timeout_punishment_frame = tk.Frame(root)
        self.timeout_punishment_label = tk.Label(self.timeout_punishment_frame, text="timeout (punishment) duration (sec):", font=self.font_style)
        self.timeout_punishment_label.pack(side=tk.LEFT)
        self.timeout_punishment_entry = tk.Entry(self.timeout_punishment_frame, font=self.font_style, width=5)
        self.timeout_punishment_entry.insert(0,"5")
        self.timeout_punishment_entry.pack(side=tk.LEFT, padx=10)
        self.timeout_punishment_frame.pack(anchor=tk.W,pady=10)

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

# Example usage
def run():
    root = tk.Tk()
    app = ParametersApp(root)
    root.mainloop()
if __name__ == "__main__":
    run()
    # root = tk.Tk()
    # app = App(root)
    # root.mainloop()
