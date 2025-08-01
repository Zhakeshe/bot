import os

def create_bot_file(token, creator_id):
    with open("template_bot.py", "r", encoding="utf-8") as f:
        code = f.read()
    code = code.replace("USER_BOT_TOKEN", token)
    code = code.replace("CREATOR_TELEGRAM_ID", str(creator_id))
    filename = f"bots/bot_{token[:10]}.py"
    os.makedirs("bots", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    return filename

def is_token_valid(token):
    try:
        import telebot
        bot = telebot.TeleBot(token)
        bot.get_me()
        return True
    except:
        return False