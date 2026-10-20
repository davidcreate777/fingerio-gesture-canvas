import cv2
import numpy as np
import datetime
import os

class DrawingCanvas:
    def __init__(self, width=1152, height=814):
        self.width = width
        self.height = height
        
        # Initialize canvas as white (255, 255, 255)
        self.canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        # Drawing parameters
        self.thickness = 6
        self.eraser_size = 30

    def draw_stroke(self, prev_pt, curr_pt, color):
        """Draw a line stroke on the canvas between two points."""
        cv2.line(self.canvas, prev_pt, curr_pt, color, self.thickness, cv2.LINE_AA)

    def erase(self, pt):
        """Erase by drawing a white circle on the canvas."""
        cv2.circle(self.canvas, pt, self.eraser_size, (255, 255, 255), -1, cv2.LINE_AA)

    def clear(self):
        """Reset the canvas to pure white."""
        self.canvas[:] = 255

    def get_image(self):
        """Return the current canvas image."""
        return self.canvas

    def save_drawing(self):
        """Save the canvas as a PNG file in a 'saves' directory.
        Returns the filename if successful, otherwise None.
        """
        if not os.path.exists("saves"):
            os.makedirs("saves")
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saves/fingerio_{timestamp}.png"
        
        # Save canvas directly
        success = cv2.imwrite(filename, self.canvas)
        return filename if success else None
