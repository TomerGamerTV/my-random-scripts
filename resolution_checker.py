import importlib

def check_pyqt5():
    try:
        importlib.import_module("PyQt5")
        print("PyQt5 is already installed.")
    except ImportError:
        print("PyQt5 is not found. Please install it by running 'pip install pyqt5'.")

def main():
    check_pyqt5()

    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt5.QtCore import QSize, Qt

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

        def resizeEvent(self, event):
            size = event.size()
            width = size.width()
            height = size.height()
            self.update_centered_label()

            self.setWindowTitle(f"Resizable Window - {width}x{height}")

        def update_centered_label(self):
            self.centered_label.setGeometry(0, 0, self.width(), self.height())
            self.centered_label.setText(f"{self.width()}x{self.height()}")

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()