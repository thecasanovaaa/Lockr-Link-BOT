import os
import requests
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from keep_alive import run
run()   # Start Flask keepalive BEFORE bot polling

# ================== SETTINGS ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ---- LOCKR ----
LOCKR_API = os.getenv("LOCKR_API")
LOCKR_KEY = os.getenv("LOCKR_KEY")

# ---- GITHUB GIST ----
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# =============================================

TEMPLATE_A = """
🏠 TELEGRAM :
https://t.me/+kqzetFzSS3llYmVl
Discord ⬇:
https://discord.gg/42R8KJeK

🔴 MEGA :

{{MEGA}}

Download the link Quickly before it gets Deleted by MEGA & JOIN Telegram and DISCORD to be UPDATED⭐☑.
"""

TEMPLATE_B = """
🏠 TELEGRAM :
https://t.me/+kqzetFzSS3llYmVl
Discord ⬇
https://discord.gg/42R8KJeK

(LAST STEP)⬇

{{LOCKR}}

𝗗𝗶𝘀𝗰𝗹𝗮𝗶𝗺𝗲𝗿🗒:
THIS IS NOT A LOOP
THIS IS THE LAST STEP TO RECEIVE THE MEGA LINK.
"""

user_state = {}

# ---------- GIST ----------
def create_gist(text):
    payload = {
        "description": "Telegram Bot Paste",
        "public": True,
        "files": {
            "content.txt": {
                "content": text
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    r = requests.post(
        "https://api.github.com/gists",
        json=payload,
        headers=headers,
        timeout=20
    )

    r.raise_for_status()
    return r.json()["html_url"]


def make_lockr(target_url, title):
    if len(title) > 60:
        title = title[:57] + "..."

    payload = {
        "title": title,
        "target": target_url
    }

    headers = {
        "Authorization": f"Bearer {LOCKR_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(LOCKR_API, json=payload, headers=headers, timeout=20)

    if r.status_code not in (200, 201):
        raise Exception(r.text)

    data = r.json()

    urls = re.findall(r'https?://[^\s"\'\}]+', str(data))
    if not urls:
        raise Exception("Lockr created but no URL found")

    for u in urls:
        if "lockr" in u.lower():
            return u

    return urls[-1]


# ---------- TELEGRAM ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    user_state.pop(update.effective_user.id, None)
    await update.message.reply_text("👋 Mega Link Bejh Gandu:")


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    if user != OWNER_ID:
        return

    text = update.message.text

    # Step 1
    if user not in user_state:
        user_state[user] = {"mega": text}
        await update.message.reply_text("Chinal ka Naam bejh:")
        return

    # Step 2
    user_state[user]["name"] = text
    mega = user_state[user]["mega"]
    name = user_state[user]["name"]

    await update.message.reply_text("Shanti rakh jhatu kar rha hu na kaam ⏳")

    try:
        t1 = TEMPLATE_A.replace("{{MEGA}}", str(mega))
        paste_a = create_gist(t1)

        lockr_a = make_lockr(paste_a, f"{name} mega link")
        if not lockr_a:
            raise Exception("Lockr A Failed")

        t2 = TEMPLATE_B.replace("{{LOCKR}}", str(lockr_a))
        paste_b = create_gist(t2)

        lockr_b = make_lockr(paste_b, name)
        if not lockr_b:
            raise Exception("Final Lockr Failed")

        await update.message.reply_text(f"🔥 LE RE LAND KE:\n{lockr_b}")

    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")

    finally:
        user_state.pop(user, None)


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Locker Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
