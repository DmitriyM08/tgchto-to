# import asyncio
# from telethon import TelegramClient, functions, types

# api_id = 34879829
# api_hash = 'd8fe880abccc67116a434dd51e2dd73a'

# async def main():
#     # Используем новую сессию, чтобы не конфликтовать с рассылкой
#     async with TelegramClient('export_frozen_acc', api_id, api_hash) as client:
#         print("--- ПРОЦЕСС ОЖИВЛЕНИЯ И СБОРА ЧАТОВ ---")
        
#         # 1. Будим аккаунт и тянем все диалоги
#         print("Подключаюсь и прогружаю диалоги (может занять время)...")
#         await client.get_dialogs() 
        
#         # 2. Получаем структуру папок
#         print("Запрашиваю список папок (ворк РФ, ворк УКР и др.)...")
#         result = await client(functions.messages.GetDialogFiltersRequest())
        
#         all_links = []
        
#         for folder in result.filters:
#             if hasattr(folder, 'title'):
#                 folder_title = folder.title.text if hasattr(folder.title, 'text') else str(folder.title)
#                 print(f"--> Захожу в папку: {folder_title}")
                
#                 if hasattr(folder, 'include_peers'):
#                     for peer in folder.include_peers:
#                         try:
#                             # Пытаемся достать данные чата напрямую
#                             entity = await client.get_entity(peer)
                            
#                             # Нам нужны только юзернеймы (@) для переноса на другой акк
#                             username = getattr(entity, 'username', None)
                            
#                             if username:
#                                 link = f"t.me/{username}"
#                                 if link not in all_links:
#                                     all_links.append(link)
#                                     print(f"[+] Нашел: @{username}")
                            
#                         except Exception:
#                             # Если чат совсем "мертвый" или приватный без ссылки
#                             continue

#         # 3. Сохраняем только чистые ссылки
#         if all_links:
#             with open("my_chats_backup.txt", "w", encoding="utf-8") as f:
#                 for link in all_links:
#                     f.write(link + "\n")
#             print(f"\nГОТОВО! Собрано {len(all_links)} рабочих ссылок.")
#             print("Все ссылки сохранены в файл: my_chats_backup.txt")
#         else:
#             print("\n[!] Ссылок не найдено. Возможно, в папках только приватные группы.")

# if __name__ == '__main__':
#     asyncio.run(main())



# import asyncio
# from telethon import TelegramClient, functions, types

# # Твои данные
# api_id = 33365891
# api_hash = 'eff47ae95ca73b5c6636606b6ba80fd0'

# async def main():
#     # Добавляем параметры устройства, чтобы Telegram "доверял" входу
#     client = TelegramClient(
#         'session_fill_v11', 
#         api_id, 
#         api_hash,
#         system_version="4.16.30-vxCUSTOM",
#         device_model="Desktop",
#         app_version="4.8.4"
#     )

#     async with client:
#         print("--- ПОДКЛЮЧЕНО ---")
        
#         # 1. Загрузка списка чатов из файла
#         try:
#             with open("my_chats_backup.txt", "r", encoding="utf-8") as f:
#                 links = [line.strip().replace('t.me/', '').replace('@', '') for line in f if line.strip()]
#         except FileNotFoundError:
#             print("Ошибка: Файл my_chats_backup.txt не найден!")
#             return

#         print(f"Найдено ссылок: {len(links)}. Превращаю их в объекты...")
        
#         all_peers = []
#         for link in links:
#             try:
#                 # Используем get_entity для "замороженных" акков
#                 peer = await client.get_input_entity(link)
#                 all_peers.append(peer)
#                 print(f"[+] Добавлен: {link}")
#             except Exception as e:
#                 print(f"[!] Не нашел {link}: {e}")
#             await asyncio.sleep(1) # Увеличил паузу для безопасности

#         print("\n2. Получение папок...")
#         current_filters = await client(functions.messages.GetDialogFiltersRequest())
        
#         # Берем папки, которые ты создал
#         target_folders = [f for f in current_filters.filters if hasattr(f, 'title')]
        
#         if not target_folders:
#             print("Ошибка: Создай сначала пустые папки в Telegram!")
#             return

#         chunk_size = 100
#         for i, folder in enumerate(target_folders):
#             start = i * chunk_size
#             end = start + chunk_size
#             chunk = all_peers[start:end]
            
#             if not chunk:
#                 break
                
#             print(f"Заполняю папку '{folder.title.text}' ({len(chunk)} чатов)...")
            
#             # Создаем новый объект фильтра с твоими чатами
#             new_filter = types.DialogFilter(
#                 id=folder.id,
#                 title=folder.title,
#                 include_peers=chunk,
#                 pinned_peers=[],
#                 exclude_peers=[]
#             )
            
#             try:
#                 await client(functions.messages.UpdateDialogFilterRequest(id=folder.id, filter=new_filter))
#                 print(f"Успешно: {folder.title.text}")
#             except Exception as e:
#                 print(f"Ошибка при обновлении папки: {e}")

#         print("\n--- ГОТОВО ---")

# if __name__ == '__main__':
#     asyncio.run(main())
import asyncio
import random
import os
import time
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, UsernameInvalidError, ChannelPrivateError

# Данные те же
api_id = 33574840
api_hash = 'b8639fd38e1db0e49bd26c3dcaceb026'

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
    client = TelegramClient('joiner_session', api_id, api_hash)
    
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

            wait = random.randint(60, 100)
            print(f"⏳ Ждем {wait} сек...")
            await asyncio.sleep(wait)

        except FloodWaitError as e:
            print(f"🛑 Флуд на {e.seconds} сек")
            await asyncio.sleep(e.seconds + 10)
        except Exception as e:
            print(f"❌ Ошибка на {current_link}: {e}")
            remove_link_from_file(file_path, current_link)
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())