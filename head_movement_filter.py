import cv2
import numpy as np
import mediapipe as mp
import time
import random
import os

def calculate_head_angle(nose_tip, face_center_x):
    return (nose_tip.x - face_center_x) * 100

def resize_image(image, width, height):
    if image is None:
        return np.zeros((height, width, 3), dtype=np.uint8)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

def overlay_image(background, overlay, position):
    x, y = position
    h, w, _ = overlay.shape
    bh, bw, _ = background.shape
    w = min(w, bw - x)
    h = min(h, bh - y)
    overlay_resized = cv2.resize(overlay, (w, h))
    background[y:y+h, x:x+w] = overlay_resized
    return background

player_points = {
    "gk1": 85, "gk2": 90, "gk3": 70, "gk4": 88,
    "lb1": 77, "lb2": 80, "lb3": 82, "lb4": 78,
    "lcb1": 75, "lcb2": 85, "lcb3": 87, "lcb4": 80,
    "rcb1": 88, "rcb2": 82, "rcb3": 79, "rcb4": 81,
    "rb1": 76, "rb2": 85, "rb3": 80, "rb4": 78,
    "cmf1": 82, "cmf2": 89, "cmf3": 84, "cmf4": 81,
    "dmf1": 87, "dmf2": 85, "dmf3": 90, "dmf4": 80,
    "lwf1": 88, "lwf2": 92, "lwf3": 84, "lwf4": 86,
    "cf1": 95, "cf2": 90, "cf3": 88, "cf4": 91,
    "rwf1": 89, "rwf2": 87, "rwf3": 86, "rwf4": 84
}

asset_path = "asset"
player_images = {}
for name in player_points.keys():
    path = os.path.join(asset_path, f"player_{name}.jpg")
    img = cv2.imread(path)
    player_images[name] = img if img is not None else np.zeros((150, 150, 3), dtype=np.uint8)

positions = [
    {"name": " GK", "options": ["gk1", "gk2", "gk3", "gk4"]},
    {"name": "LB", "options": ["lb1", "lb2", "lb3", "lb4"]},
    {"name": "LCB", "options": ["lcb1", "lcb2", "lcb3", "lcb4"]},
    {"name": "RCB", "options": ["rcb1", "rcb2", "rcb3", "rcb4"]},
    {"name": "RB", "options": ["rb1", "rb2", "rb3", "rb4"]},
    {"name": "CMF1", "options": ["cmf1", "cmf2", "cmf3", "cmf4"]},
    {"name": "DMF", "options": ["dmf1", "dmf2", "dmf3", "dmf4"]},
    {"name": "CMF2", "options": ["cmf1", "cmf2", "cmf3", "cmf4"]},
    {"name": "LWF", "options": ["lwf1", "lwf2", "lwf3", "lwf4"]},
    {"name": "CF", "options": ["cf1", "cf2", "cf3", "cf4"]},
    {"name": "RWF", "options": ["rwf1", "rwf2", "rwf3", "rwf4"]}
]

def create_result_display(selected_players):
    canvas = np.ones((720, 1280, 3), dtype=np.uint8) * 34
    coords = {
        "goalkeeper": [(640, 620)],
        "defenders": [(340, 470), (540, 470), (740, 470), (940, 470)],
        "midfielders": [(440, 270), (640, 320), (840, 270)],
        "forwards": [(340, 120), (640, 70), (940, 120)]
    }

    scores = [player_points[p] for p in selected_players]
    total = sum(scores)
    rating = "Very Very Very Nice Team!" if total >= 900 else \
             "Good Team" if total >= 800 else \
             "Better Team" if total >= 700 else \
             "Goodluck Team" if total >= 600 else "Bad Team"

    for i, p in enumerate(selected_players):
        img = resize_image(player_images[p], 80, 80)
        if i == 0:
            x, y = coords["goalkeeper"][0]
        elif i < 5:
            x, y = coords["defenders"][i-1]
        elif i < 8:
            x, y = coords["midfielders"][i-5]
        else:
            x, y = coords["forwards"][i-8]
        canvas[y:y+80, x:x+80] = img
        cv2.putText(canvas, f"{scores[i]} pts", (x, y+100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(canvas, f"Total Score: {total}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
    cv2.putText(canvas, rating, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
    return canvas

def main():
    cap = cv2.VideoCapture(0)
    selected_players = []
    idx = 0
    last_time = time.time()
    stable_count = 0
    prev_dir = None
    selected_options = {}
    angle_threshold = 7
    stability_threshold = 5
    cooldown = 1.0
    confirm_time = None
    showing_result = False

    with mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            direction = None

            if results.multi_face_landmarks and idx < len(positions):
                face = results.multi_face_landmarks[0]
                nose = face.landmark[1]
                left = face.landmark[234]
                right = face.landmark[454]
                center_x = (left.x + right.x) / 2
                angle = calculate_head_angle(nose, center_x)

                if angle > angle_threshold:
                    direction = "right"
                elif angle < -angle_threshold:
                    direction = "left"

                if direction == prev_dir:
                    stable_count += 1
                else:
                    stable_count = 0
                prev_dir = direction

                pos = positions[idx]
                if pos["name"] not in selected_options:
                    selected_options[pos["name"]] = random.sample(pos["options"], 2)
                p1, p2 = selected_options[pos["name"]]
                img1 = resize_image(player_images[p1], 150, 150)
                img2 = resize_image(player_images[p2], 150, 150)
                frame = overlay_image(frame, img1, (50, 100))
                frame = overlay_image(frame, img2, (400, 100))

                if direction == "left":
                    cv2.rectangle(frame, (50, 100), (200, 250), (0, 255, 0), 3)
                elif direction == "right":
                    cv2.rectangle(frame, (400, 100), (550, 250), (0, 255, 0), 3)

                if stable_count >= stability_threshold and time.time() - last_time > cooldown:
                    chosen = p1 if direction == "left" else p2
                    selected_players.append(chosen)
                    idx += 1
                    last_time = time.time()

            if idx >= len(positions) and not showing_result:
                result_img = create_result_display(selected_players)
                showing_result = True

            if showing_result:
                cv2.imshow("Starting Eleven Result", result_img)
            else:
                cv2.imshow("Starting Eleven Selection", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a'):
                prev_dir = "left"; stable_count = stability_threshold
            elif key == ord('d'):
                prev_dir = "right"; stable_count = stability_threshold

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
