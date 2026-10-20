import cv2
import numpy as np
from utils import draw_filled_rounded_rect, draw_rounded_rect, draw_pencil_icon, draw_palette_icon, draw_disk_icon, draw_gesture_icon

class FingerIO_UI:
    def __init__(self, width=1536, height=864):
        self.width = width
        self.height = height
        self.canvas_w = 1152
        self.canvas_h = 814
        self.title_h = 50
        
        # Initialize screen buffer
        self.screen_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Colors
        self.bg_sidebar = (248, 246, 245)   # Light gray-blue
        self.title_bg = (30, 26, 24)        # Dark navy/charcoal
        self.text_dark = (40, 40, 40)       # Charcoal text
        self.white = (255, 255, 255)
        self.border_gray = (225, 222, 220)  # Subtle border gray
        
        # Close button rect: [x1, y1, x2, y2]
        self.close_btn_rect = [1485, 10, 1520, 40]

    def check_close_click(self, mx, my):
        """Check if mouse clicked the close button on the custom title bar."""
        x1, y1, x2, y2 = self.close_btn_rect
        return x1 <= mx <= x2 and y1 <= my <= y2

    def draw_base_layout(self):
        """Clear and paint the background sections: sidebar and title bar."""
        # 1. Fill entire screen buffer with white (default for canvas area)
        self.screen_buffer[:] = 255
        
        # 2. Draw sidebar background (x from 1152 to 1536, y from 50 to 864)
        self.screen_buffer[self.title_h : self.height, self.canvas_w : self.width] = self.bg_sidebar
        
        # 3. Draw vertical separator border between canvas and sidebar
        cv2.line(
            self.screen_buffer, 
            (self.canvas_w, self.title_h), 
            (self.canvas_w, self.height), 
            self.border_gray, 
            2, 
            cv2.LINE_AA
        )
        
        # 4. Draw title bar background (x from 0 to 1536, y from 0 to 50)
        self.screen_buffer[0 : self.title_h, 0 : self.width] = self.title_bg
        
        # 5. Draw Title Text "FINGERIO" centered
        cv2.putText(
            self.screen_buffer, 
            "FINGERIO", 
            (self.width // 2 - 70, 34), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.8, 
            self.white, 
            2, 
            cv2.LINE_AA
        )
        
        # 6. Draw custom window controls at top right
        # Minimize "-"
        cv2.line(self.screen_buffer, (1415, 25), (1427, 25), self.white, 2, cv2.LINE_AA)
        
        # Maximize "[]"
        cv2.rectangle(self.screen_buffer, (1450, 19), (1462, 31), self.white, 2, cv2.LINE_AA)
        
        # Close "X"
        x1, y1, x2, y2 = self.close_btn_rect
        # Draw soft red hover highlight if we want, but simple outline for now
        cv2.line(self.screen_buffer, (1492, 19), (1504, 31), self.white, 2, cv2.LINE_AA)
        cv2.line(self.screen_buffer, (1504, 19), (1492, 31), self.white, 2, cv2.LINE_AA)

        # 7. Draw Sidebar Section Headers
        # Colors Header
        cv2.putText(
            self.screen_buffer, 
            "COLORS", 
            (self.canvas_w + 140, 95), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.55, 
            self.text_dark, 
            2, 
            cv2.LINE_AA
        )
        
        # Gestures Header
        cv2.putText(
            self.screen_buffer, 
            "GESTURES", 
            (self.canvas_w + 130, 435), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.55, 
            self.text_dark, 
            2, 
            cv2.LINE_AA
        )
        
        # Subtle horizontal dividers
        cv2.line(
            self.screen_buffer, 
            (self.canvas_w + 20, 395), 
            (self.width - 20, 395), 
            self.border_gray, 
            1, 
            cv2.LINE_AA
        )
        cv2.line(
            self.screen_buffer, 
            (self.canvas_w + 20, 680), 
            (self.width - 20, 680), 
            self.border_gray, 
            1, 
            cv2.LINE_AA
        )

    def draw_gesture_guide(self):
        """Draw reference gestures and their instructions in the sidebar."""
        start_y = 470
        gap = 50
        
        instructions = [
            (1, "1 Finger  -> Hover / Select"),
            (2, "2 Fingers -> Draw"),
            (3, "3 Fingers -> Erase"),
            (4, "4 Fingers -> Clear")
        ]
        
        for i, (fingers, text) in enumerate(instructions):
            y_pos = start_y + i * gap
            # Draw vector hand representation
            draw_gesture_icon(
                self.screen_buffer, 
                (self.canvas_w + 40, y_pos), 
                fingers, 
                self.text_dark, 
                22
            )
            # Draw description text
            cv2.putText(
                self.screen_buffer, 
                text, 
                (self.canvas_w + 75, y_pos + 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.45, 
                self.text_dark, 
                1, 
                cv2.LINE_AA
            )

    def draw_status_widget(self, current_mode, active_color_name, active_color_bgr):
        """Draw the status container with Mode and Color indicators."""
        x1, y1 = self.canvas_w + 20, 700
        x2, y2 = self.width - 20, 790
        
        # Border box
        draw_rounded_rect(self.screen_buffer, (x1, y1), (x2, y2), self.border_gray, thickness=1, radius=8)
        draw_filled_rounded_rect(self.screen_buffer, (x1+1, y1+1), (x2-1, y2-1), self.white, radius=8)
        
        # Mode Section
        # Icon
        draw_pencil_icon(self.screen_buffer, (x1 + 25, y1 + 25), self.text_dark, 16)
        # Label
        cv2.putText(
            self.screen_buffer, 
            "MODE", 
            (x1 + 45, y1 + 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.45, 
            self.text_dark, 
            2, 
            cv2.LINE_AA
        )
        # Value (accents draw color for drawing state, or dark gray for idle/clear)
        mode_color = active_color_bgr if current_mode == "DRAW" else (180, 50, 50) if current_mode == "ERASE" else (80, 80, 80)
        cv2.putText(
            self.screen_buffer, 
            current_mode, 
            (x1 + 220, y1 + 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.48, 
            mode_color, 
            2, 
            cv2.LINE_AA
        )
        
        # Color Section
        # Icon
        draw_palette_icon(self.screen_buffer, (x1 + 25, y1 + 60), self.text_dark, 16)
        # Label
        cv2.putText(
            self.screen_buffer, 
            "COLOR", 
            (x1 + 45, y1 + 65), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.45, 
            self.text_dark, 
            2, 
            cv2.LINE_AA
        )
        # Value
        cv2.putText(
            self.screen_buffer, 
            active_color_name, 
            (x1 + 220, y1 + 65), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.48, 
            active_color_bgr, 
            2, 
            cv2.LINE_AA
        )

    def draw_save_guide(self):
        """Draw the save guidelines at the very bottom of the sidebar."""
        x = self.canvas_w + 25
        y = 828
        # Icon
        draw_disk_icon(self.screen_buffer, (x + 10, y), self.text_dark, 16)
        # Text label
        cv2.putText(
            self.screen_buffer, 
            "Press 'S' to save as PNG", 
            (x + 30, y + 5), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.42, 
            self.text_dark, 
            1, 
            cv2.LINE_AA
        )

    def draw_canvas(self, canvas_img):
        """Copy the canvas drawing layer onto the canvas screen section."""
        self.screen_buffer[self.title_h : self.height, 0 : self.canvas_w] = canvas_img

    def draw_cursor(self, cx, cy, mode, color_bgr, eraser_size):
        """Draw a custom visual indicator at the smoothed cursor coordinate."""
        # Check if cursor falls in the canvas area (we allow cursor anywhere on screen, but only draw mode-specific shapes)
        if cy < self.title_h:
            return
            
        if mode == "DRAW" and cx < self.canvas_w:
            # Drawing cursor: dot in active color, outlined with white for visibility
            cv2.circle(self.screen_buffer, (cx, cy), 8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.circle(self.screen_buffer, (cx, cy), 5, color_bgr, -1, cv2.LINE_AA)
            
        elif mode == "ERASE" and cx < self.canvas_w:
            # Eraser cursor: Red hollow circle showing eraser bounding box
            cv2.circle(self.screen_buffer, (cx, cy), eraser_size, (50, 50, 220), 2, cv2.LINE_AA)
            cv2.circle(self.screen_buffer, (cx, cy), 2, (50, 50, 220), -1, cv2.LINE_AA)
            
        elif mode == "HOVER":
            # Selection cursor: thin dark ring
            cv2.circle(self.screen_buffer, (cx, cy), 10, (100, 100, 100), 1, cv2.LINE_AA)
            cv2.circle(self.screen_buffer, (cx, cy), 2, (100, 100, 100), -1, cv2.LINE_AA)
            
        else:
            # Idle cursor: tiny gray dot
            cv2.circle(self.screen_buffer, (cx, cy), 4, (150, 150, 150), -1, cv2.LINE_AA)

    def get_screen_buffer(self):
        """Return the rendered screen buffer."""
        return self.screen_buffer
