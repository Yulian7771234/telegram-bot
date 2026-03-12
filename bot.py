
import telebot
from telebot import types
import time
import os
import logging
from flask import Flask, request
import sys

# ========== ЛОГИРОВАНИЕ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ВСТАВЬ СВОЙ ТОКЕН
TOKEN = "8211032032:AAFUUIgTep0FZdJo0GWmJNBk0j70vrtT2rM"
if not TOKEN:
    logger.error("❌ ТОКЕН НЕ УСТАНОВЛЕН!")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# ========== НАСТРОЙКИ ==========
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', '')
PORT = int(os.environ.get('PORT', 10000))
WEBHOOK_URL = f"{RENDER_URL}/webhook" if RENDER_URL else None

# Создаем Flask приложение
app = Flask(__name__)

# ========== ДАННЫЕ ==========
helper_links = {
    "helper1": {"name": "Помощник 1", "links": {
        "link1": {"url": "", "description": "Яндекс.Диск", "added_by": ""},
        "link2": {"url": "", "description": "Таблица", "added_by": ""}
    }},
    "helper2": {"name": "Помощник 2", "links": {
        "link1": {"url": "", "description": "Яндекс.Диск", "added_by": ""},
        "link2": {"url": "", "description": "Таблица", "added_by": ""}
    }},
    "helper3": {"name": "Помощник 3", "links": {
        "link1": {"url": "", "description": "Яндекс.Диск", "added_by": ""},
        "link2": {"url": "", "description": "Таблица", "added_by": ""}
    }}
}

user_selection = {}

# ========== ФУНКЦИИ ==========
def create_private_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        types.KeyboardButton("👤 Помощник 1"),
        types.KeyboardButton("👤 Помощник 2"),
        types.KeyboardButton("👤 Помощник 3")
    )
    return keyboard

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = f"""
    🎉 <b>ПРИВЕТСТВУЮ, {message.from_user.first_name}!</b>
    
    👇 <b>Выбери помощника для управления ссылками:</b>
    
    📌 <b>Для каждого можно добавить:</b>
    • 🔗 Яндекс.Диск
    • 📊 Таблица
    """
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='HTML',
        reply_markup=create_private_menu()
    )

@bot.message_handler(func=lambda m: m.text in ["👤 Помощник 1", "👤 Помощник 2", "👤 Помощник 3"])
def helper_menu(message):
    helper_key = {"👤 Помощник 1": "helper1", "👤 Помощник 2": "helper2", "👤 Помощник 3": "helper3"}[message.text]
    helper = helper_links[helper_key]
    
    text = f"<b>{helper['name']}</b>\n\n"
    
    # Яндекс.Диск
    if helper["links"]["link1"]["url"]:
        text += f"🔗 <b>Яндекс.Диск:</b>\n{helper['links']['link1']['url']}\n👤 {helper['links']['link1']['added_by']}\n\n"
    else:
        text += "❌ Яндекс.Диск не добавлен\n\n"
    
    # Таблица
    if helper["links"]["link2"]["url"]:
        text += f"📊 <b>Таблица:</b>\n{helper['links']['link2']['url']}\n👤 {helper['links']['link2']['added_by']}\n\n"
    else:
        text += "❌ Таблица не добавлена\n\n"
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if helper["links"]["link1"]["url"]:
        keyboard.add(types.InlineKeyboardButton("🔗 Открыть Яндекс.Диск", url=helper["links"]["link1"]["url"]))
    if helper["links"]["link2"]["url"]:
        keyboard.add(types.InlineKeyboardButton("📊 Открыть Таблицу", url=helper["links"]["link2"]["url"]))
    
    keyboard.add(
        types.InlineKeyboardButton("➕ Добавить Яндекс.Диск", callback_data=f"add_{helper_key}_link1"),
        types.InlineKeyboardButton("➕ Добавить Таблицу", callback_data=f"add_{helper_key}_link2")
    )
    
    if helper["links"]["link1"]["url"] and helper["links"]["link1"]["added_by"] == message.from_user.first_name:
        keyboard.add(types.InlineKeyboardButton("🗑 Удалить Яндекс.Диск", callback_data=f"clear_{helper_key}_link1"))
    if helper["links"]["link2"]["url"] and helper["links"]["link2"]["added_by"] == message.from_user.first_name:
        keyboard.add(types.InlineKeyboardButton("🗑 Удалить Таблицу", callback_data=f"clear_{helper_key}_link2"))
    
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "back_to_main":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
        return
    
    if call.data.startswith("add_"):
        _, helper, link = call.data.split("_")
        user_selection[call.from_user.id] = {"helper": helper, "link": link}
        link_name = "Яндекс.Диск" if link == "link1" else "Таблицу"
        bot.edit_message_text(
            f"📝 Отправь ссылку на {link_name}:",
            call.message.chat.id,
            call.message.message_id
        )
    
    if call.data.startswith("clear_"):
        _, helper, link = call.data.split("_")
        helper_links[helper]["links"][link] = {"url": "", "description": "", "added_by": ""}
        bot.answer_callback_query(call.id, "✅ Удалено!")
        helper_menu(call.message)

@bot.message_handler(func=lambda m: True)
def handle_link(m):
    if m.from_user.id in user_selection:
        sel = user_selection[m.from_user.id]
        link = m.text.strip()
        
        if not (link.startswith('http://') or link.startswith('https://')):
            bot.reply_to(m, "❌ Нужно отправить ссылку, начинающуюся с http:// или https://")
            return
        
        link_name = "Яндекс.Диск" if sel["link"] == "link1" else "Таблицу"
        helper_links[sel["helper"]]["links"][sel["link"]] = {
            "url": link, "description": link_name, "added_by": m.from_user.first_name
        }
        
        bot.send_message(m.chat.id, f"✅ {link_name} сохранен!")
        del user_selection[m.from_user.id]
        helper_menu(m)
    else:
        bot.reply_to(m, "❌ Используй /start")

# ========== FLASK ==========
@app.route('/', methods=['GET'])
def index():
    return "Bot is running!", 200

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid request', 403

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    # Удаляем старый вебхук и устанавливаем новый
    if RENDER_URL:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"✅ Webhook установлен на {WEBHOOK_URL}")
    
    # ЗАПУСКАЕМ FLASK (это главное!)
    app.run(host='0.0.0.0', port=PORT)