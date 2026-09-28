from typing import List
from app.config import get_settings
from app.models import ComicRequest, PanelOutline, PanelStory
from app.services.gemini_client import generate_text


def generate_story(request: ComicRequest, outline: List[PanelOutline]) -> List[PanelStory]:
    settings = get_settings()
    outline_text = "\n".join(
        f"Panel {p.panel_number}: {p.title}\nScene: {p.scene_description}\nImage prompt: {p.image_prompt}"
        for p in outline
    )
    prompt = f"""
Expand this five-panel comic outline into polished comic narration and dialogue.
Story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Outline:
{outline_text}

Return exactly five PanelStory objects in the same order.
For every panel provide:
- panel_number and title matching the outline
- scene_description (1-2 sentences)
- caption (short ambient/comic caption)
- narration (2-4 sentences)
- dialogue (short natural dialogue, or empty string if none is appropriate)
- image_prompt preserving the visual continuity of the outline
Keep the story family-friendly and coherent. Do not introduce new main characters unless needed by the plot.
"""
    raw = generate_text(settings.gemini_pro_model, prompt, schema=list[PanelStory], temperature=0.95)
    import json
    data = json.loads(raw)
    panels = [PanelStory.model_validate(item) for item in data]
    if len(panels) != 5:
        raise RuntimeError(f"Expected 5 story panels, received {len(panels)}.")
    return panels
