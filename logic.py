import sys
import io
import os
import subprocess
from config import Config

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
Config.validate_path()

def get_script_lists():
    """создание списка имен скриптов"""
    script_list = []
    for i, file in enumerate(os.listdir(Config.get_script_folder()), 1):
        if file.endswith(".ps1"):
            script_list.append(file)
    return script_list

def get_script_path(script_name):
    """Создает полный путь до скрипта"""
    script_path = os.path.join(Config.get_script_folder(), script_name)
    return script_path

def start_script(script_name):
    try:
        subprocess.run([
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-NoProfile",
            "-File", get_script_path(script_name)],
            check = True
        )
        print("Скрипт запущен")
    except subprocess.CalledProcessError:
        print("Ошибка при запуске скрипта")