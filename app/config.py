from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True
    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"
    image_provider: str = "placeholder"
    hf_api_key: str = ""
    hf_image_model: str = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    image_device: str = "auto"
    image_width: int = 512
    image_height: int = 512
    image_steps: int = 20
    image_guidance: float = 7.5
    static_dir: str = "static"
    panels_dir: str = "static/panels"
    exports_dir: str = "static/exports"
    max_prompt_length: int = 2000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def root_dir(self) -> Path:
        return ROOT_DIR

    @property
    def static_path(self) -> Path:
        return ROOT_DIR / self.static_dir

    @property
    def panels_path(self) -> Path:
        return ROOT_DIR / self.panels_dir

    @property
    def exports_path(self) -> Path:
        return ROOT_DIR / self.exports_dir

    def ensure_directories(self) -> None:
        self.static_path.mkdir(parents=True, exist_ok=True)
        self.panels_path.mkdir(parents=True, exist_ok=True)
        self.exports_path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
