import sys

from PySide6.QtWidgets import QApplication

from camera.modul_kamer import find_cameras
from gui.gui_start import MainWindow

app = QApplication(sys.argv)

cams = find_cameras()

window = MainWindow(cams)
window.show()

sys.exit(app.exec())