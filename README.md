Ayyy 😈 FINAL STAGE — README + DEPLOY GUIDE
Rule follow: ek file, full content, copy-paste ready.
Iske baad koi bole “kaise deploy karu?” to tu seedha README phek ke marega 💀


---

🧱 FILE 39/??

📄 README.md

# 💀 FileLinkFucker

> **Underground File & Link Engine**  
> No Premium. No Limits. No Expiry (till admin deletes).

━━━━━━━━━━━━━━━━━━━
## ⚡ WHAT IS THIS?
━━━━━━━━━━━━━━━━━━━

**FileLinkFucker** is a Telegram bot + web API that converts:

- 📁 Telegram files  
- 🔗 Direct links  
- 📡 Telegram post links  

into **permanent download, streaming & TG mirror links**  
with **optional password protection** and **full admin control**.

This is **not a normal bot**.  
This is a **system**.

━━━━━━━━━━━━━━━━━━━
## 🔥 FEATURES
━━━━━━━━━━━━━━━━━━━

- ✅ File → Download / Stream / Telegram mirror links
- ✅ Link → Auto-detect & extract
- ✅ Password protected access
- ✅ No expiry (till admin nukes)
- ✅ Duplicate detection (DB-first)
- ✅ Recovery via storage channel
- ✅ FSUB support
- ✅ Full admin panel
- ✅ Hacker-style logs
- ✅ Web API (FastAPI)

━━━━━━━━━━━━━━━━━━━
## 🧠 COMMANDS
━━━━━━━━━━━━━━━━━━━

### 👤 USER

/start      - Check system status /help       - Help menu /about      - About the system

### 💀 ADMIN (OWNER ONLY)

/stats               - Bot statistics /user_data id|@u   - User full data + files /delete <file_key>   - Delete single file /delfile <user_id>   - Delete all files of a user

━━━━━━━━━━━━━━━━━━━
## 🗂️ PROJECT STRUCTURE
━━━━━━━━━━━━━━━━━━━

filelinkfucker/ │ ├── bot/ │   ├── main.py │   ├── client.py │   ├── config.py │   ├── texts.py │   ├── database/ │   ├── handlers/ │   ├── services/ │   └── utils/ │ ├── api/ │   └── main.py │ ├── storage/               # Local cache (auto-created) ├── requirements.txt ├── pyproject.toml ├── .env.example └── README.md

━━━━━━━━━━━━━━━━━━━
## 🔐 ENV SETUP
━━━━━━━━━━━━━━━━━━━

Copy `.env.example` → `.env`

```env
API_ID=123456
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

OWNER_ID=123456789

MONGO_URL=mongodb+srv://user:pass@cluster/db

BASE_URL=https://your-domain.com
API_HOST=0.0.0.0
API_PORT=8000

FSUB_CHANNELS=@leech_hub,@ABS_Updates
STORAGE_CHANNEL_ID=-100xxxxxxxxxx
LOG_CHANNEL_ID=-100xxxxxxxxxx

━━━━━━━━━━━━━━━━━━━

🚀 DEPLOYMENT

━━━━━━━━━━━━━━━━━━━

🟢 OPTION 1: LOCAL / VPS

git clone https://github.com/yourname/filelinkfucker
cd filelinkfucker

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

▶ Run BOT

python -m bot.main

▶ Run API (new terminal)

python -m api.main


---

🟣 OPTION 2: HEROKU

1️⃣ Create App

heroku create filelinkfucker

2️⃣ Add Buildpacks

heroku buildpacks:add heroku/python

3️⃣ Set Config Vars

heroku config:set API_ID=xxx
heroku config:set API_HASH=xxx
heroku config:set BOT_TOKEN=xxx
heroku config:set OWNER_ID=xxx
heroku config:set MONGO_URL=xxx
heroku config:set BASE_URL=https://your-app.herokuapp.com

4️⃣ Deploy

git push heroku main

5️⃣ Scale

heroku ps:scale web=1


---

🟠 OPTION 3: RAILWAY / RENDER

Use Python service

Add same ENV vars

Start command:


python -m bot.main

API:

python -m api.main

━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT NOTES

━━━━━━━━━━━━━━━━━━━

🔑 File Keys are permanent

🧨 Deleting file nukes all access

🔐 Passwords are HASHED (never stored plain)

📡 Storage channel = source of truth

🧠 Duplicate files reuse existing storage


━━━━━━━━━━━━━━━━━━━

💀 DISCLAIMER

━━━━━━━━━━━━━━━━━━━

This project is for educational & personal use only.
You are responsible for how you use it.

━━━━━━━━━━━━━━━━━━━

⚡ POWERED BY

━━━━━━━━━━━━━━━━━━━

🔥 @leech_hub
⚡ @ABS_Updates

💀 Bot by : ABS Studios
