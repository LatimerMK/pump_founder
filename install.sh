#!/bin/bash

# bash <(curl -s https://raw.githubusercontent.com/LatimerMK/pump_founder/main/install.sh)

curl -s https://raw.githubusercontent.com/LatimerMK/bash-install/refs/heads/main/tools/logo.sh | bash

# Оновлення пакунків
echo "Оновлення системи..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Встановлення Python та pip
echo "Встановлення Python3 і pip..."
sudo apt-get install python3 python3-pip python3-venv git -y

# Клонуємо репозиторій
echo "Клонуємо репозиторій..."
git clone https://github.com/LatimerMK/pump_founder.git

# Перехід в каталог з проєктом
cd pump_founder

# Створення віртуального середовища
echo "Створення віртуального середовища..."
python3 -m venv .venv
source .venv/bin/activate

# Встановлення залежностей
echo "Встановлення залежностей..."
pip install -r requirements.txt

# Запит користувача на API ключ і секрет
echo "Будь ласка, введіть ваш API ключ (Binance):"
read API_KEY
echo "Будь ласка, введіть ваш API секрет (Binance):"
read API_SECRET
echo "Будь ласка, введіть ваш API секрет (Binance):"
read TELEGRAM_BOT_TOKEN
echo "Будь ласка, введіть ваш API секрет (Binance):"
read TELEGRAM_CHAT_ID

# Створення .env файлу
echo "Створення .env файлу..."
cat <<EOT > .env
API_KEY=$API_KEY
API_SECRET=$API_SECRET
# Ваш Telegram Bot Token
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
# Ваш Telegram Chat ID
TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID
EOT

# Створення скрипта для запуску програми
echo "Створення скрипта для запуску..."
cat <<EOT > start.sh
#!/bin/bash
# Активуємо віртуальне середовище і запускаємо програму
source ~/pump_founder/.venv/bin/activate
python3 main.py
EOT

echo "Створення скрипта для запуску Tmux..."
cat <<EOT > start_tmux.sh
#!/bin/bash
# Створення нової сесії tmux
tmux new-session -d -s pump_founder

# Запуск команд у tmux сесії
tmux send-keys -t pump_founder "source ~/pump_founder/.venv/bin/activate" C-m
tmux send-keys -t pump_founder "python3 main.py" C-m
tmux send-keys -t echo "tmux new-session -d -s pump_founder"

tmux send-keys -t pump_founder "echo 'Створення нової сесії: tmux new-session -d -s pump_founder'" C-m
tmux send-keys -t pump_founder "echo 'Вхід в сесію: tmux attach -t pump_founder'" C-m
tmux send-keys -t pump_founder "echo 'Щоб вийти з сесії Ctrl + b, потім d'" C-m
tmux send-keys -t pump_founder "echo 'Закриття сесії з середини: exit'" C-m

# Підключення до сесії для моніторингу
tmux attach -t pump_founder
EOT

# Робимо start.sh виконуваним
chmod +x start.sh
chmod +x start_tmux.sh

# Підсумок
echo "Установка завершена. Для запуску програми використовуйте './start.sh'. bash start.sh (start_tmux.sh)"
