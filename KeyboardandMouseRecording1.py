# Keyboard and Mouse Recording (1)

import pyautogui
import keyboard
import time
import json
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# Global variables
recorded_actions = []
recording = False
active_app = None  # 'Paint' or 'Notepad'

def start_recording(app):
    global recording, recorded_actions, active_app
    if recording:
        messagebox.showerror("Error", "Stop and save the current recording first!")
        return
    
    active_app = app
    recorded_actions = []
    recording = True
    
    root.iconify()  # Minimize the window
    start_time = time.time()
    
    if app == "Paint":
        while recording:
            x, y = pyautogui.position()
            if keyboard.is_pressed("left shift"):  # Use shift key to indicate drawing
                recorded_actions.append({"type": "mouse", "x": x, "y": y, "action": "drag", "time": time.time() - start_time})
            else:
                recorded_actions.append({"type": "mouse", "x": x, "y": y, "action": "move", "time": time.time() - start_time})
            time.sleep(0.01)
    elif app == "Notepad":
        def on_press(event):
            if event.event_type == "down" and event.name not in ["shift", "left shift", "right shift", "ctrl", "alt", "tab", "caps lock", "esc", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"]:
                recorded_actions.append({"type": "keyboard", "key": event.name, "time": time.time() - start_time})
        keyboard.hook(on_press)
        while recording:
            time.sleep(0.01)

    root.deiconify()  # Restore the window

def stop_recording():
    global recording
    if not recording:
        messagebox.showerror("Error", "No active recording to stop!")
        return
    recording = False
    keyboard.unhook_all()

def save_recording():
    if not recorded_actions:
        messagebox.showerror("Error", "No recorded actions to save!")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w") as f:
            json.dump(recorded_actions, f, indent=4)

def load_recording():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r") as f:
            return json.load(f)
    return None

def replay_recording():
    actions = load_recording()
    if not actions:
        messagebox.showerror("Error", "No valid recording loaded!")
        return
    
    # Determine if the recording is for Paint or Notepad
    if any(action["type"] == "mouse" for action in actions):
        open_paint()
    elif any(action["type"] == "keyboard" for action in actions):
        open_notepad()
    
    time.sleep(2)  # Ensure the application is open before replaying
    
    start_time = time.time()
    for action in actions:
        elapsed = action["time"] - (time.time() - start_time)
        if elapsed > 0:
            time.sleep(elapsed)
        if action["type"] == "mouse":
            pyautogui.moveTo(action["x"], action["y"], duration=0.01)
            if action["action"] == "drag":
                pyautogui.mouseDown()
            else:
                pyautogui.mouseUp()
        elif action["type"] == "keyboard":
            if action["key"] == "space":
                keyboard.write(" ")
            elif action["key"] == "enter":
                keyboard.press_and_release("enter")
            else:
                keyboard.write(action["key"])

def open_paint():
    subprocess.Popen("mspaint")

def open_notepad():
    subprocess.Popen("notepad")

# GUI setup
root = tk.Tk()
root.title("Mouse and Keyboard Recorder")
root.geometry("400x350")

tk.Button(root, text="Open Paint", command=open_paint).pack(pady=5)
tk.Button(root, text="Open Notepad", command=open_notepad).pack(pady=5)
tk.Button(root, text="Record Paint", command=lambda: threading.Thread(target=start_recording, args=("Paint",), daemon=True).start()).pack(pady=5)
tk.Button(root, text="Record Notepad", command=lambda: threading.Thread(target=start_recording, args=("Notepad",), daemon=True).start()).pack(pady=5)
tk.Button(root, text="Stop Recording", command=stop_recording).pack(pady=5)
tk.Button(root, text="Save Recording", command=save_recording).pack(pady=5)
tk.Button(root, text="Replay Recording", command=replay_recording).pack(pady=5)

tk.Label(root, text="Record mouse in Paint or keyboard in Notepad.").pack(pady=10)

root.mainloop()