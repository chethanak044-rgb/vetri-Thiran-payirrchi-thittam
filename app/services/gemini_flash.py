from typing import List
from app.config import get_settings
from app.models import ComicRequest, PanelOutline
from app.services.gemini_client import generate_text


def generate_outline(request: ComicRequest) -> List[PanelOutline]:
    settings = get_settings()
    prompt = f"""
Create a cohesive five-panel comic outline.
User story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Requirements:
- Return exactly 5 panels numbered 1 through 5.
- Maintain continuity across panels.
- Each panel needs a concise title, scene description, and a detailed visual image prompt.
- Do not put dialogue into image_prompt.
- Make the visual prompts suitable for a single comic illustration and include composition, lighting,
  character appearance/action, environment, and the requested art style.
"""
    raw = generate_text(settings.gemini_flash_model, prompt, schema=list[PanelOutline], temperature=0.8)
    import json
    data = json.loads(raw)
    panels = [PanelOutline.model_validate(item) for item in data]
    if len(panels) != 5:
        raise RuntimeError(f"Expected 5 outline panels, received {len(panels)}.")
    return panels
