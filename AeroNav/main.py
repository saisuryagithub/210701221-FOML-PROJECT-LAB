import cv2
import mediapipe as mp
import time
import numpy as np
import pyautogui
import threading

# Define virtual key codes
up_pressed = 0x48
down_pressed = 0x50
right_pressed = 0x4D
left_pressed = 0x4B

# Define spacebar key press function
def press_spacebar():
    pyautogui.press('space')

# Function to perform click action with a delay
def perform_click():
    time.sleep(1)  # Adjust click delay as needed (1 second delay added here)
    pyautogui.click()

# Function to perform mouse movement
def move_mouse(x, y):
    screenWidth, screenHeight = pyautogui.size()
    pyautogui.moveTo((1-x) * screenWidth, y * screenHeight)  # Invert x-axis

def start_program(video):
    global down_pressed
    left_key_pressed = left_pressed
    right_key_pressed = right_pressed
    up_key_pressed = up_pressed
    down_key_pressed = down_pressed

    tipIds = [4, 8, 12, 16, 20]
    last_movement_time = time.time()
    cursor_stable = False

    time.sleep(2.0)
    current_key_pressed = set()

    mp_draw = mp.solutions.drawing_utils
    mp_hand = mp.solutions.hands

    with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while True:
            keyPressed = False
            key_count = 0
            ret, image = video.read()
            if not ret:
                print("Failed to capture video.")
                break
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            lmList = []

            if results.multi_hand_landmarks:
                for hand_landmark in results.multi_hand_landmarks:
                    for id, lm in enumerate(hand_landmark.landmark):
                        h, w, c = image.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])
                    mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)

                fingers = []

                if len(lmList) != 0:
                    if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                    for id in range(1, 5):
                        if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                    total = fingers.count(1)

                    if total == 4 and len(results.multi_hand_landmarks) == 1:  # Right gesture
                        pyautogui.press('left')  # Simulate pressing the left arrow key
                        current_key_pressed.add(left_key_pressed)
                        keyPressed = True
                        key_count = key_count + 1

                    elif total == 5 and len(results.multi_hand_landmarks) == 1:  # Left gesture
                        pyautogui.press('right')  # Simulate pressing the right arrow key
                        current_key_pressed.add(right_key_pressed)
                        keyPressed = True
                        key_count = key_count + 1

                    elif total == 1 and len(results.multi_hand_landmarks) == 1:  # Up gesture
                        pyautogui.press('up')  # Simulate pressing the up arrow key
                        current_key_pressed.add(up_key_pressed)
                        keyPressed = True
                        key_count = key_count + 1

                    elif total == 0 and len(results.multi_hand_landmarks) == 1:  # Down gesture
                        pyautogui.press('down')  # Simulate pressing the down arrow key
                        current_key_pressed.add(down_key_pressed)
                        keyPressed = True
                        key_count = key_count + 1

                # Perform spacebar key action if both palms are open (all ten fingers extended)
                if len(results.multi_hand_landmarks) == 2:
                    press_spacebar()  # Simulate pressing the spacebar

                # Check for cursor movement
                if len(results.multi_hand_landmarks) == 1:
                    hand = results.multi_hand_landmarks[0]
                    cx, cy = hand.landmark[8].x, hand.landmark[8].y
                    move_mouse(cx, cy)

                    # Check if cursor remains stable for more than 10 seconds
                    if time.time() - last_movement_time > 10:
                        cursor_stable = True
                    else:
                        cursor_stable = False

                # Perform click action if cursor remains stable for more than 10 seconds
                if cursor_stable:
                    perform_click()  # Perform click action if cursor remains stable for 10 seconds
                    last_movement_time = time.time()  # Reset timer

            if not keyPressed and len(current_key_pressed) != 0:
                for key in current_key_pressed:
                    pyautogui.keyUp(chr(key))
                current_key_pressed = set()

            elif key_count == 1 and len(current_key_pressed) == 2:
                for key in current_key_pressed:
                    if key in [left_key_pressed, right_key_pressed, up_key_pressed, down_key_pressed]:
                        pyautogui.keyUp(chr(key))
                current_key_pressed = set()

            cv2.imshow("AeroNav", image)
            k = cv2.waitKey(1)
            if k == ord('q'):
                break

def start_program_thread():
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("Failed to open camera.")
        return
    threading.Thread(target=start_program, args=(video,), daemon=True).start()

# Call the function to start the program
start_program_thread()
