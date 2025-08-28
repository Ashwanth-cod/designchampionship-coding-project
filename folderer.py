import os

# Root dataset folder
root_dir = "waste_dataset"

# Classes
classes = [
    "fruits_and_vegetables",
    "packed_foods",
    "plastic_utensils",
    "metal_utensils",
    "electronics",
    "papers",
    "books",
    "cardboards",
    "clothings",
    "furnitures",
    "plastic_covers",
    "stationaries",
    "bio_wastes",
    "ceramic"
]

# YOLOv8 expected structure
subfolders = ["images/train", "labels/train"]

for cls in classes:
    for sub in subfolders:
        path = os.path.join(root_dir, cls, sub)
        os.makedirs(path, exist_ok=True)
        print(f"Created: {path}")

print("\n✅ Dataset directories created successfully!")
