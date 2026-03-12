# АЛТАЙЦИНК - IP Phone Manager

Программа для ведения базы данных логинов и паролей стационарных IP-телефонов компании АЛТАЙЦИНК.

## Возможности

- ✅ Добавление, редактирование и удаление записей о телефонах
- ✅ Поиск и фильтрация по всем полям
- ✅ Сортировка по любому столбцу
- ✅ Хранение дополнительной текстовой информации
- ✅ Экспорт базы данных в PDF
- ✅ Валидация IP-адресов и обязательных полей
- ✅ Выбор папки для хранения данных при первом запуске

## Структура данных

Каждая запись содержит:
- ФИО
- Номер телефона
- Login
- Password
- IP-адрес
- Локация
- Комментарий

## Требования

- Python 3.10 или выше
- Windows 10/11

## Установка зависимостей

```bash
pip install reportlab
```

Или из файла requirements.txt:

```bash
pip install -r requirements.txt
```

## Запуск программы

```bash
python main.py
```

## Первый запуск

При первом запуске программа попросит выбрать папку для хранения данных. В этой папке будут созданы:
- `phonebook.db` — база данных SQLite
- `notes.txt` — файл с текстовой информацией

Настройки программы хранятся в домашней директории пользователя:
- `%USERPROFILE%\.altayzinc_phonebook\altayzinc_phonebook_config.json`

## Поддержка русского языка в PDF

Для корректного отображения русских символов в PDF необходим шрифт DejaVuSans.

### Варианты установки шрифта:

1. **Создайте папку `fonts`** в директории программы и поместите туда файл `DejaVuSans.ttf`

2. **Скачайте шрифт** с официального сайта: https://dejavu-fonts.github.io/

3. **Или установите шрифт в систему** — скопируйте `DejaVuSans.ttf` в `C:\Windows\Fonts`

Программа автоматически найдёт шрифт в одном из этих мест.

## Сборка в EXE

### Установка PyInstaller:

```bash
pip install pyinstaller
```

### Сборка:

```bash
pyinstaller --onefile --windowed --name "AltayZinc_PhoneManager" --icon=icon.ico main.py
```

Или для сборки с папкой (быстрее запускается):

```bash
pyinstaller --onedir --windowed --name "AltayZinc_PhoneManager" main.py
```

### Сборка со всеми модулями:

```bash
pyinstaller --onefile --windowed ^
    --name "AltayZinc_PhoneManager" ^
    --add-data "fonts;fonts" ^
    --hidden-import=reportlab ^
    --hidden-import=reportlab.lib ^
    --hidden-import=reportlab.platypus ^
    main.py
```

После сборки исполняемый файл будет в папке `dist`.

**Важно:** Если используете шрифт DejaVuSans, поместите папку `fonts` рядом с exe-файлом или установите шрифт в систему.

## Структура проекта

```
altayzinc_phonebook/
├── main.py           # Точка входа
├── gui.py            # Графический интерфейс
├── database.py       # Работа с SQLite
├── config.py         # Управление настройками
├── validators.py     # Валидация данных
├── notes_manager.py  # Управление заметками
├── pdf_export.py     # Экспорт в PDF
├── requirements.txt  # Зависимости
├── README.md         # Документация
└── fonts/            # Папка для шрифтов (опционально)
    └── DejaVuSans.ttf
```

## Автор

Matrix Agent

## Лицензия

Свободное использование для внутренних нужд компании АЛТАЙЦИНК.
