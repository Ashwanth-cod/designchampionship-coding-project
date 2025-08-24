import json
from pymongo import MongoClient

# Connect to MongoDB (make sure MongoDB is running locally or on your server)
client = MongoClient("mongodb://localhost:27017/")

# Choose database and collection
db = client["waste_sorter"]
collection = db["items"]

# Load JSON file
with open("wastes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Insert into MongoDB
collection.insert_many(data)

print("✅ Dataset inserted into MongoDB under waste_sorter.items")
