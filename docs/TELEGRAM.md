# Telegram Bot API integration

The optional bridge uses the official Telegram Bot API directly over HTTPS. The Kolobok computer does not need to open Telegram Web or the Telegram desktop application. Create a bot through @BotFather and set its token in the local Kolobok telegram.json file or app settings. For private use, populate allowed_user_ids with the numeric Telegram user IDs allowed to interact.

Telegram does not let a bot initiate a private chat before the user starts it. Open the bot once and press Start or send a message. After that, the local bridge can poll updates and send replies. A Telegram client is still needed on the recipient device to read messages.

Run run_telegram.bat after configuring the token and AI provider. Keep the token private; never commit it. This bridge is an optional polling process, not a background service unless you explicitly configure one.