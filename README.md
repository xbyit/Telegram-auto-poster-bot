# Telegram Auto Poster Bot

A Telegram bot that automatically generates and publishes engaging technical, scientific, or literary content to your channels using AI (GPT + DALL·E). You can control content type, language, and post intervals for each channel individually.

## Features

- Auto-generate posts using GPT based on selected content category.
- Auto-generate relevant images using DALL·E.
- Supports multiple Telegram channels per user.
- Per-channel settings: content type, language (`Arabic` / `English`), and interval in hours.
- Admin panel via bot UI for adding, deleting, and managing channels.

## Supported Content Types

- Programming
- Cybersecurity
- Poetry
- Scientific Knowledge

## Technologies Used

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot-API-blue?logo=telegram)
![GPT-3.5](https://img.shields.io/badge/GPT-3.5-lightgray?logo=openai)
![DALL·E](https://img.shields.io/badge/DALL·E-Image%20Generator-green?logo=openai)
![JSON](https://img.shields.io/badge/Storage-JSON-yellow)

## How to Use

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/telegram-auto-poster.git
   cd telegram-auto-poster```

2. Install dependencies:

```pip install -r requirements.txt```


3. Replace the token in the script with your bot token:

TOKEN = 'YOUR_BOT_TOKEN'


4. Run the bot:

```python telegram_auto_poster.py```

License

This project is open-source and free to use under the MIT License.
