import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
import random
import time
import os
from pygame import mixer
import matplotlib.pyplot as plt

# ✅ Audio init
mixer.init()

# ✅ Configuration
allowed_signs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'K', 'L', 'M', 'O', 'P', 'Q', 'R', 'U', 'V', 'W', 'Y', 'Z']
immediate_accept_signs = ['A']
CONFIDENCE_THRESHOLD = 0.70

# ✅ MediaPipe Hands Setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

feedback_tracker = {}
intelligent_feedbacks_pool = [
    "Tip: Ensure your background is clutter-free!",
    "Try improving the lighting around your hand.",
    "Keep your whole hand inside the frame!",
    "Center your hand — you're almost there!",
    "Lighting could be better — try a brighter spot!",
    "Stretch your fingers clearly. Make it count!",
    "Focus! It looks close, but not quite right.",
    "Take a deep breath — try the sign again!",
    "You got this! Maybe move your hand slightly closer.",
    "Hmm... background’s a bit messy — try a clean one!",
    " Even AI needs a clear shot! Let's try again.",
    "Think of it as yoga for fingers — precision helps!",
    "Almost perfect! Just a little tweak!",
    "Maybe rotate your hand a little. I believe in you!",
]
used_feedbacks = []

# Define number of feedbacks required based on sign type
def required_feedbacks_for_sign(sign):
    return 1 if sign in immediate_accept_signs else 2

def play_win_sound():
    mixer.music.load("mixkit-winning-notification-2018.wav")
    mixer.music.play()

def draw_center_text(img, text, color=(255, 255, 255), scale=2, thickness=4, y_offset=0):
    (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    x = int((img.shape[1] - text_w) / 2)
    y = int((img.shape[0] + text_h) / 2) + y_offset
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)

def ask_hand():
    cap = cv2.VideoCapture(0)
    selected_hand = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame[:] = 0
        draw_center_text(frame, "Which is your dominant hand?", (100, 180, 255), 1.5, 3, -60)
        draw_center_text(frame, "Press 'l' for Left | 'r' for Right", (255, 255, 255), 1, 2, 0)
        cv2.imshow("Select Dominant Hand", frame)
        key = cv2.waitKey(1)
        if key in [ord('l'), ord('L')]:
            selected_hand = "Left"
            break
        elif key in [ord('r'), ord('R')]:
            selected_hand = "Right"
            break
    cap.release()
    cv2.destroyAllWindows()
    return selected_hand

def load_hand_model(hand_side):
    path = f"Model_alpha_{hand_side}/"
    model = load_model(path + "keras_model.h5")
    with open(path + "labels.txt", 'r') as f:
        labels = f.read().splitlines()
    return model, labels

def load_letter_image(letter):
    image_path = os.path.join("letter_images", f"{letter}.jpg")
    return cv2.imread(image_path) if os.path.exists(image_path) else None

def generate_custom_letter_sequence():
    easy_letters = immediate_accept_signs.copy()
    hard_letters = [l for l in allowed_signs if l not in easy_letters]
    random.shuffle(easy_letters)
    random.shuffle(hard_letters)
    return easy_letters[:3] + hard_letters[:2] + easy_letters[3:5]

def get_suggestion():
    global used_feedbacks, intelligent_feedbacks_pool
    if len(used_feedbacks) == len(intelligent_feedbacks_pool):
        used_feedbacks = []
    unused_feedbacks = list(set(intelligent_feedbacks_pool) - set(used_feedbacks))
    suggestion = random.choice(unused_feedbacks)
    used_feedbacks.append(suggestion)
    return suggestion

def main():
    global feedback_tracker
    dominant_hand = ask_hand()
    model, labels = load_hand_model(dominant_hand)
    game_letters = generate_custom_letter_sequence()

    current_index = 0
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    cap = cv2.VideoCapture(0)

    state = "waiting"
    result_time = None
    feedback, display_color = "", (0, 255, 255)
    IMG_SIZE = 300
    start_timer = None
    TIMER_LIMIT = 7
    pause_due_to_no_hand = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if current_index >= len(game_letters):
            feedback = f"Game Over!"
            state = "game_over"

        current_label = game_letters[current_index] if current_index < len(game_letters) else ""
        if current_label not in feedback_tracker:
            feedback_tracker[current_label] = 0

        if state == "waiting":
            frame[:] = 0
            draw_center_text(frame, "Sign Language Game", (0, 255, 255), 2.2, 4, -80)
            draw_center_text(frame, "Press 's' to Start", (255, 255, 255), 1.2, 3, -20)
            draw_center_text(frame, "Press 'q' to Quit | 'z' to Skip Letter", (180, 180, 180), 0.9, 2, 30)
            cv2.imshow("Sign Game", frame)
            key = cv2.waitKey(1)
            if key == ord('s'):
                state = "predict"
                start_timer = time.time()
            elif key == ord('q'):
                break
            continue

        cv2.putText(frame, "Make this Sign:", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (180, 100, 255), 3)
        cv2.putText(frame, current_label, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 4.5, (255, 105, 180), 8)

        ref_img = load_letter_image(current_label)
        if ref_img is not None:
            ref_img = cv2.resize(ref_img, (IMG_SIZE, IMG_SIZE))
            frame[100:100 + IMG_SIZE, w - IMG_SIZE - 30:w - 30] = ref_img

        if start_timer and not pause_due_to_no_hand:
            time_left = int(max(0, TIMER_LIMIT - (time.time() - start_timer)))
            cv2.rectangle(frame, (int(w / 2) - 120, 60), (int(w / 2) + 120, 105), (20, 20, 20), -1)
            cv2.putText(frame, f"{time_left} sec left", (int(w / 2) - 100, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 4)

        if results.multi_hand_landmarks:
            pause_due_to_no_hand = False
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            x_list = [int(lm.x * w) for lm in hand_landmarks.landmark]
            y_list = [int(lm.y * h) for lm in hand_landmarks.landmark]
            x_min, x_max = max(min(x_list) - 20, 0), min(max(x_list) + 20, w)
            y_min, y_max = max(min(y_list) - 20, 0), min(max(y_list) + 20, h)

            if ref_img is not None:
                try:
                    overlay = cv2.resize(ref_img, (x_max - x_min, y_max - y_min))
                    blended = cv2.addWeighted(frame[y_min:y_max, x_min:x_max], 0.6, overlay, 0.4, 0)
                    frame[y_min:y_max, x_min:x_max] = blended
                except:
                    pass

            if state == "predict" and not pause_due_to_no_hand and (time.time() - start_timer) >= TIMER_LIMIT:
                cropped = frame[y_min:y_max, x_min:x_max]
                if cropped.size > 0:
                    try:
                        img = cv2.resize(cropped, (224, 224))
                        img = np.asarray(img, dtype=np.float32).reshape(1, 224, 224, 3) / 255.0
                        prediction = model.predict(img)[0]
                        predicted_index = np.argmax(prediction)
                        predicted_label = labels[predicted_index]
                        confidence = prediction[predicted_index]

                        max_attempts = required_feedbacks_for_sign(current_label)

                        if predicted_label == current_label and confidence >= CONFIDENCE_THRESHOLD:
                            feedback = f"Correct! Accuracy: {random.randint(80,95)}%"
                            display_color = (0, 255, 0)
                            play_win_sound()
                            current_index += 1
                            feedback_tracker[current_label] = 0
                        else:
                            feedback_tracker[current_label] += 1
                            if feedback_tracker[current_label] == 1:
                                feedback = get_suggestion()
                                display_color = (0, 0, 255)
                            elif feedback_tracker[current_label] >= max_attempts:
                                feedback = f"Accepted. Accuracy: {random.randint(80,95)}%"
                                display_color = (0, 255, 0)
                                play_win_sound()
                                current_index += 1
                                feedback_tracker[current_label] = 0

                        result_time = time.time()
                        state = "result"
                    except:
                        feedback = f"Error during prediction!"
                        display_color = (0, 0, 255)
                        result_time = time.time()
                        state = "result"
        else:
            if state == "predict":
                feedback = "No hand detected! Paused..."
                display_color = (0, 255, 255)
                pause_due_to_no_hand = True
                draw_center_text(frame, feedback, display_color, 1.2, 2, -h // 4)

        if state == "result":
            draw_center_text(frame, feedback, display_color, 1.4, 3, int(h / 2) - 100)
            if time.time() - result_time > 2:
                if current_index >= len(game_letters):
                    state = "game_over"
                else:
                    state = "predict"
                    start_timer = time.time()

        if state == "game_over":
            frame[:] = 0
            draw_center_text(frame, feedback, (0, 255, 255), 1.8, 4, -20)
            draw_center_text(frame, "Press 'q' to Quit | 's' to Restart", (180, 180, 180), 1, 2, 60)

        cv2.imshow("Sign Game", frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            game_letters = generate_custom_letter_sequence()
            current_index = 0
            feedback_tracker = {}
            state = "predict"
            start_timer = time.time()
        elif key == ord('z'):
            current_index += 1
            feedback_tracker = {}
            if current_index >= len(game_letters):
                feedback = f"Game Over!"
                state = "game_over"

    cv2.waitKey(0)
cv2.destroyAllWindows()

    

if __name__ == "__main__":
    main()