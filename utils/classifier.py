import json
import os

class MaterialClassifier:
    def __init__(self, json_path: str):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)["materials"]

    def classify_text(self, text: str):
        text = text.lower().strip()
        for material in self.data:
            for alias in material["aliases"]:
                if alias in text:
                    return {
                        "name": material["name"],
                        "type": material["type"],
                        "eco_tip": material["eco_tip"],
                        "notes": material["notes"]
                    }
        return {
            "name": "Unknown Material",
            "type": "not_found",
            "eco_tip": "Material not found in the database.",
            "notes": "Consider updating the materials.json file."
        }
