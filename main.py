# ============================================
# BLACK PRO CYBER BOT - Main Entry Point
# ============================================
# Bot Name: BLACK PRO CYBER BOT
# Developer: @jiolinhacker
# ============================================

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, get_db_admins
from handlers_user import user_router
from handlers_admin import admin_router

# ─── Logging ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


# ─── Bot Commands ─────────────────────────────────────────
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="বট শুরু করুন"),
        BotCommand(command="admin", description="Admin Panel (Admin Only)"),
        BotCommand(command="cancel", description="বর্তমান অপারেশন বাতিল করুন"),
    ]
    await bot.set_my_commands(commands)


# ─── Startup ──────────────────────────────────────────────
async def on_startup(bot: Bot):
    logger.info("🚀 BLACK PRO CYBER BOT Starting...")
    init_db()
    await set_bot_commands(bot)

    bot_info = await bot.get_me()
    logger.info(f"✅ Bot started: @{bot_info.username}")

    # Notify admins
    all_admins = list(set(ADMIN_IDS + get_db_admins()))
    for admin_id in all_admins:
        try:
            await bot.send_message(
                admin_id,
                f"🟢 <b>BLACK PRO CYBER BOT চালু হয়েছে!</b>\n\n"
                f"🤖 Bot: @{bot_info.username}\n"
                f"✅ সব সিস্টেম সক্রিয়",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Could not notify admin {admin_id}: {e}")


# ─── Shutdown ─────────────────────────────────────────────
async def on_shutdown(bot: Bot):
    logger.info("🔴 Bot shutting down...")
    all_admins = list(set(ADMIN_IDS + get_db_admins()))
    for admin_id in all_admins:
        try:
            await bot.send_message(admin_id, "🔴 <b>Bot বন্ধ হয়ে যাচ্ছে...</b>", parse_mode="HTML")
        except Exception:
            pass


# ─── Main ────────────────────────────────────────────────
async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Startup/shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("⚡ Starting polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
