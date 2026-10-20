import cv2
import numpy as np
from utils import draw_filled_rounded_rect, draw_rounded_rect

class ColorPalette:
    def __init__(self):
        # Color definitions: (BGR_COLOR, LABEL, BG_COLOR, TEXT_COLOR)
        # Accented premium colors matching the visual mockup
        self.colors_dict = {
            "RED": {
                "color": (28, 28, 219),      # Premium red
                "bg_color": (245, 245, 255),  # Light pink/red
                "text_color": (28, 28, 219),
            },
            "GREEN": {
                "color": (46, 174, 69),      # Premium green
                "bg_color": (245, 255, 245),  # Light green
                "text_color": (46, 174, 69),
            },
            "BLUE": {
                "color": (219, 102, 17),     # Premium blue
                "bg_color": (255, 245, 240),  # Light blue
                "text_color": (219, 102, 17),
            },
            "BLACK": {
                "color": (20, 20, 20),        # Soft black
                "bg_color": (240, 240, 240),  # Light gray
                "text_color": (20, 20, 20),
            }
        }
        
        # Color order for UI
        self.color_keys = ["RED", "GREEN", "BLUE", "BLACK"]
        self.active_color_key = "BLUE"  # Start with BLUE as shown in mockup
        
        # Button positions: [x1, y1, x2, y2]
        self.buttons = {}
        start_y = 120
        height = 50
        gap = 15
        
        for i, key in enumerate(self.color_keys):
            y1 = start_y + i * (height + gap)
            y2 = y1 + height
            self.buttons[key] = [1172, y1, 1516, y2]
            
        # Hover tracking: {COLOR_KEY: frame_count}
        self.hover_counts = {key: 0 for key in self.color_keys}
        self.hover_threshold = 24  # About 0.8 seconds at ~30 FPS

    def get_active_color(self):
        return self.colors_dict[self.active_color_key]["color"]

    def get_active_color_name(self):
        return self.active_color_key

    def update(self, finger_x, finger_y, is_hover_mode):
        """Update hover counts based on finger position and mode."""
        if not is_hover_mode:
            # Reset hover progress if not in hover mode
            for key in self.color_keys:
                self.hover_counts[key] = 0
            return None

        selected_key = None
        for key, rect in self.buttons.items():
            x1, y1, x2, y2 = rect
            if x1 <= finger_x <= x2 and y1 <= finger_y <= y2:
                self.hover_counts[key] += 1
                if self.hover_counts[key] >= self.hover_threshold:
                    self.active_color_key = key
                    selected_key = key
                    # Reset hover counts on successful selection
                    for k in self.color_keys:
                        self.hover_counts[k] = 0
                    break
            else:
                self.hover_counts[key] = 0
                
        return selected_key

    def draw(self, img):
        """Draw the colors palette in the sidebar."""
        for key in self.color_keys:
            rect = self.buttons[key]
            x1, y1, x2, y2 = rect
            cfg = self.colors_dict[key]
            
            # 1. Draw button background (light tint)
            draw_filled_rounded_rect(img, (x1, y1), (x2, y2), cfg["bg_color"], radius=8)
            
            # 2. Draw border
            is_active = (key == self.active_color_key)
            border_color = cfg["color"] if is_active else (220, 220, 220)
            border_thickness = 2 if is_active else 1
            draw_rounded_rect(img, (x1, y1), (x2, y2), border_color, thickness=border_thickness, radius=8)
            
            # 3. Draw color circle inside button
            circle_center = (x1 + 25, y1 + 25)
            cv2.circle(img, circle_center, 12, cfg["color"], -1, cv2.LINE_AA)
            
            # 4. Draw progress ring if hovering
            hover_pct = self.hover_counts[key] / self.hover_threshold
            if hover_pct > 0:
                angle = int(360 * hover_pct)
                # Outer ring representing selection progress
                cv2.ellipse(
                    img, 
                    circle_center, 
                    (16, 16), 
                    -90, 
                    0, 
                    angle, 
                    cfg["color"], 
                    2, 
                    cv2.LINE_AA
                )
                
            # 5. Draw color label text
            cv2.putText(
                img, 
                key, 
                (x1 + 55, y1 + 32), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.55, 
                cfg["text_color"], 
                2, 
                cv2.LINE_AA
            )
