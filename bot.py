"""COMMANDER AI - 24/7 Telegram boshqaruv markazi.
Ishga tushirish:  python bot.py
"""
import io
import re
import logging
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
import commander
import imagegen

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO
)
log = logging.getLogger("commander")


def is_admin(update: Update) -> bool:
    if not config.ADMIN_CHAT_ID:
        return True
    return str(update.effective_chat.id) == config.ADMIN_CHAT_ID


# Rasm va video so'rovlarini aniqlash uchun kalit so'zlar
IMG_KEYS = ("rasm", "surat", "image", "chiz", "rasim")
VID_KEYS = ("video", "vidio", "klip", "video qil")
# Promptdan olib tashlanadigan buyruq so'zlari
STRIP_WORDS = [
    "rasm chizib ber", "rasm qilib ber", "rasm chiz", "rasm qil", "chizib ber",
    "video qilib ber", "video qil", "rasm", "surat", "image", "chiz", "video",
    "vidio", "klip", "qilib ber", "qil",
]


def clean_prompt(text: str) -> str:
    p = text
    for w in STRIP_WORDS:
        p = re.sub(re.escape(w), "", p, flags=re.IGNORECASE)
    return p.strip(" :,-—.")


WELCOME = (
    "🎖 *COMMANDER AI* ishga tushdi!\n\n"
    "Men sizning avtomatlashtirish markazingizman. Vazifa yozing — men uni "
    "kerakli agentga yuboraman va hisobot qaytaraman.\n\n"
    "📌 *Buyruqlar:*\n"
    "/agents — yo'nalishlar ro'yxati\n"
    "/jadval — avtomatik vazifalar\n"
    "/rasm <tavsif> — rasm chizish 🎨\n"
    "/vazifa <matn> — vazifa berish\n\n"
    "Yoki shunchaki yozing:\n"
    "_«Mehmonxonam uchun yozgi narx strategiyasi»_\n"
    "_«rasm: tog'lar ustida quyosh chiqishi»_"
)

AGENTS_LIST = (
    "👥 *YO'NALISHLAR VA AGENTLAR*\n\n"
    "🏨 *Hotel* — Booking, Pricing, Guest Support, Review, CRM\n"
    "🎥 *Content* — YouTube, Shorts, Script, Thumbnail, SEO, Story\n"
    "📈 *Marketing* — Reklama, Analytics, Competitor, Sales\n"
    "🎨 *Rasm* — Pollinations orqali rasm generatsiya\n"
    "🤖 *Umumiy* — Automation, Database, QA, Brand, Expansion\n\n"
    "Vazifa yozsangiz, Commander avtomatik to'g'ri yo'nalishni tanlaydi."
)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    await update.message.reply_text(WELCOME, parse_mode=ParseMode.MARKDOWN)


async def cmd_agents(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    await update.message.reply_text(AGENTS_LIST, parse_mode=ParseMode.MARKDOWN)


async def cmd_jadval(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    sched = ctx.application.bot_data.get("scheduler")
    jobs = sched.get_jobs() if sched else []
    if not jobs:
        await update.message.reply_text("📅 Hozircha avtomatik vazifalar yo'q.")
        return
    lines = ["📅 *Avtomatik vazifalar:*\n"]
    for j in jobs:
        nxt = j.next_run_time.strftime("%Y-%m-%d %H:%M") if j.next_run_time else "—"
        lines.append(f"• {j.name} → keyingi: {nxt}")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def make_image(update: Update, prompt: str):
    """Rasm chizib, Telegram'ga yuboradi."""
    if len(prompt) < 2:
        await update.message.reply_text(
            "🎨 Nimani chizay? Masalan: «rasm: tog'lar ustida quyosh chiqishi»"
        )
        return
    await update.message.chat.send_action("upload_photo")
    await update.message.reply_text("🎨 Rasm chizilyapti, biroz kuting...")
    try:
        final = await imagegen.enhance(prompt)
        data = await imagegen.fetch(final)
        await update.message.reply_photo(
            photo=io.BytesIO(data), caption=f"🎨 {prompt}"
        )
    except Exception as e:  # noqa: BLE001
        await update.message.reply_text(
            f"❌ Rasm yaratishda xato: {e}\nQayta urinib ko'ring."
        )


async def cmd_rasm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    prompt = " ".join(ctx.args).strip()
    await make_image(update, prompt)


async def run_task(update: Update, task: str):
    await update.message.chat.send_action("typing")
    report = await commander.execute(task)
    for chunk in [report[i : i + 4000] for i in range(0, len(report), 4000)]:
        await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)


async def cmd_vazifa(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    task = " ".join(ctx.args).strip()
    if not task:
        await update.message.reply_text("Foydalanish: /vazifa <matn>")
        return
    await run_task(update, task)


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    text = update.message.text.strip()
    low = text.lower()

    # Video so'rovi
    if any(k in low for k in VID_KEYS):
        await update.message.reply_text(
            "🎬 Video generatsiya hozircha sozlanmagan.\n"
            "Video uchun pullik xizmat (Replicate yoki fal.ai) API kaliti kerak. "
            "Qo'shishni xohlasangiz, adminga ayting."
        )
        return

    # Rasm so'rovi
    if any(k in low for k in IMG_KEYS):
        await make_image(update, clean_prompt(text))
        return

    # Oddiy vazifa
    await run_task(update, text)


async def daily_briefing(app: Application):
    if not config.ADMIN_CHAT_ID:
        return
    task = "Bugungi kun uchun biznes bo'yicha qisqa motivatsion maslahat va 3 ta ustuvor vazifa ber."
    report = await commander.execute(task)
    text = f"☀️ *Ertalabki avtomatik hisobot*\n\n{report}"
    await app.bot.send_message(
        chat_id=config.ADMIN_CHAT_ID, text=text[:4000], parse_mode=ParseMode.MARKDOWN
    )


def setup_scheduler(app: Application) -> AsyncIOScheduler:
    tz = ZoneInfo(config.TIMEZONE)
    sched = AsyncIOScheduler(timezone=tz)
    sched.add_job(
        daily_briefing,
        "cron",
        hour=8,
        minute=0,
        args=[app],
        name="Ertalabki hisobot (har kuni 08:00)",
    )
    sched.start()
    log.info("Scheduler ishga tushdi. Vaqt mintaqasi: %s", config.TIMEZONE)
    return sched


def main():
    missing = config.check()
    if missing:
        raise SystemExit(
            "❌ Quyidagi sozlamalar to'ldirilmagan (Railway Variables ga qo'shing): "
            + ", ".join(missing)
        )

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("agents", cmd_agents))
    app.add_handler(CommandHandler("jadval", cmd_jadval))
    app.add_handler(CommandHandler("rasm", cmd_rasm))
    app.add_handler(CommandHandler("vazifa", cmd_vazifa))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    async def _post_init(application: Application):
        application.bot_data["scheduler"] = setup_scheduler(application)
        if config.ADMIN_CHAT_ID:
            try:
                await application.bot.send_message(
                    chat_id=config.ADMIN_CHAT_ID,
                    text="🎖 Commander AI server ishga tushdi va 24/7 tayyor! (rasm: /rasm)",
                )
            except Exception as e:  # noqa: BLE001
                log.warning("Adminga xabar yuborilmadi: %s", e)

    app.post_init = _post_init

    log.info("Commander AI ishga tushyapti... (AI: %s)", "yoqilgan" if config.AI_ENABLED else "o'chiq")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
