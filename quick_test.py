"""
Quick comprehensive test for Eye Mouse Control system
"""

import sys
import os
import traceback

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
    except ImportError as e:
        print(f"❌ MediaPipe import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import pyautogui
        print("✅ PyAutoGUI imported successfully")
    except ImportError as e:
        print(f"❌ PyAutoGUI import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("✅ PIL imported successfully")
    except ImportError as e:
        print(f"❌ PIL import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ Matplotlib imported successfully")
    except ImportError as e:
        print(f"❌ Matplotlib import failed: {e}")
        return False
    
    try:
        from scipy.signal import savgol_filter
        print("✅ SciPy imported successfully")
    except ImportError as e:
        print(f"❌ SciPy import failed: {e}")
        return False
    
    return True

def test_module_imports():
    """Test custom module imports"""
    print("\nTesting custom modules...")
    
    try:
        import eye_mouse_control
        print("✅ eye_mouse_control imported successfully")
    except ImportError as e:
        print(f"❌ eye_mouse_control import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        import config_gui
        print("✅ config_gui imported successfully")
    except ImportError as e:
        print(f"❌ config_gui import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        import advanced_filters
        print("✅ advanced_filters imported successfully")
    except ImportError as e:
        print(f"❌ advanced_filters import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        import test_system
        print("✅ test_system imported successfully")
    except ImportError as e:
        print(f"❌ test_system import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        import demo_script
        print("✅ demo_script imported successfully")
    except ImportError as e:
        print(f"❌ demo_script import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_class_creation():
    """Test class instantiation"""
    print("\nTesting class creation...")
    
    try:
        from eye_mouse_control import EyeMouseController, CalibrationData, BlinkConfig
        
        # Test CalibrationData
        cal = CalibrationData()
        print("✅ CalibrationData created successfully")
        
        # Test BlinkConfig
        blink = BlinkConfig()
        print("✅ BlinkConfig created successfully")
        
        # Test EyeMouseController
        controller = EyeMouseController()
        print("✅ EyeMouseController created successfully")
        
        # Test advanced filters
        from advanced_filters import MultiFilterPipeline
        pipeline = MultiFilterPipeline()
        print("✅ MultiFilterPipeline created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Class creation failed: {e}")
        traceback.print_exc()
        return False

def test_camera_access():
    """Test camera access"""
    print("\nTesting camera access...")
    
    try:
        import cv2
        
        # Try different camera indices
        for camera_index in range(3):  # Try 0, 1, 2
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera {camera_index} working: {frame.shape[1]}x{frame.shape[0]}")
                    cap.release()
                    return True
                else:
                    cap.release()
                    continue
            else:
                continue
        
        print("⚠️  No camera available (this is OK if no camera is connected)")
        return True  # Don't fail the test for missing camera
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_mediapipe_face():
    """Test MediaPipe face detection"""
    print("\nTesting MediaPipe face detection...")
    
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
        
        # Create a test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Initialize MediaPipe
        mp_face = mp.solutions.face_mesh
        face_mesh = mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Process test image
        rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_image)
        
        print("✅ MediaPipe Face Mesh initialized successfully")
        face_mesh.close()
        return True
        
    except Exception as e:
        print(f"❌ MediaPipe test failed: {e}")
        traceback.print_exc()
        return False

def test_file_operations():
    """Test file operations"""
    print("\nTesting file operations...")
    
    try:
        # Test calibration save/load
        from eye_mouse_control import CalibrationData
        
        cal = CalibrationData()
        cal.save("test_calibration.json")
        
        loaded_cal = CalibrationData.load("test_calibration.json")
        
        if os.path.exists("test_calibration.json"):
            os.remove("test_calibration.json")
        
        print("✅ Calibration save/load working")
        
        # Test config files
        import json
        test_data = {"test": "data"}
        with open("test_config.json", "w") as f:
            json.dump(test_data, f)
        
        with open("test_config.json", "r") as f:
            loaded_data = json.load(f)
        
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        
        print("✅ JSON file operations working")
        return True
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("EYE MOUSE CONTROL - COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_imports),
        ("Custom Modules", test_module_imports),
        ("Class Creation", test_class_creation),
        ("Camera Access", test_camera_access),
        ("MediaPipe Face", test_mediapipe_face),
        ("File Operations", test_file_operations),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} : {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is ready!")
        return 0
    else:
        print("⚠️  Some tests failed - Check the issues above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
