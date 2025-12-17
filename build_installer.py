"""
Script to create a professional installer for Eye Mouse Control
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_installer_package():
    """Create a distributable package with installer"""
    
    # Paths
    project_root = Path.cwd()
    dist_dir = project_root / "dist"
    package_dir = project_root / "installer_package"
    
    # Clean and create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy executable
    exe_path = dist_dir / "EyeMouseControl.exe"
    shutil.copy2(exe_path, package_dir / "EyeMouseControl.exe")
    
    # Copy documentation
    shutil.copy2(project_root / "README.md", package_dir / "README.md")
    
    # Create installation instructions
    install_instructions = """Eye Mouse Control - Installation Instructions
===============================================

QUICK START:
1. Double-click EyeMouseControl.exe to run the application
2. Allow camera access when prompted
3. Use ESC to exit, SPACE to pause/resume, 'c' to calibrate

SYSTEM REQUIREMENTS:
- Windows 10 or later
- Webcam or built-in camera
- 2GB RAM minimum
- 100MB free disk space

FEATURES:
- Hands-free mouse control using head movement
- Eye blink detection for clicking
- Configurable sensitivity settings
- Real-time visual feedback
- Safety hotkeys for quick exit

TROUBLESHOOTING:
- If camera doesn't work, check Windows privacy settings
- For smooth performance, close other camera applications
- Run as administrator if mouse control doesn't work

SUPPORT:
- Press 'h' in the application for help
- Check README.md for detailed documentation
"""
    
    with open(package_dir / "INSTALL.txt", "w") as f:
        f.write(install_instructions)
    
    # Create a simple batch file for easy launch
    batch_file = """@echo off
title Eye Mouse Control
echo Starting Eye Mouse Control...
echo.
echo Press ESC to exit, SPACE to pause, 'c' to calibrate
echo.
EyeMouseControl.exe
pause
"""
    
    with open(package_dir / "Start Eye Mouse Control.bat", "w") as f:
        f.write(batch_file)
    
    # Create ZIP package
    zip_name = "EyeMouseControl_v1.0_Portable.zip"
    with zipfile.ZipFile(project_root / zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Installer package created: {zip_name}")
    print(f"📦 Package contents:")
    for item in package_dir.iterdir():
        print(f"   - {item.name}")
    
    # Get file sizes
    exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
    zip_size = (project_root / zip_name).stat().st_size / (1024 * 1024)  # MB
    
    print(f"\n📊 File sizes:")
    print(f"   - Executable: {exe_size:.1f} MB")
    print(f"   - ZIP Package: {zip_size:.1f} MB")
    
    return zip_name

if __name__ == "__main__":
    create_installer_package()
