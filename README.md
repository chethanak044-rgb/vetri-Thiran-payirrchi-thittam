# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application that turns a user prompt into a five-panel comic. The workflow follows the supplied project specification: structured outline generation, expanded narration/dialogue, panel illustrations, layout binding, and PDF export.

## Architecture

```text
Browser / API client
        |
        v
FastAPI routes.py
        |
        +--> gemini_flash.py  -> 5-panel structured outline
        |
        +--> gemini_pro.py    -> narration + dialogue
        |
        +--> image_generator.py -> placeholder / Hugging Face / local Diffusers
        |
        +--> layout_builder.py -> panel data + image URLs
        |
        +--> exporters.py -> multi-page PDF
        |
        v
Jinja2 templates + static assets
```

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   ├── exporters.py
│   │   └── pipeline.py
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── panels/.gitkeep
│   └── exports/.gitkeep
├── tests/test_layout.py
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## VS Code setup — Windows

1. Install Python 3.11 or newer and VS Code.
2. Open this `ComicCraft` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate
```

5. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Create the environment file:

```powershell
Copy-Item .env.example .env
```

7. Open `.env` and add your Gemini API key.

## First run: no GPU required

Keep:

```env
IMAGE_PROVIDER=placeholder
```

This mode is intentionally included so you can verify the entire FastAPI → Gemini → layout → PDF flow without downloading a multi-gigabyte image model. The generated panels are development placeholders.

Start the server:

```powershell
python run.py
```

Open:

- http://127.0.0.1:8000 — web UI
- http://127.0.0.1:8000/docs — Swagger API docs
- http://127.0.0.1:8000/health — health check

## Real Stable Diffusion images

For local Hugging Face Diffusers image generation, set:

```env
IMAGE_PROVIDER=diffusers
HF_IMAGE_MODEL=stable-diffusion-v1-5/stable-diffusion-v1-5
IMAGE_DEVICE=auto
```

A CUDA-capable NVIDIA GPU is strongly recommended for practical local generation. On CPU, generation can be very slow and memory-heavy.

The implementation uses `StableDiffusionPipeline.from_pretrained()` and supports automatic CUDA/CPU selection. The Diffusers documentation describes this pipeline-loading approach and Stable Diffusion text-to-image API. See the official Hugging Face documentation for model/runtime details.

## Hugging Face hosted image generation

If you prefer not to run Stable Diffusion locally, use the hosted inference backend:

```env
IMAGE_PROVIDER=hf_api
HF_API_KEY=your_hugging_face_token
HF_IMAGE_MODEL=stable-diffusion-v1-5/stable-diffusion-v1-5
```

## API example

`POST /generate-comic/json`

```json
{
  "story_prompt": "A brave fox discovers a hidden library beneath an enchanted forest.",
  "character_name": "Milo",
  "setting": "forest",
  "tone": "adventurous",
  "art_style": "comic book"
}
```

The response contains the generated title, five panel records, image URLs, and a PDF URL.

## Image-only test

The developer endpoint is:

```text
POST /test-image
```

It accepts a form field named `prompt`.

## Tests

Run:

```powershell
pytest -q
```

The included tests do not call external AI services.

## Notes on the supplied specification

The source document names `google-generativeai`, `gemini-1.5-flash`, `gemini-1.5-pro`, and `runwayml/stable-diffusion-v1-5`. This implementation preserves the intended Flash/Pro role separation and Stable Diffusion role, but uses the current Google GenAI Python SDK and configurable current model names so the project is maintainable as model APIs change.

Generated assets are intentionally excluded from Git by `.gitignore`.
