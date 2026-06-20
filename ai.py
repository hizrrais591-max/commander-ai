"""AI miyasi - OpenAI mos keladigan API ga so'rov yuboradi.
AI_API_KEY bo'lmasa, oddiy fallback javob qaytaradi (bot kalitsiz ham ishlaydi)."""
import httpx
import config


async def ask(system_prompt: str, user_prompt: str, max_tokens: int = 900) -> str:
    if not config.AI_ENABLED:
        return (
            "⚠️ AI kaliti ulanmagan (AI_API_KEY bo'sh).\n"
            "To'liq AI javoblari uchun Railway Variables ga AI_API_KEY qo'shing.\n\n"
            f"So'rov qabul qilindi: {user_prompt[:200]}"
        )

    url = f"{config.AI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:  # noqa: BLE001
        return f"❌ AI xatosi: {e}"
