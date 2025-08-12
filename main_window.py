from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout,
    QMenuBar, QMenu, QFileDialog, QMessageBox
)
from PySide6.QtGui import QShortcut, QFont, QIcon
from PySide6.QtCore import Qt
import sys
from logic import get_script_lists, start_script
from config import Config


class ScriptManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Manager")
        self.resize(400, 600)
        self.setStyleSheet("""
            QMainWindow {background: #23272e;}
            QLabel {color: #e0e0e0;}
            QListWidget {background: #181a20; color: #e0e0e0; border-radius: 6px;}
            QPushButton {background: #2d313a; color: #e0e0e0; border-radius: 6px; padding: 6px;}
            QPushButton:disabled {background: #444;}
            QStatusBar{background-color:#181a20; color:#e0e0e0;}
        """)

        self.list_widget = None
        self.button_run = None
        self.button_refresh = None
        self.status_bar = self.statusBar()
        self.setup_menu()
        self.setup_ui()
        self.setup_shortcuts()
        self.load_scripts()

    def setup_menu(self):
        menu_bar = QMenuBar(self)
        settings_menu = QMenu("Настройки", self)
        select_folder_action = settings_menu.addAction("Выбрать папку скриптов")
        select_folder_action.triggered.connect(self.select_script_folder)
        menu_bar.addMenu(settings_menu)
        self.setMenuBar(menu_bar)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        label = QLabel("Список скриптов")
        label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        main_layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Consolas", 11))
        main_layout.addWidget(self.list_widget)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

        btn_layout = QHBoxLayout()
        self.button_run = QPushButton(QIcon(), "Запустить")
        self.button_run.setEnabled(False)
        self.button_run.clicked.connect(self.on_button_clicked)
        btn_layout.addWidget(self.button_run)

        self.button_refresh = QPushButton(QIcon(), "Обновить")
        self.button_refresh.clicked.connect(self.load_scripts)
        btn_layout.addWidget(self.button_refresh)

        main_layout.addLayout(btn_layout)

        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.showMessage("Готово")

    def on_selection_changed(self):
        self.button_run.setEnabled(len(self.list_widget.selectedItems()) > 0)

    def on_button_clicked(self):
        selection = self.list_widget.selectedItems()
        if not selection:
            self.status_bar.showMessage("Скрипт не выбран")
            return

        script_name = selection[0].text()
        self.button_run.setEnabled(False)
        self.status_bar.showMessage(f"Запуск {script_name}")
        start_script(script_name)
        self.status_bar.showMessage(f"Скрипт {script_name} запущен")
        self.button_run.setEnabled(True)

    def load_scripts(self):
        self.list_widget.clear()
        try:
            scripts = get_script_lists()
            if scripts:
                self.list_widget.addItems(scripts)
                self.status_bar.showMessage(f"Загружено {len(scripts)} скриптов")
            else:
                self.status_bar.showMessage("Нет доступных скриптов")
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки: {str(e)}")

    def select_script_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку со скриптами", Config.get_script_folder())
        if folder:
            Config.set_script_folder(folder)
            QMessageBox.information(self, "Папка изменена", "Папка скриптов успешно изменена.\nОбновите список скриптов.")
            self.status_bar.showMessage("Папка скриптов изменена")

    def setup_shortcuts(self):
        refresh = QShortcut("F5", self)
        refresh.activated.connect(self.load_scripts)

# Основное окно
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ScriptManager()
    window.show()
    app.exec()
