# -*- coding: utf-8 -*-
"""
Модуль валидации данных.
Проверяет корректность вводимых данных.
"""

import re
from typing import Tuple, List


class DataValidator:
    """Класс для валидации данных записей."""
    
    # Регулярное выражение для проверки IP-адреса
    IP_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    @classmethod
    def validate_ip_address(cls, ip: str) -> Tuple[bool, str]:
        """
        Проверяет корректность IP-адреса.
        
        Args:
            ip: IP-адрес для проверки.
            
        Returns:
            Кортеж (валидность, сообщение об ошибке).
        """
        ip = ip.strip()
        
        if not ip:
            return False, "IP-адрес не может быть пустым."
        
        if not cls.IP_PATTERN.match(ip):
            return False, f"Некорректный формат IP-адреса: {ip}\nОжидается формат: xxx.xxx.xxx.xxx"
        
        return True, ""
    
    @classmethod
    def validate_required_field(cls, value: str, field_name: str) -> Tuple[bool, str]:
        """
        Проверяет, что обязательное поле заполнено.
        
        Args:
            value: Значение поля.
            field_name: Название поля для сообщения об ошибке.
            
        Returns:
            Кортеж (валидность, сообщение об ошибке).
        """
        if not value or not value.strip():
            return False, f"Поле '{field_name}' не может быть пустым."
        
        return True, ""
    
    @classmethod
    def validate_phone_number(cls, phone: str) -> Tuple[bool, str]:
        """
        Проверяет корректность номера телефона.
        
        Args:
            phone: Номер телефона для проверки.
            
        Returns:
            Кортеж (валидность, сообщение об ошибке).
        """
        phone = phone.strip()
        
        if not phone:
            return False, "Номер телефона не может быть пустым."
        
        # Разрешаем цифры, пробелы, дефисы, скобки и плюс
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        if not cleaned.isdigit():
            return False, "Номер телефона должен содержать только цифры и допустимые символы (+, -, пробел, скобки)."
        
        return True, ""
    
    @classmethod
    def validate_record(cls, full_name: str, phone_number: str, login: str, 
                       password: str, ip_address: str) -> Tuple[bool, List[str]]:
        """
        Полная валидация записи.
        
        Args:
            full_name: ФИО.
            phone_number: Номер телефона.
            login: Логин.
            password: Пароль.
            ip_address: IP-адрес.
            
        Returns:
            Кортеж (успех, список ошибок).
        """
        errors = []
        
        # Проверка обязательных полей
        valid, msg = cls.validate_required_field(full_name, "ФИО")
        if not valid:
            errors.append(msg)
            
        valid, msg = cls.validate_phone_number(phone_number)
        if not valid:
            errors.append(msg)
            
        valid, msg = cls.validate_required_field(login, "Login")
        if not valid:
            errors.append(msg)
            
        valid, msg = cls.validate_required_field(password, "Password")
        if not valid:
            errors.append(msg)
            
        valid, msg = cls.validate_ip_address(ip_address)
        if not valid:
            errors.append(msg)
        
        return len(errors) == 0, errors
