from pathlib import Path
from typing import List
from app.models import PanelStory, ComicPanel
from app.config import get_settings


def build_comic_layout(stories: List[PanelStory], image_paths: List[str]) -> List[ComicPanel]:
    if len(stories) != len(image_paths):
        raise ValueError("Every story panel must have a matching image.")
    settings = get_settings()
    result = []
    for story, image_path in zip(stories, image_paths):
        filename = Path(image_path).name
        result.append(ComicPanel(
            panel_number=story.panel_number,
            title=story.title,
            image_path=image_path,
            image_url=f"/static/panels/{filename}",
            scene_description=story.scene_description,
            caption=story.caption,
            narration=story.narration,
            dialogue=story.dialogue,
            image_prompt=story.image_prompt,
        ))
    return result
