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
        data=train_path,     
        epochs=50,
        imgsz=224,
        batch=4,
        name="waste_classifier",
        split=0.0,           # no validation

        # ✅ Augmentations (filters ON)
        augment=True,        
        fliplr=0.5,          # allow horizontal flip
        flipud=0.1,          # allow vertical flip (light)
        erasing=0.4,         # random erasing
        hsv_h=0.015,         # hue adjustment
        hsv_s=0.7,           # saturation adjustment
        hsv_v=0.4,           # brightness/value adjustment

        # ❌ Disabled augmentations (NO crops, scale, rotation)
        scale=0.0,           
        degrees=0.0,         
        shear=0.0,           
        perspective=0.0      
    )

    # Optionally delete dataset after training
    if os.path.exists(dataset_path):
        shutil.rmtree(dataset_path)
        print(f"✅ Dataset deleted: {dataset_path}")

except Exception as e:
    print(f"❌ Training failed: {e}")
