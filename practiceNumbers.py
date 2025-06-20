import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
import random
import time
import os
from pygame import mixer

# ✅ Audio init
mixer.init()

# ✅ Configuration
allowed_signs = [str(i) for i in range(0, 11) if i != 9]
immediate_accept_signs = ['0']
CONFIDENCE_THRESHOLD = 0.70

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

feedback_tracker = {}
used_feedbacks = {}
intelligent_feedbacks_pool = [
    "Tip: Ensure your background is clutter‑free!",
    "Try improving the lighting around your hand.",
    "Keep your whole hand in the frame!",
    "Center your hand — almost there!",
    "Try a brighter spot!",
    "Stretch your fingers clearly!",
    "Focus! Looks close!",
    " Breathe & try again!",
    " Move your hand slightly closer.",
    " Clean up your background.",
    " Even AI needs clarity!",
    " Precision matters—slow down.",
    " Almost perfect!",
    " Rotate your hand just a bit.",
]

def required_feedbacks_for_sign(sign: str) -> int:
    return 1 if sign in immediate_accept_signs else 2

def play_win_sound():
    mixer.music.load("mixkit-winning-notification-2018.wav")
    mixer.music.play()

def draw_text_with_panel(img, text, color=(255, 255, 255), scale=1.5, thickness=3, y_off=0):
    (w_, h_), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_COMPLEX, scale, thickness)
    x = (img.shape[1] - w_) // 2
    y = (img.shape[0] + h_) // 2 + y_off

    overlay = img.copy()
    cv2.rectangle(overlay, (x - 20, y - h_ - 20), (x + w_ + 20, y + 20), (50, 50, 50), -1)
    alpha = 0.6
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    cv2.putText(img, text, (x + 2, y + 2), cv2.FONT_HERSHEY_COMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_COMPLEX, scale, color, thickness, cv2.LINE_AA)

def ask_hand():
    cap = cv2.VideoCapture(0)
    sel = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame[:] = (20, 20, 20)
        draw_text_with_panel(frame, "Which is your dominant hand?", (100, 180, 255), 1.5, 3, -60)
        draw_text_with_panel(frame, "Press 'l' for Left | 'r' for Right", (255, 255, 255), 1, 2, 0)
        cv2.imshow("Select Dominant Hand", frame)
        key = cv2.waitKey(1)
        if key in [ord('l'), ord('L')]:
            sel = "Left"
            break
        elif key in [ord('r'), ord('R')]:
            sel = "Right"
            break
    cap.release()
    cv2.destroyAllWindows()
    return sel

def load_hand_model(sign_type):
    path = f"Model_number_{sign_type}/"
    model = load_model(os.path.join(path, "keras_model.h5"))
    with open(os.path.join(path, "labels.txt")) as f:
        labels = f.read().splitlines()
    return model, labels

def load_target_image(target):
    path = os.path.join("number_images", f"{target}.jpg")
    if os.path.exists(path):
        return cv2.imread(path)
    return None

def generate_custom_sequence():
    seq = allowed_signs.copy()
    random.shuffle(seq)
    return seq

def get_suggestion(sign):
    used_feedbacks.setdefault(sign, [])
    available = [f for f in intelligent_feedbacks_pool if f not in used_feedbacks[sign]]
    if not available:
        used_feedbacks[sign].clear()
        available = intelligent_feedbacks_pool
    pick = random.choice(available)
    used_feedbacks[sign].append(pick)
    return pick

def main():
    dominant_hand = ask_hand()
    model, labels = load_hand_model(dominant_hand)
    sequence = generate_custom_sequence()
    current = 0

    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    state = "waiting"
    start_t = result_t = None
    feedback = ""
    color = (0, 255, 255)
    pause_no_hand = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(img_rgb)

        if current >= len(sequence):
            feedback = "Game Over!"
            state = "game_over"

        if current % 5 == 0 and current != 0 and state not in ["pause", "game_over"]:
            state = "pause"

        target = sequence[current] if current < len(sequence) else ""
        feedback_tracker.setdefault(target, 0)

        draw_text_with_panel(frame, "SignLingo", (255, 255, 255), 1.5, 2, -h // 2 + 30)
        cv2.putText(frame, "Press 's' to Start | 'q' to Quit | 'z' to Skip", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 4)

        if state == "waiting":
            draw_text_with_panel(frame, "Press 's' to begin", (0, 200, 200), 1.2, 2, 0)
            cv2.imshow("SignLingo", frame)
            key = cv2.waitKey(1)
            if key == ord('s'):
                state = "predict"
                start_t = time.time()
            elif key == ord('q'):
                break
            continue

        if state == "pause":
            draw_text_with_panel(frame, "Break Time!", (255, 255, 0), 1.5, 2, -40)
            draw_text_with_panel(frame, "Press 'c' to Continue or 'q' to Quit", (255, 255, 255), 1, 2, 20)
            cv2.imshow("SignLingo", frame)
            key = cv2.waitKey(0)
            if key == ord('q'):
                break
            elif key == ord('c'):
                state = "predict"
                start_t = time.time()
                continue

        cv2.putText(frame, f"Show number: {target}", (10, 80), cv2.FONT_HERSHEY_COMPLEX, 1.8, (100, 200, 255), 4)

        img = load_target_image(target)
        if img is not None:
            img_size = 250
            padding = 15
            img = cv2.resize(img, (img_size, img_size))

            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            img = cv2.filter2D(img, -1, kernel)

            x1, y1 = w - img_size - 2 * padding, 10
            x2, y2 = w - padding, 10 + img_size + 2 * padding

            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (40, 40, 40), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

            frame[y1 + padding: y1 + padding + img_size, x1 + padding: x1 + padding + img_size] = img

        if state == "predict" and not pause_no_hand and start_t:
            elapsed = time.time() - start_t
            bar_len = int(min(elapsed / 7.0, 1.0) * (w - 20))
            cv2.rectangle(frame, (10, h - 40), (10 + bar_len, h - 30), (0, 255, 0), -1)

        predicted_label = ""
        confidence = 0

        if res.multi_hand_landmarks:
            pause_no_hand = False
            hl = res.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)

            box_x = [int(lm.x * w) for lm in hl.landmark]
            box_y = [int(lm.y * h) for lm in hl.landmark]
            x1, x2 = max(min(box_x) - 20, 0), min(max(box_x) + 20, w)
            y1, y2 = max(min(box_y) - 20, 0), min(max(box_y) + 20, h)
            crop = frame[y1:y2, x1:x2]

            if crop.size > 0:
                img = cv2.resize(crop, (224, 224))
                img = img.astype(np.float32) / 255.0
                pred = model.predict(img[np.newaxis, ...])[0]
                idx = np.argmax(pred)
                predicted_label = labels[idx]
                confidence = pred[idx]

            cv2.putText(frame, f"Live Match: {predicted_label} ({int(confidence * 100)}%)",
                        (10, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 10)

            if state == "predict" and time.time() - start_t >= 7:
                max_fb = required_feedbacks_for_sign(target)
                if predicted_label == target and confidence >= CONFIDENCE_THRESHOLD:
                    feedback = f"Correct! Accuracy: {int(confidence * 100)}%"
                    color = (0, 255, 128)
                    play_win_sound()
                    current += 1
                    feedback_tracker[target] = 0
                else:
                    feedback_tracker[target] += 1
                    if feedback_tracker[target] < max_fb:
                        feedback = get_suggestion(target)
                        color = (255, 85, 85)
                    else:
                        feedback = f"Accepted! Accuracy: {int(confidence * 100)}%"
                        color = (0, 255, 128)
                        play_win_sound()
                        current += 1
                        feedback_tracker[target] = 0
                result_t = time.time()
                state = "result"
        else:
            if state == "predict":
                feedback = "No hand detected!"
                color = (255, 204, 0)
                pause_no_hand = True

        if state == "result":
            draw_text_with_panel(frame, feedback, color, 1, 3, 0)
            if time.time() - result_t > 2:
                state = "predict"
                start_t = time.time()

        if state == "game_over":
            draw_text_with_panel(frame, feedback, (0, 200, 200), 1.5, 2, 0)
            draw_text_with_panel(frame, "Press 's' to Restart or 'q' to Quit", (200, 200, 200), 1, 3, 40)

        cv2.imshow("SignLingo", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('z'):
            current += 1
            feedback_tracker[target] = 0
        elif key == ord('s') and state == "game_over":
            sequence = generate_custom_sequence()
            current = 0
            feedback_tracker.clear()
            state = "waiting"

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
