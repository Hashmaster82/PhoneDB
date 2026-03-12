@echo off
chcp 65001 >nul
title АЛТАЙЦИНК - IP Phone Manager

echo ============================================
echo   АЛТАЙЦИНК - IP Phone Manager
echo   Запуск программы
echo ============================================
echo.

:: Переход в директорию скрипта
cd /d "%~dp0"

:: Проверка наличия Python
echo [1/4] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден в системе!
    echo.
    echo Установите Python с официального сайта:
    echo https://www.python.org/downloads/
    echo.
    echo Не забудьте отметить "Add Python to PATH" при установке.
    echo.
    pause
    exit /b 1
)
echo [OK] Python найден

:: Проверка наличия Git
echo [2/4] Проверка Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ВНИМАНИЕ] Git не найден. Проверка обновлений пропущена.
    echo Для автоматических обновлений установите Git:
    echo https://git-scm.com/download/win
    echo.
    goto :install_deps
)
echo [OK] Git найден

:: Проверка обновлений
echo [3/4] Проверка обновлений...

:: Проверяем, инициализирован ли git репозиторий
if not exist ".git" (
    echo Инициализация репозитория...
    git init >nul 2>&1
    git remote add origin https://github.com/Hashmaster82/PhoneDB.git >nul 2>&1
)

:: Получаем информацию об обновлениях
git fetch origin main >nul 2>&1
if errorlevel 1 (
    git fetch origin master >nul 2>&1
)

:: Проверяем, есть ли новые коммиты
for /f %%i in ('git rev-parse HEAD 2^>nul') do set LOCAL_COMMIT=%%i
for /f %%i in ('git rev-parse origin/main 2^>nul') do set REMOTE_COMMIT=%%i

if "%REMOTE_COMMIT%"=="" (
    for /f %%i in ('git rev-parse origin/master 2^>nul') do set REMOTE_COMMIT=%%i
)

if not "%LOCAL_COMMIT%"=="%REMOTE_COMMIT%" (
    if not "%REMOTE_COMMIT%"=="" (
        echo.
        echo [!] Доступно обновление!
        echo.
        set /p UPDATE_CHOICE="Обновить программу? (Y/N): "
        if /i "%UPDATE_CHOICE%"=="Y" (
            echo Загрузка обновлений...
            git pull origin main 2>nul || git pull origin master 2>nul
            if errorlevel 1 (
                echo [ОШИБКА] Не удалось загрузить обновления.
            ) else (
                echo [OK] Обновление завершено!
            )
        ) else (
            echo Обновление пропущено.
        )
    )
) else (
    echo [OK] Установлена последняя версия
)

:install_deps
:: Проверка и установка зависимостей
echo [4/4] Проверка зависимостей...

python -c "import reportlab" >nul 2>&1
if errorlevel 1 (
    echo Установка reportlab...
    pip install reportlab >nul 2>&1
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить reportlab
        echo Попробуйте вручную: pip install reportlab
        pause
        exit /b 1
    )
    echo [OK] reportlab установлен
) else (
    echo [OK] Зависимости установлены
)

:: Запуск программы
echo.
echo ============================================
echo   Запуск АЛТАЙЦИНК IP Phone Manager...
echo ============================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Программа завершилась с ошибкой.
    pause
)
