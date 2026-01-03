# =========================================================
# ⛧⃟ LOFI PAPA GC TOOL — FINAL PRODUCTION FILE ⛧⃟
# Ultra Fast • Stable • No Auto Stop
# =========================================================

import asyncio
import json
import os
import io
import logging
from typing import Dict

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import RetryAfter, TimedOut
from gtts import gTTS

# ---------------- CONFIG ----------------
TOKENS = [
  "8573637179:AAGCSunvJ2ImXo91uiZMsL8qYosalHbxG8g",
"8568640757:AAGnx23gXlyYtyANpfFR6QUTe1XBh7aGo0k",
"8132064693:AAFbzGudnXFAhVAYBu4Nr3AL6IyGPVRSCCw",
"8573986079:AAEIihNgDJOPBHUv6aYrIWR3xzrGVUt6tQ0",
"8233444972:AAFIHE5gM5QM6hB9TlSqVhnczdADd1G6jPE",
"8218342121:AAFIxqyLP9CrWsVnTwlOo9yEwhsRraqqh5E",
"8495037330:AAGoJZlDq02bDxa5Vw3g9mr5O2-Sp-gI7vE",
"8573637179:AAGCSunvJ2ImXo91uiZMsL8qYosalHbxG8g",

]

OWNER_ID = 6416341860
SUDO_FILE = "sudo.json"

# HARD / EYE-CATCHING EMOJIS
RAID_TEXTS = [
    "⛧⃟𓆩𓆪⛧", "𓆩🩸𓆪", "☠︎︎𓆩𓆪☠︎︎", "𓆰⚔𓆪", "𓆩𓂀𓆪",
    "𓆩☣𓆪", "𓆩𓃵𓆪", "𓆩𓃭𓆪", "⸸𓆩𓆪⸸", "𓆩☠︎︎𓆪",
    "𓆩🕷𓆪", "𓆩🦂𓆪", "𓆩⚠︎𓆪", "𓆩⚡𓆪", "𓆩🔥𓆪",
    "𓆩💀𓆪", "𓆩👁𓆪", "𓆩🖤𓆪", "𓆩🕸𓆪",
]

SPAM_PATTERNS = [
    "[ any text ] 1-//--🩷" * 40,
    "[ any text ] l --🦋" * 40,
    "[ any text ]k-//--💗" * 40,
    "[ any text ] l - 🤍" * 40,
]

logging.basicConfig(level=logging.INFO)

# ---------------- STATE ----------------
apps = []
bots = []

group_tasks: Dict[int, Dict[str, asyncio.Task]] = {}
voice_tasks: Dict[int, asyncio.Task] = {}
spam_tasks: Dict[int, asyncio.Task] = {}
reply_mode: Dict[int, str] = {}
reply_idx: Dict[int, int] = {}

VOICE_CACHE = []

# ---------------- UTILS ----------------
def load_sudo():
    if os.path.exists(SUDO_FILE):
        try:
            with open(SUDO_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            pass
    return {OWNER_ID}

SUDO_USERS = load_sudo()

def only_owner(func):
    async def wrap(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or update.effective_user.id != OWNER_ID:
            return
        return await func(update, context)
    return wrap

# ---------------- CORE LOOPS ----------------
async def nc_loop(bot, chat_id, base, start_index, step):
    i = start_index
    while True:
        try:
            title = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
            await bot.set_chat_title(chat_id, title)
            await asyncio.sleep(1)
            i += step
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TimedOut:
            continue
        except Exception:
            continue

async def generate_voice_cache():
    if VOICE_CACHE:
        return
    for t in RAID_TEXTS:
        bio = io.BytesIO()
        gTTS(text=t, lang="en").write_to_fp(bio)
        bio.seek(0)
        VOICE_CACHE.append(bio.read())

async def voice_loop(bot, chat_id):
    i = 0
    while True:
        try:
            v = io.BytesIO(VOICE_CACHE[i % len(VOICE_CACHE)])
            v.seek(0)
            await bot.send_voice(chat_id, voice=v)
            i += 1
            await asyncio.sleep(1)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            continue

async def spam_loop(bot, chat_id, base):
    i = 0
    while True:
        try:
            pat = SPAM_PATTERNS[i % len(SPAM_PATTERNS)]
            msg = pat.replace("[ any text ]", base)
            await bot.send_message(chat_id, msg)
            i += 1
            await asyncio.sleep(0.2)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            continue

# ---------------- COMMANDS ----------------
@only_owner
async def ncloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return
    base = " ".join(context.args)
    cid = update.message.chat_id
    group_tasks.setdefault(cid, {})

    step = len(bots)
    for idx, bot in enumerate(bots):
        key = bot.token
        if key not in group_tasks[cid]:
            task = asyncio.create_task(nc_loop(bot, cid, base, idx, step))
            group_tasks[cid][key] = task

    await update.message.reply_text(f"✅ NC STARTED — {step} NC / sec")

@only_owner
async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in group_tasks:
        for t in group_tasks[cid].values():
            t.cancel()
        group_tasks[cid] = {}
    await update.message.reply_text("🛑 NC STOPPED")

@only_owner
async def voiceloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in voice_tasks:
        voice_tasks[cid].cancel()
    voice_tasks[cid] = asyncio.create_task(voice_loop(context.bot, cid))
    await update.message.reply_text("🎤 VOICE LOOP STARTED")

@only_owner
async def stopvoiceloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in voice_tasks:
        voice_tasks[cid].cancel()
        voice_tasks.pop(cid, None)
    await update.message.reply_text("🛑 VOICE LOOP STOPPED")

@only_owner
async def replytext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return
    cid = update.message.chat_id
    reply_mode[cid] = " ".join(context.args)
    reply_idx[cid] = 0
    await update.message.reply_text("⚡ FAST REPLY MODE ON")

@only_owner
async def stopreplytext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    reply_mode.pop(cid, None)
    reply_idx.pop(cid, None)
    await update.message.reply_text("🛑 REPLY MODE OFF")

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in reply_mode and update.message.text:
        try:
            i = reply_idx.get(cid, 0)
            txt = f"{reply_mode[cid]} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
            reply_idx[cid] = i + 1
            await update.message.reply_text(txt)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            pass

@only_owner
async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return
    cid = update.message.chat_id
    if cid in spam_tasks:
        spam_tasks[cid].cancel()
    spam_tasks[cid] = asyncio.create_task(
        spam_loop(context.bot, cid, " ".join(context.args))
    )
    await update.message.reply_text("💥 SPAM STARTED")

@only_owner
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in spam_tasks:
        spam_tasks[cid].cancel()
        spam_tasks.pop(cid, None)
    await update.message.reply_text("🛑 SPAM STOPPED")

@only_owner
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t1 = asyncio.get_event_loop().time()
    msg = await update.message.reply_text("⏳ pinging...")
    t2 = asyncio.get_event_loop().time()
    await msg.edit_text(f"⚡ pong • {int((t2 - t1)*1000)} ms")

@only_owner
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆔 User ID: {update.effective_user.id}\n"
        f"🗂 Chat ID: {update.message.chat_id}"
    )

@only_owner
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    await update.message.reply_text(
        f"📊 STATUS\n"
        f"NC bots: {len(group_tasks.get(cid, {}))}\n"
        f"Voice: {'ON' if cid in voice_tasks else 'OFF'}\n"
        f"Reply: {'ON' if cid in reply_mode else 'OFF'}\n"
        f"Spam : {'ON' if cid in spam_tasks else 'OFF'}"
    )

@only_owner
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⛧⃟  𝐋 𝐎 𝐅 𝐈   𝐏 𝐀 𝐏 𝐀   𝐆 𝐂   𝐌 𝐄 𝐍 𝐔  ⛧⃟\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🧿 NC : /ncloop <text> | /stopgcnc\n"
        "🎤 Voice : /voiceloop | /stopvoiceloop\n"
        "💬 Reply : /replytext <text> | /stopreplytext\n"
        "💥 Spam  : /spam <text> | /stopspam\n"
        "🛠 Info  : /ping | /myid | /status\n\n"
        "☠︎︎ LOFI PAPA • ULTRA FAST • STABLE ☠︎︎"
    )

# ---------------- BUILD & RUN ----------------
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ncloop", ncloop))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(CommandHandler("voiceloop", voiceloop))
    app.add_handler(CommandHandler("stopvoiceloop", stopvoiceloop))
    app.add_handler(CommandHandler("replytext", replytext))
    app.add_handler(CommandHandler("stopreplytext", stopreplytext))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("stopspam", stopspam))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    return app

async def run_all():
    await generate_voice_cache()

    for token in TOKENS:
        app = build_app(token)
        apps.append(app)

    for app in apps:
        # 🔥 ONLY THIS — no initialize(), no start()
        asyncio.create_task(app.run_polling(close_loop=False))
        bots.append(app.bot)
        await asyncio.sleep(0.6)

    print("🚀 LOFI PAPA bots are LIVE and listening to commands.")
    await asyncio.Event().wait()
