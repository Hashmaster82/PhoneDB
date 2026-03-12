# -*- coding: utf-8 -*-
"""
Модуль для работы с текстовыми заметками.
Управляет хранением дополнительной текстовой информации.
"""

from pathlib import Path
from typing import Optional


class NotesManager:
    """Менеджер заметок."""
    
    def __init__(self, notes_path: Path):
        """
        Инициализация менеджера заметок.
        
        Args:
            notes_path: Путь к файлу заметок.
        """
        self.notes_path = notes_path
        
    def load_notes(self) -> str:
        """
        Загружает заметки из файла.
        
        Returns:
            Текст заметок или пустая строка.
        """
        if self.notes_path.exists():
            try:
                with open(self.notes_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except IOError:
                return ""
        return ""
    
    def save_notes(self, text: str) -> tuple[bool, str]:
        """
        Сохраняет заметки в файл.
        
        Args:
            text: Текст для сохранения.
            
        Returns:
            Кортеж (успех, сообщение).
        """
        try:
            with open(self.notes_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True, "Заметки сохранены."
        except IOError as e:
            return False, f"Ошибка сохранения: {str(e)}"
