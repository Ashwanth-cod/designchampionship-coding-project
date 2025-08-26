import json

# ===== Load your JSON waste data =====
with open("waste_data.json", "r") as f:
    WASTE_DATA = json.load(f)


class WasteSorterApp(QMainWindow):
    # ... keep everything else the same ...

    def search_item(self):
        query = self.input_box.text().strip().lower()
        self.result_layout.setParent(None)  # clear old results

        # fresh scroll area layout
        scroll_content = QWidget()
        self.result_layout = QVBoxLayout(scroll_content)
        self.scroll_area.setWidget(scroll_content)

        if not query:
            self.result_layout.addWidget(QLabel("❌ Please enter an item."))
            self.scroll_area.show()
            return

        # Search in data
        found_items = []
        for item in WASTE_DATA:
            if query in item["name"].lower() or any(query in assoc.lower() for assoc in item["associates"]):
                found_items.append(item)

        if not found_items:
            self.result_layout.addWidget(QLabel("⚠️ No match found. Try another keyword."))
        else:
            for item in found_items:
                self.display_item(item)

        self.scroll_area.show()

    def display_item(self, item):
        """ Nicely format & display one item inside the phone screen """
        block = QFrame()
        block.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-radius: 14px;
                padding: 12px;
                margin-bottom: 14px;
            }
            QLabel { color: white; font-size: 14px; }
        """)
        layout = QVBoxLayout(block)

        name = QLabel(f"🔹 {item['name']} ({item['type']})")
        name.setStyleSheet("font-size: 16px; font-weight: bold; color: #00e676;")
        layout.addWidget(name)

        layout.addWidget(QLabel(f"🗑 Disposal: {item['disposal']}"))
        layout.addWidget(QLabel(f"☣️ Toxicity: {item['toxicity']}"))
        layout.addWidget(QLabel(f"♻️ 3R Tip: {item['three_r_tip']}"))
        layout.addWidget(QLabel(f"✨ Alternatives: {', '.join(item['alternatives'])}"))
        layout.addWidget(QLabel(f"👀 Associates: {', '.join(item['associates'])}"))
        layout.addWidget(QLabel(f"⚠️ Handling: {item['handling_precautions']}"))

        self.result_layout.addWidget(block)
