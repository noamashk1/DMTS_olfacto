import numpy as np
import sounddevice as sd
import tkinter as tk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    EMAIL = "educage.lab@gmail.com"
    APP_PASSWORD = "vptc kxsf gggs ybxa"  
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Mail sent to {to_email}")
    except Exception as e:
        print("❌ Error sending email:", e)

def center_the_window(window,size=None):
    # Implicitly set dimensions for example purposes
    if size is not None:
        window.geometry(size)
    
    # Ensures the window's dimensions are known
    window.update_idletasks()

    # Retrieve the window size dynamically
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the center position
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    
    # Adjust the window's position to be centered
    window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

def create_table(data_list, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    if data_list:
        # Style configuration
        label_font = ("Arial", 10)
        entry_font = ("Arial", 10)

        # Create headers for the columns
        tk.Label(frame, text="Mouse", font=("Arial", 12, "bold"), borderwidth=2).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(frame, text="Level", font=("Arial", 12, "bold"), borderwidth=2).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Populate the table
        for i, item in enumerate(data_list):
            # Create a label for each list item
            label = tk.Label(frame, text=item, font=label_font, borderwidth=0)
            label.grid(row=i + 1, column=0, sticky="nsew", padx=5, pady=2)

            # Create an entry field with default value '1' for user input
            entry = tk.Entry(frame, font=entry_font, width=5, borderwidth=0)
            entry.insert(0, "1")  # Insert default value of '1'
            entry.grid(row=i + 1, column=1, sticky="nsew", padx=5, pady=2)

        # Configure grid size weights for uniformity
        frame.grid_columnconfigure(0, weight=1)  # Mouse column
        frame.grid_columnconfigure(1, weight=0)  # Level column, keeping it narrower
        for row in range(len(data_list) + 1):
            frame.grid_rowconfigure(row, weight=0)  # No expansion for rows to keep height small

def generate_white_noise(duration, Fs, voltage):
    """
    Generate white noise.

    Parameters:
    duration - Duration of the noise in seconds
    sample_rate - Sample rate in Hz
    
    Returns:
    noise - A NumPy array containing the white noise samples
    """
    # Calculate the number of samples
    num_samples = int(duration * Fs)
    
    # Generate random samples between -1 and 1
    noise = np.random.uniform(-1, 1, num_samples)
    
    # Scale the noise by the voltage (amplitude) before converting to integers
    noise *= voltage  # Adjust the volume

    # Clamp the noise values to ensure they stay within the valid range
    noise = np.clip(noise, -1, 1)
    
    sd.play(noise, Fs)
    sd.wait()  # Wait until sound finishes playing
    
    np.save('/home/educage/git_educage2/educage2/pythonProject1/stimulus/white_noise', noise)

    return noise

def generate_white_noise_npz(duration, Fs, voltage, save_path='/home/educage/git_educage2/educage2/pythonProject1/stimuli/white_noise.npz'):
    """
    Generate and play white noise, then save it along with its sample rate.

    Parameters:
    duration (float): Duration of the noise in seconds
    Fs (int): Sampling rate in Hz
    voltage (float): Amplitude scaling factor (between 0 and 1)
    save_path (str): Path to save the noise and sample rate
    """
    # Calculate the number of samples
    num_samples = int(duration * Fs)
    
    # Generate random white noise in range [-1, 1]
    noise = np.random.uniform(-1, 1, num_samples)
    
    # Scale the noise by voltage
    noise *= voltage
    
    # Clip to ensure values remain in [-1, 1]
    noise = np.clip(noise, -1, 1)
    
    # Play the sound
    sd.play(noise, samplerate=Fs)
    sd.wait()

    # Save noise and sample rate together
    np.savez(save_path, noise=noise, Fs=Fs)

    return noise

#generate_white_noise_npz(duration=1, Fs=44100, voltage=0.8)
def scary_with_ultrasonic(duration=3.0, sample_rate=192000, click_rate=10, save_path = None):
    """
    מוסיף גם רכיב על-קולי בתדרים שהעכברים שומעים (אנחנו לא).
    חשוב להשתמש בכרטיס קול שיכול לנגן עד 192kHz!
    """
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)

    # --- תדרים צורמים בתוך טווח השמיעה שלנו ---
    f1, f2, f3 = 15000, 15500, 16000
    tone_audible = (
        0.25 * np.sin(2 * np.pi * f1 * t) +
        0.25 * np.sin(2 * np.pi * f2 * t) +
        0.25 * np.sin(2 * np.pi * f3 * t)
    )

    # --- רכיב על-קולי (עכברים בלבד) ---
    f4, f5 = 25000, 35000  # 25–35 kHz
    tone_ultra = (
        0.25 * np.sin(2 * np.pi * f4 * t) +
        0.25 * np.sin(2 * np.pi * f5 * t)
    )

    # --- רעש לבן ---
    noise = 0.3 * np.random.normal(0, 1, len(t))

    # --- נקישות ---
    click_signal = np.zeros_like(t)
    click_interval = int(sample_rate / click_rate)
    click_len = int(0.002 * sample_rate)  # 2ms
    for i in range(0, len(t), click_interval):
        click_signal[i:i+click_len] = 1.0

    # שילוב הכל
    signal = tone_audible + tone_ultra + noise + click_signal
    signal = signal / np.max(np.abs(signal))

    # השמעה
    sd.play(signal, samplerate=sample_rate)
    sd.wait()

    # שמירה כ-NPZ (בדומה ל-General_functions.generate_white_noise_npz)
    if save_path:
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            # נשמור גם במפתחות כפולים לתאימות ('noise','Fs') וגם ('data','rate')
            np.savez(save_path, data=signal, Fs=sample_rate)
            print("stimulus saved")
        except Exception as e:
            print(f"[save npz] failed to save '{save_path}': {e}")


#scary_with_ultrasonic(2, click_rate=15, save_path = '/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise_with_ultrasonic.npz')

def scary_with_clicks(duration=3.0, sample_rate=44100, click_rate=10, save_path = None):
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)

    # --- בסיס: תדרים צורמים ---
    f1, f2, f3 = 15000, 15500, 16000
    tone = (
        0.3 * np.sin(2 * np.pi * f1 * t) +
        0.3 * np.sin(2 * np.pi * f2 * t) +
        0.3 * np.sin(2 * np.pi * f3 * t)
    )

    # --- הוספת רעש לבן ---
    noise = 0.2 * np.random.normal(0, 1, len(t))

    # --- יצירת נקישות ---
    click_signal = np.zeros_like(t)
    click_interval = int(sample_rate / click_rate)  # כל כמה דגימות נקישה
    click_len = int(0.002 * sample_rate)  # נקישה של 2ms
    for i in range(0, len(t), click_interval):
        click_signal[i:i+click_len] = 1.0  # פולס קצר

    # שילוב הכל
    signal = tone + noise + click_signal

    # נרמול
    signal = signal / np.max(np.abs(signal))

    # השמעה
    sd.play(signal, samplerate=sample_rate)
    sd.wait()

    # שמירה כ-NPZ (בדומה ל-General_functions.generate_white_noise_npz)
    if save_path:
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            np.savez(save_path, data=signal, Fs=sample_rate)
            print("stimulus saved")
        except Exception as e:
            print(f"[save npz] failed to save '{save_path}': {e}")

#scary_with_clicks(duration=2, click_rate=12, save_path = '/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise.npz') 


