"""
Production-ready error handling and logging for Eye Mouse Control
"""

import logging
import sys
import traceback
import os
import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import threading

class ProductionErrorHandler:
    """Production-ready error handling system"""
    
    def __init__(self, app_name="EyeMouseControl"):
        self.app_name = app_name
        self.log_dir = Path.home() / f".{app_name.lower()}"
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Setup crash reporting
        self.setup_crash_handler()
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        
        # Create log file with timestamp
        log_file = self.log_dir / f"{self.app_name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Create logger
        self.logger = logging.getLogger(self.app_name)
        self.logger.info(f"=== {self.app_name} v1.0.0 Started ===")
        
    def setup_crash_handler(self):
        """Setup global exception handler"""
        
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions"""
            
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            self.logger.critical("Uncaught exception occurred", exc_info=(exc_type, exc_value, exc_traceback))
            
            # Create crash report
            crash_report = {
                "timestamp": datetime.now().isoformat(),
                "error_type": exc_type.__name__,
                "error_message": str(exc_value),
                "traceback": traceback.format_exception(exc_type, exc_value, exc_traceback),
                "system_info": self.get_system_info()
            }
            
            # Save crash report
            crash_file = self.log_dir / f"crash_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(crash_file, 'w', encoding='utf-8') as f:
                json.dump(crash_report, f, indent=2, ensure_ascii=False)
            
            # Show user-friendly error message
            self.show_error_dialog(exc_value, crash_file)
            
        sys.excepthook = handle_exception
        
    def get_system_info(self):
        """Get system information for debugging"""
        import platform
        import cv2
        
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "opencv_version": cv2.__version__,
            "executable": sys.executable
        }
        
    def show_error_dialog(self, error, crash_file):
        """Show user-friendly error dialog"""
        
        def show_dialog():
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            message = f"""
{self.app_name} encountered an error and needs to close.

Error: {str(error)}

A crash report has been saved to:
{crash_file}

Please report this issue to our support team.
            """
            
            messagebox.showerror(f"{self.app_name} - Error", message.strip())
            root.destroy()
        
        # Run in separate thread to avoid blocking
        threading.Thread(target=show_dialog, daemon=True).start()
        
    def log_error(self, error, context=""):
        """Log an error with context"""
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
        
    def log_warning(self, message, context=""):
        """Log a warning message"""
        self.logger.warning(f"Warning in {context}: {message}")
        
    def log_info(self, message):
        """Log an info message"""
        self.logger.info(message)
        
    def get_log_files(self):
        """Get list of log files"""
        return list(self.log_dir.glob("*.log"))
        
    def cleanup_old_logs(self, days_to_keep=7):
        """Clean up old log files"""
        import time
        
        current_time = time.time()
        for log_file in self.get_log_files():
            file_age = current_time - log_file.stat().st_mtime
            if file_age > days_to_keep * 24 * 3600:  # Convert days to seconds
                log_file.unlink()
                self.logger.info(f"Deleted old log file: {log_file}")

# Global error handler instance
error_handler = None

def initialize_error_handler():
    """Initialize the global error handler"""
    global error_handler
    if error_handler is None:
        error_handler = ProductionErrorHandler()
    return error_handler

def get_error_handler():
    """Get the global error handler instance"""
    return error_handler
