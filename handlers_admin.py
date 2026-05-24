# ============================================
# BLACK PRO CYBER BOT - Admin Handlers
# ============================================

import asyncio
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from utils import (
    admin_panel_keyboard, admin_apk_list_keyboard,
    admin_course_list_keyboard, refer_settings_keyboard, back_keyboard
)
from config import ADMIN_IDS

admin_router = Router()


# ─── FSM States ───────────────────────────────────────────

class AdminStates(StatesGroup):
    # APK States
    waiting_apk_name = State()
    waiting_apk_desc = State()
    waiting_apk_file = State()
    waiting_apk_link = State()

    # Course States
    waiting_course_name = State()
    waiting_course_desc = State()
    waiting_course_file = State()
    waiting_course_link = State()

    # Broadcast
    waiting_broadcast = State()

    # Ban/Unban
    waiting_ban_id = State()
    waiting_unban_id = State()

    # User Info
    waiting_user_info_id = State()

    # Refer Settings
    waiting_apk_refer_count = State()
    waiting_course_refer_count = State()

    # Admin Management
    waiting_add_admin_id = State()
    waiting_remove_admin_id = State()


# ─── Helper ───────────────────────────────────────────────

def get_all_admins():
    return list(set(ADMIN_IDS + db.get_db_admins()))


def is_admin(user_id: int) -> bool:
    return user_id in get_all_admins()


def admin_only(func):
    """Decorator to restrict access to admins only."""
    async def wrapper(event, *args, **kwargs):
        if isinstance(event, Message):
            uid = event.from_user.id
        elif isinstance(event, CallbackQuery):
            uid = event.from_user.id
        else:
            return
        if not is_admin(uid):
            if isinstance(event, Message):
                await event.answer("🚫 এই কমান্ড শুধু Admin দের জন্য!")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Admin Only!", show_alert=True)
            return
        return await func(event, *args, **kwargs)
    return wrapper


# ─── /admin Command ───────────────────────────────────────

@admin_router.message(Command("admin"))
async def admin_panel_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 এই কমান্ড শুধু Admin দের জন্য!")
        return
    await message.answer(
        """╔══════════════════════════╗
║  👑  ADMIN PANEL  👑     ║
╚══════════════════════════╝

স্বাগতম Admin! নিচের মেনু থেকে
যেকোনো অপশন বেছে নিন:""",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data == "admin_panel")
async def admin_panel_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        """╔══════════════════════════╗
║  👑  ADMIN PANEL  👑     ║
╚══════════════════════════╝

স্বাগতম Admin! নিচের মেনু থেকে
যেকোনো অপশন বেছে নিন:""",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )


# ─── User Count ───────────────────────────────────────────

@admin_router.callback_query(F.data == "admin_user_count")
async def admin_user_count(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    count = db.get_user_count()
    await callback.answer(f"👥 মোট User: {count}", show_alert=True)


# ─── APK Management ───────────────────────────────────────

@admin_router.callback_query(F.data == "admin_add_apk")
async def admin_add_apk_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_apk_name)
    await callback.message.edit_text(
        "📱 <b>নতুন APK যোগ করুন</b>\n\n✏️ APK এর নাম লিখুন:\n\n/cancel - বাতিল করতে",
        reply_markup=None, parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_apk_name)
async def admin_apk_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল করা হয়েছে।", reply_markup=admin_panel_keyboard())
        return
    await state.update_data(apk_name=message.text)
    await state.set_state(AdminStates.waiting_apk_desc)
    await message.answer("📝 APK এর বিবরণ লিখুন (অথবা /skip):\n\n/cancel - বাতিল করতে")


@admin_router.message(AdminStates.waiting_apk_desc)
async def admin_apk_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    desc = "" if message.text == "/skip" else message.text
    await state.update_data(apk_desc=desc)
    await state.set_state(AdminStates.waiting_apk_file)
    await message.answer("📎 APK File পাঠান (অথবা /skip):\n\n/cancel - বাতিল করতে")


@admin_router.message(AdminStates.waiting_apk_file)
async def admin_apk_file(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    file_id = ""
    if message.text == "/skip":
        pass
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer("⚠️ Document পাঠান অথবা /skip লিখুন।")
        return
    await state.update_data(apk_file_id=file_id)
    await state.set_state(AdminStates.waiting_apk_link)
    await message.answer("🔗 APK Download Link দিন (অথবা /skip):\n\n/cancel - বাতিল করতে")


@admin_router.message(AdminStates.waiting_apk_link)
async def admin_apk_link(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    link = "" if message.text == "/skip" else message.text
    data = await state.get_data()
    apk_id = db.add_apk(
        name=data['apk_name'],
        description=data.get('apk_desc', ''),
        file_id=data.get('apk_file_id', ''),
        download_link=link,
        added_by=message.from_user.id
    )
    await state.clear()
    await message.answer(
        f"✅ <b>APK সফলভাবে যোগ হয়েছে!</b>\n\n"
        f"📱 <b>নাম:</b> {data['apk_name']}\n"
        f"🆔 <b>ID:</b> {apk_id}",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data == "admin_del_apk")
async def admin_del_apk(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    apks = db.get_all_apks()
    if not apks:
        await callback.answer("📭 কোনো APK নেই!", show_alert=True)
        return
    await callback.message.edit_text(
        "🗑️ <b>কোন APK মুছবেন?</b>",
        reply_markup=admin_apk_list_keyboard(apks),
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data.startswith("admin_delete_apk_"))
async def admin_delete_apk(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    apk_id = int(callback.data.split("_")[-1])
    success = db.delete_apk(apk_id)
    if success:
        await callback.answer("✅ APK মুছে ফেলা হয়েছে!", show_alert=True)
    else:
        await callback.answer("❌ APK পাওয়া যায়নি!", show_alert=True)
    await callback.message.edit_text(
        """╔══════════════════════════╗
║  👑  ADMIN PANEL  👑     ║
╚══════════════════════════╝""",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )


# ─── Course Management ────────────────────────────────────

@admin_router.callback_query(F.data == "admin_add_course")
async def admin_add_course_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_course_name)
    await callback.message.edit_text(
        "📚 <b>নতুন Course যোগ করুন</b>\n\n✏️ Course এর নাম লিখুন:\n\n/cancel - বাতিল করতে",
        reply_markup=None, parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_course_name)
async def admin_course_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    await state.update_data(course_name=message.text)
    await state.set_state(AdminStates.waiting_course_desc)
    await message.answer("📝 Course এর বিবরণ লিখুন (অথবা /skip):\n\n/cancel - বাতিল করতে")


@admin_router.message(AdminStates.waiting_course_desc)
async def admin_course_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    desc = "" if message.text == "/skip" else message.text
    await state.update_data(course_desc=desc)
    await state.set_state(AdminStates.waiting_course_file)
    await message.answer("📎 Course File পাঠান (অথবা /skip):\n\n/cancel - বাতিল করতে")


@admin_router.message(AdminStates.waiting_course_file)
async def admin_course_file(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    file_id = ""
    if message.text == "/skip":
        pass
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer("⚠️ Document পাঠান অথবা /skip লিখুন।")
        return
    await state.update_data(course_file_id=file_id)
    await state.set_state(AdminStates.waiting_course_link)
    await message.answer("🔗 Course Download Link দিন (অথবা /skip):\n\n/cancel - বাতিল করতে")


@admin_router.message(AdminStates.waiting_course_link)
async def admin_course_link(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    link = "" if message.text == "/skip" else message.text
    data = await state.get_data()
    course_id = db.add_course(
        name=data['course_name'],
        description=data.get('course_desc', ''),
        file_id=data.get('course_file_id', ''),
        download_link=link,
        added_by=message.from_user.id
    )
    await state.clear()
    await message.answer(
        f"✅ <b>Course সফলভাবে যোগ হয়েছে!</b>\n\n"
        f"📚 <b>নাম:</b> {data['course_name']}\n"
        f"🆔 <b>ID:</b> {course_id}",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data == "admin_del_course")
async def admin_del_course(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    courses = db.get_all_courses()
    if not courses:
        await callback.answer("📭 কোনো Course নেই!", show_alert=True)
        return
    await callback.message.edit_text(
        "🗑️ <b>কোন Course মুছবেন?</b>",
        reply_markup=admin_course_list_keyboard(courses),
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data.startswith("admin_delete_course_"))
async def admin_delete_course(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    course_id = int(callback.data.split("_")[-1])
    success = db.delete_course(course_id)
    if success:
        await callback.answer("✅ Course মুছে ফেলা হয়েছে!", show_alert=True)
    else:
        await callback.answer("❌ Course পাওয়া যায়নি!", show_alert=True)
    await callback.message.edit_text(
        """╔══════════════════════════╗
║  👑  ADMIN PANEL  👑     ║
╚══════════════════════════╝""",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )


# ─── Broadcast ────────────────────────────────────────────

@admin_router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_broadcast)
    await callback.message.edit_text(
        "📢 <b>Broadcast Message</b>\n\nযে message সব user দের পাঠাতে চান তা লিখুন:\n\n/cancel - বাতিল করতে",
        reply_markup=None, parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return

    await state.clear()
    users = db.get_all_users()
    sent = 0
    failed = 0
    status_msg = await message.answer(f"📢 <b>Broadcast শুরু হচ্ছে...</b>\n👥 মোট: {len(users)} জন", parse_mode="HTML")

    for uid in users:
        try:
            await bot.copy_message(uid, message.chat.id, message.message_id)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ <b>Broadcast সম্পন্ন!</b>\n\n"
        f"✅ সফল: {sent}\n❌ ব্যর্থ: {failed}\n👥 মোট: {len(users)}",
        parse_mode="HTML"
    )


# ─── Ban / Unban ──────────────────────────────────────────

@admin_router.callback_query(F.data == "admin_ban")
async def admin_ban_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_ban_id)
    await callback.message.edit_text(
        "🚫 <b>User Ban করুন</b>\n\nBan করতে User ID লিখুন:\n\n/cancel - বাতিল করতে",
        reply_markup=None, parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_ban_id)
async def admin_ban_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    try:
        target_id = int(message.text.strip())
        db.ban_user(target_id)
        await state.clear()
        await message.answer(
            f"✅ <b>User {target_id} কে Ban করা হয়েছে!</b>",
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ সঠিক User ID দিন!")


@admin_router.callback_query(F.data == "admin_unban")
async def admin_unban_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_unban_id)
    await callback.message.edit_text(
        "✅ <b>User Unban করুন</b>\n\nUnban করতে User ID লিখুন:\n\n/cancel - বাতিল করতে",
        reply_markup=None, parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_unban_id)
async def admin_unban_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    try:
        target_id = int(message.text.strip())
        db.unban_user(target_id)
        await state.clear()
        await message.answer(
            f"✅ <b>User {target_id} কে Unban করা হয়েছে!</b>",
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ সঠিক User ID দিন!")


# ─── User Info ────────────────────────────────────────────

@admin_router.callback_query(F.data == "admin_user_info")
async def admin_user_info_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_user_info_id)
    await callback.message.edit_text(
        "🔍 <b>User Info দেখুন</b>\n\nUser ID লিখুন:\n\n/cancel - বাতিল করতে",
        reply_markup=None, parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_user_info_id)
async def admin_user_info_show(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    try:
        target_id = int(message.text.strip())
        user = db.get_user(target_id)
        if not user:
            await message.answer("❌ User পাওয়া যায়নি!")
            return
        await state.clear()
        username = f"@{user['username']}" if user.get('username') else "N/A"
        banned = "🚫 হ্যাঁ" if user.get('is_banned') else "✅ না"
        info = f"""╔══════════════════════════╗
║  🔍  USER INFO  🔍       ║
╚══════════════════════════╝

👤 <b>নাম:</b> {user.get('full_name', 'N/A')}
🆔 <b>ID:</b> <code>{user['user_id']}</code>
📧 <b>Username:</b> {username}
🚫 <b>Banned:</b> {banned}

━━━━━━━━━━━━━━━━━━━━━━
📊 <b>বর্তমান Refer:</b> {user.get('refer_count', 0)}
📈 <b>মোট Refer:</b> {user.get('total_refers', 0)}
📱 <b>APK নিয়েছে:</b> {user.get('apk_claimed', 0)}টি
📚 <b>Course নিয়েছে:</b> {user.get('course_claimed', 0)}টি
━━━━━━━━━━━━━━━━━━━━━━
📅 <b>Join করেছে:</b> {user.get('joined_at', 'N/A')}
⏰ <b>শেষ Active:</b> {user.get('last_active', 'N/A')}"""
        await message.answer(info, reply_markup=admin_panel_keyboard(), parse_mode="HTML")
    except ValueError:
        await message.answer("❌ সঠিক User ID দিন!")


# ─── Refer Settings ───────────────────────────────────────

@admin_router.callback_query(F.data == "admin_refer_settings")
async def admin_refer_settings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    apk_req = int(db.get_setting('apk_refer_required') or 3)
    course_req = int(db.get_setting('course_refer_required') or 5)
    await callback.message.edit_text(
        f"⚙️ <b>Refer সেটিং</b>\n\nবর্তমান সেটিং:\n📱 APK: {apk_req} Refer\n📚 Course: {course_req} Refer",
        reply_markup=refer_settings_keyboard(apk_req, course_req),
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data == "change_apk_refer")
async def change_apk_refer_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_apk_refer_count)
    await callback.message.edit_text(
        "📱 APK এর জন্য কতটি Refer লাগবে? (সংখ্যা লিখুন)\n\n/cancel - বাতিল করতে",
        reply_markup=None
    )


@admin_router.message(AdminStates.waiting_apk_refer_count)
async def change_apk_refer_set(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    try:
        count = int(message.text.strip())
        if count < 1:
            raise ValueError
        db.set_setting('apk_refer_required', count)
        await state.clear()
        await message.answer(
            f"✅ APK Refer সংখ্যা <b>{count}</b> এ পরিবর্তন করা হয়েছে!",
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ সঠিক সংখ্যা দিন!")


@admin_router.callback_query(F.data == "change_course_refer")
async def change_course_refer_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_course_refer_count)
    await callback.message.edit_text(
        "📚 Course এর জন্য কতটি Refer লাগবে? (সংখ্যা লিখুন)\n\n/cancel - বাতিল করতে",
        reply_markup=None
    )


@admin_router.message(AdminStates.waiting_course_refer_count)
async def change_course_refer_set(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    try:
        count = int(message.text.strip())
        if count < 1:
            raise ValueError
        db.set_setting('course_refer_required', count)
        await state.clear()
        await message.answer(
            f"✅ Course Refer সংখ্যা <b>{count}</b> এ পরিবর্তন করা হয়েছে!",
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ সঠিক সংখ্যা দিন!")


# ─── Admin Management ─────────────────────────────────────

@admin_router.callback_query(F.data == "admin_add_admin")
async def admin_add_admin_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_add_admin_id)
    await callback.message.edit_text(
        "👑 <b>নতুন Admin যোগ করুন</b>\n\nনতুন Admin এর User ID লিখুন:\n\n/cancel - বাতিল করতে",
        reply_markup=None, parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_add_admin_id)
async def admin_add_admin_set(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    try:
        new_admin_id = int(message.text.strip())
        success = db.add_admin(new_admin_id, message.from_user.id)
        await state.clear()
        if success:
            await message.answer(
                f"✅ <b>User {new_admin_id} কে Admin বানানো হয়েছে!</b>",
                reply_markup=admin_panel_keyboard(), parse_mode="HTML"
            )
            try:
                await bot.send_message(new_admin_id, "🎉 আপনাকে BLACK PRO CYBER BOT এর Admin বানানো হয়েছে!")
            except Exception:
                pass
        else:
            await message.answer("⚠️ এই User আগে থেকেই Admin!", reply_markup=admin_panel_keyboard())
    except ValueError:
        await message.answer("❌ সঠিক User ID দিন!")


@admin_router.callback_query(F.data == "admin_remove_admin")
async def admin_remove_admin_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 Admin Only!", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_remove_admin_id)
    await callback.message.edit_text(
        "❌ <b>Admin সরান</b>\n\nAdmin এর User ID লিখুন:\n\n/cancel - বাতিল করতে",
        reply_markup=None, parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_remove_admin_id)
async def admin_remove_admin_set(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ বাতিল।", reply_markup=admin_panel_keyboard())
        return
    try:
        rm_id = int(message.text.strip())
        if rm_id in ADMIN_IDS:
            await message.answer("❌ Config এ থাকা Admin কে সরানো যাবে না!")
            return
        success = db.remove_admin(rm_id)
        await state.clear()
        if success:
            await message.answer(
                f"✅ <b>User {rm_id} এর Admin পদ সরানো হয়েছে!</b>",
                reply_markup=admin_panel_keyboard(), parse_mode="HTML"
            )
        else:
            await message.answer("❌ এই User Admin নন!", reply_markup=admin_panel_keyboard())
    except ValueError:
        await message.answer("❌ সঠিক User ID দিন!")
