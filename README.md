<div align="center">

#  bot-api-imap

**Mail → Telegram forwarder · Пересылка новых писем в Telegram**

![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

 **Choose your language / Выберите язык** 

</div>

---

<details open>
<summary><h2>English</h2></summary>

### About

A small Python script that watches an email inbox over **IMAP** and forwards every new email (sender, subject and the beginning of the body) to one or more **Telegram** chats through the Bot API.

### Features

- Polls the `INBOX` over IMAP SSL (Gmail by default, any IMAP server works)
- Forwards sender, subject and body text to Telegram
- Several recipients at once (comma-separated chat IDs)
- Optional whitelist of allowed senders
- Converts HTML-only emails to plain text and decodes encoded headers
- Remembers the last processed email (`state.json`), so nothing is sent twice after a restart
- Does **not** mark emails as read (the mailbox is opened read-only)
- Old emails are skipped on the first launch, only new ones are forwarded

### Requirements

- Python 3.8 or newer
- A mailbox with IMAP access and an **app password** (for Gmail: 2-Step Verification must be enabled)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/unhappy7/bot-api-imap.git
   cd bot-api-imap
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```
   Activate it:
   - Linux / macOS: `source venv/bin/activate`
   - Windows (PowerShell): `venv\Scripts\Activate.ps1`

3. **Install dependencies**
   ```bash
   pip install requests python-dotenv
   ```

4. **Create a Telegram bot**
   - Open [@BotFather](https://t.me/BotFather), send `/newbot` and follow the instructions.
   - Copy the token it gives you.
   - Open your new bot and press **Start** (otherwise it cannot write to you).

5. **Find your chat ID**
   - Send any message to [@userinfobot](https://t.me/userinfobot), it replies with your ID.
   - For a group, add the bot to the group and use the group's ID (it starts with `-`).

6. **Get an IMAP app password** (Gmail example)
   - Enable 2-Step Verification in your Google account.
   - Create an app password at <https://myaccount.google.com/apppasswords>.
   - Use this 16-character password as `IMAP_PASSWORD`, not your normal password.

7. **Create the config file**

   Create a file named `.env` next to `mail_to_telegram.py` (or copy `.env.example`) with this content and put your own values in:

   ```ini
   # Required
   IMAP_USER=you@gmail.com
   IMAP_PASSWORD=your_app_password
   BOT_TOKEN=123456:ABC-DEF
   CHAT_ID=12345678

   # Optional
   # IMAP_HOST=imap.gmail.com
   CHECK_INTERVAL=60
   # MAX_BODY_CHARS=1000
   # ALLOWED_SENDERS=a@example.com,b@example.com
   ```

   > Write values **without** inline comments on the same line (`KEY=value`). Put comments on separate lines.

8. **Run the bot**
   ```bash
   python mail_to_telegram.py
   ```
   On success you will see a line like `I keep an eye on you@gmail.com on imap.gmail.com ...`.

### Configuration

All settings are read from the `.env` file (or from environment variables).

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `IMAP_USER` | ✅ | – | Email address (login) |
| `IMAP_PASSWORD` | ✅ | – | IMAP / app password |
| `BOT_TOKEN` | ✅ | – | Telegram bot token from BotFather |
| `CHAT_ID` | ✅ | – | Recipient chat ID(s), comma-separated: `12345678,87654321` |
| `IMAP_HOST` | ❌ | `imap.gmail.com` | IMAP server address |
| `CHECK_INTERVAL` | ❌ | `60` | Mailbox check interval, seconds |
| `MAX_BODY_CHARS` | ❌ | `1000` | Maximum number of body characters sent |
| `ALLOWED_SENDERS` | ❌ | empty (all) | Comma-separated sender addresses to forward |

### Running in the background (Linux, systemd)

Create `/etc/systemd/system/bot-api-imap.service`:

```ini
[Unit]
Description=bot-api-imap
After=network-online.target

[Service]
WorkingDirectory=/path/to/bot-api-imap
ExecStart=/path/to/bot-api-imap/venv/bin/python mail_to_telegram.py
Restart=always
User=youruser

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bot-api-imap
```

### How it works

1. On the first launch the script remembers the UID of the newest email and skips all older ones.
2. Every `CHECK_INTERVAL` seconds it asks the server for emails with a higher UID.
3. Each new email is formatted and sent to every chat in `CHAT_ID`. Messages are cut to Telegram's 4096-character limit.
4. The UID of the last processed email is saved to `state.json`. To start again from "now", delete this file.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `KeyError: 'IMAP_USER'` (or another variable) | `.env` is missing or the variable is not set |
| `Error: [AUTHENTICATIONFAILED]` | Use an app password, check the login and that IMAP is enabled |
| `Couldn't send to ...: 403` | Open the bot in Telegram and press **Start**; check the chat ID |
| `Couldn't send to ...: 401` | Wrong `BOT_TOKEN` |
| Nothing is forwarded | Check `ALLOWED_SENDERS`; emails received before the first launch are skipped |



<details>
<summary><h2>Русский</h2></summary>

### О проекте

Небольшой Python-скрипт, который следит за почтовым ящиком по **IMAP** и пересылает каждое новое письмо (отправитель, тема и начало текста) в один или несколько чатов **Telegram** через Bot API.

### Возможности

- Проверяет папку `INBOX` по IMAP SSL (по умолчанию Gmail, подойдёт любой IMAP-сервер)
- Пересылает в Telegram отправителя, тему и текст письма
- Несколько получателей сразу (ID чатов через запятую)
- Необязательный белый список отправителей
- Преобразует HTML-письма в обычный текст и декодирует закодированные заголовки
- Запоминает последнее обработанное письмо (`state.json`), поэтому после перезапуска ничего не придёт дважды
- **Не** помечает письма прочитанными (ящик открывается только для чтения)
- При первом запуске старые письма пропускаются, пересылаются только новые

### Требования

- Python 3.8 или новее
- Почтовый ящик с доступом по IMAP и **паролем приложения** (для Gmail должна быть включена двухэтапная аутентификация)
- Токен Telegram-бота от [@BotFather](https://t.me/BotFather)

### Установка

1. **Склонируйте репозиторий**
   ```bash
   git clone https://github.com/unhappy7/bot-api-imap.git
   cd bot-api-imap
   ```

2. **Создайте виртуальное окружение** (рекомендуется)
   ```bash
   python -m venv venv
   ```
   Активируйте его:
   - Linux / macOS: `source venv/bin/activate`
   - Windows (PowerShell): `venv\Scripts\Activate.ps1`

3. **Установите зависимости**
   ```bash
   pip install requests python-dotenv
   ```

4. **Создайте Telegram-бота**
   - Откройте [@BotFather](https://t.me/BotFather), отправьте `/newbot` и следуйте инструкциям.
   - Скопируйте выданный токен.
   - Откройте своего нового бота и нажмите **Start** (иначе он не сможет вам писать).

5. **Узнайте свой chat ID**
   - Отправьте любое сообщение боту [@userinfobot](https://t.me/userinfobot), он ответит вашим ID.
   - Для группы добавьте бота в группу и используйте ID группы (начинается с `-`).

6. **Получите пароль приложения для IMAP** (на примере Gmail)
   - Включите двухэтапную аутентификацию в аккаунте Google.
   - Создайте пароль приложения: <https://myaccount.google.com/apppasswords>.
   - Используйте этот 16-символьный пароль как `IMAP_PASSWORD`, а не обычный пароль от почты.

7. **Создайте файл настроек**

   Создайте файл `.env` рядом с `mail_to_telegram.py` (или скопируйте `.env.example`) с таким содержимым и впишите свои значения:

   ```ini
   # Обязательные
   IMAP_USER=you@gmail.com
   IMAP_PASSWORD=your_app_password
   BOT_TOKEN=123456:ABC-DEF
   CHAT_ID=12345678

   # Необязательные
   # IMAP_HOST=imap.gmail.com
   CHECK_INTERVAL=60
   # MAX_BODY_CHARS=1000
   # ALLOWED_SENDERS=a@example.com,b@example.com
   ```

   >  Пишите значения **без** комментариев в той же строке (`KEY=value`). Комментарии размещайте на отдельных строках.

8. **Запустите бота**
   ```bash
   python mail_to_telegram.py
   ```
   При успешном запуске появится строка вида `I keep an eye on you@gmail.com on imap.gmail.com ...`.

### Настройка

Все параметры читаются из файла `.env` (или из переменных окружения).

| Переменная | Обязательна | По умолчанию | Описание |
|------------|:-----------:|--------------|----------|
| `IMAP_USER` | ✅ | – | Адрес почты (логин) |
| `IMAP_PASSWORD` | ✅ | – | IMAP-пароль / пароль приложения |
| `BOT_TOKEN` | ✅ | – | Токен Telegram-бота от BotFather |
| `CHAT_ID` | ✅ | – | ID чатов-получателей через запятую: `12345678,87654321` |
| `IMAP_HOST` | ❌ | `imap.gmail.com` | Адрес IMAP-сервера |
| `CHECK_INTERVAL` | ❌ | `60` | Интервал проверки почты, секунды |
| `MAX_BODY_CHARS` | ❌ | `1000` | Максимум символов текста письма в сообщении |
| `ALLOWED_SENDERS` | ❌ | пусто (все) | Адреса отправителей через запятую |

### Запуск в фоне (Linux, systemd)

Создайте файл `/etc/systemd/system/bot-api-imap.service`:

```ini
[Unit]
Description=bot-api-imap
After=network-online.target

[Service]
WorkingDirectory=/path/to/bot-api-imap
ExecStart=/path/to/bot-api-imap/venv/bin/python mail_to_telegram.py
Restart=always
User=youruser

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bot-api-imap
```

### Как это работает

1. При первом запуске скрипт запоминает UID самого нового письма и пропускает все более старые.
2. Каждые `CHECK_INTERVAL` секунд он запрашивает у сервера письма с большим UID.
3. Каждое новое письмо форматируется и отправляется во все чаты из `CHAT_ID`. Сообщения обрезаются до лимита Telegram в 4096 символов.
4. UID последнего обработанного письма сохраняется в `state.json`. Чтобы начать заново «с текущего момента», удалите этот файл.

### Решение проблем

| Проблема | Решение |
|----------|---------|
| `KeyError: 'IMAP_USER'` (или другая переменная) | Нет файла `.env` или переменная не задана |
| `Error: [AUTHENTICATIONFAILED]` | Используйте пароль приложения, проверьте логин и включён ли IMAP |
| `Couldn't send to ...: 403` | Откройте бота в Telegram и нажмите **Start**; проверьте chat ID |
| `Couldn't send to ...: 401` | Неверный `BOT_TOKEN` |
| Ничего не пересылается | Проверьте `ALLOWED_SENDERS`; письма, пришедшие до первого запуска, пропускаются |


### License

Distributed under the **MIT License**.

<details>
<summary>Full license text</summary>

```text
MIT License

Copyright (c) 2026 unhappy7

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

</details>

</details>
