import serial
import glob
import time
import threading
import tkinter as tk
from tkinter import ttk

class RFIDDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Detector")
        self.root.geometry("400x200")
        
        # Initialize serial connection
        self.ser = None
        self.running = False
        self.current_rfid = None
        self.last_rfid_time = None  # Track when last RFID was detected
        
        # Setup GUI
        self.setup_gui()
        
        # Try to connect to serial
        self.connect_serial()
        
        # Start detection thread
        if self.ser:
            self.running = True
            self.detection_thread = threading.Thread(target=self.detect_rfid, daemon=True)
            self.detection_thread.start()
    
    def setup_gui(self):
        """Setup the GUI elements"""
        # Title label
        title_label = tk.Label(self.root, text="RFID Detector", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Connecting...", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Current RFID label
        current_label = tk.Label(self.root, text="Current RFID:", font=("Arial", 12))
        current_label.pack(pady=5)
        
        # RFID display (using Text widget for better visibility)
        self.rfid_display = tk.Text(self.root, height=2, width=30, font=("Arial", 14, "bold"),
                                    relief=tk.SUNKEN, borderwidth=2, state=tk.DISABLED)
        self.rfid_display.pack(pady=10)
        
        # Placeholder text
        self.rfid_display.config(state=tk.NORMAL)
        self.rfid_display.insert("1.0", "No RFID detected")
        self.rfid_display.config(state=tk.DISABLED)
        
        # Close button
        close_button = tk.Button(self.root, text="Close", command=self.close_app, width=10)
        close_button.pack(pady=10)
    
    def connect_serial(self):
        """Connect to serial port"""
        try:
            ports = glob.glob('/dev/ttyUSB*')
            if not ports:
                self.status_label.config(text="No USB serial device found!", fg="red")
                return False
            
            port = ports[0]
            self.ser = serial.Serial(port=port, baudrate=9600, timeout=0.01)
            self.status_label.config(text=f"Connected to {port}", fg="green")
            return True
        except Exception as e:
            self.status_label.config(text=f"Connection error: {e}", fg="red")
            return False
    
    def update_rfid_display(self, rfid):
        """Update the RFID display with new value"""
        self.rfid_display.config(state=tk.NORMAL)
        self.rfid_display.delete("1.0", tk.END)
        if rfid:
            self.rfid_display.insert("1.0", rfid)
        self.rfid_display.config(state=tk.DISABLED)
        self.current_rfid = rfid
    
    def clear_rfid_display(self):
        """Clear the RFID display"""
        self.rfid_display.config(state=tk.NORMAL)
        self.rfid_display.delete("1.0", tk.END)
        self.rfid_display.config(state=tk.DISABLED)
        self.current_rfid = None
    
    def detect_rfid(self):
        """Main detection loop - runs in separate thread"""
        while self.running:
            try:
                if self.ser and self.ser.in_waiting > 0:
                    raw_data = self.ser.readline()
                    mouse_id = raw_data.decode('utf-8').rstrip()
                    
                    if mouse_id and mouse_id != self.current_rfid:
                        # New RFID detected - update display
                        self.last_rfid_time = time.time()
                        self.root.after(0, self.update_rfid_display, mouse_id)
                        print(f"RFID detected: {mouse_id}")
                else:
                    # Check if 5 seconds have passed since last RFID detection
                    if self.last_rfid_time is not None:
                        if time.time() - self.last_rfid_time >= 5.0:
                            # Clear display after 5 seconds
                            self.root.after(0, self.clear_rfid_display)
                            self.last_rfid_time = None  # Reset timer
                            print("Display cleared - 5 seconds without new RFID")
                    time.sleep(0.05)
            except Exception as e:
                print(f"Error reading RFID: {e}")
                time.sleep(0.1)
    
    def close_app(self):
        """Close the application"""
        self.running = False
        if self.ser:
            self.ser.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RFIDDetector(root)
    root.mainloop()

if __name__ == "__main__":
    main()

