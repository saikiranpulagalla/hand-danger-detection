"""
Hand detection using background subtraction for maximum robustness
"""
import cv2
import numpy as np


class HandDetector:
    def __init__(self, min_hand_area=1000, max_hand_area=500000, use_bg_subtraction=True):
        """
        Initialize hand detector using background subtraction
        
        Args:
            min_hand_area: Minimum contour area to consider as hand
            max_hand_area: Maximum contour area to consider as hand
            use_bg_subtraction: Use background subtraction (False for demo mode, True for real)
        """
        self.min_hand_area = min_hand_area
        self.max_hand_area = max_hand_area
        self.use_bg_subtraction = use_bg_subtraction
        
        # Background subtractor - learns scene and detects moving objects
        if use_bg_subtraction:
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=100,
                varThreshold=20,
                detectShadows=False
            )
        
        # Fallback: skin color detection - TIGHT to avoid background
        self.skin_ranges = [
            # Accurate YCrCb range for skin tones ONLY
            # Hand: Y~144, Cr~111, Cb~148
            # Excludes background and other objects
            {'space': 'YCrCb', 'lower': np.array([80, 100, 130], dtype=np.uint8), 
             'upper': np.array([200, 125, 160], dtype=np.uint8)},
        ]
        
        self.frame_count = 0
    
    def detect_hand(self, frame):
        """
        Detect hand using hybrid approach:
        - Background subtraction for real webcam (catches moving objects)
        - Skin color detection (reliable fallback and primary for demo)
        
        Returns:
            dict with detected hand information
        """
        h, w = frame.shape[:2]
        self.frame_count += 1
        
        # ALWAYS use skin color detection - it's the most reliable
        combined_mask = np.zeros((h, w), dtype=np.uint8)
        
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        skin_mask = np.zeros((h, w), dtype=np.uint8)
        
        for range_info in self.skin_ranges:
            if range_info['space'] == 'YCrCb':
                mask = cv2.inRange(ycrcb, range_info['lower'], range_info['upper'])
                skin_mask = cv2.bitwise_or(skin_mask, mask)
        
        # Also try HSV for robustness
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_hsv1 = np.array([0, 20, 40], dtype=np.uint8)     # More relaxed saturation
        upper_hsv1 = np.array([25, 255, 255], dtype=np.uint8)
        lower_hsv2 = np.array([330, 20, 40], dtype=np.uint8)
        upper_hsv2 = np.array([360, 255, 255], dtype=np.uint8)
        
        hsv_mask = cv2.bitwise_or(
            cv2.inRange(hsv, lower_hsv1, upper_hsv1),
            cv2.inRange(hsv, lower_hsv2, upper_hsv2)
        )
        skin_mask = cv2.bitwise_or(skin_mask, hsv_mask)
        
        # In real mode, also try background subtraction after warming up
        if self.use_bg_subtraction and self.frame_count > 20:
            fg_mask = self.bg_subtractor.apply(frame)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
            fg_mask = cv2.dilate(fg_mask, kernel, iterations=1)
            
            # Combine: foreground AND skin color (both must match)
            combined_mask = cv2.bitwise_and(fg_mask, skin_mask)
            
            # If combination too strict, fall back to skin only
            if cv2.countNonZero(combined_mask) < 50:
                combined_mask = skin_mask
        else:
            # Demo mode or early frames: skin color only
            combined_mask = skin_mask
        
        # Final morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(
            combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        result = {
            'contour': None,
            'centroid': None,
            'fingertip': None,
            'mask': combined_mask,
            'detected': False
        }
        
        if not contours:
            return result
        
        # Filter contours by area - balanced to catch hands but reject arms/objects
        # Hand area: ~2000-100000 px depending on distance
        # Arm/large objects: 100000+ px
        hand_min_area = 2000    # Minimum to avoid small noise
        hand_max_area = 100000  # Maximum to reject large objects
        
        valid_contours = [
            c for c in contours 
            if hand_min_area < cv2.contourArea(c) < hand_max_area
        ]
        
        if not valid_contours:
            return result
        
        # Get largest contour (the hand)
        hand_contour = max(valid_contours, key=cv2.contourArea)
        result['contour'] = hand_contour
        result['detected'] = True
        
        # Calculate centroid
        M = cv2.moments(hand_contour)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            
            # Ensure centroid is in frame
            cx = max(10, min(w - 10, cx))
            cy = max(10, min(h - 10, cy))
            
            result['centroid'] = (cx, cy)
        
        # Find fingertip (topmost point)
        if len(hand_contour) > 0:
            topmost = hand_contour[hand_contour[:, 0, 1].argmin()][0]
            result['fingertip'] = tuple(topmost)
        
        return result
    
    def calibrate_skin_color(self, frame, roi):
        """
        Calibrate skin color thresholds based on ROI
        
        Args:
            frame: BGR image
            roi: (x, y, w, h) region of interest containing skin
        """
        x, y, w, h = roi
        skin_sample = frame[y:y+h, x:x+w]
        
        # Analyze in YCrCb
        ycrcb_sample = cv2.cvtColor(skin_sample, cv2.COLOR_BGR2YCrCb)
        mean_y = np.mean(ycrcb_sample[:, :, 0])
        mean_cr = np.mean(ycrcb_sample[:, :, 1])
        mean_cb = np.mean(ycrcb_sample[:, :, 2])
        
        std_y = np.std(ycrcb_sample[:, :, 0])
        std_cr = np.std(ycrcb_sample[:, :, 1])
        std_cb = np.std(ycrcb_sample[:, :, 2])
        
        # Update range with calibrated values (mean ± 2*std)
        self.skin_ranges[0]['lower'] = np.clip(
            [mean_y - 2*std_y, mean_cr - 2*std_cr, mean_cb - 2*std_cb], 0, 255
        ).astype(np.uint8)
        self.skin_ranges[0]['upper'] = np.clip(
            [mean_y + 2*std_y, mean_cr + 2*std_cr, mean_cb + 2*std_cb], 0, 255
        ).astype(np.uint8)
        
        print(f"Skin color calibrated!")
        print(f"  Y: {self.skin_ranges[0]['lower'][0]:.0f}-{self.skin_ranges[0]['upper'][0]:.0f}")
        print(f"  Cr: {self.skin_ranges[0]['lower'][1]:.0f}-{self.skin_ranges[0]['upper'][1]:.0f}")
        print(f"  Cb: {self.skin_ranges[0]['lower'][2]:.0f}-{self.skin_ranges[0]['upper'][2]:.0f}")