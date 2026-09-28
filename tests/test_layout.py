from pathlib import Path
from app.models import PanelStory
from app.services.layout_builder import build_comic_layout


def test_build_comic_layout():
    stories = [
        PanelStory(panel_number=i, title=f"Panel {i}", scene_description="Scene", caption="Caption", narration="Narration", dialogue="", image_prompt="Prompt")
        for i in range(1, 6)
    ]
    paths = [f"static/panels/{i:02d}_panel.png" for i in range(1, 6)]
    result = build_comic_layout(stories, paths)
    assert len(result) == 5
    assert result[0].image_url.endswith("01_panel.png")


def test_project_assets_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "app" / "main.py").exists()
    assert (root / "templates" / "index.html").exists()
