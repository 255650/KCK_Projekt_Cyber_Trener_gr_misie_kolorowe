import sys
import cv2
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)
from camera.modul_kamer import find_cameras
from PySide6.QtCore import Qt, QTimer


class TrainingWindow(QWidget):
    def __init__(self, cams):
        super().__init__()

        self.setWindowTitle("Trening")
        self.resize(1280, 720)

        self.cams = cams

        layout = QVBoxLayout()

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.camera_label)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS


    def update_frame(self):
        ret1, frame = self.cams[0].read()

        if not ret1:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape
        bytes_per_line = ch * w

        qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_img)

        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.width(),
                self.camera_label.height(),
                Qt.KeepAspectRatio
            )
        )

class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Historia treningów")
        self.resize(700, 400)

        layout = QVBoxLayout()

        title = QLabel("Historia treningów")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        table = QTableWidget()
        table.setRowCount(3)
        table.setColumnCount(3)

        table.setHorizontalHeaderLabels([
            "Data",
            "Powtórzenia",
            "Technika"
        ])

        # Przykładowe dane narazie
        data = [
            ["2026-05-01", "10", "82%"],
            ["2026-05-03", "12", "88%"],
            ["2026-05-05", "9", "79%"],
        ]

        for row in range(len(data)):
            for col in range(len(data[row])):
                table.setItem(
                    row,
                    col,
                    QTableWidgetItem(data[row][col])
                )

        layout.addWidget(title)
        layout.addWidget(table)

        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self,cams):
        super().__init__()

        self.cams=cams
        self.setWindowTitle("Cyber Trener")
        self.resize(500, 400)

        layout = QVBoxLayout()

        title = QLabel("CYBER TRENER")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 30px;
        """)

        self.start_button = QPushButton("START TRENINGU")
        self.history_button = QPushButton("HISTORIA")
        self.exit_button = QPushButton("WYJŚCIE")

        buttons = [
            self.start_button,
            self.history_button,
            self.exit_button
        ]

        for button in buttons:
            button.setFixedHeight(60)

            button.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    background-color: #333;
                    color: white;
                    border-radius: 10px;
                }

                QPushButton:hover {
                    background-color: #555;
                }
            """)

            layout.addWidget(button)

        layout.insertWidget(0, title)

        self.setLayout(layout)

        self.start_button.clicked.connect(self.open_training)
        self.history_button.clicked.connect(self.open_history)
        self.exit_button.clicked.connect(self.close)

    def open_training(self):
        self.training_window = TrainingWindow(self.cams)
        self.training_window.show()

    def open_history(self):
        self.history_window = HistoryWindow()
        self.history_window.show()


app = QApplication(sys.argv)
cams = find_cameras()
window = MainWindow(cams)
window.show()

sys.exit(app.exec())