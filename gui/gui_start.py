import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem, QHBoxLayout,
)

from audio.komunikaty_glosowe import powiedz
from camera.analiza import get_combined_tech, get_rep_count, reset_session
from camera.kamera_boczna import process_side_frame
from camera.kamera_przednia import process_front_frame
from database.db_manager import get_training_history


class TrainingWindow(QWidget):
    def __init__(self, cams):
        super().__init__()

        self.setWindowTitle("Trening")
        self.resize(1280, 720)

        self.cams = cams

        main_layout = QVBoxLayout()
        top_bar = QHBoxLayout()
        self.tech_label = QLabel("TECHNIKA: 0%")
        self.rep_label = QLabel("POWTORZENIA: 0")
        self.end_label = QLabel("Naciśnij SPACJĘ lub ESCAPE aby zakończyć trening")
        self.end_label.setAlignment(Qt.AlignCenter)
        for lbl in (self.tech_label, self.rep_label):
            lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
            lbl.setFixedHeight(30)
        top_bar.addWidget(self.tech_label)
        top_bar.addStretch()
        top_bar.addWidget(self.end_label)
        top_bar.addStretch()
        top_bar.addWidget(self.rep_label)

        layout = QHBoxLayout()
        self.front_label = QLabel()
        self.side_label = QLabel()

        for label in [self.front_label, self.side_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: black;")

        layout.addWidget(self.front_label)
        layout.addWidget(self.side_label)

        main_layout.addLayout(top_bar)
        main_layout.addLayout(layout)
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        if len(self.cams) < 2:
            return

        ret1, front = self.cams[0].read()
        ret2, side = self.cams[1].read()

        if ret1:
            front_proc = process_front_frame(front)
            self.show_frame(front_proc, self.front_label)
        if ret2:
            side_proc = process_side_frame(side)
            self.show_frame(side_proc, self.side_label)

        try:
            combined = get_combined_tech()
            reps = get_rep_count()

            if combined >= 85:
                bg = "#1f6f3a"
            elif combined >= 70:
                bg = "#8a6a1a"
            else:
                bg = "#7a1f1f"

            self.tech_label.setStyleSheet(f"""
                font-size: 16px;
                font-weight: bold;
                padding: 6px;
                border-radius: 6px;
                background-color: {bg};
            """)

            self.tech_label.setText(f"TECHNIKA: {combined}%")
            self.rep_label.setText(f"POWTORZENIA: {reps}")
        except Exception:
            pass

    def show_frame(self, frame, label):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        label.setPixmap(
            pixmap.scaled(
                label.width(),
                label.height(),
                Qt.KeepAspectRatio
            )
        )

    def closeEvent(self, event):
        from database.db_manager import save_training

        self.timer.stop()

        try:
            koncowe_powtorzenia = get_rep_count()
            koncowa_technika = f"{get_combined_tech()}%"

            save_training(koncowe_powtorzenia, koncowa_technika)
            print(f" ZAPISANO TRENING: {koncowe_powtorzenia} powt., {koncowa_technika} techniki.")
        except Exception as e:
            print(f"Błąd zapisu do bazy: {e}")

        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Space:
            print("Wykryto klawisz końca treningu. Zamykam i zapisuję...")
            self.close()

class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Historia treningów")
        self.resize(700, 400)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
        """)
        layout = QVBoxLayout()

        title = QLabel("HISTORIA TRENINGÓW")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 10px;
        """)

        dane_z_bazy = get_training_history()

        table = QTableWidget()
        table.setRowCount(len(dane_z_bazy))
        table.setColumnCount(3)

        table.setHorizontalHeaderLabels([
            "DATA",
            "POWTÓRZENIA",
            "TECHNIKA"
        ])
        table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                border: none;
                gridline-color: #444;
            }

            QHeaderView::section {
                background-color: #00a8ff;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }

            QTableWidget::item {
                padding: 6px;
            }

            QTableWidget::item:selected {
                background-color: #0077bb;
            }
        """)
        for row in range(len(dane_z_bazy)):
            for col in range(len(dane_z_bazy[row])):
                table.setItem(
                    row,
                    col,
                    QTableWidgetItem(str(dane_z_bazy[row][col]))
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

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("CYBER TRENER")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 40px;
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
                    font-weight: bold;
                    background-color: #00a8ff;
                    color: white;
                    border-radius: 12px;
                }

                QPushButton:hover {
                    background-color: #0090dd;
                }

                QPushButton:pressed {
                    background-color: #0077bb;
                }
            """)

            layout.addWidget(button)

        layout.insertWidget(0, title)

        self.setLayout(layout)

        status = QLabel("Gotowy do rozpoczęcia treningu?")
        status.setAlignment(Qt.AlignCenter)

        status.setStyleSheet("""
            color: #888;
            font-size: 12px;
        """)

        layout.addWidget(status)

        self.start_button.clicked.connect(self.open_training)
        self.history_button.clicked.connect(self.open_history)
        self.exit_button.clicked.connect(self.close)

    def open_training(self):
        powiedz("Wybrane ćwiczenie: rumuński martwy ciąg")
        reset_session()
        self.training_window = TrainingWindow(self.cams)
        self.training_window.show()

    def open_history(self):
        self.history_window = HistoryWindow()
        self.history_window.show()

