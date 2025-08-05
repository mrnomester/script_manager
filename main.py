import tkinter as tk
from config import Config
import subprocess
import os

class ScriptManager(tk.Tk):
    def __init__(self):
        super().__init__()
        """основное окно"""
        self.title("Script manager")
        self.geometry("1200x800")
        self._check_path()
        self._create_widgets()

    def _open_script_folder(self, folder_path): # принимает путь
        """Открывает папку со скриптами"""
        subprocess.Popen(f'explorer "{folder_path}"')

    def _check_path(self):
        """валидация всех путей и проверка доступов""" # Не приоритет, реализуется позднее

        pass


    def _check_script(self):
        """Чтение всех скриптов из папки со скриптами (для перечисления и запуска)"""
        
        pass

    def _scrip_command_line(self): # принимает имя скрипта из списка
        """путь до выбранного скрипта"""
        pass

    def _create_widgets(self):
        """Создаёт все элементы интерфейса."""
        # кнопка закрытия основного окна
        btn_close = tk.Button(
            self,
            text="Закрыть окно",
            command=self.destroy
        )
        btn_close.pack(pady=10)

        # кнопка открытия папки со скриптами
        btn_open_script_folder = tk.Button(
            self,
            text="Открыть папку со скриптами",
            command = lambda:  self.open_script_folder(Config.SCRIPT_FOLDER)
        )
        btn_open_script_folder.pack(pady=10)

        # кнопка запуска скрипта с обычными правами
        btn_start_script = tk.Button(
            self,
            text="Запустить скрипт",
            command = subprocess.Popen(f'r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File "{_script_command_line}"')
        )
        btn_start_script.pack(pady=10)

        # кнопка запуска от имени админа

        # кнопка просмотра скрипта и редактирования





if __name__ == "__main__":
    """Запуск приложения"""
    app = ScriptManager()
    app.mainloop()
