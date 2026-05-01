# Presentation Draft — Adaptive Camera Calibration System

**Course:** CSE 499A, North South University  
**Date:** May 2026

---

## Slide 1: Title Slide

**Speaker Notes:** Introduce the project, greet the audience and the instructor. Briefly state the course and the project title. Keep it short — the details come in the following slides.

**Bullet Points:**
- **Project Title:** Adaptive Camera Calibration System
- **Course:** CSE 499A — Senior Design Project I
- **University:** North South University
- **Date:** May 2026

**Visuals suggested:** University logo, project title in large bold text, a subtle background image of a checkerboard pattern or camera lens.

---

## Slide 2: Introduction — What is Camera Calibration?

**Speaker Notes:** Camera calibration is the process of estimating the internal parameters of a camera lens so that we can correct optical distortions. Every real camera lens introduces some distortion — straight lines in the real world may appear curved in the image. This is especially critical in robotics, autonomous navigation, and 3D reconstruction, where accurate measurements from images are essential.

**Bullet Points:**
- Camera calibration estimates **intrinsic parameters** (focal length, optical center) and **distortion coefficients**
- Real camera lenses introduce **radial and tangential distortion**
- Straight lines in the real world appear curved in raw camera images
- Calibration enables accurate measurements and corrections from images
- Essential for robotics, autonomous vehicles, AR/VR, and 3D vision

**Visuals suggested:** Side-by-side image showing a distorted vs. undistorted photo. Diagram showing how barrel/pincushion distortion warps straight lines.

---

## Slide 3: Problem Statement — What Does This Project Do?

**Speaker Notes:** The specific problem we address is: given a camera that introduces unknown distortion, how can we compute its intrinsic parameters and correct the distortion — not just once, but continuously in real time? Our system computes the camera matrix and distortion coefficients from checkerboard images, then runs a live webcam feed that shows the corrected output alongside the original, adapting when the camera setup changes.

**Bullet Points:**
- **Problem:** Unknown lens distortion makes raw camera images unreliable for precise tasks
- **Goal:** Compute intrinsic camera parameters (fx, fy, cx, cy) and distortion coefficients (k1, k2, p1, p2, k3)
- **Deliverable 1:** `calibrate.py` — offline calibration from checkerboard images
- **Deliverable 2:** `adaptive_calibration.py` — live real-time correction with drift detection
- **Output:** `camera_params.npz` file containing the computed parameters

**Visuals suggested:** System overview flowchart: checkerboard images → calibrate.py → camera_params.npz → adaptive_calibration.py → live corrected feed.

---

## Slide 4: Background — Zhang's Calibration Method

**Speaker Notes:** The foundation of our project is Zhang's flexible camera calibration technique, published in the year 2000. Zhang proposed using a planar checkerboard pattern viewed from multiple angles to estimate camera parameters. Unlike older methods that required expensive 3D calibration rigs, Zhang's approach only needs a printed checkerboard and a few photographs. This method is now the standard in both academia and industry, implemented in OpenCV and MATLAB.

**Bullet Points:**
- Zhang (2000) introduced a **flexible calibration technique** using a planar pattern
- Requires only a **flat checkerboard** viewed from multiple orientations — no 3D rig needed
- Estimates both **intrinsic parameters** and **lens distortion coefficients**
- Uses **homography estimation** between the pattern plane and image plane
- Now the **de facto standard** — implemented in OpenCV, MATLAB, and ROS

**Visuals suggested:** Photo of a checkerboard pattern with detected corners highlighted. Diagram illustrating the pinhole camera model and how homographies relate the pattern to the image.

---

## Slide 5: Related Works — Existing Tools & Literature

**Speaker Notes:** Several tools exist for camera calibration. MATLAB's Camera Calibration Toolbox provides a GUI-based workflow but requires a commercial license. OpenCV's calibration module is open-source and well-documented, making it ideal for academic and embedded use. Bradski's 2008 reference book on OpenCV covers the calibration pipeline in detail. We chose OpenCV because it is free, works with Python, and can run on low-power hardware like Raspberry Pi — critical for our 499B hardware integration.

**Bullet Points:**
- **MATLAB Camera Calibration Toolbox** — GUI-based, commercial license required
- **OpenCV `cv2.calibrateCamera()`** — open-source, works with Python and C++
- **Bradski & Kaehler (2008)** — comprehensive reference on OpenCV's vision pipeline
- OpenCV chosen for: **zero cost, Python compatibility, embedded hardware support**
- Adaptive/real-time calibration is an active area — most tools only support one-time static calibration

**Visuals suggested:** Comparison table of MATLAB vs. OpenCV vs. ROS calibration features. Screenshot of OpenCV's corner detection in action.

---

## Slide 6: Why Adaptive Calibration Matters

**Speaker Notes:** Traditional calibration is performed once and assumed to hold forever. But in practice, cameras can shift — a bump to the robot, a change in temperature, or a different mounting position all alter the optical properties. Our adaptive system monitors the live feed for signs of calibration drift using feature tracking. When drift is detected, the system automatically triggers recalibration using the live checkerboard frames. This ensures the camera parameters remain accurate over time without manual intervention.

**Bullet Points:**
- One-time calibration assumes camera never moves — **unrealistic in robotics**
- Physical disturbances (bumps, vibrations, remounting) change camera alignment
- Our system uses **ORB feature tracking** to detect calibration drift in real time
- When error exceeds threshold (1.5), automatic **recalibration** is triggered
- Recalibration uses **10 live checkerboard frames** — no manual re-run needed

**Visuals suggested:** Diagram showing the feedback loop: live frame → drift detection → error threshold → recalibration trigger → updated parameters.

---

## Slide 7: Proposed Solution — System Architecture

**Speaker Notes:** Our system follows a clean two-script architecture. The first script, calibrate.py, processes stored checkerboard images offline to compute the initial camera parameters. These are saved to a NumPy binary file. The second script, adaptive_calibration.py, loads these parameters and runs a live webcam feed showing original and undistorted frames side by side. It monitors drift and triggers recalibration when necessary. This modular design keeps the offline calibration logic separate from the real-time adaptive loop.

**Bullet Points:**
- **Two-script modular design** — separation of concerns
- `calibrate.py` → offline processing → saves `camera_params.npz`
- `adaptive_calibration.py` → loads params → live webcam feed → drift detection → recalibration
- **Data format:** NumPy `.npz` (compact, fast to load, no dependencies)
- **Package manager:** `uv` for reproducible Python environment

**Visuals suggested:** Architecture block diagram showing the two scripts, data flow through camera_params.npz, and the webcam feedback loop.

---

## Slide 8: Proposed Solution — Calibration Pipeline (calibrate.py)

**Speaker Notes:** The calibration script follows a well-defined pipeline. First, we prepare 3D object points representing the known geometry of the 9×6 checkerboard. Then we load all JPEG images from the checkerboard_images folder. For each image, we detect corners using OpenCV's findChessboardCorners and refine them to sub-pixel accuracy using cornerSubPix. Finally, we pass all matched 3D-to-2D point pairs to calibrateCamera, which uses Zhang's method internally to compute the camera matrix and distortion coefficients. The reprojection error tells us how accurately the model fits.

**Bullet Points:**
- Define 3D object points for a **9×6 inner corner** checkerboard grid
- Load images → convert to grayscale → detect corners with `cv2.findChessboardCorners()`
- Refine corners to **sub-pixel accuracy** using `cv2.cornerSubPix()`
- Run `cv2.calibrateCamera()` — solves for camera matrix and distortion
- Compute **mean reprojection error** across all images as quality metric

**Visuals suggested:** Step-by-step pipeline flowchart. Screenshot of a checkerboard image with detected corners drawn (colorful lines connecting corners).

---

## Slide 9: Proposed Solution — Design Choices & Comparisons

**Speaker Notes:** We chose Python for rapid development and academic clarity. OpenCV was selected over MATLAB because it is free and runs on embedded hardware. The 9×6 checkerboard provides 54 corner points per image, which is a good balance between accuracy and ease of detection. We store parameters in NumPy's .npz format rather than JSON or YAML because it preserves exact floating-point precision and loads faster. Compared to purely manual recalibration, our adaptive approach reduces downtime and human error.

**Bullet Points:**
- **Python + OpenCV** over MATLAB — free, embeddable, large community
- **9×6 checkerboard** — 54 corners per image, good accuracy-detection balance
- **`.npz` format** — preserves float64 precision, faster than JSON/YAML
- **ORB features** for drift detection — lightweight, real-time capable
- **Automatic recalibration** vs. manual re-run — reduces human intervention

**Visuals suggested:** Comparison table: Python+OpenCV vs. MATLAB vs. C++ approaches (cost, speed, portability, ease of use).

---

## Slide 10: Preliminary Results — Calibration Output

**Speaker Notes:** We ran calibrate.py on 14 checkerboard images captured from a laptop webcam at various angles and distances. The script successfully detected corners in the images and computed the camera parameters. The resulting reprojection error was 0.0054, which is excellent — well below the 1.0 threshold that indicates a good calibration. The camera matrix gives us focal lengths of approximately 2277 and 1977 pixels in the x and y directions, with the optical center at roughly (323, 230). The distortion coefficients show significant radial distortion that our system corrects.

**Bullet Points:**
- Successfully processed **14 checkerboard images** from laptop webcam
- **Reprojection error: 0.0054** — excellent (threshold < 1.0)
- Camera matrix: fx ≈ 2277, fy ≈ 1977, cx ≈ 323, cy ≈ 230
- Distortion coefficients: k1 ≈ −2.54, k2 ≈ 112.4, p1 ≈ 0.028, p2 ≈ −0.0003, k3 ≈ −1799.96
- Parameters saved to `camera_params.npz` — ready for live use

**Visuals suggested:** Terminal screenshot showing calibrate.py output. Table displaying the camera matrix and distortion coefficients. Bar chart comparing the achieved error (0.0054) against the acceptable threshold (1.0).

---

## Slide 11: Preliminary Results — Live Adaptive Demo

**Speaker Notes:** The adaptive_calibration.py script opens the webcam and displays a split-screen view: the original frame on the left with ORB keypoints drawn in green, and the undistorted frame on the right. The reprojection error is displayed in the top-left corner in green when stable. When the camera is disturbed — for example, by covering the lens or shaking the laptop — the error spikes above the 1.5 threshold, the text turns red, and the system displays "RECALIBRATING..." while it collects 10 new checkerboard frames. Upon successful recalibration, it shows "RECALIBRATION COMPLETE" for 2 seconds and resumes normal operation.

**Bullet Points:**
- **Split-screen display:** Original (with ORB keypoints) | Undistorted
- **Green text:** reprojection error displayed live when stable
- **Red "RECALIBRATING..."** triggered when error > 1.5 threshold
- Collects **10 checkerboard frames** from live feed for recalibration
- **"RECALIBRATION COMPLETE"** shown for 2 seconds after successful update

**Visuals suggested:** Screenshot of the live demo window showing the split screen. Two screenshots: one in normal (green) state and one in recalibrating (red) state.

---

## Slide 12: What Will Be Completed in 499B

**Speaker Notes:** In CSE 499B, we will extend this software to work with actual hardware. The immediate next step is capturing images from the specific target camera — a Raspberry Pi Camera Module — and fine-tuning the calibration for that sensor. We will then deploy the adaptive calibration system on a Raspberry Pi, optimizing for its limited compute resources. The final integration involves mounting the calibrated camera on a robot chassis for the RoboSub AUV project, where accurate underwater vision requires robust calibration. We will also benchmark calibration accuracy across different camera types and environmental conditions.

**Bullet Points:**
- Fine-tune calibration with **real captured images** from the target camera (Pi Camera)
- Deploy and test on **Raspberry Pi** hardware — optimize for limited compute
- Integrate calibrated camera onto **robot chassis** (RoboSub AUV context)
- **Performance benchmarking** across different camera types and lighting conditions
- Stress-test adaptive recalibration under **real-world disturbances** (vibration, temperature)

**Visuals suggested:** Photo of a Raspberry Pi with camera module attached. Timeline/Gantt chart showing 499B milestones. Conceptual rendering of the RoboSub AUV with camera placement.

---

## Slide 13: References (IEEE Format)

**Speaker Notes:** Here are the key references that informed our approach. Zhang's original paper established the calibration method we use. The OpenCV documentation provided the API details for implementation. Bradski's book gave us a comprehensive understanding of the vision pipeline.

**Bullet Points:**

- [1] Z. Zhang, "A flexible new technique for camera calibration," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 22, no. 11, pp. 1330–1334, Nov. 2000.
- [2] G. Bradski and A. Kaehler, *Learning OpenCV: Computer Vision with the OpenCV Library*. Sebastopol, CA, USA: O'Reilly Media, 2008.
- [3] OpenCV, "Camera Calibration and 3D Reconstruction," OpenCV Documentation, 2024. [Online]. Available: https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
- [4] R. Y. Tsai, "A versatile camera calibration technique for high-accuracy 3D machine vision metrology using off-the-shelf TV cameras and lenses," *IEEE Journal on Robotics and Automation*, vol. 3, no. 4, pp. 323–344, Aug. 1987.
- [5] J. Heikkila and O. Silven, "A four-step camera calibration procedure with implicit image correction," in *Proc. IEEE Computer Society Conf. on Computer Vision and Pattern Recognition (CVPR)*, 1997, pp. 1106–1112.

**Visuals suggested:** Clean list with consistent IEEE formatting. No images needed — text-only reference slide.

---

*End of Presentation Draft*
