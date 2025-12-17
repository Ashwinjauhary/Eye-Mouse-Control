"""
Demo script for Eye Mouse Control
Shows the system capabilities and provides a guided tour
"""

import cv2
import time
import numpy as np
from pathlib import Path
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_demo_video():
    """Create a demonstration video showing system features"""
    
    # Create demo frames
    frames = []
    width, height = 640, 480
    
    # Demo scenarios
    scenarios = [
        ("Welcome to Eye Mouse Control", (0, 0, 255)),
        ("Move your head to control the cursor", (0, 255, 0)),
        ("Blink to click - Single blink = Left click", (255, 255, 0)),
        ("Double blink = Double click", (255, 165, 0)),
        ("Long blink = Right click", (255, 0, 255)),
        ("Press SPACE to pause/resume", (0, 255, 255)),
        ("Press C to calibrate", (255, 0, 0)),
        ("Press ESC to exit", (255, 255, 255)),
        ("Starting camera feed...", (0, 255, 0)),
    ]
    
    for text, color in scenarios:
        # Create frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add text
        cv2.putText(frame, text, (50, height//2), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, "Eye Mouse Control Demo", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add progress indicator
        progress = (scenarios.index((text, color)) + 1) / len(scenarios)
        bar_width = int(width * progress)
        cv2.rectangle(frame, (0, height - 20), (bar_width, height), (0, 255, 0), -1)
        
        frames.append(frame)
    
    return frames

def show_demo():
    """Run the demo presentation"""
    
    print("Eye Mouse Control - Demo")
    print("=" * 40)
    print()
    print("This demo will show you the main features of the Eye Mouse Control system.")
    print("Press any key to advance through the demo slides.")
    print()
    print("Starting demo in 3 seconds...")
    
    time.sleep(3)
    
    # Create demo frames
    demo_frames = create_demo_video()
    
    # Show demo
    for i, frame in enumerate(demo_frames):
        cv2.imshow("Eye Mouse Control - Demo", frame)
        
        # Wait for key press or timeout
        key = cv2.waitKey(3000) & 0xFF  # 3 second timeout
        
        if key == 27:  # ESC
            break
        elif key != 255:  # Any key pressed
            continue
    
    cv2.destroyAllWindows()

def show_features():
    """Display system features"""
    
    features = [
        "🎯 Head Movement Control",
        "👁️  Blink Detection",
        "🖱️  Multiple Click Types",
        "⚙️  Calibration System",
        "🎛️  Configuration GUI",
        "🔧  Advanced Filtering",
        "📊  Performance Monitoring",
        "🛡️  Safety Features",
        "📝  Comprehensive Logging",
        "🧪  Testing Suite",
    ]
    
    print("\nEye Mouse Control - Features")
    print("=" * 40)
    
    for feature in features:
        print(f"  {feature}")
        time.sleep(0.2)
    
    print("\n" + "=" * 40)

def show_quick_start():
    """Show quick start guide"""
    
    guide = [
        "1. Install dependencies: pip install -r requirements.txt",
        "2. Run the main application: python eye_mouse_control.py",
        "3. Calibrate the system: Press 'C' when prompted",
        "4. Use the system:",
        "   - Move head to control cursor",
        "   - Blink to click",
        "   - Press SPACE to pause",
        "   - Press ESC to exit",
        "5. Configure settings: python config_gui.py",
        "6. Test system: python test_system.py",
    ]
    
    print("\nQuick Start Guide")
    print("=" * 40)
    
    for step in guide:
        print(f"  {step}")
        time.sleep(0.3)
    
    print("\n" + "=" * 40)

def check_system():
    """Check system requirements"""
    
    print("Checking system requirements...")
    
    # Check Python version
    import sys
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    else:
        print("✅ Python version OK")
    
    # Check OpenCV
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV not installed")
        return False
    
    # Check MediaPipe
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe version: {mp.__version__}")
    except ImportError:
        print("❌ MediaPipe not installed")
        return False
    
    # Check NumPy
    try:
        import numpy as np
        print(f"✅ NumPy version: {np.__version__}")
    except ImportError:
        print("❌ NumPy not installed")
        return False
    
    # Check PyAutoGUI
    try:
        import pyautogui
        print(f"✅ PyAutoGUI version: {pyautogui.__version__}")
    except ImportError:
        print("❌ PyAutoGUI not installed")
        return False
    
    # Check camera
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera working: {frame.shape[1]}x{frame.shape[0]}")
            else:
                print("❌ Camera not providing frames")
                return False
        else:
            print("❌ Camera not accessible")
            return False
        cap.release()
    except Exception as e:
        print(f"❌ Camera error: {e}")
        return False
    
    print("✅ All requirements met!")
    return True

def main():
    """Main demo function"""
    
    print("Eye Mouse Control - Interactive Demo")
    print("=" * 50)
    print()
    
    while True:
        print("Choose an option:")
        print("1. System Check")
        print("2. Feature Overview")
        print("3. Quick Start Guide")
        print("4. Visual Demo")
        print("5. Run Main Application")
        print("6. Exit")
        print()
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            print()
            check_system()
            print()
        elif choice == "2":
            print()
            show_features()
            print()
        elif choice == "3":
            print()
            show_quick_start()
            print()
        elif choice == "4":
            print()
            show_demo()
            print()
        elif choice == "5":
            print()
            print("Starting Eye Mouse Control...")
            print("Press ESC to exit, SPACE to pause/resume, C to calibrate")
            time.sleep(2)
            
            # Import and run main application
            try:
                from eye_mouse_control import EyeMouseController
                controller = EyeMouseController()
                controller.run()
            except Exception as e:
                print(f"Error starting application: {e}")
                print("Make sure all dependencies are installed.")
            
            print()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            print()
        
        input("Press Enter to continue...")
        print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    main()
