"""AI와 채널 결과 객체."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, JsonValue

from app.schemas.product import Issue


class Usage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    image_count: int | None = None
    actual_cost_krw: Decimal | None = None
    provider_usage: dict[str, JsonValue] = {}
    billing_status: Literal["verified", "unbilled", "unknown"] = "unknown"


class DetailContent(BaseModel):
    title: str
    sections: list[dict[str, str]]


class DetailResult(BaseModel):
    content: DetailContent | None = None
    usage: Usage = Usage()
    issues: list[Issue] = []


class GeneratedImage(BaseModel):
    path: str
    mime_type: str
    width: int
    height: int
    prompt: str


class ImageResult(BaseModel):
    images: list[GeneratedImage] = []
    usage: Usage = Usage()
    issues: list[Issue] = []


class CategoryResult(BaseModel):
    categories: list[dict[str, str]] = []
    issues: list[Issue] = []


class RegisterResult(BaseModel):
    outcome: Literal["succeeded", "failed", "unknown", "simulated"]
    external_id: str | None = None
    external_url: str | None = None
    response: dict[str, JsonValue] | None = None
    issues: list[Issue] = []
