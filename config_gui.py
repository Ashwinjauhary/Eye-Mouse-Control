"""
Configuration GUI for Eye Mouse Control
Provides a user-friendly interface for adjusting settings and calibration
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import cv2
import threading
import time
from PIL import Image, ImageTk
from eye_mouse_control import CalibrationData, BlinkConfig, EyeMouseController

class ConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Eye Mouse Control - Configuration")
        self.root.geometry("800x600")
        
        # Load current calibration
        self.calibration = CalibrationData.load("calibration.json")
        self.blink_config = BlinkConfig()
        
        # Camera preview variables
        self.camera_active = False
        self.cap = None
        self.current_frame = None
        
        # Create GUI elements
        self.create_widgets()
        
        # Start with camera preview
        self.start_camera_preview()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Settings
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Right panel - Camera preview
        preview_frame = ttk.LabelFrame(main_frame, text="Camera Preview", padding="10")
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create settings controls
        self.create_settings_controls(settings_frame)
        
        # Create camera preview
        self.create_camera_preview(preview_frame)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Calibration", command=self.start_calibration).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Settings", command=self.test_settings).pack(side=tk.LEFT, padx=5)
    
    def create_settings_controls(self, parent):
        """Create settings control widgets"""
        row = 0
        
        # Sensitivity Settings
        ttk.Label(parent, text="Sensitivity Settings", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # X Sensitivity
        ttk.Label(parent, text="X Sensitivity:").grid(row=row, column=0, sticky=tk.W)
        self.x_sensitivity_var = tk.DoubleVar(value=self.calibration.sensitivity_x)
        x_sensitivity_scale = ttk.Scale(parent, from_=0.1, to=3.0, variable=self.x_sensitivity_var, orient=tk.HORIZONTAL)
        x_sensitivity_scale.grid(row=row, column=1, sticky=(tk.W, tk.E))
        self.x_sensitivity_label = ttk.Label(parent, text=f"{self.x_sensitivity_var.get():.2f}")
        self.x_sensitivity_label.grid(row=row, column=2)
        x_sensitivity_scale.config(command=lambda v: self.x_sensitivity_label.config(text=f"{float(v):.2f}"))
        row += 1
        
        # Y Sensitivity
        ttk.Label(parent, text="Y Sensitivity:").grid(row=row, column=0, sticky=tk.W)
        self.y_sensitivity_var = tk.DoubleVar(value=self.calibration.sensitivity_y)
        y_sensitivity_scale = ttk.Scale(parent, from_=0.1, to=3.0, variable=self.y_sensitivity_var, orient=tk.HORIZONTAL)
        y_sensitivity_scale.grid(row=row, column=1, sticky=(tk.W, tk.E))
        self.y_sensitivity_label = ttk.Label(parent, text=f"{self.y_sensitivity_var.get():.2f}")
        self.y_sensitivity_label.grid(row=row, column=2)
        y_sensitivity_scale.config(command=lambda v: self.y_sensitivity_label.config(text=f"{float(v):.2f}"))
        row += 1
        
        # Smoothing
        ttk.Label(parent, text="Smoothing:").grid(row=row, column=0, sticky=tk.W)
        self.smoothing_var = tk.DoubleVar(value=self.calibration.smoothing_alpha)
        smoothing_scale = ttk.Scale(parent, from_=0.0, to=0.8, variable=self.smoothing_var, orient=tk.HORIZONTAL)
        smoothing_scale.grid(row=row, column=1, sticky=(tk.W, tk.E))
        self.smoothing_label = ttk.Label(parent, text=f"{self.smoothing_var.get():.2f}")
        self.smoothing_label.grid(row=row, column=2)
        smoothing_scale.config(command=lambda v: self.smoothing_label.config(text=f"{float(v):.2f}"))
        row += 1
        
        # Deadzone
        ttk.Label(parent, text="Deadzone (pixels):").grid(row=row, column=0, sticky=tk.W)
        self.deadzone_var = tk.IntVar(value=self.calibration.deadzone_px)
        deadzone_scale = ttk.Scale(parent, from_=0, to=50, variable=self.deadzone_var, orient=tk.HORIZONTAL)
        deadzone_scale.grid(row=row, column=1, sticky=(tk.W, tk.E))
        self.deadzone_label = ttk.Label(parent, text=f"{self.deadzone_var.get()}")
        self.deadzone_label.grid(row=row, column=2)
        deadzone_scale.config(command=lambda v: self.deadzone_label.config(text=f"{int(float(v))}"))
        row += 1
        
        # Blink Detection Settings
        ttk.Label(parent, text="Blink Detection", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1
        
        # EAR Threshold
        ttk.Label(parent, text="EAR Threshold:").grid(row=row, column=0, sticky=tk.W)
        self.ear_threshold_var = tk.DoubleVar(value=self.calibration.ear_threshold)
        ear_scale = ttk.Scale(parent, from_=0.1, to=0.4, variable=self.ear_threshold_var, orient=tk.HORIZONTAL)
        ear_scale.grid(row=row, column=1, sticky=(tk.W, tk.E))
        self.ear_label = ttk.Label(parent, text=f"{self.ear_threshold_var.get():.3f}")
        self.ear_label.grid(row=row, column=2)
        ear_scale.config(command=lambda v: self.ear_label.config(text=f"{float(v):.3f}"))
        row += 1
        
        # Consecutive Frames
        ttk.Label(parent, text="Consecutive Frames:").grid(row=row, column=0, sticky=tk.W)
        self.consecutive_frames_var = tk.IntVar(value=self.calibration.ear_consecutive_frames)
        frames_scale = ttk.Scale(parent, from_=1, to=10, variable=self.consecutive_frames_var, orient=tk.HORIZONTAL)
        frames_scale.grid(row=row, column=1, sticky=(tk.W, tk.E))
        self.frames_label = ttk.Label(parent, text=f"{self.consecutive_frames_var.get()}")
        self.frames_label.grid(row=row, column=2)
        frames_scale.config(command=lambda v: self.frames_label.config(text=f"{int(float(v))}"))
        row += 1
        
        # Click Cooldown
        ttk.Label(parent, text="Click Cooldown (s):").grid(row=row, column=0, sticky=tk.W)
        self.cooldown_var = tk.DoubleVar(value=self.blink_config.click_cooldown)
        cooldown_scale = ttk.Scale(parent, from_=0.1, to=2.0, variable=self.cooldown_var, orient=tk.HORIZONTAL)
        cooldown_scale.grid(row=row, column=1, sticky=(tk.W, tk.E))
        self.cooldown_label = ttk.Label(parent, text=f"{self.cooldown_var.get():.2f}")
        self.cooldown_label.grid(row=row, column=2)
        cooldown_scale.config(command=lambda v: self.cooldown_label.config(text=f"{float(v):.2f}"))
        row += 1
        
        # Blink Actions
        ttk.Label(parent, text="Blink Actions", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1
        
        # Single Blink Action
        ttk.Label(parent, text="Single Blink:").grid(row=row, column=0, sticky=tk.W)
        self.single_blink_var = tk.StringVar(value=self.blink_config.single_blink_action)
        single_blink_combo = ttk.Combobox(parent, textvariable=self.single_blink_var, 
                                         values=["left_click", "right_click", "double_click", "none"])
        single_blink_combo.grid(row=row, column=1, sticky=(tk.W, tk.E))
        row += 1
        
        # Double Blink Action
        ttk.Label(parent, text="Double Blink:").grid(row=row, column=0, sticky=tk.W)
        self.double_blink_var = tk.StringVar(value=self.blink_config.double_blink_action)
        double_blink_combo = ttk.Combobox(parent, textvariable=self.double_blink_var,
                                         values=["left_click", "right_click", "double_click", "none"])
        double_blink_combo.grid(row=row, column=1, sticky=(tk.W, tk.E))
        row += 1
        
        # Long Blink Action
        ttk.Label(parent, text="Long Blink:").grid(row=row, column=0, sticky=tk.W)
        self.long_blink_var = tk.StringVar(value=self.blink_config.long_blink_action)
        long_blink_combo = ttk.Combobox(parent, textvariable=self.long_blink_var,
                                       values=["left_click", "right_click", "double_click", "none"])
        long_blink_combo.grid(row=row, column=1, sticky=(tk.W, tk.E))
        row += 1
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def create_camera_preview(self, parent):
        """Create camera preview widget"""
        # Create a label to display camera feed
        self.camera_label = ttk.Label(parent, text="Camera feed will appear here")
        self.camera_label.pack(expand=True, fill=tk.BOTH)
        
        # Status label
        self.status_label = ttk.Label(parent, text="Camera starting...")
        self.status_label.pack(pady=5)
    
    def start_camera_preview(self):
        """Start camera preview in a separate thread"""
        self.camera_active = True
        self.camera_thread = threading.Thread(target=self.camera_preview_loop, daemon=True)
        self.camera_thread.start()
    
    def camera_preview_loop(self):
        """Camera preview loop"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        while self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame = frame
                
                # Update GUI in main thread
                self.root.after(0, self.update_camera_display)
            time.sleep(0.03)  # ~30 FPS
        
        if self.cap:
            self.cap.release()
    
    def update_camera_display(self):
        """Update camera display in GUI"""
        if self.current_frame is not None:
            # Convert to PIL Image and then to PhotoImage
            image = Image.fromarray(self.current_frame)
            image = image.resize((320, 240), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image=image)
            
            self.camera_label.configure(image=photo)
            self.camera_label.image = photo  # Keep reference
            self.status_label.configure(text="Camera active")
    
    def save_settings(self):
        """Save current settings to calibration file"""
        # Update calibration object
        self.calibration.sensitivity_x = self.x_sensitivity_var.get()
        self.calibration.sensitivity_y = self.y_sensitivity_var.get()
        self.calibration.smoothing_alpha = self.smoothing_var.get()
        self.calibration.deadzone_px = self.deadzone_var.get()
        self.calibration.ear_threshold = self.ear_threshold_var.get()
        self.calibration.ear_consecutive_frames = self.consecutive_frames_var.get()
        
        # Update blink config
        self.blink_config.single_blink_action = self.single_blink_var.get()
        self.blink_config.double_blink_action = self.double_blink_var.get()
        self.blink_config.long_blink_action = self.long_blink_var.get()
        self.blink_config.click_cooldown = self.cooldown_var.get()
        
        # Save calibration
        self.calibration.save("calibration.json")
        
        # Save blink config
        with open("blink_config.json", "w") as f:
            json.dump(self.blink_config.__dict__, f, indent=2)
        
        messagebox.showinfo("Success", "Settings saved successfully!")
    
    def reset_defaults(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Reset calibration
            self.calibration = CalibrationData()
            
            # Reset blink config
            self.blink_config = BlinkConfig()
            
            # Update GUI variables
            self.x_sensitivity_var.set(self.calibration.sensitivity_x)
            self.y_sensitivity_var.set(self.calibration.sensitivity_y)
            self.smoothing_var.set(self.calibration.smoothing_alpha)
            self.deadzone_var.set(self.calibration.deadzone_px)
            self.ear_threshold_var.set(self.calibration.ear_threshold)
            self.consecutive_frames_var.set(self.calibration.ear_consecutive_frames)
            
            self.single_blink_var.set(self.blink_config.single_blink_action)
            self.double_blink_var.set(self.blink_config.double_blink_action)
            self.long_blink_var.set(self.blink_config.long_blink_action)
            self.cooldown_var.set(self.blink_config.click_cooldown)
            
            messagebox.showinfo("Reset Complete", "Settings reset to default values!")
    
    def start_calibration(self):
        """Start the calibration process"""
        # Stop camera preview
        self.camera_active = False
        time.sleep(0.1)  # Give thread time to stop
        
        # Close GUI and start main calibration
        self.root.destroy()
        
        # Start main application in calibration mode
        controller = EyeMouseController()
        controller.is_calibrating = True
        controller.run()
    
    def test_settings(self):
        """Test current settings with a temporary controller"""
        # Update calibration with current GUI values
        self.calibration.sensitivity_x = self.x_sensitivity_var.get()
        self.calibration.sensitivity_y = self.y_sensitivity_var.get()
        self.calibration.smoothing_alpha = self.smoothing_var.get()
        self.calibration.deadzone_px = self.deadzone_var.get()
        self.calibration.ear_threshold = self.ear_threshold_var.get()
        self.calibration.ear_consecutive_frames = self.consecutive_frames_var.get()
        
        # Save temporary calibration
        self.calibration.save("temp_calibration.json")
        
        messagebox.showinfo("Test Mode", "Test mode starting. Use ESC to return to configuration.")
        
        # Start test mode in separate thread
        def test_mode():
            controller = EyeMouseController()
            controller.calibration_file = "temp_calibration.json"
            controller.calibration = self.calibration
            controller.run()
        
        test_thread = threading.Thread(target=test_mode, daemon=True)
        test_thread.start()
    
    def on_closing(self):
        """Handle window closing"""
        self.camera_active = False
        time.sleep(0.1)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ConfigGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
