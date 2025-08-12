from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QMenuBar, QMenu, QFileDialog, QMessageBox, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QShortcut, QFont, QIcon
from PySide6.QtCore import Qt
import sys
from logic import get_script_lists, start_script
from config import Config
import tempfile
import configparser
import datetime
import os

APP_ICON = None  # Можно добавить путь к иконке, например: "icon.png"

CACHE_DIR = os.path.join(tempfile.gettempdir(), "script_manager_cache")
HISTORY_FILE = os.path.join(CACHE_DIR, "script_history.ini")


def ensure_cache():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("")


def get_history():
    ensure_cache()
    config = configparser.ConfigParser()
    config.read(HISTORY_FILE, encoding="utf-8")
    return config


def set_last_run(script_path):
    ensure_cache()
    config = get_history()
    section = "history"
    if section not in config:
        config.add_section(section)
    config.set(section, script_path, datetime.datetime.now().isoformat())
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        config.write(f)


def get_last_run(script_path):
    config = get_history()
    section = "history"
    if section in config and script_path in config[section]:
        return config[section][script_path]
    return None


def format_datetime(dt_str):
    try:
        dt = datetime.datetime.fromisoformat(dt_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return "-"


def elide_text(text, width, widget):
    metrics = widget.fontMetrics()
    return metrics.elidedText(text, Qt.ElideRight, width)


class ScriptManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Manager")
        self.resize(600, 700)
        if APP_ICON:
            self.setWindowIcon(QIcon(APP_ICON))
        self.setStyleSheet("""
            QMainWindow {background: #23272e;}
            QLabel {color: #e0e0e0; font-family: 'Segoe UI';}
            QTableWidget {
                background: #181a20;
                color: #e0e0e0;
                border-radius: 12px;
                font-family: 'Segoe UI';
                font-size: 12px;
                gridline-color: transparent;
            }
            QHeaderView::section {
                background: #23272e;
                color: #e0e0e0;
                font-family: 'Segoe UI';
                font-size: 12px;
                border: none;
                padding: 6px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3a8dde, stop:1 #1e5aa8);
                color: #fff;
                border-radius: 10px;
                font-family: 'Segoe UI';
                font-size: 15px;
                padding: 10px 18px;
                margin: 0 6px;
                font-weight: 500;
                box-shadow: 0px 2px 8px #00000033;
            }
            QPushButton:disabled {
                background: #444;
                color: #bbb;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5bb6ff, stop:1 #3a8dde);
            }
            QStatusBar {
                background-color: #181a20;
                color: #e0e0e0;
                font-family: 'Segoe UI';
                font-size: 13px;
                border-top: 1px solid #333;
            }
        """)

        self.table_widget = None
        self.button_run = None
        self.button_run_admin = None
        self.button_refresh = None
        self.status_bar = self.statusBar()
        self.title_label = None
        self.sort_column = 0
        self.sort_order = Qt.SortOrder.DescendingOrder  # <-- поменяли приоритет на противоположный
        self.scripts_data = []
        self.setup_menu()
        self.setup_ui()
        self.setup_shortcuts()
        self.load_scripts()

    def setup_menu(self):
        menu_bar = QMenuBar(self)
        settings_menu = QMenu("⚙ Настройки", self)
        select_folder_action = settings_menu.addAction("Выбрать папку скриптов")
        select_folder_action.triggered.connect(self.select_script_folder)
        about_action = settings_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about)
        menu_bar.setStyleSheet("""
            QMenuBar {background: #23272e; color: #e0e0e0; font-family: 'Segoe UI'; font-size: 14px;}
            QMenu {background: #23272e; color: #e0e0e0; font-family: 'Segoe UI'; font-size: 14px;}
            QMenu::item:selected {background: #3a8dde;}
        """)
        menu_bar.addMenu(settings_menu)
        self.setMenuBar(menu_bar)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(22)

        self.title_label = QLabel("Список скриптов")
        self.title_label.setFont(QFont("Segoe UI", 18, QFont.Medium))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Название", "Создан", "Запуск"])
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setFont(QFont("Segoe UI", 12))
        self.table_widget.horizontalHeader().setStretchLastSection(False)
        self.table_widget.horizontalHeader().setSectionsClickable(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(False)
        main_layout.addWidget(self.table_widget)
        self.table_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.table_widget.horizontalHeader().sectionClicked.connect(self.sort_by_column)

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)

        self._resize_columns = self.resize_columns
        self.table_widget.viewport().resizeEvent = self.on_table_resize
        self.resize_columns()

        btn_layout = QHBoxLayout()
        self.button_run = QPushButton(QIcon.fromTheme("media-playback-start"), "Запустить")
        self.button_run.setFont(QFont("Segoe UI", 15))
        self.button_run.setToolTip("Запустить выбранный скрипт")
        self.button_run.setEnabled(False)
        self.button_run.clicked.connect(self.on_button_clicked)
        btn_layout.addWidget(self.button_run)

        self.button_run_admin = QPushButton("🛡 Админ")
        self.button_run_admin.setFont(QFont("Segoe UI", 15))
        self.button_run_admin.setToolTip("Запустить выбранный скрипт с правами администратора")
        self.button_run_admin.setEnabled(False)
        self.button_run_admin.setFixedWidth(140)
        self.button_run_admin.clicked.connect(self.on_button_admin_clicked)
        btn_layout.addWidget(self.button_run_admin)

        self.button_refresh = QPushButton(QIcon.fromTheme("view-refresh"), "Обновить")
        self.button_refresh.setFont(QFont("Segoe UI", 15))
        self.button_refresh.setToolTip("Обновить список скриптов")
        self.button_refresh.clicked.connect(self.load_scripts)
        btn_layout.addWidget(self.button_refresh)

        main_layout.addLayout(btn_layout)

        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.showMessage("Готово")

    def resize_columns(self):
        header = self.table_widget.horizontalHeader()
        total = self.table_widget.viewport().width()
        header.resizeSection(0, int(total * 0.5))
        header.resizeSection(1, int(total * 0.25))
        header.resizeSection(2, int(total * 0.25))

    def on_table_resize(self, event):
        self.resize_columns()
        QTableWidget.viewport(self.table_widget).resizeEvent(event)

    def load_scripts(self):
        selected_row = None
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
        self.table_widget.setRowCount(0)
        if not Config.is_folder_available():
            QMessageBox.critical(self, "Ошибка", "Нет доступа до папки скриптов.\nПроверьте настройки.")
            self.status_bar.showMessage("Ошибка доступа к папке")
            self.title_label.setText("Список скриптов")
            return
        try:
            scripts = get_script_lists()
            self.scripts_data = []
            if scripts:
                for script in scripts:
                    script_path = os.path.join(Config.get_script_folder(), script)
                    created = os.path.getctime(script_path)
                    created_str = datetime.datetime.fromtimestamp(created).strftime("%d.%m.%Y %H:%M")
                    last_run = get_last_run(script_path)
                    last_run_str = format_datetime(last_run) if last_run else "-"
                    self.scripts_data.append({
                        "name": script,
                        "created": created_str,
                        "created_raw": created,
                        "last_run": last_run_str,
                        "last_run_raw": last_run if last_run else "",
                        "path": script_path
                    })
                self.apply_sort()
                self.status_bar.showMessage(f"Загружено {len(scripts)} скриптов")
                self.title_label.setText(f"Список скриптов ({len(scripts)})")
                if selected_row is not None and selected_row < self.table_widget.rowCount():
                    self.table_widget.selectRow(selected_row)
            else:
                self.status_bar.showMessage("Нет доступных скриптов")
                self.title_label.setText("Список скриптов (0)")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", str(e))
            self.status_bar.showMessage("Ошибка загрузки")
            self.title_label.setText("Список скриптов")

    def apply_sort(self):
        # Сортировка по выбранному столбцу и направлению (перевёрнутая логика)
        col = self.sort_column
        order = self.sort_order
        reverse = order == Qt.SortOrder.AscendingOrder  # теперь Ascending — обратная сортировка
        if col == 0:
            self.scripts_data.sort(key=lambda x: x["name"].lower(), reverse=reverse)
        elif col == 1:
            self.scripts_data.sort(key=lambda x: x["created_raw"], reverse=not reverse)
        elif col == 2:
            def last_run_key(x):
                try:
                    return datetime.datetime.fromisoformat(x["last_run_raw"])
                except Exception:
                    return datetime.datetime.min
            self.scripts_data.sort(key=last_run_key, reverse=not reverse)
        self.fill_table()

    def fill_table(self):
        self.table_widget.setRowCount(len(self.scripts_data))
        header = self.table_widget.horizontalHeader()
        total = self.table_widget.viewport().width()
        name_col_width = int(total * 0.5)
        font = QFont("Segoe UI", 12)
        for idx, data in enumerate(self.scripts_data):
            elided_name = elide_text(data["name"], name_col_width - 20, self.table_widget)
            name_item = QTableWidgetItem(elided_name)
            name_item.setData(Qt.ItemDataRole.UserRole, data["name"])
            name_item.setFont(font)
            created_item = QTableWidgetItem(data["created"])
            created_item.setFont(font)
            last_run_item = QTableWidgetItem(data["last_run"])
            last_run_item.setFont(font)
            self.table_widget.setItem(idx, 0, name_item)
            self.table_widget.setItem(idx, 1, created_item)
            self.table_widget.setItem(idx, 2, last_run_item)
        # Отображение стрелки сортировки
        header.setSortIndicator(self.sort_column, self.sort_order)
        header.setSortIndicatorShown(True)
        self.resize_columns()

    def on_selection_changed(self):
        enabled = len(self.table_widget.selectedItems()) > 0
        self.button_run.setEnabled(enabled)
        self.button_run_admin.setEnabled(enabled)

    def get_selected_script(self):
        selected = self.table_widget.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        return self.table_widget.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def on_button_clicked(self):
        script_name = self.get_selected_script()
        if not script_name:
            self.status_bar.showMessage("Скрипт не выбран")
            return
        script_path = os.path.join(Config.get_script_folder(), script_name)
        self.status_bar.showMessage(f"Запуск {script_name}")
        start_script(script_name)
        set_last_run(script_path)
        self.load_scripts()
        self.status_bar.showMessage(f"Скрипт {script_name} запущен")

    def on_button_admin_clicked(self):
        script_name = self.get_selected_script()
        if not script_name:
            self.status_bar.showMessage("Скрипт не выбран")
            return
        script_path = os.path.join(Config.get_script_folder(), script_name)
        self.status_bar.showMessage(f"Запуск {script_name} как админ")
        import subprocess
        if script_name.endswith(".ps1"):
            subprocess.Popen([
                "powershell",
                "-Command",
                f'Start-Process powershell -ArgumentList \'-ExecutionPolicy Bypass -NoProfile -File "{script_path}"\' -Verb RunAs'
            ])
        elif script_name.endswith(".bat"):
            subprocess.Popen([
                "powershell",
                "-Command",
                f'Start-Process "{script_path}" -Verb RunAs'
            ])
        set_last_run(script_path)
        self.load_scripts()
        self.status_bar.showMessage(f"Скрипт {script_name} запущен как админ")

    def sort_by_column(self, idx):
        # Переключение направления сортировки (перевёрнутая логика)
        if self.sort_column == idx:
            self.sort_order = Qt.SortOrder.DescendingOrder if self.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.sort_column = idx
            self.sort_order = Qt.SortOrder.DescendingOrder  # <-- поменяли приоритет на противоположный
        self.apply_sort()

    def select_script_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку со скриптами", Config.get_script_folder())
        if folder:
            Config.set_script_folder(folder)
            QMessageBox.information(self, "Папка изменена", "Папка скриптов успешно изменена.\nОбновите список скриптов.")
            self.status_bar.showMessage("Папка скриптов изменена")

    def show_about(self):
        QMessageBox.information(self, "О программе",
            "Script Manager\n\nУдобный запуск PowerShell и BAT скриптов\n\nАвтор: kodelnik_ms")

    def setup_shortcuts(self):
        refresh = QShortcut("F5", self)
        refresh.activated.connect(self.load_scripts)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ScriptManager()
    window.show()
    window.resize_columns()
    app.exec()
