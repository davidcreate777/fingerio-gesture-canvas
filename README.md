# FingerIO: Gesture-Controlled Interactive Digital Canvas

A modular, touchless digital canvas and air-drawing suite featuring gesture recognition, Exponential Moving Average (EMA) cursor smoothing, a draggable Picture-in-Picture (PiP) webcam feed, an interactive UI color palette, and high-resolution artwork export.

---

## Overview

**FingerIO** delivers an interactive virtual whiteboard experience powered by computer vision. Using MediaPipe Hands and OpenCV, users sketch in mid-air using fingertip tracking. Unlike basic air-drawing scripts, FingerIO features a modular software architecture with a floating draggable camera preview, custom UI toolbars, color palettes, anti-jitter smoothing, and instant image saving.

---

## Features

- **Gesture-Based Drawing:** Tracks the index fingertip with customizable gesture activation.
- **Jitter-Free Tracking:** Uses Exponential Moving Average (EMA) filtering (`alpha = 0.4`) to produce smooth, clean brush strokes.
- **Draggable Webcam PiP:** Floating Picture-in-Picture camera preview window that can be freely dragged anywhere on the screen using mouse input.
- **Interactive UI Toolbar:** Custom-rendered GUI complete with a top title bar, mode indicators, and notification toasts.
- **Color Palette & Tools:** Includes multiple color presets, dynamic brush sizing, dedicated eraser mode, and instant canvas clearing.
- **Save to Disk:** Instantly captures and exports your artwork as timestamped PNG files in the `saves/` directory.

---

## Project Structure

```
fingerio/
├── camera.py      # Webcam preview component with draggable PiP support
├── colors.py      # Color palette presets and brush property management
├── drawing.py     # Canvas operations, stroke interpolation, and eraser logic
├── gestures.py    # MediaPipe hand tracking and gesture recognition engine
├── main.py        # Application orchestrator, event loop, and smoothing pipeline
├── ui.py          # Custom GUI renderer (toolbars, buttons, notifications)
├── utils.py       # Geometric utilities, vector math, and smoothing helpers
├── saves/         # Output directory for exported artwork (.png)
└── .gitignore     # Git ignore configuration
```

---

## Requirements

### Hardware
- Standard webcam or USB camera.

### Software & Libraries
- Python 3.8+
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- NumPy (`numpy`)

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/davidcreate777/fingerio-gesture-canvas.git
   cd fingerio-gesture-canvas
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install opencv-python mediapipe numpy
   ```

---

## Usage

Run the main application:
```bash
python main.py
```

### Controls & Shortcuts
- **Draw:** Raise your index finger to sketch on the canvas.
- **Drag Camera Preview:** Click and drag the floating camera window anywhere on the canvas.
- **Save Artwork:** Press `s` on your keyboard to save the current drawing to `saves/`.
- **Exit:** Click the on-screen close button or press `q`.
