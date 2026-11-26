
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import argparse

# Parse input arguments
parser = argparse.ArgumentParser(description="Locate target image in scene image.")
parser.add_argument("target", type=str, help="Path to the target image")
parser.add_argument("feat", type=str, help="Feature detector")
parser.add_argument("--draw_matches", action="store_true")
args = parser.parse_args()

# Load images
target = cv.imread(args.target, cv.IMREAD_COLOR_BGR)
if target is None:
    raise ValueError("Could not load one or both input images.")
h, w, *_ = target.shape

cap = cv.VideoCapture(0)

# Initialize feature extractor
if args.feat == "SIFT":
    feat_detector = cv.SIFT_create()
    FLANN_INDEX_LSH = 6
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

elif args.feat == "ORB":
    feat_detector = cv.ORB_create()
    FLANN_INDEX_LSH = 6
    index_params = dict(algorithm=FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
    search_params = dict(checks=50)

# Initialize FLANN matcher
flann = cv.FlannBasedMatcher(index_params, search_params)

# Target image corners for BBox transformation
pts = np.float32([
    [0, 0],
    [0, h - 1],
    [w - 1, h - 1],
    [w - 1, 0]
]).reshape(-1, 1, 2)

# pre-compute target features
kpT, desT = feat_detector.detectAndCompute(target, None)

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Can't receive frame. Skipping ...")
        continue

    try:
        kpF, desF = feat_detector.detectAndCompute(frame, None)

        if desF is None or len(kpF) < 4:
            raise ValueError("Could not detect features in frame.")

        # Find nearest matches
        matches = flann.knnMatch(desT, desF, k=2)

        # Apply Lowe's ratio test
        good = [m[0] for m in matches if len(m) == 2 and m[0].distance < 0.7 * m[1].distance]
        if len(good) < 4:
            raise ValueError("Not enough good matches to calculate homography.")

        # Extract matching points
        src_pts = np.float32([kpT[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kpF[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # Calculate homography using RANSAC
        M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)

        if M is None:
            raise ValueError("Could not estimate homography.")

        # Project target image corners onto frame
        dst = cv.perspectiveTransform(pts, M)

        # Draw detected target boundary
        frame = cv.polylines(frame, [np.int32(dst)], True, (0, 0, 255), 3, cv.LINE_AA)

        # Draw only RANSAC inlier matches
        matchesMask = mask.ravel().tolist()

    except ValueError as e:
        kpF = []
        matchesMask = [0] * len(good)

    finally:
        img = frame
        if args.draw_matches:
            img = cv.drawMatches(
                target, kpT,
                frame, kpF,
                good, None,
                matchesThickness=1,
                matchColor=(0, 255, 0),
                singlePointColor=None,
                matchesMask=matchesMask
            )

    cv.imshow('frame', img)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()