"""Marketing yo'nalishi: Reklama, Analytics, Competitor, SEO, Sales."""
import ai

SYSTEM = (
    "Sen raqamli marketing bo'yicha ekspert agentsan. O'zbek tilida javob "
    "ber. ROI, konversiya, byudjet samaradorligi va raqobatga e'tibor ber."
)


async def handle(task: str) -> str:
    prompt = (
        f"Marketing vazifasi: {task}\n\n"
        "Quyidagi formatda javob ber:\n"
        "📊 Tahlil\n🎯 Tavsiyalar (aniq harakatlar)\n💰 Byudjet bo'yicha maslahat\n🚀 Keyingi qadamlar"
    )
    body = await ai.ask(SYSTEM, prompt)
    return f"📈 *Marketing agentlari* (Reklama · Analytics · Competitor · Sales)\n\n{body}"
