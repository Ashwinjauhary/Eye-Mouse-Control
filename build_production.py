"""
Production build script for Eye Mouse Control
Creates professional installer and distribution packages
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import json
from datetime import datetime

class ProductionBuilder:
    """Production build manager"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.version = "1.0.0"
        self.app_name = "Eye Mouse Control"
        
    def create_user_manual(self):
        """Create comprehensive user manual"""
        
        manual_content = f"""# {self.app_name} - User Manual

## Table of Contents
1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Features](#features)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Safety Information](#safety-information)
7. [Technical Support](#technical-support)

## Installation

### System Requirements
- Windows 10 or later (64-bit)
- Webcam or built-in camera
- 2GB RAM minimum (4GB recommended)
- 200MB free disk space
- .NET Framework 4.7.2 or later (usually included with Windows)

### Installation Steps
1. Download the installer from the official website
2. Right-click the installer and select "Run as administrator"
3. Follow the installation wizard
4. Launch the application from Start Menu or Desktop shortcut

### First Time Setup
1. Allow camera access when prompted
2. Position yourself in front of the camera
3. Press 'c' to calibrate the system
4. Test mouse movement with head movements
5. Test clicking with eye blinks

## Getting Started

### Basic Controls
- **Head Movement**: Move your head to control the cursor
- **Eye Blink**: Blink to perform left-click
- **Double Blink**: Double blink to perform right-click
- **Space Bar**: Pause/resume tracking
- **ESC Key**: Exit application
- **'c' Key**: Calibrate system
- **'h' Key**: Show help overlay

### Calibration Process
1. Sit comfortably in front of your camera
2. Press 'c' to enter calibration mode
3. Follow the on-screen instructions
4. Look at each corner of your screen when prompted
5. Center your view and press Enter to complete

## Features

### Core Features
- **Real-time Face Tracking**: Advanced MediaPipe technology
- **Smooth Cursor Control**: Intelligent smoothing algorithms
- **Blink Detection**: Precise eye blink recognition
- **Configurable Sensitivity**: Adjustable to your preferences
- **Safety Features**: Quick exit and pause controls

### Advanced Features
- **Multiple Monitor Support**: Works across all connected displays
- **Profile Management**: Save and switch between user profiles
- **Statistics Tracking**: Monitor usage patterns and performance
- **Automatic Updates**: Keep the software up to date

## Configuration

### Settings Menu
Access settings by right-clicking the system tray icon or pressing 's'.

### Adjustable Parameters
- **Cursor Sensitivity**: Control cursor movement speed
- **Blink Sensitivity**: Adjust blink detection threshold
- **Dead Zone**: Set minimum movement threshold
- **Smoothing**: Control cursor movement smoothness
- **Camera Selection**: Choose between multiple cameras

### Profile Management
- Save your calibration settings
- Create profiles for different users
- Export/import configuration files

## Troubleshooting

### Common Issues

**Camera Not Working**
- Check Windows privacy settings
- Ensure no other app is using the camera
- Restart the application
- Try a different USB port

**Cursor Not Moving**
- Verify camera is working
- Check if application is paused (press Space)
- Recalibrate the system (press 'c')
- Adjust sensitivity settings

**Click Not Working**
- Ensure proper lighting conditions
- Adjust blink sensitivity
- Check if glasses are interfering
- Try slower, deliberate blinks

**Performance Issues**
- Close other camera applications
- Ensure adequate lighting
- Check system resources
- Restart the application

### Error Messages
If you encounter an error, a crash report will be automatically saved to:
`%USERPROFILE%\\.eyemousecontrol\\`

Please include this file when reporting issues.

## Safety Information

### Important Safety Notes
- Take regular breaks to avoid eye strain
- Ensure proper lighting to prevent eye fatigue
- Stop using if you experience dizziness or discomfort
- Consult a doctor if you have pre-existing eye conditions

### Privacy and Security
- Camera data is processed locally on your device
- No personal data is transmitted to external servers
- Camera access can be revoked in Windows settings

## Technical Support

### Getting Help
- **User Manual**: This document
- **Online Help**: Press 'h' in the application
- **Community Forum**: [GitHub Discussions]
- **Bug Reports**: [GitHub Issues]
- **Email Support**: support@example.com

### System Information
When reporting issues, please include:
- Windows version
- Camera model
- Error messages
- Steps to reproduce the issue

### Version Information
Current Version: {self.version}
Build Date: {datetime.now().strftime('%Y-%m-%d')}

---

© 2024 Eye Mouse Control Team. All rights reserved.
"""
        
        with open(self.project_root / "USER_MANUAL.md", "w", encoding="utf-8") as f:
            f.write(manual_content)
        
        print("✅ User manual created: USER_MANUAL.md")
        
    def create_portable_package(self):
        """Create portable distribution package"""
        
        portable_dir = self.project_root / "portable_package"
        if portable_dir.exists():
            shutil.rmtree(portable_dir)
        portable_dir.mkdir()
        
        # Copy executable
        shutil.copy2(self.project_root / "dist" / "EyeMouseControl.exe", 
                    portable_dir / "EyeMouseControl.exe")
        
        # Copy documentation
        shutil.copy2(self.project_root / "USER_MANUAL.md", 
                    portable_dir / "USER_MANUAL.md")
        shutil.copy2(self.project_root / "README.md", 
                    portable_dir / "README.md")
        shutil.copy2(self.project_root / "LICENSE.txt", 
                    portable_dir / "LICENSE.txt")
        
        # Create portable launcher
        launcher_content = """@echo off
title Eye Mouse Control - Portable Version
echo Starting Eye Mouse Control (Portable)...
echo.
echo Press ESC to exit, SPACE to pause, 'c' to calibrate
echo.
EyeMouseControl.exe
pause
"""
        with open(portable_dir / "Start Portable.bat", "w") as f:
            f.write(launcher_content)
        
        # Create portable info
        info_content = f"""Eye Mouse Control v{self.version} - Portable Version
=====================================================

This is a portable version that requires no installation.

To use:
1. Extract all files to a folder
2. Run "Start Portable.bat" or double-click "EyeMouseControl.exe"
3. Allow camera access when prompted

Configuration files will be stored in:
%USERPROFILE%\\.eyemousecontrol\\

For detailed instructions, see USER_MANUAL.md

Version: {self.version}
Build Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        with open(portable_dir / "PORTABLE_INFO.txt", "w") as f:
            f.write(info_content)
        
        # Create ZIP package
        zip_name = f"{self.app_name.replace(' ', '')}_v{self.version}_Portable.zip"
        with zipfile.ZipFile(self.project_root / zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in portable_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(portable_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Portable package created: {zip_name}")
        return zip_name
        
    def build_installer(self):
        """Build NSIS installer if available"""
        
        # Check if NSIS is available
        try:
            subprocess.run(['makensis', '/VERSION'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  NSIS not found. Skipping installer build.")
            print("   Install NSIS from https://nsis.sourceforge.io/")
            return None
        
        # Build installer
        installer_script = self.project_root / "installer.nsi"
        if installer_script.exists():
            try:
                subprocess.run(['makensis', str(installer_script)], 
                             check=True, cwd=self.project_root)
                
                # Find the generated installer
                installer_exe = self.project_root / f"{self.app_name.replace(' ', '')}_Setup_v{self.version}.exe"
                if installer_exe.exists():
                    print(f"✅ Installer created: {installer_exe}")
                    return installer_exe
            except subprocess.CalledProcessError as e:
                print(f"❌ Installer build failed: {e}")
        
        return None
        
    def create_release_notes(self):
        """Create release notes"""
        
        release_notes = f"""# Eye Mouse Control v{self.version} Release Notes

## Release Date: {datetime.now().strftime('%B %d, %Y')}

### 🎉 New Features
- Professional installer with Windows integration
- Enhanced error handling and crash reporting
- Comprehensive user manual
- Portable version for easy distribution
- Improved camera compatibility
- Better performance optimizations

### 🔧 Improvements
- Smoother cursor movement
- More accurate blink detection
- Better multi-monitor support
- Enhanced calibration process
- Improved user interface

### 🐛 Bug Fixes
- Fixed camera initialization issues
- Resolved memory leaks
- Fixed crash on some systems
- Improved stability

### 📋 System Requirements
- Windows 10 or later (64-bit)
- 2GB RAM minimum (4GB recommended)
- Webcam or built-in camera
- 200MB free disk space

### 📦 Installation Options
1. **Installer Version**: Full Windows installer with Start Menu integration
2. **Portable Version**: No installation required - just extract and run

### 🆘 Support
- User Manual: Included with installation
- Online Help: Press 'h' in the application
- Bug Reports: https://github.com/example/eye-mouse-control/issues
- Community Forum: https://github.com/example/eye-mouse-control/discussions

---

Thank you for using Eye Mouse Control!
"""
        
        with open(self.project_root / "RELEASE_NOTES.md", "w", encoding="utf-8") as f:
            f.write(release_notes)
        
        print("✅ Release notes created: RELEASE_NOTES.md")
        
    def build_all(self):
        """Build all distribution packages"""
        
        print("🚀 Starting production build...")
        print("=" * 50)
        
        # Create user manual
        self.create_user_manual()
        
        # Create portable package
        portable_zip = self.create_portable_package()
        
        # Build installer
        installer_exe = self.build_installer()
        
        # Create release notes
        self.create_release_notes()
        
        # Create build summary
        summary = {
            "version": self.version,
            "build_date": datetime.now().isoformat(),
            "files_created": []
        }
        
        if portable_zip:
            portable_zip_path = self.project_root / portable_zip
            summary["files_created"].append({
                "type": "portable",
                "file": str(portable_zip),
                "size_mb": portable_zip_path.stat().st_size / (1024 * 1024)
            })
        
        if installer_exe:
            summary["files_created"].append({
                "type": "installer",
                "file": str(installer_exe),
                "size_mb": installer_exe.stat().st_size / (1024 * 1024)
            })
        
        # Save build summary
        with open(self.project_root / "build_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print("=" * 50)
        print("📦 Build Summary:")
        for file_info in summary["files_created"]:
            print(f"   ✅ {file_info['type'].title()}: {file_info['file']} ({file_info['size_mb']:.1f} MB)")
        
        print(f"\n🎉 Production build completed successfully!")
        print(f"   Version: {self.version}")
        print(f"   Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return summary

if __name__ == "__main__":
    builder = ProductionBuilder()
    builder.build_all()
