"""COMMANDER AI - markaziy orkestrator.
Vazifani qabul qiladi -> yo'nalishni aniqlaydi -> agentga yuboradi -> natija."""
import agent_hotel
import agent_content
import agent_marketing
import agent_general

ROUTES = {
    "hotel": [
        "mehmonxona", "hotel", "booking", "bron", "narx", "pricing", "mehmon",
        "guest", "review", "sharh", "otel", "nomer", "xona",
    ],
    "content": [
        "youtube", "video", "shorts", "kontent", "content", "skript", "script",
        "thumbnail", "seo", "story", "blog", "post", "reels", "tiktok", "kanal",
    ],
    "marketing": [
        "reklama", "marketing", "ads", "kampaniya", "campaign", "analytics",
        "analitika", "raqobat", "competitor", "sotuv", "sales", "byudjet", "roi",
    ],
}

AGENTS = {
    "hotel": agent_hotel.handle,
    "content": agent_content.handle,
    "marketing": agent_marketing.handle,
    "general": agent_general.handle,
}


def route(task: str) -> str:
    text = task.lower()
    scores = {name: 0 for name in ROUTES}
    for name, keywords in ROUTES.items():
        for kw in keywords:
            if kw in text:
                scores[name] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


async def execute(task: str) -> str:
    target = route(task)
    handler = AGENTS[target]
    result = await handler(task)
    header = (
        "📋 *COMMANDER AI — HISOBOT*\n"
        f"Vazifa: {task}\n"
        f"👥 Yo'nalish: {target}\n"
        "━━━━━━━━━━━━━━\n\n"
    )
    return header + result
