import telebot
from telebot import types
import time
import os
import logging
from flask import Flask, request
import sys
import threading
import requests  # Добавлен для внешних запросов

# ========== ЛОГИРОВАНИЕ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ВСТАВЬ СВОЙ ТОКЕН СЮДА
TOKEN = "8211032032:AAFUUIgTep0FZdJo0GWmJNBk0j70vrtT2rM"
if not TOKEN:
    logger.error("ТОКЕН НЕ УСТАНОВЛЕН!")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# ========== НАСТРОЙКИ ДЛЯ WEBHOOK ==========
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', '')
if not RENDER_URL:
    logger.warning("RENDER_EXTERNAL_URL не найден, проверь настройки Render")
    RENDER_URL = "http://localhost:5000"

WEBHOOK_URL = f"{RENDER_URL}/webhook"
PORT = int(os.environ.get('PORT', 10000))

# Создаем Flask приложение
app = Flask(__name__)

# ========== ХРАНЕНИЕ ССЫЛОК В ПАМЯТИ ==========
helper_links = {
    "helper1": {
        "name": "Помощник 1", 
        "links": {
            "link1": {"url": "", "description": "Яндекс.Диск", "added_by": ""},
            "link2": {"url": "", "description": "Таблица", "added_by": ""}
        }
    },
    "helper2": {
        "name": "Помощник 2", 
        "links": {
            "link1": {"url": "", "description": "Яндекс.Диск", "added_by": ""},
            "link2": {"url": "", "description": "Таблица", "added_by": ""}
        }
    },
    "helper3": {
        "name": "Помощник 3", 
        "links": {
            "link1": {"url": "", "description": "Яндекс.Диск", "added_by": ""},
            "link2": {"url": "", "description": "Таблица", "added_by": ""}
        }
    }
}

# Словарь для временного хранения состояния выбора помощника
user_selection = {}

# ========== ПОЛУЧЕНИЕ USERNAME БОТА ==========
def get_bot_username():
    try:
        me = bot.get_me()
        logger.info(f"Бот @{me.username} авторизован")
        return me.username
    except Exception as e:
        logger.error(f"Ошибка получения username: {e}")
        return "bot_username"

# ========== УСТАНОВКА КОМАНД ДЛЯ БОТА ==========
def set_bot_commands():
    """Устанавливает список команд для бота - создает кнопку меню с /start"""
    try:
        commands = [
            types.BotCommand("start", "🚀 Запустить бота")
        ]
        bot.set_my_commands(commands)
        logger.info("✅ Команда /start закреплена в меню бота")
    except Exception as e:
        logger.error(f"Ошибка установки команд: {e}")

# ========== СОЗДАНИЕ МЕНЮ ДЛЯ ЛИЧКИ ==========
def create_private_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, 
        row_width=1,
        input_field_placeholder="Выберите помощника"
    )
    btn_helper1 = types.KeyboardButton("Помощник 1")
    btn_helper2 = types.KeyboardButton("Помощник 2")
    btn_helper3 = types.KeyboardButton("Помощник 3")
    keyboard.add(btn_helper1)
    keyboard.add(btn_helper2)
    keyboard.add(btn_helper3)
    return keyboard

# ========== ФУНКЦИЯ ПРИВЕТСТВИЯ С МЕНЮ ==========
def send_welcome_with_menu(chat_id, user_name):
    welcome_text = f"""
<b>Для выбора просмотра/добавления ссылки нажмите на "Помощника" 👇</b>
    """
    
    try:
        bot.send_message(
            chat_id,
            welcome_text,
            parse_mode='HTML',
            reply_markup=create_private_menu()
        )
        logger.info(f"Приветствие отправлено пользователю {user_name}")
    except Exception as e:
        logger.error(f"Ошибка отправки приветствия: {e}")

# ========== ОБРАБОТЧИК КОМАНДЫ /start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_name = message.from_user.first_name
        logger.info(f"Получена команда /start от {user_name}")
        send_welcome_with_menu(message.chat.id, user_name)
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")

# ========== ВЫБОР ПОМОЩНИКА ==========
@bot.message_handler(func=lambda message: message.text in ["Помощник 1", "Помощник 2", "Помощник 3"])
def handle_helper_selection(message):
    try:
        user_name = message.from_user.first_name
        
        if message.text == "Помощник 1":
            show_bot_links("helper1", message, user_name)
        elif message.text == "Помощник 2":
            show_bot_links("helper2", message, user_name)
        elif message.text == "Помощник 3":
            show_bot_links("helper3", message, user_name)
            
    except Exception as e:
        logger.error(f"Ошибка выбора помощника: {e}")

# ========== ПОКАЗ ССЫЛОК В БОТЕ ==========
def show_bot_links(helper_key, message, user_name, edit_message_id=None):
    helper = helper_links[helper_key]
    
    text = f"""
<b>{helper['name']}</b>

"""

    # Ссылка 1 - Яндекс.Диск
    if helper["links"]["link1"]["url"]:
        text += f"""
📁 <b>Яндекс.Диск</b>
{helper['links']['link1']['url']}
<i>Добавил: {helper['links']['link1']['added_by']}</i>

"""
    else:
        text += """
📁 <b>Яндекс.Диск не добавлен</b>

"""
    
    # Ссылка 2 - Таблица
    if helper["links"]["link2"]["url"]:
        text += f"""
📊 <b>Таблица</b>
{helper['links']['link2']['url']}
<i>Добавил: {helper['links']['link2']['added_by']}</i>
"""
    else:
        text += """
📊 <b>Таблица не добавлена</b>
"""
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопки для перехода по ссылкам
    if helper["links"]["link1"]["url"]:
        btn_go1 = types.InlineKeyboardButton(
            text="📁 Перейти на Яндекс.Диск",
            url=helper["links"]["link1"]["url"]
        )
        keyboard.add(btn_go1)
    
    if helper["links"]["link2"]["url"]:
        btn_go2 = types.InlineKeyboardButton(
            text="📊 Перейти к таблице",
            url=helper["links"]["link2"]["url"]
        )
        keyboard.add(btn_go2)
    
    # Кнопки добавления
    btn_add1 = types.InlineKeyboardButton(
        text="➕ Добавить Яндекс.Диск",
        callback_data=f"add_{helper_key}_link1"
    )
    btn_add2 = types.InlineKeyboardButton(
        text="➕ Добавить Таблицу",
        callback_data=f"add_{helper_key}_link2"
    )
    keyboard.add(btn_add1, btn_add2)
    
    # Кнопки удаления (только для своих)
    if helper["links"]["link1"]["url"] and helper["links"]["link1"]["added_by"] == user_name:
        btn_clear1 = types.InlineKeyboardButton(
            text="✖ Удалить Яндекс.Диск",
            callback_data=f"clear_{helper_key}_link1"
        )
        keyboard.add(btn_clear1)
    
    if helper["links"]["link2"]["url"] and helper["links"]["link2"]["added_by"] == user_name:
        btn_clear2 = types.InlineKeyboardButton(
            text="✖ Удалить Таблицу",
            callback_data=f"clear_{helper_key}_link2"
        )
        keyboard.add(btn_clear2)
    
    # Кнопка назад в меню
    btn_back = types.InlineKeyboardButton(
        text="◀ Назад",
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
            except Exception as e:
                logger.error(f"Ошибка редактирования: {e}")
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
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")

# ========== ОБРАБОТКА INLINE-КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data == "back_to_private_menu":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_welcome_with_menu(call.message.chat.id, call.from_user.first_name)
            
        elif call.data.startswith("add_"):
            parts = call.data.split("_")
            if len(parts) >= 3:
                helper_key = parts[1]
                link_key = parts[2]
                
                link_name = "Яндекс.Диск" if link_key == "link1" else "Таблицу"
                
                user_id = call.from_user.id
                user_selection[user_id] = {
                    "helper": helper_key, 
                    "link": link_key,
                    "message_id": call.message.message_id,
                    "chat_id": call.message.chat.id
                }
                
                bot.edit_message_text(
                    f"<b>ДОБАВЛЕНИЕ ССЫЛКИ</b>\n\n"
                    f"Вы выбрали: <b>{link_name}</b>\n\n"
                    f"Отправьте ссылку (должна начинаться с http:// или https://):",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='HTML'
                )
                
        elif call.data.startswith("clear_"):
            parts = call.data.split("_")
            if len(parts) >= 3:
                helper_key = parts[1]
                link_key = parts[2]
                
                link_name = "Яндекс.Диск" if link_key == "link1" else "Таблицу"
                
                helper_links[helper_key]["links"][link_key] = {"url": "", "description": link_name, "added_by": ""}
                
                bot.answer_callback_query(call.id, f"{link_name} удален!")
                
                user_name = call.from_user.first_name
                show_bot_links(helper_key, call.message, user_name, call.message.message_id)
                
    except Exception as e:
        logger.error(f"Ошибка в обработчике callback: {e}")
        try:
            bot.answer_callback_query(call.id, "Произошла ошибка")
        except:
            pass

# ========== ОБРАБОТКА ДОБАВЛЕНИЯ ССЫЛОК ==========
@bot.message_handler(func=lambda message: message.from_user.id in user_selection)
def handle_link_input(message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        text = message.text
        
        if user_id in user_selection and "link" in user_selection[user_id]:
            helper_key = user_selection[user_id]["helper"]
            link_key = user_selection[user_id]["link"]
            message_id = user_selection[user_id]["message_id"]
            
            link_name = "Яндекс.Диск" if link_key == "link1" else "Таблицу"
            link = text.strip()
            
            if not (link.startswith('http://') or link.startswith('https://')):
                bot.reply_to(
                    message,
                    f"<b>ОШИБКА</b>\n\n"
                    f"Ссылка на {link_name} должна начинаться с http:// или https://\n\n"
                    f"Попробуйте еще раз:",
                    parse_mode='HTML'
                )
                return
            
            helper_links[helper_key]["links"][link_key] = {
                "url": link, 
                "description": link_name,
                "added_by": user_name
            }
            
            bot.send_message(
                message.chat.id,
                f"<b>ССЫЛКА СОХРАНЕНА</b>\n\n"
                f"{link_name}: {link}",
                parse_mode='HTML'
            )
            
            show_bot_links(helper_key, message, user_name, message_id)
            del user_selection[user_id]
            
    except Exception as e:
        logger.error(f"Ошибка обработки ссылки: {e}")

# ========== ОБРАБОТКА ВСЕХ ОСТАЛЬНЫХ СООБЩЕНИЙ (ИГНОРИРУЕМ) ==========
@bot.message_handler(func=lambda message: True)
def ignore_all_other_messages(message):
    """Полностью игнорируем все остальные сообщения"""
    logger.info(f"Сообщение от {message.from_user.first_name} проигнорировано")
    # Ничего не делаем, просто пропускаем

# ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ ДЛЯ ВНЕШНЕГО ПИНГА ==========
def external_ping():
    """Пингует свой собственный URL через внешний запрос"""
    while True:
        try:
            # Пингуем свой собственный URL через /health эндпоинт
            ping_url = f"{RENDER_URL}/health"
            response = requests.get(ping_url, timeout=10)
            logger.info(f"🔄 Внешний пинг отправлен на {ping_url}, статус: {response.status_code}")
            
            # Ждем 4 минуты (240 секунд)
            time.sleep(240)
            
        except Exception as e:
            logger.error(f"Ошибка внешнего пинга: {e}")
            time.sleep(60)

# ========== FLASK WEBHOOK ==========
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
            logger.error(f"Ошибка обработки webhook: {e}")
            return 'Error', 500
    else:
        return 'Invalid request', 403

# ========== НАСТРОЙКА WEBHOOK ==========
def setup_webhook():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Попытка установки webhook #{attempt + 1}")
            bot.remove_webhook()
            time.sleep(2)
            
            if RENDER_URL and RENDER_URL != "http://localhost:5000":
                result = bot.set_webhook(url=WEBHOOK_URL)
                if result:
                    logger.info(f"Webhook установлен на {WEBHOOK_URL}")
                    return True
            else:
                logger.warning("RENDER_EXTERNAL_URL не найден")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка установки webhook: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    return False

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║         TELEGRAM BOT STARTING          ║
    ╚════════════════════════════════════════╝
    """)
    
    logger.info("Бот запускается...")
    
    # Получаем информацию о боте
    try:
        bot_info = bot.get_me()
        logger.info(f"Бот: @{bot_info.username}")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    
    # Устанавливаем команды бота (только /start)
    set_bot_commands()
    
    # Запускаем поток для внешнего пинга (это решит проблему!)
    external_ping_thread = threading.Thread(target=external_ping, daemon=True)
    external_ping_thread.start()
    logger.info("✅ Поток внешнего пинга запущен")
    
    # Устанавливаем webhook
    if setup_webhook():
        logger.info("✅ Бот готов к работе! Команда /start закреплена в меню")
        # Запускаем Flask
        app.run(host='0.0.0.0', port=PORT, debug=False)
    else:
        logger.error("❌ Не удалось настроить webhook")
        sys.exit(1)