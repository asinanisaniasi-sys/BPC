# 🌟 BLACK PRO CYBER BOT

**একটি সম্পূর্ণ Bengali Telegram Referral Bot**

---

## 📁 File Structure

```
black_pro_cyber_bot/
├── main.py              # Main entry point
├── config.py            # Configuration (edit this first!)
├── database.py          # SQLite database handler
├── handlers_user.py     # User command handlers
├── handlers_admin.py    # Admin panel handlers
├── utils.py             # Keyboards, messages, utilities
├── requirements.txt     # Python dependencies
├── Procfile             # For Railway/Render/Koyeb
├── runtime.txt          # Python version
└── README.md            # This file
```

---

## ⚙️ Setup Guide

### Step 1: Edit config.py

Open `config.py` and fill in:

```python
BOT_TOKEN = "your_bot_token_here"         # From @BotFather
API_ID    = 12345678                       # From my.telegram.org
API_HASH  = "your_api_hash"               # From my.telegram.org

ADMIN_IDS = [123456789, 987654321]        # Your Telegram User IDs

CHANNEL_1 = "@your_channel_1"             # Force join channel 1
CHANNEL_2 = "@your_channel_2"             # Force join channel 2

FACEBOOK_GROUP_LINK = "https://facebook.com/groups/your_group"
TELEGRAM_GROUP_LINK = "https://t.me/your_group"

LOGS_CHANNEL = "@your_logs_channel"       # Optional: set None to disable
```

**How to get your Telegram User ID:**
- Message @userinfobot on Telegram

**How to get API_ID and API_HASH:**
- Go to https://my.telegram.org
- Log in → App Configuration → Create new app

### Step 2: Make bot admin in channels

Add your bot as **Admin** to both CHANNEL_1 and CHANNEL_2 so it can check membership.

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the bot

```bash
python main.py
```

---

## 🚀 Hosting on Railway

1. Push your code to a GitHub repo
2. Go to https://railway.app
3. New Project → Deploy from GitHub repo
4. Set environment variables (or use config.py directly)
5. Deploy!

## 🚀 Hosting on Render

1. Push code to GitHub
2. Go to https://render.com
3. New → Background Worker
4. Connect GitHub repo
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python main.py`
7. Deploy!

## 🚀 Hosting on Koyeb

1. Push code to GitHub
2. Go to https://app.koyeb.com
3. Create App → GitHub → select repo
4. Set run command: `python main.py`
5. Deploy!

---

## 👑 Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | Open Admin Panel |
| `/cancel` | Cancel current operation |

### Admin Panel Features:
- ➕ APK যোগ করুন / মুছুন
- ➕ Course যোগ করুন / মুছুন
- 👥 মোট User Count দেখুন
- 📢 সব User দের Broadcast
- 🚫 User Ban / ✅ Unban
- 🔍 যেকোনো User Info দেখুন
- ⚙️ APK/Course Refer সংখ্যা পরিবর্তন
- 👑 নতুন Admin যোগ / সরান

---

## 🤖 User Features

| Button | Function |
|--------|----------|
| 🔗 আমার Refer Link | Unique referral link দেখুন |
| 💰 আমার Refer Balance | Progress ও stats দেখুন |
| 📱 APK নিন | 3 Refer দিয়ে APK নিন |
| 📚 Course নিন | 5 Refer দিয়ে Course নিন |
| 👑 Admin যোগাযোগ | Admin এর সাথে chat করুন |

---

## 🔒 Anti-Fake Refer System

- ✅ নতুন User এর Refer শুধু Count হয়
- ✅ একই User দুইবার Count হয় না
- ✅ নিজেকে Refer করা যায় না
- ✅ Banned User Refer Count হয় না
- ✅ Anti-spam cooldown system

---

## 📞 Support

Developer: @jiolinhacker
