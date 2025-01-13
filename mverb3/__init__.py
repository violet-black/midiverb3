import sys
from PySide6.QtWidgets import QApplication
from mverb3.app import _MainWindow, Device

__all__ = ["main"]


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MidiVerb III")
    window = _MainWindow()
    window.show()
    device = Device(window)
    app.exec()
    device.close()
