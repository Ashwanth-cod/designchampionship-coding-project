import json

def get_all_names_and_associates():
    with open("waste_items.json", "r") as f:
        waste_items = json.load(f)

    all_names = []

    for item in waste_items:
        all_names.append(item["name"])           # full name

    # Save names to file
    with open("cache/waste_names.txt", "w") as f_names:
        for name in all_names:
            f_names.write(name + "\n")


    print("✅ Names and associates saved to files.")
    return all_names

names = get_all_names_and_associates()
