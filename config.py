# -*- coding: utf-8 -*-
"""
Модуль для работы с конфигурацией программы.
Управляет настройками и путями к данным.
"""

import os
import json
from pathlib import Path


class ConfigManager:
    """Менеджер конфигурации приложения."""
    
    # Имя файла конфигурации в домашней директории
    CONFIG_FILENAME = "altayzinc_phonebook_config.json"
    
    # Имена файлов данных
    DATABASE_FILENAME = "phonebook.db"
    NOTES_FILENAME = "notes.txt"
    
    def __init__(self):
        """Инициализация менеджера конфигурации."""
        self.app_config_dir = Path.home() / ".altayzinc_phonebook"
        self.app_config_file = self.app_config_dir / self.CONFIG_FILENAME
        self.data_path = None
        
    def ensure_app_config_dir(self):
        """Создаёт директорию конфигурации приложения, если её нет."""
        self.app_config_dir.mkdir(parents=True, exist_ok=True)
        
    def load_config(self) -> dict:
        """
        Загружает конфигурацию из файла.
        
        Returns:
            dict: Словарь с настройками или пустой словарь, если файл не существует.
        """
        self.ensure_app_config_dir()
        
        if self.app_config_file.exists():
            try:
                with open(self.app_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_config(self, config: dict):
        """
        Сохраняет конфигурацию в файл.
        
        Args:
            config: Словарь с настройками для сохранения.
        """
        self.ensure_app_config_dir()
        
        with open(self.app_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def get_data_path(self) -> Path | None:
        """
        Получает путь к папке с данными из конфигурации.
        
        Returns:
            Path или None, если путь не установлен.
        """
        config = self.load_config()
        path_str = config.get("data_path")
        
        if path_str:
            path = Path(path_str)
            if path.exists() and path.is_dir():
                self.data_path = path
                return path
        return None
    
    def set_data_path(self, path: str | Path):
        """
        Устанавливает путь к папке с данными.
        
        Args:
            path: Путь к папке для хранения данных.
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        config = self.load_config()
        config["data_path"] = str(path)
        self.save_config(config)
        self.data_path = path
    
    def get_database_path(self) -> Path | None:
        """
        Получает полный путь к файлу базы данных.
        
        Returns:
            Path к файлу БД или None.
        """
        data_path = self.get_data_path()
        if data_path:
            return data_path / self.DATABASE_FILENAME
        return None
    
    def get_notes_path(self) -> Path | None:
        """
        Получает полный путь к файлу заметок.
        
        Returns:
            Path к файлу заметок или None.
        """
        data_path = self.get_data_path()
        if data_path:
            return data_path / self.NOTES_FILENAME
        return None
    
    def is_configured(self) -> bool:
        """
        Проверяет, настроена ли программа.
        
        Returns:
            True, если путь к данным установлен и доступен.
        """
        return self.get_data_path() is not None
    
    def validate_data_path(self) -> tuple[bool, str]:
        """
        Проверяет доступность пути к данным.
        
        Returns:
            Кортеж (успех, сообщение об ошибке).
        """
        config = self.load_config()
        path_str = config.get("data_path")
        
        if not path_str:
            return False, "Путь к данным не настроен."
        
        path = Path(path_str)
        
        if not path.exists():
            return False, f"Папка не существует: {path}"
        
        if not path.is_dir():
            return False, f"Указанный путь не является папкой: {path}"
        
        # Проверка прав записи
        test_file = path / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except (IOError, PermissionError):
            return False, f"Нет прав на запись в папку: {path}"
        
        return True, ""
