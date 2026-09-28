from datetime import datetime, timezone
from pathlib import Path
from fpdf import FPDF
from PIL import Image
from app.config import get_settings
from app.models import ComicPanel


def _pdf_text(value: str) -> str:
    """Keep built-in Helvetica PDF output safe for Unicode AI text."""
    return str(value).encode("latin-1", "replace").decode("latin-1")


def _fit_image(pdf: FPDF, path: str, max_w: float, max_h: float) -> tuple[float, float]:
    with Image.open(path) as img:
        w, h = img.size
    ratio = min(max_w / w, max_h / h)
    return w * ratio, h * ratio


def save_pdf(title: str, panels: list[ComicPanel]) -> str:
    settings = get_settings()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title).strip("_")[:50] or "comic"
    output = settings.exports_path / f"{safe_title}_{timestamp}.pdf"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    for panel in panels:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10,  _pdf_text(f"Panel {panel.panel_number}: {panel.title}"))
        pdf.ln(2)
        max_w, max_h = 180, 105
        w, h = _fit_image(pdf, panel.image_path, max_w, max_h)
        x = (210 - w) / 2
        pdf.image(panel.image_path, x=x, y=pdf.get_y(), w=w, h=h)
        pdf.set_y(pdf.get_y() + h + 6)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _pdf_text(panel.scene_description))
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 6, _pdf_text(f"Caption: {panel.caption}"))
        pdf.ln(1)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, _pdf_text(panel.narration))
        if panel.dialogue:
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, _pdf_text(f'Dialogue: {panel.dialogue}'))
    pdf.output(str(output))
    return str(output)
