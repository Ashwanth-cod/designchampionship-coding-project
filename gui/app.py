import tkinter as tk
from tkinter import ttk
from utils.classifier import MaterialClassifier
from utils.camera import WebcamClassifier
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "materials.json")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "waste_sorter.pt")

def launch_app():
    root = tk.Tk()
    root.title("Waste Sorter")
    root.state("zoomed")  # Fullscreen
    
    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 16), padding=10)
    style.configure("TButton", font=("Segoe UI", 14), padding=10)

    classifier = MaterialClassifier(DATA_PATH)
    cam_classifier = WebcamClassifier(MODEL_PATH)

    # Layout
    frame = ttk.Frame(root, padding=30)
    frame.pack(expand=True, fill="both")

    result_label = ttk.Label(frame, text="Welcome to Waste Sorter", font=("Segoe UI", 20, "bold"))
    result_label.pack(pady=20)

    # Text Input
    text_entry = ttk.Entry(frame, font=("Segoe UI", 14), width=50)
    text_entry.pack(pady=10)

    def classify_text():
        item = text_entry.get()
        res = classifier.classify_text(item)
        result_label.config(
            text=f"{res['name']} → {res['type'].upper()}\nTip: {res['eco_tip']}\nNotes: {res['notes']}"
        )

    # Camera Input
    def classify_camera():
        cat, msg = cam_classifier.capture_and_classify()
        result_label.config(text=f"Camera result: {cat.upper()} - {msg}")

    text_button = ttk.Button(frame, text="Classify Text", command=classify_text)
    text_button.pack(pady=10)

    cam_button = ttk.Button(frame, text="Classify via Camera", command=classify_camera)
    cam_button.pack(pady=10)

    root.mainloop()
