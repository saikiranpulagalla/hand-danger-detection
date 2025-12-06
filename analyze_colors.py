"""
Analyze the color ranges in the test to fix detection
"""
import cv2
import numpy as np

# Create a frame with the test hand
width, height = 640, 480
frame = np.ones((height, width, 3), dtype=np.uint8) * 100

# Draw hand in skin tone (BGR: 180, 150, 120)
hand_x, hand_y = 320, 240
cv2.circle(frame, (hand_x, hand_y), 40, (180, 150, 120), -1)

# Extract the hand region
hand_region = frame[hand_y-50:hand_y+50, hand_x-50:hand_x+50]

# Analyze in YCrCb
ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
ycrcb_hand = ycrcb[hand_y-50:hand_y+50, hand_x-50:hand_x+50]

print("Hand color analysis:")
print(f"BGR: (180, 150, 120)")
print(f"YCrCb mean: ({ycrcb_hand[:, :, 0].mean():.0f}, {ycrcb_hand[:, :, 1].mean():.0f}, {ycrcb_hand[:, :, 2].mean():.0f})")
print(f"YCrCb std: ({ycrcb_hand[:, :, 0].std():.0f}, {ycrcb_hand[:, :, 1].std():.0f}, {ycrcb_hand[:, :, 2].std():.0f})")

# Also check HSV
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
hsv_hand = hsv[hand_y-50:hand_y+50, hand_x-50:hand_x+50]

print(f"HSV mean: ({hsv_hand[:, :, 0].mean():.0f}, {hsv_hand[:, :, 1].mean():.0f}, {hsv_hand[:, :, 2].mean():.0f})")
print(f"HSV std: ({hsv_hand[:, :, 0].std():.0f}, {hsv_hand[:, :, 1].std():.0f}, {hsv_hand[:, :, 2].std():.0f})")

# Test current detection ranges
print("\nCurrent YCrCb range: Y [0, 255], Cr [133, 173], Cb [77, 127]")
lower = np.array([0, 133, 77], dtype=np.uint8)
upper = np.array([255, 173, 127], dtype=np.uint8)
mask = cv2.inRange(ycrcb, lower, upper)
print(f"Pixels in range: {cv2.countNonZero(mask)}")

# Test broader range
print("\nTesting broader ranges:")
for y_range in [[0, 255]]:
    for cr_min in [100, 120, 130, 140]:
        for cr_max in [180, 190, 200]:
            for cb_min in [60, 70, 80]:
                for cb_max in [140, 150, 160]:
                    lower = np.array([y_range[0], cr_min, cb_min], dtype=np.uint8)
                    upper = np.array([y_range[1], cr_max, cb_max], dtype=np.uint8)
                    test_mask = cv2.inRange(ycrcb, lower, upper)
                    if cv2.countNonZero(test_mask) > 1000:  # Good coverage
                        print(f"  Y [{y_range[0]}, {y_range[1]}], Cr [{cr_min}, {cr_max}], Cb [{cb_min}, {cb_max}]: {cv2.countNonZero(test_mask)} pixels")
