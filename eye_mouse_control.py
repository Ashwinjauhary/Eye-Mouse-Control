"""
Eye Mouse Control - Hands-free cursor control using face tracking and blink detection.

Features:
- Head movement controls cursor position
- Eye blink detection for mouse clicks
- Configurable sensitivity and calibration
- Safety features and hotkeys
- Real-time visual feedback

Press ESC to exit, SPACE to pause/resume, 'c' to calibrate
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import json
import os
from dataclasses import dataclass, asdict
from typing import Tuple, Optional, Dict, Any
import logging
from pathlib import Path

# Disable PyAutoGUI failsafe for this application
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

@dataclass
class CalibrationData:
    """Stores calibration data for cursor mapping"""
    center_x: float = 0.5
    center_y: float = 0.5
    min_x: float = 0.0
    max_x: float = 1.0
    min_y: float = 0.0
    max_y: float = 1.0
    ear_threshold: float = 0.21
    ear_consecutive_frames: int = 2
    sensitivity_x: float = 1.0
    sensitivity_y: float = 1.0
    deadzone_px: int = 8
    smoothing_alpha: float = 0.25
    
    def save(self, filepath: str) -> None:
        """Save calibration data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'CalibrationData':
        """Load calibration data from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            return cls(**data)
        return cls()

@dataclass
class BlinkConfig:
    """Configuration for blink detection"""
    single_blink_action: str = "left_click"
    double_blink_action: str = "double_click"
    long_blink_action: str = "right_click"
    double_blink_window: float = 0.5  # seconds
    long_blink_threshold: float = 0.3  # seconds
    click_cooldown: float = 0.5  # seconds

class EyeMouseController:
    def __init__(self):
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # MediaPipe setup
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Eye landmark indices for MediaPipe Face Mesh
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        self.NOSE_TIP = 1  # Nose tip landmark
        
        # Calibration and settings
        self.calibration_file = "calibration.json"
        self.calibration = CalibrationData.load(self.calibration_file)
        self.blink_config = BlinkConfig()
        
        # Cursor tracking
        self.smoothed_x = self.screen_w // 2
        self.smoothed_y = self.screen_h // 2
        
        # Blink detection
        self.blink_counter = 0
        self.last_blink_time = 0
        self.blink_start_time = 0
        self.last_click_time = 0
        self.blink_history = []
        
        # System state
        self.is_paused = False
        self.is_calibrating = False
        self.calibration_step = 0
        self.calibration_points = []
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Logging setup
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for debugging and performance monitoring"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('eye_mouse.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def eye_aspect_ratio(self, landmarks, indices, img_w, img_h) -> float:
        """Calculate Eye Aspect Ratio (EAR) for blink detection"""
        pts = [(int(landmarks[i].x * img_w), int(landmarks[i].y * img_h)) for i in indices]
        p1, p2, p3, p4, p5, p6 = pts
        
        # Vertical distances
        A = np.linalg.norm(np.array(p2) - np.array(p6))
        B = np.linalg.norm(np.array(p3) - np.array(p5))
        # Horizontal distance
        C = np.linalg.norm(np.array(p1) - np.array(p4))
        
        if C == 0:
            return 0.0
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blink(self, ear: float) -> Optional[str]:
        """Detect blinks and classify them based on duration and pattern"""
        current_time = time.time()
        
        if ear < self.calibration.ear_threshold:
            if self.blink_counter == 0:
                self.blink_start_time = current_time
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.calibration.ear_consecutive_frames:
                # Calculate blink duration
                blink_duration = current_time - self.blink_start_time
                
                # Check for double blink
                self.blink_history.append(current_time)
                self.blink_history = [t for t in self.blink_history if current_time - t < self.blink_config.double_blink_window]
                
                if len(self.blink_history) >= 2:
                    action = self.blink_config.double_blink_action
                    self.logger.info(f"Double blink detected: {action}")
                elif blink_duration > self.blink_config.long_blink_threshold:
                    action = self.blink_config.long_blink_action
                    self.logger.info(f"Long blink detected: {action}")
                else:
                    action = self.blink_config.single_blink_action
                    self.logger.info(f"Single blink detected: {action}")
                
                self.blink_counter = 0
                return action
            self.blink_counter = 0
        
        return None
    
    def execute_click_action(self, action: str):
        """Execute the appropriate mouse action based on blink type"""
        current_time = time.time()
        if current_time - self.last_click_time < self.blink_config.click_cooldown:
            return
        
        if action == "left_click":
            pyautogui.click()
        elif action == "right_click":
            pyautogui.click(button='right')
        elif action == "double_click":
            pyautogui.doubleClick()
        
        self.last_click_time = current_time
    
    def map_to_screen(self, nose_x: float, nose_y: float) -> Tuple[int, int]:
        """Map normalized nose position to screen coordinates with calibration"""
        # Apply calibration bounds
        bounded_x = max(self.calibration.min_x, min(self.calibration.max_x, nose_x))
        bounded_y = max(self.calibration.min_y, min(self.calibration.max_y, nose_y))
        
        # Map to screen with sensitivity adjustment
        screen_x = int(((bounded_x - self.calibration.min_x) / 
                       (self.calibration.max_x - self.calibration.min_x)) * self.screen_w)
        screen_y = int(((bounded_y - self.calibration.min_y) / 
                       (self.calibration.max_y - self.calibration.min_y)) * self.screen_h)
        
        # Apply sensitivity
        screen_x = int(self.screen_w // 2 + (screen_x - self.screen_w // 2) * self.calibration.sensitivity_x)
        screen_y = int(self.screen_h // 2 + (screen_y - self.screen_h // 2) * self.calibration.sensitivity_y)
        
        return screen_x, screen_y
    
    def smooth_cursor_movement(self, target_x: int, target_y: int) -> Tuple[int, int]:
        """Apply smoothing to cursor movement to reduce jitter"""
        alpha = self.calibration.smoothing_alpha
        self.smoothed_x = int(alpha * target_x + (1 - alpha) * self.smoothed_x)
        self.smoothed_y = int(alpha * target_y + (1 - alpha) * self.smoothed_y)
        return self.smoothed_x, self.smoothed_y
    
    def move_cursor(self, target_x: int, target_y: int):
        """Move cursor with deadzone and smoothing"""
        current_x, current_y = pyautogui.position()
        
        # Apply deadzone
        if (abs(target_x - current_x) > self.calibration.deadzone_px or 
            abs(target_y - current_y) > self.calibration.deadzone_px):
            
            # Apply smoothing
            smooth_x, smooth_y = self.smooth_cursor_movement(target_x, target_y)
            pyautogui.moveTo(smooth_x, smooth_y, duration=0.01)
    
    def process_calibration(self, frame, landmarks):
        """Handle calibration process"""
        h, w = frame.shape[:2]
        nose = landmarks[self.NOSE_TIP]
        nose_x, nose_y = nose.x, nose.y
        
        instructions = [
            "Look at center of screen and press SPACE",
            "Look at top-left corner and press SPACE",
            "Look at top-right corner and press SPACE", 
            "Look at bottom-left corner and press SPACE",
            "Look at bottom-right corner and press SPACE",
            "Blink naturally 3 times and press SPACE"
        ]
        
        if self.calibration_step < len(instructions):
            # Display instruction
            cv2.putText(frame, f"Calibration Step {self.calibration_step + 1}/6", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, instructions[self.calibration_step], 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Store calibration points
            if self.calibration_step == 0:  # Center
                self.calibration.center_x = nose_x
                self.calibration.center_y = nose_y
            elif self.calibration_step == 1:  # Top-left
                self.calibration.min_x = nose_x
                self.calibration.min_y = nose_y
            elif self.calibration_step == 2:  # Top-right
                self.calibration.max_x = nose_x
                self.calibration.min_y = min(self.calibration.min_y, nose_y)
            elif self.calibration_step == 3:  # Bottom-left
                self.calibration.min_x = min(self.calibration.min_x, nose_x)
                self.calibration.max_y = nose_y
            elif self.calibration_step == 4:  # Bottom-right
                self.calibration.max_x = max(self.calibration.max_x, nose_x)
                self.calibration.max_y = max(self.calibration.max_y, nose_y)
            elif self.calibration_step == 5:  # Blink calibration
                # Auto-calibrate EAR threshold based on blinks
                left_ear = self.eye_aspect_ratio(landmarks, self.LEFT_EYE, w, h)
                right_ear = self.eye_aspect_ratio(landmarks, self.RIGHT_EYE, w, h)
                avg_ear = (left_ear + right_ear) / 2
                
                # Collect EAR values during blinks for threshold calibration
                if hasattr(self, 'blink_ear_values'):
                    self.blink_ear_values.append(avg_ear)
                else:
                    self.blink_ear_values = [avg_ear]
    
    def draw_visualization(self, frame, face_landmark_obj, ear: float, blink_action: Optional[str]):
        """Draw visual feedback on frame"""
        h, w = frame.shape[:2]
        
        # Extract landmarks from the face landmark object
        landmarks = face_landmark_obj.landmark
        
        # Draw face mesh
        if face_landmark_obj:
            self.mp_draw.draw_landmarks(
                frame, 
                face_landmark_obj, 
                self.mp_face.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
            )
            
            # Draw nose indicator
            nose = landmarks[self.NOSE_TIP]
            nose_pos = (int(nose.x * w), int(nose.y * h))
            cv2.circle(frame, nose_pos, 8, (0, 255, 255), -1)
            cv2.circle(frame, nose_pos, 12, (0, 255, 255), 2)
            
            # Draw eye indicators
            left_eye_pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in self.LEFT_EYE]
            right_eye_pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in self.RIGHT_EYE]
            
            for pts in [left_eye_pts, right_eye_pts]:
                for pt in pts:
                    cv2.circle(frame, pt, 3, (255, 0, 0), -1)
        
        # Status overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Display status information
        status_color = (0, 255, 0) if not self.is_paused else (0, 0, 255)
        cv2.putText(frame, f"EAR: {ear:.3f}", (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        if blink_action:
            cv2.putText(frame, f"Action: {blink_action}", (10, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        status_text = "PAUSED" if self.is_paused else "ACTIVE"
        cv2.putText(frame, f"Status: {status_text}", (10, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Controls help
        help_text = "ESC: Exit | SPACE: Pause/Resume | C: Calibrate"
        cv2.putText(frame, help_text, (w - 400, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Main application loop"""
        self.logger.info("Starting Eye Mouse Control")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.error("Camera not available")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            blink_action = None
            ear = 0.0
            
            if results.multi_face_landmarks and not self.is_paused:
                landmarks = results.multi_face_landmarks[0].landmark
                
                if self.is_calibrating:
                    self.process_calibration(frame, landmarks)
                else:
                    # Calculate EAR for blink detection
                    left_ear = self.eye_aspect_ratio(landmarks, self.LEFT_EYE, w, h)
                    right_ear = self.eye_aspect_ratio(landmarks, self.RIGHT_EYE, w, h)
                    ear = (left_ear + right_ear) / 2.0
                    
                    # Detect blinks
                    blink_action = self.detect_blink(ear)
                    if blink_action:
                        self.execute_click_action(blink_action)
                    
                    # Map nose position to cursor
                    nose = landmarks[self.NOSE_TIP]
                    target_x, target_y = self.map_to_screen(nose.x, nose.y)
                    self.move_cursor(target_x, target_y)
            
            # Draw visualization
            if results.multi_face_landmarks:
                frame = self.draw_visualization(frame, results.multi_face_landmarks[0], ear, blink_action)
            
            cv2.imshow("Eye Mouse Control", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                if self.is_calibrating:
                    self.calibration_step += 1
                    if self.calibration_step >= 6:
                        # Finish calibration
                        self.is_calibrating = False
                        self.calibration.save(self.calibration_file)
                        self.logger.info("Calibration completed and saved")
                        self.calibration_step = 0
                else:
                    self.is_paused = not self.is_paused
                    self.logger.info(f"System {'paused' if self.is_paused else 'resumed'}")
            elif key == ord('c'):  # Start calibration
                self.is_calibrating = True
                self.calibration_step = 0
                self.blink_ear_values = []
                self.logger.info("Starting calibration process")
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        self.logger.info("Eye Mouse Control stopped")

if __name__ == "__main__":
    controller = EyeMouseController()
    controller.run()
