import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QListWidget, QScrollArea, QFileDialog,
    QGridLayout, QFrame
)
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt
from ultralytics import YOLO
from google import genai
from google.genai import types

# ===================== CONFIG =====================
API_KEY = "AIzaSyAAsF1Q6vFVxuWbsKWjToLigZc0Zi_f-5o"
YOLO_MODEL_PATH = "best.pt"

# ===================== GEMINI TIP =====================
def get_disposal_tip(item_name: str) -> str:
    try:
        client = genai.Client(api_key=API_KEY)
        prompt = (
            f"Give me a short disposal tip for '{item_name}'. "
            "The answer must be exactly 3 lines. "
            "Keep it simple, clear, and eco-friendly, formatted as a paragraph."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5, max_output_tokens=200)
        )
        return response.text.strip() if response and response.text else "⚠️ No response from Gemini."
    except Exception as e:
        return f"❌ Error: {e}"

# ===================== APP =====================
class WasteSorterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("♻️ Waste Sorter")
        self.showMaximized()

        self.font_large = QFont("Arial", 28, QFont.Bold)
        self.font_mid = QFont("Arial", 16)

        # Background gradient
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#0b0b0b"))
        gradient.setColorAt(1, QColor("#003300"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        # Load JSON data
        with open("assets/waste_items.json", "r", encoding="utf-8") as f:
            self.waste_data = json.load(f)

        # Load YOLO model
        self.yolo_model = YOLO(YOLO_MODEL_PATH)

        # Central layout
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

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFont(self.font_mid)
        btn_refresh.setStyleSheet("background: #ff9800; color: black; border-radius: 12px; padding: 10px;")
        btn_refresh.clicked.connect(self.clear_results)
        left_layout.addWidget(btn_refresh)

        self.image_label = QLabel("Upload or take an image")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: #1e1e1e; color: white; border-radius: 12px;")
        self.image_label.setFixedHeight(250)
        left_layout.addWidget(self.image_label)

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

        main_layout.addWidget(self.phone, 7)
        self.setCentralWidget(central)

    # ===== Suggestions handling =====
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
        self.suggestion_list.hide()
        self.search_item()

    # ===== Clear results =====
    def clear_results(self):
        for i in reversed(range(self.result_layout.count())):
            widget = self.result_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.search_bar.clear()
        self.image_label.setText("Upload or take an image")
        self.suggestion_list.hide()

    # ===== Display item =====
    def display_item(self, item, show_reference=True):
        if show_reference:
            ref_img_path = f"assets/reference/{item['name'].title().replace(' ', '-')}.png"
            if os.path.exists(ref_img_path):
                MAX_WIDTH = 400
                MAX_HEIGHT = 400
                pixmap = QPixmap(ref_img_path).scaled(
                    MAX_WIDTH, MAX_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.image_label.setPixmap(pixmap)

        item_with_tip = item.copy()
        item_with_tip["disposal_tip"] = get_disposal_tip(item["name"]) or "⚠️ No disposal tip available."

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-radius: 16px;
                border: 1px solid #333;
                padding: 16px;
            }
        """)
        grid = QGridLayout(card)
        grid.setSpacing(12)

        key_style = "color: #00e676; font-size: 18px; font-weight: bold;"
        value_style = "color: white; font-size: 18px;"

        fields = [
            "name", "waste_category", "three_r_tip",
            "toxicity", "alternatives", "handling_precautions",
            "disposal_tip"
        ]

        for row, field in enumerate(fields):
            if field not in item_with_tip:
                continue
            key = QLabel(field.replace("_", " ").title() + ":")
            key.setStyleSheet(key_style)
            key.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            key.setTextInteractionFlags(Qt.TextSelectableByMouse)

            val_raw = item_with_tip[field]
            val_text = ", ".join(str(v) for v in val_raw) if isinstance(val_raw, list) else str(val_raw)

            value = QLabel(val_text)
            value.setStyleSheet(value_style)
            value.setWordWrap(True)
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)

            grid.addWidget(key, row, 0)
            grid.addWidget(value, row, 1)

        card.setLayout(grid)
        self.result_layout.addWidget(card)

    # ===== Text Search =====
    def search_item(self):
        query = self.search_bar.text().strip().lower()
        if not query:
            return
        self.clear_results()
        matches = [
            item for item in self.waste_data
            if query in item["name"].lower()
            or any(query in a.lower() for a in item.get("associates", []))
        ]
        if matches:
            for item in matches:
                self.display_item(item, show_reference=True)
        else:
            lbl = QLabel(f"⚠ No match found for '{query}'")
            lbl.setStyleSheet("color: yellow; font-size: 20px;")
            self.result_layout.addWidget(lbl)

    # ===== Image Upload =====
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_path:
            return
        self.clear_results()
        pixmap = QPixmap(file_path).scaled(600, 400, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)

        try:
            results = self.yolo_model(file_path)
            probs = results[0].probs
            if probs is None:
                lbl = QLabel("⚠ YOLO did not return class probabilities.")
                lbl.setStyleSheet("color: red; font-size: 20px;")
                self.result_layout.addWidget(lbl)
                return

            top_idx = int(probs.top1)
            predicted_cat = results[0].names[top_idx].replace("_", " ")

            # Populate suggestions only
            matches = [item for item in self.waste_data if item.get("type", "").lower() == predicted_cat.lower()]
            if matches:
                self.suggestion_list.clear()
                for item in matches:
                    self.suggestion_list.addItem(item["name"])
                self.suggestion_list.setVisible(True)
            else:
                lbl = QLabel(f"⚠ No items found in category '{predicted_cat}'.")
                lbl.setStyleSheet("color: yellow; font-size: 20px;")
                self.result_layout.addWidget(lbl)

        except Exception as e:
            lbl = QLabel(f"❌ YOLO error: {e}")
            lbl.setStyleSheet("color: red; font-size: 20px;")
            self.result_layout.addWidget(lbl)

# ===================== MAIN =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WasteSorterApp()
    win.show()
    sys.exit(app.exec_())
