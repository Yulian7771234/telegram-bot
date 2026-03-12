import telebot
from telebot import types
import time

# ВСТАВЬ СВОЙ ТОКЕН СЮДА
TOKEN = "8211032032:AAFUUIgTep0FZdJo0GWmJNBk0j70vrtT2rM"
bot = telebot.TeleBot(TOKEN)

# ========== НАСТРОЙКИ ==========
CHANNEL_ID = -1003857838981  # ID твоего канала
CHANNEL_LINK = "https://t.me/+gPXyWBWPB2FkYmZi"  # Ссылка на канал

# ========== ХРАНЕНИЕ ССЫЛОК В ПАМЯТИ ==========
helper_links = {
    "helper1": {
        "name": "Помощник 1", 
        "links": {
            "link1": {"url": "", "description": "", "added_by": ""},
            "link2": {"url": "", "description": "", "added_by": ""}
        }
    },
    "helper2": {
        "name": "Помощник 2", 
        "links": {
            "link1": {"url": "", "description": "", "added_by": ""},
            "link2": {"url": "", "description": "", "added_by": ""}
        }
    },
    "helper3": {
        "name": "Помощник 3", 
        "links": {
            "link1": {"url": "", "description": "", "added_by": ""},
            "link2": {"url": "", "description": "", "added_by": ""}
        }
    }
}

# Словарь для временного хранения состояния выбора помощника
user_selection = {}

# ========== ПОЛУЧЕНИЕ USERNAME БОТА ==========
def get_bot_username():
    """Получает username бота"""
    try:
        me = bot.get_me()
        return me.username
    except:
        return "bot_username"

# ========== СОЗДАНИЕ INLINE-МЕНЮ ДЛЯ КАНАЛА (ТОЛЬКО ПРОСМОТР) ==========
def create_channel_menu():
    """Создает inline-кнопки для канала - только просмотр ссылок"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    # Кнопка Помощник 1
    btn_helper1 = types.InlineKeyboardButton(
        text="👤 Помощник 1",
        callback_data="channel_show_helper1"
    )
    keyboard.add(btn_helper1)
    
    # Кнопка Помощник 2
    btn_helper2 = types.InlineKeyboardButton(
        text="👤 Помощник 2",
        callback_data="channel_show_helper2"
    )
    keyboard.add(btn_helper2)
    
    # Кнопка Помощник 3
    btn_helper3 = types.InlineKeyboardButton(
        text="👤 Помощник 3",
        callback_data="channel_show_helper3"
    )
    keyboard.add(btn_helper3)
    
    # Кнопка Открыть бота
    bot_username = get_bot_username()
    btn_bot = types.InlineKeyboardButton(
        text="🤖 Открыть бота для управления",
        url=f"https://t.me/{bot_username}"
    )
    keyboard.add(btn_bot)
    
    return keyboard

# ========== СОЗДАНИЕ МЕНЮ ДЛЯ ЛИЧКИ (ПОЛНОЕ УПРАВЛЕНИЕ) ==========
def create_private_menu():
    """Создает reply-кнопки для личных сообщений"""
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, 
        row_width=1,
        input_field_placeholder="👇 Выбери действие"
    )
    btn_helper1 = types.KeyboardButton("👤 Помощник 1")
    btn_helper2 = types.KeyboardButton("👤 Помощник 2")
    btn_helper3 = types.KeyboardButton("👤 Помощник 3")
    keyboard.add(btn_helper1)
    keyboard.add(btn_helper2)
    keyboard.add(btn_helper3)
    
    return keyboard

# ========== ОТПРАВКА МЕНЮ В КАНАЛ ==========
def send_menu_to_channel():
    """Отправляет меню в канал"""
    menu_text = """
    📋 <b>МЕНЮ ПОМОЩНИКОВ</b>
    
👇 <b>Нажми на помощника для просмотра ссылок</b>
    
📢 <b>Чтобы добавить или удалить ссылку:</b>
1. Нажми "🤖 Открыть бота"
2. Выбери помощника
3. Управляй ссылками
    """
    
    try:
        bot.send_message(
            CHANNEL_ID,
            menu_text,
            parse_mode='HTML',
            reply_markup=create_channel_menu()
        )
        print(f"✅ Меню отправлено в канал")
    except Exception as e:
        print(f"❌ Ошибка отправки в канал: {e}")

# ========== ПРОВЕРКА ПОДПИСКИ ==========
def check_subscription(user_id):
    """Проверяет, подписан ли пользователь на канал"""
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return False

# ========== ФУНКЦИЯ ПРИВЕТСТВИЯ С МЕНЮ ==========
def send_welcome_with_menu(chat_id, user_name):
    """Отправляет приветствие с меню"""
    welcome_text = f"""
    🎉 <b>ПРИВЕТСТВУЮ, {user_name}!</b>
    
    👇 <b>Выбери помощника для управления ссылками:</b>
    """
    
    bot.send_message(
        chat_id,
        welcome_text,
        parse_mode='HTML',
        reply_markup=create_private_menu()
    )

# ========== ОБРАБОТКА НОВЫХ УЧАСТНИКОВ КАНАЛА ==========
@bot.chat_member_handler()
def handle_new_member(update):
    """Когда новый пользователь присоединяется к каналу"""
    if update.new_chat_member and update.new_chat_member.status in ['member', 'administrator']:
        welcome_text = f"""
        <b>ДОБРО ПОЖАЛОВАТЬ В КОМАНДУ!</b>
        
        👇 <b>Вот меню помощников:</b>
        """
        
        try:
            bot.send_message(
                CHANNEL_ID,
                welcome_text,
                parse_mode='HTML',
                reply_markup=create_channel_menu()
            )
        except:
            pass

# ========== ОБРАБОТКА СООБЩЕНИЙ В КАНАЛЕ ==========
@bot.channel_post_handler(func=lambda message: True)
def handle_channel_posts(message):
    """Обрабатывает сообщения в канале - только по слову 'отчет'"""
    if message.text and "отчет" in message.text.lower():
        bot.send_message(
            message.chat.id,
            """📋 <b>МЕНЮ ПОМОЩНИКОВ</b> 
 <b> 👇 Нажми на помощника для просмотра ссылок</b> """,
            parse_mode='HTML',
            reply_markup=create_channel_menu()
        )

# ========== ПОКАЗ ССЫЛОК В КАНАЛЕ (ТОЛЬКО ПРОСМОТР) ==========
def show_channel_links(helper_key, call):
    """Показывает ссылки помощника в канале - только просмотр"""
    helper = helper_links[helper_key]
    
    # Формируем текст со ссылками
    text = f"<b>{helper['name']}</b>\n\n"
    
    # Ссылка 1
    if helper["links"]["link1"]["url"]:
        text += f"🔗 <b>Ссылка 1:</b> {helper['links']['link1']['description']}\n"
        text += f"🔗 {helper['links']['link1']['url']}\n"
        text += f"👤 Добавил: {helper['links']['link1']['added_by']}\n\n"
    else:
        text += f"❌ Ссылка 1 не добавлена\n\n"
    
    # Ссылка 2
    if helper["links"]["link2"]["url"]:
        text += f"🔗 <b>Ссылка 2:</b> {helper['links']['link2']['description']}\n"
        text += f"🔗 {helper['links']['link2']['url']}\n"
        text += f"👤 Добавил: {helper['links']['link2']['added_by']}\n\n"
    else:
        text += f"❌ Ссылка 2 не добавлена\n\n"
    
    # Кнопки для перехода по ссылкам
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if helper["links"]["link1"]["url"]:
        btn_go1 = types.InlineKeyboardButton(
            text="🔗 Перейти по ссылке 1",
            url=helper["links"]["link1"]["url"]
        )
        keyboard.add(btn_go1)
    
    if helper["links"]["link2"]["url"]:
        btn_go2 = types.InlineKeyboardButton(
            text="🔗 Перейти по ссылке 2",
            url=helper["links"]["link2"]["url"]
        )
        keyboard.add(btn_go2)
    
    # Кнопка назад
    btn_back = types.InlineKeyboardButton(
        text="◀️ Назад к меню",
        callback_data="back_to_channel_menu"
    )
    keyboard.add(btn_back)
    
    # Редактируем сообщение
    try:
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    except:
        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

# ========== ПОКАЗ ССЫЛОК В БОТЕ (С УПРАВЛЕНИЕМ) ==========
def show_bot_links(helper_key, message, user_name, edit_message_id=None):
    """Показывает ссылки помощника в боте с кнопками управления"""
    helper = helper_links[helper_key]
    
    # Формируем текст со ссылками
    text = f"<b>{helper['name']}</b>\n\n"
    
    # Ссылка 1
    if helper["links"]["link1"]["url"]:
        text += f"🔗 <b>Ссылка 1:</b> {helper['links']['link1']['description']}\n"
        text += f"🔗 {helper['links']['link1']['url']}\n"
        text += f"👤 Добавил: {helper['links']['link1']['added_by']}\n\n"
    else:
        text += f"❌ Ссылка 1 не добавлена\n\n"
    
    # Ссылка 2
    if helper["links"]["link2"]["url"]:
        text += f"🔗 <b>Ссылка 2:</b> {helper['links']['link2']['description']}\n"
        text += f"🔗 {helper['links']['link2']['url']}\n"
        text += f"👤 Добавил: {helper['links']['link2']['added_by']}\n\n"
    else:
        text += f"❌ Ссылка 2 не добавлена\n\n"
    
    # Кнопки управления
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопки для перехода
    if helper["links"]["link1"]["url"]:
        btn_go1 = types.InlineKeyboardButton(
            text="🔗 Перейти по ссылке 1",
            url=helper["links"]["link1"]["url"]
        )
        keyboard.add(btn_go1)
    
    if helper["links"]["link2"]["url"]:
        btn_go2 = types.InlineKeyboardButton(
            text="🔗 Перейти по ссылке 2",
            url=helper["links"]["link2"]["url"]
        )
        keyboard.add(btn_go2)
    
    # Кнопки добавления
    btn_add1 = types.InlineKeyboardButton(
        text="➕ Добавить ссылку 1",
        callback_data=f"add_{helper_key}_link1"
    )
    btn_add2 = types.InlineKeyboardButton(
        text="➕ Добавить ссылку 2",
        callback_data=f"add_{helper_key}_link2"
    )
    keyboard.add(btn_add1, btn_add2)
    
    # Кнопки удаления (только для своих)
    if helper["links"]["link1"]["url"] and helper["links"]["link1"]["added_by"] == user_name:
        btn_clear1 = types.InlineKeyboardButton(
            text="🗑 Удалить ссылку 1",
            callback_data=f"clear_{helper_key}_link1"
        )
        keyboard.add(btn_clear1)
    
    if helper["links"]["link2"]["url"] and helper["links"]["link2"]["added_by"] == user_name:
        btn_clear2 = types.InlineKeyboardButton(
            text="🗑 Удалить ссылку 2",
            callback_data=f"clear_{helper_key}_link2"
        )
        keyboard.add(btn_clear2)
    
    # Кнопка назад в меню
    btn_back = types.InlineKeyboardButton(
        text="◀️ Назад в меню",
        callback_data="back_to_private_menu"
    )
    keyboard.add(btn_back)
    
    # Если есть ID сообщения для редактирования - редактируем, иначе отправляем новое
    if edit_message_id:
        try:
            bot.edit_message_text(
                text,
                message.chat.id,
                edit_message_id,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except:
            bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
    else:
        bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

# ========== ОБРАБОТКА INLINE-КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    # ===== КАНАЛ - ТОЛЬКО ПРОСМОТР =====
    if call.data == "channel_show_helper1":
        show_channel_links("helper1", call)
    elif call.data == "channel_show_helper2":
        show_channel_links("helper2", call)
    elif call.data == "channel_show_helper3":
        show_channel_links("helper3", call)
    elif call.data == "back_to_channel_menu":
        bot.edit_message_text(
            """📋 <b>МЕНЮ ПОМОЩНИКОВ</b> 
 <b> 👇 Нажми на помощника для просмотра ссылок</b> """,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=create_channel_menu()
        )
    
    # ===== БОТ - ПОЛНОЕ УПРАВЛЕНИЕ =====
    elif call.data == "back_to_private_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "👇 <b>Выбери помощника для управления ссылками:</b>",
            parse_mode='HTML',
            reply_markup=create_private_menu()
        )
    
    # Добавление ссылок
    elif call.data.startswith("add_"):
        parts = call.data.split("_")
        helper_key = parts[1]
        link_key = parts[2]
        
        user_id = call.from_user.id
        user_selection[user_id] = {
            "helper": helper_key, 
            "link": link_key,
            "message_id": call.message.message_id,
            "chat_id": call.message.chat.id
        }
        
        bot.edit_message_text(
            f"📝 Отправь мне <b>описание</b> для ссылки (например: 'Мой канал', 'Полезный сайт' и т.д.):",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML'
        )
    
    # Удаление ссылок
    elif call.data.startswith("clear_"):
        parts = call.data.split("_")
        helper_key = parts[1]
        link_key = parts[2]
        
        helper_links[helper_key]["links"][link_key] = {"url": "", "description": "", "added_by": ""}
        
        bot.answer_callback_query(call.id, "✅ Ссылка удалена!")
        
        # Показываем обновленный список
        user_name = call.from_user.first_name
        show_bot_links(helper_key, call.message, user_name, call.message.message_id)

# ========== ОБРАБОТКА КОМАНДЫ /start В ЛИЧКЕ ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    is_subscribed = check_subscription(user_id)
    
    if not is_subscribed:
        keyboard = types.InlineKeyboardMarkup()
        btn_channel = types.InlineKeyboardButton(
            text="📢 Подписаться на канал",
            url=CHANNEL_LINK
        )
        keyboard.add(btn_channel)
        
        bot.send_message(
            message.chat.id,
            "❌ <b>Доступ ограничен</b>\n\nПодпишись на канал, чтобы управлять ссылками:",
            parse_mode='HTML',
            reply_markup=keyboard
        )
        return
    
    send_welcome_with_menu(message.chat.id, user_name)

# ========== ВЫБОР ПОМОЩНИКА В ЛИЧКЕ ==========
@bot.message_handler(func=lambda message: message.text in [
    "👤 Помощник 1",
    "👤 Помощник 2", 
    "👤 Помощник 3"
])
def handle_helper_selection(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if not check_subscription(user_id):
        return
    
    if message.text == "👤 Помощник 1":
        show_bot_links("helper1", message, user_name)
    elif message.text == "👤 Помощник 2":
        show_bot_links("helper2", message, user_name)
    elif message.text == "👤 Помощник 3":
        show_bot_links("helper3", message, user_name)

# ========== ОБРАБОТКА ОПИСАНИЯ И ССЫЛКИ ==========
@bot.message_handler(func=lambda message: True)
def handle_link_input(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    text = message.text
    
    if not check_subscription(user_id):
        return
    
    # Проверяем, есть ли у пользователя выбранный помощник и ссылка
    if user_id in user_selection and "link" in user_selection[user_id]:
        if "waiting_for" not in user_selection[user_id]:
            # Сохраняем описание и запрашиваем ссылку
            user_selection[user_id]["description"] = text
            user_selection[user_id]["waiting_for"] = "url"
            bot.reply_to(
                message,
                "✅ Описание сохранено!\n\nТеперь отправь мне <b>ссылку</b> (должна начинаться с http:// или https://):",
                parse_mode='HTML'
            )
        
        elif user_selection[user_id]["waiting_for"] == "url":
            # Сохраняем ссылку
            helper_key = user_selection[user_id]["helper"]
            link_key = user_selection[user_id]["link"]
            description = user_selection[user_id]["description"]
            link = text.strip()
            message_id = user_selection[user_id]["message_id"]
            chat_id = user_selection[user_id]["chat_id"]
            
            if not (link.startswith('http://') or link.startswith('https://')):
                bot.reply_to(
                    message,
                    "❌ Это не похоже на ссылку\n\nСсылка должна начинаться с http:// или https://\nПопробуй еще раз:"
                )
                return
            
            # Сохраняем ссылку
            helper_links[helper_key]["links"][link_key] = {
                "url": link, 
                "description": description,
                "added_by": user_name
            }
            
            # Создаем сообщение для подтверждения
            success_text = f"✅ Ссылка успешно сохранена!\n\n"
            success_text += f"<b>Описание:</b> {description}\n"
            success_text += f"<b>Ссылка:</b> {link}"
            
            bot.send_message(
                message.chat.id,
                success_text,
                parse_mode='HTML'
            )
            
            # Возвращаемся к управлению ссылками
            show_bot_links(helper_key, message, user_name, message_id)
            
            # Очищаем выбор пользователя
            del user_selection[user_id]
    
    else:
        # Если нет выбора, показываем меню
        send_welcome_with_menu(message.chat.id, user_name)

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("✅ Бот запущен!")
    print("📢 В КАНАЛЕ - ТОЛЬКО ПРОСМОТР:")
    print("   • При нажатии на помощника - просмотр ссылок")
    print("   • Кнопки перехода по ссылкам")
    print("📋 В БОТЕ - ПОЛНОЕ УПРАВЛЕНИЕ:")
    print("   • При нажатии на помощника - управление ссылками")
    print("   • Можно добавлять ссылки (работает!)")
    print("   • Можно удалять только свои ссылки")
    print("=" * 50)
    
    send_menu_to_channel()
    
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")