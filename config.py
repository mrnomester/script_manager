import os
import sys
import configparser

class Config:
    _DEFAULT_SCRIPT_FOLDER = r"\\nas\Distrib\script\.manual_scripts"
    _INI_FILE = os.path.join(os.path.dirname(__file__), "settings.ini")
    _SCRIPT_FOLDER = None

    @classmethod
    def load_settings(cls):
        if os.path.exists(cls._INI_FILE):
            config = configparser.ConfigParser()
            config.read(cls._INI_FILE, encoding="utf-8")
            if "main" in config and "script_folder" in config["main"]:
                cls._SCRIPT_FOLDER = config["main"]["script_folder"]
            else:
                cls._SCRIPT_FOLDER = cls._DEFAULT_SCRIPT_FOLDER
        else:
            cls._SCRIPT_FOLDER = cls._DEFAULT_SCRIPT_FOLDER

    @classmethod
    def save_settings(cls):
        config = configparser.ConfigParser()
        config["main"] = {"script_folder": cls._SCRIPT_FOLDER}
        with open(cls._INI_FILE, "w", encoding="utf-8") as f:
            config.write(f)

    @classmethod
    def set_script_folder(cls, folder):
        cls._SCRIPT_FOLDER = folder
        cls.save_settings()

    @classmethod
    def validate_path(cls):
        cls.load_settings()
        if not os.path.isdir(cls._SCRIPT_FOLDER):
            raise FileNotFoundError("Нет доступа до папки")

    @classmethod
    def get_script_folder(cls):
        cls.load_settings()
        return cls._SCRIPT_FOLDER

    @classmethod
    def is_folder_available(cls):
        cls.load_settings()
        return os.path.isdir(cls._SCRIPT_FOLDER)
