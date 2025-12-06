"""
Utility functions for image processing and display
"""
import cv2
import numpy as np


def resize_frame(frame, width=640):
    """
    Resize frame while maintaining aspect ratio
    
    Args:
        frame: Input frame
        width: Target width in pixels
    
    Returns:
        Resized frame
    """
    height = int(frame.shape[0] * (width / frame.shape[1]))
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)


def apply_gaussian_blur(frame, kernel_size=7):
    """
    Apply Gaussian blur to reduce noise
    
    Args:
        frame: Input frame
        kernel_size: Size of Gaussian kernel (must be odd)
    
    Returns:
        Blurred frame
    """
    return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)


def draw_text_with_background(frame, text, position, font_scale=1.0, 
                               color=(255, 255, 255), bg_color=(0, 0, 0),
                               thickness=2):
    """
    Draw text with a solid background for better visibility
    
    Args:
        frame: Frame to draw on
        text: Text string
        position: (x, y) tuple for text position
        font_scale: Scale of font
        color: Text color (BGR)
        bg_color: Background color (BGR)
        thickness: Text thickness
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )
    
    # Draw background rectangle
    x, y = position
    cv2.rectangle(
        frame,
        (x - 5, y - text_height - 5),
        (x + text_width + 5, y + baseline + 5),
        bg_color,
        -1
    )
    
    # Draw text
    cv2.putText(frame, text, position, font, font_scale, color, thickness)