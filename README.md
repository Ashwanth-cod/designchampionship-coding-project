# Waste Sorter (Tkinter + Turtle + Ultralytics)


Offline desktop app to classify waste from **camera input** (Ultralytics YOLO
classifier) or **text input** (keyword-based). Shows an eco-friendly disposal
**tip** and a Turtle-drawn symbol for the predicted category
(*recycle/compost/trash*).


## Quick start
```bash
python -m venv .venv && source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```


## Model
Train a 3-class YOLO **classification** model (labels: `recycle`, `compost`,
`trash`) and place weights at `models/waste_sorter.pt`. Until then, the app
handles the missing model gracefully and disables camera classification.


Example (Ultralytics):
```bash
yolo classify train data=models/dataset.yaml model=yolov8n-cls.pt epochs=20 imgsz=224
# After training, copy best weights to:
cp runs/classify/train*/weights/best.pt models/waste_sorter.pt
```


## Notes
- Works fully **offline**. No file uploads; camera or text only.
- Tkinter for GUI; Turtle for playful, visual feedback.
- If your webcam index is not 0, change it in `utils/camera.py`.

