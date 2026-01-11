# import asyncio
# import random
# import os
# from telethon.sync import TelegramClient
# from telethon.tl.functions.channels import JoinChannelRequest
# from telethon.tl.functions.folders import EditPeerFoldersRequest
# from telethon.tl.types import InputFolderPeer
# from telethon.errors import FloodWaitError, UsernameInvalidError, ChannelPrivateError

# api_id = 34879829
# api_hash = 'd8fe880abccc67116a434dd51e2dd73a'

# client = TelegramClient('reke_session_final', api_id, api_hash)

# async def main():
#     await client.start()
#     print("🚀 Бот запущен. Начинаю быструю проходку.")

#     while True:
#         if not os.path.exists('chats.txt'):
#             print("❌ Файл chats.txt не найден!")
#             break

#         with open('chats.txt', 'r', encoding='utf-8') as f:
#             links = [line.strip() for line in f if line.strip()]

#         if not links:
#             print("🏁 Список пуст!")
#             break

#         current_link = links[0]
#         clean_link = current_link.replace('https://t.me/', '').replace('@', '').strip()

#         try:
#             print(f"\n--> Обработка: {clean_link} (Осталось: {len(links)})")
            
#             # Ставим жесткий тайм-аут на вступление, чтобы не висел
#             # 1. Вступаем
#             result = await asyncio.wait_for(
#                 client(JoinChannelRequest(clean_link)), 
#                 timeout=15
#             )
            
#             chat = result.chats[0]
#             print(f"✅ Успешно: '{chat.title}'")

#             # 2. Перенос в архив
#             peer = await client.get_input_entity(chat)
#             await client(EditPeerFoldersRequest(folder_peers=[
#                 InputFolderPeer(peer=peer, folder_id=1)
#             ]))
            
#             # Удаляем из списка только после успешного вступления
#             with open('chats.txt', 'w', encoding='utf-8') as f:
#                 f.write('\n'.join(links[1:]))
            
#             # Рандомная пауза, чтобы не словить бан
#             wait_time = random.randint(110, 240) 
#             print(f"⏳ Ок, спим {wait_time} сек...")
#             await asyncio.sleep(wait_time)

#         except FloodWaitError as e:
#             print(f"⚠️ ФЛУД! Спим {e.seconds} секунд. НЕ ВЫКЛЮЧАЙ.")
#             await asyncio.sleep(e.seconds + 5)
#             # Ссылку НЕ удаляем, попробуем её после паузы

#         except (UsernameInvalidError, ValueError, ChannelPrivateError) as e:
#             print(f"❌ Чат битый или приватный ({clean_link}): {e}. Пропускаю...")
#             # Удаляем мусорную ссылку сразу
#             with open('chats.txt', 'w', encoding='utf-8') as f:
#                 f.write('\n'.join(links[1:]))

#         except asyncio.TimeoutError:
#             print(f"⏰ Тайм-аут! Чат {clean_link} не отвечает. Удаляю из очереди...")
#             with open('chats.txt', 'w', encoding='utf-8') as f:
#                 f.write('\n'.join(links[1:]))

#         except Exception as e:
#             print(f"❓ Неизвестная ошибка с {clean_link}: {e}")
#             with open('chats.txt', 'w', encoding='utf-8') as f:
#                 f.write('\n'.join(links[1:]))
#             await asyncio.sleep(5)

# with client:
#     client.loop.run_until_complete(main())

# Твои данные
import asyncio
from telethon import TelegramClient, functions, types

# Твои данные
api_id = 33365891
api_hash = 'eff47ae95ca73b5c6636606b6ba80fd0'

# Твой текст (без прем-эмодзи, просто чистый текст и смайлы)
my_text = "🥰 В НАЛИЧИИ 🥰\n\n🔞 ПОРНО 💋\n \n               🍑 ДЕТСКОЕ 🔵\n\n  🍑 ДЕТСКОЕ 🔵\n                        🍑 ДЕТСКОЕ 🔵\n\n        🍌 ШКОЛЬНИЦЫ 🍑\n\n🍌 ШКОЛЬНИЦЫ 🍑\n\n                 🍌 ШКОЛЬНИЦЫ 🍑\n\n            🙃 ВЗРОСЛОЕ 🍑\n\n    🙃 ВЗРОСЛОЕ 🍑\n                                \n                      🙃 ВЗРОСЛОЕ 🍑\n\n                  😀 А ТАК ЖЕ 👅\n\n😀 ВИРТИК 😀\n😀 ВИДЕО ДЗВОНОК 😀\n😀 ФОТОЧКИ 😀\n🍑 БДСМ 🌛\n🌟 ЛЕЗБИ 🌟\n🌟 ПЕДО МАМКИ 🌟\n\n          🌟 ЖДУ В ЛИЧНЫЕ 👠\n            🌟 СООБЩЕНИЯ 🌟"

async def main():
    # Новая сессия v10 для чистого старта
    async with TelegramClient('session_final_v10', api_id, api_hash) as client:
        print("--- СКРИПТ ЗАПУЩЕН (Бесконечный цикл) ---")
        
        while True:
            # 1. Лечим ошибку со скриншота: прогружаем все контакты
            print("\nОбновляю базу чатов...")
            await client.get_dialogs() 
            
            # 2. Берем стикер из Избранного
            sticker = None
            async for msg in client.iter_messages('me', limit=5):
                if msg.sticker:
                    sticker = msg.sticker
                    break
            
            # 3. Собираем все чаты из папок ворк РФ/УКР
            result = await client(functions.messages.GetDialogFiltersRequest())
            chat_peers = []
            for folder in result.filters:
                if hasattr(folder, 'include_peers'):
                    for peer in folder.include_peers:
                        chat_peers.append(peer)

            total = len(chat_peers)
            print(f"Начинаю круг по {total} чатам. Пауза 15 сек...")

            # 4. Сама рассылка
            count = 0
            for peer in chat_peers:
                try:
                    # Отправляем текст
                    await client.send_message(peer, my_text, link_preview=True)
                    
                    # Шлем стикер, если нашелся
                    if sticker:
                        await client.send_file(peer, sticker)
                    
                    count += 1
                    print(f"[{count}/{total}] Улетело. Жду 15 сек...")
                    await asyncio.sleep(15) # Твоя задержка
                    
                except Exception as e:
                    # Если чат недоступен, просто идем к следующему
                    print(f"[!] Пропуск чата: {e}")

            print(f"Круг пройден. Отдыхаю 45 секунд и иду заново...")
            await asyncio.sleep(45)

if __name__ == '__main__':
    asyncio.run(main())