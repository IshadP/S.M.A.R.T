#!/bin/bash

cd S.M.A.R.T || { echo "❌ Cannot find S.M.A.R.T directory."; exit 1; }

if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️ Virtual environment not found. Run the setup script first."
    exit 1
fi

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN is not set in the environment. Please add it to your .env file."
    exit 1
fi

echo "📥 Checking for updates..."
git pull || { echo "❌ Failed to pull from GitHub."; exit 1; }

if [ -f "requirements.txt" ]; then
    echo "📦 Updating dependencies..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found. Skipping dependency update."
fi

echo "🚀 Running the updated bot..."
python3 telegram_bot.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to run the bot."
    exit 1
fi
echo "✅ Bot is running successfully."
echo "🔄 To stop the bot, use Ctrl+C."