import asyncio
import random
import re
import os
import base64
import logging
from pyrogram import Client, enums, utils
from pyrogram.raw import functions
from pyrogram.errors import FloodWait, RPCError, SessionPasswordNeeded, AuthKeyUnregistered

# Настройка логирования, чтобы не мусорило
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("pyrogram").setLevel(logging.CRITICAL)

try:
    import qrcode
except ImportError:
    os.system('pip install qrcode')
    import qrcode

# --- НАСТРОЙКИ ---
api_id = 33574840
api_hash = 'b8639fd38e1db0e49bd26c3dcaceb026'
session_name = "Asya_pyro_beast" # Файл сессии
ACC_NAME = "Софья"              # Имя для логов в терминале

app = Client(
    session_name,
    api_id=api_id,
    api_hash=api_hash,
    device_model="Samsung SM-S901B",
    system_version="Android 13",
    app_version="10.0.1",
    no_updates=True # Защита от ошибок ID invalid
)

global_sent_counter = 0

BIO_PHRASES = [
    "Жду тебя в ЛС 🥰", "Самый сочный контент тут 🔞", "Пиши, не стесняйся 💋",
    "Твоя любимая девочка 🔥", "Онлайн 24/7, заходи 🍑", "Хочешь увидеть больше? 😉",
    "Самое вкусное скрыто тут 🍑🔥", "Жду твоего сообщения, котик 💋"
]

# --- ФУНКЦИИ МОДУЛЯ ---

async def update_bio():
    try:
        new_bio = random.choice(BIO_PHRASES)
        await app.update_profile(about=new_bio)
        print(f"✨ [{ACC_NAME}] | БИО ОБНОВЛЕНО: {new_bio}")
    except: pass

async def delete_after(chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try: await app.delete_messages(chat_id, message_id)
    except: pass

def shuffle_emojis(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        emojis = re.findall(r'[🥰🔞💋🍑🔵🍌🙃😀👅🌛🌟👠]', line)
        if len(emojis) > 1:
            temp_emojis = emojis.copy()
            random.shuffle(temp_emojis)
            new_line = line
            for i in range(len(emojis)):
                new_line = new_line.replace(emojis[i], temp_emojis[i], 1)
            new_lines.append(new_line)
        else: new_lines.append(line)
    return '\n'.join(new_lines)

async def get_fixed_text():
    """Генерация рекламного сообщения"""
    raw_text = (
        "🥰 В НАЛИЧИИ 🥰\n\n🔞 ПОРНО 💋\n \n      🍑 ДЕТСКОЕ 🔵\n\n 🍑 ДЕТСКОЕ 🔵\n            🍑 ДЕТСКОЕ 🔵\n\n"
        "        🍌 ШКОЛЬНИЦЫ 🍑\n\n🍌 ШКОЛЬНИЦЫ 🍑\n\n                 🍌 ШКОЛЬНИЦЫ 🍑\n\n"
        "            🙃 ВЗРОСЛОЕ 🍑\n\n    🙃 ВЗРОСЛОЕ 🍑\n\n                     🙃 ВЗРОСЛОЕ 🍑\n\n"
        "                  😀 А ТАК ЖЕ 👅\n\n😀 ВИРТИК 😀\n😀 ВИДЕО ДЗВОНОК 😀\n😀 ФОТОЧКИ 😀\n🍑 БДСМ 🌛\n🌟 ЛЕЗБИ 🌟\n🌟 ПЕДО МАМКИ 🌟\n\n"
        "          🌟 ЖДУ В ЛИЧНЫЕ 👠\n            🌟 СООБЩЕНИЯ 🌟"
    )
    return shuffle_emojis(raw_text)


async def login_with_qr():
    print(f"\n ПРОВЕРКА АККАУНТА [{ACC_NAME}]...")
    try:
        await app.connect()
        me = await app.get_me()
        if me:
            print(f"✅ [{ACC_NAME}] | СЕССИЯ АКТИВНА")
            return
    except:
        print(f"🔑 [{ACC_NAME}] | НУЖЕН ВХОД...")
        if os.path.exists(f"{session_name}.session"):
            os.remove(f"{session_name}.session")
        await app.connect()

    qr_state = await app.invoke(functions.auth.ExportLoginToken(api_id=api_id, api_hash=api_hash, except_ids=[]))
    token_b64 = base64.urlsafe_b64encode(qr_state.token).decode("utf-8").rstrip("=")
    login_url = f"tg://login?token={token_b64}"

    print(f"\n📸 ОТСКАНИРУЙТЕ QR ДЛЯ [{ACC_NAME}]:")
    qr = qrcode.QRCode(); qr.add_data(login_url); qr.print_ascii(invert=True)

    while True:
        try:
            await app.invoke(functions.auth.ImportLoginToken(token=qr_state.token))
            break
        except SessionPasswordNeeded:
            pwd = input(f"🔐 [{ACC_NAME}] Введите 2FA пароль: ")
            await app.check_password(pwd)
            break
        except: await asyncio.sleep(2)
    print(f"✅ [{ACC_NAME}] ВХОД ВЫПОЛНЕН!")

# --- ГЛАВНЫЙ ЦИКЛ ---

async def infinite_worker():
    await login_with_qr()
    print(f"\n🚀 [{ACC_NAME}] СТАРТ РАБОТЫ: ЗВЕРЬ V7 АКТИВИРОВАН\n" + "="*40)
    
    global global_sent_counter
    while True:
        try:
            filters = await app.invoke(functions.messages.GetDialogFilters())
            
            for folder in filters:
                if not hasattr(folder, "title") or "SNIPER" in str(folder.title).upper():
                    continue
                
                folder_name = str(folder.title)
                print(f"\n📂 [{ACC_NAME}] | ПАПКА: {folder_name}")
                
                for peer in folder.include_peers:
                    try:
                        if hasattr(peer, "channel_id"): chat_id = utils.get_channel_id(peer.channel_id)
                        elif hasattr(peer, "chat_id"): chat_id = -peer.chat_id
                        else: continue

                        # Отправка
                        text = await get_fixed_text()
                        msg = await app.send_message(chat_id, text, disable_web_page_preview=True)
                        global_sent_counter += 1
                        try:
                            chat_info = await app.get_chat(chat_id)
                            chat_title = chat_info.title or chat_info.first_name or "Без названия"
                        except Exception:
                            chat_title = f"ID: {chat_id}" 
                        
                        # КД и БИО
                        cd = random.randint(6, 16)

                        remains_to_bio = 5 - (global_sent_counter % 5)

                        if remains_to_bio == 0: remains_to_bio = 5

                        print(f"📨 [{ACC_NAME}] | ✅[{global_sent_counter}] Сообщение -> 📂{chat_title} ушло! | КД: {cd} сек. | До БИО: {remains_to_bio}")
                        
                        if global_sent_counter % 5 == 0: 
                            asyncio.create_task(update_bio())

                        # Удаление рекламы из чата через 20 мин
                        asyncio.create_task(delete_after(chat_id, msg.id, 1200))
                        
                        await asyncio.sleep(cd)

                    except FloodWait as e:
                        print(f"🛑 [{ACC_NAME}] | ФЛУД! Спим {e.value} сек.")
                        await asyncio.sleep(e.value)
                    except Exception: continue
                
                print(f"⌛ [{ACC_NAME}] | Папка '{folder_name}' готова. Отдых 60 сек.")
                await asyncio.sleep(60)

        except Exception as e:
            print(f"❌ [{ACC_NAME}] | ОШИБКА ЦИКЛА: {e}")
            await asyncio.sleep(15)

if __name__ == "__main__":
    try:
        app.run(infinite_worker())
    except KeyboardInterrupt:
        print(f"\n🛑 [{ACC_NAME}] Работа остановлена.")