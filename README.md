## Встановлення

```bash
git clone https://github.com/yourusername/pump_founder.git
cd paradex_option_mon
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS<br>
.venv\Scripts\activate       # Windows<br>
pip install -r requirements.txt
touch .env
```

У .env додати:

- TELEGRAM_BOT_TOKEN=<ваш токен>
- TELEGRAM_CHAT_ID=<id чату>


## Автозапуск

### 💾 Крок 1: Створення файлу автозапуску `systemd`

Спочатку відкрийте файл конфігурації служби `systemd` для редагування:

```bash
sudo nano /etc/systemd/system/pump_founder.service
```

-----

### 📝 Крок 2: Вміст файлу `pump_founder.service`

**Скопіюйте та вставте** цей блок у редактор `nano`. Не забудьте **замінити** `user1` на вашого реального користувача та перевірити шляхи\!

```ini
[Unit]
Description=Trade option project auto start
After=network.target

[Service]
# 👤 Вкажи користувача, від якого має запускатись
User=user1
Group=user1

# 📂 Робоча директорія проекту
WorkingDirectory=/home/user1/projects/pump_founder

# 🚀 Запуск Python з віртуального середовища
ExecStart=/home/user1/projects/pump_founder/.venv/bin/python /home/user1/projects/pump_founder/main.py

# 🔁 Перезапуск при падінні
Restart=always
RestartSec=5

# 🧠 Оточення
Environment="PYTHONUNBUFFERED=1"
Environment="PATH=/home/user1/projects/pump_founder/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"

[Install]
WantedBy=multi-user.target
```

-----

### 🚀 Крок 3: Активація та керування службою

Виконайте ці команди у терміналі:

#### 1️⃣ Перезавантаження systemd

Зчитайте новий файл конфігурації:

```bash
sudo systemctl daemon-reload
```

#### 2️⃣ Увімкнення автозапуску

Встановіть службу для автоматичного старту системи:

```bash
sudo systemctl enable pump_founder.service
```

### 3️⃣ Ручний запуск

Запустіть службу негайно:

```bash
sudo systemctl start pump_founder.service
```

#### 4️⃣ Перевірка статусу і логів

Перевірте, чи успішно працює служба (натисніть **Ctrl+C** для виходу з логів):

```bash
sudo systemctl status pump_founder.service
journalctl -u pump_founder -f
```