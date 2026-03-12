import telebot
from telebot import types
import time
import os
import threading
import logging
from flask import Flask, request
import sys

# ========== ИСПРАВЛЕННОЕ ЛОГИРОВАНИЕ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Было asime, стало asctime
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ВСТАВЬ СВОЙ ТОКЕН СЮДА
TOKEN = "8211032032:AAFUUIgTep0FZdJo0GWmJNBk0j70vrtT2rM"
if not TOKEN:
    logger.error("❌ ТОКЕН НЕ УСТАНОВЛЕН!")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# ========== НАСТРОЙКИ ДЛЯ WEBHOOK ==========
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', '')
if not RENDER_URL:
    logger.warning("⚠️ RENDER_EXTERNAL_URL не найден, проверь настройки Render")
    # Для локального тестирования
    RENDER_URL = "http://localhost:5000"

WEBHOOK_URL = f"{RENDER_URL}/webhook"
PORT = int(os.environ.get('PORT', 10000))

# Создаем Flask приложение
app = Flask(__name__)

# ========== НАСТРОЙКИ ==========
try:
    CHANNEL_ID = -1003857838981  # ID твоего канала
    CHANNEL_LINK = "https://t.me/+gPXyWBWPB2FkYmZi"  # Ссылка на канал
    logger.info(f"✅ Настройки загружены: CHANNEL_ID={CHANNEL_ID}")
except Exception as e:
    logger.error(f"❌ Ошибка в настройках: {e}")
    CHANNEL_ID = None
    CHANNEL_LINK = ""

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
    try:
        me = bot.get_me()
        logger.info(f"✅ Бот @{me.username} авторизован")
        return me.username
    except Exception as e:
        logger.error(f"❌ Ошибка получения username: {e}")
        return "bot_username"

# ========== СОЗДАНИЕ INLINE-МЕНЮ ДЛЯ КАНАЛА ==========
def create_channel_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    btn_helper1 = types.InlineKeyboardButton(
        text="👤 Помощник 1",
        callback_data="channel_show_helper1"
    )
    btn_helper2 = types.InlineKeyboardButton(
        text="👤 Помощник 2",
        callback_data="channel_show_helper2"
    )
    btn_helper3 = types.InlineKeyboardButton(
        text="👤 Помощник 3",
        callback_data="channel_show_helper3"
    )
    
    bot_username = get_bot_username()
    btn_bot = types.InlineKeyboardButton(
        text="🤖 Открыть бота для управления",
        url=f"https://t.me/{bot_username}"
    )
    
    keyboard.add(btn_helper1)
    keyboard.add(btn_helper2)
    keyboard.add(btn_helper3)
    keyboard.add(btn_bot)
    
    return keyboard

# ========== СОЗДАНИЕ МЕНЮ ДЛЯ ЛИЧКИ ==========
def create_private_menu():
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
    if not CHANNEL_ID:
        logger.warning("⚠️ CHANNEL_ID не установлен, пропускаем отправку в канал")
        return
        
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
        logger.info("✅ Меню отправлено в канал")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в канал: {e}")

# ========== ПРОВЕРКА ПОДПИСКИ ==========
def check_subscription(user_id):
    if not CHANNEL_ID:
        return True  # Если нет канала, считаем что подписка не нужна
        
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        logger.error(f"❌ Ошибка проверки подписки для пользователя {user_id}: {e}")
        return False

# ========== ФУНКЦИЯ ПРИВЕТСТВИЯ С МЕНЮ ==========
def send_welcome_with_menu(chat_id, user_name):
    welcome_text = f"""
    🎉 <b>ПРИВЕТСТВУЮ, {user_name}!</b>
    
    👇 <b>Выбери помощника для управления ссылками:</b>
    """
    
    try:
        bot.send_message(
            chat_id,
            welcome_text,
            parse_mode='HTML',
            reply_markup=create_private_menu()
        )
        logger.info(f"✅ Приветствие отправлено пользователю {user_name} (ID: {chat_id})")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки приветствия: {e}")

# ========== ОБРАБОТКА НОВЫХ УЧАСТНИКОВ КАНАЛА ==========
@bot.chat_member_handler()
def handle_new_member(update):
    if not CHANNEL_ID:
        return
        
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
            logger.info("✅ Приветствие отправлено новому участнику канала")
        except Exception as e:
            logger.error(f"❌ Ошибка приветствия нового участника: {e}")

# ========== ОБРАБОТКА СООБЩЕНИЙ В КАНАЛЕ ==========
@bot.channel_post_handler(func=lambda message: True)
def handle_channel_posts(message):
    if message.text and "отчет" in message.text.lower():
        try:
            bot.send_message(
                message.chat.id,
                """📋 <b>МЕНЮ ПОМОЩНИКОВ</b> 
 <b> 👇 Нажми на помощника для просмотра ссылок</b> """,
                parse_mode='HTML',
                reply_markup=create_channel_menu()
            )
            logger.info("✅ Меню отправлено по команде 'отчет'")
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения в канале: {e}")

# ========== ПОКАЗ ССЫЛОК В КАНАЛЕ ==========
def show_channel_links(helper_key, call):
    helper = helper_links[helper_key]
    
    text = f"<b>{helper['name']}</b>\n\n"
    
    if helper["links"]["link1"]["url"]:
        text += f"🔗 <b>Ссылка 1:</b> {helper['links']['link1']['description']}\n"
        text += f"🔗 {helper['links']['link1']['url']}\n"
        text += f"👤 Добавил: {helper['links']['link1']['added_by']}\n\n"
    else:
        text += f"❌ Ссылка 1 не добавлена\n\n"
    
    if helper["links"]["link2"]["url"]:
        text += f"🔗 <b>Ссылка 2:</b> {helper['links']['link2']['description']}\n"
        text += f"🔗 {helper['links']['link2']['url']}\n"
        text += f"👤 Добавил: {helper['links']['link2']['added_by']}\n\n"
    else:
        text += f"❌ Ссылка 2 не добавлена\n\n"
    
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
    
    btn_back = types.InlineKeyboardButton(
        text="◀️ Назад к меню",
        callback_data="back_to_channel_menu"
    )
    keyboard.add(btn_back)
    
    try:
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=keyboard
        )
        logger.info(f"✅ Показаны ссылки {helper['name']} в канале")
    except Exception as e:
        logger.error(f"❌ Ошибка редактирования сообщения: {e}")
        try:
            bot.send_message(
                call.message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")

# ========== ПОКАЗ ССЫЛОК В БОТЕ ==========
def show_bot_links(helper_key, message, user_name, edit_message_id=None):
    helper = helper_links[helper_key]
    
    text = f"<b>{helper['name']}</b>\n\n"
    
    if helper["links"]["link1"]["url"]:
        text += f"🔗 <b>Ссылка 1:</b> {helper['links']['link1']['description']}\n"
        text += f"🔗 {helper['links']['link1']['url']}\n"
        text += f"👤 Добавил: {helper['links']['link1']['added_by']}\n\n"
    else:
        text += f"❌ Ссылка 1 не добавлена\n\n"
    
    if helper["links"]["link2"]["url"]:
        text += f"🔗 <b>Ссылка 2:</b> {helper['links']['link2']['description']}\n"
        text += f"🔗 {helper['links']['link2']['url']}\n"
        text += f"👤 Добавил: {helper['links']['link2']['added_by']}\n\n"
    else:
        text += f"❌ Ссылка 2 не добавлена\n\n"
    
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
    
    btn_add1 = types.InlineKeyboardButton(
        text="➕ Добавить ссылку 1",
        callback_data=f"add_{helper_key}_link1"
    )
    btn_add2 = types.InlineKeyboardButton(
        text="➕ Добавить ссылку 2",
        callback_data=f"add_{helper_key}_link2"
    )
    keyboard.add(btn_add1, btn_add2)
    
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
    
    btn_back = types.InlineKeyboardButton(
        text="◀️ Назад в меню",
        callback_data="back_to_private_menu"
    )
    keyboard.add(btn_back)
    
    try:
        if edit_message_id:
            try:
                bot.edit_message_text(
                    text,
                    message.chat.id,
                    edit_message_id,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
                logger.info(f"✅ Обновлены ссылки {helper['name']} для пользователя {user_name}")
            except Exception as e:
                logger.error(f"❌ Ошибка редактирования: {e}")
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
            logger.info(f"✅ Показаны ссылки {helper['name']} пользователю {user_name}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")

# ========== ОБРАБОТКА INLINE-КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
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
        elif call.data == "back_to_private_menu":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(
                call.message.chat.id,
                "👇 <b>Выбери помощника для управления ссылками:</b>",
                parse_mode='HTML',
                reply_markup=create_private_menu()
            )
        elif call.data.startswith("add_"):
            parts = call.data.split("_")
            if len(parts) >= 3:
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
                    f"📝 Отправь мне <b>описание</b> для ссылки:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='HTML'
                )
                logger.info(f"✅ Пользователь {call.from_user.first_name} начал добавление ссылки {link_key} для {helper_key}")
        elif call.data.startswith("clear_"):
            parts = call.data.split("_")
            if len(parts) >= 3:
                helper_key = parts[1]
                link_key = parts[2]
                
                helper_links[helper_key]["links"][link_key] = {"url": "", "description": "", "added_by": ""}
                
                bot.answer_callback_query(call.id, "✅ Ссылка удалена!")
                logger.info(f"✅ Пользователь {call.from_user.first_name} удалил ссылку {link_key} для {helper_key}")
                
                user_name = call.from_user.first_name
                show_bot_links(helper_key, call.message, user_name, call.message.message_id)
    except Exception as e:
        logger.error(f"❌ Ошибка в обработчике callback: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        except:
            pass

# ========== ОБРАБОТКА КОМАНДЫ /start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        
        logger.info(f"📨 Получена команда /start от {user_name} (ID: {user_id})")
        
        is_subscribed = check_subscription(user_id)
        
        if not is_subscribed and CHANNEL_ID:
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
            logger.info(f"⚠️ Пользователь {user_name} не подписан на канал")
            return
        
        send_welcome_with_menu(message.chat.id, user_name)
    except Exception as e:
        logger.error(f"❌ Ошибка в /start: {e}")

# ========== ВЫБОР ПОМОЩНИКА В ЛИЧКЕ ==========
@bot.message_handler(func=lambda message: message.text in ["👤 Помощник 1", "👤 Помощник 2", "👤 Помощник 3"])
def handle_helper_selection(message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        
        logger.info(f"📨 Пользователь {user_name} выбрал: {message.text}")
        
        if not check_subscription(user_id) and CHANNEL_ID:
            return
        
        if message.text == "👤 Помощник 1":
            show_bot_links("helper1", message, user_name)
        elif message.text == "👤 Помощник 2":
            show_bot_links("helper2", message, user_name)
        elif message.text == "👤 Помощник 3":
            show_bot_links("helper3", message, user_name)
    except Exception as e:
        logger.error(f"❌ Ошибка выбора помощника: {e}")

# ========== ОБРАБОТКА ОПИСАНИЯ И ССЫЛКИ ==========
@bot.message_handler(func=lambda message: True)
def handle_link_input(message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        text = message.text
        
        if not check_subscription(user_id) and CHANNEL_ID:
            return
        
        if user_id in user_selection and "link" in user_selection[user_id]:
            if "waiting_for" not in user_selection[user_id]:
                user_selection[user_id]["description"] = text
                user_selection[user_id]["waiting_for"] = "url"
                bot.reply_to(
                    message,
                    "✅ Описание сохранено!\n\nТеперь отправь мне <b>ссылку</b> (должна начинаться с http:// или https://):",
                    parse_mode='HTML'
                )
                logger.info(f"✅ Пользователь {user_name} ввел описание: {text}")
            
            elif user_selection[user_id]["waiting_for"] == "url":
                helper_key = user_selection[user_id]["helper"]
                link_key = user_selection[user_id]["link"]
                description = user_selection[user_id]["description"]
                link = text.strip()
                message_id = user_selection[user_id]["message_id"]
                
                if not (link.startswith('http://') or link.startswith('https://')):
                    bot.reply_to(
                        message,
                        "❌ Это не похоже на ссылку\n\nСсылка должна начинаться с http:// или https://\nПопробуй еще раз:"
                    )
                    logger.warning(f"⚠️ Пользователь {user_name} ввел некорректную ссылку: {link}")
                    return
                
                helper_links[helper_key]["links"][link_key] = {
                    "url": link, 
                    "description": description,
                    "added_by": user_name
                }
                
                success_text = f"✅ Ссылка успешно сохранена!\n\n"
                success_text += f"<b>Описание:</b> {description}\n"
                success_text += f"<b>Ссылка:</b> {link}"
                
                bot.send_message(
                    message.chat.id,
                    success_text,
                    parse_mode='HTML'
                )
                logger.info(f"✅ Пользователь {user_name} добавил ссылку для {helper_key}/{link_key}")
                
                show_bot_links(helper_key, message, user_name, message_id)
                del user_selection[user_id]
        else:
            send_welcome_with_menu(message.chat.id, user_name)
    except Exception as e:
        logger.error(f"❌ Ошибка обработки ссылки: {e}")

# ========== FLASK WEBHOOK ОБРАБОТЧИК ==========
@app.route('/', methods=['GET'])
def index():
    return "Bot is running!", 200

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
        except Exception as e:
            logger.error(f"❌ Ошибка обработки webhook: {e}")
            return 'Error', 500
    else:
        logger.warning(f"⚠️ Получен запрос с неправильным content-type: {request.headers.get('content-type')}")
        return 'Invalid request', 403

# ========== ИНИЦИАЛИЗАЦИЯ И ЗАПУСК ==========
def setup_webhook():
    """Настройка webhook при запуске"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Попытка установки webhook #{attempt + 1}")
            bot.remove_webhook()
            time.sleep(2)
            
            if RENDER_URL and RENDER_URL != "http://localhost:5000":
                result = bot.set_webhook(url=WEBHOOK_URL)
                if result:
                    logger.info(f"✅ Webhook успешно установлен на {WEBHOOK_URL}")
                    return True
                else:
                    logger.error(f"❌ Не удалось установить webhook (попытка {attempt + 1})")
            else:
                logger.warning("⚠️ RENDER_EXTERNAL_URL не найден, webhook не установлен")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка установки webhook (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                logger.error("❌ Не удалось установить webhook после всех попыток")
                return False

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║         TELEGRAM BOT STARTING          ║
    ╚════════════════════════════════════════╝
    """)
    
    logger.info("✅ Бот инициализируется...")
    logger.info(f"📢 RENDER_URL: {RENDER_URL}")
    logger.info(f"🔧 PORT: {PORT}")
    
    # Получаем информацию о боте
    try:
        bot_info = bot.get_me()
        logger.info(f"🤖 Бот: @{bot_info.username} (ID: {bot_info.id})")
    except Exception as e:
        logger.error(f"❌ Не удалось получить информацию о боте: {e}")
    
    # Отправляем меню в канал (если бот уже добавлен в канал)
    if CHANNEL_ID:
        try:
            send_menu_to_channel()
        except Exception as e:
            logger.error(f"⚠️ Не удалось отправить меню в канал: {e}")
    
    # Устанавливаем webhook
    webhook_set = setup_webhook()
    
    if webhook_set:
        logger.info("🚀 Запуск Flask сервера для приема webhook'ов...")
        # Запускаем Flask в основном потоке
        app.run(host='0.0.0.0', port=PORT, debug=False)
    else:
        logger.error("❌ Не удалось настроить webhook. Бот не будет работать.")
        sys.exit(1)