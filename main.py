import telebot
import subprocess
from utils import create_bot_file, is_token_valid
from flask import Flask

API_TOKEN = '8276354521:AAGKLwBNmOFgkv3bda9lCjqyWzREVyXH8HM'  # ← өз BotFather токеніңізді қойыңыз
bot = telebot.TeleBot(API_TOKEN)
bot.remove_webhook()  # <-- міне осы жолды қосыңыз
app = Flask(__name__)

@app.route('/')
def home():
    return "Сервер жұмыс істеп тұр!"

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Render портты ENV арқылы береді
    app.run(host='0.0.0.0', port=port)
    
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "Для подключения бота выполните следующее:\n\n"
        "1. Создайте бота в @BotFather\n"
        "2. Отправьте мне токен вашего нового бота, полученного в @BotFather "
        "(выглядит как набор цифр и букв: 12345:ABCD)"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: True)
def receive_token(message):
    token = message.text.strip()
    if not is_token_valid(token):
        bot.send_message(message.chat.id, "❌ Токен недействителен. Проверьте и попробуйте снова.")
        return

    filename = create_bot_file(token, message.from_user.id)
    subprocess.Popen(["python", filename])
    bot_username = telebot.TeleBot(token).get_me().username
    bot.send_message(
        message.chat.id,
        f"🟢 Поздравляем, бот https://t.me/{bot_username} успешно подключён!\n\n"
        "Для проверки его работы выполните следующее:\n"
        f"1. Перейдите в https://t.me/{bot_username}\n"
        "2. Отправьте /start"
    )

bot.set_webhook(url=f'https://bot-8mr1.onrender.com/{TOKEN}')  # 👈 URL дұрыстап қой
    app.run(host='0.0.0.0', port=port)

