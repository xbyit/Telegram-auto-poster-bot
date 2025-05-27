import os
import json
import time
import random
import requests
import telebot
from telebot import types
import threading

TOKEN = 'YOUR_TOKEN'
bot = telebot.TeleBot(TOKEN)

DATA_DIR = 'users'
os.makedirs(DATA_DIR, exist_ok=True)

CONTENT_TYPES = ['برمجة', 'أمن معلومات', 'شعر', 'معلومات علمية']
LANGUAGES = ['ar', 'en']
user_states = {}
last_sent = {}

def get_user_file(user_id):
    return os.path.join(DATA_DIR, f'{user_id}.json')

def load_user(user_id):
    path = get_user_file(user_id)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"channels": {}}

def save_user(user_id, data):
    with open(get_user_file(user_id), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def gpt(t, lang='ar'):
    if lang == 'en':
        t = f"Translate this prompt to English and generate content: {t}"
    url = f"https://dev-pycodz-blackbox.pantheonsite.io/DEvZ44d/deepseek.php?text={requests.utils.quote(t)}"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("response", "")
    except:
        return ""

def generate_topic(content_type, lang):
    if lang == 'en':
        return gpt(f"Suggest a one-line topic about {content_type} in English.", lang)
    else:
        return gpt(f"اقترح لي فقط عنوان فكرة محتوى {content_type} باللغة العربية، في جملة واحدة فقط، بدون شرح أو تفاصيل أو نقاط أو أمثلة.", lang)

def generate_content(topic, content_type, lang):
    if lang == 'en':
        return gpt(f"Write a short {content_type} post (max 1000 characters) in English about: {topic}.")
    else:
        return gpt(f"اكتب لي منشورًا {content_type} باللغة العربية بناءً على هذه الفكرة: {topic}، اجعله نصًا متصلًا وسلسًا بدون عناوين أو تقسيمات، ولا تضف أي فواصل أو نقاط مرقمة.")

def generate_image(topic, lang):
    if lang == 'en':
        prompt = f"Create a detailed description for an image about this topic: {topic}."
    else:
        prompt = f"أنشئ وصفًا تفصيليًا لصورة تعبر عن هذا العنوان: {topic}."
    desc = gpt(prompt, lang)
    url = f'https://dev-pycodz-blackbox.pantheonsite.io/DEvZ44d/imger.php?img={requests.utils.quote(desc)}'
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open('img.jpg', 'wb') as f:
                f.write(r.content)
            return 'img.jpg'
    except:
        pass
    return None

@bot.message_handler(commands=['start'])
def start(msg):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('إضافة قناة', callback_data='add_channel'))
    kb.add(types.InlineKeyboardButton('عرض قنواتي', callback_data='show_channels'))
    kb.add(types.InlineKeyboardButton('حذف قناة', callback_data='delete_channel'))
    kb.add(types.InlineKeyboardButton('تعديل توقيت قناة', callback_data='set_interval'))
    bot.send_message(msg.chat.id, 'مرحبًا بك، يمكنك إدارة قنواتك ونوع المحتوى من هنا.', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data == 'add_channel')
def ask_channel_id(call):
    user_states[call.message.chat.id] = {'step': 'await_channel'}
    bot.send_message(call.message.chat.id, 'أرسل آيدي القناة (مثل: @mychannel أو -100xxxxxxxxxx)')

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'await_channel')
def ask_content_type(msg):
    user_states[msg.chat.id]['channel'] = msg.text.strip()
    user_states[msg.chat.id]['step'] = 'await_type'
    kb = types.InlineKeyboardMarkup()
    for t in CONTENT_TYPES:
        kb.add(types.InlineKeyboardButton(t, callback_data=f'set_type_{t}'))
    bot.send_message(msg.chat.id, 'اختر نوع المحتوى لهذه القناة:', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_type_'))
def ask_language(call):
    content_type = call.data.split('_', 2)[2]
    user_states[call.message.chat.id]['type'] = content_type
    user_states[call.message.chat.id]['step'] = 'await_lang'
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('العربية', callback_data='set_lang_ar'))
    kb.add(types.InlineKeyboardButton('English', callback_data='set_lang_en'))
    bot.send_message(call.message.chat.id, 'اختر اللغة:', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_lang_'))
def save_channel_setting(call):
    lang = call.data.split('_')[-1]
    uid = call.message.chat.id
    ch = user_states[uid]['channel']
    tp = user_states[uid]['type']
    data = load_user(uid)
    data['channels'][ch] = {"language": lang, "type": tp, "interval": 5}
    save_user(uid, data)
    user_states.pop(uid)
    bot.send_message(uid, f"تم حفظ القناة: {ch}\nالنوع: {tp}\nاللغة: {'العربية' if lang == 'ar' else 'English'}")

@bot.callback_query_handler(func=lambda call: call.data == 'show_channels')
def show_channels(call):
    data = load_user(call.message.chat.id)
    if not data['channels']:
        bot.send_message(call.message.chat.id, 'لا توجد قنوات محفوظة.')
        return
    text = 'قنواتك:\n'
    for ch, conf in data['channels'].items():
        text += f"{ch} | {conf['type']} | {'AR' if conf['language'] == 'ar' else 'EN'} | كل {conf.get('interval', 5)} ساعات\n"
    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == 'delete_channel')
def ask_channel_to_delete(call):
    data = load_user(call.message.chat.id)
    if not data['channels']:
        bot.send_message(call.message.chat.id, 'لا توجد قنوات لحذفها.')
        return
    kb = types.InlineKeyboardMarkup()
    for ch in data['channels']:
        kb.add(types.InlineKeyboardButton(ch, callback_data=f'del_{ch}'))
    bot.send_message(call.message.chat.id, 'اختر القناة التي تريد حذفها:', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
def delete_channel(call):
    ch = call.data[4:]
    data = load_user(call.message.chat.id)
    if ch in data['channels']:
        del data['channels'][ch]
        save_user(call.message.chat.id, data)
        bot.send_message(call.message.chat.id, f'تم حذف القناة: {ch}')

@bot.callback_query_handler(func=lambda call: call.data == 'set_interval')
def choose_channel_for_interval(call):
    data = load_user(call.message.chat.id)
    if not data['channels']:
        bot.send_message(call.message.chat.id, 'لا توجد قنوات لتعديل توقيتها.')
        return
    kb = types.InlineKeyboardMarkup()
    for ch in data['channels']:
        kb.add(types.InlineKeyboardButton(ch, callback_data=f'sel_interval_{ch}'))
    bot.send_message(call.message.chat.id, 'اختر القناة التي تريد تعديل توقيتها:', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sel_interval_'))
def ask_new_interval(call):
    ch = call.data.replace('sel_interval_', '')
    user_states[call.message.chat.id] = {'step': 'await_interval', 'channel': ch}
    bot.send_message(call.message.chat.id, 'أرسل عدد الساعات بين كل منشور (مثال: 6)')

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'await_interval')
def set_new_interval(msg):
    try:
        hours = int(msg.text.strip())
        ch = user_states[msg.chat.id]['channel']
        data = load_user(msg.chat.id)
        if ch in data['channels']:
            data['channels'][ch]['interval'] = hours
            save_user(msg.chat.id, data)
            bot.send_message(msg.chat.id, f'تم تعديل التوقيت لقناة {ch} إلى كل {hours} ساعة.')
        else:
            bot.send_message(msg.chat.id, 'لم يتم العثور على القناة.')
    except:
        bot.send_message(msg.chat.id, 'الرجاء إدخال رقم صحيح.')
    user_states.pop(msg.chat.id, None)

def auto_post():
    while True:
        for filename in os.listdir(DATA_DIR):
            uid = int(filename.replace('.json', ''))
            with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
            for ch, conf in data['channels'].items():
                now = time.time()
                last = last_sent.get((uid, ch), 0)
                if now - last >= conf.get('interval', 5) * 3600:
                    topic = generate_topic(conf['type'], conf['language'])
                    if not topic:
                        continue
                    text = generate_content(topic, conf['type'], conf['language'])
                    img = generate_image(topic, conf['language'])
                    try:
                        if img:
                            with open(img, 'rb') as photo:
                                bot.send_photo(ch, photo, caption=text)
                        else:
                            bot.send_message(ch, text)
                        last_sent[(uid, ch)] = now
                    except Exception as e:
                        print(f"خطأ في النشر إلى {ch}: {e}")
        time.sleep(60)

threading.Thread(target=auto_post).start()
bot.infinity_polling()
