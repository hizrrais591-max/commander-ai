"""Umumiy agent: yo'nalishga tushmagan vazifalar uchun (Automation, Python,
Database, QA, Expansion, Brand va h.k.)."""
import ai

SYSTEM = (
    "Sen Commander AI ning umumiy yordamchi agentisan. O'zbek tilida, qisqa "
    "va amaliy javob ber. Avtomatlashtirish va biznes o'sishiga e'tibor ber."
)


async def handle(task: str) -> str:
    prompt = (
        f"Vazifa: {task}\n\n"
        "📊 Tahlil, 🎯 Tavsiyalar va 🚀 Keyingi qadamlar formatida javob ber."
    )
    body = await ai.ask(SYSTEM, prompt)
    return f"🤖 *Umumiy agent*\n\n{body}"
