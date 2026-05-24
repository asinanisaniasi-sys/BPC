# ============================================
# BLACK PRO CYBER BOT - User Handlers
# ============================================

import asyncio
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import database as db
from utils import (
    is_fully_joined, force_join_keyboard, main_menu_keyboard,
    apk_list_keyboard, course_list_keyboard, back_keyboard,
    start_message, force_join_message, balance_message,
    refer_link_message, new_user_notification, is_on_cooldown
)
from config import ADMIN_IDS, LOGS_CHANNEL

user_router = Router()


def get_all_admins():
    return list(set(ADMIN_IDS + db.get_db_admins()))


async def send_log(bot: Bot, text: str):
    if LOGS_CHANNEL:
        try:
            await bot.send_message(LOGS_CHANNEL, text, parse_mode="HTML")
        except Exception:
            pass


# ─── /start Handler ───────────────────────────────────────

@user_router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = message.from_user
    user_id = user.id
    args = message.text.split()

    # Check if banned
    if db.is_banned(user_id):
        await message.answer("🚫 আপনি এই বট ব্যবহার করতে পারবেন না। (Banned)")
        return

    # Typing animation
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(0.5)

    # Extract referrer
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].split("_")[1])
            if referrer_id == user_id:
                referrer_id = None  # Can't refer yourself
        except (ValueError, IndexError):
            referrer_id = None

    # Add user to DB
    is_new = db.add_user(
        user_id=user_id,
        username=user.username,
        full_name=user.full_name,
        referred_by=referrer_id
    )

    # Update username if returning user
    if not is_new:
        db.update_username(user_id, user.username, user.full_name)
        db.update_last_active(user_id)

    # Process referral for new users only
    if is_new and referrer_id and referrer_id != user_id:
        referrer = db.get_user(referrer_id)
        if referrer and not db.is_banned(referrer_id):
            success = db.add_referral(referrer_id, user_id)
            if success:
                new_count = db.get_refer_count(referrer_id)
                # Notify referrer
                try:
                    await bot.send_message(
                        referrer_id,
                        f"🎉 <b>নতুন Refer!</b>\n\n"
                        f"👤 <b>{user.full_name}</b> আপনার লিংক দিয়ে জয়েন করেছে!\n"
                        f"📊 <b>আপনার Refer Count:</b> {new_count}",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

                # Notify all admins
                for admin_id in get_all_admins():
                    try:
                        await bot.send_message(
                            admin_id,
                            new_user_notification(
                                referrer.get('full_name', 'Unknown'),
                                user.full_name,
                                user_id,
                                new_count
                            ),
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass

                # Log it
                await send_log(bot, f"🔗 New Referral: {user.full_name} referred by {referrer.get('full_name')}")

    # Check force join
    joined = await is_fully_joined(bot, user_id)
    if not joined:
        await message.answer(
            force_join_message(),
            reply_markup=force_join_keyboard(),
            parse_mode="HTML"
        )
        return

    # Send welcome
    await message.answer(
        start_message(user.full_name),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


# ─── Verify Join Callback ─────────────────────────────────

@user_router.callback_query(F.data == "verify_join")
async def verify_join(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if db.is_banned(user_id):
        await callback.answer("🚫 আপনি Ban হয়েছেন!", show_alert=True)
        return

    await callback.answer("⏳ চেক করা হচ্ছে...", show_alert=False)
    await bot.send_chat_action(callback.message.chat.id, "typing")
    await asyncio.sleep(1)

    joined = await is_fully_joined(bot, user_id)
    if joined:
        db.update_last_active(user_id)
        await callback.message.edit_text(
            start_message(callback.from_user.full_name),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.answer(
            "❌ আপনি এখনো সব Channel Join করেননি! Join করে আবার চেষ্টা করুন।",
            show_alert=True
        )


# ─── Back to Menu ─────────────────────────────────────────

@user_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if db.is_banned(user_id):
        await callback.answer("🚫 আপনি Ban হয়েছেন!", show_alert=True)
        return

    joined = await is_fully_joined(bot, user_id)
    if not joined:
        await callback.message.edit_text(
            force_join_message(),
            reply_markup=force_join_keyboard(),
            parse_mode="HTML"
        )
        return

    await callback.message.edit_text(
        start_message(callback.from_user.full_name),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


# ─── My Refer Link ────────────────────────────────────────

@user_router.callback_query(F.data == "my_refer_link")
async def my_refer_link(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if db.is_banned(user_id):
        await callback.answer("🚫 Ban!", show_alert=True)
        return

    if is_on_cooldown(user_id):
        await callback.answer("⏳ একটু অপেক্ষা করুন...", show_alert=False)
        return

    joined = await is_fully_joined(bot, user_id)
    if not joined:
        await callback.message.edit_text(
            force_join_message(),
            reply_markup=force_join_keyboard(),
            parse_mode="HTML"
        )
        return

    bot_info = await bot.get_me()
    user = db.get_user(user_id)

    await callback.message.edit_text(
        refer_link_message(
            user_id,
            bot_info.username,
            user.get('refer_count', 0),
            user.get('total_refers', 0)
        ),
        reply_markup=back_keyboard(),
        parse_mode="HTML"
    )


# ─── My Balance ───────────────────────────────────────────

@user_router.callback_query(F.data == "my_balance")
async def my_balance(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if db.is_banned(user_id):
        await callback.answer("🚫 Ban!", show_alert=True)
        return

    if is_on_cooldown(user_id):
        await callback.answer("⏳ একটু অপেক্ষা করুন...", show_alert=False)
        return

    joined = await is_fully_joined(bot, user_id)
    if not joined:
        await callback.message.edit_text(
            force_join_message(),
            reply_markup=force_join_keyboard(),
            parse_mode="HTML"
        )
        return

    user = db.get_user(user_id)
    apk_req = int(db.get_setting('apk_refer_required') or 3)
    course_req = int(db.get_setting('course_refer_required') or 5)

    await callback.message.edit_text(
        balance_message(user, apk_req, course_req),
        reply_markup=back_keyboard(),
        parse_mode="HTML"
    )


# ─── Get APK ─────────────────────────────────────────────

@user_router.callback_query(F.data == "get_apk")
async def get_apk(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if db.is_banned(user_id):
        await callback.answer("🚫 Ban!", show_alert=True)
        return

    joined = await is_fully_joined(bot, user_id)
    if not joined:
        await callback.message.edit_text(
            force_join_message(),
            reply_markup=force_join_keyboard(),
            parse_mode="HTML"
        )
        return

    user = db.get_user(user_id)
    apk_req = int(db.get_setting('apk_refer_required') or 3)
    refer_count = user.get('refer_count', 0)

    if refer_count < apk_req:
        needed = apk_req - refer_count
        bot_info = await bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        await callback.message.edit_text(
            f"""╔══════════════════════════╗
║  📱  APK নিন  📱         ║
╚══════════════════════════╝

❌ <b>আপনার পর্যাপ্ত Refer নেই!</b>

━━━━━━━━━━━━━━━━━━━━━━
📊 <b>আপনার Refer:</b> {refer_count}/{apk_req}
⚠️ <b>আরো {needed}টি Refer দরকার</b>
━━━━━━━━━━━━━━━━━━━━━━

🔗 <b>আপনার Refer Link:</b>
<code>{ref_link}</code>

বন্ধুদের এই লিংক শেয়ার করুন এবং
{apk_req}টি Refer সম্পন্ন করুন! 🚀""",
            reply_markup=back_keyboard(),
            parse_mode="HTML"
        )
        return

    apks = db.get_all_apks()
    if not apks:
        await callback.message.edit_text(
            "📭 <b>এখন কোনো APK উপলব্ধ নেই।</b>\n\nপরে আবার চেষ্টা করুন!",
            reply_markup=back_keyboard(),
            parse_mode="HTML"
        )
        return

    await callback.message.edit_text(
        f"""╔══════════════════════════╗
║  📱  APK List  📱         ║
╚══════════════════════════╝

✅ <b>আপনার {refer_count}টি Refer আছে!</b>
নিচের যেকোনো APK নিন:

⚠️ <i>APK নেওয়ার পর Refer Balance ০ হবে</i>""",
        reply_markup=apk_list_keyboard(apks),
        parse_mode="HTML"
    )


# ─── Claim APK ────────────────────────────────────────────

@user_router.callback_query(F.data.startswith("claim_apk_"))
async def claim_apk(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    apk_id = int(callback.data.split("_")[-1])

    if db.is_banned(user_id):
        await callback.answer("🚫 Ban!", show_alert=True)
        return

    joined = await is_fully_joined(bot, user_id)
    if not joined:
        await callback.answer("❌ Channel Join করুন!", show_alert=True)
        return

    user = db.get_user(user_id)
    apk_req = int(db.get_setting('apk_refer_required') or 3)

    if user.get('refer_count', 0) < apk_req:
        await callback.answer("❌ পর্যাপ্ত Refer নেই!", show_alert=True)
        return

    apk = db.get_apk(apk_id)
    if not apk:
        await callback.answer("❌ APK পাওয়া যায়নি!", show_alert=True)
        return

    # Claim APK
    db.claim_apk(user_id, apk_id)

    msg = f"""╔══════════════════════════╗
║  🎉  APK Claimed!  🎉    ║
╚══════════════════════════╝

✅ <b>আপনি সফলভাবে APK নিয়েছেন!</b>

📱 <b>APK নাম:</b> {apk['name']}
"""
    if apk.get('description'):
        msg += f"📝 <b>বিবরণ:</b> {apk['description']}\n"

    msg += "\n━━━━━━━━━━━━━━━━━━━━━━\n"

    if apk.get('download_link'):
        msg += f"🔗 <b>Download Link:</b>\n{apk['download_link']}\n"

    msg += "\n⚠️ <i>আপনার Refer Balance ০ হয়ে গেছে।\nআবার নতুন APK নিতে নতুন Refer করুন।</i>"

    await callback.message.edit_text(msg, reply_markup=back_keyboard(), parse_mode="HTML")

    # Send file if available
    if apk.get('file_id'):
        try:
            await bot.send_document(callback.message.chat.id, apk['file_id'],
                                    caption=f"📱 {apk['name']}")
        except Exception:
            pass

    await send_log(bot, f"📱 APK Claimed: {callback.from_user.full_name} claimed {apk['name']}")


# ─── Get Course ───────────────────────────────────────────

@user_router.callback_query(F.data == "get_course")
async def get_course(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if db.is_banned(user_id):
        await callback.answer("🚫 Ban!", show_alert=True)
        return

    joined = await is_fully_joined(bot, user_id)
    if not joined:
        await callback.message.edit_text(
            force_join_message(),
            reply_markup=force_join_keyboard(),
            parse_mode="HTML"
        )
        return

    user = db.get_user(user_id)
    course_req = int(db.get_setting('course_refer_required') or 5)
    refer_count = user.get('refer_count', 0)

    if refer_count < course_req:
        needed = course_req - refer_count
        bot_info = await bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        await callback.message.edit_text(
            f"""╔══════════════════════════╗
║  📚  Course নিন  📚      ║
╚══════════════════════════╝

❌ <b>আপনার পর্যাপ্ত Refer নেই!</b>

━━━━━━━━━━━━━━━━━━━━━━
📊 <b>আপনার Refer:</b> {refer_count}/{course_req}
⚠️ <b>আরো {needed}টি Refer দরকার</b>
━━━━━━━━━━━━━━━━━━━━━━

🔗 <b>আপনার Refer Link:</b>
<code>{ref_link}</code>

বন্ধুদের এই লিংক শেয়ার করুন এবং
{course_req}টি Refer সম্পন্ন করুন! 🚀""",
            reply_markup=back_keyboard(),
            parse_mode="HTML"
        )
        return

    courses = db.get_all_courses()
    if not courses:
        await callback.message.edit_text(
            "📭 <b>এখন কোনো Course উপলব্ধ নেই।</b>\n\nপরে আবার চেষ্টা করুন!",
            reply_markup=back_keyboard(),
            parse_mode="HTML"
        )
        return

    await callback.message.edit_text(
        f"""╔══════════════════════════╗
║  📚  Course List  📚     ║
╚══════════════════════════╝

✅ <b>আপনার {refer_count}টি Refer আছে!</b>
নিচের যেকোনো Course নিন:

⚠️ <i>Course নেওয়ার পর Refer Balance ০ হবে</i>""",
        reply_markup=course_list_keyboard(courses),
        parse_mode="HTML"
    )


# ─── Claim Course ─────────────────────────────────────────

@user_router.callback_query(F.data.startswith("claim_course_"))
async def claim_course(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    course_id = int(callback.data.split("_")[-1])

    if db.is_banned(user_id):
        await callback.answer("🚫 Ban!", show_alert=True)
        return

    joined = await is_fully_joined(bot, user_id)
    if not joined:
        await callback.answer("❌ Channel Join করুন!", show_alert=True)
        return

    user = db.get_user(user_id)
    course_req = int(db.get_setting('course_refer_required') or 5)

    if user.get('refer_count', 0) < course_req:
        await callback.answer("❌ পর্যাপ্ত Refer নেই!", show_alert=True)
        return

    course = db.get_course(course_id)
    if not course:
        await callback.answer("❌ Course পাওয়া যায়নি!", show_alert=True)
        return

    # Claim Course
    db.claim_course(user_id, course_id)

    msg = f"""╔══════════════════════════╗
║  🎉  Course Claimed! 🎉  ║
╚══════════════════════════╝

✅ <b>আপনি সফলভাবে Course নিয়েছেন!</b>

📚 <b>Course নাম:</b> {course['name']}
"""
    if course.get('description'):
        msg += f"📝 <b>বিবরণ:</b> {course['description']}\n"

    msg += "\n━━━━━━━━━━━━━━━━━━━━━━\n"

    if course.get('download_link'):
        msg += f"🔗 <b>Download Link:</b>\n{course['download_link']}\n"

    msg += "\n⚠️ <i>আপনার Refer Balance ০ হয়ে গেছে।\nআবার নতুন Course নিতে নতুন Refer করুন।</i>"

    await callback.message.edit_text(msg, reply_markup=back_keyboard(), parse_mode="HTML")

    if course.get('file_id'):
        try:
            await bot.send_document(callback.message.chat.id, course['file_id'],
                                    caption=f"📚 {course['name']}")
        except Exception:
            pass

    await send_log(bot, f"📚 Course Claimed: {callback.from_user.full_name} claimed {course['name']}")
