import os
import cv2
import albumentations as A
from tqdm import tqdm

# Input and output folders
INPUT_DIR = "assets/dataset/"   # Your 10 images/class go here
OUTPUT_DIR = "assets/dataset_123" # Augmented dataset

# Define augmentations (you can add more)
transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.2),
    A.Rotate(limit=25, p=0.5),
    A.RandomBrightnessContrast(p=0.5),
    A.Blur(blur_limit=3, p=0.3),
    A.RandomResizedCrop(size=(224, 224), scale=(0.8, 1.0), p=0.5),
])

# Loop through all classes
for class_name in os.listdir(INPUT_DIR):
    class_input_path = os.path.join(INPUT_DIR, class_name)
    class_output_path = os.path.join(OUTPUT_DIR, class_name)
    os.makedirs(class_output_path, exist_ok=True)

    images = [f for f in os.listdir(class_input_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    for img_name in tqdm(images, desc=f"Augmenting {class_name}"):
        img_path = os.path.join(class_input_path, img_name)
        image = cv2.imread(img_path)

        # Generate 50 augmentations per image
        for i in range(50):
            augmented = transform(image=image)
            aug_img = augmented["image"]
            out_name = f"{os.path.splitext(img_name)[0]}_aug{i}.jpg"
            cv2.imwrite(os.path.join(class_output_path, out_name), aug_img)
