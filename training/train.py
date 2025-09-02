from ultralytics import YOLO
import shutil
import os

# Load model
model = YOLO("yolov8n-cls.pt")

dataset_path = "../assets/dataset"
train_path = os.path.join(dataset_path, "train")

# Detect number of classes
classes = [d for d in os.listdir(train_path) if os.path.isdir(os.path.join(train_path, d))]
num_classes = len(classes)
print(f"✅ Detected {num_classes} classes: {classes}")

try:
    model.train(
        data=train_path,     # ✅ explicitly point to train folder
        epochs=50,
        imgsz=224,
        batch=4,
        name="waste_classifier",
        split=0.0            # ✅ disables validation safely
    )

    # Only delete dataset if training succeeds
    if os.path.exists(dataset_path):
        shutil.rmtree(dataset_path)
        print(f"✅ Dataset deleted: {dataset_path}")

except Exception as e:
    print(f"❌ Training failed: {e}")
