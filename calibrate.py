import cv2
import numpy as np
import glob
import os

# Checkerboard dimensions (inner corners, not squares)
CHECKERBOARD = (9, 6)
IMAGES_PATH = "./checkerboard_images/*.jpg"
PARAMS_FILE = "camera_params.npz"

def main():
    # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    # Load all checkerboard images
    images = glob.glob(IMAGES_PATH)
    if not images:
        print(f"No images found in {IMAGES_PATH}. Please add images and try again.")
        return

    print(f"Found {len(images)} images. Processing...")

    # Iterate through images and find chessboard corners
    image_size = None
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if image_size is None:
            image_size = gray.shape[::-1]

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            
            # Refine corner locations
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            
            print(f"Corners detected in: {os.path.basename(fname)}")
        else:
            print(f"Corners NOT detected in: {os.path.basename(fname)}")

    if not imgpoints:
        print("Could not detect corners in any image. Calibration failed.")
        return

    # Perform camera calibration
    print("\nRunning calibration...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image_size, None, None)

    if ret:
        # Calculate total reprojection error
        total_error = 0
        for i in range(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            total_error += error
        
        avg_error = total_error / len(objpoints)
        print(f"Reprojection Error: {avg_error:.4f}")

        # Save calibration parameters
        np.savez(PARAMS_FILE, mtx=mtx, dist=dist)
        print(f"Calibration successful. Parameters saved to {PARAMS_FILE}")
    else:
        print("Calibration failed.")

if __name__ == "__main__":
    main()
