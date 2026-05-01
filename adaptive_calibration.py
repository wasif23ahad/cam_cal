import cv2
import numpy as np
import os
import time

# Constants
PARAMS_FILE = "camera_params.npz"
ERROR_THRESHOLD = 1.5
CHECKERBOARD = (9, 6)
RECALIB_FRAMES_NEEDED = 10
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.8
FONT_THICKNESS = 2
TEXT_POS_ERROR = (20, 40)
TEXT_POS_RECALIB = (20, 80)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (0, 0, 255)


def load_camera_params():
    # Load calibration data from file
    if not os.path.exists(PARAMS_FILE):
        print(f"Error: {PARAMS_FILE} not found. Run calibrate.py first.")
        exit()

    data = np.load(PARAMS_FILE)
    return data['mtx'], data['dist']


def calculate_drift_error(frame, prev_gray, orb, prev_pts):
    # Simplified reprojection error metric for live feed
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp, des = orb.detectAndCompute(gray, None)

    if prev_gray is None or prev_pts is None or len(kp) < 10:
        return 0.5, gray, kp

    feature_count = len(kp)
    if feature_count < 20:
        return 2.0, gray, kp

    # Mock reprojection error based on feature density
    error = 1.0 / (np.log10(feature_count) + 0.1) * 2.5
    error += np.random.uniform(-0.05, 0.05)

    return error, gray, kp


def try_collect_recalib_frame(gray, objpoints_buf, imgpoints_buf):
    # Try to detect checkerboard in frame and add to recalibration buffer
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
    if ret:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        objpoints_buf.append(objp)
        imgpoints_buf.append(corners2)
        return True
    return False


def run_recalibration(objpoints_buf, imgpoints_buf, image_size):
    # Run cv2.calibrateCamera on collected frames and return new parameters
    ret, mtx_new, dist_new, rvecs, tvecs = cv2.calibrateCamera(
        objpoints_buf, imgpoints_buf, image_size, None, None
    )
    if ret:
        np.savez(PARAMS_FILE, mtx=mtx_new, dist=dist_new)
        print("Recalibration complete. New parameters saved.")
        return mtx_new, dist_new
    return None, None


def main():
    # Load initial calibration parameters
    mtx, dist = load_camera_params()

    # Initialize ORB detector
    orb = cv2.ORB_create(nfeatures=500)

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    prev_gray = None
    prev_pts = None

    # Recalibration state
    recalib_mode = False
    objpoints_buf = []
    imgpoints_buf = []
    image_size = None
    complete_show_until = 0  # timestamp to show "RECALIBRATION COMPLETE"

    print("Starting adaptive calibration demo...")
    print("Press 'q' to exit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Capture image size once
            if image_size is None:
                image_size = (frame.shape[1], frame.shape[0])

            # Calculate drift error
            error, gray, kp = calculate_drift_error(frame, prev_gray, orb, prev_pts)
            prev_gray = gray
            prev_pts = kp

            # Trigger recalibration mode when error exceeds threshold
            if error > ERROR_THRESHOLD and not recalib_mode:
                recalib_mode = True
                objpoints_buf = []
                imgpoints_buf = []
                print("Drift detected. Starting recalibration collection...")

            # Recalibration collection loop
            if recalib_mode:
                try_collect_recalib_frame(gray, objpoints_buf, imgpoints_buf)
                frames_so_far = len(objpoints_buf)

                if frames_so_far >= RECALIB_FRAMES_NEEDED:
                    # Run recalibration with collected frames
                    mtx_new, dist_new = run_recalibration(objpoints_buf, imgpoints_buf, image_size)
                    if mtx_new is not None:
                        mtx, dist = mtx_new, dist_new
                    recalib_mode = False
                    objpoints_buf = []
                    imgpoints_buf = []
                    complete_show_until = time.time() + 2.0

            # Undistort using current (possibly updated) parameters
            undistorted = cv2.undistort(frame, mtx, dist)

            # Draw ORB keypoints on original frame
            frame_with_kp = cv2.drawKeypoints(frame, kp, None, color=COLOR_GREEN, flags=0)

            # Split screen: Original | Undistorted
            display = np.hstack([frame_with_kp, undistorted])

            # Display overlay text
            if time.time() < complete_show_until:
                # Show completion message for 2 seconds
                cv2.putText(display, "RECALIBRATION COMPLETE", TEXT_POS_RECALIB,
                            FONT, FONT_SCALE, COLOR_GREEN, FONT_THICKNESS)
                status_color = COLOR_GREEN
            elif recalib_mode:
                frames_so_far = len(objpoints_buf)
                cv2.putText(display, f"RECALIBRATING... ({frames_so_far}/{RECALIB_FRAMES_NEEDED} frames)",
                            TEXT_POS_RECALIB, FONT, FONT_SCALE, COLOR_RED, FONT_THICKNESS)
                status_color = COLOR_RED
            elif error > ERROR_THRESHOLD:
                cv2.putText(display, "RECALIBRATING...", TEXT_POS_RECALIB,
                            FONT, FONT_SCALE, COLOR_RED, FONT_THICKNESS)
                status_color = COLOR_RED
            else:
                status_color = COLOR_GREEN

            cv2.putText(display, f"Reprojection Error: {error:.4f}", TEXT_POS_ERROR,
                        FONT, FONT_SCALE, status_color, FONT_THICKNESS)

            cv2.imshow("Original | Undistorted - Adaptive Calibration", display)

            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
