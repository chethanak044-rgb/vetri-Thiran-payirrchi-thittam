import hashlib
import io
import re
from pathlib import Path
from typing import Optional

import httpx
from PIL import Image, ImageDraw, ImageFont

from app.config import get_settings


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return cleaned[:60] or "panel"


def _placeholder(prompt: str, output_path: Path, panel_number: int) -> None:
    settings = get_settings()
    image = Image.new("RGB", (settings.image_width, settings.image_height), (245, 238, 224))
    draw = ImageDraw.Draw(image)
    # A deterministic abstract comic background makes development/testing possible without model weights.
    seed = int(hashlib.sha256(prompt.encode()).hexdigest()[:8], 16)
    for i in range(7):
        x = (seed * (i + 3)) % settings.image_width
        y = (seed // (i + 2)) % settings.image_height
        r = 45 + (seed % 80)
        draw.ellipse((x-r, y-r, x+r, y+r), outline=(30, 30, 30), width=3)
    draw.rectangle((18, 18, settings.image_width-18, settings.image_height-18), outline=(20, 20, 20), width=6)
    font = ImageFont.load_default(size=26)
    draw.text((35, 35), f"COMICCRAFT • PANEL {panel_number}", fill=(20, 20, 20), font=font)
    wrapped = prompt[:220].replace("\n", " ")
    draw.text((35, settings.image_height - 90), wrapped, fill=(20, 20, 20), font=ImageFont.load_default(size=16))
    image.save(output_path, format="PNG")


def _hf_api(prompt: str, output_path: Path) -> None:
    settings = get_settings()
    if not settings.hf_api_key:
        raise RuntimeError("HF_API_KEY is required when IMAGE_PROVIDER=hf_api.")
    url = f"https://router.huggingface.co/hf-inference/models/{settings.hf_image_model}"
    response = httpx.post(url, headers={"Authorization": f"Bearer {settings.hf_api_key}"}, json={"inputs": prompt}, timeout=180)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    with Image.open(output_path) as image:
        image.convert("RGB").save(output_path, format="PNG")


def _diffusers(prompt: str, output_path: Path) -> None:
    settings = get_settings()
    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except ImportError as exc:
        raise RuntimeError("Diffusers image generation requires torch and diffusers to be installed.") from exc

    device = settings.image_device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    pipe = StableDiffusionPipeline.from_pretrained(settings.hf_image_model, torch_dtype=dtype, use_safetensors=True)
    pipe = pipe.to(device)
    if device == "cpu":
        pipe.enable_attention_slicing()
    result = pipe(
        prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
    )
    result.images[0].save(output_path, format="PNG")


def generate_image(prompt: str, panel_number: int, filename_hint: Optional[str] = None) -> str:
    settings = get_settings()
    name = _safe_name(filename_hint or f"panel_{panel_number}")
    output_path = settings.panels_path / f"{panel_number:02d}_{name}.png"
    provider = settings.image_provider.lower()
    if provider == "placeholder":
        _placeholder(prompt, output_path, panel_number)
    elif provider == "hf_api":
        _hf_api(prompt, output_path)
    elif provider == "diffusers":
        _diffusers(prompt, output_path)
    else:
        raise RuntimeError(f"Unsupported IMAGE_PROVIDER: {settings.image_provider}")
    return str(output_path)
