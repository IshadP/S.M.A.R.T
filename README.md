📦 S.M.A.R.T - Spam, Malicious, and Fake News Detection Bot

S.M.A.R.T is a Telegram bot designed to detect spam messages, malicious links, and fake news using machine learning. It helps keep your chat groups safe and informed by automatically analyzing messages in real time.
🚀 Features

    🛡️ Spam Detection — Filters out spammy messages using NLP models.

    🔗 Malicious Link Detection — Detects harmful or suspicious URLs.

    📰 Fake News Detection — Identifies fake or misleading news content.

    🤖 Easy Deployment — Just run a script and you're good to go!
    

🔧 Setup Instructions
1. Download & Run Setup Script

This script will:

    Clone the bot repo

    Prompt you for a BotFather token

    Install all dependencies

    Start the bot

# Download script
curl -O https://raw.githubusercontent.com/IshadP/S.M.A.R.T/main/scripts/setup_smart_bot.sh

# Make it executable
chmod +x setup_smart_bot.sh

# Run it
./setup_smart_bot.sh

    🔐 Make sure you've disabled privacy mode via @BotFather > /setprivacy and set it to Disabled (so the bot can read all messages).

2. Updating the Bot Later

To update your bot after new changes are pushed to GitHub:

# Download update script
curl -O https://raw.githubusercontent.com/IshadP/S.M.A.R.T/main/scripts/update_and_run_bot.sh

# Make it executable
chmod +x update_and_run_bot.sh

# Run it
./update_and_run_bot.sh

📁 Folder Structure

S.M.A.R.T/
├── telegram_bot.py
├── models/
│   ├── spam_model.joblib
│   ├── spam_vectorizer.joblib
│   ├── fake_news_model.joblib
│   ├── fake_news_vectorizer.joblib
│   └── malicious_link_model.joblib
├── requirements.txt
├── .env
└── scripts/
    ├── setup_smart_bot.sh
    └── update_and_run_bot.sh

📜 License

MIT License – feel free to use and modify.
💬 Contact

For issues or improvements, feel free to open an Issue or Pull Request.
🔗 Script Download Links

Once you upload the scripts to your GitHub under the scripts/ folder:

    📥 [setup_smart_bot.sh]()

    🔄 [start.sh]()
