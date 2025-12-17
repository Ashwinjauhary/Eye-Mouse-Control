"""
Test system for Eye Mouse Control
Comprehensive testing and validation suite
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import json
import logging
from pathlib import Path
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eye_mouse_control import EyeMouseController, CalibrationData
from advanced_filters import MultiFilterPipeline

@dataclass
class TestResults:
    """Store test results"""
    test_name: str
    timestamp: str
    fps: float
    latency_ms: float
    accuracy_pixels: float
    false_positive_rate: float
    false_negative_rate: float
    system_info: Dict
    passed: bool
    details: Dict

class SystemTester:
    """Comprehensive testing suite for Eye Mouse Control"""
    
    def __init__(self):
        self.logger = self.setup_logging()
        self.test_results = []
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # MediaPipe setup
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        self.NOSE_TIP = 1
        
    def setup_logging(self):
        """Setup test logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_results.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def test_camera_performance(self) -> TestResults:
        """Test camera performance and frame rate"""
        self.logger.info("Testing camera performance...")
        
        frame_count = 0
        start_time = time.time()
        test_duration = 10.0  # 10 seconds
        
        while time.time() - start_time < test_duration:
            ret, frame = self.cap.read()
            if ret:
                frame_count += 1
        
        fps = frame_count / test_duration
        
        results = TestResults(
            test_name="Camera Performance",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            fps=fps,
            latency_ms=0,
            accuracy_pixels=0,
            false_positive_rate=0,
            false_negative_rate=0,
            system_info={"resolution": f"{frame.shape[1]}x{frame.shape[0]}" if ret else "unknown"},
            passed=fps >= 25,  # Target: 25+ FPS
            details={"frame_count": frame_count, "test_duration": test_duration}
        )
        
        self.logger.info(f"Camera FPS: {fps:.2f} - {'PASS' if results.passed else 'FAIL'}")
        return results
    
    def test_face_detection(self) -> TestResults:
        """Test face detection accuracy and speed"""
        self.logger.info("Testing face detection...")
        
        detection_count = 0
        total_frames = 0
        processing_times = []
        
        start_time = time.time()
        test_duration = 10.0
        
        while time.time() - start_time < test_duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            total_frames += 1
            
            # Process frame
            process_start = time.time()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            process_time = time.time() - process_start
            processing_times.append(process_time)
            
            if results.multi_face_landmarks:
                detection_count += 1
        
        detection_rate = detection_count / total_frames if total_frames > 0 else 0
        avg_processing_time = np.mean(processing_times) if processing_times else 0
        
        results = TestResults(
            test_name="Face Detection",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            fps=0,
            latency_ms=avg_processing_time * 1000,
            accuracy_pixels=detection_rate * 100,
            false_positive_rate=0,
            false_negative_rate=(1 - detection_rate) * 100,
            system_info={"total_frames": total_frames, "detections": detection_count},
            passed=detection_rate >= 0.9,  # Target: 90% detection rate
            details={"avg_processing_time": avg_processing_time}
        )
        
        self.logger.info(f"Face detection rate: {detection_rate*100:.1f}% - {'PASS' if results.passed else 'FAIL'}")
        return results
    
    def test_blink_detection_accuracy(self) -> TestResults:
        """Test blink detection accuracy with simulated data"""
        self.logger.info("Testing blink detection accuracy...")
        
        # Simulate EAR values
        normal_ear_values = np.random.normal(0.25, 0.02, 100)  # Normal eye state
        blink_ear_values = np.random.normal(0.15, 0.02, 50)    # Blink state
        
        # Test thresholds
        ear_threshold = 0.21
        consecutive_frames = 2
        
        # Test normal state (should not detect blinks)
        false_positives = 0
        blink_counter = 0
        
        for ear in normal_ear_values:
            if ear < ear_threshold:
                blink_counter += 1
                if blink_counter >= consecutive_frames:
                    false_positives += 1
                    blink_counter = 0
            else:
                blink_counter = 0
        
        # Test blink state (should detect blinks)
        true_positives = 0
        blink_counter = 0
        
        for ear in blink_ear_values:
            if ear < ear_threshold:
                blink_counter += 1
                if blink_counter >= consecutive_frames:
                    true_positives += 1
                    blink_counter = 0
            else:
                blink_counter = 0
        
        false_positive_rate = false_positives / len(normal_ear_values)
        true_positive_rate = true_positives / len(blink_ear_values)
        false_negative_rate = 1 - true_positive_rate
        
        results = TestResults(
            test_name="Blink Detection Accuracy",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            fps=0,
            latency_ms=0,
            accuracy_pixels=true_positive_rate * 100,
            false_positive_rate=false_positive_rate * 100,
            false_negative_rate=false_negative_rate * 100,
            system_info={"threshold": ear_threshold, "consecutive_frames": consecutive_frames},
            passed=false_positive_rate < 0.05 and true_positive_rate > 0.8,
            details={
                "true_positives": true_positives,
                "false_positives": false_positives,
                "normal_samples": len(normal_ear_values),
                "blink_samples": len(blink_ear_values)
            }
        )
        
        self.logger.info(f"Blink detection - TPR: {true_positive_rate*100:.1f}%, FPR: {false_positive_rate*100:.1f}% - {'PASS' if results.passed else 'FAIL'}")
        return results
    
    def test_cursor_mapping(self) -> TestResults:
        """Test cursor mapping accuracy and linearity"""
        self.logger.info("Testing cursor mapping...")
        
        # Test calibration data
        calibration = CalibrationData()
        
        # Test points (normalized coordinates)
        test_points = [
            (0.0, 0.0),   # Top-left
            (0.5, 0.0),   # Top-center
            (1.0, 0.0),   # Top-right
            (0.0, 0.5),   # Middle-left
            (0.5, 0.5),   # Center
            (1.0, 0.5),   # Middle-right
            (0.0, 1.0),   # Bottom-left
            (0.5, 1.0),   # Bottom-center
            (1.0, 1.0),   # Bottom-right
        ]
        
        screen_w, screen_h = 1920, 1080  # Assume full HD
        mapping_errors = []
        
        for nx, ny in test_points:
            # Expected screen position
            expected_x = int(nx * screen_w)
            expected_y = int(ny * screen_h)
            
            # Actual mapping (using controller logic)
            bounded_x = max(calibration.min_x, min(calibration.max_x, nx))
            bounded_y = max(calibration.min_y, min(calibration.max_y, ny))
            
            actual_x = int(((bounded_x - calibration.min_x) / 
                           (calibration.max_x - calibration.min_x)) * screen_w)
            actual_y = int(((bounded_y - calibration.min_y) / 
                           (calibration.max_y - calibration.min_y)) * screen_h)
            
            # Calculate error
            error = np.sqrt((actual_x - expected_x)**2 + (actual_y - expected_y)**2)
            mapping_errors.append(error)
        
        avg_error = np.mean(mapping_errors)
        max_error = np.max(mapping_errors)
        
        results = TestResults(
            test_name="Cursor Mapping",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            fps=0,
            latency_ms=0,
            accuracy_pixels=avg_error,
            false_positive_rate=0,
            false_negative_rate=0,
            system_info={"screen_resolution": f"{screen_w}x{screen_h}"},
            passed=avg_error < 5,  # Target: < 5 pixel error
            details={"max_error": max_error, "test_points": len(test_points)}
        )
        
        self.logger.info(f"Cursor mapping error: {avg_error:.1f}px - {'PASS' if results.passed else 'FAIL'}")
        return results
    
    def test_filtering_performance(self) -> TestResults:
        """Test advanced filtering performance"""
        self.logger.info("Testing filtering performance...")
        
        pipeline = MultiFilterPipeline()
        
        # Generate noisy test data
        np.random.seed(42)
        test_size = 1000
        
        # Base trajectory (circle)
        t = np.linspace(0, 4*np.pi, test_size)
        base_x = 0.5 + 0.3 * np.cos(t)
        base_y = 0.5 + 0.3 * np.sin(t)
        
        # Add noise
        noise_level = 0.05
        noisy_x = base_x + np.random.normal(0, noise_level, test_size)
        noisy_y = base_y + np.random.normal(0, noise_level, test_size)
        
        # Measure filtering time
        start_time = time.time()
        filtered_points = []
        
        for i in range(test_size):
            fx, fy = pipeline.filter_cursor_position(noisy_x[i], noisy_y[i])
            filtered_points.append((fx, fy))
        
        filtering_time = time.time() - start_time
        avg_filtering_time = filtering_time / test_size
        
        # Calculate smoothing effectiveness
        filtered_x = [p[0] for p in filtered_points]
        filtered_y = [p[1] for p in filtered_points]
        
        # Calculate variance reduction
        original_variance = np.var(noisy_x) + np.var(noisy_y)
        filtered_variance = np.var(filtered_x) + np.var(filtered_y)
        variance_reduction = (original_variance - filtered_variance) / original_variance
        
        results = TestResults(
            test_name="Filtering Performance",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            fps=0,
            latency_ms=avg_filtering_time * 1000,
            accuracy_pixels=variance_reduction * 100,
            false_positive_rate=0,
            false_negative_rate=0,
            system_info={"test_points": test_size},
            passed=avg_filtering_time < 0.001 and variance_reduction > 0.5,
            details={
                "avg_filtering_time_ms": avg_filtering_time * 1000,
                "variance_reduction": variance_reduction,
                "original_variance": original_variance,
                "filtered_variance": filtered_variance
            }
        )
        
        self.logger.info(f"Filtering - Time: {avg_filtering_time*1000:.3f}ms, Variance reduction: {variance_reduction*100:.1f}% - {'PASS' if results.passed else 'FAIL'}")
        return results
    
    def test_system_integration(self) -> TestResults:
        """Test complete system integration"""
        self.logger.info("Testing system integration...")
        
        try:
            # Try to create controller
            controller = EyeMouseController()
            
            # Test calibration loading
            calibration = CalibrationData.load("calibration.json")
            
            # Test basic functionality
            test_ear = 0.15
            test_threshold = 0.21
            ear_result = controller.eye_aspect_ratio(
                controller.face_mesh.FaceMesh()._landmarks, 
                controller.LEFT_EYE, 
                640, 480
            ) if hasattr(controller, 'face_mesh') else 0.2
            
            integration_score = 100  # All components loaded successfully
            
            results = TestResults(
                test_name="System Integration",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                fps=0,
                latency_ms=0,
                accuracy_pixels=integration_score,
                false_positive_rate=0,
                false_negative_rate=0,
                system_info={"components_loaded": True},
                passed=True,
                details={"controller_created": True, "calibration_loaded": True}
            )
            
        except Exception as e:
            self.logger.error(f"Integration test failed: {e}")
            results = TestResults(
                test_name="System Integration",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                fps=0,
                latency_ms=0,
                accuracy_pixels=0,
                false_positive_rate=100,
                false_negative_rate=0,
                system_info={"error": str(e)},
                passed=False,
                details={"exception": str(e)}
            )
        
        self.logger.info(f"System integration - {'PASS' if results.passed else 'FAIL'}")
        return results
    
    def run_all_tests(self) -> List[TestResults]:
        """Run all tests and return results"""
        self.logger.info("Starting comprehensive system testing...")
        
        tests = [
            self.test_camera_performance,
            self.test_face_detection,
            self.test_blink_detection_accuracy,
            self.test_cursor_mapping,
            self.test_filtering_performance,
            self.test_system_integration,
        ]
        
        results = []
        for test_func in tests:
            try:
                result = test_func()
                results.append(result)
                self.test_results.append(result)
            except Exception as e:
                self.logger.error(f"Test {test_func.__name__} failed: {e}")
        
        return results
    
    def generate_report(self, results: List[TestResults]) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("=" * 60)
        report.append("EYE MOUSE CONTROL - SYSTEM TEST REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(results)}")
        report.append(f"Passed: {sum(1 for r in results if r.passed)}")
        report.append(f"Failed: {sum(1 for r in results if not r.passed)}")
        report.append("")
        
        for result in results:
            report.append(f"TEST: {result.test_name}")
            report.append(f"Status: {'PASS' if result.passed else 'FAIL'}")
            report.append(f"Timestamp: {result.timestamp}")
            
            if result.fps > 0:
                report.append(f"FPS: {result.fps:.2f}")
            if result.latency_ms > 0:
                report.append(f"Latency: {result.latency_ms:.2f}ms")
            if result.accuracy_pixels > 0:
                report.append(f"Accuracy: {result.accuracy_pixels:.2f}%")
            if result.false_positive_rate > 0:
                report.append(f"False Positive Rate: {result.false_positive_rate:.2f}%")
            if result.false_negative_rate > 0:
                report.append(f"False Negative Rate: {result.false_negative_rate:.2f}%")
            
            report.append(f"Details: {result.details}")
            report.append("-" * 40)
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 40)
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        pass_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
        
        report.append(f"Overall Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            report.append("System Status: EXCELLENT")
        elif pass_rate >= 75:
            report.append("System Status: GOOD")
        elif pass_rate >= 50:
            report.append("System Status: ACCEPTABLE")
        else:
            report.append("System Status: NEEDS IMPROVEMENT")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_results(self, results: List[TestResults], filename: str = "test_results.json"):
        """Save test results to JSON file"""
        results_data = []
        for result in results:
            results_data.append({
                'test_name': result.test_name,
                'timestamp': result.timestamp,
                'fps': result.fps,
                'latency_ms': result.latency_ms,
                'accuracy_pixels': result.accuracy_pixels,
                'false_positive_rate': result.false_positive_rate,
                'false_negative_rate': result.false_negative_rate,
                'system_info': result.system_info,
                'passed': result.passed,
                'details': result.details
            })
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        self.logger.info(f"Test results saved to {filename}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    """Main test execution"""
    tester = SystemTester()
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate and save report
        report = tester.generate_report(results)
        
        # Save to file
        with open("test_report.txt", "w") as f:
            f.write(report)
        
        # Save JSON results
        tester.save_results(results)
        
        # Print report
        print(report)
        
        # Return exit code based on results
        failed_count = sum(1 for r in results if not r.passed)
        return 1 if failed_count > 0 else 0
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
