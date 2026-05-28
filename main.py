import sys

from PySide6.QtWidgets import QApplication
from audio.komunikaty_glosowe import uruchom_glos
from camera.modul_kamer import find_cameras
from gui.gui_start import MainWindow
from database.db_manager import init_db

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)

    cams = find_cameras()

    window = MainWindow(cams)
    window.show()
    uruchom_glos()

    sys.exit(app.exec())