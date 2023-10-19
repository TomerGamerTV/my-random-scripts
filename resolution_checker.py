import importlib
import platform
import os
import ctypes
import threading
import sys
import signal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QThread, QCoreApplication, pyqtSignal
import base64
import io
import pyaudio
import wave
from pydub import AudioSegment
from pydub.playback import play

def check_pyqt5():
    try:
        importlib.import_module("PyQt5")
    except ImportError:
        print("PyQt5 is not found. Please install it by running 'pip install pyqt5'.")

class LoadingThread(QThread):
    finished = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        # Simulating resource loading
        import time
        time.sleep(5)  # Simulating a 5-second loading time
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resizable Window")
        self.resize(800, 600)

        self.centered_label = QLabel(self)
        self.centered_label.setAlignment(Qt.AlignCenter)
        self.centered_label.setGeometry(0, 0, self.width(), self.height())
        self.centered_label.setStyleSheet("font-size: 20pt; font-weight: bold;")
        self.update_centered_label()

        self.resolution_loaded = False

        self.loading_thread = None

        self.show()

    def resizeEvent(self, event):
        size = event.size()
        width = size.width()
        height = size.height()
        self.update_centered_label()

        self.setWindowTitle(f"Resizable Window - {width}x{height}")

        if not self.loading_thread or not self.loading_thread.isRunning():
            self.resolution_loaded = False
            self.loading_thread = LoadingThread(self)
            self.loading_thread.finished.connect(self.loading_finished)
            self.loading_thread.start()

    def update_centered_label(self):
        self.centered_label.setGeometry(0, 0, self.width(), self.height())
        self.centered_label.setText(f"{self.width()}x{self.height()}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.play_sound()  # Play the sound here
            self.copy_resolution()
        elif event.key() == Qt.Key_Escape:
            self.exit_program()
        else:
            super().keyPressEvent(event)

    def copy_resolution(self):
        clipboard = QApplication.clipboard()
        resolution = f"{self.width()}x{self.height()}"
        clipboard.setText(resolution)
        self.show_resolution_copy_popup()

    def show_resolution_copy_popup(self):
        popup = QMessageBox()
        popup.setWindowTitle("Resolution Copied")
        popup.setText("The resolution has been copied to the clipboard.")
        popup.exec_()

    def exit_program(self):
        if self.loading_thread and self.loading_thread.isRunning():
            self.resolution_loaded = True
            self.loading_thread.quit()
            self.loading_thread.wait()
        QCoreApplication.quit()

    def loading_finished(self):
        self.resolution_loaded = True

    def play_sound(self):
        if platform.system() == 'Windows':
            ctypes.windll.user32.MessageBeep(0)
        else:
            os.system('play /usr/share/sounds/gnome/default/alerts/drip.ogg')


    def closeEvent(self, event):
        self.exit_program()

def handle_interrupt(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

app = QApplication([])
window = MainWindow()

sys.exit(app.exec_())