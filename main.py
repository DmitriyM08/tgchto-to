import asyncio
from SOFIA_account.rasilkaSOFIA import infinite_worker
from ASYA_account.rasilkaASYA import main

async def start_all():
    # Создаем задачи для обоих аккаунтов
    # asyncio.gather запускает их одновременно
    print("🚀 Запуск обоих аккаунтов...")
    
    await asyncio.gather(
        main(),           # Функция main от Telethon (наш последний код)
        # infinite_worker() # Функция infinite_worker от Pyrogram (твой первый код)
    )

if __name__ == "__main__":
    try:
        # Для совместного запуска используем стандартный loop asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_all())
    except KeyboardInterrupt:
        print("\n🛑 Оба скрипта остановлены пользователем.")
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")