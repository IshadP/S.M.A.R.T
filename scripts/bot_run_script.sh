#!/bin/bash


echo "📥 Cloning S.M.A.R.T bot repository..."
git clone https://github.com/IshadP/S.M.A.R.T.git || { echo "❌ Git clone failed."; exit 1; }

cd S.M.A.R.T || { echo "❌ Failed to enter repo directory"; exit 1; }

read -p "🤖 Enter your Telegram bot token from BotFather: " BOT_TOKEN
echo "BOT_TOKEN=$BOT_TOKEN" > .env

read -p "✅ Type 'yes' if you’ve used /setprivacy in @BotFather to allow the bot to read all messages: " SET_PRIVACY
if [ "$SET_PRIVACY" != "yes" ]; then
    echo "⚠️ Please run /setprivacy in BotFather and set privacy to 'Disabled' to let the bot read messages."
fi

echo "🐍 Creating virtual environment..."
python3 -m venv venv || { echo "❌ Failed to create virtualenv"; exit 1; }
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt || {
    echo "⚠️ requirements.txt not found or failed. Installing basic packages manually..."
    pip install python-telegram-bot joblib python-dotenv scikit-learn numpy scipy
}

echo "🚀 Starting the bot...
To add bot to group, search bot name and add it!"
python3 telegram_bot.py

