from difflib import get_close_matches
from db import search_item, get_all_items


def classify_item(user_input):
    """Classify a waste item using fuzzy matching."""
    all_items = get_all_items()
    names = [item["name"] for item in all_items]

    # Try direct DB search first
    db_result = search_item(user_input)
    if db_result:
        return db_result, []

    # Fuzzy match if not found directly
    matches = get_close_matches(user_input, names, n=3, cutoff=0.4)
    similar_items = []
    for match in matches:
        for item in all_items:
            if item["name"].lower() == match.lower():
                similar_items.append(item)

    return None, similar_items
