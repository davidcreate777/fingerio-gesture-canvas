import cv2
import numpy as np

class WebcamPreview:
    def __init__(self, canvas_width=1152, canvas_height=814, title_bar_h=50):
        # Camera capture setup
        self.cap = cv2.VideoCapture(0)
        
        # Dimensions
        self.canvas_w = canvas_width
        self.canvas_h = canvas_height
        self.title_h = title_bar_h
        
        # Floating window dimension
        self.pip_w = 320
        self.pip_h = 240
        self.top_bar_h = 25
        
        # Default position (bottom-right of canvas with padding)
        self.pip_x = self.canvas_w - self.pip_w - 20
        self.pip_y = (self.canvas_h + self.title_h) - self.pip_h - 20
        
        # Dragging state
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def read_frame(self):
        """Read a frame from webcam and flip it horizontally.
        Returns:
            success (bool): capture success
            frame (ndarray): mirrored raw camera BGR frame
        """
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
        return success, frame

    def handle_mouse_event(self, event, mx, my):
        """Handle mouse drag-and-drop callbacks for the floating preview."""
        # The region includes the camera preview and its top title bar
        # Title bar: [pip_x, pip_y - top_bar_h, pip_x + pip_w, pip_y]
        # Camera feed: [pip_x, pip_y, pip_x + pip_w, pip_y + pip_h]
        in_title_bar = (self.pip_x <= mx <= self.pip_x + self.pip_w and 
                       self.pip_y - self.top_bar_h <= my <= self.pip_y)
        
        in_camera = (self.pip_x <= mx <= self.pip_x + self.pip_w and 
                    self.pip_y <= my <= self.pip_y + self.pip_h)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if in_title_bar or in_camera:
                self.is_dragging = True
                self.drag_offset_x = mx - self.pip_x
                self.drag_offset_y = my - self.pip_y
                
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.is_dragging:
                # Update position
                self.pip_x = mx - self.drag_offset_x
                self.pip_y = my - self.drag_offset_y
                
                # Constrain to canvas borders
                # Horizontal boundaries
                self.pip_x = max(10, min(self.canvas_w - self.pip_w - 10, self.pip_x))
                
                # Vertical boundaries (must account for title bar and canvas start)
                min_y = self.title_h + self.top_bar_h + 10
                max_y = (self.title_h + self.canvas_h) - self.pip_h - 10
                self.pip_y = max(min_y, min(max_y, self.pip_y))
                
        elif event == cv2.EVENT_LBUTTONUP:
            self.is_dragging = False

    def overlay_preview(self, screen_img, camera_frame, hand_detector, has_hand):
        """Resize camera frame, draw landmarks if any, and render the PiP panel on the screen buffer."""
        # 1. Process hand drawings directly on the raw camera frame (makes landmarks smooth and high resolution)
        preview_frame = camera_frame.copy()
        
        # 2. Resize to PiP dimensions
        preview_frame = cv2.resize(preview_frame, (self.pip_w, self.pip_h))
        
        # 3. Draw PiP Title Bar
        tx1 = self.pip_x
        ty1 = self.pip_y - self.top_bar_h
        tx2 = self.pip_x + self.pip_w
        ty2 = self.pip_y
        
        # Title bar background
        cv2.rectangle(screen_img, (tx1, ty1), (tx2, ty2), (30, 26, 24), -1)
        
        # Red 'recording/live' indicator dot
        cv2.circle(screen_img, (tx1 + 15, ty1 + 12), 4, (0, 0, 255), -1, cv2.LINE_AA)
        
        # Title text
        cv2.putText(
            screen_img, 
            "LIVE CAMERA", 
            (tx1 + 28, ty1 + 17), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.38, 
            (255, 255, 255), 
            1, 
            cv2.LINE_AA
        )
        
        # 4. Insert camera feed
        screen_img[self.pip_y : self.pip_y + self.pip_h, self.pip_x : self.pip_x + self.pip_w] = preview_frame
        
        # 5. Draw panel border
        cv2.rectangle(
            screen_img, 
            (tx1, ty1), 
            (tx2, self.pip_y + self.pip_h), 
            (40, 40, 40), 
            2, 
            cv2.LINE_AA
        )

    def release(self):
        """Release the capture device."""
        self.cap.release()
