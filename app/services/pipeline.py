from app.models import ComicRequest
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


def generate_comic(request: ComicRequest):
    outline = generate_outline(request)
    stories = generate_story(request, outline)
    image_paths = [
        generate_image(panel.image_prompt, panel.panel_number, panel.title)
        for panel in stories
    ]
    layout = build_comic_layout(stories, image_paths)
    title = stories[0].title if stories else "ComicCraft Comic"
    pdf_path = save_pdf(title, layout)
    return title, layout, pdf_path
