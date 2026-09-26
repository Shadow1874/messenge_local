import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from network import MessengerNetwork
from SQL import get_users


BLUE = "#1976D2"
DARK_BLUE = "#1565C0"

BG_COLOR = "#F4F6F8"
PANEL_COLOR = "#E8EDF3"
LIGHT_BLUE = "#E3F2FD"

TEXT_COLOR = "#222222"


class MessengerGUI:
    def __init__(self):
        self.network = MessengerNetwork()

        self.network.on_message = \
            self.receive_message

        self.network.on_file = \
            self.receive_file

        self.network.on_disconnect = \
            self.disconnected

        self.root = tk.Tk()

        self.root.title(
            "Корпоративный мессенджер"
        )

        self.root.geometry(
            "1280x720"
        )

        self.root.configure(
            bg=BG_COLOR
        )

        self.create_interface()

    # ---------------- INTERFACE ----------------

    def create_interface(self):
        left = tk.Frame(
            self.root,
            width=300,
            bg=PANEL_COLOR
        )

        left.pack(
            side="left",
            fill="y"
        )

        right = tk.Frame(
            self.root,
            bg=BG_COLOR
        )

        right.pack(
            side="right",
            fill="both",
            expand=True
        )

        title = tk.Label(
            left,
            text="Мессенджер",
            font=(
                "Arial",
                18,
                "bold"
            ),
            bg=PANEL_COLOR,
            fg=BLUE
        )

        title.pack(
            pady=15
        )

        # Имя

        tk.Label(
            left,
            text="Имя пользователя",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR
        ).pack(
            pady=5
        )

        self.name_entry = tk.Entry(
            left
        )

        self.name_entry.pack(
            padx=10,
            fill="x"
        )

        # IP

        tk.Label(
            left,
            text="IP адрес",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR
        ).pack(
            pady=5
        )

        self.ip_entry = tk.Entry(
            left
        )

        self.ip_entry.pack(
            padx=10,
            fill="x"
        )

        # Порт

        tk.Label(
            left,
            text="Порт",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR
        ).pack(
            pady=5
        )

        self.port_entry = tk.Entry(
            left
        )

        self.port_entry.insert(
            0,
            "8080"
        )

        self.port_entry.pack(
            padx=10,
            fill="x"
        )

        # Сервер

        tk.Button(
            left,
            text="Запустить сервер",
            command=self.start_server,
            bg=DARK_BLUE,
            fg="white",
            activebackground=BLUE,
            activeforeground="white"
        ).pack(
            padx=10,
            pady=10,
            fill="x"
        )

        # Подключение

        tk.Button(
            left,
            text="Подключиться",
            command=self.connect,
            bg=BLUE,
            fg="white",
            activebackground=DARK_BLUE,
            activeforeground="white"
        ).pack(
            padx=10,
            pady=5,
            fill="x"
        )

        # Старые IP

        tk.Button(
            left,
            text="Старые IP",
            command=self.show_old_ips,
            bg=BLUE,
            fg="white",
            activebackground=DARK_BLUE,
            activeforeground="white"
        ).pack(
            padx=10,
            pady=10,
            fill="x"
        )

        # Область чата

        self.chat = tk.Text(
            right,
            state="disabled",
            bg="white",
            fg=TEXT_COLOR,
            insertbackground=BLUE,
            font=(
                "Arial",
                11
            )
        )

        self.chat.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Нижняя панель

        bottom = tk.Frame(
            right,
            bg=BG_COLOR
        )

        bottom.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.message_entry = tk.Entry(
            bottom,
            bg="white",
            fg=TEXT_COLOR,
            insertbackground=BLUE,
            font=(
                "Arial",
                11
            )
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=6
        )

        self.message_entry.bind(
            "<Return>",
            lambda event:
            self.send_message()
        )

        tk.Button(
            bottom,
            text="Отправить",
            command=self.send_message,
            bg=BLUE,
            fg="white",
            activebackground=DARK_BLUE,
            activeforeground="white"
        ).pack(
            side="right",
            padx=5
        )

        tk.Button(
            right,
            text="Отправить файл",
            command=self.send_file,
            bg=LIGHT_BLUE,
            fg=TEXT_COLOR,
            activebackground="#BBDEFB"
        ).pack(
            pady=5
        )

    # ---------------- SERVER ----------------

    def start_server(self):
        name = \
            self.name_entry.get().strip()

        if not name:
            messagebox.showerror(
                "Ошибка",
                "Введите имя"
            )
            return
        try:

            port = int(
                self.port_entry.get()
            )

            self.network.start_server(
                name,
                port
            )

            self.add_message(
                f"Сервер запущен на порту {port}"
            )
        except Exception as error:
            messagebox.showerror(
                "Ошибка",
                str(error)
            )

    # ---------------- CONNECT ----------------

    def connect(self):
        name = \
            self.name_entry.get().strip()

        ip = \
            self.ip_entry.get().strip()

        port_text = \
            self.port_entry.get().strip()
        if not name or not ip or not port_text:

            messagebox.showerror("Ошибка", "Заполните все поля" )
            return
        try:

            port = int(
                port_text
            )

            self.network.connect(
                ip,
                port,
                name
            )

            self.add_message(
                "Подключение выполнено"
            )

            # Автоматическая загрузка
            # старой переписки

            history = \
                self.network.load_history(
                    ip,
                    port
                )

            if history:
                self.add_message(
                    history.rstrip()
                )
        except Exception as error:

            messagebox.showerror(
                "Ошибка подключения",
                str(error)
            )

    # ---------------- OLD IP ----------------

    def show_old_ips(self):
        users = get_users()

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Ранее подключенные"
        )

        window.geometry(
            "350x400"
        )

        window.configure(
            bg=BG_COLOR
        )

        tk.Label(
            window,
            text="Ранее подключенные IP",
            font=(
                "Arial",
                14,
                "bold"
            ),
            bg=BG_COLOR,
            fg=BLUE
        ).pack(
            pady=10
        )

        listbox = tk.Listbox(
            window,
            font=(
                "Arial",
                11
            ),
            bg="white",
            fg=TEXT_COLOR,
            selectbackground=BLUE,
            selectforeground="white"
        )

        listbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        for ip, port in users:
            listbox.insert(
                tk.END,
                f"{ip}:{port}"
            )

        def select_user(event):
            selection = \
                listbox.curselection()
            if not selection:
                return

            text = \
                listbox.get(
                    selection[0]
                )

            ip, port = \
                text.rsplit(
                    ":",
                    1
                )

            self.ip_entry.delete(
                0,
                tk.END
            )

            self.ip_entry.insert(
                0,
                ip
            )

            self.port_entry.delete(
                0,
                tk.END
            )

            self.port_entry.insert(
                0,
                port
            )

            window.destroy()

        listbox.bind(
            "<Double-Button-1>",
            select_user
        )

    # ---------------- MESSAGE ----------------

    def send_message(self):
        message = \
            self.message_entry.get().strip()
        if not message:
            return

        name = \
            self.name_entry.get().strip()

        if not name:
            messagebox.showerror(
                "Ошибка",
                "Введите имя пользователя"
            )
            return

        self.network.send_text(
            name,
            message
        )

        self.add_message(
            f"{name}: {message}"
        )

        self.message_entry.delete(
            0,
            tk.END
        )

    def receive_message(
        self,
        message
    ):

        self.root.after(
            0,
            lambda:
            self.add_message(
                message
            )
        )

    # ---------------- FILE ----------------

    def send_file(self):
        filepath = \
            filedialog.askopenfilename()

        if not filepath:
            return

        self.network.send_file(
            filepath
        )

        self.add_message(
            "Файл отправлен: " +
            filepath
        )

    def receive_file(
        self,
        filename,
        path
    ):

        self.root.after(
            0,
            lambda:
            self.add_message(
                "Файл получен: " +
                filename
            )
        )

    # ---------------- CHAT ----------------

    def add_message(
        self,
        message
    ):

        self.chat.config(
            state="normal"
        )

        self.chat.insert(
            tk.END,
            message + "\n"
        )

        self.chat.config(
            state="disabled"
        )

        self.chat.see(
            tk.END
        )

    # ---------------- DISCONNECT ----------------

    def disconnected(self):
        self.root.after(
            0,
            lambda:
            self.add_message(
                "Соединение закрыто"
            )
        )

    # ---------------- CLOSE ----------------

    def close(self):
        self.network.close()
        self.root.destroy()

    # ---------------- RUN ----------------

    def run(self):
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.root.mainloop()