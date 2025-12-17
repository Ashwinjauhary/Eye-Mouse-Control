"""
Advanced filtering and smoothing algorithms for Eye Mouse Control
Provides Kalman filtering, adaptive smoothing, and noise reduction
"""

import numpy as np
from scipy.signal import savgol_filter
from collections import deque
import time

class KalmanFilter1D:
    """1D Kalman filter for smooth cursor tracking"""
    
    def __init__(self, process_variance=1e-3, measurement_variance=1e-1):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        
        # State: [position, velocity]
        self.state = np.array([0.0, 0.0])
        self.covariance = np.eye(2)
        
        # State transition matrix
        self.F = np.array([[1.0, 1.0],
                           [0.0, 1.0]])
        
        # Measurement matrix
        self.H = np.array([[1.0, 0.0]])
        
        # Process noise covariance
        self.Q = process_variance * np.array([[1/4, 1/2],
                                            [1/2, 1.0]])
        
        # Measurement noise
        self.R = np.array([[measurement_variance]])
    
    def predict(self, dt=1.0):
        """Predict next state"""
        # Update state transition for time step
        self.F[0, 1] = dt
        
        # Predict
        self.state = self.F @ self.state
        self.covariance = self.F @ self.covariance @ self.F.T + self.Q
    
    def update(self, measurement):
        """Update with measurement"""
        # Kalman gain
        S = self.H @ self.covariance @ self.H.T + self.R
        K = self.covariance @ self.H.T @ np.linalg.inv(S)
        
        # Update state and covariance
        y = measurement - self.H @ self.state
        self.state = self.state + K @ y
        self.covariance = (np.eye(2) - K @ self.H) @ self.covariance
    
    def filter(self, measurement, dt=1.0):
        """Filter measurement and return smoothed position"""
        self.predict(dt)
        self.update(measurement)
        return self.state[0]

class AdaptiveSmoother:
    """Adaptive smoothing that adjusts based on movement speed"""
    
    def __init__(self, base_alpha=0.3, speed_threshold=50, max_alpha=0.8):
        self.base_alpha = base_alpha
        self.speed_threshold = speed_threshold
        self.max_alpha = max_alpha
        
        self.prev_x = None
        self.prev_y = None
        self.prev_time = None
        
        self.smoothed_x = 0
        self.smoothed_y = 0
    
    def smooth(self, x, y, timestamp=None):
        """Apply adaptive smoothing"""
        if timestamp is None:
            timestamp = time.time()
        
        if self.prev_x is None:
            # First measurement
            self.smoothed_x = x
            self.smoothed_y = y
        else:
            # Calculate movement speed
            if self.prev_time is not None:
                dt = timestamp - self.prev_time
                if dt > 0:
                    speed = np.sqrt((x - self.prev_x)**2 + (y - self.prev_y)**2) / dt
                    
                    # Adaptive alpha based on speed
                    if speed < self.speed_threshold:
                        # Slow movement - more smoothing
                        alpha = self.base_alpha
                    else:
                        # Fast movement - less smoothing for responsiveness
                        alpha = min(self.max_alpha, self.base_alpha + (speed - self.speed_threshold) / 100)
                    
                    # Apply smoothing
                    self.smoothed_x = alpha * x + (1 - alpha) * self.smoothed_x
                    self.smoothed_y = alpha * y + (1 - alpha) * self.smoothed_y
                else:
                    # Fallback to base smoothing
                    self.smoothed_x = self.base_alpha * x + (1 - self.base_alpha) * self.smoothed_x
                    self.smoothed_y = self.base_alpha * y + (1 - self.base_alpha) * self.smoothed_y
        
        self.prev_x = x
        self.prev_y = y
        self.prev_time = timestamp
        
        return self.smoothed_x, self.smoothed_y

class NoiseReducer:
    """Multi-stage noise reduction for cursor input"""
    
    def __init__(self, history_size=5, outlier_threshold=3.0):
        self.history_size = history_size
        self.outlier_threshold = outlier_threshold
        
        self.x_history = deque(maxlen=history_size)
        self.y_history = deque(maxlen=history_size)
        
        self.savgol_window = min(history_size, 5)
        if self.savgol_window % 2 == 0:
            self.savgol_window += 1  # Must be odd
    
    def add_point(self, x, y):
        """Add new point to history"""
        self.x_history.append(x)
        self.y_history.append(y)
    
    def remove_outliers(self):
        """Remove outlier points using median absolute deviation"""
        if len(self.x_history) < 3:
            return list(self.x_history), list(self.y_history)
        
        x_data = np.array(self.x_history)
        y_data = np.array(self.y_history)
        
        # Calculate median and MAD
        x_median = np.median(x_data)
        y_median = np.median(y_data)
        
        x_mad = np.median(np.abs(x_data - x_median))
        y_mad = np.median(np.abs(y_data - y_median))
        
        # Filter outliers
        x_mask = np.abs(x_data - x_median) < self.outlier_threshold * x_mad
        y_mask = np.abs(y_data - y_median) < self.outlier_threshold * y_mad
        
        # Combine masks (point must be good in both dimensions)
        mask = x_mask & y_mask
        
        return x_data[mask].tolist(), y_data[mask].tolist()
    
    def smooth_savgol(self):
        """Apply Savitzky-Golay filter for smoothing"""
        if len(self.x_history) < self.savgol_window:
            return self.x_history[-1] if self.x_history else 0, \
                   self.y_history[-1] if self.y_history else 0
        
        # Remove outliers first
        x_clean, y_clean = self.remove_outliers()
        
        if len(x_clean) < self.savgol_window:
            return x_clean[-1] if x_clean else 0, y_clean[-1] if y_clean else 0
        
        # Apply Savitzky-Golay filter
        x_smooth = savgol_filter(x_clean, self.savgol_window, 2)
        y_smooth = savgol_filter(y_clean, self.savgol_window, 2)
        
        return x_smooth[-1], y_smooth[-1]
    
    def filter_point(self, x, y):
        """Filter a new point through the noise reduction pipeline"""
        self.add_point(x, y)
        return self.smooth_savgol()

class BlinkStabilizer:
    """Stabilize blink detection to reduce false positives"""
    
    def __init__(self, window_size=10, confirmation_threshold=0.6):
        self.window_size = window_size
        self.confirmation_threshold = confirmation_threshold
        
        self.ear_history = deque(maxlen=window_size)
        self.blink_history = deque(maxlen=window_size)
    
    def add_ear_value(self, ear, threshold):
        """Add new EAR value and update blink detection"""
        self.ear_history.append(ear)
        blink_detected = ear < threshold
        self.blink_history.append(blink_detected)
    
    def get_stable_blink(self):
        """Get stabilized blink detection"""
        if len(self.blink_history) < self.window_size:
            return False
        
        # Require a certain percentage of recent frames to indicate blink
        blink_ratio = sum(self.blink_history) / len(self.blink_history)
        return blink_ratio >= self.confirmation_threshold
    
    def get_ear_stats(self):
        """Get EAR statistics for debugging"""
        if not self.ear_history:
            return 0, 0, 0
        
        ear_array = np.array(self.ear_history)
        return np.mean(ear_array), np.min(ear_array), np.max(ear_array)

class HeadPoseFilter:
    """Filter for head pose estimation to improve cursor stability"""
    
    def __init__(self, alpha=0.3, variance_threshold=0.01):
        self.alpha = alpha
        self.variance_threshold = variance_threshold
        
        self.filtered_x = 0.5
        self.filtered_y = 0.5
        
        self.x_variance = 0
        self.y_variance = 0
    
    def filter_pose(self, x, y):
        """Filter head pose coordinates"""
        # Calculate variance from filtered value
        self.x_variance = (x - self.filtered_x) ** 2
        self.y_variance = (y - self.filtered_y) ** 2
        
        # Adaptive filtering based on variance
        if self.x_variance < self.variance_threshold and self.y_variance < self.variance_threshold:
            # Low variance - stable pose, apply normal filtering
            self.filtered_x = self.alpha * x + (1 - self.alpha) * self.filtered_x
            self.filtered_y = self.alpha * y + (1 - self.alpha) * self.filtered_y
        else:
            # High variance - sudden movement, be more responsive
            responsive_alpha = min(0.8, self.alpha * 2)
            self.filtered_x = responsive_alpha * x + (1 - responsive_alpha) * self.filtered_x
            self.filtered_y = responsive_alpha * y + (1 - responsive_alpha) * self.filtered_y
        
        return self.filtered_x, self.filtered_y

class MultiFilterPipeline:
    """Combines multiple filters for optimal cursor tracking"""
    
    def __init__(self):
        # Initialize filters
        self.kalman_x = KalmanFilter1D(process_variance=1e-3, measurement_variance=1e-2)
        self.kalman_y = KalmanFilter1D(process_variance=1e-3, measurement_variance=1e-2)
        
        self.adaptive_smoother = AdaptiveSmoother(base_alpha=0.3, speed_threshold=30, max_alpha=0.7)
        self.noise_reducer = NoiseReducer(history_size=7, outlier_threshold=2.5)
        self.head_pose_filter = HeadPoseFilter(alpha=0.4, variance_threshold=0.005)
        
        self.blink_stabilizer = BlinkStabilizer(window_size=8, confirmation_threshold=0.5)
        
        self.last_time = time.time()
    
    def filter_cursor_position(self, x, y):
        """Apply complete filtering pipeline to cursor position"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Stage 1: Head pose filtering
        pose_x, pose_y = self.head_pose_filter.filter_pose(x, y)
        
        # Stage 2: Kalman filtering
        kalman_x = self.kalman_x.filter(pose_x, dt)
        kalman_y = self.kalman_y.filter(pose_y, dt)
        
        # Stage 3: Noise reduction
        noise_x, noise_y = self.noise_reducer.filter_point(kalman_x, kalman_y)
        
        # Stage 4: Adaptive smoothing
        smooth_x, smooth_y = self.adaptive_smoother.smooth(noise_x, noise_y, current_time)
        
        return smooth_x, smooth_y
    
    def stabilize_blink(self, ear, threshold):
        """Stabilize blink detection"""
        self.blink_stabilizer.add_ear_value(ear, threshold)
        return self.blink_stabilizer.get_stable_blink()
    
    def get_debug_info(self):
        """Get debugging information from all filters"""
        ear_mean, ear_min, ear_max = self.blink_stabilizer.get_ear_stats()
        
        return {
            'ear_stats': {'mean': ear_mean, 'min': ear_min, 'max': ear_max},
            'head_variance': {'x': self.head_pose_filter.x_variance, 'y': self.head_pose_filter.y_variance},
            'kalman_state': {'x': self.kalman_x.state[0], 'y': self.kalman_y.state[0]},
            'adaptive_alpha': self.adaptive_smoother.base_alpha
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the filtering pipeline
    pipeline = MultiFilterPipeline()
    
    # Simulate noisy cursor data
    np.random.seed(42)
    test_points = []
    
    # Generate test trajectory with noise
    for i in range(100):
        base_x = 0.5 + 0.3 * np.sin(i * 0.1)
        base_y = 0.5 + 0.3 * np.cos(i * 0.1)
        
        # Add noise
        noise_x = base_x + np.random.normal(0, 0.05)
        noise_y = base_y + np.random.normal(0, 0.05)
        
        test_points.append((noise_x, noise_y))
    
    # Apply filtering
    filtered_points = []
    for x, y in test_points:
        filtered_x, filtered_y = pipeline.filter_cursor_position(x, y)
        filtered_points.append((filtered_x, filtered_y))
    
    print(f"Original points: {len(test_points)}")
    print(f"Filtered points: {len(filtered_points)}")
    print(f"Filtering complete!")
    
    # Test blink stabilization
    ear_values = [0.25, 0.15, 0.12, 0.18, 0.28, 0.22, 0.14, 0.11, 0.26]
    threshold = 0.20
    
    for ear in ear_values:
        blink_detected = pipeline.stabilize_blink(ear, threshold)
        print(f"EAR: {ear:.3f}, Blink: {blink_detected}")
