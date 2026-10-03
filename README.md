# Корпоративный мессенджер / Local Messenger

## 🇷🇺 Русская версия

### О проекте

**Корпоративный мессенджер** — это приложение для обмена текстовыми сообщениями и файлами между пользователями в локальной сети.

Программа разработана на языке **Python** с использованием библиотеки **Tkinter** для графического интерфейса, **Socket** для сетевого обмена и **SQLite** для хранения информации о ранее подключенных устройствах.

Приложение может работать как **сервер и клиент**. Сервер принимает подключения от других пользователей, а клиент может подключаться к запущенному серверу по IP-адресу и порту.

### Основные возможности

- запуск собственного TCP-сервера;
- подключение к другому пользователю по IP-адресу и порту;
- обмен текстовыми сообщениями;
- отправка файлов;
- получение файлов;
- работа нескольких подключений к серверу;
- сохранение ранее использованных IP-адресов и портов;
- просмотр списка ранее подключенных устройств;
- сохранение истории сообщений;
- автоматическое создание папок для полученных файлов и истории;
- графический интерфейс на Tkinter;
- работа в локальной сети.

### Используемые технологии

- **Python 3**
- **Tkinter** — графический интерфейс;
- **Socket / TCP** — сетевое соединение;
- **Threading** — обработка нескольких подключений;
- **SQLite** — хранение IP-адресов и портов;
- **OS** — работа с файлами и папками.

### Структура проекта

```text
messenge_local/
│
├── main.py          # Запуск приложения
├── gui.py           # Графический интерфейс
├── network.py       # Сетевая логика и обмен данными
├── SQL.py           # Работа с базой данных SQLite
├── users.db         # База данных подключений
│
├── received/        # Полученные файлы
└── chats/           # История переписок
```

### Установка

Для запуска проекта необходимо установить **Python 3**.

Проверить установку Python можно командой:

```bash
python --version
```

После этого необходимо перейти в папку проекта:

```bash
cd путь_к_проекту
```

Дополнительные библиотеки устанавливать не требуется, так как используемые модули входят в стандартную библиотеку Python.

### Запуск

Для запуска приложения выполните:

```bash
python main.py
```

После запуска появится графическое окно мессенджера.

### Подключение пользователей

Для работы двух компьютеров в одной локальной сети необходимо:

1. Запустить программу на первом компьютере.
2. Ввести имя пользователя.
3. Указать порт, например `8080`.
4. Нажать **«Запустить сервер»**.
5. На втором компьютере запустить программу.
6. Ввести имя пользователя.
7. В поле IP указать локальный IP первого компьютера.
8. Указать тот же порт.
9. Нажать **«Подключиться»**.

После успешного подключения пользователи могут обмениваться сообщениями и файлами.

### База данных

Для хранения ранее подключенных устройств используется SQLite.

В базе данных сохраняются:

- IP-адрес устройства;
- порт устройства.

Кнопка **«Старые IP»** позволяет посмотреть ранее сохраненные подключения и выбрать нужное устройство.

### Файлы и история

Полученные файлы сохраняются в папке:

```text
received/
```

История переписки сохраняется в папке:

```text
chats/
```

Необходимые папки создаются автоматически при запуске программы.

### Важная информация

Мессенджер предназначен прежде всего для работы в **локальной сети (LAN)**. Для подключения компьютеры должны иметь сетевую доступность друг для друга.

Если подключение не устанавливается, необходимо проверить:

- правильность IP-адреса;
- правильность порта;
- подключение компьютеров к одной сети;
- настройки брандмауэра Windows;
- отсутствие блокировки выбранного TCP-порта.

---

## 🇬🇧 English version

### About the project

**Local Messenger** is an application for exchanging text messages and files between users over a local network.

The application is developed in **Python** and uses **Tkinter** for the graphical user interface, **Socket** for network communication, and **SQLite** for storing information about previously connected devices.

The application can work as both a **server and a client**. The server accepts connections from other users, while the client can connect to a running server using its IP address and port.

### Main features

- starting a TCP server;
- connecting to another user by IP address and port;
- exchanging text messages;
- sending files;
- receiving files;
- handling multiple client connections;
- saving previously used IP addresses and ports;
- viewing previously connected devices;
- saving chat history;
- automatic creation of folders for received files and chat history;
- graphical interface built with Tkinter;
- operation over a local network.

### Technologies

- **Python 3**
- **Tkinter** — graphical user interface;
- **Socket / TCP** — network communication;
- **Threading** — handling multiple connections;
- **SQLite** — storing IP addresses and ports;
- **OS** — file and directory management.

### Project structure

```text
messenge_local/
│
├── main.py          # Application entry point
├── gui.py           # Graphical user interface
├── network.py       # Network logic and data exchange
├── SQL.py           # SQLite database operations
├── users.db         # Connection database
│
├── received/        # Received files
└── chats/           # Chat history
```

### Installation

Python 3 is required to run the project.

You can check the installed Python version with:

```bash
python --version
```

Then open the project directory:

```bash
cd path_to_project
```

No additional libraries are required because the project uses modules included in the Python standard library.

### Running the application

Run the following command:

```bash
python main.py
```

The messenger's graphical interface will open.

### Connecting users

To connect two computers on the same local network:

1. Start the application on the first computer.
2. Enter the username.
3. Specify a port, for example `8080`.
4. Click **"Start Server"**.
5. Start the application on the second computer.
6. Enter the username.
7. Enter the local IP address of the first computer.
8. Enter the same port.
9. Click **"Connect"**.

After a successful connection, users can exchange messages and files.

### Database

SQLite is used to store information about previously connected devices.

The database stores:

- device IP address;
- device port.

The **"Old IPs"** button allows users to view previously saved connections and select a device.

### Files and chat history

Received files are stored in:

```text
received/
```

Chat history is stored in:

```text
chats/
```

The required directories are created automatically when the application starts.

### Important information

The messenger is primarily designed to work over a **local area network (LAN)**. The computers must be able to communicate with each other over the network.

If the connection cannot be established, check:

- the IP address;
- the port number;
- whether both computers are connected to the same network;
- Windows Firewall settings;
- whether the selected TCP port is blocked.
