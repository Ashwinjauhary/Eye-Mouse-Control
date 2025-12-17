"""
Installation verification script for Eye Mouse Control
"""

import subprocess
import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version >= (3, 9):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\nChecking dependencies...")
    
    required_packages = [
        'opencv-python',
        'mediapipe', 
        'numpy',
        'pyautogui',
        'pynput',
        'scipy',
        'pillow',
        'matplotlib'
    ]
    
    all_ok = True
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"✅ {package} - {cv2.__version__}")
            elif package == 'pillow':
                import PIL
                print(f"✅ {package} - {PIL.__version__}")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {package} - {version}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_files():
    """Check if all required files exist"""
    print("\nChecking project files...")
    
    required_files = [
        'eye_mouse_control.py',
        'config_gui.py',
        'advanced_filters.py',
        'test_system.py',
        'demo_script.py',
        'requirements.txt',
        'README.md',
        'setup.py',
        'run.bat',
        'quick_test.py'
    ]
    
    all_ok = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_ok = False
    
    return all_ok

def install_missing():
    """Install missing dependencies"""
    print("\nInstalling missing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def main():
    """Main verification"""
    print("=" * 50)
    print("EYE MOUSE CONTROL - INSTALLATION VERIFICATION")
    print("=" * 50)
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check files
    files_ok = check_files()
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    print(f"Python Version: {'✅ OK' if python_ok else '❌ NEEDS UPDATE'}")
    print(f"Dependencies: {'✅ OK' if deps_ok else '❌ NEEDS INSTALLATION'}")
    print(f"Project Files: {'✅ OK' if files_ok else '❌ INCOMPLETE'}")
    
    if python_ok and deps_ok and files_ok:
        print("\n🎉 INSTALLATION COMPLETE - System ready!")
        print("\nTo start the application:")
        print("  python eye_mouse_control.py")
        print("\nTo configure settings:")
        print("  python config_gui.py")
        print("\nTo run tests:")
        print("  python quick_test.py")
        return 0
    else:
        print("\n⚠️  INSTALLATION INCOMPLETE")
        
        if not python_ok:
            print("\nPlease install Python 3.9 or higher")
        
        if not deps_ok:
            print("\nInstalling missing dependencies...")
            if install_missing():
                print("✅ Dependencies installed - Please run verification again")
            else:
                print("❌ Manual installation required:")
                print("  pip install -r requirements.txt")
        
        if not files_ok:
            print("\nSome project files are missing - Please re-download the project")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nPress Enter to exit...")
    sys.exit(exit_code)
