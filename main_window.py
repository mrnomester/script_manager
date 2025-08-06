from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtWidgets import QListWidget
import sys

'''
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Manager")
        self.resize(800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main(app)

'''
app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Script Manager")
window.resize(800, 600)
window.show()
app.exec_()