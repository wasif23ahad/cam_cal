# Adaptive Camera Calibration — Setup & Run Guide

CSE 499A | Group 7 | NSU

---

## What You Need

- Python 3.11 or above
- A printed checkerboard pattern (provided separately)
- Your laptop webcam

---

## First Time Setup

```bash
# Install uv if you don't have it
pip install uv

# Install project dependencies
uv sync
```

---

## Step 1 — Collect Your Checkerboard Photos

1. Print the checkerboard pattern and tape it flat on a book
2. Take **20–30 photos** with your laptop webcam
   - Different angles (left, right, top, bottom tilts)
   - Different distances (close, medium, far)
   - Different positions in frame (corners, center)
   - Every photo must be sharp — no blur
3. Put all photos inside the `checkerboard_images/` folder

---

## Step 2 — Run Calibration (Once)

```bash
uv run calibrate.py
```

You should see output like:
```
Found corners in 24/27 images
Calibration complete.
Reprojection error: 0.34
Camera parameters saved to camera_params.npz
```

Reprojection error must be **below 1.0** for good calibration.
If it is above 1.0 — retake your checkerboard photos more carefully.

---

## Step 3 — Run the Live Demo

```bash
uv run adaptive_calibration.py
```

Your webcam will open. You will see:
- **Left panel:** Original camera feed
- **Right panel:** Corrected (undistorted) feed
- **Top-left text:** Live reprojection error value
  - Green = calibration is accurate
  - Red + "RECALIBRATING..." = drift detected, system is correcting

Press **Q** to exit.

---

## To Trigger the Adaptive Effect (For Demo)

To show the adaptive recalibration during your presentation:
- Cover part of the camera with your hand
- Shake the camera slightly
- Change the lighting suddenly (turn room lights off and on)

The error will spike, turn red, and the system will auto-correct.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No images found" | Make sure photos are in checkerboard_images/ folder |
| Reprojection error > 1.0 | Retake photos — make sure board is flat and photos are sharp |
| Webcam doesn't open | Try changing VideoCapture(0) to VideoCapture(1) in adaptive_calibration.py |
| camera_params.npz not found | Run calibrate.py before adaptive_calibration.py |
