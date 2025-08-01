import telebot
from telebot import types

TOKEN = 'USER_BOT_TOKEN'
CREATOR_ID = CREATOR_TELEGRAM_ID  # Автомат түрде қойылады
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

user_messages = {}      # {user_id: message_id}
banned_users = set()    # ID списка заблокированных пользователей
admins = set([CREATOR_ID])  # Массив админов
channel_username = None

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in banned_users:
        return bot.send_message(message.chat.id, "⛔ Вы заблокированы.")

    if message.from_user.id == CREATOR_ID:
        text = (
            "Здравствуйте, этот текст толко ты видишь! \n чтобы посмотреть админ меню пишите ./help"
        )
    else:
        text = (
            "Здравствуйте!\\n\\n"
            "Отправьте своё сообщение, и мы ответим в ближайшее время 🎭"
        )
    bot.send_message(message.chat.id, text)
    
@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id != CREATOR_ID:
        return
    faq = (
        "📌 FAQ для создателя:\n\n"
        "1. Ответ на сообщения\n"
        "- Чтобы ответить на сообщение, нужно просто свайпнуть его и отправить ответ\n\n"
        "2. Статистика, приветствие и название бота\n"
        "- Напишите /admin, чтобы открыть меню управления\n\n"
        "3. Блокировка пользователей\n"
        "- Напишите /ban в ответ на сообщение пользователя\n\n"
        "4. Изменить аватарку/описание\n"
        "- Откройте профиль бота и нажмите “Изменить”\n\n"
        "5. Рассылка\n"
        "- Напишите /broadcast и следуйте инструкции\n\n"
        "6. Привязать канал\n"
        "- Напишите /channel для получения информации\n"
    )
    # FAQ - просто как сообщение
    bot.send_message(message.chat.id, faq)

    # Последняя строка — как цитата на /help
    bot.send_message(
        message.chat.id,
        "ℹ️ Информация будет дополняться",
        reply_to_message_id=message.message_id  # вот здесь reply
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != CREATOR_ID:
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data='stats'))
    markup.add(types.InlineKeyboardButton("➕ Добавить админа", callback_data='add_admin'))
    markup.add(types.InlineKeyboardButton("➖ Удалить админа", callback_data='remove_admin'))
    markup.add(types.InlineKeyboardButton("📌 Привязать канал", callback_data='link_channel'))
    bot.send_message(message.chat.id, "🛠 Панель управления:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.from_user.id != CREATOR_ID:
        return

    if call.data == 'stats':
        total_users = len(user_messages)
        total_admins = len(admins)
        total_banned = len(banned_users)
        stats = f"📊 Статистика:\n👥 Пользователи: {total_users}\n👑 Админы: {total_admins}\n⛔ В бане: {total_banned}"
        bot.send_message(call.message.chat.id, stats, reply_to_message_id=call.message.message_id)

    elif call.data == 'add_admin':
        msg = bot.send_message(call.message.chat.id, "Введите ID пользователя, которого хотите сделать админом:")
        bot.register_next_step_handler(msg, process_add_admin)

    elif call.data == 'remove_admin':
        msg = bot.send_message(call.message.chat.id, "Введите ID админа, которого хотите удалить:")
        bot.register_next_step_handler(msg, process_remove_admin)

    elif call.data == 'link_channel':
        msg = bot.send_message(call.message.chat.id, "Введите @username канала (бот должен быть админом там):")
        bot.register_next_step_handler(msg, process_link_channel)

def process_add_admin(message):
    try:
        user_id = int(message.text.strip())
        admins.add(user_id)
        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} теперь админ.")
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID.")

def process_remove_admin(message):
    try:
        user_id = int(message.text.strip())
        if user_id == CREATOR_ID:
            bot.send_message(message.chat.id, "❌ Создателя удалить нельзя.")
            return
        admins.discard(user_id)
        bot.send_message(message.chat.id, f"🗑 Админ {user_id} удалён.")
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID.")

def process_link_channel(message):
    global channel_username
    username = message.text.strip()
    if username.startswith("@"):
        channel_username = username
        bot.send_message(message.chat.id, f"📌 Канал {username} успешно привязан!")
    else:
        bot.send_message(message.chat.id, "❌ Укажите в формате @channelusername.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id in admins and message.reply_to_message:
        user_id = message.reply_to_message.forward_from.id if message.reply_to_message.forward_from else None
        if user_id:
            banned_users.add(user_id)
            bot.send_message(message.chat.id, f"⛔ Пользователь {user_id} заблокирован.")
        else:
            bot.send_message(message.chat.id, "⚠️ Невозможно определить пользователя.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id not in admins:
        return

    # 1. Егер reply бар болса
    if message.reply_to_message:
        reply = message.reply_to_message
        user_id = reply.forward_from.id if reply.forward_from else None
        if user_id:
            banned_users.discard(user_id)
            bot.send_message(message.chat.id, f"✅ Пользователь {user_id} разблокирован через ответ.")
        else:
            bot.send_message(message.chat.id, "⚠️ Невозможно определить пользователя из ответа.")
    else:
        # 2. Егер reply болмаса — ID сұраймыз
        msg = bot.send_message(message.chat.id, "Введите ID пользователя для разблокировки:")
        bot.register_next_step_handler(msg, process_unban)


def process_unban(message):
    try:
        user_id = int(message.text.strip())
        banned_users.discard(user_id)
        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} разблокирован.")
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID.")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == CREATOR_ID:
        msg = bot.send_message(message.chat.id, "✉️ Введите текст для рассылки:")
        bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    for user_id in user_messages:
        try:
            bot.send_message(user_id, message.text)
        except:
            pass
    bot.send_message(message.chat.id, "✅ Рассылка завершена.")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.from_user.id in banned_users:
        return

    if message.from_user.id == CREATOR_ID and message.reply_to_message:
        for user_id, msg_id in user_messages.items():
            if msg_id == message.reply_to_message.message_id:
                bot.send_message(user_id, f"💬 Ответ от админа:\n{message.text}")
                break
    elif message.from_user.id != CREATOR_ID:
        sent = bot.send_message(CREATOR_ID, f"✉️ Новое сообщение от пользователя:\n\n{message.text}")
        user_messages[message.from_user.id] = sent.message_id
        bot.send_message(message.chat.id, "📨 Ваше сообщение отправлено. Ожидайте ответ.")

bot.polling(none_stop=True)