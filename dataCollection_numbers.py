import cv2 
import os
import mediapipe as mp
import time
import numpy as np

# ========== CONFIG ==========
DATA_DIR = "Number_Data"
NUM_IMAGES = 300
CAPTURE_INTERVAL = 0.1  # seconds
IMAGE_SIZE = 200

# Get user input with validation
label = input("Enter number label (0 to 10):").strip()
hand_type = input("Enter hand type (left/right):").strip().lower()

# Validate input
if not label.isdigit() or not (0 <= int(label) <= 10) or hand_type not in ["left", "right"]:
    print("[ERROR] Invalid input. Label must be 0 to 10 and hand type must be 'left' or 'right'.")
    exit()

# Folder structure like: Number_Data/0_left/
folder_name = f"{label}_{hand_type}"
save_path = os.path.join(DATA_DIR, folder_name)
os.makedirs(save_path, exist_ok=True)

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)
count = 0
start_capture = False
last_capture_time = 0

print(f"[INFO] Ready to capture images for '{label}' using '{hand_type}' hand.")
print("Press 's' to start capturing. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        # Bounding box around the hand
        h, w, _ = frame.shape
        x_list = [int(lm.x * w) for lm in hand_landmarks.landmark]
        y_list = [int(lm.y * h) for lm in hand_landmarks.landmark]
        min_x, max_x = max(min(x_list) - 20, 0), min(max(x_list) + 20, w)
        min_y, max_y = max(min(y_list) - 20, 0), min(max(y_list) + 20, h)

        # Square bounding box
        box_width = max_x - min_x
        box_height = max_y - min_y
        box_size = max(box_width, box_height)
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2

        square_min_x = max(center_x - box_size // 2, 0)
        square_max_x = min(center_x + box_size // 2, w)
        square_min_y = max(center_y - box_size // 2, 0)
        square_max_y = min(center_y + box_size // 2, h)

        hand_crop = frame[square_min_y:square_max_y, square_min_x:square_max_x]
        hand_crop_resized = cv2.resize(hand_crop, (IMAGE_SIZE, IMAGE_SIZE))

        hand_final = np.ones((IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8) * 255
        hand_final[:IMAGE_SIZE, :IMAGE_SIZE] = hand_crop_resized

        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.rectangle(frame, (square_min_x, square_min_y), (square_max_x, square_max_y), (0, 255, 0), 2)

        cv2.imshow("Hand Preview", hand_final)

        if start_capture and (time.time() - last_capture_time) >= CAPTURE_INTERVAL:
            filename = os.path.join(save_path, f"{count}.jpg")
            cv2.imwrite(filename, hand_final)
            print(f"[Saved] {filename}")
            count += 1
            last_capture_time = time.time()
    else:
        cv2.putText(frame, "No hand detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Hand Detection", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        start_capture = True
        print("[INFO] Started capturing...")
        last_capture_time = time.time()
    elif key == ord('q') or count >= NUM_IMAGES:
        print("[INFO] Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
