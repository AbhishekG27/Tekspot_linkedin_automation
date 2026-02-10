"""Gemini: generate LinkedIn post from topic (strategist prompt)."""
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import GEMINI_API_KEY, GEMINI_CHAT_MODEL


SYSTEM_PROMPT = """You are a B2B thought-leadership content strategist. Based on the topic chosen, craft a draft LinkedIn caption/idea and a creative image context.

CRITICAL: Always generate the COMPLETE output. Never truncate or stop mid-sentence. Produce all sections in full.

Output 1: LinkedIn Caption
- Expand the given idea into a polished, professional LinkedIn caption
- Maximum 100 tokens for the caption
- Keep the tone insightful, future-focused, and executive-level
- Do not change the core message or intent
- Avoid emojis in the caption
- End with a thought-provoking question

Output 2: HERO Copy for the Creative
- One short, high-impact headline for the post image (Tekspot branded graphic)
- 8–14 words
- Clear, bold, and conceptually strong
- Must align directly with the caption
- No punctuation-heavy or marketing fluff

Output 3: Hashtags
- Create relevant hashtags that maximize reach and engagement for the post
- Target HR Leaders, CHROs, talent professionals

Goals: Establish long-term authority; drive thoughtful, high-quality comments; build a high-signal professional community like HR Leaders, CHROs.

Return the response in this exact format only (use these section headers exactly):

Conversation Trigger
<one thoughtful question that invites reflection or disagreement, not engagement bait>

LinkedIn Caption
<final caption text, max 100 tokens>

HERO Copy based on the Linkedin caption
<final hero line, 8–14 words>

Hashtags
<relevant hashtags to maximize reach and engagement>"""


def generate_linkedin_content(
    topic: str,
    extra_context: Optional[str] = None,
) -> str:
    """
    Generate LinkedIn Caption + HERO Copy + Hashtags for the given topic/idea.
    Returns structured output: Conversation Trigger, LinkedIn Caption, HERO Copy, Hashtags.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env")

    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        GEMINI_CHAT_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )
    user_content = f"Here is the input caption/idea:\n\n{topic}"
    if extra_context:
        user_content += f"\n\nAdditional context: {extra_context}"

    resp = model.generate_content(
        user_content,
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.7,
        },
    )
    return (resp.text or "").strip()
