import cv2
import numpy as np
import mediapipe as mp
import time
import random
import os
import logging

# Suppress MediaPipe warnings
logging.getLogger('mediapipe').setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Player ratings
player_points = {
    "gk1": 85, "gk2": 90, "gk3": 70, "gk4": 88,
    "lb1": 77, "lb2": 80, "lb3": 82, "lb4": 78,
    "lcb1": 75, "lcb2": 85, "lcb3": 87, "lcb4": 80,
    "rcb1": 88, "rcb2": 82, "rcb3": 79, "rcb4": 81,
    "rb1": 76, "rb2": 85, "rb3": 80, "rb4": 78,
    "cmf1": 82, "cmf2": 89, "cmf3": 84, "cmf4": 81,
    "dmf1": 87, "dmf2": 85, "dmf3": 90, "dmf4": 80,
    "cmf5": 82, "cmf6": 89, "cmf7": 84, "cmf8": 81,
    "lwf1": 88, "lwf2": 92, "lwf3": 84, "lwf4": 86,
    "cf1": 95, "cf2": 90, "cf3": 88, "cf4": 91,
    "rwf1": 89, "rwf2": 87, "rwf3": 86, "rwf4": 84
}

# Team positions
positions = [
    {"name": "GK", "options": ["gk1", "gk2", "gk3", "gk4"]},
    {"name": "LB", "options": ["lb1", "lb2", "lb3", "lb4"]},
    {"name": "LCB", "options": ["lcb1", "lcb2", "lcb3", "lcb4"]},
    {"name": "RCB", "options": ["rcb1", "rcb2", "rcb3", "rcb4"]},
    {"name": "RB", "options": ["rb1", "rb2", "rb3", "rb4"]},
    {"name": "CMF", "options": ["cmf1", "cmf2", "cmf3", "cmf4"]},
    {"name": "DMF", "options": ["dmf1", "dmf2", "dmf3", "dmf4"]},
    {"name": "CMF", "options": ["cmf5", "cmf6", "cmf7", "cmf8"]},
    {"name": "LWF", "options": ["lwf1", "lwf2", "lwf3", "lwf4"]},
    {"name": "CF", "options": ["cf1", "cf2", "cf3", "cf4"]},
    {"name": "RWF", "options": ["rwf1", "rwf2", "rwf3", "rwf4"]}
]

def load_player_images():
    """Load all player images"""
    asset_path = "asset"
    images = {}
    
    for position in positions:
        for player in position["options"]:
            img_path = os.path.join(asset_path, f"player_{player}.jpg")
            img = cv2.imread(img_path)
            if img is None:
                # Create dummy colored rectangle if image not found
                img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
                cv2.putText(img, player.upper(), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            images[player] = img
    
    return images

def get_nose_direction(landmarks, frame_width):
    """Detect nose tilt direction for selection"""
    # Get nose tip and face center points
    nose_tip = landmarks.landmark[1]  # Nose tip
    left_cheek = landmarks.landmark[234]  # Left cheek
    right_cheek = landmarks.landmark[454]  # Right cheek
    
    # Calculate face center
    face_center_x = (left_cheek.x + right_cheek.x) / 2
    
    # Calculate nose offset from center
    nose_offset = nose_tip.x - face_center_x
    
    # Threshold for nose tilt detection (adjusted for sensitivity)
    tilt_threshold = 0.02
    
    if nose_offset > tilt_threshold:
        return "right"
    elif nose_offset < -tilt_threshold:
        return "left"
    else:
        return "center"

def create_result_display(selected_players, player_images):
    """Create final team formation display"""
    canvas = np.ones((720, 1280, 3), dtype=np.uint8) * 34
    
    # 4-3-3 Formation positions
    formation_positions = [
        (640, 620),  # GK
        (320, 480), (480, 480), (800, 480), (960, 480),  # Defense
        (480, 340), (640, 320), (800, 340),  # Midfield
        (400, 180), (640, 150), (880, 180)   # Attack
    ]
    
    total_score = 0
    
    for i, player in enumerate(selected_players[:11]):
        if i < len(formation_positions):
            x, y = formation_positions[i]
            
            # Resize and place player image
            img = cv2.resize(player_images[player], (80, 80))
            canvas[y:y+80, x-40:x+40] = img
            
            # Add player rating
            score = player_points[player]
            total_score += score
            cv2.putText(canvas, f"{score}", (x-15, y+100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Team rating
    if total_score >= 900:
        rating = "LEGENDARY TEAM!"
    elif total_score >= 800:
        rating = "EXCELLENT TEAM!"
    elif total_score >= 700:
        rating = "GOOD TEAM"
    elif total_score >= 600:
        rating = "DECENT TEAM"
    else:
        rating = "WEAK TEAM"
    
    # Display total score and rating
    cv2.putText(canvas, f"Total: {total_score}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(canvas, rating, (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
    
    return canvas

def main():
    # Initialize camera with error handling
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
        
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    mp_face_mesh = mp.solutions.face_mesh
    
    # Load player images
    player_images = load_player_images()
    
    # Game state
    current_position = 0
    selected_players = []
    last_action_time = 0
    action_cooldown = 2.0  # Seconds between selections
    
    # Current selection options
    current_options = None
    option_display_time = 0
    show_options_duration = 3.0  # Show options for 3 seconds
    
    # Nose tilt selection state
    tilt_start_time = 0
    current_tilt_direction = "center"
    hold_duration = 1.0  # Hold for 1 second to select
    is_holding = False
    
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=False,  # Disable refine landmarks to reduce warnings
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        static_image_mode=False
    ) as face_mesh:
        
        while cap.isOpened() and current_position < len(positions):
            ret, frame = cap.read()
            if not ret:
                print("Cannot read from camera")
                break
            
            # Get frame dimensions
            frame_height, frame_width = frame.shape[:2]
            frame = cv2.flip(frame, 1)  # Mirror the frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with proper dimensions
            frame_rgb.flags.writeable = False
            results = face_mesh.process(frame_rgb)
            frame_rgb.flags.writeable = True
            
            current_time = time.time()
            position_info = positions[current_position]
            
            # Show current position
            cv2.putText(frame, f"Select {position_info['name']}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            
            # Show instructions
            cv2.putText(frame, "Tilt nose LEFT/RIGHT and HOLD 1 sec", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Generate new options if needed
            if current_options is None:
                current_options = random.sample(position_info["options"], 2)
                option_display_time = current_time
            
            # Show player options
            if current_time - option_display_time < show_options_duration:
                # Left option
                left_img = cv2.resize(player_images[current_options[0]], (120, 120))
                frame[150:270, 100:220] = left_img
                cv2.putText(frame, f"LEFT: {current_options[0].upper()}", (80, 290), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"Rating: {player_points[current_options[0]]}", (80, 320), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Right option
                right_img = cv2.resize(player_images[current_options[1]], (120, 120))
                frame[150:270, 400:520] = right_img
                cv2.putText(frame, f"RIGHT: {current_options[1].upper()}", (380, 290), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"Rating: {player_points[current_options[1]]}", (380, 320), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Detect nose direction and handle hold mechanism
            if results.multi_face_landmarks and current_time - last_action_time > action_cooldown:
                try:
                    face_landmarks = results.multi_face_landmarks[0]
                    nose_direction = get_nose_direction(face_landmarks, frame_width)
                    
                    # Check if direction changed
                    if nose_direction != current_tilt_direction:
                        current_tilt_direction = nose_direction
                        if nose_direction in ["left", "right"]:
                            tilt_start_time = current_time
                            is_holding = True
                        else:
                            is_holding = False
                    
                    # Calculate hold progress
                    hold_progress = 0
                    if is_holding and current_tilt_direction in ["left", "right"]:
                        hold_progress = min((current_time - tilt_start_time) / hold_duration, 1.0)
                    
                    # Show current direction and progress
                    direction_color = (0, 255, 0) if current_tilt_direction in ["left", "right"] else (255, 0, 0)
                    cv2.putText(frame, f"Nose: {current_tilt_direction.upper()}", (50, 400), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, direction_color, 2)
                    
                    # Show hold progress bar
                    if is_holding and current_tilt_direction in ["left", "right"]:
                        # Progress bar background
                        cv2.rectangle(frame, (50, 430), (350, 460), (100, 100, 100), -1)
                        # Progress bar fill
                        progress_width = int(300 * hold_progress)
                        progress_color = (0, 255, 0) if hold_progress < 1.0 else (0, 255, 255)
                        cv2.rectangle(frame, (50, 430), (50 + progress_width, 460), progress_color, -1)
                        # Progress text
                        cv2.putText(frame, f"Hold: {hold_progress:.1%}", (50, 480), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Make selection when hold duration is reached
                    if is_holding and hold_progress >= 1.0:
                        if current_tilt_direction == "left":
                            selected_players.append(current_options[0])
                            cv2.putText(frame, f"SELECTED: {current_options[0].upper()}!", (200, 520), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                            current_position += 1
                            current_options = None
                            last_action_time = current_time
                            is_holding = False
                            
                        elif current_tilt_direction == "right":
                            selected_players.append(current_options[1])
                            cv2.putText(frame, f"SELECTED: {current_options[1].upper()}!", (200, 520), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                            current_position += 1
                            current_options = None
                            last_action_time = current_time
                            is_holding = False
                
                except Exception as e:
                    print(f"Face detection error: {e}")
                    pass
            
            # Show progress
            cv2.putText(frame, f"Progress: {current_position}/{len(positions)}", (50, 550), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            cv2.imshow("Team Selection", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # Show final result
    if len(selected_players) == len(positions):
        result_display = create_result_display(selected_players, player_images)
        cv2.imshow("Your Team Formation", result_display)
        cv2.waitKey(10000)  # Show for 10 seconds
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
