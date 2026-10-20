import cv2
import mediapipe as mp

class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        
        # Configure MediaPipe Hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Landmark indices for finger tips and PIP joints
        self.finger_tips = [8, 12, 16, 20]    # Index, Middle, Ring, Pinky
        self.finger_pips = [6, 10, 14, 18]    # PIP joints for comparison

    def process_frame(self, frame_rgb):
        """Process the frame using MediaPipe and return the hand tracking results."""
        return self.hands.process(frame_rgb)

    def draw_landmarks(self, frame, hand_landmarks):
        """Draw hand skeleton landmarks on the preview frame."""
        self.mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_draw.DrawingSpec(color=(0, 220, 0), thickness=2, circle_radius=3),
            self.mp_draw.DrawingSpec(color=(0, 180, 0), thickness=2, circle_radius=2)
        )

    def is_finger_up(self, hand_landmarks, finger_index):
        """Check if a specific finger is up.
        finger_index: 0=Index, 1=Middle, 2=Ring, 3=Pinky
        """
        tip = self.finger_tips[finger_index]
        pip = self.finger_pips[finger_index]
        return hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y

    def get_gesture_state(self, hand_landmarks):
        """Determine current mode and the cursor position based on hand landmarks.
        Returns:
            mode (str): "HOVER", "DRAW", "ERASE", "CLEAR", "IDLE"
            cursor_pos (tuple): (x_norm, y_norm) normalized coordinates of cursor finger
        """
        # Read state of 4 fingers
        index_up = self.is_finger_up(hand_landmarks, 0)
        middle_up = self.is_finger_up(hand_landmarks, 1)
        ring_up = self.is_finger_up(hand_landmarks, 2)
        pinky_up = self.is_finger_up(hand_landmarks, 3)

        # 1. CLEAR: Index, Middle, Ring, Pinky are all up
        if index_up and middle_up and ring_up and pinky_up:
            mode = "CLEAR"
            # Cursor from index
            cursor_landmark = hand_landmarks.landmark[8]
            
        # 2. ERASE: Index, Middle, Ring up, Pinky down
        elif index_up and middle_up and ring_up and not pinky_up:
            mode = "ERASE"
            # Eraser follows middle finger tip as in prototype
            cursor_landmark = hand_landmarks.landmark[12]
            
        # 3. DRAW: Index, Middle up, Ring, Pinky down
        elif index_up and middle_up and not ring_up:
            mode = "DRAW"
            # Draw cursor follows index finger tip
            cursor_landmark = hand_landmarks.landmark[8]
            
        # 4. HOVER: Index up, Middle, Ring, Pinky down
        elif index_up and not middle_up:
            mode = "HOVER"
            cursor_landmark = hand_landmarks.landmark[8]
            
        # 5. IDLE
        else:
            mode = "IDLE"
            cursor_landmark = hand_landmarks.landmark[8]
            
        return mode, (cursor_landmark.x, cursor_landmark.y)
