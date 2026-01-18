import asyncio
import random
from telethon import TelegramClient, events
import openai

# ТВОИ НОВЫЕ ДАННЫЕ
api_id = 33574840
api_hash = 'b8639fd38e1db0e49bd26c3dcaceb026'

# ТВОЙ КЛЮЧ OpenAI (нужно вставить свой)
openai.api_key = "ТВОЙ_OPENAI_API_KEY"

# ХАРАКТЕР БОТА
AI_PROMPT = (
    "Ты — молодая, дерзкая девушка по имени Кира. "
    "Общаешься в Телеграме. Твой стиль: живой, неформальный, немного пошлый и игривый. "
    "Пиши как реальный человек: не всегда используй заглавные буквы, минимум знаков препинания, "
    "используй смайлики (🍑, 😈, 😉). Отвечай коротко. "
    "Твоя цель — заигрывать и держать парня в напряжении."
)

async def main():
    # Настройки сессии (имя файла сессии теперь 'resends2')
    client = TelegramClient('resends2', api_id, api_hash, 
                            device_model="iPhone 15 Pro", 
                            system_version="iOS 17.0")

    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def handler(event):
        # Не отвечаем себе
        me = await client.get_me()
        if event.sender_id == me.id:
            return

        # 1. Имитация прочтения (пауза 2-5 сек)
        await asyncio.sleep(random.randint(2, 5))
        await event.mark_read()

        print(f"Новое сообщение от {event.sender_id}: {event.text}")

        try:
            # 2. Запрос к нейросети
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": AI_PROMPT},
                    {"role": "user", "content": event.text}
                ],
                temperature=0.8
            )
            reply_text = response.choices[0].message.content

            # 3. Имитация набора текста (typing)
            async with client.action(event.chat_id, 'typing'):
                # Время печати зависит от длины текста
                wait_time = len(reply_text) * 0.15 
                await asyncio.sleep(min(wait_time, 8)) 

                # 4. Отправка ответа
                await event.reply(reply_text)
                print(f"Кира ответила: {reply_text}")

        except Exception as e:
            print(f"Ошибка ИИ: {e}")

    print("--- КИРА ЗАПУЩЕНА (resends2) ---")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())