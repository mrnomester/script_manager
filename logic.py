import sys
import io
import os
import subprocess
from config import Config

Config.validate_path()

def get_script_lists():
    """создание списка имен скриптов"""
    script_list = []
    for file in os.listdir(Config.get_script_folder()):
        if file.endswith(".ps1") or file.endswith(".bat"):
            script_list.append(file)
    return sorted(script_list)

def get_script_path(script_name):
    """Создает полный путь до скрипта"""
    script_path = os.path.join(Config.get_script_folder(), script_name)
    return script_path

def start_script(script_name):
    script_path = get_script_path(script_name)
    if script_name.endswith(".ps1"):
        subprocess.Popen([
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-NoProfile",
            "-File", script_path
        ])
    elif script_name.endswith(".bat"):
        subprocess.Popen([script_path], shell=True)
