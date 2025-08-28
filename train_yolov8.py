# train_yolov8.py
from ultralytics import YOLO

# 1️⃣ Load a YOLOv8 model (choose 'yolov8n.pt' for nano, lightweight and fast)
model = YOLO("yolov8n.pt")  

# 2️⃣ Train the model
model.train(
    data="dataset.yaml",  # path to your dataset YAML
    imgsz=640,            # image size
    epochs=100,           # small dataset: 100 epochs is reasonable
    batch=2,              # small batch size for small dataset
    workers=2,            # number of CPU threads for data loading
    patience=20,          # early stopping if no improvement
    optimizer="SGD",      # SGD is fine for small datasets
    lr0=0.01,             # initial learning rate
    augment=True,         # enable augmentation to avoid overfitting
    cache=True            # cache images in RAM for faster training
)

# 3️⃣ Save trained model
model.export(format="onnx")  # export to ONNX (optional)
