import cv2
import ctypes
import threading
import time
import mediapipe as mp

# Define virtual key codes
up_pressed = 0x48
down_pressed = 0x50
right_pressed = 0x4D
left_pressed = 0x4B

# Define ctypes structures and functions for sending keyboard inputs
SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Function to simulate pressing a key
def KeyOn(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Function to simulate releasing a key
def KeyOff(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Define the start_program function
def start_program(video):
    global down_pressed
    left_key_pressed = left_pressed
    right_key_pressed = right_pressed
    up_key_pressed = up_pressed
    down_key_pressed = down_pressed

    tipIds = [4, 8, 12, 16, 20]

    time.sleep(2.0)
    current_key_pressed = set()

    mp_draw = mp.solutions.drawing_utils
    mp_hand = mp.solutions.hands

    with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while True:
            keyPressed = False
            break_pressed = False
            jump_pressed = False
            dunk_pressed = False
            accelerator_pressed = False
            key_count = 0
            key_pressed = 0
            ret, image = video.read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            lmList = []
            text = ''

            if results.multi_hand_landmarks:
                for idx, classification in enumerate(results.multi_handedness):
                    if classification.classification[0].index == idx:
                        label = classification.classification[0].label
                        text = '{}'.format(label)
                    else:
                        label = classification.classification[0].label
                        text = '{}'.format(label)

                for hand_landmark in results.multi_hand_landmarks:
                    myHands = results.multi_hand_landmarks[0]
                    for id, lm in enumerate(myHands.landmark):
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

                if total == 4 and text == "Right":
                    KeyOn(left_key_pressed)
                    break_pressed = True
                    current_key_pressed.add(left_key_pressed)
                    key_pressed = left_key_pressed
                    keyPressed = True
                    key_count = key_count + 1

                elif total == 5 and text == "Left":
                    KeyOn(right_key_pressed)
                    key_pressed = right_key_pressed
                    accelerator_pressed = True
                    keyPressed = True
                    current_key_pressed.add(right_key_pressed)
                    key_count = key_count + 1

                elif total == 1:
                    KeyOn(up_key_pressed)
                    key_pressed = up_key_pressed
                    jump_pressed = True
                    keyPressed = True
                    current_key_pressed.add(up_key_pressed)
                    key_count = key_count + 1

                elif total == 0:
                    KeyOn(down_key_pressed)
                    key_pressed = down_key_pressed
                    down_pressed = True
                    keyPressed = True
                    current_key_pressed.add(down_key_pressed)
                    key_count = key_count + 1

            if not keyPressed and len(current_key_pressed) != 0:
                for key in current_key_pressed:
                    KeyOff(key)
                current_key_pressed = set()

            elif key_count == 1 and len(current_key_pressed) == 2:
                for key in current_key_pressed:
                    if key_pressed != key:
                        KeyOff(key)
                current_key_pressed = set()

            cv2.imshow("AeroNav", image)
            k = cv2.waitKey(1)
            if k == ord('q'):
                break

# Function to start the program in a separate thread
def start_program_thread():
    video = cv2.VideoCapture(0)
    threading.Thread(target=start_program, args=(video,), daemon=True).start()
