"""Image generation: Gemini 3 Pro Image with reference images, Tekspot template, minimal content."""
import base64
import time
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple, List

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    GEMINI_API_KEY,
    GEMINI_IMAGE_MODEL,
    OUTPUT_DIR,
    IMAGES_DIR,
    ensure_dirs,
)

# Tekspot branded template: purple-teal gradient, logo top-left, minimal text + topic imagery
TEKSPOT_TEMPLATE = (
    "Professional LinkedIn post graphic for TEKSPOT GLOBAL SOLUTIONS. "
    "Match the reference image style exactly: "
    "Smooth gradient background from deep purple (left) to teal/light green (right). "
    "Include TEKSPOT GLOBAL SOLUTIONS logo in top-left corner (white text, globe icon, clean sans-serif). "
    "Minimal text only: one short headline, 5-10 words max. No extra copy, bullet points, or long sentences. "
    "Include topic-relevant imagery: visuals, icons, or metaphors that match the theme (e.g., talent/HR: people, teams, handshakes, workforce; tech/IT: computers, digital, recruitment; skills: learning, growth). "
    "Left side: headline text. Right side or center: relevant visual element tied to the topic. Clean, corporate, high-end aesthetic. 16:9 aspect ratio."
)


def _load_reference_images(images_dir: Path, max_count: int = 2) -> List:
    """Load up to max_count reference images from images/ folder for style guidance."""
    if not images_dir or not images_dir.exists():
        return []
    try:
        from PIL import Image
    except ImportError:
        return []
    supported = {".jpg", ".jpeg", ".png", ".webp"}
    files = sorted(
        [f for f in images_dir.iterdir() if f.suffix.lower() in supported],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    refs = []
    for f in files[:max_count]:
        try:
            img = Image.open(f).convert("RGB")
            refs.append(img)
        except Exception:
            continue
    return refs


def generate_post_image(
    topic: str,
    style: str = "professional, clean, LinkedIn-style graphic",
    template_description: Optional[str] = None,
    hero_copy: Optional[str] = None,
    reference_images_dir: Optional[Path] = None,
) -> Tuple[Optional[Path], Optional[str]]:
    """
    Generate an image for the LinkedIn post using Gemini 3 Pro Image.
    Uses reference images from images/ folder to match Tekspot template.
    Includes Tekspot logo, minimal content (short headline only).
    Returns (local_file_path, None) on success, or (None, error_message).
    """
    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY is not set in .env"

    ensure_dirs()

    # Limit hero_copy for "less content" - max ~10 words, single punchy line
    headline = ""
    if hero_copy and hero_copy.strip():
        words = hero_copy.strip().split()[:10]
        headline = " ".join(words)
    if not headline:
        # Fallback: use first few words of topic
        headline = " ".join(topic.strip().split()[:8])

    template = template_description.strip() if template_description and template_description.strip() else TEKSPOT_TEMPLATE

    prompt = (
        f"Create a new image following this exact template: {template} "
        f"Topic/theme: {topic}. "
        f"Display this headline text (bold, white, left side): \"{headline}\". "
        f"Include relevant imagery on the right or center that visually represents the topic — e.g., for talent acquisition: professionals, teams, hiring; for workforce/skills: learning, growth, people; for IT recruitment: tech, digital. "
        f"No other text. Match the reference images' layout, colors, and Tekspot branding. Suitable for LinkedIn company post."
    )

    ref_dir = reference_images_dir or IMAGES_DIR
    ref_images = _load_reference_images(ref_dir, max_count=2)

    try:
        from google import genai
        from google.genai import types
        from PIL import Image as PILImage
    except ImportError:
        return None, "Install google-genai: pip install google-genai"

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        contents = [prompt]
        if ref_images:
            contents = [prompt] + ref_images

        config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
                image_size="2K",
            ),
        )

        response = client.models.generate_content(
            model=GEMINI_IMAGE_MODEL,
            contents=contents,
            config=config,
        )

        # Extract image from response (google-genai SDK)
        image_bytes = None
        parts = []
        if hasattr(response, "parts"):
            parts = list(response.parts)
        elif hasattr(response, "candidates") and response.candidates:
            cand = response.candidates[0]
            if hasattr(cand, "content") and hasattr(cand.content, "parts"):
                parts = list(cand.content.parts)

        for part in parts:
            if hasattr(part, "as_image"):
                try:
                    img = part.as_image()
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    image_bytes = buf.getvalue()
                    break
                except Exception:
                    pass
            if hasattr(part, "inline_data") and part.inline_data:
                blob = part.inline_data
                data = getattr(blob, "data", None) or getattr(blob, "image_bytes", None)
                if data:
                    image_bytes = data if isinstance(data, bytes) else base64.b64decode(data)
                    break

        if not image_bytes:
            return None, "No image in Gemini response"

        safe_name = "".join(
            c if c.isalnum() or c in " -_" else "_" for c in topic[:50]
        )
        fpath = OUTPUT_DIR / f"linkedin_image_{safe_name}_{int(time.time())}.png"

        img = PILImage.open(BytesIO(image_bytes))
        img.save(str(fpath), format="PNG")
        return fpath, None

    except Exception as e:
        return None, str(e)
