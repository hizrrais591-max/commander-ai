"""Rasm generatsiya - Pollinations.ai (bepul, API kalit kerak emas).

Promptni (xohlasa AI orqali inglizchaga o'girib) rasmga aylantiradi va
rasm baytlarini qaytaradi, shunda bot uni Telegram'ga yuboradi.
"""
import urllib.parse
import httpx

import config
import ai


async def enhance(prompt: str) -> str:
    """O'zbekcha so'rovni batafsil inglizcha image-prompt ga aylantiradi.
    AI o'chiq bo'lsa - promptni o'zgartirmasdan qaytaradi."""
    if not config.AI_ENABLED:
        return prompt
    system = (
        "You convert a short user request (any language) into a vivid, "
        "detailed English image-generation prompt. Reply with ONLY the prompt "
        "on one line, no quotes, no explanation."
    )
    out = await ai.ask(system, prompt, max_tokens=120)
    out = (out or "").strip().replace("\n", " ")
    if not out or out.startswith("❌") or out.startswith("⚠️"):
        return prompt
    return out


def image_url(prompt: str) -> str:
    enc = urllib.parse.quote(prompt)
    return (
        f"https://image.pollinations.ai/prompt/{enc}"
        "?width=1024&height=1024&nologo=true&model=flux"
    )


async def fetch(prompt: str) -> bytes:
    """Rasm baytlarini yuklab oladi (Pollinations generatsiyasi biroz vaqt oladi)."""
    url = image_url(prompt)
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as c:
        r = await c.get(url)
        r.raise_for_status()
        return r.content
