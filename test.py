import requests
import base64

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/yangy50/garbage-classification"
API_TOKEN = "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"   # replace with your Hugging Face access token
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def classify_waste(image_path):
    # read and encode image in base64
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    data = {"inputs": base64.b64encode(img_bytes).decode("utf-8")}

    # send request
    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return None

    result = response.json()

    # pick highest score
    best = max(result, key=lambda x: x['score'])
    print(f"✅ Prediction: {best['label']} ({best['score']:.2%})")
    return best

# Example usage
if __name__ == "__main__":
    classify_waste(input("Enter path of the waste"))  # replace with your image path
