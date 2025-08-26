import json

def get_all_associates():
    with open("waste_items.json", "r") as f:
        waste_items = json.load(f)

    all_associates = []
    for item in waste_items:
        all_associates.extend(item["associates"])  # add all associates

    # Print them nicely
    print("📌 All Associates:")
    for assoc in all_associates:
        file1 = open("waste_classes.txt", "a+")
        file1.write(assoc + "\n")
    return all_associates

classes = get_all_associates()
