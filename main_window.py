from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QListWidget, QPushButton
)
import sys
from logic import script_lists, start_script


class ScriptManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Manager")
        #self.setWindowIcon(QIcon("icon.ico"))
        self.resize(500, 600)

        self.list_widget = None
        self.button = None
        self.status_bar = None

        self.setup_ui()

    def setup_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        #Лэйауты
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        layout.setContentsMargins(10, 10, 10, 10)  # Отступы: лево, верх, право, низ
        layout.setSpacing(10)  # Расстояние между элементами

        # Подпись в лэайаут скриптов
        label = QLabel("Скрипты:")
        layout.addWidget(label)

        # Поле, где будет список скриптов
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Загружаем скрипты
        scripts = script_lists()
        self.list_widget.addItems(scripts)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

        # Кнопка запуска скрипта
        self.button = QPushButton("Запустить")
        self.button.clicked.connect(self.on_button_clicked)
        self.button.setEnabled(False)
        layout.addWidget(self.button)

        # Статус бар
        self.status_bar = self.statusBar()
        self.status_bar.setSizeGripEnabled(True)
        self.status_bar.setStyleSheet("QStatusBar{background-color:rgb(0, 0, 0)}")
        self.status_bar.showMessage("Готово")

    def on_selection_changed(self):
        self.button.setEnabled(len(self.list_widget.selectedItems()) > 0)

    def on_button_clicked(self):
        selection = self.list_widget.selectedItems()
        if selection:
            self.status_bar.showMessage(f"Выбран {selection[0].text()}")
        else:
            self.status_bar.showMessage("Готово ")


# Основное окно
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ScriptManager()
    window.show()
    app.exec()
