import cv2
import numpy as np

def draw_rounded_rect(img, top_left, bottom_right, color, thickness=2, radius=10):
    """Draw an outlined rectangle with rounded corners."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # Restrict radius to size limits
    w = x2 - x1
    h = y2 - y1
    radius = min(radius, w // 2, h // 2)
    
    # Straight lines
    cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness, cv2.LINE_AA)
    
    # Corners
    cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness, cv2.LINE_AA)

def draw_filled_rounded_rect(img, top_left, bottom_right, color, radius=10):
    """Draw a filled rectangle with rounded corners."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    w = x2 - x1
    h = y2 - y1
    radius = min(radius, w // 2, h // 2)
    
    # Central blocks
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1)
    
    # Corners
    cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, -1, cv2.LINE_AA)
    cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, -1, cv2.LINE_AA)
    cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, -1, cv2.LINE_AA)
    cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, -1, cv2.LINE_AA)

def draw_pencil_icon(img, pos, color=(80, 80, 80), size=20):
    """Draw a pencil icon at a given position."""
    x, y = pos
    # Diagonal pencil body
    pts = np.array([
        [x - size//2, y + size//2],
        [x + size//4, y - size//4],
        [x + size//2, y - size//2],
        [x + size//4, y - size//2],
        [x - size//4, y - size//4]
    ], np.int32)
    
    # Draw body
    cv2.line(img, (x - size//2, y + size//2), (x + size//3, y - size//3), color, 2, cv2.LINE_AA)
    # Pencil tip
    tip_pts = np.array([
        [x - size//2, y + size//2],
        [x - size//2 + 4, y + size//2 - 1],
        [x - size//2 + 1, y + size//2 - 4]
    ], np.int32)
    cv2.fillPoly(img, [tip_pts], color)

def draw_palette_icon(img, pos, color=(80, 80, 80), size=20):
    """Draw a paint palette icon with color dots."""
    x, y = pos
    r = size // 2
    # Draw palette shape
    cv2.circle(img, (x, y), r, color, 2, cv2.LINE_AA)
    # Thumb hole
    cv2.circle(img, (x - r//3, y + r//3), r//5, color, -1, cv2.LINE_AA)
    # Color spots
    cv2.circle(img, (x + r//3, y - r//3), 2, (0, 0, 255), -1, cv2.LINE_AA) # Red
    cv2.circle(img, (x + r//2, y), 2, (0, 255, 0), -1, cv2.LINE_AA) # Green
    cv2.circle(img, (x, y - r//2), 2, (255, 0, 0), -1, cv2.LINE_AA) # Blue

def draw_disk_icon(img, pos, color=(80, 80, 80), size=20):
    """Draw a floppy disk save icon."""
    x, y = pos
    hs = size // 2
    x1, y1 = x - hs, y - hs
    x2, y2 = x + hs, y + hs
    
    # Outer frame
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)
    # Cut top right corner
    cv2.line(img, (x2 - 4, y1), (x2, y1 + 4), (255, 255, 255), 2, cv2.LINE_AA) # overlay background color
    cv2.line(img, (x2 - 4, y1), (x2, y1 + 4), color, 2, cv2.LINE_AA)
    # Slider label
    cv2.rectangle(img, (x1 + 3, y1 + 3), (x2 - 5, y1 + hs), color, 1, cv2.LINE_AA)
    # Bottom window
    cv2.rectangle(img, (x1 + 4, y2 - hs + 2), (x2 - 4, y2 - 1), color, -1, cv2.LINE_AA)

def draw_gesture_icon(img, pos, fingers_count, color=(80, 80, 80), size=24):
    """Draw a stylized hand icon showing the specified number of fingers pointing up."""
    x, y = pos
    
    # Draw palm base
    cv2.ellipse(img, (x, y + size//4), (size//3, size//4), 0, 0, 360, color, 2, cv2.LINE_AA)
    
    # Draw thumb
    cv2.line(img, (x - size//3, y + size//4), (x - size//2, y), color, 2, cv2.LINE_AA)
    
    # Draw fingers based on count
    # index, middle, ring, pinky
    finger_xs = [x - size//5, x, x + size//5, x + size//3 + 2]
    finger_heights = [size//2, size//2 + 3, size//2 - 1, size//3 + 2]
    
    for i in range(4):
        f_x = finger_xs[i]
        f_h = finger_heights[i]
        
        # Determine if finger is up or down based on index
        if i < fingers_count:
            # Finger pointing up
            cv2.line(img, (f_x, y + size//6), (f_x, y + size//6 - f_h), color, 2, cv2.LINE_AA)
            cv2.circle(img, (f_x, y + size//6 - f_h), 2, color, -1, cv2.LINE_AA)
        else:
            # Finger curled down (represented as short loop or just not drawn)
            cv2.ellipse(img, (f_x, y + size//6), (2, 4), 0, 0, 360, color, 1, cv2.LINE_AA)
