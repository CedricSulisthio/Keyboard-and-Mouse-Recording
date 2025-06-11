# Keyboard and Mouse Recording (2)

import tkinter as tk
import pyautogui
import subprocess
import json
import time
import threading
from pynput import mouse, keyboard  

actions = []
recording = False
mouse_holding = False  

def launch_paint():
    subprocess.Popen('mspaint')
    register_action('launch_paint')
    time.sleep(2)  # Ensure Paint has enough time to open

def launch_notepad():
    subprocess.Popen(['notepad.exe'])
    register_action('launch_notepad')

def capture_actions():
    global actions, recording, mouse_holding
    actions = []
    recording = True
    mouse_holding = False
    pyautogui.PAUSE = 0.005  

    def refresh_gui_text(text):
        instructions_label.config(text=text)

    refresh_gui_text("Capturing... Move the pointer, click, and type. Press Esc to end.")

    def track_move(x, y):
        global recording, mouse_holding
        if recording:
            actions.append({'type': 'move', 'x': x, 'y': y, 'time': time.time(), 'holding': mouse_holding})

    def track_click(x, y, button, pressed):
        global recording, mouse_holding
        if recording:
            if pressed:
                actions.append({'type': 'mouse_down', 'x': x, 'y': y, 'button': str(button), 'time': time.time()})
                mouse_holding = True
            else:
                actions.append({'type': 'mouse_up', 'x': x, 'y': y, 'button': str(button), 'time': time.time()})
                mouse_holding = False

    def track_keypress(key):
        global recording
        if key == keyboard.Key.esc:
            recording = False
            return False
        try:
            key_value = key.char if hasattr(key, 'char') else str(key)
            actions.append({'type': 'keypress', 'key': key_value, 'time': time.time()})
        except AttributeError:
            pass  # Ignore unknown keys

    mouse_listener = mouse.Listener(on_move=track_move, on_click=track_click)
    keyboard_listener = keyboard.Listener(on_press=track_keypress)

    mouse_listener.start()
    keyboard_listener.start()

    while recording:
        time.sleep(0.01)

    with open('recorded_actions.json', 'w') as f:
        json.dump(actions, f)

    refresh_gui_text("Capturing ended. Actions saved as recorded_actions.json.")

def register_action(action_type):
    actions.append({'type': action_type, 'time': time.time()})

def execute_actions():
    try:
        with open('recorded_actions.json', 'r') as f:
            actions = json.load(f)

        def refresh_gui_text(text):
            instructions_label.config(text=text)

        refresh_gui_text("Executing...")

        last_time = None

        for action in actions:
            if last_time:
                delay = max(0, action['time'] - last_time)
                time.sleep(delay)  # Maintain natural timing
            last_time = action['time']

            if action['type'] == 'launch_paint':
                launch_paint()
                time.sleep(2)  # Give extra time for Paint to open
            elif action['type'] == 'launch_notepad':
                launch_notepad()
                time.sleep(1)
            elif action['type'] == 'mouse_down':
                pyautogui.moveTo(action['x'], action['y'], duration=0.02)
                pyautogui.mouseDown()
            elif action['type'] == 'move':
                pyautogui.moveTo(action['x'], action['y'], duration=0.02)
                if action['holding']:
                    pyautogui.mouseDown()
            elif action['type'] == 'mouse_up':
                pyautogui.mouseUp()
            elif action['type'] == 'keypress':
                key = action['key']

                # Handle special keys correctly
                special_keys = {
                    'Key.space': 'space',
                    'Key.enter': 'enter',
                    'Key.backspace': 'backspace',
                    'Key.delete': 'delete',
                    'Key.tab': 'tab'
                }

                if key in special_keys:
                    pyautogui.press(special_keys[key])
                elif len(key) == 1:
                    pyautogui.write(key, interval=0.05)

        refresh_gui_text("Execution completed.")

    except Exception as e:
        instructions_label.config(text="Error: Unable to load actions.")
        print(f"Error: {e}")

def initiate_recording():
    threading.Thread(target=capture_actions, daemon=True).start()

def initiate_execution():
    threading.Thread(target=execute_actions, daemon=True).start()

def build_gui():
    global root, instructions_label
    
    root = tk.Tk()
    root.title("Activity Logger")
    root.resizable(False, False)
    root.geometry("400x400")

    instructions_label = tk.Label(root, text="Select an action.", font=("Arial", 12))
    instructions_label.pack(pady=20)

    launch_paint_button = tk.Button(root, text="Launch Paint", command=launch_paint)
    launch_paint_button.pack(pady=10)
    
    launch_notepad_button = tk.Button(root, text="Launch Notepad", command=launch_notepad)
    launch_notepad_button.pack(pady=10)

    capture_button = tk.Button(root, text="Start Capturing", command=initiate_recording)
    capture_button.pack(pady=10)
    
    execute_button = tk.Button(root, text="Run Recorded Actions", command=initiate_execution)
    execute_button.pack(pady=10)

    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=10)

    root.mainloop()

build_gui()