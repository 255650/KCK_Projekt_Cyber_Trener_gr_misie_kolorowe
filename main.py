import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from audio.komunikaty_glosowe import powiedz
from camera.modul_kamer import find_cameras
from gui.gui_start import MainWindow
from database.db_manager import init_db

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    cams = find_cameras()
    window = MainWindow(cams)
    window.show()
    QTimer.singleShot(500, lambda: powiedz("Wybrano język polski"))
    sys.exit(app.exec())