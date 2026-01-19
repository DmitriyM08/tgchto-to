import asyncio
import random
import re
from datetime import datetime

# pip install telethon
from telethon import TelegramClient, functions, types, errors, utils
from data import data_account, AD_TEMPLATE

BIO_PHRASES = [
    "Жду тебя в ЛС 🥰", "Самый сочный контент тут 🔞", "Пиши, не стесняйся 💋",
    "Твоя любимая девочка 🔥", "Онлайн 24/7, заходи 🍑", "Хочешь увидеть больше? 😉",
    "Самое вкусное скрыто тут 🍑🔥", "Жду твоего сообщения, котик 💋"
]

class AsyaTelethon:
    def __init__(self, acc):
        self.acc_name = acc["account"]
        self.client = TelegramClient(
            self.acc_name, 
            int(acc["api_code"]), 
            acc["api_hash"],
            device_model="Samsung SM-S901B"
        )
        self.sent_counter = 0
        self.bio_counter = 0
        self.bio_trigger = random.randint(3, 5)

    def get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def log(self, text):
        print(f"[{self.get_time()}] [{self.acc_name}] {text}")

    def _shuffle_emojis(self, text):
        emoji_pattern = r'[🥰🔞💋🍑🔵🍌🙃😀👅🌛🌟👠]'
        lines = text.split('\n')
        processed = []
        for line in lines:
            emojis = re.findall(emoji_pattern, line)
            if len(emojis) > 1:
                shuf = emojis.copy()
                random.shuffle(shuf)
                for orig in emojis:
                    line = line.replace(orig, shuf.pop(0), 1)
            processed.append(line)
        return '\n'.join(processed)

    async def update_bio(self):
        try:
            new_bio = random.choice(BIO_PHRASES)
            await self.client(functions.account.UpdateProfileRequest(about=new_bio))
            self.log("✨ BIO обновлен.")
        except: pass

    async def start_engine(self):
        await self.client.start()
        self.log("🚀 Двигатель запущен.")
        
        while True:
            try:
                all_dialogs = await self.client.get_dialogs(limit=None)
                result = await self.client(functions.messages.GetDialogFiltersRequest())
                
                for folder in result.filters:
                    if not hasattr(folder, 'title') or folder.title is None:
                        continue
                    
                    title = getattr(folder.title, 'text', str(folder.title))
                    if "SNIPER" in title.upper():
                        continue

                    folder_chats = []
                    included_ids = set()
                    peers = (getattr(folder, 'include_peers', []) + getattr(folder, 'pinned_peers', []))
                    for p in peers:
                        included_ids.add(utils.get_peer_id(p))

                    for d in all_dialogs:
                        peer_id = d.id
                        is_manual = peer_id in included_ids
                        is_category = False
                        if getattr(folder, 'groups', False) and (d.is_group or d.is_megagroup):
                            is_category = True
                        if getattr(folder, 'broadcasts', False) and d.is_channel and not d.is_group:
                            is_category = True
                            
                        if is_manual or is_category:
                            excluded_ids = {utils.get_peer_id(p) for p in getattr(folder, 'exclude_peers', [])}
                            if peer_id not in excluded_ids:
                                folder_chats.append(d)

                    if not folder_chats:
                        continue
                    
                    self.log(f"📍 Папка '{title}': вижу {len(folder_chats)} чатов.")

                    for dialog in folder_chats:
                        if self.bio_counter >= self.bio_trigger:
                            await self.update_bio()
                            self.bio_counter = 0
                            self.bio_trigger = random.randint(3, 5)

                        try:
                            content = self._shuffle_emojis(AD_TEMPLATE)
                            msg = await self.client.send_message(dialog.input_entity, content, link_preview=False)
                            
                            self.sent_counter += 1
                            self.bio_counter += 1
                            
                            asyncio.create_task(self._delayed_delete(dialog.input_entity, msg.id))

                            cd = random.randint(35, 55)
                            self.log(f"✅ #{self.sent_counter} -> {dialog.name} | КД: {cd}с")
                            await asyncio.sleep(cd)

                        except errors.FloodWaitError as e:
                            self.log(f"🛑 ФЛУД: спим {e.seconds}с")
                            await asyncio.sleep(e.seconds)

                        # --- ИЗМЕНЕННАЯ ЛОГИКА: БЕЗ УДАЛЕНИЯ ---
                        except (errors.UserBannedInChannelError, errors.ChannelPrivateError) as e:
                            err_name = type(e).__name__
                            self.log(f"⚠️ Пропуск '{dialog.name}': бан или недоступен ({err_name})")
                            continue

                        except errors.ChatWriteForbiddenError:
                            self.log(f"🚫 В '{dialog.name}' нельзя писать. Пропускаю.")
                            continue
                        except Exception as e:
                            self.log(f"⚠️ Ошибка в '{dialog.name}': {type(e).__name__}")
                            continue

                    self.log(f"⌛ Папка '{title}' закончена. Пауза 1 мин...")
                    await asyncio.sleep(60)

                self.log("⌛ Все папки пройдены. Спим 5 минут...")
                await asyncio.sleep(300)

            except Exception as e:
                self.log(f"❌ Критическая ошибка: {e}")
                await asyncio.sleep(90)

    async def _delayed_delete(self, entity, msg_id):
        await asyncio.sleep(1200)
        try: await self.client.delete_messages(entity, [msg_id])
        except: pass

async def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💎 АСЯ TELETHON ЗАПУЩЕНА (ТОЛЬКО РАССЫЛКА).")
    
    tasks = []
    for i, acc in enumerate(data_account):
        if i > 0:
            wait_time = random.randint(20, 45)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Ожидаю {wait_time}с перед запуском {acc['account']}...")
            await asyncio.sleep(wait_time)
        
        asya = AsyaTelethon(acc)
        task = asyncio.create_task(asya.start_engine())
        tasks.append(task)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {acc['account']} отправлен на взлет!")

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🕴️ Отключаюсь.")