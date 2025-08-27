from transformers import pipeline
from PIL import Image

# Hugging Face object detection pipeline (online)
# You can also provide your HF token if you hit rate limits
detector = pipeline(
    "object-detection", 
    model="facebook/detr-resnet-50",
    # token="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"  # optional: your Hugging Face token
)

# Load your image
image_path = "assets/newspaper.jpg"  # Replace with your image path
image = Image.open(image_path).convert("RGB")

# Detect objects
results = detector(image)

# Print detected objects
if len(results) == 0:
    print("No objects detected.")
else:
    print("Detected objects:")
    for obj in results:
        print(f"{obj['label']} ({obj['score']:.2f})")
