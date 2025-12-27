import asyncio
from pyrogram import Client
from pyrogram.raw import functions
import dotenv, os

dotenv.load_dotenv()

# Ваши данные
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
folder_name = "ворк УКР" 
message_text = "Привітик😘\nПравила фіксовані. Умови не обговорюються \n• 1 година — ≈ 2500 ₴\n• 2 години — ≈ 4000₴\n• 30 хв — ≈ 1 500₴\n• Нічний формат — ≈ 7000₴\n• Масаж — ≈ 1 500₴\n• Bupт с фото,видео и кружками 🍬\n• фото/вuдeo из архива и на заказ💝 - 70 грн \n• Сочный видеозвонок как только захочешь 🍓 - 120 грн \n• Сочный приватик с лучшими фоточками - 50 грн\n• Пишіть🥰\nУмови:\nПередплата ≈ 250 ₴(сплата за таксi)💋"

async def main():
    async with Client("my_account", api_id, api_hash) as app:
        print("Подключение успешно. Ищу папку...")
        
        folder_id = None
        suggested_filters = await app.invoke(functions.messages.GetDialogFilters())
        
        target_folder = None
        for folder in suggested_filters:
            if hasattr(folder, "title") and folder.title == folder_name:
                target_folder = folder
                break
        
        if not target_folder:
            print(f"Папка '{folder_name}' не найдена. Проверьте название.")
            return
        
        peer_ids = []
        for peer in target_folder.include_peers:
            if hasattr(peer, "chat_id"):
                peer_ids.append(peer.chat_id)
            elif hasattr(peer, "channel_id"):
                peer_ids.append(int(f"-100{peer.channel_id}"))
            elif hasattr(peer, "user_id"):
                peer_ids.append(peer.user_id)

        print(f"Найдено чатов в папке: {len(peer_ids)}")

        while True:
            for chat_id in peer_ids:
                try:
                    try:
                        await app.get_chat(chat_id)
                    except:
                        pass 

                    await app.send_message(chat_id, message_text)
                    print(f"Успешно отправлено в {chat_id}")
                    await asyncio.sleep(11) 
                    
                except Exception as e:
                    if "ALLOW_PAYMENT_REQUIRED" in str(e):
                        print(f"Пропущено: в чате {chat_id} платная отправка сообщений.")
                    else:
                        print(f"Ошибка в чате {chat_id}")
                    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())