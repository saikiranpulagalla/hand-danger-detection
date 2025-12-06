"""
Debug: check what the detection mask shows
"""
import cv2
import numpy as np

frame = np.ones((480, 640, 3), dtype=np.uint8) * 100  # Dark background
cv2.circle(frame, (320, 240), 40, (180, 150, 120), -1)  # Skin-colored hand

# Convert to YCrCb
ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

# Current range (NEW)
lower = np.array([80, 100, 130], dtype=np.uint8)
upper = np.array([200, 125, 160], dtype=np.uint8)
mask = cv2.inRange(ycrcb, lower, upper)

print(f"YCrCb range mask: {cv2.countNonZero(mask)} pixels")

# HSV
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
lower_hsv1 = np.array([0, 20, 40], dtype=np.uint8)
upper_hsv1 = np.array([25, 255, 255], dtype=np.uint8)
lower_hsv2 = np.array([330, 20, 40], dtype=np.uint8)
upper_hsv2 = np.array([360, 255, 255], dtype=np.uint8)

hsv_mask = cv2.bitwise_or(
    cv2.inRange(hsv, lower_hsv1, upper_hsv1),
    cv2.inRange(hsv, lower_hsv2, upper_hsv2)
)
print(f"HSV mask: {cv2.countNonZero(hsv_mask)} pixels")

# Combined
combined = cv2.bitwise_or(mask, hsv_mask)
print(f"Combined: {cv2.countNonZero(combined)} pixels")

# After morphology
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
morph = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=1)
morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel, iterations=1)
print(f"After morphology: {cv2.countNonZero(morph)} pixels")

# Contours
contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Contours found: {len(contours)}")
for i, c in enumerate(contours):
    area = cv2.contourArea(c)
    print(f"  Contour {i}: area={area:.0f}")
