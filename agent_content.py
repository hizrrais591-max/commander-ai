"""Kontent yo'nalishi: YouTube, Shorts, Script, Thumbnail, SEO, Story."""
import ai

SYSTEM = (
    "Sen YouTube va qisqa video kontent bo'yicha ekspert agentsan. O'zbek "
    "tilida javob ber. Viral hook, retention va SEO ga e'tibor ber."
)


async def handle(task: str) -> str:
    prompt = (
        f"Kontent vazifasi: {task}\n\n"
        "Quyidagilarni ber:\n"
        "🎬 3 ta video g'oya (sarlavha bilan)\n"
        "🪝 Har biriga ochilish hook\n"
        "🔑 SEO kalit so'zlar\n"
        "🚀 Keyingi qadamlar"
    )
    body = await ai.ask(SYSTEM, prompt)
    return f"🎥 *Content agentlari* (YouTube · Shorts · Script · SEO · Thumbnail)\n\n{body}"
