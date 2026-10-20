import cv2
import numpy as np
from gestures import HandGestureDetector
from drawing import DrawingCanvas
from camera import WebcamPreview
from colors import ColorPalette
from ui import FingerIO_UI

def main():
    # 1. Initialize core system components
    # Using window resolution 1536 x 864
    screen_w, screen_h = 1536, 864
    canvas_w, canvas_h = 1152, 814
    title_bar_h = 50
    
    detector = HandGestureDetector()
    canvas = DrawingCanvas(width=canvas_w, height=canvas_h)
    camera = WebcamPreview(canvas_width=canvas_w, canvas_height=canvas_h, title_bar_h=title_bar_h)
    palette = ColorPalette()
    ui = FingerIO_UI(width=screen_w, height=screen_h)

    # Full-screen window setup
    win_name = "FingerIO"
    cv2.namedWindow(win_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # 2. Main control states
    running = True
    prev_cx, prev_cy = None, None
    prev_draw_x, prev_draw_y = None, None
    prev_mode = "IDLE"
    
    # Cursor coordinate smoothing factor (Exponential Moving Average)
    alpha = 0.4
    
    # Visual notification variables
    save_msg_timer = 0
    save_msg_text = ""

    # 3. Mouse Callback for Draggable Preview & Close Button
    def mouse_callback(event, x, y, flags, param):
        nonlocal running
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check custom window close click
            if ui.check_close_click(x, y):
                running = False
                return
        # Delegate dragging inputs to webcam preview window
        camera.handle_mouse_event(event, x, y)

    cv2.setMouseCallback(win_name, mouse_callback)

    print("FingerIO Application Loop Started. Press 'S' to Save, 'Q' to Exit.")

    while running:
        # 1. Capture camera frame
        success, cam_frame = camera.read_frame()
        if not success:
            print("Warning: Camera frame capture failed.")
            # If camera is disconnected, use a placeholder frame so UI continues to run
            cam_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(cam_frame, "No Camera Found", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            hand_detected = False
            results = None
        else:
            hand_detected = True
            # Process hand gestures in RGB
            rgb_frame = cv2.cvtColor(cam_frame, cv2.COLOR_BGR2RGB)
            results = detector.process_frame(rgb_frame)

        mode = "IDLE"
        smoothed_cx, smoothed_cy = None, None

        # 2. Process Hand Tracking Coordinates and State Machine
        if hand_detected and results and results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw skeleton overlays directly on raw webcam frame for PiP preview
            detector.draw_landmarks(cam_frame, hand_landmarks)
            
            # Extract normalized tip coordinates and current gesture state
            raw_mode, (norm_x, norm_y) = detector.get_gesture_state(hand_landmarks)
            mode = raw_mode
            
            # Map normalized coordinates to FULL WINDOW dimensions
            target_cx = int(norm_x * screen_w)
            target_cy = int(norm_y * screen_h)
            
            # Apply EMA coordinate smoothing to prevent brush jitter
            if prev_cx is None or prev_cy is None:
                smoothed_cx = target_cx
                smoothed_cy = target_cy
            else:
                smoothed_cx = int(alpha * target_cx + (1 - alpha) * prev_cx)
                smoothed_cy = int(alpha * target_cy + (1 - alpha) * prev_cy)
                
            prev_cx, prev_cy = smoothed_cx, smoothed_cy
            
            # Trigger Color Selection Collision logic in hover mode
            palette.update(smoothed_cx, smoothed_cy, mode == "HOVER")
            
        else:
            # Hand tracking lost, reset cursor histories
            prev_cx, prev_cy = None, None
            prev_mode = "IDLE"

        # 3. Canvas State Updates
        if smoothed_cx is not None and smoothed_cy is not None:
            # Map screen coordinate space to Canvas pixel coordinates
            canvas_x = smoothed_cx
            canvas_y = smoothed_cy - title_bar_h
            
            # Check if hand cursor lies within canvas boundaries
            in_canvas = (0 <= canvas_x < canvas_w and 0 <= canvas_y < canvas_h)
            
            if in_canvas:
                if mode == "DRAW":
                    # Clean drawing stroke connection:
                    # Prevent drawing lines stretching from other modes (e.g. Hover to Draw transition)
                    if prev_mode == "DRAW" and prev_draw_x is not None:
                        canvas.draw_stroke(
                            (prev_draw_x, prev_draw_y), 
                            (canvas_x, canvas_y), 
                            palette.get_active_color()
                        )
                    prev_draw_x = canvas_x
                    prev_draw_y = canvas_y
                elif mode == "ERASE":
                    # Brush erasing
                    canvas.erase((canvas_x, canvas_y))
                    prev_draw_x, prev_draw_y = None, None
                else:
                    # Reset stroke tracking in any other gesture mode
                    prev_draw_x, prev_draw_y = None, None
            else:
                # Left canvas boundary, disconnect stroke lines
                prev_draw_x, prev_draw_y = None, None
            
            # Handle clear canvas (instant trigger)
            if mode == "CLEAR":
                canvas.clear()
                
            prev_mode = mode
        else:
            # Hand tracking lost, reset stroke tracking
            prev_draw_x, prev_draw_y = None, None
            prev_mode = "IDLE"

        # 4. Render Layout & Sections
        # Fill base backgrounds (sidebar, top bar, headers)
        ui.draw_base_layout()
        
        # Draw canvas image onto the left window pane
        ui.draw_canvas(canvas.get_image())
        
        # Render static gesture guidelines in sidebar
        ui.draw_gesture_guide()
        
        # Draw active color palette buttons
        palette.draw(ui.screen_buffer)
        
        # Render Mode / Color status cards
        ui.draw_status_widget(mode, palette.get_active_color_name(), palette.get_active_color())
        
        # Draw saving guidelines
        ui.draw_save_guide()
        
        # Overlay active cursor indicators (brush preview, eraser border, select ring)
        if smoothed_cx is not None and smoothed_cy is not None:
            ui.draw_cursor(smoothed_cx, smoothed_cy, mode, palette.get_active_color(), canvas.eraser_size)
            
        # Overlay picture-in-picture camera feed
        camera.overlay_preview(ui.screen_buffer, cam_frame, detector, hand_detected)

        # 5. Save Confirmation Banner Visuals
        if save_msg_timer > 0:
            # Draw green overlay alert banner on top of the canvas
            cv2.rectangle(ui.screen_buffer, (10, 60), (450, 110), (240, 255, 240), -1)
            cv2.rectangle(ui.screen_buffer, (10, 60), (450, 110), (46, 174, 69), 1, cv2.LINE_AA)
            cv2.putText(
                ui.screen_buffer, 
                save_msg_text, 
                (20, 92), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.42, 
                (46, 174, 69), 
                1, 
                cv2.LINE_AA
            )
            save_msg_timer -= 1

        # 6. Display Screen Buffer & Capture Inputs
        cv2.imshow(win_name, ui.screen_buffer)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == 27: # 'q' or ESC
            running = False
        elif key == ord('s'):
            # Save drawing layer
            saved_file = canvas.save_drawing()
            if saved_file:
                save_msg_text = f"SUCCESS: Saved Canvas to {saved_file}"
                print(save_msg_text)
            else:
                save_msg_text = "ERROR: Failed to save canvas"
            save_msg_timer = 90  # display message for about 3 seconds
            
    # Cleanup capture devices and close windows
    camera.release()
    cv2.destroyAllWindows()
    print("FingerIO Application Exited Safely.")

if __name__ == "__main__":
    main()
