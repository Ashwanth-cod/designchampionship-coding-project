import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QTextBrowser
)
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve

# ------------ Load JSON ------------
with open("waste_items.json", "r", encoding="utf-8") as f:
    ITEMS = json.load(f)

def search_item(query: str):
    query = query.lower().strip()
    for item in ITEMS:
        if query == item["name"].lower() or query in [a.lower() for a in item["associates"]]:
            return item
    return None

def find_suggestions(query: str):
    query = query.lower().strip()
    if not query:
        return []
    matches = []
    for item in ITEMS:
        if query in item["name"].lower() or any(query in a.lower() for a in item["associates"]):
            matches.append(item["name"])
    return matches

# ------------ App ------------
class WasteSorterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("♻️ Waste Sorter")
        self.resize(1400, 850)

        # Dark gradient background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 1000)
        gradient.setColorAt(0.0, QColor("#0d0d0d"))
        gradient.setColorAt(1.0, QColor("#1a1a1a"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        # Fonts
        self.font_large = QFont("Arial", 22, QFont.Bold)
        self.font_mid = QFont("Arial", 13)

        # Central layout
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(40)

        # ===== Left: Search Section =====
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        title = QLabel("♻️ Waste Sorter")
        title.setFont(self.font_large)
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        left_layout.addWidget(title)

        self.suggestion_list = QListWidget()
        self.suggestion_list.setMaximumHeight(150)
        self.suggestion_list.setStyleSheet("""
            QListWidget {
                background: #1e1e1e;
                border-radius: 12px;
                font-size: 14px;
                color: white;
            }
            QListWidget::item { padding: 8px; }
            QListWidget::item:hover { background: #333; }
        """)
        self.suggestion_list.itemClicked.connect(self.use_suggestion)
        self.suggestion_list.hide()
        left_layout.addWidget(self.suggestion_list)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Search waste item...")
        self.input_box.setFont(self.font_mid)
        self.input_box.setStyleSheet("""
            QLineEdit {
                background: #1e1e1e;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
                border: 2px solid #333;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #00e676;
            }
        """)
        self.input_box.textChanged.connect(self.show_suggestions)
        left_layout.addWidget(self.input_box)

        btn = QPushButton("Search")
        btn.setFont(self.font_mid)
        btn.setStyleSheet("""
            QPushButton {
                background: #00e676;
                color: black;
                font-weight: bold;
                border-radius: 12px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background: #00c853;
            }
        """)
        btn.clicked.connect(self.search_item)
        left_layout.addWidget(btn)

        left_layout.addStretch()
        main_layout.addLayout(left_layout, 3)  # 30% width

        # ===== Right: Phone Section =====
        self.phone = QFrame()
        self.phone.setStyleSheet("""
            QFrame {
                background: black;
                border-radius: 40px;
                border: 6px solid #333;
            }
        """)
        phone_outer_layout = QVBoxLayout(self.phone)
        phone_outer_layout.setContentsMargins(8, 8, 8, 8)

        # Inner screen
        self.phone_screen = QFrame()
        self.phone_screen.setStyleSheet("""
            QFrame {
                background: #121212;
                border-radius: 28px;
            }
        """)
        phone_layout = QVBoxLayout(self.phone_screen)
        phone_layout.setContentsMargins(10, 10, 10, 10)
        phone_layout.setSpacing(10)

        # App header inside phone
        header = QLabel("EcoSort ♻️")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00c853, stop:1 #00e676
                );
                color: white;
                padding: 14px;
                border-top-left-radius: 28px;
                border-top-right-radius: 28px;
            }
        """)
        phone_layout.addWidget(header)

        # Scrollable result area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: #121212; border: none;")
        self.scroll_area.hide()

        scroll_content = QWidget()
        self.result_layout = QVBoxLayout(scroll_content)
        self.result_layout.setContentsMargins(6, 6, 6, 6)
        scroll_content.setLayout(self.result_layout)
        self.scroll_area.setWidget(scroll_content)

        phone_layout.addWidget(self.scroll_area)
        phone_outer_layout.addWidget(self.phone_screen)
        main_layout.addWidget(self.phone, 7)  # 70% width

        self.setCentralWidget(central)
        self.animate_widget(self.phone, y_offset=100, duration=700)

    # ---------- Suggestions ----------
    def show_suggestions(self, text):
        self.suggestion_list.clear()
        if not text.strip():
            self.suggestion_list.hide()
            return

        matches = find_suggestions(text)
        if matches:
            for m in matches[:5]:
                self.suggestion_list.addItem(QListWidgetItem(m))
            self.suggestion_list.show()
            self.animate_widget(self.suggestion_list, y_offset=-15, duration=300)
        else:
            self.suggestion_list.hide()

    def use_suggestion(self, item):
        self.input_box.setText(item.text())
        self.search_item()

    # ---------- Search ----------
    def search_item(self):
        query = self.input_box.text().strip()
        if not query:
            return

        result = search_item(query)
        for i in reversed(range(self.result_layout.count())):
            widget = self.result_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if result:
            for key, value in result.items():
                if isinstance(value, list):
                    value = ", ".join(value)

                text_box = QTextBrowser()
                text_box.setFont(self.font_mid)
                text_box.setOpenExternalLinks(True)
                text_box.setMinimumHeight(90)
                text_box.setFixedWidth(self.phone_screen.width() - 16)
                text_box.setStyleSheet("""
                    QTextBrowser {
                        background: #1e1e1e;
                        border-radius: 10px;
                        padding: 10px;
                        margin: 6px 0;
                        color: white;
                        border: 1px solid #333;
                    }
                    QTextBrowser a {
                        color: #00e676;
                        text-decoration: none;
                        font-weight: bold;
                    }
                    QTextBrowser a:hover {
                        color: #69f0ae;
                    }
                """)
                if "http" in str(value):
                    text_box.setHtml(f"<b style='color:#00e676'>{key.replace('_',' ').title()}:</b> "
                                     f"<a href='{value}'>{value}</a>")
                else:
                    text_box.setHtml(f"<b style='color:#00e676'>{key.replace('_',' ').title()}:</b> {value}")
                self.result_layout.addWidget(text_box)
                self.animate_widget(text_box, y_offset=20, duration=400)
            self.scroll_area.show()
        else:
            box = QLabel("❌ Item not found")
            box.setFont(self.font_mid)
            box.setStyleSheet("color: #ff5252; margin: 8px;")
            self.result_layout.addWidget(box)
            self.scroll_area.show()

    # ---------- Animations ----------
    def animate_widget(self, widget, y_offset=20, duration=400):
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration)
        anim.setStartValue(QRect(widget.x(), widget.y() + y_offset, widget.width(), widget.height()))
        anim.setEndValue(widget.geometry())
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WasteSorterApp()
    window.show()
    sys.exit(app.exec_())
