"""
Distance calculation and state determination logic
"""
import numpy as np


class DistanceStateManager:
    def __init__(self, safe_threshold=150, warning_threshold=60):
        """
        Initialize distance-based state manager
        
        Args:
            safe_threshold: Distance (px) above which state is SAFE
            warning_threshold: Distance (px) below which state is DANGER
        """
        self.safe_threshold = safe_threshold
        self.warning_threshold = warning_threshold
        
        # State history for smoothing
        self.state_history = []
        self.history_length = 5
    
    def calculate_distance(self, point, boundary_points):
        """
        Calculate minimum Euclidean distance from point to boundary
        
        Args:
            point: (x, y) tuple of hand centroid position
            boundary_points: List of (x, y) tuples on object boundary
        
        Returns:
            Minimum distance in pixels
        """
        if point is None or not boundary_points:
            return float('inf')
        
        if len(boundary_points) == 0:
            return float('inf')
        
        px, py = point
        
        # Calculate distance to each boundary point
        distances = []
        for bx, by in boundary_points:
            dist = np.sqrt((px - bx)**2 + (py - by)**2)
            distances.append(dist)
        
        if not distances:
            return float('inf')
        
        min_distance = min(distances)
        
        # Debug output
        # print(f"DEBUG: Hand at ({px}, {py}), nearest boundary at {min_distance:.1f} px")
        
        return min_distance
    
    def determine_state(self, distance):
        """
        Determine state based on distance
        
        Args:
            distance: Distance in pixels
        
        Returns:
            State string: 'SAFE', 'WARNING', or 'DANGER'
        """
        if distance > self.safe_threshold:
            state = 'SAFE'
        elif distance > self.warning_threshold:
            state = 'WARNING'
        else:
            state = 'DANGER'
        
        # Add to history for smoothing
        self.state_history.append(state)
        if len(self.state_history) > self.history_length:
            self.state_history.pop(0)
        
        # Use majority voting for stability
        state_counts = {
            'SAFE': self.state_history.count('SAFE'),
            'WARNING': self.state_history.count('WARNING'),
            'DANGER': self.state_history.count('DANGER')
        }
        
        return max(state_counts, key=state_counts.get)
    
    def get_state_info(self, distance):
        """
        Get comprehensive state information
        
        Args:
            distance: Distance in pixels
        
        Returns:
            Dictionary with state and metadata
        """
        state = self.determine_state(distance)
        
        return {
            'state': state,
            'distance': distance,
            'safe_threshold': self.safe_threshold,
            'warning_threshold': self.warning_threshold,
            'percentage': self._calculate_danger_percentage(distance)
        }
    
    def _calculate_danger_percentage(self, distance):
        """
        Calculate danger level as percentage (100% = immediate danger)
        
        Args:
            distance: Distance in pixels
        
        Returns:
            Percentage (0-100)
        """
        if distance == float('inf'):
            return 0
        elif distance > self.safe_threshold:
            return 0
        elif distance < self.warning_threshold:
            return 100
        else:
            # Linear interpolation between warning and safe
            range_size = self.safe_threshold - self.warning_threshold
            return int(100 * (1 - (distance - self.warning_threshold) / range_size))