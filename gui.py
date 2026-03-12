# -*- coding: utf-8 -*-
"""
Главный модуль графического интерфейса.
Реализует основное окно программы на Tkinter.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from pathlib import Path
from typing import Optional, List
from config import ConfigManager
from database import DatabaseManager, PhoneRecord
from validators import DataValidator
from notes_manager import NotesManager
from pdf_export import PDFExporter


class RecordDialog(tk.Toplevel):
    """Диалоговое окно для добавления/редактирования записи."""

    def __init__(self, parent, title: str, record: Optional[PhoneRecord] = None):
        """
        Инициализация диалога.

        Args:
            parent: Родительское окно.
            title: Заголовок окна.
            record: Запись для редактирования (None для новой записи).
        """
        super().__init__(parent)
        self.title(title)
        self.result: Optional[PhoneRecord] = None
        self.record = record

        self.transient(parent)
        self.grab_set()

        self.resizable(False, False)

        self._create_widgets()
        self._fill_data()

        # Центрируем окно
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.bind("<Return>", lambda e: self._on_save())

    def _create_widgets(self):
        """Создаёт виджеты формы."""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Поля ввода
        fields = [
            ("ФИО *:  ", "full_name"),
            ("Номер *:  ", "phone_number"),
            ("Login *:  ", "login"),
            ("Password *:  ", "password"),
            ("IP-адрес *:  ", "ip_address"),
            ("Локация:  ", "location"),
        ]

        self.entries = {}

        for i, (label_text, field_name) in enumerate(fields):
            label = ttk.Label(main_frame, text=label_text)
            label.grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))

            entry = ttk.Entry(main_frame, width=40)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)
            self.entries[field_name] = entry

        # Комментарий (многострочный)
        comment_label = ttk.Label(main_frame, text="Комментарий:  ")
        comment_label.grid(row=len(fields), column=0, sticky=tk.NW, pady=5, padx=(0, 10))

        self.comment_text = tk.Text(main_frame, width=40, height=4)
        self.comment_text.grid(row=len(fields), column=1, sticky=tk.EW, pady=5)

        # Примечание об обязательных полях
        note_label = ttk.Label(main_frame, text="* - обязательные поля",
                               foreground="gray", font=("", 8))
        note_label.grid(row=len(fields) + 1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=len(fields) + 2, column=0, columnspan=2, pady=(15, 0))

        save_btn = ttk.Button(buttons_frame, text="Сохранить", command=self._on_save, width=15)
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(buttons_frame, text="Отмена", command=self._on_cancel, width=15)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # Фокус на первом поле
        self.entries["full_name"].focus_set()

    def _fill_data(self):
        """Заполняет поля данными из записи."""
        if self.record:
            self.entries["full_name"].insert(0, self.record.full_name)
            self.entries["phone_number"].insert(0, self.record.phone_number)
            self.entries["login"].insert(0, self.record.login)
            self.entries["password"].insert(0, self.record.password)
            self.entries["ip_address"].insert(0, self.record.ip_address)
            self.entries["location"].insert(0, self.record.location)
            self.comment_text.insert("1.0", self.record.comment)

    def _on_save(self):
        """Обработчик сохранения."""
        # Получаем данные
        full_name = self.entries["full_name"].get().strip()
        phone_number = self.entries["phone_number"].get().strip()
        login = self.entries["login"].get().strip()
        password = self.entries["password"].get().strip()
        ip_address = self.entries["ip_address"].get().strip()
        location = self.entries["location"].get().strip()
        comment = self.comment_text.get("1.0", tk.END).strip()

        # Валидация
        valid, errors = DataValidator.validate_record(
            full_name, phone_number, login, password, ip_address
        )

        if not valid:
            messagebox.showerror("Ошибка валидации", "\n".join(errors), parent=self)
            return

        # Создаём запись
        record_id = self.record.id if self.record else None
        self.result = PhoneRecord(
            id=record_id,
            full_name=full_name,
            phone_number=phone_number,
            login=login,
            password=password,
            ip_address=ip_address,
            location=location,
            comment=comment
        )

        self.destroy()

    def _on_cancel(self):
        """Обработчик отмены."""
        self.result = None
        self.destroy()

class NotesWindow(tk.Toplevel):
    """Окно для текстовых заметок."""
    def __init__(self, parent, notes_manager: NotesManager):
        """
        Инициализация окна заметок.
        """
        super().__init__(parent)
        self.title("АЛТАЙЦИНК - Текстовая информация ")
        self.notes_manager = notes_manager

        # ИЗМЕНЕНИЕ: Используем state('zoomed') для корректного разворачивания
        # Это учитывает панель задач, в отличие от ручного задания геометрии
        self.state('zoomed')
        self.minsize(800, 600)

        self._create_widgets()
        self._load_notes()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        """Создаёт виджеты окна."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        header_label = ttk.Label(
            main_frame,
            text="Введите дополнительную текстовую информацию:   ",
            font=("", 10, "bold")
        )
        header_label.pack(anchor=tk.W, pady=(0, 10))

        # Текстовое поле с прокруткой
        text_frame = ttk.Frame(main_frame)
        # expand=True заставляет это поле занимать всё свободное место
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10)
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)

        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        # pack без expand=True гарантирует, что кнопки останутся внизу
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        save_btn = ttk.Button(buttons_frame, text="Сохранить ", command=self._on_save, width=15)
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = ttk.Button(buttons_frame, text="Закрыть ", command=self._on_close, width=15)
        close_btn.pack(side=tk.LEFT, padx=5)

    def _load_notes(self):
        """Загружает заметки."""
        text = self.notes_manager.load_notes()
        self.text_widget.insert("1.0", text)

    def _on_save(self):
        """Сохраняет заметки."""
        text = self.text_widget.get("1.0", tk.END)
        success, message = self.notes_manager.save_notes(text)

        if success:
            messagebox.showinfo("Успех ", message, parent=self)
        else:
            messagebox.showerror("Ошибка ", message, parent=self)

    def _on_close(self):
        """Закрывает окно с предложением сохранить."""
        self.destroy()

class SearchDialog(simpledialog.Dialog):
    """Диалог поиска."""

    def __init__(self, parent):
        self.search_text = ""
        super().__init__(parent, title="Поиск")

    def body(self, master):
        ttk.Label(master, text="Введите текст для поиска:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry = ttk.Entry(master, width=40)
        self.entry.grid(row=1, column=0, pady=5)
        return self.entry

    def apply(self):
        self.search_text = self.entry.get().strip()


class SettingsDialog(tk.Toplevel):
    """Диалоговое окно настроек программы."""

    def __init__(self, parent, config_manager: ConfigManager, application_path: Path = None):
        """
        Инициализация диалога настроек.

        Args:
            parent: Родительское окно.
            config_manager: Менеджер конфигурации.
            application_path: Путь к директории приложения.
        """
        super().__init__(parent)
        self.title("Настройки программы")
        self.config_manager = config_manager
        self.application_path = application_path
        self.path_changed = False

        self.geometry("650x450")
        self.minsize(600, 400)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_current_paths()

        # Центрируем окно
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Создаёт виджеты окна настроек."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="Настройки путей к данным",
            font=("", 12, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 15))

        # Блок пути к данным (БД и Заметки)
        data_frame = ttk.LabelFrame(main_frame, text="Путь к данным (База данных и Заметки)", padding=10)
        data_frame.pack(fill=tk.X, pady=(0, 15))

        self.data_path_var = tk.StringVar()
        data_entry = ttk.Entry(data_frame, textvariable=self.data_path_var, width=60)
        data_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(data_frame, text="Обзор...", command=self._select_data_path).pack(side=tk.LEFT, padx=(10, 0))

        # Блок пути к конфигурации
        config_frame = ttk.LabelFrame(main_frame, text="Путь к файлу конфигурации", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 15))

        self.config_path_var = tk.StringVar()
        config_entry = ttk.Entry(config_frame, textvariable=self.config_path_var, width=60)
        config_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(config_frame, text="Обзор...", command=self._select_config_path).pack(side=tk.LEFT, padx=(10, 0))

        # Предупреждение
        warning_label = ttk.Label(
            main_frame,
            text="⚠ При смене пути к данным убедитесь, что файлы phonebook.db и notes.txt\n"
                 "перенесены в новую папку, либо выберите пустую папку для начала работы с нуля.",
            foreground="orange",
            wraplength=600,
            justify=tk.LEFT
        )
        warning_label.pack(anchor=tk.W, pady=(10, 0))

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame, text="Сохранить", command=self._on_save, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy, width=15).pack(side=tk.RIGHT)

    def _load_current_paths(self):
        """Загружает текущие пути в поля ввода."""
        data_path = self.config_manager.get_data_path()
        if data_path:
            self.data_path_var.set(str(data_path))

        self.config_path_var.set(str(self.config_manager.app_config_dir))

    def _select_data_path(self):
        """Открывает диалог выбора папки для данных."""
        folder = filedialog.askdirectory(
            initialdir=self.data_path_var.get(),
            title="Выберите папку для хранения данных"
        )
        if folder:
            self.data_path_var.set(folder)

    def _select_config_path(self):
        """Открывает диалог выбора папки для конфигурации."""
        folder = filedialog.askdirectory(
            initialdir=self.config_path_var.get(),
            title="Выберите папку для файла конфигурации"
        )
        if folder:
            self.config_path_var.set(folder)

    def _on_save(self):
        """Обработчик сохранения настроек."""
        # Сохраняем путь к данным
        new_data_path = self.data_path_var.get().strip()
        if new_data_path:
            new_data_path_obj = Path(new_data_path)
            if new_data_path_obj.exists() and new_data_path_obj.is_dir():
                # Проверка прав записи
                test_file = new_data_path_obj / ".write_test"
                try:
                    test_file.touch()
                    test_file.unlink()
                except (IOError, PermissionError):
                    messagebox.showerror(
                        "Ошибка",
                        f"Нет прав на запись в папку: {new_data_path}",
                        parent=self
                    )
                    return

                old_data_path = self.config_manager.get_data_path()
                if old_data_path and str(old_data_path) != new_data_path:
                    self.path_changed = True

                self.config_manager.set_data_path(new_data_path)
            else:
                messagebox.showerror(
                    "Ошибка",
                    f"Указанный путь не существует или не является папкой: {new_data_path}",
                    parent=self
                )
                return

        # Сохраняем путь к конфигурации (если изменён)
        new_config_path = self.config_path_var.get().strip()
        if new_config_path:
            new_config_path_obj = Path(new_config_path)
            old_config_path = self.config_manager.app_config_dir

            if new_config_path_obj != old_config_path:
                if new_config_path_obj.exists() and new_config_path_obj.is_dir():
                    # Проверка прав записи
                    test_file = new_config_path_obj / ".config_write_test"
                    try:
                        test_file.touch()
                        test_file.unlink()
                    except (IOError, PermissionError):
                        messagebox.showerror(
                            "Ошибка",
                            f"Нет прав на запись в папку конфигурации: {new_config_path}",
                            parent=self
                        )
                        return

                    # Копируем текущий конфиг в новую папку
                    import shutil
                    if self.config_manager.app_config_file.exists():
                        try:
                            new_config_file = new_config_path_obj / self.config_manager.CONFIG_FILENAME.strip()
                            shutil.copy2(self.config_manager.app_config_file, new_config_file)

                            # Сохраняем путь в bootstrap файл (если application_path доступен)
                            if self.application_path:
                                bootstrap_path = Path(self.application_path) / "config_location.txt"
                                bootstrap_path.write_text(str(new_config_path_obj), encoding='utf-8')

                            self.path_changed = True
                        except Exception as e:
                            messagebox.showerror(
                                "Ошибка",
                                f"Не удалось перенести файл конфигурации: {str(e)}",
                                parent=self
                            )
                            return
                else:
                    messagebox.showerror(
                        "Ошибка",
                        f"Указанный путь конфигурации не существует: {new_config_path}",
                        parent=self
                    )
                    return

        messagebox.showinfo(
            "Успех",
            "Настройки сохранены.\nПрограмма будет использовать новые пути после перезагрузки.",
            parent=self
        )
        self.destroy()


class MainWindow:
    """Главное окно приложения."""

    APP_TITLE = "АЛТАЙЦИНК - IP Phone Manager"

    def __init__(self, application_path: Path = None):
        """
        Инициализация главного окна.

        Args:
            application_path: Путь к директории приложения.
        """
        self.root = tk.Tk()
        self.root.title(self.APP_TITLE)
        self.root.geometry("1200x600")
        self.root.minsize(900, 500)

        # Путь к приложению
        self.application_path = application_path

        # Менеджеры
        self.config_manager = ConfigManager()
        self.db_manager: Optional[DatabaseManager] = None
        self.notes_manager: Optional[NotesManager] = None
        self.pdf_exporter = PDFExporter()

        # Состояние сортировки
        self.sort_column = "id"
        self.sort_ascending = True
        self.search_mode = False
        self.current_search = ""

        # Проверяем конфигурацию
        if not self._check_configuration():
            return

        self._create_widgets()
        self._setup_styles()
        self._refresh_table()

        # Центрируем окно
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"+{x}+{y}")

    def _check_configuration(self) -> bool:
        """
        Проверяет конфигурацию и запрашивает путь при необходимости.

        Returns:
            True, если конфигурация успешна.
        """
        if not self.config_manager.is_configured():
            # Первый запуск - запрашиваем путь
            messagebox.showinfo(
                "Первый запуск",
                "Добро пожаловать в АЛТАЙЦИНК IP Phone Manager!\n\n"
                "Выберите папку для хранения базы данных и настроек программы.",
                parent=self.root
            )

            if not self._select_data_folder():
                self.root.destroy()
                return False
        else:
            # Проверяем доступность пути
            valid, error_msg = self.config_manager.validate_data_path()
            if not valid:
                messagebox.showerror(
                    "Ошибка",
                    f"Папка с данными недоступна:\n{error_msg}\n\n"
                    "Выберите новую папку для данных.",
                    parent=self.root
                )
                if not self._select_data_folder():
                    self.root.destroy()
                    return False

        # Инициализируем менеджеры
        db_path = self.config_manager.get_database_path()
        notes_path = self.config_manager.get_notes_path()

        if db_path and notes_path:
            self.db_manager = DatabaseManager(db_path)
            self.db_manager.connect()

            self.notes_manager = NotesManager(notes_path)

            return True
        else:
            messagebox.showerror(
                "Ошибка",
                "Не удалось получить пути к файлам данных.",
                parent=self.root
            )
            self.root.destroy()
            return False

    def _select_data_folder(self) -> bool:
        """
        Открывает диалог выбора папки для данных.

        Returns:
            True, если папка выбрана.
        """
        folder = filedialog.askdirectory(
            title="Выберите папку для хранения данных",
            parent=self.root
        )

        if folder:
            self.config_manager.set_data_path(folder)
            return True
        return False

    def _setup_styles(self):
        """Настраивает стили виджетов."""
        style = ttk.Style()
        style.theme_use('clam')

        # Стиль для Treeview
        style.configure(
            "Treeview",
            rowheight=25,
            font=("", 9)
        )
        style.configure(
            "Treeview.Heading",
            font=("", 9, "bold")
        )

        # Стиль для кнопок
        style.configure(
            "Action.TButton",
            padding=(10, 5)
        )

    def _create_widgets(self):
        """Создаёт виджеты главного окна."""
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(
            header_frame,
            text="АЛТАЙЦИНК - База данных IP-телефонов",
            font=("", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # Статус
        self.status_label = ttk.Label(header_frame, text=" ", foreground="gray")
        self.status_label.pack(side=tk.RIGHT)

        # Панель кнопок
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))

        # ИЗМЕНЕНИЕ: Добавлена кнопка "Настройки"
        buttons = [
            ("Добавить", self._on_add),
            ("Редактировать", self._on_edit),
            ("Удалить", self._on_delete),
            ("Поиск", self._on_search),
            ("Обновить", self._on_refresh),
            ("Текстовая информация", self._on_notes),
            ("Настройки", self._on_settings),  # НОВАЯ КНОПКА
            ("Экспорт в PDF", self._on_export_pdf),
        ]

        for text, command in buttons:
            btn = ttk.Button(buttons_frame, text=text, command=command, style="Action.TButton")
            btn.pack(side=tk.LEFT, padx=(0, 5))

        # Кнопка сброса поиска
        self.reset_search_btn = ttk.Button(
            buttons_frame,
            text="Сбросить поиск",
            command=self._on_reset_search,
            style="Action.TButton"
        )

        # Таблица с прокруткой
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Прокрутка
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Таблица
        columns = ("id", "full_name", "phone_number", "login", "password",
                   "ip_address", "location", "comment")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )

        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)

        # Настройка столбцов
        column_config = {
            "id": ("№", 50),
            "full_name": ("ФИО", 150),
            "phone_number": ("Номер", 100),
            "login": ("Login", 100),
            "password": ("Password", 100),
            "ip_address": ("IP-адрес", 120),
            "location": ("Локация", 120),
            "comment": ("Комментарий", 200),
        }

        for col, (heading, width) in column_config.items():
            self.tree.heading(col, text=heading, command=lambda c=col: self._on_sort(c))
            self.tree.column(col, width=width, minwidth=50)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Двойной клик для редактирования
        self.tree.bind("<Double-1>", lambda e: self._on_edit())

        # Информационная панель
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))

        self.info_label = ttk.Label(info_frame, text=" ", foreground="gray")
        self.info_label.pack(side=tk.LEFT)

        # Путь к данным
        data_path = self.config_manager.get_data_path()
        self.path_label = ttk.Label(info_frame, text=f"Данные: {data_path}", foreground="gray")
        self.path_label.pack(side=tk.RIGHT)

    def _refresh_table(self):
        """Обновляет данные в таблице."""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Загружаем записи
        if self.search_mode and self.current_search:
            records = self.db_manager.search_records(self.current_search)
            self.status_label.config(text=f"Поиск: '{self.current_search}'")
            self.reset_search_btn.pack(side=tk.LEFT, padx=(10, 0))
        else:
            records = self.db_manager.get_all_records(self.sort_column, self.sort_ascending)
            self.status_label.config(text=" ")
            self.reset_search_btn.pack_forget()

        # Заполняем таблицу
        for record in records:
            values = (
                record.id,
                record.full_name,
                record.phone_number,
                record.login,
                record.password,
                record.ip_address,
                record.location,
                record.comment[:50] + "..." if len(record.comment) > 50 else record.comment
            )
            self.tree.insert("", tk.END, values=values)

        # Обновляем информацию
        total = self.db_manager.get_record_count()
        shown = len(records)

        if self.search_mode:
            self.info_label.config(text=f"Найдено записей: {shown} из {total}")
        else:
            self.info_label.config(text=f"Всего записей: {total}")

    def _get_selected_record_id(self) -> Optional[int]:
        """Возвращает ID выбранной записи."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return item["values"][0]
        return None

    def _on_add(self):
        """Обработчик добавления записи."""
        dialog = RecordDialog(self.root, "Добавить запись")
        self.root.wait_window(dialog)

        if dialog.result:
            self.db_manager.add_record(dialog.result)
            self._refresh_table()
            messagebox.showinfo("Успех", "Запись успешно добавлена!", parent=self.root)

    def _on_edit(self):
        """Обработчик редактирования записи."""
        record_id = self._get_selected_record_id()

        if not record_id:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования.", parent=self.root)
            return

        record = self.db_manager.get_record_by_id(record_id)

        if record:
            dialog = RecordDialog(self.root, "Редактировать запись", record)
            self.root.wait_window(dialog)

            if dialog.result:
                self.db_manager.update_record(dialog.result)
                self._refresh_table()
                messagebox.showinfo("Успех", "Запись успешно обновлена!", parent=self.root)

    def _on_delete(self):
        """Обработчик удаления записи."""
        record_id = self._get_selected_record_id()

        if not record_id:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.", parent=self.root)
            return

        # Подтверждение удаления
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить выбранную запись?\n\nЭто действие нельзя отменить.",
            parent=self.root
        )

        if confirm:
            self.db_manager.delete_record(record_id)
            self._refresh_table()
            messagebox.showinfo("Успех", "Запись удалена.", parent=self.root)

    def _on_search(self):
        """Обработчик поиска."""
        dialog = SearchDialog(self.root)

        if dialog.search_text:
            self.search_mode = True
            self.current_search = dialog.search_text
            self._refresh_table()

    def _on_reset_search(self):
        """Сбрасывает режим поиска."""
        self.search_mode = False
        self.current_search = ""
        self._refresh_table()

    def _on_refresh(self):
        """Обновляет таблицу."""
        self._refresh_table()

    def _on_sort(self, column: str):
        """Обработчик сортировки по столбцу."""
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True

        self._refresh_table()

    def _on_notes(self):
        """Открывает окно заметок."""
        NotesWindow(self.root, self.notes_manager)

    def _on_settings(self):
        """Открывает окно настроек."""
        dialog = SettingsDialog(self.root, self.config_manager, self.application_path)
        self.root.wait_window(dialog)

        # Если путь к данным изменился, нужно переподключить менеджеры
        if dialog.path_changed:
            self._reload_managers()

    def _reload_managers(self):
        """Пересоздает менеджеры БД и заметок после смены пути."""
        # Закрываем текущее соединение с БД
        if self.db_manager:
            self.db_manager.close()

        # Получаем новые пути
        db_path = self.config_manager.get_database_path()
        notes_path = self.config_manager.get_notes_path()

        if db_path and notes_path:
            # Создаём новые менеджеры
            self.db_manager = DatabaseManager(db_path)
            self.db_manager.connect()

            self.notes_manager = NotesManager(notes_path)

            # Обновляем таблицу и лейбл пути
            self._refresh_table()

            data_path = self.config_manager.get_data_path()
            self.path_label.config(text=f"Данные: {data_path}")

            messagebox.showinfo(
                "Успех",
                "Пути обновлены. Программа переподключена к новым файлам.",
                parent=self.root
            )
        else:
            messagebox.showerror(
                "Ошибка",
                "Не удалось получить пути к данным после обновления.",
                parent=self.root
            )
            self.root.destroy()

    def _on_export_pdf(self):
        """Экспортирует данные в PDF."""
        # Выбираем файл для сохранения
        file_path = filedialog.asksaveasfilename(
            title="Сохранить PDF",
            defaultextension=".pdf",
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")],
            initialfile="altayzinc_phones_export.pdf",
            parent=self.root
        )

        if not file_path:
            return

        # Проверяем статус шрифта
        font_ok, font_name = self.pdf_exporter.get_font_status()

        if not font_ok:
            messagebox.showwarning(
                "Предупреждение",
                "Шрифт с поддержкой русского языка не найден.\n"
                "PDF будет создан, но русские символы могут отображаться некорректно.\n\n"
                "Для корректного отображения поместите файл DejaVuSans.ttf  "
                "в папку fonts рядом с программой.",
                parent=self.root
            )

        # Получаем данные
        records = self.db_manager.get_all_records()
        notes_text = self.notes_manager.load_notes()

        # Экспортируем
        success, message = self.pdf_exporter.export_to_pdf(
            Path(file_path), records, notes_text
        )

        if success:
            messagebox.showinfo("Успех", message, parent=self.root)
        else:
            messagebox.showerror("Ошибка", message, parent=self.root)

    def run(self):
        """Запускает главный цикл приложения."""
        if self.db_manager is None:
            return  # Если инициализация не прошла успешно
        self.root.mainloop()

        # Закрываем соединение с БД
        if self.db_manager:
            self.db_manager.close()


if __name__ == "__main__":
    app = MainWindow()
    app.run()