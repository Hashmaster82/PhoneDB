# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных SQLite.
Управляет хранением записей о телефонах.
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PhoneRecord:
    """Запись о телефоне."""
    id: Optional[int]
    full_name: str      # ФИО
    phone_number: str   # Номер
    login: str          # Login
    password: str       # Password
    ip_address: str     # IP адрес
    location: str       # Локация
    comment: str        # Комментарий
    
    def to_tuple(self) -> tuple:
        """Преобразует запись в кортеж (без ID)."""
        return (
            self.full_name,
            self.phone_number,
            self.login,
            self.password,
            self.ip_address,
            self.location,
            self.comment
        )
    
    @classmethod
    def from_row(cls, row: tuple) -> 'PhoneRecord':
        """Создаёт запись из строки БД."""
        return cls(
            id=row[0],
            full_name=row[1],
            phone_number=row[2],
            login=row[3],
            password=row[4],
            ip_address=row[5],
            location=row[6],
            comment=row[7]
        )


class DatabaseManager:
    """Менеджер базы данных."""
    
    CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS phones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            location TEXT DEFAULT '',
            comment TEXT DEFAULT ''
        )
    """
    
    def __init__(self, db_path: Path):
        """
        Инициализация менеджера БД.
        
        Args:
            db_path: Путь к файлу базы данных.
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """Устанавливает соединение с БД и создаёт таблицы."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.execute(self.CREATE_TABLE_SQL)
        self.connection.commit()
        
    def close(self):
        """Закрывает соединение с БД."""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def add_record(self, record: PhoneRecord) -> int:
        """
        Добавляет новую запись в БД.
        
        Args:
            record: Запись для добавления.
            
        Returns:
            ID новой записи.
        """
        cursor = self.connection.execute(
            """
            INSERT INTO phones (full_name, phone_number, login, password, ip_address, location, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            record.to_tuple()
        )
        self.connection.commit()
        return cursor.lastrowid
    
    def update_record(self, record: PhoneRecord):
        """
        Обновляет существующую запись.
        
        Args:
            record: Запись с обновлёнными данными.
        """
        self.connection.execute(
            """
            UPDATE phones SET
                full_name = ?,
                phone_number = ?,
                login = ?,
                password = ?,
                ip_address = ?,
                location = ?,
                comment = ?
            WHERE id = ?
            """,
            (*record.to_tuple(), record.id)
        )
        self.connection.commit()
        
    def delete_record(self, record_id: int):
        """
        Удаляет запись по ID.
        
        Args:
            record_id: ID записи для удаления.
        """
        self.connection.execute("DELETE FROM phones WHERE id = ?", (record_id,))
        self.connection.commit()
        
    def get_all_records(self, order_by: str = "id", ascending: bool = True) -> List[PhoneRecord]:
        """
        Получает все записи из БД.
        
        Args:
            order_by: Поле для сортировки.
            ascending: True для сортировки по возрастанию.
            
        Returns:
            Список записей.
        """
        # Защита от SQL-инъекций
        valid_columns = ["id", "full_name", "phone_number", "login", "password", 
                         "ip_address", "location", "comment"]
        if order_by not in valid_columns:
            order_by = "id"
            
        direction = "ASC" if ascending else "DESC"
        
        cursor = self.connection.execute(
            f"SELECT * FROM phones ORDER BY {order_by} {direction}"
        )
        
        return [PhoneRecord.from_row(row) for row in cursor.fetchall()]
    
    def search_records(self, search_text: str) -> List[PhoneRecord]:
        """
        Поиск записей по текстовому запросу.
        
        Args:
            search_text: Текст для поиска.
            
        Returns:
            Список найденных записей.
        """
        search_pattern = f"%{search_text}%"
        
        cursor = self.connection.execute(
            """
            SELECT * FROM phones
            WHERE full_name LIKE ? OR phone_number LIKE ? OR login LIKE ?
                OR password LIKE ? OR ip_address LIKE ? OR location LIKE ?
                OR comment LIKE ?
            ORDER BY id
            """,
            (search_pattern,) * 7
        )
        
        return [PhoneRecord.from_row(row) for row in cursor.fetchall()]
    
    def get_record_by_id(self, record_id: int) -> Optional[PhoneRecord]:
        """
        Получает запись по ID.
        
        Args:
            record_id: ID записи.
            
        Returns:
            Запись или None, если не найдена.
        """
        cursor = self.connection.execute(
            "SELECT * FROM phones WHERE id = ?", (record_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return PhoneRecord.from_row(row)
        return None
    
    def get_record_count(self) -> int:
        """
        Возвращает количество записей в БД.
        
        Returns:
            Количество записей.
        """
        cursor = self.connection.execute("SELECT COUNT(*) FROM phones")
        return cursor.fetchone()[0]
