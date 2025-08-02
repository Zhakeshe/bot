import telebot
import subprocess
from utils import create_bot_file, is_token_valid
from flask import Flask, request
import os

API_TOKEN = '8276354521:AAGKLwBNmOFgkv3bda9lCjqyWzREVyXH8HM'  # ← өз BotFather токеніңізді қойыңыз
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Сервер жұмыс істеп тұр!"

@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        """Мы создаем специалный бот для переписке анонимный!   

Следуйте инструкции, чтобы создать бота:

Шаг 1: Перейдите в @BotFather
Шаг 2: Напишите: /newbot
Шаг 3: Придумайте и напишите название бота (например: Аноним бот)
Шаг 4: Придумайте и напишите username бота, заканчивающийся на bot или _bot (например: mysupport_bot)
Шаг 5: В результате вы получите сообщение содержащее токен бота, перешлите его сюда или пришлите сам токен 👇"""
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f'https://bot-8mr1.onrender.com/{API_TOKEN}')
    app.run(host='0.0.0.0', port=port)
