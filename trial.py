from datetime import datetime
import csv
import random
import os
from column_constants import ColumnNames
class Trial:
    def __init__(self,fsm):
        self.fsm = fsm
        self.current_mouse = None
        self.first_stim_df = None
        self.first_stim_index = None
        self.first_stim_path = None
        self.second_stim_df = None
        self.second_stim_index = None
        self.second_stim_path = None
        self.current_value = None #go\no-go
        self.current_exp_parameters = None
        self.score = None
        self.start_time = None

        
        self.licks_time = []

    def update_current_mouse(self, new_mouse: 'Mouse'):
        self.current_mouse = new_mouse

    def save_trial(self):
        pass

    def update_score(self, score): # hit\miss\fa\cr
        self.score = score

    # def calculate_stim(self): #determine if the trial is go\nogo\catch using random
    #     level_name = self.current_mouse.get_level()
    #     level_rows = self.fsm.exp.levels_df.loc[self.fsm.exp.levels_df['Level Name'] == level_name]
    #     probabilities = level_rows["P(first))"].tolist()
    #     indices = level_rows["Index"].tolist()
    #     total_probability = sum(probabilities)
    #     normalized_probabilities = [p / total_probability for p in probabilities]
    #     chosen_index = random.choices(indices, weights=normalized_probabilities, k=1)[0]
    #     self.current_stim_df = self.fsm.exp.levels_df.loc[(self.fsm.exp.levels_df['Level Name'] == level_name)&(self.fsm.exp.levels_df['Index'] == chosen_index)]
    #     self.current_stim_path = self.current_stim_df.iloc[0]['Stimulus Path']
    #     self.current_stim_index = self.current_stim_df.iloc[0]['Index']
    #     go_probability = self.current_stim_df.iloc[0]['Go Probability']
    #     self.current_value = self.calculate_go_no_go(go_probability)
    def calculate_stim(self): #determine if the trial is go\nogo\catch using random
        level_name = self.current_mouse.get_level()
        level_rows = self.fsm.exp.levels_df.loc[self.fsm.exp.levels_df['Level Name'] == level_name]
        first_stim_index = self.weighted_random_choice("P(first)", level_rows)
        second_stim_index = self.weighted_random_choice("P(second)", level_rows)
        self.first_stim_df = self.fsm.exp.levels_df.loc[(self.fsm.exp.levels_df['Level Name'] == level_name)&(self.fsm.exp.levels_df['Index'] == first_stim_index)]
        self.second_stim_df = self.fsm.exp.levels_df.loc[(self.fsm.exp.levels_df['Level Name'] == level_name)&(self.fsm.exp.levels_df['Index'] == second_stim_index)]
        self.first_stim_path = self.first_stim_df.iloc[0]['Stimulus Path']
        self.second_stim_path = self.second_stim_df.iloc[0]['Stimulus Path']
        self.first_stim_index = self.first_stim_df.iloc[0]['Index']
        self.second_stim_index = self.second_stim_df.iloc[0]['Index']
        self.current_value = self.calculate_value()

    def weighted_random_choice(self, probabilities_column, level_rows):
        probabilities = level_rows[probabilities_column].tolist()
        indices = level_rows[ColumnNames.INDEX].tolist()
        total_probability = sum(probabilities)
        
        if total_probability == 0:
            # If all probabilities are 0, choose randomly
            return random.choice(indices)
        
        normalized_probabilities = [p / total_probability for p in probabilities]
        chosen_index = random.choices(indices, weights=normalized_probabilities, k=1)[0]
        return chosen_index

    def calculate_value(self):
        if self.second_stim_df.iloc[0]['Value'] == "catch":
            return "catch"
        elif self.first_stim_index==self.second_stim_index:
            return "go"
        else:
            return "no-go"

    def end_trial(self): # the trial is over - go to save it
        pass
    
    def clear_trial(self):
        self.current_mouse = None
        self.current_exp_parameters = None
        self.score = None
        self.current_stim = None
        self.current_value = None  # go\no-go\catch
        self.current_stim_path = None
        self.start_time = None
        self.current_stim_index = None
        self.licks_time = []

    def add_lick_time(self):
        current_datetime = datetime.now()
        self.licks_time.append(current_datetime.strftime('%H:%M:%S.%f'))
# Function to write trial results
    def write_trial_to_csv(self, txt_file_name):
        header = ['date', 'start time', 'end time', 'mouse ID', 'level', 'value',' first stim index', 'first stim name', 'second stim index', 'second stim name','score', 'licks_time'] # Define the header if the file does not exist yet
        current_datetime = datetime.now()
        date = current_datetime.strftime('%Y-%m-%d')  # Get current date
        end_time = current_datetime.strftime('%H:%M:%S.%f')  # Get current time
        first_stim_name = os.path.basename(self.first_stim_path)
        second_stim_name = os.path.basename(self.second_stim_path)
        trial_data = [date, self.start_time, end_time, self.current_mouse.id, self.current_mouse.level, self.current_value, self.first_stim_index, first_stim_name, self.second_stim_index, second_stim_name, self.score , self.licks_time]
        with open(txt_file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Check if the file is empty to write the header
            if file.tell() == 0:  # Check if the file is empty
                writer.writerow(header)  # Write the header
            writer.writerow(trial_data)



