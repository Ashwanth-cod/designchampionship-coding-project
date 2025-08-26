import sys
import cv2
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QListWidget, QScrollArea, QFrame,
    QFileDialog
)
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import json

class WasteSorterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("♻️ Waste Sorter with YOLOv8")
        self.resize(1400, 850)

        # --- Gradient background ---
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#0f2027"))
        gradient.setColorAt(0.5, QColor("#203a43"))
        gradient.setColorAt(1.0, QColor("#2c5364"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        # Fonts
        self.font_large = QFont("Arial", 26, QFont.Bold)
        self.font_mid = QFont("Arial", 14)

        # Load JSON
        with open("waste_items.json", "r") as f:
            self.waste_data = json.load(f)

        # --- Main Layout ---
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # --- Left Panel ---
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        title = QLabel("♻️ Waste Sorter")
        title.setFont(self.font_large)
        title.setStyleSheet("color: #fff; qproperty-alignment: 'AlignCenter';")
        left_layout.addWidget(title)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Search waste item...")
        self.input_box.setFont(self.font_mid)
        self.input_box.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff512f, stop:1 #dd2476);
                border-radius: 15px; padding: 12px; color: white;
                font-weight: bold;
            }
            QLineEdit:focus { border: 2px solid #ffd700; }
        """)
        self.input_box.textChanged.connect(self.show_suggestions)
        left_layout.addWidget(self.input_box)

        self.suggestion_list = QListWidget()
        self.suggestion_list.setMaximumHeight(160)
        self.suggestion_list.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #11998e, stop:1 #38ef7d);
                border-radius: 12px; color: white; font-weight: bold;
            }
            QListWidget::item:hover { background: rgba(255,255,255,0.2); }
        """)
        self.suggestion_list.itemClicked.connect(self.use_suggestion)
        self.suggestion_list.hide()
        left_layout.addWidget(self.suggestion_list)

        btn_layout = QHBoxLayout()
        btn_search = QPushButton("Search")
        btn_search.setFont(self.font_mid)
        btn_search.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00c3ff, stop:1 #ffff1c);
                color: black; border-radius: 12px; padding: 12px; font-weight: bold;
            }
            QPushButton:hover { background: #00bfff; }
        """)
        btn_search.clicked.connect(self.search_item)
        btn_layout.addWidget(btn_search)

        btn_camera = QPushButton("📷 Camera")
        btn_camera.setFont(self.font_mid)
        btn_camera.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f7971e, stop:1 #ffd200);
                color: black; border-radius: 12px; padding: 12px; font-weight: bold;
            }
            QPushButton:hover { background: #f5a623; }
        """)
        btn_camera.clicked.connect(self.open_camera)
        btn_layout.addWidget(btn_camera)

        btn_upload = QPushButton("📂 Upload Image")
        btn_upload.setFont(self.font_mid)
        btn_upload.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6a11cb, stop:1 #2575fc);
                color: white; border-radius: 12px; padding: 12px; font-weight: bold;
            }
            QPushButton:hover { background: #5a10bb; }
        """)
        btn_upload.clicked.connect(self.upload_image)
        btn_layout.addWidget(btn_upload)

        left_layout.addLayout(btn_layout)
        left_layout.addStretch()
        main_layout.addLayout(left_layout, 3)

        # --- Right Panel ---
        self.phone = QFrame()
        self.phone.setStyleSheet("""
            QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #434343, stop:1 #000000);
                border-radius: 40px; border: 6px solid #fff;}
        """)
        phone_layout = QVBoxLayout(self.phone)
        phone_layout.setContentsMargins(12, 12, 12, 12)

        header_layout = QHBoxLayout()
        header = QLabel("EcoSort ♻️")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff416c, stop:1 #ff4b2b);
                color: white; padding: 16px; border-radius: 28px; }
        """)
        header_layout.addWidget(header)

        self.btn_back = QPushButton("⬅ Back")
        self.btn_back.setFont(self.font_mid)
        self.btn_back.setStyleSheet("background: #444; color: white; border-radius: 12px; padding: 8px;")
        self.btn_back.clicked.connect(self.go_back)
        self.btn_back.hide()
        header_layout.addWidget(self.btn_back, alignment=Qt.AlignRight)
        phone_layout.addLayout(header_layout)

        # Scrollable area for results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        self.result_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(self.result_layout)
        self.scroll_area.setWidget(scroll_content)
        phone_layout.addWidget(self.scroll_area)

        # Camera display
        self.camera_label = QLabel("Camera is off")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("background: black; color: white; border-radius: 20px;")
        phone_layout.addWidget(self.camera_label)

        main_layout.addWidget(self.phone, 7)
        self.setCentralWidget(central)

        # --- Camera + YOLO ---
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.model = YOLO("yolov8n.pt")

    # --- Suggestion & Search ---
    def show_suggestions(self, text):
        self.suggestion_list.clear()
        text = text.strip().lower()
        if text:
            for item in self.waste_data:
                name = item["name"].lower()
                associates = [a.lower() for a in item["associates"]]
                if text in name or any(text in a for a in associates):
                    self.suggestion_list.addItem(item["name"])
            self.suggestion_list.setVisible(self.suggestion_list.count() > 0)
        else:
            self.suggestion_list.hide()

    def use_suggestion(self, item):
        self.input_box.setText(item.text())
        self.search_item()

    def search_item(self):
        query = self.input_box.text().strip().lower()
        self.scroll_area.show()
        self.camera_label.hide()
        self.btn_back.show()
        # Clear previous results
        for i in reversed(range(self.result_layout.count())):
            self.result_layout.itemAt(i).widget().deleteLater()

        found = False
        for item in self.waste_data:
            name = item["name"].lower()
            associates = [a.lower() for a in item["associates"]]
            if query == name or query in associates:
                found = True
                label_style = "color: white; font-size: 24px; padding: 4px;"
                fields = ["name", "type", "three_r_tip", "disposal", "toxicity", "alternatives", "handling_precautions"]
                for field in fields:
                    text = item[field] if field != "alternatives" else ', '.join(item[field])
                    lbl = QLabel(f"<b>{field.replace('_',' ').title()}:</b> {text}")
                    lbl.setStyleSheet(label_style)
                    self.result_layout.addWidget(lbl)
        if not found:
            lbl = QLabel("No result found")
            lbl.setStyleSheet("color: red; font-size: 20px;")
            self.result_layout.addWidget(lbl)

    # --- Camera & Upload ---
    def open_camera(self):
        self.scroll_area.hide()
        self.camera_label.show()
        self.btn_back.show()
        if self.cap is None:
            self.cap = cv2.VideoCapture(1)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(img_rgb)[0]

        detected_items = []
        for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
            if conf > 0.5:
                x1, y1, x2, y2 = map(int, box)
                label = self.model.names[int(cls)]
                detected_items.append(label)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        if detected_items:
            self.input_box.setText(detected_items[0])
            self.search_item()

        h, w, ch = frame.shape
        qt_img = QImage(frame.data, w, h, ch*w, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_img))

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if not file_path: return
        self.scroll_area.hide()
        self.camera_label.show()
        self.btn_back.show()
        img_bgr = cv2.imread(file_path)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = self.model(img_rgb)[0]

        detected_items = []
        for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
            if conf > 0.5:
                x1, y1, x2, y2 = map(int, box)
                label = self.model.names[int(cls)]
                detected_items.append(label)
                cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img_bgr, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)

        if detected_items:
            self.input_box.setText(detected_items[0])
            self.search_item()

        h, w, ch = img_bgr.shape
        qt_img = QImage(img_bgr.data, w, h, ch*w, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_img))

    # --- Back button ---
    def go_back(self):
        self.scroll_area.hide()
        self.camera_label.hide()
        self.btn_back.hide()
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WasteSorterApp()
    win.show()
    sys.exit(app.exec_())
