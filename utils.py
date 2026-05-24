# ============================================
# BLACK PRO CYBER BOT - Utilities
# ============================================

import time
import asyncio
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import (CHANNEL_1, CHANNEL_2, FACEBOOK_GROUP_LINK,
                    TELEGRAM_GROUP_LINK, CONTACT_USERNAME, COOLDOWN_SECONDS)

# ─── Anti-Spam Cooldown ───────────────────────────────────
_cooldown_cache = {}


def is_on_cooldown(user_id: int) -> bool:
    now = time.time()
    last = _cooldown_cache.get(user_id, 0)
    if now - last < COOLDOWN_SECONDS:
        return True
    _cooldown_cache[user_id] = now
    return False


# ─── Channel Membership Check ─────────────────────────────

async def check_channel_membership(bot: Bot, user_id: int) -> tuple[bool, bool]:
    """Returns (joined_ch1, joined_ch2)"""
    async def check_one(channel):
        try:
            member = await bot.get_chat_member(channel, user_id)
            return member.status not in ("left", "kicked", "banned")
        except Exception:
            return False

    ch1 = await check_one(CHANNEL_1)
    ch2 = await check_one(CHANNEL_2)
    return ch1, ch2


async def is_fully_joined(bot: Bot, user_id: int) -> bool:
    ch1, ch2 = await check_channel_membership(bot, user_id)
    return ch1 and ch2


# ─── Keyboards ────────────────────────────────────────────

def main_menu_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔗 আমার Refer Link", callback_data="my_refer_link"),
            InlineKeyboardButton(text="💰 আমার Refer Balance", callback_data="my_balance"),
        ],
        [
            InlineKeyboardButton(text="📱 APK নিন", callback_data="get_apk"),
            InlineKeyboardButton(text="📚 Course নিন", callback_data="get_course"),
        ],
        [
            InlineKeyboardButton(text="👑 Admin এর সাথে যোগাযোগ", url=f"https://t.me/{CONTACT_USERNAME.lstrip('@')}"),
        ],
        [
            InlineKeyboardButton(text="📘 Facebook Group", url=FACEBOOK_GROUP_LINK),
            InlineKeyboardButton(text="✈️ Telegram Group", url=TELEGRAM_GROUP_LINK),
        ],
    ])
    return kb


def force_join_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Channel 1 Join করুন", url=f"https://t.me/{CHANNEL_1.lstrip('@')}"),
        ],
        [
            InlineKeyboardButton(text="✅ Channel 2 Join করুন", url=f"https://t.me/{CHANNEL_2.lstrip('@')}"),
        ],
        [
            InlineKeyboardButton(text="🔄 Verify করুন", callback_data="verify_join"),
        ],
        [
            InlineKeyboardButton(text="📘 Facebook Group", url=FACEBOOK_GROUP_LINK),
            InlineKeyboardButton(text="✈️ Telegram Group", url=TELEGRAM_GROUP_LINK),
        ],
    ])
    return kb


def back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 মেনুতে ফিরুন", callback_data="back_to_menu")]
    ])


def apk_list_keyboard(apks):
    buttons = []
    for apk in apks:
        buttons.append([
            InlineKeyboardButton(
                text=f"📱 {apk['name']}",
                callback_data=f"claim_apk_{apk['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 মেনুতে ফিরুন", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def course_list_keyboard(courses):
    buttons = []
    for course in courses:
        buttons.append([
            InlineKeyboardButton(
                text=f"📚 {course['name']}",
                callback_data=f"claim_course_{course['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 মেনুতে ফিরুন", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_panel_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ APK যোগ করুন", callback_data="admin_add_apk"),
            InlineKeyboardButton(text="🗑️ APK মুছুন", callback_data="admin_del_apk"),
        ],
        [
            InlineKeyboardButton(text="➕ Course যোগ করুন", callback_data="admin_add_course"),
            InlineKeyboardButton(text="🗑️ Course মুছুন", callback_data="admin_del_course"),
        ],
        [
            InlineKeyboardButton(text="👥 মোট User", callback_data="admin_user_count"),
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton(text="🚫 Ban User", callback_data="admin_ban"),
            InlineKeyboardButton(text="✅ Unban User", callback_data="admin_unban"),
        ],
        [
            InlineKeyboardButton(text="🔍 User Info", callback_data="admin_user_info"),
            InlineKeyboardButton(text="⚙️ Refer সেটিং", callback_data="admin_refer_settings"),
        ],
        [
            InlineKeyboardButton(text="👑 Admin যোগ করুন", callback_data="admin_add_admin"),
            InlineKeyboardButton(text="❌ Admin সরান", callback_data="admin_remove_admin"),
        ],
        [
            InlineKeyboardButton(text="🔙 মেনুতে ফিরুন", callback_data="back_to_menu"),
        ],
    ])
    return kb


def admin_apk_list_keyboard(apks, action="delete"):
    buttons = []
    for apk in apks:
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑️ {apk['name']} (ID: {apk['id']})",
                callback_data=f"admin_delete_apk_{apk['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_course_list_keyboard(courses):
    buttons = []
    for course in courses:
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑️ {course['name']} (ID: {course['id']})",
                callback_data=f"admin_delete_course_{course['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def refer_settings_keyboard(apk_req, course_req):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"📱 APK: {apk_req} Refer", callback_data="change_apk_refer"),
        ],
        [
            InlineKeyboardButton(text=f"📚 Course: {course_req} Refer", callback_data="change_course_refer"),
        ],
        [InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_panel")],
    ])
    return kb


# ─── Messages ─────────────────────────────────────────────

def start_message(user_name):
    return f"""╔══════════════════════════╗
║  🌟 BLACK PRO CYBER BOT 🌟  ║
╚══════════════════════════╝

আসসালামুআলাইকুম 🌸
<b>{user_name}</b>, আপনাকে স্বাগতম! 🔥

━━━━━━━━━━━━━━━━━━━━━━
🤖 <b>এই বটের মাধ্যমে আপনারা ফ্রি APK এবং
Premium Course নিতে পারবেন Refer System
এর মাধ্যমে।</b>
━━━━━━━━━━━━━━━━━━━━━━

📱 <b>APK নিতে:</b> ৩টি Valid Refer লাগবে
📚 <b>Course নিতে:</b> ৫টি Valid Refer লাগবে

⚠️ <b>নিয়ম:</b>
├─ APK নেওয়ার পর Refer Balance ০ হবে
├─ একই Refer বারবার Count হবে না
└─ Channel Join ছাড়া বট কাজ করবে না

🚀 নিচের মেনু থেকে শুরু করুন!"""


def force_join_message():
    return """╔══════════════════════════╗
║  ⚠️  FORCE JOIN REQUIRED  ⚠️  ║
╚══════════════════════════╝

🔒 <b>বট ব্যবহার করতে হলে অবশ্যই</b>
<b>নিচের ২টি Channel Join করতে হবে!</b>

━━━━━━━━━━━━━━━━━━━━━━
✅ Channel 1 এ Join করুন
✅ Channel 2 এ Join করুন
━━━━━━━━━━━━━━━━━━━━━━

Join করার পর <b>"🔄 Verify করুন"</b> বাটনে
ক্লিক করুন।"""


def balance_message(user, apk_req, course_req):
    name = user.get('full_name', 'বন্ধু')
    refer_count = user.get('refer_count', 0)
    total_refers = user.get('total_refers', 0)
    apk_claimed = user.get('apk_claimed', 0)
    course_claimed = user.get('course_claimed', 0)

    apk_need = max(0, apk_req - refer_count)
    course_need = max(0, course_req - refer_count)

    apk_bar = "🟢" * refer_count + "⚪" * max(0, apk_req - refer_count)
    course_bar = "🟢" * refer_count + "⚪" * max(0, course_req - refer_count)

    return f"""╔══════════════════════════╗
║  💰  আমার Refer Balance  💰  ║
╚══════════════════════════╝

👤 <b>নাম:</b> {name}

━━━━━━━━━━━━━━━━━━━━━━
📊 <b>বর্তমান Refer Balance:</b> {refer_count}
📈 <b>মোট Refer:</b> {total_refers}
━━━━━━━━━━━━━━━━━━━━━━

📱 <b>APK Progress</b> ({refer_count}/{apk_req}):
{apk_bar}
{'✅ APK নেওয়ার যোগ্য!' if refer_count >= apk_req else f'❌ আরো {apk_need}টি Refer দরকার'}

📚 <b>Course Progress</b> ({refer_count}/{course_req}):
{course_bar}
{'✅ Course নেওয়ার যোগ্য!' if refer_count >= course_req else f'❌ আরো {course_need}টি Refer দরকার'}

━━━━━━━━━━━━━━━━━━━━━━
🏆 <b>APK নিয়েছেন:</b> {apk_claimed}টি
🎓 <b>Course নিয়েছেন:</b> {course_claimed}টি"""


def refer_link_message(user_id, bot_username, refer_count, total_refers):
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    return f"""╔══════════════════════════╗
║  🔗  আমার Refer Link  🔗  ║
╚══════════════════════════╝

🌐 <b>আপনার Unique Refer Link:</b>

<code>{link}</code>

━━━━━━━━━━━━━━━━━━━━━━
📊 <b>বর্তমান Refer:</b> {refer_count}
📈 <b>মোট Refer:</b> {total_refers}
━━━━━━━━━━━━━━━━━━━━━━

💡 <b>কিভাবে Refer করবেন?</b>
├─ উপরের Link টি কপি করুন
├─ বন্ধুদের সাথে Share করুন
├─ তারা Join করলে আপনার Count বাড়বে
└─ ৩টি Refer = ১টি APK 🎉

⚠️ <i>Note: শুধু নতুন User এর Refer Count হবে</i>"""


def new_user_notification(referrer_name, new_user_name, new_user_id, refer_count):
    return f"""🔔 <b>নতুন Refer!</b>

👤 <b>Referrer:</b> {referrer_name}
🆕 <b>নতুন User:</b> {new_user_name} (<code>{new_user_id}</code>)
📊 <b>নতুন Refer Count:</b> {refer_count}"""
