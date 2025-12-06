"""
Demo mode: Hand danger detection with simulated hand and webcam
Useful for testing without a physical webcam
"""
import cv2
import numpy as np
from hand_detector import HandDetector
from virtual_object import VirtualDangerZone
from distance_logic import DistanceStateManager
from utils import resize_frame, draw_text_with_background
import time
import math


def create_simulated_frame(width, height, hand_x, hand_y, hand_size=50):
    """
    Create a realistic simulated video frame with a synthetic hand
    """
    # Create background (gradient from light to darker)
    frame = np.ones((height, width, 3), dtype=np.uint8) * 180
    
    # Add some noise/texture
    noise = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
    frame = cv2.addWeighted(frame, 0.9, noise, 0.1, 0)
    
    # Add gradient background
    for y in range(height):
        intensity = int(180 - (y / height) * 50)
        frame[y, :] = [intensity, intensity + 20, intensity + 40]
    
    # Draw simulated hand (skin-colored circle and lines for fingers)
    # Skin tone in BGR: (200, 170, 150)
    cv2.circle(frame, (hand_x, hand_y), hand_size, (180, 150, 120), -1)
    
    # Draw fingers as lines extending upward and to sides
    finger_length = int(hand_size * 0.8)
    
    # Center finger (up)
    cv2.line(frame, (hand_x, hand_y - hand_size), 
             (hand_x, hand_y - hand_size - finger_length), (180, 150, 120), 8)
    
    # Left finger
    cv2.line(frame, (hand_x - hand_size, hand_y - int(hand_size * 0.5)), 
             (hand_x - hand_size - int(finger_length * 0.6), hand_y - int(hand_size * 1.2)), 
             (180, 150, 120), 8)
    
    # Right finger
    cv2.line(frame, (hand_x + hand_size, hand_y - int(hand_size * 0.5)), 
             (hand_x + hand_size + int(finger_length * 0.6), hand_y - int(hand_size * 1.2)), 
             (180, 150, 120), 8)
    
    # Add some lighting reflection
    cv2.circle(frame, (hand_x - hand_size // 3, hand_y - hand_size // 3), 
               hand_size // 3, (220, 200, 180), -1)
    
    return frame


def main_demo():
    """Demo mode main function"""
    print("=" * 60)
    print("HAND DANGER DETECTION - DEMO MODE")
    print("=" * 60)
    print("Running with simulated hand (no webcam needed)")
    print("")
    print("Controls:")
    print("  Arrow Keys = Move hand")
    print("  +/- = Adjust hand size")
    print("  r = Reset to center")
    print("  q = Quit")
    print("=" * 60)
    
    # Initialize components (use SAME thresholds as real mode)
    hand_detector = HandDetector(min_hand_area=1000, max_hand_area=500000, use_bg_subtraction=False)
    danger_zone = VirtualDangerZone(shape='rectangle')
    distance_manager = DistanceStateManager(safe_threshold=300, warning_threshold=120)
    
    # Create a window
    cv2.namedWindow('Hand Danger Detection - DEMO MODE', cv2.WINDOW_NORMAL)
    
    # Demo parameters
    width, height = 640, 480
    # Start hand on FAR LEFT (safe distance from danger zone on right)
    hand_x, hand_y = 100, height // 2
    hand_size = 50
    fps_counter = []
    
    print("Starting demo simulation...")
    print("Move the hand using arrow keys towards the red danger zone on RIGHT!")
    print("Watch the state change from SAFE to WARNING to DANGER as you move right!")
    
    while True:
        start_time = time.time()
        
        # Create simulated frame
        frame = create_simulated_frame(width, height, hand_x, hand_y, hand_size)
        
        # NO FLIP - matches real mode now (removed flip to match fixed main.py)
        # frame = cv2.flip(frame, 1)
        frame = resize_frame(frame, width=640)
        
        # Initialize danger zone
        if danger_zone.frame_shape is None:
            danger_zone.initialize(frame.shape)
        
        # For demo: manually set centroid
        # NO FLIP ADJUSTMENT - coordinates match directly now
        simulated_centroid = (hand_x, hand_y)
        simulated_fingertip = (hand_x, hand_y - hand_size - 30)
        
        # Calculate distance and state
        boundary_points = danger_zone.get_boundary_points()
        distance = distance_manager.calculate_distance(simulated_centroid, boundary_points)
        state_info = distance_manager.get_state_info(distance)
        
        # Draw visualizations
        # 1. Draw danger zone
        frame = danger_zone.draw(frame, state_info['state'])
        
        # 2. Draw simulated hand centroid
        cv2.circle(frame, simulated_centroid, 8, (0, 255, 255), -1)
        cv2.circle(frame, simulated_centroid, 10, (255, 255, 255), 2)
        
        # 3. Draw fingertip
        cv2.circle(frame, simulated_fingertip, 8, (255, 0, 0), -1)
        cv2.circle(frame, simulated_fingertip, 10, (255, 255, 255), 2)
        
        # 4. Draw distance line
        if distance < 300:
            cx, cy = simulated_centroid
            distances = [
                (np.sqrt((cx - bx)**2 + (cy - by)**2), (bx, by))
                for bx, by in boundary_points
            ]
            min_dist, closest_point = min(distances, key=lambda x: x[0])
            cv2.line(frame, (cx, cy), closest_point, (255, 255, 0), 2)
        
        # 5. Display state information
        state = state_info['state']
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
        
        # 6. DANGER ALERT
        if state == 'DANGER':
            h, w = frame.shape[:2]
            danger_text = "DANGER DANGER"
            blink = int(time.time() * 3) % 2
            if blink:
                draw_text_with_background(
                    frame, danger_text, (w // 2 - 200, h // 2),
                    font_scale=2.0, color=(255, 255, 255),
                    bg_color=(0, 0, 255), thickness=4
                )
        
        # 7. Demo mode indicator
        draw_text_with_background(
            frame, "DEMO MODE (No Webcam)", (10, 150),
            font_scale=0.7, color=(100, 100, 255),
            bg_color=(0, 0, 0), thickness=2
        )
        
        # 8. Hand info
        draw_text_with_background(
            frame, f"Hand: ({hand_x}, {hand_y}) Size: {hand_size}", (10, 190),
            font_scale=0.6, color=(200, 200, 200),
            bg_color=(0, 0, 0), thickness=1
        )
        
        # 9. FPS
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
        cv2.imshow('Hand Danger Detection - DEMO MODE', frame)
        
        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('r'):
            hand_x, hand_y = width // 2, height // 2
            print("Hand reset to center")
        elif key == 82:  # Up arrow
            hand_y = max(hand_size + 20, hand_y - 10)
        elif key == 84:  # Down arrow
            hand_y = min(height - hand_size - 20, hand_y + 10)
        elif key == 81:  # Left arrow
            hand_x = max(hand_size + 20, hand_x - 10)
        elif key == 83:  # Right arrow
            hand_x = min(width - hand_size - 20, hand_x + 10)
        elif key == ord('+') or key == ord('='):
            hand_size = min(100, hand_size + 5)
        elif key == ord('-') or key == ord('_'):
            hand_size = max(20, hand_size - 5)
    
    # Cleanup
    cv2.destroyAllWindows()
    print("\nDemo mode closed.")


if __name__ == "__main__":
    main_demo()
