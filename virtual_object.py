"""
Virtual danger zone object rendering
"""
import cv2
import numpy as np


class VirtualDangerZone:
    def __init__(self, shape='rectangle', position=None, size=None):
        """
        Initialize virtual danger zone
        
        Args:
            shape: 'rectangle' or 'circle'
            position: (x, y) position. If None, placed at top-right
            size: (width, height) for rectangle or radius for circle
        """
        self.shape = shape
        self.position = position
        self.size = size
        self.frame_shape = None
        
        # Visual properties based on state
        self.state_colors = {
            'SAFE': (0, 255, 0),      # Green
            'WARNING': (0, 165, 255),  # Orange
            'DANGER': (0, 0, 255)      # Red
        }
        
        self.state_thickness = {
            'SAFE': 2,
            'WARNING': 3,
            'DANGER': 5
        }
    
    def initialize(self, frame_shape):
        """
        Initialize position and size based on frame dimensions
        
        Args:
            frame_shape: (height, width) of the video frame
        """
        self.frame_shape = frame_shape
        height, width = frame_shape[:2]
        
        # Default position: right side of frame (where hand naturally reaches in forward view)
        if self.position is None:
            if self.shape == 'rectangle':
                self.position = (width - 300, height // 2 - 100)
            else:  # circle
                self.position = (width - 150, height // 2)
        
        # Default size (large for easy interaction)
        if self.size is None:
            if self.shape == 'rectangle':
                self.size = (250, 200)  # (width, height)
            else:  # circle
                self.size = 100  # radius
    
    def draw(self, frame, state='SAFE'):
        """
        Draw the virtual danger zone on the frame
        
        Args:
            frame: Frame to draw on
            state: Current state ('SAFE', 'WARNING', 'DANGER')
        
        Returns:
            Modified frame
        """
        if self.frame_shape is None:
            self.initialize(frame.shape)
        
        color = self.state_colors.get(state, (0, 255, 0))
        thickness = self.state_thickness.get(state, 2)
        
        if self.shape == 'rectangle':
            x, y = self.position
            w, h = self.size
            
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
            
            # Fill with semi-transparent color in DANGER state
            if state == 'DANGER':
                overlay = frame.copy()
                cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)
                cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            
            # Draw "DANGER ZONE" label
            label = "DANGER ZONE"
            cv2.putText(
                frame, label, (x + 10, y + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
        
        elif self.shape == 'circle':
            cx, cy = self.position
            radius = self.size
            
            # Draw circle
            cv2.circle(frame, (cx, cy), radius, color, thickness)
            
            # Fill with semi-transparent color in DANGER state
            if state == 'DANGER':
                overlay = frame.copy()
                cv2.circle(overlay, (cx, cy), radius, color, -1)
                cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            
            # Draw "DANGER" label
            label = "DANGER"
            cv2.putText(
                frame, label, (cx - 40, cy + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
        
        return frame
    
    def get_boundary_points(self):
        """
        Get boundary points for distance calculation
        
        Returns:
            List of (x, y) points on the boundary
        """
        if self.shape == 'rectangle':
            x, y = self.position
            w, h = self.size
            
            # Sample points along rectangle perimeter
            points = []
            # Top edge
            for i in range(0, w, 5):
                points.append((x + i, y))
            # Right edge
            for i in range(0, h, 5):
                points.append((x + w, y + i))
            # Bottom edge
            for i in range(w, 0, -5):
                points.append((x + i, y + h))
            # Left edge
            for i in range(h, 0, -5):
                points.append((x, y + i))
            
            return points
        
        elif self.shape == 'circle':
            cx, cy = self.position
            radius = self.size
            
            # Sample points along circle perimeter
            points = []
            for angle in range(0, 360, 5):
                rad = np.radians(angle)
                x = int(cx + radius * np.cos(rad))
                y = int(cy + radius * np.sin(rad))
                points.append((x, y))
            
            return points