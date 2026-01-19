import asyncio
from telethon import TelegramClient, functions, types

# Твои данные
api_id = 33574840
api_hash = 'b8639fd38e1db0e49bd26c3dcaceb026'
session_name = 'joiner_session' # Твоё название сессии

async def clean_folders():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print("🔍 Анализ папок (Игнорирую 'SNIPER MODE')...")
        
        try:
            response = await client(functions.messages.GetDialogFiltersRequest())
        except Exception as e:
            print(f"❌ Ошибка получения папок: {e}")
            return

        seen_chats = {}
        
        for folder in response.filters:
            if not hasattr(folder, 'title') or not hasattr(folder, 'include_peers'):
                continue
            
            folder_name = folder.title.text
            
            # УСЛОВИЕ: Пропускаем папку SNIPER MODE полностью
            if folder_name.upper() == "SNIPER MODE":
                print(f"🛡 Папка '{folder_name}' в белом списке. Пропускаю.")
                continue

            current_peers = list(folder.include_peers)
            new_peers_list = []
            removed_count = 0

            print(f"📂 Проверяю: {folder_name}")

            for peer in current_peers:
                peer_id = None
                if isinstance(peer, types.InputPeerChannel): peer_id = peer.channel_id
                elif isinstance(peer, types.InputPeerChat): peer_id = peer.chat_id
                elif isinstance(peer, types.InputPeerUser): peer_id = peer.user_id

                if peer_id is None:
                    new_peers_list.append(peer)
                    continue

                if peer_id in seen_chats:
                    print(f"   🗑 Дубль! Чат {peer_id} уже есть в '{seen_chats[peer_id]}'. Удаляю из '{folder_name}'")
                    removed_count += 1
                else:
                    seen_chats[peer_id] = folder_name
                    new_peers_list.append(peer)

            if removed_count > 0:
                try:
                    await client(functions.messages.UpdateDialogFilterRequest(
                        id=folder.id,
                        filter=types.DialogFilter(
                            id=folder.id,
                            title=folder.title,
                            include_peers=new_peers_list,
                            pinned_peers=getattr(folder, 'pinned_peers', []),
                            exclude_peers=getattr(folder, 'exclude_peers', []),
                            emoticon=getattr(folder, 'emoticon', None)
                        )
                    ))
                    print(f"✅ Папка '{folder_name}' почищена.")
                except Exception as e:
                    print(f"❌ Ошибка обновления '{folder_name}': {e}")

        print("\n🏁 Готово! Дубликаты удалены везде, кроме 'SNIPER MODE'.")

if __name__ == '__main__':
    asyncio.run(clean_folders())