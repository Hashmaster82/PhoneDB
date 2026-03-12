# -*- coding: utf-8 -*-
"""
Модуль для работы с конфигурацией программы.
Управляет настройками и путями к данным.
"""
import os
import json
import shutil
from pathlib import Path
from typing import Optional, Tuple


class ConfigManager:
    """Менеджер конфигурации приложения."""

    # Имя файла конфигурации
    CONFIG_FILENAME = "altayzinc_phonebook_config.json"

    # Имя файла-указателя пути к конфигурации (bootstrap)
    BOOTSTRAP_FILENAME = "config_location.txt"

    # Имена файлов данных
    DATABASE_FILENAME = "phonebook.db"
    NOTES_FILENAME = "notes.txt"

    def __init__(self, app_dir: Optional[Path] = None):
        """
        Инициализация менеджера конфигурации.

        Args:
            app_dir: Путь к директории приложения (для bootstrap файла).
        """
        self.app_dir = app_dir
        self.default_config_dir = Path.home() / ".altayzinc_phonebook"

        # Загружаем кастомный путь к конфигурации из bootstrap файла
        self.app_config_dir = self._load_custom_config_dir()
        self.app_config_file = self.app_config_dir / self.CONFIG_FILENAME
        self.data_path: Optional[Path] = None

    def _load_custom_config_dir(self) -> Path:
        """
        Проверяет наличие bootstrap файла с путём к конфигурации.

        Returns:
            Path: Директория конфигурации.
        """
        if self.app_dir:
            bootstrap_path = self.app_dir / self.BOOTSTRAP_FILENAME
            if bootstrap_path.exists():
                try:
                    path_str = bootstrap_path.read_text(encoding='utf-8').strip()
                    if path_str:
                        custom_path = Path(path_str)
                        if custom_path.exists() and custom_path.is_dir():
                            return custom_path
                except Exception:
                    pass
        return self.default_config_dir

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

    def get_data_path(self) -> Optional[Path]:
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

    def set_config_directory(self, new_path: str | Path) -> Tuple[bool, str]:
        """
        Устанавливает новую директорию для файла конфигурации.

        Args:
            new_path: Путь к новой директории конфигурации.

        Returns:
            Кортеж (успех, сообщение).
        """
        new_path = Path(new_path)

        # Проверяем существование и права записи
        if not new_path.exists():
            try:
                new_path.mkdir(parents=True, exist_ok=True)
            except (IOError, PermissionError) as e:
                return False, f"Не удалось создать папку: {str(e)}"

        if not new_path.is_dir():
            return False, f"Указанный путь не является папкой: {new_path}"

        # Проверяем права записи
        test_file = new_path / ".config_write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except (IOError, PermissionError) as e:
            return False, f"Нет прав на запись в папку: {str(e)}"

        # Копируем текущий конфиг в новую папку
        if self.app_config_file.exists():
            try:
                new_config_file = new_path / self.CONFIG_FILENAME
                shutil.copy2(self.app_config_file, new_config_file)
            except Exception as e:
                return False, f"Не удалось скопировать файл конфигурации: {str(e)}"

        # Сохраняем путь в bootstrap файл
        if self.app_dir:
            try:
                bootstrap_path = self.app_dir / self.BOOTSTRAP_FILENAME
                bootstrap_path.write_text(str(new_path), encoding='utf-8')
            except Exception as e:
                return False, f"Не удалось сохранить путь к конфигурации: {str(e)}"

        # Обновляем текущую директорию
        self.app_config_dir = new_path
        self.app_config_file = new_path / self.CONFIG_FILENAME

        return True, "Путь к конфигурации успешно обновлён."

    def get_database_path(self) -> Optional[Path]:
        """
        Получает полный путь к файлу базы данных.

        Returns:
            Path к файлу БД или None.
        """
        data_path = self.get_data_path()
        if data_path:
            return data_path / self.DATABASE_FILENAME
        return None

    def get_notes_path(self) -> Optional[Path]:
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

    def validate_data_path(self) -> Tuple[bool, str]:
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