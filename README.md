# Eye Mouse Control

A comprehensive hands-free mouse control system that uses face tracking and eye blink detection to control your cursor without using your hands.

## Features

### Core Functionality
- **Head Movement Control**: Move your head to control cursor position
- **Blink Detection**: Use eye blinks to trigger mouse clicks
- **Real-time Tracking**: Smooth, low-latency cursor control using MediaPipe Face Mesh
- **Adaptive Filtering**: Advanced noise reduction and smoothing algorithms

### Click Types
- **Single Blink**: Left click (configurable)
- **Double Blink**: Double click (configurable)
- **Long Blink**: Right click (configurable)

### Advanced Features
- **Calibration System**: Personalized calibration for optimal performance
- **Configuration GUI**: User-friendly interface for adjusting settings
- **Safety Features**: Pause/resume functionality and emergency controls
- **Visual Feedback**: Real-time visualization of tracking and blink detection
- **Logging System**: Comprehensive logging for debugging and performance analysis

## Quick Start

### Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Run the main application**:
```bash
python eye_mouse_control.py
```

2. **Configure settings** (optional):
```bash
python config_gui.py
```

### Controls
- **ESC**: Exit the application
- **SPACE**: Pause/Resume tracking
- **C**: Start calibration process

## Calibration

The calibration process optimizes the system for your specific setup:

1. Press 'C' to start calibration
2. Follow the on-screen instructions:
   - Look at the center of the screen
   - Look at each corner (top-left, top-right, bottom-left, bottom-right)
   - Perform natural blinks for threshold detection

Calibration data is automatically saved to `calibration.json`.

## Configuration

### Using the GUI
Run `config_gui.py` for a user-friendly configuration interface with:
- Real-time camera preview
- Sensitivity adjustments
- Blink detection settings
- Click action mappings

### Manual Configuration
Edit `calibration.json` directly:

```json
{
  "center_x": 0.5,
  "center_y": 0.5,
  "min_x": 0.0,
  "max_x": 1.0,
  "min_y": 0.0,
  "max_y": 1.0,
  "ear_threshold": 0.21,
  "ear_consecutive_frames": 2,
  "sensitivity_x": 1.0,
  "sensitivity_y": 1.0,
  "deadzone_px": 8,
  "smoothing_alpha": 0.25
}
```

### Blink Configuration
Edit `blink_config.json`:

```json
{
  "single_blink_action": "left_click",
  "double_blink_action": "double_click",
  "long_blink_action": "right_click",
  "double_blink_window": 0.5,
  "long_blink_threshold": 0.3,
  "click_cooldown": 0.5
}
```

## Technical Details

### Algorithms

#### Eye Aspect Ratio (EAR)
The system uses the Eye Aspect Ratio algorithm for blink detection:
```
EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
```
Where p1-p6 are specific eye landmarks detected by MediaPipe.

#### Filtering Pipeline
Multi-stage filtering for smooth cursor control:
1. **Kalman Filtering**: Predictive filtering for position and velocity
2. **Noise Reduction**: Outlier detection and Savitzky-Golay smoothing
3. **Adaptive Smoothing**: Dynamic smoothing based on movement speed
4. **Head Pose Filtering**: Stabilization for head movement tracking

#### Cursor Mapping
Normalized nose position is mapped to screen coordinates with:
- Calibration bounds
- Sensitivity adjustments
- Deadzone filtering
- Exponential moving average smoothing

### Performance Metrics

Target performance characteristics:
- **Latency**: < 150ms from movement to cursor response
- **Accuracy**: < 10 pixel error in normal lighting
- **False Click Rate**: < 5% during normal facial movements
- **Frame Rate**: 30+ FPS processing

## Troubleshooting

### Common Issues

#### Cursor Jumps or Jitters
- Increase `smoothing_alpha` in configuration
- Increase `deadzone_px` to filter micro-movements
- Ensure consistent lighting
- Check camera stability

#### False Clicks
- Increase `ear_threshold` (try 0.22-0.25)
- Increase `ear_consecutive_frames` (try 3-4)
- Increase `click_cooldown` to prevent rapid clicks

#### Poor Tracking
- Ensure face is clearly visible to camera
- Improve lighting conditions
- Check camera positioning (should be at eye level)
- Recalibrate system

#### Camera Not Working
- Verify `cv2.VideoCapture(0)` works
- Try different camera indices (0, 1, 2...)
- Check camera permissions
- Ensure no other applications are using the camera

### Performance Optimization

#### For Low-End Systems
- Reduce camera resolution in `eye_mouse_control.py`
- Increase `smoothing_alpha` for less processing
- Disable visual overlays if not needed

#### For High Precision
- Decrease `deadzone_px` for finer control
- Use advanced filtering in `advanced_filters.py`
- Calibrate in your typical lighting conditions

## System Requirements

### Minimum Requirements
- Python 3.9+
- Webcam (640x480 minimum resolution)
- 4GB RAM
- Dual-core processor

### Recommended Requirements
- Python 3.10+
- HD webcam (1280x720)
- 8GB RAM
- Quad-core processor
- Consistent lighting

### Dependencies
- OpenCV 4.8+
- MediaPipe 0.10+
- NumPy 1.24+
- PyAutoGUI 0.9+
- PIL (for GUI)
- SciPy (for advanced filtering)

## Advanced Usage

### Custom Filtering
Use the `advanced_filters.py` module for enhanced performance:

```python
from advanced_filters import MultiFilterPipeline

# Create pipeline
pipeline = MultiFilterPipeline()

# Apply filtering
smooth_x, smooth_y = pipeline.filter_cursor_position(x, y)
blink_stable = pipeline.stabilize_blink(ear, threshold)
```

### Integration with Other Applications
The system can be integrated as a module:

```python
from eye_mouse_control import EyeMouseController

# Create controller
controller = EyeMouseController()

# Use in your application
controller.run()
```

### Accessibility Features
- **Dwell Click**: Alternative to blink-based clicking
- **Visual Feedback**: Color-coded status indicators
- **Audio Feedback**: Optional beep on clicks
- **Emergency Pause**: Look away for 2 seconds to pause

## Development

### Project Structure
```
eye-mouse-control/
├── eye_mouse_control.py      # Main application
├── config_gui.py            # Configuration interface
├── advanced_filters.py      # Advanced filtering algorithms
├── requirements.txt         # Dependencies
├── README.md               # This file
├── calibration.json        # User calibration data
├── blink_config.json       # Blink detection settings
└── eye_mouse.log          # Application log
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Testing
Test the system under various conditions:
- Different lighting scenarios
- Various camera positions
- Multiple users
- Different screen resolutions

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the log file (`eye_mouse.log`)
3. Test with different settings
4. Report issues with system specifications

## Acknowledgments

- MediaPipe for face landmark detection
- OpenCV for camera handling
- PyAutoGUI for mouse control
- Scientific Python community for filtering algorithms

---

**Note**: This system is designed for accessibility purposes. Always ensure proper ergonomics and take regular breaks when using any head-tracking interface to prevent strain.
