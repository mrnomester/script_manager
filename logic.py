import sys
import io
import os
import subprocess
from config import Config

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
Config.validate_path()

def _script_lists():
    """создание списка имен скриптов"""
    _script_list = ["EXIT"]
    for i, file in enumerate(os.listdir(Config.get_script_folder()), 1):
        if file.endswith(".ps1"):
            _script_list.append(file)

    return _script_list

def _select_script(ordinal, _script_list):
    if ordinal is None or not (0<=ordinal<len(_script_list)):
        print("Не верный номер скрипта")
        return
    script_path = os.path.join(Config.get_script_folder(), _script_list[ordinal])
    try:
        subprocess.run([
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-NoProfile",
            "-File", script_path],
            check = True
        )
        print(f"\nСкрипт {_script_list[ordinal]} запущен")
    except subprocess.CalledProcessError:
        print(f"Ошибка при запуске скрипта {_script_list[ordinal]}")

def print_list(script_list):
    """Вывод списка скриптов"""
    for i, file in enumerate(script_list):
        print(f"{i}) {file}")

def main():
    while True:
        scripts = _script_lists()
        print_list(scripts)
        try:
            menu = int(input("Введите пункт меню: "))
        except ValueError:
            print("Введите число")
            continue
        except KeyboardInterrupt:
            print("\nЗавершение работы")
            sys.exit(0)

        if len(scripts) > menu >= 0:
            if menu == 0: sys.exit(0)
            _select_script(menu, scripts)
        else:
            print(f"Ошибка: введите число от 0 до {len(scripts) - 1}")
            continue

main()
