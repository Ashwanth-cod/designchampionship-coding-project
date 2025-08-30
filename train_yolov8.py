from ultralytics import YOLO

# Load a lightweight classification model
model = YOLO('yolov8n-cls.pt')  # pretrained

# Train the model
model.train(
    data='assets/dataset',       # path to the folder with class subfolders
    epochs=50,            # low for small dataset
    imgsz=224,            # image size
    batch=4,              # adjust for your GPU/CPU
    name='waste_classifier',
    split=0.2             # 20% of images will be used for validation automatically
)
