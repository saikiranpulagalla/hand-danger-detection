"""
Main application: Real-time hand tracking with danger detection
"""
import cv2
import numpy as np
from hand_detector import HandDetector
from virtual_object import VirtualDangerZone
from distance_logic import DistanceStateManager
from utils import resize_frame, draw_text_with_background


def find_available_camera():
    """Find the first available camera index with better error handling."""
    import subprocess
    import sys
    
    print("Searching for available cameras...")
    
    # Try Windows-specific detection
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-WmiObject Win32_PnPDevice -Filter "Name LIKE \'%Camera%\'" | Select-Object Name'],
            capture_output=True, text=True, timeout=2
        )
        if 'Camera' in result.stdout:
            print("Camera detected in Device Manager")
    except:
        pass
    
    # Try to open camera using different approaches
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i)
            # Try to read a frame to verify it actually works
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                if ret:
                    print(f"[OK] Found working camera at index {i}")
                    return i
            cap.release()
        except:
            pass
    
    return None


def main():
    # Initialize components
    hand_detector = HandDetector(min_hand_area=1000, max_hand_area=500000, use_bg_subtraction=True)
    danger_zone = VirtualDangerZone(shape='rectangle')  # Try 'circle' too!
    distance_manager = DistanceStateManager(safe_threshold=300, warning_threshold=120)
    
    # Find and open webcam
    camera_index = find_available_camera()
    if camera_index is None:
        print("\n" + "=" * 60)
        print("ERROR: No webcam found!")
        print("=" * 60)
        print("\nOptions:")
        print("1. Check if your webcam is physically connected")
        print("2. Close other applications using the camera")
        print("3. Try running the DEMO MODE instead:")
        print("   python main_demo.py")
        print("\nThe demo mode shows all features working without hardware!")
        print("=" * 60)
        return
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Cannot access camera at index {camera_index}")
        return
    
    # Set camera resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("=" * 60)
    print("HAND DANGER DETECTION SYSTEM")
    print("=" * 60)
    print("Instructions:")
    print("  - Move your hand close to the DANGER ZONE")
    print("  - Watch the state change: SAFE -> WARNING -> DANGER")
    print("")
    print("Keyboard Controls:")
    print("  q = Quit application")
    print("  c = Toggle calibration mode (for skin color)")
    print("  SPACE = Capture skin color (in calibration mode)")
    print("  d = Reset danger zone to center")
    print("  s = Increase sensitivity (lower min area)")
    print("  l = Decrease sensitivity (raise min area)")
    print("=" * 60)
    
    calibration_mode = False
    fps_counter = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame")
            break
        
        # Flip frame horizontally for mirror effect (DISABLED - causes issues with positioning)
        # frame = cv2.flip(frame, 1)
        
        # Resize for performance
        frame = resize_frame(frame, width=640)
        
        # FPS calculation
        import time
        start_time = time.time()
        
        # Initialize danger zone on first frame
        if danger_zone.frame_shape is None:
            danger_zone.initialize(frame.shape)
        
        # Detect hand
        hand_data = hand_detector.detect_hand(frame)
        
        # Calculate distance and state
        state_info = {
            'state': 'SAFE',
            'distance': float('inf'),
            'percentage': 0
        }
        
        if hand_data['centroid'] is not None:
            boundary_points = danger_zone.get_boundary_points()
            distance = distance_manager.calculate_distance(
                hand_data['centroid'], boundary_points
            )
            state_info = distance_manager.get_state_info(distance)
        
        # Draw visualizations
        # 1. Draw danger zone
        frame = danger_zone.draw(frame, state_info['state'])
        
        # 2. Draw hand contour
        if hand_data['contour'] is not None:
            cv2.drawContours(frame, [hand_data['contour']], -1, (255, 0, 255), 2)
        
        # 3. Draw hand centroid
        if hand_data['centroid'] is not None:
            cx, cy = hand_data['centroid']
            cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)
            cv2.circle(frame, (cx, cy), 10, (255, 255, 255), 2)
        
        # 4. Draw fingertip
        if hand_data['fingertip'] is not None:
            fx, fy = hand_data['fingertip']
            cv2.circle(frame, (fx, fy), 8, (255, 0, 0), -1)
            cv2.circle(frame, (fx, fy), 10, (255, 255, 255), 2)
        
        # 5. Draw distance line (from centroid to nearest boundary point)
        if hand_data['centroid'] is not None and state_info['distance'] < 300:
            boundary_points = danger_zone.get_boundary_points()
            cx, cy = hand_data['centroid']
            
            # Find closest boundary point
            distances = [
                (np.sqrt((cx - bx)**2 + (cy - by)**2), (bx, by))
                for bx, by in boundary_points
            ]
            min_dist, closest_point = min(distances, key=lambda x: x[0])
            
            cv2.line(frame, (cx, cy), closest_point, (255, 255, 0), 2)
        
        # 6. Display state and distance information
        state = state_info['state']
        distance = state_info['distance']
        
        # Hand detection status indicator
        hand_status = "HAND: DETECTED" if hand_data['detected'] else "HAND: NOT FOUND"
        hand_status_color = (0, 255, 0) if hand_data['detected'] else (0, 0, 255)
        draw_text_with_background(
            frame, hand_status, (10, 160),
            font_scale=0.7, color=hand_status_color,
            bg_color=(0, 0, 0), thickness=2
        )
        
        # State text with color coding
        state_colors = {
            'SAFE': (0, 255, 0),
            'WARNING': (0, 165, 255),
            'DANGER': (0, 0, 255)
        }
        
        draw_text_with_background(
            frame, f"STATE: {state}", (10, 30),
            font_scale=1.0, color=state_colors[state],
            bg_color=(0, 0, 0), thickness=2
        )
        
        distance_text = f"Distance: {int(distance) if distance != float('inf') else '---'} px"
        draw_text_with_background(
            frame, distance_text, (10, 70),
            font_scale=0.7, color=(255, 255, 255),
            bg_color=(0, 0, 0), thickness=2
        )
        
        draw_text_with_background(
            frame, f"Danger Level: {state_info['percentage']}%", (10, 110),
            font_scale=0.7, color=(255, 255, 255),
            bg_color=(0, 0, 0), thickness=2
        )
        
        # 7. DANGER ALERT (large text overlay)
        if state == 'DANGER':
            h, w = frame.shape[:2]
            danger_text = "DANGER DANGER"
            
            # Draw large blinking text
            import math
            blink = int(time.time() * 3) % 2  # Blink effect
            if blink:
                draw_text_with_background(
                    frame, danger_text, (w // 2 - 200, h // 2),
                    font_scale=2.0, color=(255, 255, 255),
                    bg_color=(0, 0, 255), thickness=4
                )
        
        # 8. Calibration mode
        if calibration_mode:
            h, w = frame.shape[:2]
            roi_x, roi_y, roi_w, roi_h = w // 2 - 50, h // 2 - 50, 100, 100
            cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 255, 0), 2)
            draw_text_with_background(
                frame, "Place hand in box, press SPACE to capture", (10, h - 30),
                font_scale=0.6, color=(255, 255, 255), bg_color=(0, 255, 0), thickness=2
            )
        
        # 9. FPS display
        fps = 1.0 / (time.time() - start_time)
        fps_counter.append(fps)
        if len(fps_counter) > 30:
            fps_counter.pop(0)
        avg_fps = np.mean(fps_counter)
        
        draw_text_with_background(
            frame, f"FPS: {int(avg_fps)}", (frame.shape[1] - 120, 30),
            font_scale=0.7, color=(255, 255, 255),
            bg_color=(0, 0, 0), thickness=2
        )
        
        # Display frame
        cv2.imshow('Hand Danger Detection', frame)
        
        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('c'):
            calibration_mode = not calibration_mode
            if not calibration_mode:
                print("Calibration mode OFF")
            else:
                print("Calibration mode ON - place hand in green box and press SPACE")
        elif key == ord(' ') and calibration_mode:
            h, w = frame.shape[:2]
            roi = (w // 2 - 50, h // 2 - 50, 100, 100)
            hand_detector.calibrate_skin_color(frame, roi)
            print("Skin color calibrated!")
            calibration_mode = False
        elif key == ord('d'):
            # Reset danger zone to center
            danger_zone.position = None
            danger_zone.initialize(frame.shape)
            print("Danger zone reset to center")
        elif key == ord('s'):
            # Lower hand area sensitivity
            hand_detector.min_hand_area = max(1000, hand_detector.min_hand_area - 1000)
            print(f"Sensitivity increased, min_area={hand_detector.min_hand_area}")
        elif key == ord('l'):
            # Raise hand area sensitivity
            hand_detector.min_hand_area = min(10000, hand_detector.min_hand_area + 1000)
            print(f"Sensitivity decreased, min_area={hand_detector.min_hand_area}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\nApplication closed.")


if __name__ == "__main__":
    main()
