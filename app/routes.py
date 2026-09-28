from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models import ComicRequest, ComicResponse
from app.services.image_generator import generate_image
from app.services.pipeline import generate_comic

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def _validate_form(story_prompt: str, character_name: str, setting: str, tone: str, art_style: str) -> ComicRequest:
    try:
        return ComicRequest(story_prompt=story_prompt, character_name=character_name, setting=setting, tone=tone, art_style=art_style)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"app_name": get_settings().app_name})


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    data = _validate_form(story_prompt, character_name, setting, tone, art_style)
    try:
        title, layout, pdf_path = generate_comic(data)
        pdf_url = "/static/exports/" + Path(pdf_path).name
        return templates.TemplateResponse(request=request, name="comic_preview.html", context={"app_name": get_settings().app_name, "title": title, "layout": layout, "pdf_url": pdf_url})
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html", context={"app_name": get_settings().app_name, "error": str(exc), "form": data.model_dump()})


@router.post("/generate-comic/json", response_model=ComicResponse)
async def generate_json(payload: ComicRequest):
    try:
        title, layout, pdf_path = generate_comic(payload)
        return ComicResponse(success=True, title=title, panels=layout, pdf_url="/static/exports/" + Path(pdf_path).name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        path = generate_image(prompt, 0, "test")
        return JSONResponse({"success": True, "image_url": "/static/panels/" + Path(path).name})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(request=request, name="export_success.html", context={"app_name": get_settings().app_name})
