import asyncio
import random
import os
import time
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, UsernameInvalidError, ChannelPrivateError

# Данные те же +12819383796 
api_id = 39200729
api_hash = 'fca93651288f087718e1d94acb78c384'

def remove_link_from_file(file_path, link_to_remove):
    if not os.path.exists(file_path): return
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(file_path, "w", encoding="utf-8") as f:
        for line in lines:
            clean = line.strip().replace('https://t.me/', '').replace('t.me/', '').replace('@', '')
            if clean != link_to_remove:
                f.write(line)

async def sync_archive_to_folders(client):
    print("\n📦 [АРХИВАТОР] Синхронизация...")
    try:
        dialogs = await client.get_dialogs()
        archived_peers = [d.entity for d in dialogs if d.folder_id == 1 and isinstance(d.entity, (types.Chat, types.Channel))]
        if not archived_peers: return
        
        result = await client(functions.messages.GetDialogFiltersRequest())
        for f in result.filters:
            if isinstance(f, types.DialogFilter) and f.title != "SNIPER MODE":
                current_peers = list(f.include_peers)
                added = 0
                for entity in archived_peers:
                    peer = await client.get_input_entity(entity)
                    if len(current_peers) < 200 and peer not in current_peers:
                        current_peers.append(peer)
                        added += 1
                if added > 0:
                    f.include_peers = current_peers
                    await client(functions.messages.UpdateDialogFilterRequest(id=f.id, filter=f))
    except Exception as e:
        print(f"❌ Ошибка архиватора: {e}")

async def main():
    # ИСПОЛЬЗУЕМ ОТДЕЛЬНУЮ СЕССИЮ
    client = TelegramClient('account2', api_id, api_hash)
    
    await client.start() # Тут он спросит номер телефона и код в консоли!
    
    print("--- ВСТУПАЛЬЩИК ЗАПУЩЕН ---")
    file_path = "my_chats_backup.txt"
    total_added = 0
    session_limit = 0

    while True:
        if not os.path.exists(file_path):
            print("Файл не найден.")
            break

        with open(file_path, "r", encoding="utf-8") as f:
            links = [line.strip().replace('https://t.me/', '').replace('t.me/', '').replace('@', '') for line in f if line.strip()]

        if not links:
            print("🏁 Ссылки кончились!")
            break

        current_link = links[0]
        try:
            entity = await client.get_entity(current_link)
            
            # Проверка на группу
            if not (isinstance(entity, types.Chat) or (isinstance(entity, types.Channel) and entity.megagroup)):
                print(f"🚫 {current_link} - не группа.")
                remove_link_from_file(file_path, current_link)
                continue

            # Проверка участников
            full = await client(functions.channels.GetFullChannelRequest(channel=entity))
            count = full.full_chat.participants_count
            if count < 150:
                print(f"📉 Мало людей ({count}) в {current_link}")
                remove_link_from_file(file_path, current_link)
                continue

            # Вступление
            await client(functions.channels.JoinChannelRequest(channel=entity))
            print(f"✅ Вступил: {current_link} ({count} чел.)")
            
            total_added += 1
            session_limit += 1

            # Добавление в папки
            try:
                res = await client(functions.messages.GetDialogFiltersRequest())
                for f in res.filters:
                    if isinstance(f, types.DialogFilter):
                        peers = list(f.include_peers)
                        inp = await client.get_input_entity(entity)
                        if inp not in peers and len(peers) < 200:
                            peers.append(inp)
                            f.include_peers = peers
                            await client(functions.messages.UpdateDialogFilterRequest(id=f.id, filter=f))
            except: pass

            remove_link_from_file(file_path, current_link)

            if session_limit >= 45:
                print("☕ ПЕРЕРЫВ 20 МИН")
                await sync_archive_to_folders(client)
                await asyncio.sleep(1200)
                session_limit = 0

            wait = random.randint(20, 40)
            print(f"⏳ Ждем {wait} сек...")
            await asyncio.sleep(wait)

        except FloodWaitError as e:
            print(f"🛑 Флуд на {e.seconds} сек")
            await asyncio.sleep(e.seconds + 10)
        except Exception as e:
            print(f"❌ Ошибка на {current_link}: {e}")
            remove_link_from_file(file_path, current_link)
            await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())