# Commex
**Commex** — это веб-приложение, мессенджер. Пользователи могут регистрироваться, находить собеседников, создавать диалоги и общаться в реальном времени.

Сервер построен на Django и Channels, поэтому обеспечивает как классические HTTP‑страницы, так и долговременные WebSocket‑соединения. 

## Функции
- Регистрация и авторизация пользователей с загрузкой аватара.
- Список доступных чатов и поиск собеседников.
- Создание приватных диалогов и обмен сообщениями в реальном времени.
- Шифрование текста сообщений перед сохранением в БД.
- Удаление сообщений и целых чатов с подтверждением действия.

## Стек технологий
- **Backend:** Python 3, Django, Django Channels.
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript.

## Установка
1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/HunterXIII/CommexProject
   cd CommexProject
   ```
2. **Создайте виртуальное окружение**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  
   ```
3. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```
4. **Примените миграции**
   ```bash
   python manage.py migrate
   ```
5. **Для работы WebSocket потребуется Redis.**
> Его также необходимо установить и запустить 

6. **Создайте суперпользователя (опционально для админки)**
   ```bash
   python manage.py createsuperuser
   ```
7. **Запустите сервер разработки**
   ```bash
   python manage.py runserver
   ```
8. **Откройте приложение**
   - Перейдите в браузере по адресу `http://127.0.0.1:8000/`
   - Создайте новый аккаунт или войдите под суперпользователем.

## Скриншоты
- Главная
![Главная страница](./docs/img/Home.png)
- Регистрации
![Регистрация](./docs/img/Register.png)
- Поиск
![Поиск](./docs/img/Search.png)
- Чат
![Чат](./docs/img/Chat.png)

## Схема базы данных
```mermaid
erDiagram
    MESSENGERUSER {
        int id PK
        varchar username
        varchar first_name
        varchar last_name
        varchar email
        bool is_superuser
        bool is_staff
        bool is_active
        datetime last_login
        datetime date_joined
        bool status
        varchar profile_image
        date birthday
        varchar password
    }

    CHAT {
        int id PK
        datetime date_of_creation
        varchar name
    }

    CHAT_USERS {
        int id PK
        int chat_id FK
        int messengeruser_id FK
    }

    TEXTMESSAGE {
        int id PK
        text content
        datetime date_of_sending
        bool is_read
        int chat_id FK
        int sender_id FK
        varchar iv
    }

    MESSENGERUSER ||--o{ CHAT_USERS : ""
    CHAT ||--o{ CHAT_USERS : ""
    CHAT ||--o{ TEXTMESSAGE : ""
    MESSENGERUSER ||--o{ TEXTMESSAGE : ""
```

## Архитектурная схема
```mermaid
graph LR
    A[Браузер<br>HTML/JS] -- HTTP --> B[Django Views<br>REST/Template]
    A -- WebSocket --> C[Channels Consumers]
    B -- ORM --> D[(База данных)]
    C -- ORM --> D
    C -- Crypto --> E[AES модуль]
    B -- Crypto --> E
```



