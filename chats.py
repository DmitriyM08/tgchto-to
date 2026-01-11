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
from telethon import TelegramClient, functions, types

# Твои данные (аккаунт Ася)
api_id = 33574840
api_hash = 'b8639fd38e1db0e49bd26c3dcaceb026'

async def main():
    # Используем сессию resends2
    async with TelegramClient('resends2', api_id, api_hash) as client:
        print("--- ЗАПУСК: ВСТУПЛЕНИЕ + ЗАПОЛНЕНИЕ ПАПОК ---")
        
        # 1. Читаем список чатов
        try:
            with open("my_chats_backup.txt", "r", encoding="utf-8") as f:
                links = [line.strip().replace('t.me/', '').replace('@', '') for line in f if line.strip()]
        except FileNotFoundError:
            print("[!] Ошибка: Файл my_chats_backup.txt не найден!")
            return

        print(f"Найдено ссылок: {len(links)}")
        
        all_peers = []
        for link in links:
            try:
                # Получаем объект чата
                entity = await client.get_entity(link)
                
                # Вступаем, если это канал или супергруппа
                if isinstance(entity, (types.Chat, types.Channel)):
                    try:
                        await client(functions.channels.JoinChannelRequest(channel=entity))
                        print(f"[+] Вступил в: {link}")
                    except Exception as e:
                        print(f"[-] Пропуск (уже в чате или ошибка): {link}")
                
                # Сохраняем для папок
                all_peers.append(await client.get_input_entity(entity))
                
                # ТВОЯ ЗАДЕРЖКА: от 22 до 47 секунд
                wait_time = random.randint(22, 47)
                print(f"Сплю {wait_time} сек...")
                await asyncio.sleep(wait_time) 
                
            except Exception as e:
                print(f"[!] Ошибка с {link}: {e}")

        # 2. Распределение по папкам "Рассылка"
        print("\nРаскидываю чаты по папкам...")
        current_filters = await client(functions.messages.GetDialogFiltersRequest())
        
        # Ищем твои папки
        target_folders = [f for f in current_filters.filters if hasattr(f, 'title')]
        
        if not target_folders:
            print("[!] Ошибка: Создай сначала пустые папки в Telegram!")
            return

        # Лимит 100 чатов на папку
        chunk_size = 100
        for i, folder in enumerate(target_folders):
            start = i * chunk_size
            end = start + chunk_size
            chunk = all_peers[start:end]
            
            if not chunk:
                break
                
            print(f"Заполняю папку '{folder.title.text}' (чатов: {len(chunk)})")
            
            new_filter = types.DialogFilter(
                id=folder.id,
                title=folder.title,
                include_peers=chunk, #
                pinned_peers=[],
                exclude_peers=[]
            )
            
            await client(functions.messages.UpdateDialogFilterRequest(id=folder.id, filter=new_filter))
            print(f"Готово: {folder.title.text}")

        print("\n--- ВСЕ ЗАДАНИЯ ВЫПОЛНЕНЫ ---")

if __name__ == '__main__':
    asyncio.run(main())