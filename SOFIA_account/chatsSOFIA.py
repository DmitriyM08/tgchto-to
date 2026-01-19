import asyncio
import random
import os
import time
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, UsernameInvalidError, ChannelPrivateError

# Данные для входа
api_id = 38386096
api_hash = '026a515285988ef6f296bb693b9fdeec'

def remove_link_from_file(file_path, link_to_remove):
    """Удаляет обработанную ссылку из файла сразу"""
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(file_path, "w", encoding="utf-8") as f:
        for line in lines:
            clean = line.strip().replace('https://t.me/', '').replace('t.me/', '').replace('@', '')
            if clean != link_to_remove:
                f.write(line)

async def sync_archive_to_folders(client):
    """Синхронизация архива во время перерыва"""
    print("\n📦 [АРХИВАТОР] Проверка архива...")
    try:
        dialogs = await client.get_dialogs()
        archived_peers = [
            await client.get_input_entity(d.entity) 
            for d in dialogs if d.folder_id == 1 and isinstance(d.entity, (types.Chat, types.Channel))
        ] 
        if not archived_peers: return

        filters = await client(functions.messages.GetDialogFiltersRequest())
        for target_folder in filters.filters:
            if not hasattr(target_folder, 'title'): continue
            current_peers = list(target_folder.include_peers)
            added = 0
            for peer in archived_peers:
                if len(current_peers) < 200 and peer not in current_peers:
                    current_peers.append(peer)
                    added += 1
            if added > 0:
                new_filter = types.DialogFilter(
                    id=target_folder.id, title=target_folder.title, include_peers=current_peers,
                    pinned_peers=getattr(target_folder, 'pinned_peers', []),
                    exclude_peers=getattr(target_folder, 'exclude_peers', [])
                )
                await client(functions.messages.UpdateDialogFilterRequest(id=target_folder.id, filter=new_filter))
    except Exception as e:
        print(f"❌ [АРХИВАТОР] Ошибка: {e}")

async def main():
    async with TelegramClient('joiner_session', api_id, api_hash) as client:
        print("--- БОТ ЗАПУЩЕН (ЗАЯВКИ ИГНОРИРУЮТСЯ) ---")
        
        file_path = "my_chats_backup.txt"
        total_added_counter = 0  # Общий счетчик за сессию
        session_limit_counter = 0 # Счетчик для перерыва (45)

        while True:
            if not os.path.exists(file_path):
                print("[!] Файл не найден.")
                break

            with open(file_path, "r", encoding="utf-8") as f:
                links = [line.strip().replace('https://t.me/', '').replace('t.me/', '').replace('@', '') for line in f if line.strip()]

            remaining_in_txt = len(links)

            if not links:
                print("[🏁] Все ссылки обработаны!")
                break

            current_link = links[0]

            try:
                # 1. Получаем данные о чате
                entity = await client.get_entity(current_link)
                
                # ПРОВЕРКА 1: Это группа?
                is_group = False
                if isinstance(entity, types.Channel):
                    if entity.megagroup: is_group = True
                elif isinstance(entity, types.Chat): is_group = True

                if not is_group:
                    print(f"🚫 {current_link} — КАНАЛ. Пропускаю.")
                    remove_link_from_file(file_path, current_link)
                    continue

                # ПРОВЕРКА 2: Сколько участников?
                full_chat = await client(functions.channels.GetFullChannelRequest(channel=entity))
                participants_count = full_chat.full_chat.participants_count
                
                if participants_count < 150:
                    print(f"📉 {current_link} — Мало людей ({participants_count}). Пропускаю.")
                    remove_link_from_file(file_path, current_link)
                    continue

                # 2. Вступление
                input_peer = await client.get_input_entity(entity)
                print(f"\n--> Обработка: {current_link} (Участников: {participants_count})")
                
                try:
                    await client(functions.channels.JoinChannelRequest(channel=input_peer))
                    print(f"✅ Успешно вступил!")
                except Exception as e:
                    err_msg = str(e).lower()
                    if "requested" in err_msg or "sent" in err_msg:
                        print(f"📩 Отправлена заявка на вступление (не ждем одобрения).")
                    else:
                        raise e # Если ошибка другая, уходим в основной блок catch

                total_added_counter += 1
                session_limit_counter += 1
                
                # СРАЗУ ПИШЕМ СТАТИСТИКУ
                print(f"📊 Статус: [Добавлено: {total_added_counter}] | [Осталось в файле: {remaining_in_txt - 1}]")

                # 3. Раскидываем по папкам (только если мы реально вступили)
                try:
                    filters = await client(functions.messages.GetDialogFiltersRequest())
                    for folder in filters.filters:
                        if hasattr(folder, 'title'):
                            peers = list(folder.include_peers)
                            if input_peer not in peers and len(peers) < 200:
                                peers.append(input_peer)
                                await client(functions.messages.UpdateDialogFilterRequest(
                                    id=folder.id, filter=types.DialogFilter(
                                        id=folder.id, title=folder.title, include_peers=peers,
                                        pinned_peers=getattr(folder, 'pinned_peers', []),
                                        exclude_peers=getattr(folder, 'exclude_peers', [])
                                    )
                                ))
                except:
                    pass # Если это была заявка, в папки не добавит до одобрения админом

                # Удаляем из файла
                remove_link_from_file(file_path, current_link)

                # Перерыв после 45 вступлений
                if session_limit_counter >= 45:
                    print(f"\n☕️ ПЕРЕРЫВ 20 МИНУТ. Синхронизация архива...")
                    start_p = time.time()
                    await sync_archive_to_folders(client)
                    rem = 1200 - (time.time() - start_p)
                    if rem > 0: await asyncio.sleep(rem)
                    session_limit_counter = 0
                    print("🔄 Продолжаю работу!")

                wait = random.randint(60, 100)
                print(f"⏳ Пауза {wait} сек...")
                await asyncio.sleep(wait)

            except (UsernameInvalidError, ValueError, ChannelPrivateError):
                print(f"❌ Ссылка битая {current_link}. Удаляю.")
                remove_link_from_file(file_path, current_link)
            except FloodWaitError as e:
                print(f"⚠️ Флуд: ждем {e.seconds} сек.")
                await asyncio.sleep(e.seconds + 10)
            except Exception as e:
                msg = str(e).lower()
                if "already" in msg:
                    print(f"[-] Уже в чате {current_link}. Удаляю.")
                    remove_link_from_file(file_path, current_link)
                else:
                    print(f"[!] Ошибка {current_link}: {e}")
                await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())