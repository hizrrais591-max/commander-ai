"""Mehmonxona yo'nalishi: Booking, Pricing, Guest Support, Review, CRM."""
import ai

SYSTEM = (
    "Sen mehmonxona biznesi bo'yicha ekspert agentsan. O'zbek tilida, "
    "qisqa va amaliy javob ber. Biznes foydasi, narx optimizatsiyasi va "
    "mehmon mamnuniyatiga e'tibor ber."
)


async def handle(task: str) -> str:
    prompt = (
        f"Mehmonxona biznesi vazifasi: {task}\n\n"
        "Quyidagi formatda javob ber:\n"
        "📊 Tahlil\n🎯 Tavsiyalar\n🚀 Keyingi qadamlar"
    )
    body = await ai.ask(SYSTEM, prompt)
    return f"🏨 *Hotel agentlari* (Booking · Pricing · Support · Review · CRM)\n\n{body}"
