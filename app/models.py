from typing import List
from pydantic import BaseModel, Field, ConfigDict


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str
    scene_description: str
    image_prompt: str


class PanelStory(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str = ""
    image_prompt: str


class ComicRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    story_prompt: str = Field(min_length=3, max_length=2000)
    character_name: str = Field(default="Alex", min_length=1, max_length=80)
    setting: str = Field(default="enchanted forest", min_length=1, max_length=120)
    tone: str = Field(default="dramatic", min_length=1, max_length=50)
    art_style: str = Field(default="comic book", min_length=1, max_length=80)


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    image_path: str
    image_url: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str = ""
    image_prompt: str


class ComicResponse(BaseModel):
    success: bool = True
    title: str
    panels: List[ComicPanel]
    pdf_url: str
