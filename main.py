# -*- coding: utf-8 -*-
"""
АЛТАЙЦИНК - IP Phone Manager
Программа для ведения базы данных IP-телефонов.

Автор: Matrix Agent
Версия: 1.0.0
"""

import sys
import os

# Добавляем директорию программы в путь поиска модулей
if getattr(sys, 'frozen', False):
    # Запуск из exe
    application_path = os.path.dirname(sys.executable)
else:
    # Запуск из исходников
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)
os.chdir(application_path)


def main():
    """Точка входа в программу."""
    try:
        from gui import MainWindow
        
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        import tkinter.messagebox as mb
        mb.showerror(
            "Ошибка импорта",
            f"Не удалось загрузить модули программы:\n{str(e)}\n\n"
            "Проверьте, что все файлы программы находятся в одной папке."
        )
        sys.exit(1)
        
    except Exception as e:
        import tkinter.messagebox as mb
        mb.showerror(
            "Критическая ошибка",
            f"Произошла непредвиденная ошибка:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
