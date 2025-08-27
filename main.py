import sys
import requests
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QListWidget, QScrollArea, QFileDialog
)
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt
import json
import io

HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/facebook/detr-resnet-50"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

YOLO_TO_JSON_MAPPING = {
    "cup": "Plastic Cup",
    "bottle": "Water Bottle",
    "can": "Aluminum Can",
    "tin can": "Tin Can",
    "battery": "Battery AA",
    "food": "Food Waste",
    "box": "Cereal Box",
    "newspaper": "Newspaper",
    "plastic bag": "Plastic Bag",
    "paper": "Notebook",
    "glass": "Glass Bottle",
    "plate": "Ceramic Mug",
    "fork": "Plastic Fork",
    "spoon": "Plastic Spoon",
    "knife": "Plastic Knife",
    "toy": "Plastic Toy",
    "straw": "Plastic Straw",
    "milk carton": "Milk Carton",
    "laptop": "Laptop",
    "phone": "Mobile Phone",
    "earphones": "Earphones",
    "charger": "Charger Cable",
    "keyboard": "Keyboard",
    "mouse": "Computer Mouse",
    "remote": "TV Remote",
    "refrigerator": "Refrigerator",
    "lamp": "LED Bulb",
    "light bulb": "Light Bulb (Incandescent)",
    "chair": "Plastic Chair",
    "table": "Plastic Table",
    "soap dish": "Plastic Soap Dish",
    "mug": "Ceramic Mug",
    "jar": "Glass Bottle"
}


def detect_objects_hf(image_path):
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    response = requests.post(API_URL, headers=HEADERS, files={"file": img_bytes})
    if response.status_code != 200:
        return []
    return response.json()


class WasteSorterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("♻️ Waste Sorter")
        self.showMaximized()

        # Background gradient
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#0b0b0b"))
        gradient.setColorAt(1, QColor("#003300"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        # Fonts
        self.font_large = QFont("Arial", 28, QFont.Bold)
        self.font_mid = QFont("Arial", 16)
        self.font_res = QFont("Arial", 24)

        # Load JSON data
        with open("waste_items.json", "r") as f:
            self.waste_data = json.load(f)

        # Central widget layout
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        # ===== Left Panel =====
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        title = QLabel("♻️ Waste Sorter")
        title.setFont(self.font_large)
        title.setStyleSheet("color: white;")
        left_layout.addWidget(title)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search waste item...")
        self.search_bar.setFont(self.font_mid)
        self.search_bar.setStyleSheet("""
            QLineEdit {background: #1e1e1e; border-radius: 12px; padding: 12px; color: white;}
            QLineEdit:focus {border: 2px solid #00e676;}
        """)
        self.search_bar.textChanged.connect(self.show_suggestions)
        left_layout.addWidget(self.search_bar)

        self.suggestion_list = QListWidget()
        self.suggestion_list.setStyleSheet("""
            QListWidget {background: #1e1e1e; color: white; border-radius: 8px;}
            QListWidget::item:hover {background: #333;}
        """)
        self.suggestion_list.hide()
        self.suggestion_list.itemClicked.connect(self.use_suggestion)
        left_layout.addWidget(self.suggestion_list)

        btn_search = QPushButton("Search Text")
        btn_search.setFont(self.font_mid)
        btn_search.setStyleSheet("background: #00e676; color: black; border-radius: 12px; padding: 10px;")
        btn_search.clicked.connect(self.search_item)
        left_layout.addWidget(btn_search)

        btn_upload = QPushButton("Upload Image")
        btn_upload.setFont(self.font_mid)
        btn_upload.setStyleSheet("background: #2979ff; color: white; border-radius: 12px; padding: 10px;")
        btn_upload.clicked.connect(self.upload_image)
        left_layout.addWidget(btn_upload)

        left_layout.addStretch()
        main_layout.addLayout(left_layout, 3)

        # ===== Right Panel =====
        self.phone = QWidget()
        self.phone.setStyleSheet("background: black; border-radius: 40px;")
        phone_layout = QVBoxLayout(self.phone)
        phone_layout.setContentsMargins(20, 20, 20, 20)
        phone_layout.setSpacing(10)

        header = QLabel("EcoSort ♻️")
        header.setFont(self.font_large)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00c853, stop:1 #00e676);
                color: white; padding: 14px; border-radius: 28px;
            }
        """)
        phone_layout.addWidget(header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: #121212; border: none;")
        scroll_content = QWidget()
        self.result_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(self.result_layout)
        self.scroll_area.setWidget(scroll_content)
        phone_layout.addWidget(self.scroll_area)

        self.image_label = QLabel("Upload or take an image")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: black; color: white; border-radius: 20px;")
        phone_layout.addWidget(self.image_label)

        main_layout.addWidget(self.phone, 7)
        self.setCentralWidget(central)

    # ===== Suggestion handling =====
    def show_suggestions(self, text):
        self.suggestion_list.clear()
        text = text.strip().lower()
        if text:
            for item in self.waste_data:
                name = item["name"].lower()
                associates = [a.lower() for a in item.get("associates", [])]
                if text in name or any(text in a for a in associates):
                    self.suggestion_list.addItem(item["name"])
            self.suggestion_list.setVisible(self.suggestion_list.count() > 0)
        else:
            self.suggestion_list.hide()

    def use_suggestion(self, item):
        self.search_bar.setText(item.text())
        self.search_item()
        self.suggestion_list.hide()

    # ===== Clear previous results =====
    def clear_results(self):
        for i in reversed(range(self.result_layout.count())):
            self.result_layout.itemAt(i).widget().deleteLater()

    # ===== Display a single item =====
    def display_item(self, item):
        label_style = "color: white; font-size: 24px; padding: 4px;"
        fields = ["name", "type", "three_r_tip", "disposal", "toxicity", "alternatives", "handling_precautions"]
        for field in fields:
            text = item[field] if field != "alternatives" else ', '.join(item[field])
            lbl = QLabel(f"<b>{field.replace('_',' ').title()}:</b> {text}")
            lbl.setStyleSheet(label_style)
            lbl.setWordWrap(True)
            self.result_layout.addWidget(lbl)

    # ===== Text Search =====
    def search_item(self):
        query = self.search_bar.text().strip().lower()
        self.clear_results()
        if not query:
            lbl = QLabel("⚠ Please type something to search.")
            lbl.setStyleSheet("color: red; font-size: 20px;")
            self.result_layout.addWidget(lbl)
            return

        found = False
        for item in self.waste_data:
            name_lower = item['name'].lower()
            associates_lower = [a.lower() for a in item.get('associates', [])]
            if query == name_lower or query in associates_lower or any(query in assoc for assoc in associates_lower):
                self.display_item(item)
                found = True
        if not found:
            lbl = QLabel("⚠ Item not found.")
            lbl.setStyleSheet("color: red; font-size: 20px;")
            self.result_layout.addWidget(lbl)

    # ===== Upload Image using HF API =====
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_path:
            return
        self.clear_results()

        # Display image
        pixmap = QPixmap(file_path).scaled(600, 400, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)

        # Detect with Hugging Face DETR
        results = detect_objects_hf(file_path)
        detected_items = []

        if isinstance(results, list):
            for obj in results:
                label = obj.get("label", "").lower()
                mapped_label = YOLO_TO_JSON_MAPPING.get(label, label)
                detected_items.append(mapped_label)

        if detected_items:
            self.search_bar.setText(detected_items[0])
            self.search_item()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WasteSorterApp()
    win.show()
    sys.exit(app.exec_())
