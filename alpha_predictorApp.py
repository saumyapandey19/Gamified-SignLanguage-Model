import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
import random
import time
import os
from pygame import mixer

# Streamlit page setup
st.set_page_config(page_title="Sign Language Game", layout="centered")
st.title("🖐️ Sign Language Practice - Alphabet Mode")

# Audio init
mixer.init()

allowed_signs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'K', 'L', 'M', 'O', 'P', 'Q', 'R', 'U', 'V', 'W', 'Y', 'Z']
immediate_accept_signs = ['A']
CONFIDENCE_THRESHOLD = 0.70

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
feedback_tracker = {}
intelligent_feedbacks_pool = [
    "🧠 Tip: Ensure your background is clutter-free!",
    "💡 Try improving the lighting around your hand.",
    "✋ Keep your whole hand inside the frame!",
    "📷 Center your hand — you're almost there!",
    "🌞 Lighting could be better — try a brighter spot!",
    "🖐️ Stretch your fingers clearly. Make it count!",
    "🎯 Focus! It looks close, but not quite right.",
    "💪 Take a deep breath — try the sign again!",
    "😄 You got this! Maybe move your hand slightly closer.",
    "🧼 Hmm... background’s a bit messy — try a clean one!",
    "🤖 Even AI needs a clear shot! Let's try again.",
    "✨ Think of it as yoga for fingers — precision helps!",
    "🚀 Almost perfect! Just a little tweak!",
    "🔍 Maybe rotate your hand a little. I believe in you!",
]
used_feedbacks = []

def play_win_sound():
    mixer.music.load("mixkit-winning-notification-2018.wav")
    mixer.music.play()

def load_hand_model():
    path = f"Model_alpha_Right/"
    model = load_model(path + "keras_model.h5")
    with open(path + "labels.txt", 'r') as f:
        labels = f.read().splitlines()
    return model, labels

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

if st.button("Start Game"):
    model, labels = load_hand_model()
    game_letters = generate_custom_letter_sequence()

    current_index = 0
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    cap = cv2.VideoCapture(0)
    start_timer = time.time()
    TIMER_LIMIT = 7

    feedback = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Webcam not working!")
            break

        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        current_label = game_letters[current_index] if current_index < len(game_letters) else ""
        if current_label not in feedback_tracker:
            feedback_tracker[current_label] = 0

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            x_list = [int(lm.x * frame.shape[1]) for lm in hand_landmarks.landmark]
            y_list = [int(lm.y * frame.shape[0]) for lm in hand_landmarks.landmark]
            x_min, x_max = max(min(x_list) - 20, 0), min(max(x_list) + 20, frame.shape[1])
            y_min, y_max = max(min(y_list) - 20, 0), min(max(y_list) + 20, frame.shape[0])

            cropped = frame[y_min:y_max, x_min:x_max]
            if cropped.size > 0:
                img = cv2.resize(cropped, (224, 224))
                img = np.asarray(img, dtype=np.float32).reshape(1, 224, 224, 3) / 255.0
                prediction = model.predict(img)[0]
                predicted_index = np.argmax(prediction)
                predicted_label = labels[predicted_index]
                confidence = prediction[predicted_index]

                if predicted_label == current_label and confidence >= CONFIDENCE_THRESHOLD:
                    feedback = f"✅ Correct! ({current_label})"
                    play_win_sound()
                    current_index += 1
                else:
                    feedback_tracker[current_label] += 1
                    if feedback_tracker[current_label] >= 2:
                        feedback = f"✅ Accepted. ({current_label})"
                        current_index += 1
                    else:
                        feedback = get_suggestion()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(frame, channels="RGB", use_column_width=True)
        st.write("Make the sign:", f"**{current_label}**")
        st.info(feedback)

        if current_index >= len(game_letters):
            st.success("🎉 Game Over! All signs completed.")
            break

    cap.release()
