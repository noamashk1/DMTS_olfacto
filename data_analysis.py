
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm
import numpy as np
from scipy.ndimage import gaussian_filter1d
from datetime import datetime
import ast

def calculate_d_prime(hits, fas, misses, crs):
    hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
    fa_rate = fas / (fas + crs) if (fas + crs) > 0 else 0
    hit_rate = min(max(hit_rate, 0.01), 0.99)
    fa_rate = min(max(fa_rate, 0.01), 0.99)
    z_hit = norm.ppf(hit_rate)
    z_fa = norm.ppf(fa_rate)
    return z_hit - z_fa

# קבועים עבור PSTH
BIN_SIZE_MS = 100
TRIAL_DURATION_MS = 3000
BIN_EDGES = np.arange(0, TRIAL_DURATION_MS + BIN_SIZE_MS, BIN_SIZE_MS)
SMOOTH_SIGMA = 1  # להחלקה של הגרף

class DataAnalysis:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Data Viewer")
        self.root.geometry("300x450")
        self.df = None
        self.loaded_file_path = None  # נתיב הקובץ שנטען

        self.load_button = tk.Button(root, text="Load txt", command=self.load_txt)
        self.load_button.pack(pady=(20, 10))

        self.mouse_id_label = tk.Label(root, text="Select Mouse ID:")
        self.mouse_id_label.pack()
        self.mouse_id_combobox = ttk.Combobox(root, state="readonly")
        self.mouse_id_combobox.pack()

        # קלטים לחלון ו-overlap
        self.window_size_label = tk.Label(root, text="Window Size (for D-prime):")
        self.window_size_label.pack()
        self.window_size_entry = tk.Entry(root)
        self.window_size_entry.insert(0, "200")
        self.window_size_entry.pack()

        self.overlap_label = tk.Label(root, text="Overlap: (for D-prime)")
        self.overlap_label.pack()
        self.overlap_entry = tk.Entry(root)
        self.overlap_entry.insert(0, "100")
        self.overlap_entry.pack()

        # שדה להגדרת מספר הנתונים האחרונים להצגה
        self.recent_data_label = tk.Label(root, text="Recent Data Count:")
        self.recent_data_label.pack()
        self.recent_data_entry = tk.Entry(root)
        self.recent_data_entry.insert(0, "1000")
        self.recent_data_entry.pack()

        self.graph_button = tk.Button(root, text="Score dist & D-prime", command=self.open_graph_window)
        self.graph_button.pack(pady=10)

        # כפתור לעקומה פסיכומטרית
        self.psychometric_button = tk.Button(root, text="Psychometric Curve", command=self.plot_psychometric_curve)
        self.psychometric_button.pack(pady=10)

        # כפתור ל-PSTH
        self.psth_button = tk.Button(root, text="PSTH graph", command=self.plot_psth)
        self.psth_button.pack(pady=10)

    def load_txt(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        self.loaded_file_path = file_path  # שמירת נתיב הקובץ
        self.df = pd.read_csv(file_path, sep=',')
        self.df['mouse ID'] = self.df['mouse ID'].astype(str).str.strip()
        self.df['score'] = self.df['score'].astype(str).str.upper()

        unique_ids = sorted(self.df['mouse ID'].unique())
        self.mouse_id_combobox['values'] = unique_ids
        if unique_ids:
            self.mouse_id_combobox.set(unique_ids[0])

    def open_graph_window(self):
        if self.df is None:
            return

        selected_id = self.mouse_id_combobox.get().strip()
        if not selected_id:
            return

        try:
            window_size = int(self.window_size_entry.get())
            overlap = int(self.overlap_entry.get())
            recent_data_count = int(self.recent_data_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for window size, overlap, and recent data count.")
            return

        if window_size <= 0 or overlap < 0:
            messagebox.showerror("Input Error", "Window size must be > 0 and overlap must be ≥ 0.")
            return

        if overlap >= window_size:
            messagebox.showerror("Input Error", "Overlap must be smaller than window size.")
            return

        if recent_data_count <= 0:
            messagebox.showerror("Input Error", "Recent data count must be > 0.")
            return

        stride = window_size - overlap

        mouse_data = self.df[self.df['mouse ID'] == selected_id]
        if mouse_data.empty:
            messagebox.showwarning("Warning", f"No data found for Mouse ID: {selected_id}")
            return

        if window_size > len(mouse_data):
            messagebox.showerror("Input Error", f"Window size ({window_size}) is larger than number of trials ({len(mouse_data)}).")
            return

        if recent_data_count > len(mouse_data):
            messagebox.showwarning("Warning", f"Recent data count ({recent_data_count}) is larger than number of trials ({len(mouse_data)}). Using all available data.")
            recent_data_count = len(mouse_data)

        new_window = tk.Toplevel(self.root)
        new_window.title(f"Graphs for Mouse {selected_id}")

        #score_counts = mouse_data['score'].value_counts().reindex(['HIT', 'FA', 'MISS', 'CR'], fill_value=0)
        recent_data = mouse_data.tail(recent_data_count)
        score_counts = recent_data['score'].value_counts().reindex(['HIT', 'FA', 'MISS', 'CR'], fill_value=0)

        fig, axs = plt.subplots(2, 1, figsize=(8, 8))
        fig.tight_layout(pad=3.0)

        # גרף עמודות
        axs[0].bar(score_counts.index, score_counts.values, color='skyblue')
        axs[0].set_title(f"Score Distribution for Mouse {selected_id} (Last {recent_data_count} trials)")
        axs[0].set_ylabel("Count")

        # d-prime
        d_prime_values = []
        trial_indices = []

        for start in range(0, len(mouse_data) - window_size + 1, stride):
            window = mouse_data.iloc[start:start + window_size]
            hits = (window['score'] == 'HIT').sum()
            fas = (window['score'] == 'FA').sum()
            misses = (window['score'] == 'MISS').sum()
            crs = (window['score'] == 'CR').sum()
            d_prime = calculate_d_prime(hits, fas, misses, crs)
            d_prime_values.append(d_prime)
            trial_indices.append(start + window_size)

        axs[1].plot(trial_indices, d_prime_values, marker='o', linestyle='-', color='green')
        axs[1].set_title("d-prime Over Time (overlapping windows)")
        axs[1].set_xlabel("Trial Index")
        axs[1].set_ylabel("d-prime")
        axs[1].set_xticks(trial_indices)

        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_psychometric_curve(self):
        if self.df is None:
            return

        selected_id = self.mouse_id_combobox.get().strip()
        if not selected_id:
            return

        mouse_data = self.df[self.df['mouse ID'] == selected_id]
        if mouse_data.empty:
            messagebox.showwarning("Warning", f"No data found for Mouse ID: {selected_id}")
            return

        # ננקה שמות תדרים (נסיר סיומות npz/npy)
        def extract_freq(stim_name):
            name = stim_name.upper().replace('.NPZ','').replace('.NPY','')
            for suf in ['KHZ','KHz','KHZ']:
                if suf in name:
                    freq = name.replace('KHZ','').replace('KHz','').replace('KHZ','').strip()
                    return freq.replace('-', '.')
            return name.replace('-', '.')

        mouse_data = mouse_data.copy()
        mouse_data['freq'] = mouse_data['stim name'].apply(extract_freq)
        mouse_data['stim name'] = mouse_data['stim name'].str.upper()

        # נזהה תדרים רלוונטיים
        freq_to_stim = {}
        for stim in mouse_data['stim name'].unique():
            freq = extract_freq(stim)
            freq_to_stim[freq] = stim

        results = {}
        for freq, stim in freq_to_stim.items():
            stim_trials = mouse_data[mouse_data['stim name'] == stim]
            total = len(stim_trials)
            print("freq: " + freq + ", len: " + str(total))
            if total == 0:
                continue
            if freq == '7':
                hits = (stim_trials['score'] == 'HIT').sum()
                percent = (hits / total) * 100
            elif freq == '14':
                fa = (stim_trials['score'] == 'FA').sum()
                percent = (fa / total) * 100
            else:
                # אחוז ה-catch response: כל התגובות (לא MISS) מתוך כלל ה-catch
                catch_responses = (stim_trials['score'] == 'CATCH - RESPONSE').sum()
                percent = (catch_responses / total) * 100
            results[freq] = percent

        # סדר תדרים מספרית (תמיכה ב-10-5 -> 10.5)
        sorted_freqs = sorted(results.keys(), key=lambda x: float(x.replace('-', '.')))
        y = [results[f] for f in sorted_freqs]
        x_labels = [f + ' KHz' for f in sorted_freqs]

        # ציור הגרף
        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(x_labels, y, marker='o', linestyle='-', color='purple')
        ax.set_title(f"Psychometric Curve for Mouse {selected_id}")
        ax.set_xlabel("Frequency")
        ax.set_ylabel("% Response")
        ax.set_ylim(0, 105)
        ax.grid(True)

        new_window = tk.Toplevel(self.root)
        new_window.title(f"Psychometric Curve for Mouse {selected_id}")
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_psth(self):
        """יצירת גרף PSTH עבור הקובץ שכבר נטען"""
        # בדיקה שקובץ נטען
        if self.loaded_file_path is None:
            messagebox.showwarning("Warning", "Please load a file first using 'Load txt' button.")
            return
        
        # בדיקה שעכבר נבחר
        selected_id = self.mouse_id_combobox.get().strip()
        if not selected_id:
            messagebox.showwarning("Warning", "Please select a mouse ID.")
            return
            
        # קריאת ערך recent_data מהשדה
        try:
            recent_data_count = int(self.recent_data_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid integer for recent data count.")
            return
            
        if recent_data_count <= 0:
            messagebox.showerror("Input Error", "Recent data count must be > 0.")
            return
            
        try:
            # טעינת הנתונים ויצירת הגרף
            go_trials, nogo_trials = self.load_trials_from_csv(self.loaded_file_path, recent_data_count, selected_id)
            
            if not go_trials and not nogo_trials:
                messagebox.showwarning("Warning", f"No valid trial data found for Mouse ID: {selected_id}.")
                return
                
            go_matrix = self.compute_binned_matrix(go_trials, BIN_EDGES)
            nogo_matrix = self.compute_binned_matrix(nogo_trials, BIN_EDGES)
            self.plot_smoothed_psth(go_matrix, nogo_matrix, BIN_EDGES, recent_data_count, selected_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing PSTH data: {str(e)}")

    def load_trials_from_csv(self, csv_path, recent_data_count, selected_mouse_id):
        """טעינת נתוני trials מקובץ CSV עבור עכבר ספציפי"""
        df = pd.read_csv(csv_path)
        
        # סינון לפי mouse ID
        if 'mouse ID' in df.columns:
            df['mouse ID'] = df['mouse ID'].astype(str).str.strip()
            df = df[df['mouse ID'] == selected_mouse_id]
        
        # קיצור הנתונים לפי recent_data_count
        if recent_data_count < len(df):
            df = df.tail(recent_data_count)
        
        go_trials = []
        nogo_trials = []

        for _, row in df.iterrows():
            label = row["go\\no-go"].strip().lower()
            start_time_str = row["start time"]
            licks_str = row["licks_time"]

            try:
                lick_times = ast.literal_eval(licks_str)
            except:
                continue

            if not lick_times:
                continue

            # חישוב זמנים יחסיים
            start_dt = datetime.strptime(start_time_str, "%H:%M:%S.%f")
            rel_licks = []
            for lick_str in lick_times:
                try:
                    lick_dt = datetime.strptime(lick_str, "%H:%M:%S.%f")
                    delta_ms = (lick_dt - start_dt).total_seconds() * 1000
                    if 0 <= delta_ms <= TRIAL_DURATION_MS:
                        rel_licks.append(delta_ms)
                except:
                    continue

            if label == "go":
                go_trials.append(rel_licks)
            elif label == "no-go":
                nogo_trials.append(rel_licks)

        return go_trials, nogo_trials

    def compute_binned_matrix(self, trials, bin_edges):
        """חישוב מטריצת bins עבור הנתונים"""
        matrix = []
        for trial in trials:
            counts, _ = np.histogram(trial, bins=bin_edges)
            matrix.append(counts)
        return np.array(matrix)

    def plot_smoothed_psth(self, go_matrix, nogo_matrix, bin_edges, recent_data_count, selected_mouse_id):
        """יצירת גרף PSTH מוחלק עם בדיקת מובהקות סטטיסטית בכל נקודה"""
        from scipy.stats import ttest_ind

        time_axis = (bin_edges[:-1] + bin_edges[1:]) / 2

        def compute_stats(matrix):
            if matrix.size == 0:
                return np.zeros(len(time_axis)), np.zeros(len(time_axis))
            mean_vals = matrix.mean(axis=0)
            stderr_vals = matrix.std(axis=0) / np.sqrt(matrix.shape[0])
            return gaussian_filter1d(mean_vals, sigma=SMOOTH_SIGMA), gaussian_filter1d(stderr_vals, sigma=SMOOTH_SIGMA)

        mean_go, stderr_go = compute_stats(go_matrix)
        mean_nogo, stderr_nogo = compute_stats(nogo_matrix)

        # בדיקת מובהקות סטטיסטית (t-test) בכל נקודת זמן
        significant_points = []
        p_values = []
        if go_matrix.shape[0] > 1 and nogo_matrix.shape[0] > 1:
            for i in range(go_matrix.shape[1]):
                go_bin = go_matrix[:, i]
                nogo_bin = nogo_matrix[:, i]
                # בדיקה רק אם יש ערכים בשני התנאים
                if np.any(~np.isnan(go_bin)) and np.any(~np.isnan(nogo_bin)):
                    # t-test לא תלוי, שווה שונות (או לא)
                    t_stat, p_val = ttest_ind(go_bin, nogo_bin, equal_var=False, nan_policy='omit')
                    p_values.append(p_val)
                    if p_val < 0.05:
                        significant_points.append(i)
                else:
                    p_values.append(np.nan)
        else:
            p_values = [np.nan] * len(time_axis)

        # יצירת חלון חדש עם הגרף
        new_window = tk.Toplevel(self.root)
        new_window.title("PSTH - Licks Analysis")

        fig, ax = plt.subplots(figsize=(10, 6))
        
        if go_matrix.size > 0:
            ax.plot(time_axis, mean_go, label="Go", color='blue')
            ax.fill_between(time_axis, mean_go - stderr_go, mean_go + stderr_go, color='blue', alpha=0.3)
        
        if nogo_matrix.size > 0:
            ax.plot(time_axis, mean_nogo, label="No-Go", color='orange')
            ax.fill_between(time_axis, mean_nogo - stderr_nogo, mean_nogo + stderr_nogo, color='orange', alpha=0.3)

        # חישוב הגובה המקסימלי של הנתונים (לפני הוספת כוכביות)
        max_data_height = 0
        if go_matrix.size > 0:
            max_data_height = max(max_data_height, np.max(mean_go + stderr_go))
        if nogo_matrix.size > 0:
            max_data_height = max(max_data_height, np.max(mean_nogo + stderr_nogo))

        # הוספת כוכביות מעל נקודות מובהקות
        asterisk_heights = []
        for i in significant_points:
            y_max = max(mean_go[i] + stderr_go[i], mean_nogo[i] + stderr_nogo[i])
            asterisk_y = y_max + 0.1 * max_data_height  # 10% מהגובה המקסימלי כמרווח
            ax.text(time_axis[i], asterisk_y, '*', color='red', ha='center', va='bottom', fontsize=16, fontweight='bold')
            asterisk_heights.append(asterisk_y)

        # עדכון גבולות ציר Y כדי להכיל את הכוכביות
        if asterisk_heights:
            max_asterisk_height = max(asterisk_heights)
            # הוסף עוד מעט מקום מעל הכוכבית הגבוהה ביותר
            ax.set_ylim(bottom=0, top=max_asterisk_height + 0.1 * max_data_height)
        else:
            # אם אין כוכביות, השתמש בגבולות רגילים
            ax.set_ylim(bottom=0, top=max_data_height * 1.1)

        ax.set_title(f"Smoothed PSTH of Licks (Go vs No-Go) - Mouse {selected_mouse_id} - Last {recent_data_count} trials")
        ax.set_xlabel("Time from Stimulus Onset (ms)")
        ax.set_ylabel("Average Licks per 100 ms")
        ax.legend()
        ax.grid(True)
        
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataAnalysis(root)
    root.mainloop()

