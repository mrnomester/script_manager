import os
import sys


class Config:
    _SCRIPT_FOLDER = os.path.join(r"\\nas\Distrib\script\.manual_scripts")

    @classmethod
    def validate_path(cls):
        """Проверка доступности путей"""
        if not os.path.isdir(cls._SCRIPT_FOLDER):
            print(f"Нет доступа до папки")
            sys.exit(1)

    @classmethod
    def get_script_folder(cls):
        """Единственный способ получить путь"""
        cls.validate_path()
        return cls._SCRIPT_FOLDER