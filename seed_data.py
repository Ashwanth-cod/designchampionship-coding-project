# seed_data.py

from db import get_db

def seed_categories():
    db = get_db()
    categories = db["categories"]

    # Clear existing categories
    categories.delete_many({})

    # Insert base categories
    categories.insert_many([
        {
            "name": "compostable",
            "keywords": ["banana", "peel", "apple core", "food", "leaves", "vegetable", "fruit"],
            "tips": "Add to your compost pile or bin."
        },
        {
            "name": "recyclable",
            "keywords": ["bottle", "plastic", "can", "glass", "cardboard", "paper", "tin"],
            "tips": "Rinse and place in the recycling bin."
        },
        {
            "name": "trash",
            "keywords": ["styrofoam", "chip bag", "diaper", "wrapper", "ceramics"],
            "tips": "Dispose responsibly in a landfill bin."
        }
    ])

    print("✅ Categories seeded into MongoDB")

if __name__ == "__main__":
    seed_categories()
