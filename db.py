import json
import os
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "waste_management"
COLLECTION_NAME = "items"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def load_items_from_json(file_path="waste_dataset.json"):
    """Load dataset from JSON file into MongoDB (only if empty)."""
    if collection.count_documents({}) == 0:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                collection.insert_many(data)
                print(f"[INFO] Inserted {len(data)} items into MongoDB.")
        else:
            print(f"[WARNING] JSON file {file_path} not found.")
    else:
        print("[INFO] MongoDB already contains data.")


def add_item(item):
    """Add a new item to the database."""
    collection.insert_one(item)


def search_item(query):
    """Search item by name or associate keywords."""
    return collection.find_one({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"associates": {"$regex": query, "$options": "i"}}
        ]
    })


def get_all_items():
    """Return all items in the database."""
    return list(collection.find({}))


def export_to_json(file_path="exported_items.json"):
    """Export database items to JSON file."""
    items = get_all_items()
    for item in items:
        item["_id"] = str(item["_id"])  # make MongoDB ObjectId serializable
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Exported {len(items)} items to {file_path}.")
