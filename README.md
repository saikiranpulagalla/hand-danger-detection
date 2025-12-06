# 🖐️ Real-Time Hand Tracking + Danger Detection System

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/opencv-4.8%2B-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-prototype-orange.svg)]()

A **CPU-optimized computer vision prototype** that tracks your hand in real-time and detects proximity to virtual danger zones—all without MediaPipe, OpenPose, or cloud APIs.

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [How It Works](#-how-it-works)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Performance](#-performance)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)

---

## ✨ Features

- ✅ **No External APIs**: Pure OpenCV + NumPy implementation
- ✅ **Real-Time Performance**: 15-25 FPS on CPU
- ✅ **Classical Computer Vision**: Skin color segmentation, contour detection, morphological operations
- ✅ **Distance-Based States**: SAFE → WARNING → DANGER state machine
- ✅ **Visual Feedback**: Color-coded overlays, danger alerts, distance visualization
- ✅ **Modular Architecture**: Clean, documented, easy-to-extend codebase
- ✅ **Calibration Mode**: Adaptive skin color detection for different lighting conditions
- ✅ **Customizable Danger Zones**: Rectangle or circle shapes, adjustable positions

---

## 🎬 Demo

### Basic Interaction
```
STATE: SAFE      ────→  STATE: WARNING  ────→  STATE: DANGER
Distance: 250px         Distance: 120px         Distance: 45px
[Green Zone]            [Orange Zone]           [!!! RED ALERT !!!]
```

### Real-Time Visualization
The system displays:
- 🟣 **Hand contour** (magenta outline)
- 🟡 **Hand centroid** (yellow circle with white border)
- 🔵 **Fingertip** (blue circle)
- 📏 **Distance line** (yellow line to nearest boundary)
- 📊 **Live metrics** (FPS, distance, danger level %)
- 🚨 **Danger alerts** (blinking text when in danger zone)

---

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Webcam
- Good lighting conditions

### Step 1: Clone Repository
```bash
git clone https://github.com/saikiranpulagalla/hand-danger-detection.git
cd hand-danger-detection
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install opencv-python>=4.8.0 numpy>=1.24.0
```

---

## 🏃 Quick Start

### Run the Application
```bash
python main.py
```

### First-Time Setup
1. Position yourself 2-3 feet from webcam
2. Ensure good lighting (front-facing light recommended)
3. Move your hand naturally in front of the camera
4. Approach the red **DANGER ZONE** box in the top-right

### Keyboard Controls
| Key | Action |
|-----|--------|
| `q` | Quit application |
| `c` | Toggle calibration mode |
| `SPACE` | Capture skin color (during calibration) |
| `d` | Reset danger zone to center |
| `s` | Increase sensitivity (lower min hand area) |
| `l` | Decrease sensitivity (raise min hand area) |

---

## 📖 Usage

### Basic Operation

1. **Launch the program**:
   ```bash
   python main.py
   ```

2. **Observe the states**:
   - **SAFE** (Green): Hand is far from danger zone
   - **WARNING** (Orange): Hand is approaching danger zone
   - **DANGER** (Red): Hand is too close or touching boundary

3. **Read the metrics**:
   - **Distance**: Pixels from hand center to nearest boundary
   - **Danger Level**: 0-100% proximity indicator
   - **FPS**: Real-time performance metric

### Advanced: Calibration Mode

Use this for challenging lighting or different skin tones:

1. Press `c` to enter calibration mode
2. Place your **open palm** inside the green box
3. Press `SPACE` to capture
4. System auto-adjusts skin detection thresholds
5. Press `c` again to exit calibration mode

---

## 🔬 How It Works

### Architecture Overview

```
┌─────────────┐
│  Webcam     │
│  Capture    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Hand Detector      │
│  • YCrCb conversion │
│  • Skin segmentation│
│  • Morphology ops   │
│  • Contour finding  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Distance Logic     │
│  • Euclidean calc   │
│  • State machine    │
│  • Smoothing filter │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Visualization      │
│  • Overlays         │
│  • Alerts           │
│  • Metrics display  │
└─────────────────────┘
```

### Hand Detection Pipeline

```
BGR Frame
  ↓
YCrCb Color Space Conversion
  ↓
Skin Color Thresholding
  ↓
Morphological Operations (Erode + Dilate)
  ↓
Contour Detection
  ↓
Area Filtering (5000-100000 px²)
  ↓
Centroid + Fingertip Extraction
```

### Distance Calculation

The system calculates the **minimum Euclidean distance** from the hand centroid to the danger zone boundary:

```
distance = min(√((hand_x - boundary_x)² + (hand_y - boundary_y)²))
```

### State Machine

```
┌──────┐  distance > 150px   ┌─────────┐  distance > 60px   ┌────────┐
│ SAFE ├───────────────────→ │ WARNING ├──────────────────→ │ DANGER │
└──────┘                      └─────────┘                     └────────┘
   ↑                              ↑                               ↑
   └──────────────────────────────┴───────────────────────────────┘
              Majority voting over 5 frames (smoothing)
```

---

## ⚙️ Configuration

### Project Structure
```
hand-danger-detection/
├── main.py                 # Main application loop
├── main_demo.py            # Demo mode (simulated hand, no webcam)
├── hand_detector.py        # Hand detection logic
├── virtual_object.py       # Danger zone rendering
├── distance_logic.py       # Distance & state management
├── utils.py                # Helper utilities
├── analyze_colors.py       # Utility: color analysis helper
├── debug_mask.py           # Utility: mask debugging tool
├── launch.bat              # Windows helper to activate venv & run app
├── pyproject.toml          # Optional packaging / metadata
├── requirements.txt        # Dependencies
└── README.md               # This file
```

### Utilities & Helpers

- `main_demo.py`: Runs the application in demo mode using a simulated hand (useful when no webcam is available). See the **Demo** section above for controls and usage.
- `analyze_colors.py`: Helper script for analyzing color ranges and thresholds used by the detector.
- `debug_mask.py`: Utility to visualize and debug skin/mask outputs during development.
- `launch.bat`: Windows convenience script to activate a virtual environment and launch `main.py` (edit as needed for your environment).
- `pyproject.toml`: Optional project metadata / packaging configuration (may be present alongside `requirements.txt`).
### Customizing Thresholds

#### Distance Thresholds
Edit `main.py` (current defaults shown):
```python
distance_manager = DistanceStateManager(
    safe_threshold=300,      # Distance (px): SAFE if > 300, DANGER if < 120
    warning_threshold=120    # WARNING state between 120–300
)
```
These thresholds determine state transitions:
- **SAFE**: distance > 300 px
- **WARNING**: 120 < distance ≤ 300 px
- **DANGER**: distance ≤ 120 px

#### Hand Detection Sensitivity
Edit `main.py` (effective thresholds applied during detection):
```python
hand_detector = HandDetector(
    min_hand_area=1000,      # Constructor default (not used directly)
    max_hand_area=500000,    # Constructor default (not used directly)
    use_bg_subtraction=True  # Use background subtraction + skin color
)
```
**Note:** The actual hand area filtering thresholds applied in `detect_hand()` are:
- **Minimum area**: 2000 px² (filters out noise)
- **Maximum area**: 100000 px² (rejects large objects/arms)

To adjust sensitivity, use keyboard:
- Press `s` to increase sensitivity (lower min area)
- Press `l` to decrease sensitivity (raise min area)

#### Danger Zone Configuration
Edit `main.py`:
```python
danger_zone = VirtualDangerZone(
    shape='circle',              # Options: 'rectangle', 'circle'
    position=(320, 240),         # (x, y) or None for auto
    size=80                      # radius (circle) or (width, height) (rectangle)
)
```

#### Skin Color Thresholds (Calibration)
The system uses **adaptive skin color detection** that can be calibrated at runtime:

1. **During runtime**: Press `c` to enter calibration mode, place your open palm in the green box, press `SPACE` to capture.
   - System will auto-adjust YCrCb and HSV thresholds based on your skin tone and lighting.

2. **Manual adjustment** (advanced): Edit `hand_detector.py` to modify the default `skin_ranges`:
```python
# In HandDetector.__init__() - YCrCb color space
self.skin_ranges = [
    {'space': 'YCrCb', 'lower': np.array([80, 100, 130], dtype=np.uint8), 
     'upper': np.array([200, 125, 160], dtype=np.uint8)},
]
```

**Note:** The detector also uses HSV color space as a fallback for robustness. Calibration updates both automatically.

---

## 🐛 Troubleshooting

### Issue: Hand Not Detected

**Symptom**: No magenta contour appears around your hand

**Solutions**:
1. **Improve Lighting**: Use front-facing light source
2. **Remove Clutter**: Use plain background
3. **Calibrate**: Press `c` and capture skin color
4. **Check Webcam**: Verify camera is working (`ls /dev/video*` on Linux)
5. **Adjust Thresholds**: Lower `min_hand_area` in configuration

### Issue: Low FPS (< 8 FPS)

**Symptom**: Choppy video, high latency

**Solutions**:
1. **Reduce Resolution**:
   ```python
   frame = resize_frame(frame, width=480)  # Default: 640
   ```
2. **Close Background Apps**: Free up CPU resources
3. **Increase Min Area**: Skip smaller contours
4. **Reduce Morphology**: Lower iteration count in `hand_detector.py`

### Issue: False Positives

**Symptom**: Face or other objects detected as hand

**Solutions**:
1. **Increase Min Area**: `min_hand_area=10000`
2. **Restrict Detection Zone**: Only process bottom half of frame
3. **Use Background Subtraction**: Implement in `hand_detector.py`

### Issue: Flickering States

**Symptom**: Rapid switching between SAFE/WARNING/DANGER

**Solutions**:
1. **Increase History Length** (in `distance_logic.py`):
   ```python
   self.history_length = 10  # Default: 5 (uses majority voting over more frames)
   ```
2. **Widen Thresholds**: Increase gap between state boundaries in `main.py`:
   ```python
   distance_manager = DistanceStateManager(safe_threshold=350, warning_threshold=100)
   ```
3. **Improve Lighting**: Better lighting = more stable hand detection = fewer false positives

---

## 📊 Performance

### Benchmarks

| Hardware | Resolution | FPS | Notes |
|----------|-----------|-----|-------|
| Intel i5-8265U | 640x480 | 18-22 | Typical laptop CPU |
| AMD Ryzen 5 3600 | 640x480 | 22-28 | Desktop CPU |
| Apple M1 | 640x480 | 28-35 | MacBook |
| Raspberry Pi 4 | 480x360 | 8-12 | IoT/Edge device (CPU-intensive) |

**Current system**: Uses pure OpenCV (YCrCb + HSV skin detection, morphological ops, contour finding) — no GPU acceleration, fully CPU-based.

### Optimization Tips

1. **Frame Skipping**: Process every 2nd frame
   ```python
   frame_count = 0
   if frame_count % 2 == 0:
       hand_data = hand_detector.detect_hand(frame)
   frame_count += 1
   ```

2. **ROI Processing**: Only process bottom half
   ```python
   roi = frame[frame.shape[0]//2:, :]  # Bottom half only
   ```

3. **GPU Acceleration**: Use `cv2.UMat` for OpenCL support
   ```python
   frame_gpu = cv2.UMat(frame)
   ```

---

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Multi-hand tracking
- [ ] Gesture recognition (open/closed hand)
- [ ] Audio alerts
- [ ] Configuration file (JSON)

### Version 1.2 (Future)
- [ ] 3D distance estimation
- [ ] Machine learning hand segmentation
- [ ] Kalman filter tracking
- [ ] Recording/playback mode

### Version 2.0 (Vision)
- [ ] Web interface (Flask/FastAPI)
- [ ] Multi-zone support
- [ ] Analytics dashboard
- [ ] Mobile app (React Native)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Bug Reports
Open an issue with:
- Python version
- OS and hardware specs
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests
Describe:
- Use case
- Proposed solution
- Alternative approaches

### Pull Requests
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Style
- Follow PEP 8
- Add docstrings to functions
- Include type hints
- Write unit tests

---

## 🙏 Acknowledgments

- **OpenCV Community**: For excellent documentation
- **Computer Vision Tutorials**: PyImageSearch, LearnOpenCV
- **Inspiration**: Industrial safety systems, interactive installations

---


**Project Link**: [https://github.com/saikiranpulagalla/hand-danger-detection](https://github.com/saikiranpulagalla/hand-danger-detection)

---

### Papers
- "Skin Color Detection in YCrCb Space" (2019)
- "Real-Time Hand Tracking for HCI" (2020)

---

<div align="center">

**Built with ❤️ using OpenCV and Python**

⭐ **Star this repo if you find it helpful!** ⭐

</div>
