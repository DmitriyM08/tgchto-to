import asyncio
import random
import re
import os, time
import qrcode
from telethon import TelegramClient, functions, errors

# --- НАСТРОЙКИ ---
api_id = 33574840
api_hash = 'b8639fd38e1db0e49bd26c3dcaceb026'
session_name = "Asya_telethon_beast"

BIO_PHRASES = [
    "Жду тебя в ЛС 🥰", "Самый сочный контент тут 🔞", "Пиши, не стесняйся 💋",
    "Твоя любимая девочка 🔥", "Онлайн 24/7, заходи 🍑", "Хочешь увидеть больше? 😉",
    "Самое вкусное скрыто тут 🍑🔥", "Жду твоего сообщения, котик 💋"
]

client = TelegramClient(session_name, api_id, api_hash, device_model="Samsung SM-S901B")

# --- ФУНКЦИИ ---

def shuffle_emojis(text):
    if not text: return "Проверка связи 🌟"
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
        "🥰 В НАЛИЧИИ 🥰\n\n🔞 ПOРН0 💋\n \n      🍑 Д3ТСК0E 🔵\n\n 🍑 ДЕТСК0Е 🔵\n            🍑 ДЕТСКoЕ 🔵\n\n"
        "        🍌 ШК0ЛЬHNЦЫ 🍑\n\n🍌 ШКoЛЬHNЦЫ 🍑\n\n                 🍌 ШК0ЛЬHИЦЫ 🍑\n\n"
        "            🙃 ВЗРОСЛОЕ 🍑\n\n    🙃 ВЗРОСЛOЕ 🍑\n\n                     🙃 ВЗРОСЛОЕ 🍑\n\n"
        "                  😀 А ТАК ЖЕ 👅\n\n😀 ВИРТИК 😀\n😀 ВИДЕО ДЗВ0НОК 😀\n😀 ФOТ0ЧКИ 😀\n🍑 БДCM 🌛\n🌟 ЛЕ3БИ 🌟\n🌟 ПEД0 МАМКИ 🌟\n\n"
        "          🌟 ЖДУ В ЛИЧНЫЕ 👠\n            🌟 СО0БЩЕНИЯ 🌟"
        "       💋СЛИВЫ БЛОГЕРОВ 1500+ ФОТ0🍑400+ ВИДЕ0 ПО ОЧЕНЬ ДЕШЕВОЙ ЦЕНЕ🌟"
    )
    return shuffle_emojis(raw_text)

async def update_bio():
    """Смена описания профиля"""
    try:
        new_bio = random.choice(BIO_PHRASES)
        await client(functions.account.UpdateProfileRequest(about=new_bio))
        print(f"✨ [БИО] Обновлено на: {new_bio}")
    except Exception as e:
        print(f"⚠️ Ошибка смены БИО: {e}")

async def send_report(text):
    """Отчет в Избранное"""
    try:
        await client.send_message("me", f"📊 **Отчет:**\n{text}")
    except: pass

async def login_logic():
    await client.connect()
    if not await client.is_user_authorized():
        print("🔑 Вход не выполнен. Генерирую QR...")
        qr_login = await client.qr_login()
        qr = qrcode.QRCode()
        qr.add_data(qr_login.url)
        qr.print_ascii(invert=True)
        try:
            await qr_login.wait()
            print("✅ Вход подтвержден!")
        except Exception as e:
            print(f"❌ Ошибка: {e}"); return False
    return True

# --- ГЛАВНЫЙ ЦИКЛ ---
async def deleted_delayed(peer, msg_id, delay):
    await asyncio.sleep(delay)
    try:
        await client.delete_messages(peer, [msg_id])
    except Exception as e:
        print(f"Не удалось удалить: {e}")

async def main():
    if not await login_logic(): return
    
    sent_counter = 0 # Общий счетчик
    bio_trigger = random.randint(3, 5) # Через сколько сообщений обновить БИО первый раз
    messages_since_last_bio = 0 # Счетчик сообщений с момента последнего обновления БИО

    print("\n🚀 АСЯ ЗАПУЩЕНА. МОНИТОРИНГ ВКЛЮЧЕН.")

    while True:
        try:
            response = await client(functions.messages.GetDialogFiltersRequest())
            
            for folder in response.filters:
                if not hasattr(folder, 'title') or not folder.title: continue
                folder_title = folder.title.text if hasattr(folder.title, 'text') else str(folder.title)
                
                if "SNIPER" in folder_title.upper(): continue

                print(f"\n📂 ПАПКА: {folder_title}")
                folder_success_count = 0

                for peer in folder.include_peers:
                    try:
                        # 1. ПРОВЕРКА: Нужно ли обновить БИО перед отправкой?
                        if messages_since_last_bio >= bio_trigger:
                            await update_bio()
                            messages_since_last_bio = 0 # Сброс счетчика
                            bio_trigger = random.randint(3, 5) # Новое случайное число для следующего раза

                        # 2. Инфо о чате
                        try:
                            entity = await client.get_entity(peer)
                            chat_name = getattr(entity, 'title', getattr(entity, 'first_name', 'Чат'))
                        except: chat_name = "ID: " + str(getattr(peer, 'channel_id', 'Unknown'))

                        # 3. Отправка сообщения
                        text = await get_fixed_text()
                        msg = await client.send_message(peer, text, link_preview=False)
                        
                        sent_counter += 1
                        folder_success_count += 1
                        messages_since_last_bio += 1 # Увеличиваем счетчик для БИО
                        
                        # Удаление через 20 мин (фоном)
                        asyncio.create_task(deleted_delayed(peer, msg.id, 1200))

                        # 4. ИНФО В КОНСОЛЬ
                        cd_time = random.randint(10, 20)
                        time_when_sended = f"[{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}]"
                        print(f"📨 [Ася] [{time_when_sended}] | ✅[{sent_counter}] Сообщение -> 📂{chat_name} ушло! | КД: {cd_time} сек. | До БИО: {bio_trigger - messages_since_last_bio}")
                        
                        await asyncio.sleep(cd_time)

                    except errors.FloodWaitError as e:
                        print(f"🛑 ФЛУД! Сплю {e.seconds} сек.")
                        await asyncio.sleep(e.seconds)
                    except Exception as e: 
                        continue
                
                # Отчет в избранное после папки
                if folder_success_count > 0:
                    await send_report(f"Папка `{folder_title}` обработана. Отправлено: {folder_success_count}")

            print(f"\n⌛ Круг завершен. Общий счетчик: {sent_counter}. Сплю 5 минут...")
            await asyncio.sleep(300)

        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nВыход...")