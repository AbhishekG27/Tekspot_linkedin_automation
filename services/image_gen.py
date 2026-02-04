"""Image generation: Gemini Imagen from topic (REST API, no google-genai)."""
import base64
import time
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

import requests

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    GEMINI_API_KEY,
    GEMINI_IMAGE_MODEL,
    OUTPUT_DIR,
    ensure_dirs,
)

IMAGEN_PREDICT_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"


def generate_post_image(
    topic: str,
    style: str = "professional, clean, LinkedIn-style graphic",
    template_description: Optional[str] = None,
    hero_copy: Optional[str] = None,
) -> Tuple[Optional[Path], Optional[str]]:
    """
    Generate an image for the LinkedIn post using Gemini Imagen (REST API).
    If template_description is provided, the image will follow that layout/style.
    If hero_copy is provided, use it as the headline text on the image (when template allows).
    Returns (local_file_path, None) on success, or (None, error_message).
    """
    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY is not set in .env"

    ensure_dirs()
    prompt = (
        f"Create a single, professional image suitable for a LinkedIn post. "
        f"Topic/theme: {topic}. Style: {style}. "
    )
    if template_description and template_description.strip():
        prompt += (
            f"Follow this exact visual template/layout: {template_description.strip()}. "
        )
    if hero_copy and hero_copy.strip():
        prompt += (
            f"Include this headline text on the image (clear, bold): \"{hero_copy.strip()}\". "
        )
    if not (hero_copy and hero_copy.strip()):
        prompt += "No text overlay in the image. "
    prompt += "High quality, suitable for business audience."

    try:
        url = IMAGEN_PREDICT_URL.format(model=GEMINI_IMAGE_MODEL)
        headers = {
            "x-goog-api-key": GEMINI_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9",
            },
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        predictions = data.get("predictions") or []
        if not predictions:
            return None, "No predictions in Imagen response"

        pred = predictions[0]
        # Response may have bytesBase64Encoded at top level or under "image"
        b64 = pred.get("bytesBase64Encoded") or (pred.get("image") or {}).get("bytesBase64Encoded")
        if not b64:
            return None, "No image bytes in Imagen response"

        image_bytes = base64.b64decode(b64)
        if not image_bytes:
            return None, "Empty image data"

        safe_name = "".join(
            c if c.isalnum() or c in " -_" else "_" for c in topic[:50]
        )
        fpath = OUTPUT_DIR / f"linkedin_image_{safe_name}_{int(time.time())}.png"

        from PIL import Image
        img = Image.open(BytesIO(image_bytes))
        img.save(str(fpath), format="PNG")
        return fpath, None
    except requests.HTTPError as e:
        body = e.response.text if e.response else str(e)
        return None, f"Imagen API error: {e.response.status_code} {body}"
    except Exception as e:
        return None, str(e)
