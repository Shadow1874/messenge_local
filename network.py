import socket
import threading
import os

from SQL import save_user


DEFAULT_PORT = 8080

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SAVE_DIR = os.path.join(
    BASE_DIR,
    "received"
)

CHAT_DIR = os.path.join(
    BASE_DIR,
    "chats"
)

os.makedirs(
    SAVE_DIR,
    exist_ok=True
)

os.makedirs(
    CHAT_DIR,
    exist_ok=True
)


class MessengerNetwork:

    def __init__(self):
        self.server = None
        self.sock = None

        self.clients = []
        self.clients_lock = threading.Lock()

        self.server_running = False
        self.client_running = False

        self.username = ""

        self.server_port = 0

        self.partner_ip = ""
        self.partner_port = 0

        self.on_message = None
        self.on_file = None
        self.on_disconnect = None

    # ================= SERVER =================

    def start_server(
        self,
        name,
        port=DEFAULT_PORT
    ):

        self.username = name
        self.server_port = port

        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server.bind(
            ("0.0.0.0", port)
        )

        self.server.listen(10)
        self.server_running = True

        thread = threading.Thread(
            target=self.accept_connections,
            daemon=True
        )
        thread.start()

    def accept_connections(self):
        while self.server_running:
            try:
                client, address = self.server.accept()
                user = {
                    "socket": client,
                    "ip": address[0],
                    "port": 0,
                    "name": ""
                }

                with self.clients_lock:
                    self.clients.append(
                        user
                    )

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(
                        client,
                        address
                    ),
                    daemon=True
                )

                thread.start()

            except OSError:
                break

            except Exception as error:
                print(
                    "Ошибка подключения:",
                    error
                )

    # ================= CLIENT =================

    def connect(
        self,
        ip,
        port,
        name
    ):

        self.username = name

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.sock.connect(
            (
                ip,
                int(port)
            )
        )

        self.partner_ip = ip
        self.partner_port = int(port)

        self.client_running = True

        save_user(
            ip,
            int(port)
        )

        handshake = (
            f"USER|{name}|{self.server_port}\n"
        ).encode(
            "utf-8"
        )

        self.sock.sendall(
            handshake
        )

        thread = threading.Thread(
            target=self.receive_loop,
            args=(
                self.sock,
                (
                    ip,
                    int(port)
                )
            ),
            daemon=True
        )
        thread.start()

    # ================= SERVER CLIENT =================

    def handle_client(
        self,
        client,
        address
    ):
        name = ""
        port = 0

        try:
            header = self.recv_line(
                client
            )

            if header.startswith("USER|"):
                parts = header.split(
                    "|"
                )

                if len(parts) >= 3:
                    name = parts[1]

                    try:
                        port = int(
                            parts[2]
                        )

                    except:
                        port = 0

            with self.clients_lock:
                for user in self.clients:
                    if user["socket"] == client:
                        user["name"] = name
                        user["port"] = port
                        break

            if port > 0:

                save_user(
                    address[0],
                    port
                )

            while self.server_running:

                header = self.recv_line(
                    client
                )

                if not header:
                    break

                # ---------- MESSAGE ----------

                if header.startswith("TEXT|"):
                    message = header[5:]
                    history_port = port

                    if history_port == 0:
                        history_port = (
                            address[1]
                        )

                    self.save_history(
                        address[0],
                        history_port,
                        message
                    )

                    if self.on_message:
                        self.on_message(
                            message
                        )

                    self.broadcast(
                        client,
                        header.encode(
                            "utf-8"
                        )
                    )

                # ---------- FILE ----------

                elif header.startswith("FILE|"):
                    parts = header.split(
                        "|",
                        2
                    )

                    if len(parts) != 3:
                        continue

                    filename = parts[1]

                    try:
                        size = int(
                            parts[2]
                        )
                    except:
                        continue

                    file_data = self.receive_file_data(
                        client,
                        size
                    )

                    saved_name = self.save_received_file(
                        filename,
                        file_data
                    )

                    message = (
                        "Получен файл: " +
                        saved_name
                    )

                    history_port = port

                    if history_port == 0:
                        history_port = (
                            address[1]
                        )

                    self.save_history(
                        address[0],
                        history_port,
                        message
                    )

                    if self.on_file:
                        self.on_file(
                            saved_name,
                            os.path.join(
                                SAVE_DIR,
                                saved_name
                            )
                        )

                    if self.on_message:
                        self.on_message(
                            message
                        )

                    self.broadcast_file(
                        client,
                        filename,
                        file_data
                    )

        except Exception as error:
            print(
                "Ошибка клиента:",
                error
            )

        self.remove_client(
            client
        )

        try:
            client.close()
        except:
            pass
        if self.on_disconnect:
            self.on_disconnect()

    # ================= RECEIVE CLIENT =================

    def receive_loop(
        self,
        sock,
        address
    ):

        while self.client_running:
            try:
                header = self.recv_line(
                    sock
                )
                if not header:
                    break

                # ---------- MESSAGE ----------

                if header.startswith("TEXT|"):
                    message = header[5:]

                    self.save_history(
                        address[0],
                        address[1],
                        message
                    )

                    if self.on_message:
                        self.on_message(
                            message
                        )

                # ---------- FILE ----------

                elif header.startswith("FILE|"):
                    parts = header.split(
                        "|",
                        2
                    )

                    if len(parts) != 3:
                        continue

                    filename = parts[1]

                    try:
                        size = int(
                            parts[2]
                        )
                    except:
                        continue

                    file_data = self.receive_file_data(
                        sock,
                        size
                    )

                    saved_name = self.save_received_file(
                        filename,
                        file_data
                    )

                    message = (
                        "Получен файл: " +
                        saved_name
                    )

                    self.save_history(
                        address[0],
                        address[1],
                        message
                    )

                    if self.on_file:
                        self.on_file(
                            saved_name,
                            os.path.join(
                                SAVE_DIR,
                                saved_name
                            )
                        )
                    if self.on_message:
                        self.on_message(
                            message
                        )
            except Exception as error:
                print(
                    "Ошибка получения:",
                    error
                )
                break

        if self.on_disconnect:

            self.on_disconnect()

    # ================= RECEIVE LINE =================

    def recv_line(
        self,
        sock
    ):

        data = b""

        while True:
            part = sock.recv(1)

            if not part:
                raise ConnectionError(
                    "Соединение закрыто"
                )
            if part == b"\n":
                break
            data += part
        return data.decode(
            "utf-8"
        )

    # ================= RECEIVE FILE DATA =================

    def receive_file_data(
        self,
        sock,
        size
    ):
        data = b""

        while len(data) < size:
            part = sock.recv(
                min(
                    4096,
                    size - len(data)
                )
            )

            if not part:
                raise ConnectionError(
                    "Соединение закрыто во время передачи файла"
                )
            data += part
        return data

    # ================= SEND MESSAGE =================

    def send_text(
        self,
        sender,
        message
    ):

        text = (
            f"{sender}: {message}"
        )

        data = (
                "TEXT|" + text + "\n"
        ).encode(
            "utf-8"
        )

        if self.sock:
            try:
                self.sock.sendall(
                    data
                )

                self.save_history(
                    self.partner_ip,
                    self.partner_port,
                    text
                )
            except Exception as error:
                print(
                    "Ошибка отправки:",
                    error
                )

    # ================= BROADCAST =================

    def broadcast(
        self,
        sender_socket,
        data
    ):

        with self.clients_lock:
            clients = list(
                self.clients
            )

        for user in clients:
            client = user["socket"]

            if client == sender_socket:

                continue
            try:
                client.sendall(
                    data
                )
            except:
                self.remove_client(
                    client
                )

    # ================= SEND FILE =================

    def send_file(
        self,
        filepath
    ):

        if not os.path.exists(
            filepath
        ):
            return

        filename = os.path.basename(
            filepath
        )

        with open(
            filepath,
            "rb"
        ) as file:
            file_data = file.read()

        size = len(
            file_data
        )

        header = (
            f"FILE|{filename}|{size}\n"
        ).encode(
            "utf-8"
        )

        if self.sock:
            try:
                self.sock.sendall(
                    header
                )
                self.sock.sendall(
                    file_data
                )

            except Exception as error:
                print(
                    "Ошибка отправки файла:",
                    error
                )

    # ================= BROADCAST FILE =================

    def broadcast_file(
        self,
        sender_socket,
        filename,
        file_data
    ):

        header = (
            f"FILE|{filename}|"
            f"{len(file_data)}\n"
        ).encode(
            "utf-8"
        )

        with self.clients_lock:
            clients = list(
                self.clients
            )

        for user in clients:
            client = user["socket"]

            if client == sender_socket:
                continue
            try:
                client.sendall(
                    header
                )

                client.sendall(
                    file_data
                )
            except:
                self.remove_client(
                    client
                )

    # ================= SAVE FILE =================

    def save_received_file(
        self,
        filename,
        data
    ):

        safe_name = os.path.basename(
            filename
        )

        path = self.get_unique_filename(
            safe_name
        )

        with open(
            path,
            "wb"
        ) as file:

            file.write(
                data
            )

        return os.path.basename(
            path
        )

    # ================= UNIQUE FILE NAME =================

    def get_unique_filename(
        self,
        filename
    ):

        name, extension = os.path.splitext(
            filename
        )

        path = os.path.join(
            SAVE_DIR,
            filename
        )

        number = 1

        while os.path.exists(
            path
        ):

            new_name = (
                f"{name}_{number}"
                f"{extension}"
            )

            path = os.path.join(
                SAVE_DIR,
                new_name
            )
            number += 1
        return path

    # ================= HISTORY =================

    def get_history_path(
        self,
        ip,
        port
    ):

        filename = (
            f"{ip}_{port}.txt"
        )

        return os.path.join(
            CHAT_DIR,
            filename
        )

    def save_history(
        self,
        ip,
        port,
        message
    ):

        if not ip or not port:
            return

        path = self.get_history_path(
            ip,
            port
        )

        with open(
            path,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                message + "\n"
            )

    def load_history(
        self,
        ip,
        port
    ):

        path = self.get_history_path(
            ip,
            port
        )

        if not os.path.exists(
            path
        ):
            return ""

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()

    # ================= REMOVE CLIENT =================

    def remove_client(
        self,
        sock
    ):
        with self.clients_lock:
            for user in self.clients:
                if user["socket"] == sock:
                    self.clients.remove(
                        user
                    )
                    break
        try:
            sock.close()
        except:
            pass

    # ================= CLOSE =================

    def close(self):

        self.server_running = False
        self.client_running = False

        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

        if self.server:
            try:
                self.server.close()
            except:
                pass
            self.server = None

        with self.clients_lock:
            clients = list(
                self.clients
            )
            self.clients.clear()

        for user in clients:
            try:
                user["socket"].close()
            except:
                pass