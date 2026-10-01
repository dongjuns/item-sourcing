"""환경설정과 비밀은 이 모듈에서만 읽는다."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )
    database_url: SecretStr = SecretStr("sqlite+pysqlite:///./itemsourcing.sqlite3")
    domeggook_api_key: SecretStr = SecretStr("")
    openai_api_key: SecretStr = SecretStr("")
    source_mode: Literal["live", "mock"] = "live"
    ai_mode: Literal["live", "mock"] = "mock"
    ai_text_model: str = ""
    ai_image_model: str = ""
    assets_dir: Path = PROJECT_ROOT / "assets"
    prompts_dir: Path = PROJECT_ROOT / "backend" / "prompts"
    request_timeout_seconds: float = Field(default=30, gt=0)
    source_interval_seconds: float = Field(default=2, ge=2)
    max_image_bytes: int = Field(default=10_000_000, gt=0)
    max_source_images: int = Field(default=30, gt=0)
    image_allowed_domains: list[str] = ["domeggook.com", "domemedb.com", "i.ifh.cc"]
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_config() -> Config:
    return Config()
